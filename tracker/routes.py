"""
Flight route resolver.
Fetches route (Origin-Destination) from HexDB API and maps codes to city names
using the local airport database, with local SQLite and in-memory caching.
"""

import json
import logging
import os
import sqlite3
import time
from typing import Dict, Optional, Tuple
import requests

from tracker.airports import resolve_airport

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 6 * 3600  # 6 hours cache per callsign

class RouteResolver:
    def __init__(self, db_path: str = "routes_cache.db"):
        self.db_path = db_path
        self._memory_cache: Dict[str, Tuple[str, str, float]] = {}
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS route_cache (
                        callsign TEXT PRIMARY KEY,
                        route_codes TEXT,
                        route_cities TEXT,
                        timestamp REAL
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not initialize route SQLite cache: {e}")

    def get_route(self, callsign: Optional[str]) -> Tuple[str, str]:
        """
        Returns (route_codes, route_cities).
        Example: ('PDX > LAX', 'Portland > Los Angeles')
        """
        if not callsign:
            return ("SEA AREA", "Overhead Seattle")

        cs = callsign.strip().upper()
        if not cs or cs.startswith("N"):
            return ("LOCAL", "General Aviation")

        now = time.time()

        # 1. Check in-memory cache
        if cs in self._memory_cache:
            codes, cities, exp = self._memory_cache[cs]
            if now < exp:
                return (codes, cities)

        # 2. Check SQLite cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT route_codes, route_cities, timestamp FROM route_cache WHERE callsign = ?",
                    (cs,)
                )
                row = cursor.fetchone()
                if row:
                    codes, cities, ts = row
                    if now - ts < CACHE_TTL_SECONDS:
                        self._memory_cache[cs] = (codes, cities, now + (CACHE_TTL_SECONDS - (now - ts)))
                        return (codes, cities)
        except Exception as e:
            logger.debug(f"SQLite lookup error for {cs}: {e}")

        # 3. Query HexDB API
        url = f"https://hexdb.io/api/v1/route/icao/{cs}"
        headers = {"User-Agent": "TidbytFlightTracker/2.0"}

        try:
            resp = requests.get(url, headers=headers, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                raw_route = data.get("route", "")
                if raw_route and "-" in raw_route:
                    parts = raw_route.split("-")
                    orig_raw = parts[0].strip()
                    dest_raw = parts[1].strip()

                    orig_code, orig_city = resolve_airport(orig_raw)
                    dest_code, dest_city = resolve_airport(dest_raw)

                    route_codes = f"{orig_code} > {dest_code}"
                    route_cities = f"{orig_city} > {dest_city}"

                    self._store_cache(cs, route_codes, route_cities)
                    return (route_codes, route_cities)
        except Exception as e:
            logger.debug(f"HexDB API lookup failed for {cs}: {e}")

        # Fallback if route not known
        fallback = ("SEA AREA", "En Route")
        self._store_cache(cs, fallback[0], fallback[1])
        return fallback

    def _store_cache(self, callsign: str, codes: str, cities: str):
        now = time.time()
        self._memory_cache[callsign] = (codes, cities, now + CACHE_TTL_SECONDS)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO route_cache (callsign, route_codes, route_cities, timestamp) VALUES (?, ?, ?, ?)",
                    (callsign, codes, cities, now)
                )
                conn.commit()
        except Exception as e:
            logger.debug(f"SQLite cache store error: {e}")
