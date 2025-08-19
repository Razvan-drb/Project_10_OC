import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from server import app, loadClubs, competitions, clubs, loadCompetitions, get_club_by_name, get_competition_by_name, \
    save_clubs, save_competitions


class TestServer(unittest.TestCase):
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

        # Patch the load functions to return mock data
        self.clubs_patcher = patch('server.loadClubs', return_value=self.mock_clubs)
        self.competitions_patcher = patch('server.loadCompetitions', return_value=self.mock_competitions)
        self.mock_load_clubs = self.clubs_patcher.start()
        self.mock_load_competitions = self.competitions_patcher.start()

        # Also patch save functions to do nothing (prevent file writes)
        self.save_clubs_patcher = patch('server.save_clubs')
        self.save_competitions_patcher = patch('server.save_competitions')
        self.mock_save_clubs = self.save_clubs_patcher.start()
        self.mock_save_competitions = self.save_competitions_patcher.start()

        # Set up test data for these specific tests
        self.valid_emails = [club['email'] for club in self.mock_clubs]
        self.invalid_email = "unknown@test.com"

    def tearDown(self):
        # Stop all patches
        self.clubs_patcher.stop()
        self.competitions_patcher.stop()
        self.save_clubs_patcher.stop()
        self.save_competitions_patcher.stop()

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
        # Setup test data - use mock data instead of file-loaded data
        test_club = self.mock_clubs[0]  # "Simply Lift" with 13 points
        test_competition = self.mock_competitions[0]  # "Spring Festival"

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

            # Verify points in response HTML - check for updated points (10)
            self.assertIn(b"Points available: 10", response.data)

    def test_overbooking_prevention(self):
        test_club = self.mock_clubs[0]  # "Simply Lift" with 13 points
        test_competition = self.mock_competitions[0]  # "Spring Festival"

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
            # Verify points remain unchanged - check for original points (13)
            self.assertIn(b"Points available: 13", response.data)

    def test_points_display(self):
        # Patch the pointsDisplay route to use mock clubs
        with patch('server.clubs', self.mock_clubs):
            with self.client as c:
                response = c.get('/points')
                self.assertEqual(response.status_code, 200)
                # Check header and sample club
                self.assertIn(b'Clubs Points Summary', response.data)
                self.assertIn(b'Simply Lift', response.data)
                self.assertIn(b'13', response.data)  # Just check for the number
                self.assertIn(b'points', response.data)  # Check separately if needed

    ########################## BOOK FUTURE / PAST COMPETITIONS ##########################

    def test_book_with_future_competition(self):
        """Book places for a competition with a future date."""
        future_comp = self.mock_competitions[1]  # Use the first future competition

        # Patch the global variables that the routes actually use
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                response = self.client.get(f"/book/{future_comp['name']}/Simply Lift")
                self.assertEqual(response.status_code, 200)
                self.assertIn(future_comp["name"].encode(), response.data)

    def test_book_with_past_competition(self):
        """Try booking for a past competition."""
        # Add a past competition to mock data for this test
        past_comp = {"name": "Past Competition", "date": "2020-01-01 10:00:00", "numberOfPlaces": "5"}

        # Temporarily add past competition to mock data and patch globals
        self.mock_competitions.append(past_comp)

        try:
            with patch('server.competitions', self.mock_competitions):
                with patch('server.clubs', self.mock_clubs):
                    response = self.client.get(f"/book/{past_comp['name']}/Simply Lift")
                    self.assertEqual(response.status_code, 302)
                    self.assertIn("/showSummary", response.headers["Location"])
        finally:
            # Clean up - remove the past competition
            self.mock_competitions.remove(past_comp)

    def test_competition_today(self):
        future_time = (datetime.now() + timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
        today_comp = {'name': 'Today Comp', 'date': future_time, 'numberOfPlaces': '10'}

        # Temporarily add today's competition to mock data
        self.mock_competitions.append(today_comp)

        try:
            # Patch the global competitions list for this test
            with patch('server.competitions', self.mock_competitions):
                response = self.client.get(f"/book/Today%20Comp/Simply Lift")
                self.assertEqual(response.status_code, 200)
        finally:
            # Clean up - remove the today competition
            self.mock_competitions.remove(today_comp)

    ##################### MAX 12 PLACES PER BOOKING ######################################

    def get_updated_club(self, club_name):
        """Get club from current mock data (simulates reloading)"""
        return next(club for club in self.mock_clubs if club['name'] == club_name)

    def get_updated_competition(self, competition_name):
        """Get competition from current mock data (simulates reloading)"""
        return next(comp for comp in self.mock_competitions if comp['name'] == competition_name)

    def test_booking_more_than_12_places_fails(self):
        """Booking more than 12 places should not be allowed."""
        club_name = self.mock_clubs[0]['name']  # Simply Lift has 13 points
        competition_name = self.mock_competitions[1]['name']  # Fall Classic, 10 places available

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

                    # Check mock data remains unchanged
                    club = self.get_updated_club(club_name)
                    competition = self.get_updated_competition(competition_name)

                    # Ensure points and numberOfPlaces remain unchanged
                    self.assertEqual(int(club['points']), 13)
                    self.assertEqual(int(competition['numberOfPlaces']), 10)

    def test_booking_less_than_12_places_succeeds(self):
        """Booking fewer than 12 places works normally."""
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

                    # Check mock data was updated
                    updated_club = self.get_updated_club(club_name)
                    self.assertEqual(int(updated_club['points']), 8)  # Initial 13 - 5 = 8

    def test_booking_12_places_succeeds(self):
        """Booking exactly 12 places should succeed if enough points."""
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

                    # Check mock data was updated
                    updated_club = self.get_updated_club(club_name)
                    self.assertEqual(int(updated_club['points']), 1)  # 13 - 12 = 1

    def test_book_zero_places(self):
        """Test booking zero places (triggers places_required <= 0)."""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                with self.client as c:
                    response = c.post(
                        '/purchasePlaces',
                        data={
                            'club': 'Simply Lift',
                            'competition': 'Spring Festival',
                            'places': '0'
                        },
                        follow_redirects=True
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Error: Must book at least 1 place', response.data)

    def test_book_negative_places(self):
        """Test booking negative places (also triggers places_required <= 0)."""
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

    def test_book_more_places_than_available(self):
        """Test booking more places than competition has available."""
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
                    print(f"Response status: {response.status_code}")
                    print(f"Response data: {response.data[:500]}...")  # Debug
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Error: Cannot book more than 10 places available', response.data)

    def test_book_nonexistent_competition(self):
        """Test booking with non-existent competition (triggers not comp)."""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                response = self.client.get('/book/Nonexistent Competition/Simply Lift', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Error: Competition or club not found', response.data)

    def test_book_nonexistent_club(self):
        """Test booking with non-existent club (triggers not club_data)."""
        with patch('server.competitions', self.mock_competitions):
            with patch('server.clubs', self.mock_clubs):
                response = self.client.get('/book/Spring Festival/Nonexistent Club', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Error: Competition or club not found', response.data)




    #########" LOGOUT #############"

    def test_logout(self):
        """Test logout redirects to index."""
        with self.client as c:
            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'GUDLFT Registration', response.data)

    ##########" SAVE COMP /CLUB #################

    def test_save_clubs_function(self):
        """Test that save_clubs works."""
        # Temporarily unpatch
        self.save_clubs_patcher.stop()

        try:
            # Mock the file operations
            with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
                with patch('json.dump') as mock_dump:
                    save_clubs()

                    # Verify file was opened for writing
                    mock_file.assert_called_once_with('clubs.json', 'w')
                    # Verify json.dump was called
                    mock_dump.assert_called_once()

        finally:
            # Re-patch
            self.save_clubs_patcher.start()

    def test_save_competitions_function(self):
        """Test that save_competitions works."""
        # Temporarily unpatch
        self.save_competitions_patcher.stop()

        try:
            # Mock the file operations
            with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
                with patch('json.dump') as mock_dump:
                    save_competitions()

                    # Verify file was opened for writing
                    mock_file.assert_called_once_with('competitions.json', 'w')
                    # Verify json.dump was called

        finally:
            # Re-patch
            self.save_competitions_patcher.start()


if __name__ == '__main__':
    unittest.main()