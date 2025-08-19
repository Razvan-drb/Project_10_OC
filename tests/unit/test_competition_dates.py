import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from server import app

class TestCompetitionDates(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        # Create mock test data
        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
        ]

        self.mock_competitions = [
            {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "13"},
            {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "10"}
        ]

        # Patch load functions
        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.competitions_patcher = patch('server.loadCompetitions', return_value=self.mock_competitions)
        self.mock_load_clubs = self.clubs_patcher.start()
        self.mock_load_competitions = self.competitions_patcher.start()

    def tearDown(self):
        self.clubs_patcher.stop()
        self.competitions_patcher.stop()

    def test_book_with_future_competition(self):
        """Unit test: Booking with future competition date should work"""
        future_comp = self.mock_competitions[1]  # Fall Classic 2025

        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                response = self.client.get(f"/book/{future_comp['name']}/Simply Lift")
                self.assertEqual(response.status_code, 200)
                self.assertIn(future_comp["name"].encode(), response.data)

    def test_book_with_past_competition(self):
        """Unit test: Booking with past competition date should redirect"""
        # Add a past competition to mock data for this test
        past_comp = {"name": "Past Competition", "date": "2020-01-01 10:00:00", "numberOfPlaces": "5"}
        self.mock_competitions.append(past_comp)

        try:
            with patch('server.competitions', self.mock_competitions):
                with patch('server.clubs', self.mock_clubs):
                    response = self.client.get(f"/book/{past_comp['name']}/Simply Lift")
                    self.assertEqual(response.status_code, 302)
                    self.assertIn("/showSummary", response.headers["Location"])
        finally:
            # Clean up
            self.mock_competitions.remove(past_comp)

    def test_competition_today(self):
        """Unit test: Booking with competition happening today should work"""
        future_time = (datetime.now() + timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
        today_comp = {'name': 'Today Comp', 'date': future_time, 'numberOfPlaces': '10'}
        self.mock_competitions.append(today_comp)

        try:
            with patch('server.competitions', self.mock_competitions):
                with patch('server.clubs', self.mock_clubs):
                    response = self.client.get(f"/book/Today%20Comp/Simply Lift")
                    self.assertEqual(response.status_code, 200)
        finally:
            # Clean up
            self.mock_competitions.remove(today_comp)

if __name__ == '__main__':
    unittest.main()