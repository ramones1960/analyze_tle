import unittest
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orbit_propagator import propagate_orbit

class TestOrbitPropagator(unittest.TestCase):
    def setUp(self):
        self.tle_line1 = "1 25544U 98067A   25340.55621404  .00016717  00000+0  30129-3 0  9993"
        self.tle_line2 = "2 25544  51.6396 235.9181 0006764 266.3025 210.1504 15.49479342528256"
        self.count = 10
        self.step = 60

    def test_propagation_result_structure(self):
        """Test if the propagator returns the correct structure and count."""
        results, epoch_str = propagate_orbit(self.tle_line1, self.tle_line2, self.step, self.count)
        
        # Check return count
        self.assertEqual(len(results), self.count)
        
        # Check epoch string presence
        self.assertIsInstance(epoch_str, str)
        self.assertIn("UTC", epoch_str) # Standard Skyfield output usually contains UTC
        
        # Check first point integrity
        point = results[0]
        required_keys = ['time', 'latitude', 'longitude', 'altitude_km', 'eci', 'ecef']
        for key in required_keys:
            self.assertIn(key, point)
            
        # Check ECI/ECEF structure
        self.assertIn('x', point['eci'])
        self.assertIn('y', point['eci'])
        self.assertIn('z', point['eci'])
        self.assertIn('x', point['ecef'])

    def test_values_range(self):
        """Test if propagated values are within reasonable ranges."""
        # Use TLE epoch approx (2025-12-06)
        start_time = datetime(2025, 12, 6, 13, 0, 0)
        results, _ = propagate_orbit(self.tle_line1, self.tle_line2, 60, 5, start_time=start_time)
        
        for p in results:
            print(f"DEBUG POINT: {p}")
            self.assertTrue(bool(-90 <= p['latitude'] <= 90))
            self.assertTrue(bool(-180 <= p['longitude'] <= 180))
            # ISS altitude roughly 400km
            alt = float(p['altitude_km'])
            self.assertTrue(300 < alt < 500, f"Altitude {alt} out of range")

if __name__ == '__main__':
    unittest.main()
