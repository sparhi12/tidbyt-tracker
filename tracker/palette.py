"""
Color palette manager for Tidbyt Flight Tracker.
Provides aesthetically cohesive color combinations designed specifically for 
64x32 LED matrix displays, with automatic 8-hour time-of-day rotation.
"""

from datetime import datetime
from typing import Dict, Optional

# Curated, cohesive palettes for Tidbyt LED displays
PALETTES = {
    # 08:00 - 15:59: Crisp daytime skies and cool aviation avionics
    "day": {
        "name": "Pacific Aviation",
        "row1": "#38BDF8",  # Sky Blue (Flight No)
        "row2": "#2DD4BF",  # Aqua Teal (Direction & Distance)
        "row3": "#22D3EE",  # Soft Cyan (Route Codes)
        "row4": "#7DD3FC",  # Ice Blue (Airline)
        "row5": "#E2E8F0",  # Crisp Mist (Cities)
    },
    # 16:00 - 23:59: Golden sunset tones, warm and gentle for evening
    "sunset": {
        "name": "Golden Sunset",
        "row1": "#FBBF24",  # Warm Amber (Flight No)
        "row2": "#FDBA74",  # Soft Peach (Direction & Distance)
        "row3": "#FB7185",  # Coral Sunset (Route Codes)
        "row4": "#FDE047",  # Champagne (Airline)
        "row5": "#FEF3C7",  # Warm Cream (Cities)
    },
    # 00:00 - 07:59: Night-vision soothing tones, low glare for dark rooms
    "night": {
        "name": "Midnight Aurora",
        "row1": "#34D399",  # Mint Jade (Flight No)
        "row2": "#6EE7B7",  # Soft Emerald (Direction & Distance)
        "row3": "#A7F3D0",  # Seafoam (Route Codes)
        "row4": "#C084FC",  # Soft Lavender (Airline)
        "row5": "#CBD5E1",  # Slate Silver (Cities)
    },
}

def get_palette_for_time(dt: Optional[datetime] = None, mode: str = "auto") -> Dict[str, str]:
    """
    Get the color palette for the given datetime or mode.
    
    Modes:
      - 'auto': 8-hour rotation based on local hour:
          * 00:00 - 07:59 (Period 0): 'night' (Midnight Aurora)
          * 08:00 - 15:59 (Period 1): 'day' (Pacific Aviation)
          * 16:00 - 23:59 (Period 2): 'sunset' (Golden Sunset)
      - 'day', 'sunset', 'night': lock into that specific palette
    """
    if mode in PALETTES:
        return PALETTES[mode]

    if dt is None:
        dt = datetime.now()

    hour = dt.hour
    if 0 <= hour < 8:
        return PALETTES["night"]
    elif 8 <= hour < 16:
        return PALETTES["day"]
    else:
        return PALETTES["sunset"]
