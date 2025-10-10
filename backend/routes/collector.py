# backend/routes/collector.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import traceback
from models.collector import Collector
from models.colony import Colony

bp = Blueprint('collector', __name__)

@bp.route('/register', methods=['POST'])
def register_collector():
    """This route is deprecated. Registration is handled by the unified /api/auth/register route."""
    return jsonify({'message': 'This route is deprecated. Please use /api/auth/register.'}), 404

@bp.route('/login', methods=['POST'])
def login_collector():
    """Handles collector login and returns a standardized JWT token."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        collector = Collector.get_by_email(email)

        if not collector or not Collector.verify_password(collector['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create a standardized token with the ID as the identity and the role as a custom claim
        collector_id = collector['collector_id']
        additional_claims = {"role": "collector"}
        access_token = create_access_token(identity=str(collector_id), additional_claims=additional_claims)

        collector.pop('password_hash', None)
        return jsonify({
            'message': 'Collector login successful',
            'access_token': access_token,
            'collector': collector
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_collector_profile():
    """A protected route to get the profile of the logged-in collector."""
    try:
        collector_id = get_jwt_identity()
        
        try:
            claims = get_jwt()
            if claims.get('role') != 'collector':
                return jsonify({"msg": "Access denied: Collector token required"}), 403
        except Exception:
            # If get_jwt() fails, continue without role check for now
            pass

        collector = Collector.get_by_id(collector_id)
        
        if not collector:
            return jsonify({'error': 'Collector not found'}), 404
        
        # Remove sensitive information
        collector_dict = dict(collector)
        collector_dict.pop('password_hash', None)
        
        return jsonify({'collector': collector_dict}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_collector_profile():
    """Update collector profile information."""
    try:
        collector_id = get_jwt_identity()
        claims = get_jwt()

        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403

        data = request.get_json()
        
        # Handle password update separately
        if 'password' in data and data['password']:
            Collector.update_password(collector_id, data['password'])
            data.pop('password')  # Remove from profile update
        
        # Update other profile fields
        if data:
            Collector.update_profile(collector_id, **data)
        
        # Return updated collector info
        collector = Collector.get_by_id(collector_id)
        collector.pop('password_hash', None)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'collector': collector
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/location', methods=['GET'])
@jwt_required()
def get_collector_location():
    """Get collector location information."""
    try:
        collector_id = get_jwt_identity()
        claims = get_jwt()

        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403

        location = Collector.get_location(collector_id)
        
        if location:
            return jsonify({'location': dict(location)}), 200
        else:
            return jsonify({'location': None}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/location', methods=['PUT'])
@jwt_required()
def update_collector_location():
    """Update collector location information."""
    try:
        collector_id = get_jwt_identity()
        claims = get_jwt()

        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403

        data = request.get_json()
        
        required_fields = ['latitude', 'longitude']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Update location
        Collector.update_location(
            collector_id=collector_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode'),
            service_radius_km=data.get('service_radius_km', 50.0)
        )
        
        # Return updated location info
        location = Collector.get_location(collector_id)
        
        return jsonify({
            'message': 'Location updated successfully',
            'location': dict(location) if location else None
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/ready-colonies', methods=['GET'])
@jwt_required()
def get_ready_colonies():
    """Get colonies ready for collection, with optional location filtering."""
    try:
        try:
            claims = get_jwt()
            if claims.get('role') != 'collector':
                return jsonify({"msg": "Access denied: Only collectors can view this resource"}), 403
        except Exception:
            # If get_jwt() fails, continue without role check for now
            pass
        
        collector_id = get_jwt_identity()
        collector = Collector.get_by_id(collector_id)
        
        # Get collector's waste type preferences
        waste_types = collector.get('waste_types_collected') if collector else None
        
        # Get optional location parameters
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', default=500.0, type=float)  # Increased default to 500km for collectors
        
        if lat is not None and lon is not None:
            # Get ready colonies near the collector's location
            print(f"[DEBUG] Searching for ready colonies near ({lat}, {lon}) within {radius}km")
            try:
                colonies = Colony.get_ready_colonies_near_location(lat, lon, radius, waste_types, collector_id)
                print(f"[DEBUG] Found {len(colonies)} ready colonies within radius")
                
                # If no colonies found within radius, fall back to all ready colonies
                if not colonies:
                    print(f"[INFO] No ready colonies found within {radius}km of ({lat}, {lon}), showing all ready colonies")
                    colonies = Colony.get_colonies_ready_for_collection_by_type(waste_types, collector_id)
            except Exception as location_error:
                print(f"[ERROR] Location-based query failed: {location_error}")
                traceback.print_exc()
                # Fall back to all ready colonies
                colonies = Colony.get_colonies_ready_for_collection_by_type(waste_types, collector_id)
        else:
            # Get all ready colonies (no location filter)
            colonies = Colony.get_colonies_ready_for_collection_by_type(waste_types, collector_id)
        
        return jsonify({'colonies': colonies}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500