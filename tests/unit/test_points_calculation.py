import unittest
from unittest.mock import patch
from server import app


class TestPointsCalculation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
        ]

    def test_points_display(self):
        """Unit test: Points display functionality"""
        with patch('server.clubs', self.mock_clubs):
            with self.client as c:
                response = c.get('/points')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Clubs Points Summary', response.data)
                self.assertIn(b'Simply Lift', response.data)
                self.assertIn(b'13', response.data)
                self.assertIn(b'points', response.data)

if __name__ == '__main__':
    unittest.main()