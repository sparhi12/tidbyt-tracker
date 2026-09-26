"""
Unit tests for airline database resolution.
"""

import unittest
from tracker.airlines import resolve_airline

class TestAirlines(unittest.TestCase):
    def test_major_us_airlines(self):
        self.assertEqual(resolve_airline("ASA1762"), "Alaska Airlines")
        self.assertEqual(resolve_airline("DAL1090"), "Delta Air Lines")
        self.assertEqual(resolve_airline("UAL234"), "United Airlines")
        self.assertEqual(resolve_airline("SWA120"), "Southwest Airlines")
        self.assertEqual(resolve_airline("AAL55"), "American Airlines")
        self.assertEqual(resolve_airline("SKW3412"), "SkyWest Airlines")

    def test_international_airlines(self):
        self.assertEqual(resolve_airline("ACA598"), "Air Canada")
        self.assertEqual(resolve_airline("BAW48"), "British Airways")
        self.assertEqual(resolve_airline("JAL68"), "Japan Airlines")
        self.assertEqual(resolve_airline("KAL041"), "Korean Air")
        self.assertEqual(resolve_airline("DLH490"), "Lufthansa")

    def test_general_aviation(self):
        self.assertEqual(resolve_airline("N12345"), "General Aviation")
        self.assertEqual(resolve_airline("N9655B"), "General Aviation")

    def test_unknown(self):
        self.assertEqual(resolve_airline(""), "Unknown Flight")
        self.assertEqual(resolve_airline(None), "Unknown Flight")

if __name__ == "__main__":
    unittest.main()
