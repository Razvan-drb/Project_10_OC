import unittest
from server import app, loadClubs, competitions, clubs, loadCompetitions


class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.clubs = loadClubs()
        self.competitions = loadCompetitions()
        self.valid_emails = [club['email'] for club in self.clubs]
        self.invalid_email = "unknown@test.com"

##################### LOGIN / EMAIL ######################################
    def test_unknown_email_shows_error(self):
        with self.client as c:
            response = c.post(
                '/showSummary',
                data={'email': self.invalid_email},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Error: Email not found', response.data)

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

    def test_empty_email_shows_error(self):
        with self.client as c:
            response = c.post(
                '/showSummary',
                data={'email': ''},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please enter an email address', response.data)

######################### PLACES / POINTS ##################################################

    def test_points_deduction_after_booking(self):
        # Setup test data
        test_club = self.clubs[0]  # "Simply Lift" with 13 points
        test_competition = self.competitions[0]  # "Spring Festival"

        with self.client as c:
            # Make booking request
            response = c.post(
                '/purchasePlaces',
                data={
                    'club': test_club['name'],
                    'competition': test_competition['name'],
                    'places': '3'  # String because form data
                },
                follow_redirects=True
            )

            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Great-booking complete!', response.data)

            # Verify points in response HTML
            self.assertIn(f"Points available: {10}".encode(), response.data)  # 13 - 3 = 10

    def test_overbooking_prevention(self):
        test_club = self.clubs[0]  # "Simply Lift" with 13 points
        test_competition = self.competitions[0]  # "Spring Festival"

        with self.client as c:
            response = c.post(
                '/purchasePlaces',
                data={
                    'club': test_club['name'],
                    'competition': test_competition['name'],
                    'places': '15'  # Try to book more than available points (13)
                },
                follow_redirects=True
            )

            # Should show error but stay on same page (200 OK)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Cannot book more than 13 points', response.data)
            # Verify points remain unchanged
            self.assertIn(f"Points available: {13}".encode(), response.data)

    def test_edge_cases(self):
        test_club = self.clubs[0]
        test_competition = self.competitions[0]

        # Test booking all points
        response = self.client.post(
            '/purchasePlaces',
            data={'club': test_club['name'], 'competition': test_competition['name'], 'places': '13'}
        )
        self.assertIn(b'Points available: 0', response.data)

        # Test negative numbers
        response = self.client.post(
            '/purchasePlaces',
            data={'club': test_club['name'], 'competition': test_competition['name'], 'places': '-1'}
        )
        self.assertIn(b'Must book at least 1 place', response.data)

    def test_points_display(self):
        with self.client as c:
            response = c.get('/points')
            self.assertEqual(response.status_code, 200)
            # Check header and sample club
            self.assertIn(b'Clubs Points Summary', response.data)
            self.assertIn(b'Simply Lift', response.data)
            self.assertIn(b'13 points', response.data)


if __name__ == '__main__':
    unittest.main()