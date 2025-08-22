import unittest
from unittest.mock import patch, mock_open
from server import save_clubs, save_competitions, clubs, competitions


class TestUtilityFunctions(unittest.TestCase):
    def setUp(self):
        # Mock the global data that save functions will use
        self.original_clubs = clubs[:]
        self.original_competitions = competitions[:]

    def tearDown(self):
        # placeholder to Restore original data
        pass

    def test_save_clubs_function(self):
        """Unit test: save_clubs file operation"""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_dump:
                save_clubs()

                # Verify file operations
                mock_file.assert_called_once_with('clubs.json', 'w')
                # Verify that json.dump() was called to write data
                mock_dump.assert_called_once()


    def test_save_competitions_function(self):
        """Unit test: save_competitions file operation"""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_dump:
                save_competitions()

                # Verify file operations
                mock_file.assert_called_once_with('competitions.json', 'w')
                mock_dump.assert_called_once()


if __name__ == '__main__':
    unittest.main()