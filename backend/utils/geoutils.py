# utils/geoutils.py
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the Earth's surface using the Haversine formula
    
    Args:
        lat1, lon1: Latitude and Longitude of point 1 (in decimal degrees)
        lat2, lon2: Latitude and Longitude of point 2 (in decimal degrees)
    
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

def get_nearby_locations(reference_lat, reference_lon, locations, max_distance_km=10):
    """
    Find locations within a certain distance from a reference point
    
    Args:
        reference_lat, reference_lon: Reference point coordinates
        locations: List of location dictionaries with 'latitude' and 'longitude' keys
        max_distance_km: Maximum distance in kilometers
    
    Returns:
        List of nearby locations with distance information
    """
    nearby_locations = []
    
    for location in locations:
        try:
            lat = float(location.get('latitude', 0))
            lon = float(location.get('longitude', 0))
            
            distance = calculate_distance(reference_lat, reference_lon, lat, lon)
            
            if distance <= max_distance_km:
                location_with_distance = location.copy()
                location_with_distance['distance_km'] = round(distance, 2)
                nearby_locations.append(location_with_distance)
        except (ValueError, TypeError):
            continue
    
    # Sort by distance
    nearby_locations.sort(key=lambda x: x['distance_km'])
    
    return nearby_locations

def get_bounding_box(latitude, longitude, distance_km=10):
    """
    Calculate a bounding box around a point for spatial queries
    
    Args:
        latitude, longitude: Center point coordinates
        distance_km: Distance from center point in kilometers
    
    Returns:
        Dictionary with min/max latitude and longitude
    """
    # Approximate conversion: 1° latitude ≈ 111 km
    lat_delta = distance_km / 111
    # Longitude delta depends on latitude
    lon_delta = distance_km / (111 * math.cos(math.radians(latitude)))
    
    return {
        'min_lat': latitude - lat_delta,
        'max_lat': latitude + lat_delta,
        'min_lon': longitude - lon_delta,
        'max_lon': longitude + lon_delta
    }

def is_point_in_polygon(point, polygon):
    """
    Check if a point is inside a polygon using the ray casting algorithm
    
    Args:
        point: Tuple of (latitude, longitude)
        polygon: List of tuples representing polygon vertices
    
    Returns:
        True if point is inside polygon, False otherwise
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def format_address(address_dict):
    """
    Format an address dictionary into a readable string
    
    Args:
        address_dict: Dictionary with address components
    
    Returns:
        Formatted address string
    """
    components = []
    
    if address_dict.get('address'):
        components.append(address_dict['address'])
    
    if address_dict.get('city'):
        components.append(address_dict['city'])
    
    if address_dict.get('state'):
        components.append(address_dict['state'])
    
    if address_dict.get('pincode'):
        components.append(address_dict['pincode'])
    
    return ', '.join(components)

def get_current_location():
    """
    Get the current location using browser geolocation API
    Note: This is a placeholder for frontend implementation
    """
    # This function would be implemented in JavaScript on the frontend
    # This is just a placeholder for the Python backend
    return {
        'latitude': None,
        'longitude': None,
        'accuracy': None,
        'timestamp': None
    }