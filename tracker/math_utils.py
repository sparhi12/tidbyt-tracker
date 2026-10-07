"""
Geospatial math and filtering algorithms for flight tracking:
- Haversine distance in miles
- Initial compass bearing (0-360 degrees)
- 8-point compass classification (N, NE, E, SE, S, SW, W, NW)
- Eastern hemisphere priority filter (0° to 180°: North -> East -> South)
- Row 3 formatting without scrolling (e.g. 'NW -> 0.1m')
- Forward dead reckoning projection
"""

import math
from typing import Dict, List, Optional, Tuple

COMPASS_8_SECTORS = [
    ("N", 337.5, 360.0),
    ("N", 0.0, 22.5),
    ("NE", 22.5, 67.5),
    ("E", 67.5, 112.5),
    ("SE", 112.5, 157.5),
    ("S", 157.5, 202.5),
    ("Sw", 202.5, 247.5),
    ("w", 247.5, 292.5),
    ("Nw", 292.5, 337.5),
]

COMPASS_ARROWS = {
    "N": "^",
    "NE": "^",
    "E": ">",
    "SE": "v",
    "S": "v",
    "Sw": "<",
    "w": "<",
    "Nw": "^",
}

EARTH_RADIUS_MILES = 3958.7613

def haversine_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points on Earth in miles."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_MILES * c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate forward azimuth / bearing in degrees (0° - 360°) from point 1 to point 2."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))

    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0

def bearing_to_compass(bearing: float) -> str:
    """Map bearing in degrees (0-360) to 8-point compass direction."""
    norm_bearing = (bearing + 360.0) % 360.0
    for direction, low, high in COMPASS_8_SECTORS:
        if low <= norm_bearing < high:
            return direction
    return "N"

def is_eastern_hemisphere(bearing: float) -> bool:
    """Check if bearing is in North -> East -> South right hemisphere (0° to 180°)."""
    norm = (bearing + 360.0) % 360.0
    return 0.0 <= norm <= 180.0

def format_row3(direction: str, distance_miles: float) -> str:
    """
    Format direction and distance with 2 decimal places for high-precision 1s tracking.
    Format: 'Nw 0.12', 'w 0.05', 'N 12.3'
    """
    if distance_miles < 0.005:
        dist_str = "0.00"
    elif distance_miles < 10.0:
        dist_str = f"{distance_miles:.2f}"
    elif distance_miles < 100.0:
        dist_str = f"{distance_miles:.1f}"
    else:
        dist_str = f"{int(round(distance_miles))}"

    return f"{direction} {dist_str}"

def select_best_flight(
    aircraft_list: List[Dict],
    ref_lat: float,
    ref_lon: float,
    max_radius_miles: float = 15.0,
    eastern_priority: bool = True,
    exclude_on_ground: bool = True
) -> Optional[Dict]:
    """
    Select the best aircraft to display:
    1. Filter out aircraft on ground (if exclude_on_ground=True)
    2. Filter out aircraft beyond max_radius_miles
    3. Calculate distance and bearing relative to reference point
    4. If eastern_priority is True and any aircraft are in [0°, 180°], pick the closest eastern aircraft
    5. Otherwise, pick the closest aircraft overall
    """
    candidates = []

    for ac in aircraft_list:
        if exclude_on_ground and ac.get("on_ground", False):
            continue

        lat = ac.get("lat")
        lon = ac.get("lon")
        if lat is None or lon is None:
            continue

        dist = haversine_distance_miles(ref_lat, ref_lon, lat, lon)
        if dist > max_radius_miles:
            continue

        bearing = calculate_bearing(ref_lat, ref_lon, lat, lon)
        direction = bearing_to_compass(bearing)
        eastern = is_eastern_hemisphere(bearing)

        candidates.append({
            **ac,
            "dist_miles": dist,
            "bearing": bearing,
            "direction": direction,
            "is_eastern": eastern,
            "row3_text": format_row3(direction, dist),
        })

    if not candidates:
        return None

    if eastern_priority:
        eastern_candidates = [c for c in candidates if c["is_eastern"]]
        if eastern_candidates:
            return min(eastern_candidates, key=lambda x: x["dist_miles"])

    return min(candidates, key=lambda x: x["dist_miles"])

def project_position(
    lat: float,
    lon: float,
    velocity_mps: Optional[float],
    track_deg: Optional[float],
    dt_seconds: float
) -> Tuple[float, float]:
    """
    Dead reckoning projection of aircraft position forward by dt_seconds.
    velocity_mps: speed in meters/second
    track_deg: track heading in degrees
    """
    if velocity_mps is None or track_deg is None or dt_seconds <= 0:
        return lat, lon

    dist_meters = velocity_mps * dt_seconds
    d_lat = (dist_meters * math.cos(math.radians(track_deg))) / 111320.0
    lat_rad = math.radians(lat)
    cos_lat = math.cos(lat_rad)
    if abs(cos_lat) < 1e-6:
        cos_lat = 1e-6
    d_lon = (dist_meters * math.sin(math.radians(track_deg))) / (111320.0 * cos_lat)

    return lat + d_lat, lon + d_lon
