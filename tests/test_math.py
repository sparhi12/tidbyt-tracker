"""
Unit tests for geospatial math, compass bearing, row 3 formatting,
and eastern hemisphere priority logic.
"""

import math
import unittest

from tracker.math_utils import (
    bearing_to_compass,
    calculate_bearing,
    format_row3,
    haversine_distance_miles,
    is_eastern_hemisphere,
    project_position,
    select_best_flight,
)

class TestMathUtils(unittest.TestCase):
    def setUp(self):
        # Denny Way & Westlake Ave, Seattle
        self.ref_lat = 47.6186
        self.ref_lon = -122.3365

    def test_haversine_distance(self):
        # Distance to same point is 0
        d_zero = haversine_distance_miles(self.ref_lat, self.ref_lon, self.ref_lat, self.ref_lon)
        self.assertAlmostEqual(d_zero, 0.0, places=4)

        # Distance to Sea-Tac Airport (~11.5 miles south)
        seatac_lat = 47.4502
        seatac_lon = -122.3088
        d_seatac = haversine_distance_miles(self.ref_lat, self.ref_lon, seatac_lat, seatac_lon)
        self.assertTrue(11.0 <= d_seatac <= 12.5)

    def test_bearing_cardinal_directions(self):
        # North: Lake Union (47.635, -122.3365)
        bearing_n = calculate_bearing(self.ref_lat, self.ref_lon, 47.6350, -122.3365)
        self.assertAlmostEqual(bearing_n, 0.0, delta=1.0)
        self.assertEqual(bearing_to_compass(bearing_n), "N")

        # East: Bellevue (47.6186, -122.2000)
        bearing_e = calculate_bearing(self.ref_lat, self.ref_lon, 47.6186, -122.2000)
        self.assertAlmostEqual(bearing_e, 90.0, delta=2.0)
        self.assertEqual(bearing_to_compass(bearing_e), "E")

        # South: SeaTac (47.4500, -122.3365)
        bearing_s = calculate_bearing(self.ref_lat, self.ref_lon, 47.4500, -122.3365)
        self.assertAlmostEqual(bearing_s, 180.0, delta=1.0)
        self.assertEqual(bearing_to_compass(bearing_s), "S")

        # West: Bainbridge Island (47.6186, -122.5000)
        bearing_w = calculate_bearing(self.ref_lat, self.ref_lon, 47.6186, -122.5000)
        self.assertAlmostEqual(bearing_w, 270.0, delta=2.0)
        self.assertEqual(bearing_to_compass(bearing_w), "w")

    def test_eastern_hemisphere(self):
        # 0° to 180° is eastern hemisphere (North -> East -> South)
        self.assertTrue(is_eastern_hemisphere(0.0))
        self.assertTrue(is_eastern_hemisphere(45.0))
        self.assertTrue(is_eastern_hemisphere(90.0))
        self.assertTrue(is_eastern_hemisphere(135.0))
        self.assertTrue(is_eastern_hemisphere(180.0))

        # 180.1° to 359.9° is western hemisphere
        self.assertFalse(is_eastern_hemisphere(185.0))
        self.assertFalse(is_eastern_hemisphere(270.0))
        self.assertFalse(is_eastern_hemisphere(315.0))

    def test_format_row3_no_miles(self):
        # Single directional arrow and distance without 'm' suffix
        res_01 = format_row3("Nw", 0.12)
        self.assertEqual(res_01, "Nw^0.1")
        self.assertNotIn("m", res_01)

        res_zero = format_row3("N", 0.02)
        self.assertEqual(res_zero, "N^0.0")

        res_14 = format_row3("E", 1.44)
        self.assertEqual(res_14, "E>1.4")

        res_12 = format_row3("SE", 12.3)
        self.assertEqual(res_12, "SEv12")

    def test_eastern_priority_selection(self):
        # Airplane 1: West (Bainbridge Island, 270°), 4 miles away
        plane_west = {
            "flight": "DAL123",
            "lat": 47.6186,
            "lon": -122.4200,  # ~4 miles west
            "on_ground": False,
        }

        # Airplane 2: East (Capitol Hill / Lake Washington, 90°), 7 miles away
        plane_east = {
            "flight": "ASA456",
            "lat": 47.6186,
            "lon": -122.1800,  # ~7 miles east
            "on_ground": False,
        }

        aircraft = [plane_west, plane_east]

        # With eastern_priority = True: plane_east should be selected even though plane_west is closer
        selected = select_best_flight(aircraft, self.ref_lat, self.ref_lon, eastern_priority=True)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["flight"], "ASA456")

        # With eastern_priority = False: plane_west should be selected because it is strictly closer
        selected_raw = select_best_flight(aircraft, self.ref_lat, self.ref_lon, eastern_priority=False)
        self.assertIsNotNone(selected_raw)
        self.assertEqual(selected_raw["flight"], "DAL123")

    def test_dead_reckoning_projection(self):
        # Flying north (track 0°) at 100 m/s for 10 seconds -> 1000m north
        new_lat, new_lon = project_position(47.6000, -122.3300, velocity_mps=100.0, track_deg=0.0, dt_seconds=10.0)
        self.assertGreater(new_lat, 47.6000)
        self.assertAlmostEqual(new_lon, -122.3300, places=4)

if __name__ == "__main__":
    unittest.main()
