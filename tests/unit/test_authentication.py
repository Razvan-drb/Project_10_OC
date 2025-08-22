import unittest
from unittest.mock import patch
from server import app

"""
UNIT TESTS: Authentication functionality
Evaluation: Tests individual authentication functions
Email validation, login, logout
"""

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        # Create mock test data
        self.mock_clubs = [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
            {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
        ]

        # Patch the load function
        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.mock_load_clubs = self.clubs_patcher.start()

        self.valid_emails = [club['email'] for club in self.mock_clubs]
        self.invalid_email = "unknown@test.com"

    def tearDown(self):
        self.clubs_patcher.stop()

    # Test: Invalid email display an error message
    def test_unknown_email_shows_error(self):
        with self.client as c:
            response = c.post(
                '/showSummary',
                data={'email': self.invalid_email},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Error: Email not found', response.data)

    # Test: All known/valid emails login successfully
    def test_all_valid_emails_work(self):
        for email in self.valid_emails:
            with self.subTest(email=email):
                response = self.client.post(
                    '/showSummary',
                    data={'email': email},
                    follow_redirects=True
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Welcome', response.data)

    # Test: Empty email field return message
    def test_empty_email_shows_error(self):
        with self.client as c:
            response = c.post(
                '/showSummary',
                data={'email': ''},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please enter an email address', response.data)

    # Test: Logout redirect to home page
    def test_logout(self):
        """Unit test: Logout functionality"""
        with self.client as c:
            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'GUDLFT Registration', response.data)

if __name__ == '__main__':
    unittest.main()