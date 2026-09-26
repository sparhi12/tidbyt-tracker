"""
Unit tests for airport database resolution.
"""

import unittest
from tracker.airports import resolve_airport

class TestAirports(unittest.TestCase):
    def test_local_airports(self):
        self.assertEqual(resolve_airport("KSEA"), ("SEA", "Seattle"))
        self.assertEqual(resolve_airport("SEA"), ("SEA", "Seattle"))
        self.assertEqual(resolve_airport("KBFI"), ("BFI", "Seattle Boeing"))
        self.assertEqual(resolve_airport("KPAE"), ("PAE", "Everett"))
        self.assertEqual(resolve_airport("KPDX"), ("PDX", "Portland"))

    def test_major_us_airports(self):
        self.assertEqual(resolve_airport("KLAX"), ("LAX", "Los Angeles"))
        self.assertEqual(resolve_airport("KSFO"), ("SFO", "San Francisco"))
        self.assertEqual(resolve_airport("KJFK"), ("JFK", "New York JFK"))
        self.assertEqual(resolve_airport("KORD"), ("ORD", "Chicago O'Hare"))
        self.assertEqual(resolve_airport("KATL"), ("ATL", "Atlanta"))

    def test_international_airports(self):
        self.assertEqual(resolve_airport("CYVR"), ("YVR", "Vancouver"))
        self.assertEqual(resolve_airport("EGLL"), ("LHR", "London Heathrow"))
        self.assertEqual(resolve_airport("RJTT"), ("HND", "Tokyo Haneda"))

    def test_fallback(self):
        self.assertEqual(resolve_airport(None), ("---", "Unknown"))
        self.assertEqual(resolve_airport(""), ("---", "Unknown"))

if __name__ == "__main__":
    unittest.main()
