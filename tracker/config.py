"""
Configuration manager for Tidbyt Flight Tracker.
Loads variables from environment or local .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Config:
    # Tidbyt settings
    TIDBYT_DEVICE_ID = os.getenv("TIDBYT_DEVICE_ID", "")
    TIDBYT_API_KEY = os.getenv("TIDBYT_API_KEY", "")
    TIDBYT_INSTALLATION_ID = os.getenv("TIDBYT_INSTALLATION_ID", "FlightTracker")

    # Data provider: 'airplanes_live', 'opensky', or 'dual' (tries airplanes_live, falls back to opensky)
    DATA_SOURCE = os.getenv("DATA_SOURCE", "dual").lower()

    # OpenSky Network credentials
    OPENSKY_USERNAME = os.getenv("OPENSKY_USERNAME", "")
    OPENSKY_PASSWORD = os.getenv("OPENSKY_PASSWORD", "")
    OPENSKY_CLIENT_ID = os.getenv("OPENSKY_CLIENT_ID", "")
    OPENSKY_CLIENT_SECRET = os.getenv("OPENSKY_CLIENT_SECRET", "")
    OPENSKY_POLL_INTERVAL = int(os.getenv("OPENSKY_POLL_INTERVAL", "22"))

    # Geographic reference point: Denny Way & Westlake Ave, Seattle
    REF_LAT = float(os.getenv("REF_LAT", "47.6186"))
    REF_LON = float(os.getenv("REF_LON", "-122.3365"))
    MAX_RADIUS_MILES = float(os.getenv("MAX_RADIUS_MILES", "15.0"))

    # Display update interval
    POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))

    # Clock settings: show or hide jumping second hand
    SHOW_SECOND_HAND = os.getenv("SHOW_SECOND_HAND", "false").lower() in ("true", "1", "yes")

    # Flight selection priority: Eastern hemisphere (0° to 180° / N -> E -> S)
    EASTERN_PRIORITY = os.getenv("EASTERN_PRIORITY", "true").lower() in ("true", "1", "yes")

    # Paths
    PIXLET_BIN = os.getenv("PIXLET_BIN", "pixlet")
    BASE_DIR = Path(__file__).parent.parent
    STAR_PATH = os.getenv("STAR_PATH", str(BASE_DIR / "display" / "flight.star"))
    OUTPUT_IMAGE = os.getenv("OUTPUT_IMAGE", "/tmp/tidbyt_flight.webp")
