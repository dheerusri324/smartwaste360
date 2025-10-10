# utils/validation.py
import re
from datetime import datetime

def validate_email(email):
    """Validate an email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate a phone number (basic validation)"""
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10 digits for most countries)
    return len(digits) >= 10

def validate_password(password):
    """Validate a password (at least 8 characters, with letters and numbers)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_date(date_string, date_format='%Y-%m-%d'):
    """Validate a date string"""
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def validate_coordinates(latitude, longitude):
    """Validate latitude and longitude coordinates"""
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lng <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, "Coordinates are valid"
    except (ValueError, TypeError):
        return False, "Coordinates must be valid numbers"

def validate_weight(weight):
    """Validate a weight value (must be positive)"""
    try:
        weight_val = float(weight)
        if weight_val <= 0:
            return False, "Weight must be a positive number"
        return True, "Weight is valid"
    except (ValueError, TypeError):
        return False, "Weight must be a valid number"

def validate_username(username):
    """Validate a username (alphanumeric with underscores, 3-20 characters)"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    if re.match(pattern, username):
        return True, "Username is valid"
    return False, "Username must be 3-20 characters long and contain only letters, numbers, and underscores"

def validate_json(data, required_fields=None):
    """Validate JSON data and check for required fields"""
    if not isinstance(data, dict):
        return False, "Data must be a JSON object"
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
    
    return True, "JSON is valid"

def sanitize_input(input_string, max_length=None):
    """Sanitize user input to prevent XSS and other attacks"""
    if not input_string:
        return ""
    
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]*>', '', str(input_string))
    
    # Limit length if specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned