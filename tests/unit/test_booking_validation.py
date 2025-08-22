import unittest
from unittest.mock import patch
from server import app


class TestBookingValidation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        # Create mock test data
        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
            {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
        ]

        self.mock_competitions = [
            {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "13"},
            {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "10"}
        ]

        # Patch the load and save functions
        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.competitions_patcher = patch('server.loadCompetitions', return_value=self.mock_competitions)
        self.save_clubs_patcher = patch('server.save_clubs')
        self.save_competitions_patcher = patch('server.save_competitions')

        self.mock_load_clubs = self.clubs_patcher.start()
        self.mock_load_competitions = self.competitions_patcher.start()
        self.mock_save_clubs = self.save_clubs_patcher.start()
        self.mock_save_competitions = self.save_competitions_patcher.start()

    def tearDown(self):
        self.clubs_patcher.stop()
        self.competitions_patcher.stop()
        self.save_clubs_patcher.stop()
        self.save_competitions_patcher.stop()

    def get_updated_club(self, club_name):
        """Get club from current mock data (simulates reloading)"""
        return next(club for club in self.mock_clubs if club['name'] == club_name)

    def get_updated_competition(self, competition_name):
        """Get competition from current mock data (simulates reloading)"""
        return next(comp for comp in self.mock_competitions if comp['name'] == competition_name)

    def test_booking_more_than_12_places_fails(self):
        """Integration test: 12-place limit validation in complete workflow"""
        club_name = self.mock_clubs[0]['name']  # Simply Lift has 13 points
        competition_name = self.mock_competitions[1]['name']  # Fall Classic, 10 places

        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': club_name,
                            'competition': competition_name,
                            'places': '13'  # More than 12
                        },
                        follow_redirects=True
                    )

                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Cannot book more than 12 places', response.data)

                    # Verify data remains unchanged
                    club = self.get_updated_club(club_name)
                    competition = self.get_updated_competition(competition_name)
                    self.assertEqual(int(club['points']), 13)
                    self.assertEqual(int(competition['numberOfPlaces']), 10)

    # Test: Booking fewer than 12 places succeed and deduct points
    def test_booking_less_than_12_places_succeeds(self):
        """Integration test: Successful booking with points deduction"""
        club_name = self.mock_clubs[0]['name']  # "Simply Lift"
        competition_name = self.mock_competitions[1]['name']  # "Fall Classic"

        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': club_name,
                            'competition': competition_name,
                            'places': '5'
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Great-booking complete!', response.data)

                    # Verify points were deducted
                    updated_club = self.get_updated_club(club_name)
                    self.assertEqual(int(updated_club['points']), 8)  # 13 - 5 = 8

    # Test: exactly 12 places succeed
    def test_booking_12_places_succeeds(self):
        """Integration test: Edge case - exactly 12 places booking"""
        club_name = self.mock_clubs[0]['name']  # Simply Lift, 13 points
        competition_name = self.mock_competitions[0]['name']  # Spring Festival, 13 places

        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': club_name,
                            'competition': competition_name,
                            'places': '12'
                        },
                        follow_redirects=True
                    )

                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Great-booking complete!', response.data)

                    # Verify points were deducted to 1
                    updated_club = self.get_updated_club(club_name)
                    self.assertEqual(int(updated_club['points']), 1)  # 13 - 12 = 1


if __name__ == '__main__':
    unittest.main()