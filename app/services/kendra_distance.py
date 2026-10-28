import math
import re
import urllib.parse
from typing import Optional, Tuple


# Earth radius in kilometers (WGS 84 mean radius)
EARTH_RADIUS_KM = 6371.0

# Indian Postal Index Number (PIN) code regex: 6 digits, first digit between 1 and 9
PINCODE_REGEX = re.compile(r"^[1-9][0-9]{5}$")


def validate_coordinates(lat: Optional[float], lon: Optional[float]) -> Tuple[bool, Optional[str]]:
    """
    Validates geographical latitude and longitude bounds.
    Latitude must be between -90 and 90.
    Longitude must be between -180 and 180.
    """
    if lat is None or lon is None:
        return False, "Coordinates cannot be null."
    try:
        f_lat = float(lat)
        f_lon = float(lon)
    except (ValueError, TypeError):
        return False, "Coordinates must be valid numbers."

    if math.isnan(f_lat) or math.isinf(f_lat) or math.isnan(f_lon) or math.isinf(f_lon):
        return False, "Coordinates cannot be NaN or infinity."

    if not (-90.0 <= f_lat <= 90.0):
        return False, f"Latitude {f_lat} out of bounds (-90 to +90)."

    if not (-180.0 <= f_lon <= 180.0):
        return False, f"Longitude {f_lon} out of bounds (-180 to +180)."

    return True, None


def validate_pincode(pincode: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validates standard Indian 6-digit PIN code format.
    """
    if not pincode:
        return False, "PIN code cannot be empty."
    clean = str(pincode).strip()
    if not PINCODE_REGEX.match(clean):
        return False, f"Invalid PIN code '{clean}'. Must be a 6-digit Indian postal code starting with 1-9."
    return True, clean


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth's surface
    using the Haversine formula in kilometers.
    """
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    # Clamp 'a' to [0, 1] to prevent domain errors with float inaccuracy
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = EARTH_RADIUS_KM * c
    return round(distance, 2)


def generate_directions_url(
    lat: Optional[float],
    lon: Optional[float],
    address: Optional[str] = None,
    provider: str = "google",
) -> Optional[str]:
    """
    Builds a secure, validated map navigation URL.
    Prefers exact verified coordinates; falls back to verified street address.
    Strictly avoids open redirect parameters.
    """
    valid_coords, _ = validate_coordinates(lat, lon)

    if provider.lower() == "osm" or provider.lower() == "openstreetmap":
        if valid_coords:
            return f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=%3B{lat:.6f}%2C{lon:.6f}"
        elif address:
            query = urllib.parse.quote(address.strip())
            return f"https://www.openstreetmap.org/search?query={query}"
        return None

    # Default to Google Maps Directions API URL
    if valid_coords:
        return f"https://www.google.com/maps/dir/?api=1&destination={lat:.6f},{lon:.6f}"
    elif address and address.strip():
        query = urllib.parse.quote(address.strip())
        return f"https://www.google.com/maps/dir/?api=1&destination={query}"

    return None
