import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_fetcher import get_tle_by_intdes

class TestDataFetcher(unittest.TestCase):
    
    @patch('src.data_fetcher.requests.get')
    def test_fetch_success(self, mock_get):
        """Test successful TLE retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Mocking CSV response from CelesTrak (3 lines usually for GP)
        # Assuming module returns list of lines or dict?
        # Let's check source code... wait, I recall it returns (name, line1, line2).
        
        # GP format sample
        fake_content = (
            "OBJECT_NAME\n"
            "1 12345U 98067A   20340.00000000  .00000000  00000-0  00000-0 0  9990\n"
            "2 12345  00.0000   0.0000 0000000   0.0000   0.0000 00.00000000    0\n"
        )
        mock_response.text = fake_content
        mock_get.return_value = mock_response
        
        result = get_tle_by_intdes("12345")
        
        self.assertIsNotNone(result)
        l1, l2, name = result
        self.assertEqual(name, "OBJECT_NAME")
        self.assertTrue(l1.startswith("1 12345"))
        self.assertTrue(l2.startswith("2 12345"))

    @patch('src.data_fetcher.requests.get')
    def test_fetch_failure(self, mock_get):
        """Test API failure handling."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = get_tle_by_intdes("INVALID")
        self.assertEqual(result, (None, None, None))

if __name__ == '__main__':
    unittest.main()
