"""
Airplanes.live / ADSB.lol open ADS-B client.
Free, unmetered public API for hobbyists with sub-second latency and 10s updates.
Endpoint: GET https://api.airplanes.live/v2/point/{lat}/{lon}/{radius}
"""

import logging
import time
from typing import Dict, List
import requests

logger = logging.getLogger(__name__)

class AirplanesLiveClient:
    BASE_URL = "https://api.airplanes.live/v2/point"

    def __init__(self, timeout_seconds: float = 4.0):
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (TidbytFlightTracker/2.0; Linux x86_64) AppleWebKit/537.36"
        })

    def get_aircraft(self, center_lat: float, center_lon: float, radius_nm: float = 15.0) -> List[Dict]:
        """
        Fetch live aircraft within radius_nm nautical miles of (center_lat, center_lon).
        """
        url = f"{self.BASE_URL}/{center_lat:.4f}/{center_lon:.4f}/{int(radius_nm)}"
        now = time.time()

        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                ac_list = data.get("ac") or []
                results = []

                for ac in ac_list:
                    lat = ac.get("lat")
                    lon = ac.get("lon")
                    if lat is None or lon is None:
                        continue

                    raw_flight = (ac.get("flight") or "").strip()
                    hex_code = (ac.get("hex") or "").lower()
                    flight_no = raw_flight if raw_flight else hex_code.upper()

                    alt_baro = ac.get("alt_baro")
                    on_ground = (alt_baro == "ground")
                    alt_m = 0.0
                    if isinstance(alt_baro, (int, float)):
                        alt_m = alt_baro * 0.3048  # feet to meters

                    # Ground speed: in knots, convert to m/s
                    gs_knots = ac.get("gs")
                    velocity_mps = (gs_knots * 0.514444) if isinstance(gs_knots, (int, float)) else None

                    track = ac.get("track")
                    track_deg = float(track) if isinstance(track, (int, float)) else None

                    results.append({
                        "hex": hex_code,
                        "flight": flight_no,
                        "lat": float(lat),
                        "lon": float(lon),
                        "alt_m": alt_m,
                        "on_ground": on_ground,
                        "velocity": velocity_mps,
                        "track": track_deg,
                        "source": "airplanes_live",
                        "updated_at": now,
                    })

                return results
            else:
                logger.debug(f"Airplanes.live returned status {resp.status_code}")

        except Exception as e:
            logger.debug(f"Airplanes.live request error: {e}")

        return []
