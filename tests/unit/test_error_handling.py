import unittest
from unittest.mock import patch
from server import app


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        ]

        self.mock_competitions = [
            {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "13"}
        ]

        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.competitions_patcher = patch('server.loadCompetitions', return_value=self.mock_competitions)
        self.mock_load_clubs = self.clubs_patcher.start()
        self.mock_load_competitions = self.competitions_patcher.start()

    def tearDown(self):
        self.clubs_patcher.stop()
        self.competitions_patcher.stop()

    def test_book_nonexistent_competition(self):
        """Unit test: Error handling for non-existent competition"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                response = self.client.get('/book/Nonexistent Competition/Simply Lift', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Error: Competition or club not found', response.data)

    def test_book_nonexistent_club(self):
        """Unit test: Error handling for non-existent club"""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                response = self.client.get('/book/Spring Festival/Nonexistent Club', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Error: Competition or club not found', response.data)

if __name__ == '__main__':
    unittest.main()