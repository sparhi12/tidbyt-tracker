"""
Flight route resolver.
Queries adsbdb.com API (primary) and HexDB API (fallback) to resolve
Origin > Destination IATA codes and full city names with SQLite and memory caching.
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

# Common IATA to ICAO mapping for fallback queries
IATA_TO_ICAO = {
    "AS": "ASA", "DL": "DAL", "UA": "UAL", "AA": "AAL", "WN": "SWA",
    "B6": "JBU", "F9": "FFT", "NK": "NKS", "HA": "HAL", "AC": "ACA",
    "WS": "WJA", "BA": "BAW", "AF": "AFR", "LH": "DLH", "NH": "ANA",
    "JL": "JAL", "KE": "KAL", "BR": "EVA", "CI": "CAL", "CX": "CPA",
    "SQ": "SIA", "EK": "UAE", "QR": "QTR", "QX": "QXE", "OO": "SKW",
}

class RouteResolver:
    def __init__(self, db_path: str = "routes_cache.db"):
        self.db_path = db_path
        self._memory_cache: Dict[str, Tuple[str, str, float]] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TidbytFlightTracker/2.0"})
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
        Example: ('SEA > SFO', 'Seattle > San Francisco')
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

        # 3. Query primary source: api.adsbdb.com (real-time flight routes)
        route = self._query_adsbdb(cs)
        if route:
            self._store_cache(cs, route[0], route[1])
            return route

        # Try alternative callsign format (e.g. AS1762 <-> ASA1762)
        alt_cs = self._get_alternate_callsign(cs)
        if alt_cs:
            route = self._query_adsbdb(alt_cs)
            if route:
                self._store_cache(cs, route[0], route[1])
                return route

        # 4. Query secondary source: HexDB API
        route = self._query_hexdb(cs)
        if route:
            self._store_cache(cs, route[0], route[1])
            return route

        if alt_cs:
            route = self._query_hexdb(alt_cs)
            if route:
                self._store_cache(cs, route[0], route[1])
                return route

        # Fallback if route unknown
        fallback = ("SEA AREA", "En Route")
        self._store_cache(cs, fallback[0], fallback[1])
        return fallback

    def _query_adsbdb(self, callsign: str) -> Optional[Tuple[str, str]]:
        url = f"https://api.adsbdb.com/v0/callsign/{callsign}"
        try:
            resp = self.session.get(url, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                flightroute = data.get("response", {}).get("flightroute")
                if flightroute:
                    orig = flightroute.get("origin") or {}
                    dest = flightroute.get("destination") or {}

                    orig_code = orig.get("iata_code") or orig.get("icao_code", "")
                    dest_code = dest.get("iata_code") or dest.get("icao_code", "")

                    orig_city = orig.get("municipality") or orig.get("name", "")
                    dest_city = dest.get("municipality") or dest.get("name", "")

                    if orig_code and dest_code:
                        return (f"{orig_code} > {dest_code}", f"{orig_city} > {dest_city}")
        except Exception as e:
            logger.debug(f"adsbdb lookup failed for {callsign}: {e}")
        return None

    def _query_hexdb(self, callsign: str) -> Optional[Tuple[str, str]]:
        url = f"https://hexdb.io/api/v1/route/icao/{callsign}"
        try:
            resp = self.session.get(url, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                raw_route = data.get("route", "")
                if raw_route and "-" in raw_route:
                    parts = raw_route.split("-")
                    orig_code, orig_city = resolve_airport(parts[0].strip())
                    dest_code, dest_city = resolve_airport(parts[1].strip())
                    return (f"{orig_code} > {dest_code}", f"{orig_city} > {dest_city}")
        except Exception as e:
            logger.debug(f"hexdb lookup failed for {callsign}: {e}")
        return None

    def _get_alternate_callsign(self, cs: str) -> Optional[str]:
        # If IATA 2-letter (e.g. AS1762), convert to ICAO (ASA1762)
        if len(cs) > 2 and cs[:2] in IATA_TO_ICAO and cs[2].isdigit():
            return IATA_TO_ICAO[cs[:2]] + cs[2:]
        # If ICAO 3-letter (e.g. ASA1762), convert to IATA (AS1762)
        for iata, icao in IATA_TO_ICAO.items():
            if cs.startswith(icao) and len(cs) > 3 and cs[3].isdigit():
                return iata + cs[3:]
        return None

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
