"""
Unified Flight Service.
Orchestrates data fetching, dual-source fallback, rate-limit-safe polling,
dead reckoning, aircraft selection with eastern priority, and route enrichment.
"""

from datetime import datetime
import logging
import time
from typing import Dict, List, Optional, Tuple

from tracker.airlines import resolve_airline
from tracker.airplanes_live import AirplanesLiveClient
from tracker.config import Config
from tracker.math_utils import (
    bearing_to_compass,
    calculate_bearing,
    format_row3,
    haversine_distance_miles,
    project_position,
    select_best_flight,
)
from tracker.opensky import OpenSkyClient
from tracker.routes import RouteResolver

logger = logging.getLogger(__name__)

class FlightService:
    def __init__(self, config: Config):
        self.config = config
        self.airplanes_client = AirplanesLiveClient()
        self.opensky_client = OpenSkyClient(
            username=config.OPENSKY_USERNAME,
            password=config.OPENSKY_PASSWORD,
            client_id=config.OPENSKY_CLIENT_ID,
            client_secret=config.OPENSKY_CLIENT_SECRET,
        )
        self.route_resolver = RouteResolver()

        # State tracking for dead reckoning and rate limiting
        self._cached_aircraft: List[Dict] = []
        self._last_fetch_time: float = 0.0
        self._last_opensky_fetch: float = 0.0

    def get_current_display_data(self) -> Dict[str, str]:
        """
        Produce complete, formatted data dictionary for the Tidbyt display template.
        """
        now = time.time()
        source = self.config.DATA_SOURCE

        aircraft_list = []

        # 1. Fetch live data according to configured source
        if source in ("airplanes_live", "dual"):
            aircraft_list = self.airplanes_client.get_aircraft(
                self.config.REF_LAT,
                self.config.REF_LON,
                radius_nm=self.config.MAX_RADIUS_MILES
            )

        # Fallback to OpenSky if airplanes_live is empty or if source is explicitly opensky
        if not aircraft_list and (source in ("opensky", "dual")):
            # Respect OpenSky credit limits: poll only once every OPENSKY_POLL_INTERVAL
            if (now - self._last_opensky_fetch) >= self.config.OPENSKY_POLL_INTERVAL:
                opensky_data = self.opensky_client.get_aircraft(
                    self.config.REF_LAT,
                    self.config.REF_LON,
                    box_deg=(self.config.MAX_RADIUS_MILES / 60.0)
                )
                if opensky_data:
                    aircraft_list = opensky_data
                    self._last_opensky_fetch = now
                    self._cached_aircraft = aircraft_list
                    self._last_fetch_time = now
            elif self._cached_aircraft:
                # Project cached positions using dead reckoning
                dt = now - self._last_fetch_time
                projected = []
                for ac in self._cached_aircraft:
                    new_lat, new_lon = project_position(
                        ac["lat"], ac["lon"], ac.get("velocity"), ac.get("track"), dt
                    )
                    projected.append({**ac, "lat": new_lat, "lon": new_lon})
                aircraft_list = projected

        if aircraft_list:
            self._cached_aircraft = aircraft_list
            self._last_fetch_time = now

        # 2. Select best flight (closest with Eastern Priority 0°-180°)
        best = select_best_flight(
            self._cached_aircraft,
            self.config.REF_LAT,
            self.config.REF_LON,
            max_radius_miles=self.config.MAX_RADIUS_MILES,
            eastern_priority=self.config.EASTERN_PRIORITY,
            exclude_on_ground=True
        )

        if not best:
            # Standby mode when no flights are overhead
            return {
                "flight_no": "SCANNING",
                "airline": "Seattle Skies",
                "row3_text": format_row3("Nw", 0.0),
                "route_codes": "SEA>---",
                "route_cities": "Overhead Seattle",
                "is_active": "false"
            }

        callsign = best.get("flight", "").strip()
        airline_name = resolve_airline(callsign)
        route_codes, route_cities = self.route_resolver.get_route(callsign)

        # Apply 1-second real-time position projection
        lat = best.get("lat")
        lon = best.get("lon")
        velocity = best.get("velocity")
        track = best.get("track")
        updated_at = best.get("updated_at", now)

        dt = max(0.0, now - updated_at)
        if velocity and track and dt > 0:
            proj_lat, proj_lon = project_position(lat, lon, velocity, track, dt)
        else:
            proj_lat, proj_lon = lat, lon

        dist_miles = haversine_distance_miles(
            self.config.REF_LAT, self.config.REF_LON, proj_lat, proj_lon
        )
        bearing = calculate_bearing(
            self.config.REF_LAT, self.config.REF_LON, proj_lat, proj_lon
        )
        direction = bearing_to_compass(bearing)
        row3_text = format_row3(direction, dist_miles)

        return {
            "flight_no": callsign if callsign else "OVERHEAD",
            "airline": airline_name,
            "row3_text": row3_text,
            "route_codes": route_codes,
            "route_cities": route_cities,
            "is_active": "true"
        }
