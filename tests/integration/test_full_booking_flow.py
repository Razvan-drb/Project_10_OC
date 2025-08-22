import unittest
from unittest.mock import patch
from server import app


class TestBookingWorkflows(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
        ]

        self.mock_competitions = [
            {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "13"},
            {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "10"}
        ]

        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.competitions_patcher = patch('server.loadCompetitions', return_value=self.mock_competitions)
        self.save_patcher = patch('server.save_clubs')

        self.mock_load_clubs = self.clubs_patcher.start()
        self.mock_load_competitions = self.competitions_patcher.start()
        self.mock_save = self.save_patcher.start()

    def tearDown(self):
        # Clean up patches after each test
        self.clubs_patcher.stop()
        self.competitions_patcher.stop()
        self.save_patcher.stop()

    # Test: Valid booking deducts points from the club
    def test_points_deduction_after_booking(self):
        """Integration test: Complete booking workflow with points deduction"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': 'Simply Lift',
                            'competition': 'Spring Festival',
                            'places': '3'
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Great-booking complete!', response.data)
                    self.assertIn(b"Points available: 10", response.data)

    # Test: Club cannot book more places than allowed (overbooking prevention)
    def test_overbooking_prevention(self):
        """Integration test: Error handling for overbooking"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': 'Simply Lift',
                            'competition': 'Spring Festival',
                            'places': '15'
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Cannot book more than 13 points', response.data)
                    self.assertIn(b"Points available: 13", response.data)


if __name__ == '__main__':
    unittest.main()