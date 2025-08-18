import json
import unittest
from datetime import datetime, timedelta

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
        test_club = self.clubs[0]
        test_competition = self.competitions[0]

        with self.client as c:
            # Make booking request
            response = c.post(
                '/purchasePlaces',
                data={
                    'club': test_club['name'],
                    'competition': test_competition['name'],
                    'places': '3'
                },
                follow_redirects=True
            )

            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Great-booking complete!', response.data)

            # Verify points in response HTML
            self.assertIn(f"Points available: {10}".encode(), response.data)


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


########################## FUTURE / PAST COMPETITIONS ##########################

    def test_book_with_future_competition(self):
        """Book places for a competition with a future date."""
        future_comp = next(
            comp for comp in self.competitions
            if comp["date"] > "2025-01-01"
        )
        response = self.client.get(f"/book/{future_comp['name']}/Simply Lift")
        assert response.status_code == 200
        assert future_comp["name"].encode() in response.data


    def test_book_with_past_competition(self):
        """Try booking for a past competition."""
        past_comp = next(
            comp for comp in self.competitions
            if comp["date"] < "2025-01-01"
        )

        response = self.client.get(f"/book/{past_comp['name']}/Simply Lift")
        assert response.status_code == 302
        assert "/showSummary" in response.headers["Location"]


    def test_competition_today(self):
        future_time = (datetime.now() + timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
        today_comp = {'name': 'Today Comp', 'date': future_time, 'numberOfPlaces': '10'}
        competitions.append(today_comp)

        response = self.client.get(f"/book/Today%20Comp/Simply Lift")
        self.assertEqual(response.status_code, 200)

    ##################### MAX 12 PLACES PER BOOKING ######################################

    # Add this helper method inside your TestServer class
    def get_updated_club(self, club_name):
        """Reloads clubs from JSON and returns the specified club."""
        with open('clubs.json') as c:
            clubs = json.load(c)['clubs']
            return next(club for club in clubs if club['name'] == club_name)

    def test_booking_more_than_12_places_fails(self):
        """Booking more than 12 places should not be allowed."""
        club = self.clubs[0]  # Simply Lift has 13 points
        competition = self.competitions[1]  # Fall Classic, 10 places available

        with self.client as c:
            response = c.post(
                '/purchasePlaces',
                data={
                    'club': club['name'],
                    'competition': competition['name'],
                    'places': '13'  # More than 12
                },
                follow_redirects=True
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Cannot book more than 12 places', response.data)
            # Points and numberOfPlaces should remain unchanged
            self.assertEqual(club['points'], 13)
            self.assertEqual(int(competition['numberOfPlaces']), 10)

    def test_booking_less_than_12_places_succeeds(self):
        """Booking fewer than 12 places works normally."""
        club_name = self.clubs[0]['name']  # "Simply Lift"
        competition_name = self.competitions[1]['name']  # "Fall Classic"

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

            # Get the UPDATED club data before asserting
            updated_club = self.get_updated_club(club_name)
            self.assertEqual(int(updated_club['points']), 8)  # Initial 13 - 5 = 8

    def test_booking_12_places_succeeds(self):
        """Booking exactly 12 places should succeed if enough points."""
        club_name = self.clubs[0]['name']  # Simply Lift, 13 points
        competition_name = self.competitions[0]['name']  # Spring Festival, 13 places

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

            # Get the UPDATED club and competition data before asserting
            updated_club = self.get_updated_club(club_name)
            # You would need a similar helper for competitions if you assert on it
            # updated_competition = self.get_updated_competition(competition_name)

            self.assertEqual(int(updated_club['points']), 1)  # Initial 13 - 12 = 1
            # self.assertEqual(int(updated_competition['numberOfPlaces']), 1)


if __name__ == '__main__':
    unittest.main()