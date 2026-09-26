"""
OpenSky Network API client.
Supports HTTP Basic Auth (username:password) and OAuth2 Client Credentials.
Queries aircraft state vectors within a geographic bounding box.
"""

import base64
import logging
import time
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

class OpenSkyClient:
    BASE_URL = "https://opensky-network.org/api"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout_seconds: float = 6.0
    ):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout_seconds
        self.session = requests.Session()

        # OAuth2 token state
        self._oauth_token: Optional[str] = None
        self._token_expires_at: float = 0.0

        # Rate limit backoff tracking
        self._backoff_until: float = 0.0

    def _get_oauth_token(self) -> Optional[str]:
        if not self.client_id or not self.client_secret:
            return None

        now = time.time()
        if self._oauth_token and now < (self._token_expires_at - 60):
            return self._oauth_token

        token_url = "https://opensky-network.org/api/auth/token"
        try:
            resp = self.session.post(
                token_url,
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._oauth_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                self._token_expires_at = now + expires_in
                logger.info("Successfully refreshed OpenSky OAuth2 token.")
                return self._oauth_token
            else:
                logger.warning(f"OpenSky OAuth2 token fetch failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.warning(f"OpenSky OAuth2 request error: {e}")

        return None

    def get_aircraft(
        self,
        center_lat: float,
        center_lon: float,
        box_deg: float = 0.35
    ) -> List[Dict]:
        """
        Fetch aircraft state vectors in bounding box around (center_lat, center_lon).
        """
        now = time.time()
        if now < self._backoff_until:
            logger.debug(f"OpenSky in backoff period for {int(self._backoff_until - now)}s.")
            return []

        lamin = center_lat - box_deg
        lamax = center_lat + box_deg
        lomin = center_lon - (box_deg * 1.3)
        lomax = center_lon + (box_deg * 1.3)

        url = f"{self.BASE_URL}/states/all"
        params = {
            "lamin": f"{lamin:.4f}",
            "lamax": f"{lamax:.4f}",
            "lomin": f"{lomin:.4f}",
            "lomax": f"{lomax:.4f}",
        }

        headers = {"User-Agent": "TidbytFlightTracker/2.0"}
        auth = None

        oauth_token = self._get_oauth_token()
        if oauth_token:
            headers["Authorization"] = f"Bearer {oauth_token}"
        elif self.username and self.password:
            auth = (self.username, self.password)

        try:
            resp = self.session.get(url, params=params, headers=headers, auth=auth, timeout=self.timeout)

            if resp.status_code == 200:
                data = resp.json()
                raw_states = data.get("states") or []
                aircraft_list = []
                for s in raw_states:
                    if len(s) < 11:
                        continue
                    icao24 = s[0] or ""
                    callsign = (s[1] or "").strip()
                    country = s[2] or ""
                    lon = s[5]
                    lat = s[6]
                    baro_alt = s[7]
                    on_ground = bool(s[8])
                    velocity = s[9]   # m/s
                    track = s[10]     # degrees

                    if lat is None or lon is None:
                        continue

                    aircraft_list.append({
                        "hex": icao24,
                        "flight": callsign if callsign else icao24.upper(),
                        "country": country,
                        "lat": float(lat),
                        "lon": float(lon),
                        "alt_m": float(baro_alt) if baro_alt is not None else 0.0,
                        "on_ground": on_ground,
                        "velocity": float(velocity) if velocity is not None else None,
                        "track": float(track) if track is not None else None,
                        "source": "opensky",
                        "updated_at": now,
                    })
                return aircraft_list

            elif resp.status_code == 429:
                logger.warning("OpenSky rate limit hit (429 Too Many Requests). Backing off 60s.")
                self._backoff_until = now + 60.0
            else:
                logger.warning(f"OpenSky request returned status {resp.status_code}: {resp.text[:100]}")

        except Exception as e:
            logger.warning(f"OpenSky connection error: {e}")

        return []
