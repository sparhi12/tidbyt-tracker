import unittest
from datetime import datetime
from tracker.palette import PALETTES, get_palette_for_time

class TestPalette(unittest.TestCase):
    def test_palettes_exist_and_have_all_rows(self):
        for mode in ("day", "sunset", "night"):
            self.assertIn(mode, PALETTES)
            palette = PALETTES[mode]
            self.assertIn("name", palette)
            for r in range(1, 6):
                key = f"row{r}"
                self.assertIn(key, palette)
                self.assertTrue(palette[key].startswith("#"))
                self.assertEqual(len(palette[key]), 7)

    def test_8_hour_rotation_night(self):
        # 00:00 to 07:59 should be night
        dt = datetime(2026, 10, 10, 3, 30)
        palette = get_palette_for_time(dt, mode="auto")
        self.assertEqual(palette["name"], "Midnight Aurora")

    def test_8_hour_rotation_day(self):
        # 08:00 to 15:59 should be day
        dt = datetime(2026, 10, 10, 11, 45)
        palette = get_palette_for_time(dt, mode="auto")
        self.assertEqual(palette["name"], "Pacific Aviation")

    def test_8_hour_rotation_sunset(self):
        # 16:00 to 23:59 should be sunset
        dt = datetime(2026, 10, 10, 19, 15)
        palette = get_palette_for_time(dt, mode="auto")
        self.assertEqual(palette["name"], "Golden Sunset")

    def test_mode_override(self):
        # When explicit mode is passed, it should override datetime
        dt = datetime(2026, 10, 10, 3, 0)  # night time
        palette = get_palette_for_time(dt, mode="sunset")
        self.assertEqual(palette["name"], "Golden Sunset")
