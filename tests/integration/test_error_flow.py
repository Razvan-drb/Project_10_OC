import unittest
from unittest.mock import patch

from server import app


class TestErrorFlows(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Test data for error cases
        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
        ]

        self.mock_competitions = [
            {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "13"},
            {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "10"}
        ]
        # Patch database functions to use mock data
        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.competitions_patcher = patch('server.loadCompetitions', return_value=self.mock_competitions)
        self.save_patcher = patch('server.save_clubs') # Prevent file writes

        self.mock_load_clubs = self.clubs_patcher.start()
        self.mock_load_competitions = self.competitions_patcher.start()
        self.mock_save = self.save_patcher.start()

    def tearDown(self):
        # Clean up patches after each test
        self.clubs_patcher.stop()
        self.competitions_patcher.stop()
        self.save_patcher.stop()

    # Test: Booking zero places raise an error
    def test_book_zero_places(self):
        """Integration test: Zero places booking error flow"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': 'Simply Lift',
                            'competition': 'Spring Festival',
                            'places': '0' # Must book at least 1 place
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Error: Must book at least 1 place', response.data)

    # Test: Booking negative places raise an error
    def test_book_negative_places(self):
        """Integration test: Negative places booking error flow"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': 'Simply Lift',
                            'competition': 'Spring Festival',
                            'places': '-1'
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Error: Must book at least 1 place', response.data)

    # Test: Booking more places than competition capacity raise an error
    def test_book_more_places_than_available(self):
        """Integration test: Overbooking competition capacity error flow"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': 'Simply Lift',
                            'competition': 'Fall Classic',  # Only 10 places available
                            'places': '11'  # More than available
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Error: Cannot book more than 10 places available', response.data)


if __name__ == '__main__':
    unittest.main()