# backend/routes/auth.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import requests
import traceback
import bcrypt
from models.user import User
from models.colony import Colony
from models.collector import Collector

bp = Blueprint('auth', __name__)

def get_address_from_coords(lat, lon):
    """Uses Nominatim (OpenStreetMap) to get address details from coordinates with smart area grouping."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'SmartWaste360/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        address = data.get('address', {})
        
        # Smart hierarchical location detection
        # Priority: suburb > neighbourhood > city_district > postcode area > road
        colony_name = (
            address.get('suburb') or 
            address.get('neighbourhood') or 
            address.get('city_district') or
            address.get('quarter') or
            address.get('residential') or
            address.get('road') or 
            'Unknown Area'
        )
        
        # Clean up common prefixes/suffixes for better grouping
        colony_name = clean_area_name(colony_name)
        
        print(f"[INFO] Location detected: {colony_name} from coordinates ({lat}, {lon})")
        return colony_name
    except Exception as e:
        print(f"[ERROR] Geocoding failed: {e}")
        return "Unknown Area"

def clean_area_name(area_name):
    """Clean and standardize area names for better grouping"""
    if not area_name or area_name == 'Unknown Area':
        return area_name
    
    # Remove common prefixes and suffixes
    prefixes_to_remove = ['Ward ', 'ward ', 'WARD ']
    suffixes_to_remove = [' Colony', ' colony', ' COLONY', ' Area', ' area', ' AREA']
    
    cleaned = area_name.strip()
    
    # Remove prefixes
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    
    # Remove suffixes  
    for suffix in suffixes_to_remove:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
    
    # Capitalize properly
    cleaned = cleaned.title()
    
    # Handle special cases for better grouping
    area_mappings = {
        # Hyderabad area mappings
        'Koti': 'Kothapet',
        'Boiguda': 'Secunderabad',
        'Kavadiguda': 'Secunderabad',
        'Nagaram': 'Nagaram',
        # Add more mappings as needed
    }
    
    return area_mappings.get(cleaned, cleaned)

@bp.route('/register', methods=['POST'])
def register():
    """
    A single, unified route to register either a 'user' or a 'collector'.
    """
    try:
        data = request.get_json()
        role = data.get('role', 'user')

        if role == 'user':
            required = ['username', 'email', 'password', 'full_name', 'latitude', 'longitude']
            if not all(field in data for field in required):
                return jsonify({'error': 'Missing required fields for user registration'}), 400
            
            # Check if email is already registered
            if User.get_user_by_username_or_email(data['email']):
                return jsonify({'error': 'Email is already registered'}), 409
            
            # Check if username is already registered
            if User.get_user_by_username_or_email(data['username']):
                return jsonify({'error': 'Username is already taken'}), 409

            colony_name = get_address_from_coords(data['latitude'], data['longitude'])
            colony_id = Colony.find_or_create(colony_name, data['latitude'], data['longitude'])

            try:
                user_id = User.create_user(
                    username=data['username'], email=data['email'], password=data['password'],
                    full_name=data['full_name'], colony_id=colony_id, phone=data.get('phone')
                )
                return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
            except Exception as db_error:
                if 'duplicate key value violates unique constraint' in str(db_error):
                    if 'users_email_key' in str(db_error):
                        return jsonify({'error': 'Email is already registered'}), 409
                    elif 'users_username_key' in str(db_error):
                        return jsonify({'error': 'Username is already taken'}), 409
                    else:
                        return jsonify({'error': 'User with this information already exists'}), 409
                raise db_error
        
        elif role == 'collector':
            required = ['full_name', 'phone', 'email', 'password']
            if not all(field in data for field in required):
                return jsonify({'error': 'Missing required fields for collector registration'}), 400

            try:
                # Check if collector already exists
                existing_collector = Collector.get_by_email(data['email'])
                if existing_collector:
                    return jsonify({'error': 'A collector with this email already exists'}), 409
                
                # Create new collector
                collector_id = Collector.create(
                    name=data['full_name'],
                    phone=data['phone'],
                    email=data['email'],
                    password=data['password'],
                    vehicle_number=data.get('vehicle_number')
                )
                return jsonify({'message': 'Collector registered successfully', 'collector_id': collector_id}), 201
                
            except Exception as collector_error:
                traceback.print_exc()
                return jsonify({'error': f'Collector registration failed: {str(collector_error)}'}), 500
        
        elif role == 'admin':
            required = ['username', 'full_name', 'email', 'password']
            if not all(field in data for field in required):
                return jsonify({'error': 'Missing required fields for admin registration'}), 400

            from models.admin import Admin
            if Admin.get_by_email(data['email']):
                return jsonify({'error': 'An admin with this email already exists'}), 409
            
            if Admin.get_by_username(data['username']):
                return jsonify({'error': 'An admin with this username already exists'}), 409
            
            admin_id = Admin.create_admin(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                full_name=data['full_name']
            )
            return jsonify({'message': 'Admin registered successfully', 'admin_id': admin_id}), 201
        
        else:
            return jsonify({'error': 'Invalid role specified'}), 400
            
    except Exception as e:
        print(f"ERROR in /register route: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Handles user login and creates a STANDARDIZED token."""
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')
    
        if not identifier or not password:
            return jsonify({'error': 'Username/email and password required'}), 400
        
        # First try to find user in users table
        user = User.get_user_by_username_or_email(identifier)
        
        if user and User.verify_password(user['password_hash'], password):
            # Regular user login
            user_id = user['user_id']
            additional_claims = {"role": "user"}
            access_token = create_access_token(identity=str(user_id), additional_claims=additional_claims)
            
            User.update_last_login(user_id)
            user.pop('password_hash', None)
            
            return jsonify({ 'message': 'Login successful', 'access_token': access_token, 'user': user }), 200
        
        # If not found in users, try admins table
        from models.admin import Admin
        admin = Admin.get_by_email(identifier) or Admin.get_by_username(identifier)
        
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            # Admin login
            admin_id = admin['admin_id']
            additional_claims = {"role": "admin"}
            access_token = create_access_token(identity=str(admin_id), additional_claims=additional_claims)
            
            admin.pop('password_hash', None)
            
            return jsonify({ 'message': 'Admin login successful', 'access_token': access_token, 'admin': admin }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Gets the profile of the logged-in user using the standardized token."""
    try:
        # --- THIS IS THE FIX ---
        user_id = get_jwt_identity() # This now correctly gets the user ID string
        claims = get_jwt()
        if claims.get('role') != 'user':
            return jsonify({"msg": "Access denied: User token required"}), 403

        user = User.get_user_by_id(user_id)
        if not user: return jsonify({'error': 'User not found'}), 404
        
        user.pop('password_hash', None)
        return jsonify({'user': user}), 200
    except Exception as e:
        return jsonify({'error': 'An internal server error occurred'}), 500
@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Updates the profile for the currently logged-in user."""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'user':
            return jsonify({"msg": "Access denied: User token required"}), 403
        
        data = request.get_json()
        
        # Handle password update separately
        if 'password' in data and data['password']:
            User.update_password(user_id, data['password'])
            data.pop('password')  # Remove from profile update
        
        # Only allow updating specific fields
        allowed_updates = {
            'full_name': data.get('full_name'),
            'phone': data.get('phone')
        }
        # Filter out any keys that were not provided in the request
        update_data = {k: v for k, v in allowed_updates.items() if v is not None}

        if update_data:
            User.update_user(user_id, **update_data)
        
        updated_user = User.get_user_by_id(user_id)
        updated_user.pop('password_hash', None)

        return jsonify({
            'message': 'Profile updated successfully',
            'user': updated_user
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500