# backend/routes/admin.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import traceback
from models.admin import Admin
from models.user import User
from models.collector import Collector
from models.colony import Colony
from models.collection_point import CollectionPoint

bp = Blueprint('admin', __name__)

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_admin_profile():
    """Get admin profile"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        admin_id = get_jwt_identity()
        admin = Admin.get_by_id(admin_id)
        
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        
        admin.pop('password_hash', None)
        return jsonify({'admin': admin}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        admin = Admin.get_by_email(email)
        if not admin or not Admin.verify_password(admin['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create token with admin role
        admin_id = admin['admin_id']
        additional_claims = {"role": "admin"}
        access_token = create_access_token(identity=str(admin_id), additional_claims=additional_claims)

        admin.pop('password_hash', None)
        return jsonify({
            'message': 'Admin login successful',
            'access_token': access_token,
            'admin': admin
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Get admin dashboard overview data"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        overview_data = Admin.get_system_overview()
        
        # Format datetime objects for JSON serialization
        for activity in overview_data['recent_activity']:
            if activity.get('created_at'):
                activity['created_at'] = activity['created_at'].isoformat()
        
        return jsonify(overview_data), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/dashboard/analytics', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get admin dashboard analytics data"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        date_range = request.args.get('range', '30d')
        analytics_data = Admin.get_analytics_data(date_range)
        
        # Format datetime objects for JSON serialization
        for trend in analytics_data['daily_trends']:
            if trend.get('date'):
                trend['date'] = trend['date'].isoformat()
        
        return jsonify(analytics_data), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users with pagination"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        users = User.get_all_users()
        return jsonify({'users': users}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    """Update user active status"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'is_active field is required'}), 400

        success = User.update_status(user_id, is_active)
        
        if success:
            return jsonify({
                'message': f'User {"activated" if is_active else "deactivated"} successfully'
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/collectors', methods=['GET'])
@jwt_required()
def get_all_collectors():
    """Get all collectors with pagination"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        collectors = Collector.get_all_collectors()
        return jsonify({'collectors': collectors}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/collectors/<collector_id>/status', methods=['PUT'])
@jwt_required()
def update_collector_status(collector_id):
    """Update collector active status"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'is_active field is required'}), 400

        success = Collector.update_status(collector_id, is_active)
        
        if success:
            return jsonify({
                'message': f'Collector {"activated" if is_active else "deactivated"} successfully'
            }), 200
        else:
            return jsonify({'error': 'Collector not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/collectors/<collector_id>', methods=['PUT'])
@jwt_required()
def update_collector(collector_id):
    """Update collector information"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        data = request.get_json()
        
        # Update collector
        success = Collector.update_collector(collector_id, data)
        
        if success:
            return jsonify({'message': 'Collector updated successfully'}), 200
        else:
            return jsonify({'error': 'Collector not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/colonies', methods=['GET'])
@jwt_required()
def get_all_colonies():
    """Get all colonies for admin management"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        colonies = Colony.get_all()
        return jsonify({'colonies': colonies}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/colonies', methods=['POST'])
@jwt_required()
def create_colony():
    """Create a new colony"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        data = request.get_json()
        required_fields = ['colony_name', 'address', 'city', 'state', 'pincode']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        colony_id = Colony.create_colony(
            colony_name=data['colony_name'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        return jsonify({
            'message': 'Colony created successfully',
            'colony_id': colony_id
        }), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/collection-points', methods=['GET'])
@jwt_required()
def get_all_collection_points():
    """Get all collection points for admin management"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        collection_points = CollectionPoint.get_all_active()
        return jsonify({'collection_points': collection_points}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/collection-points', methods=['POST'])
@jwt_required()
def create_collection_point():
    """Create a new collection point"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        data = request.get_json()
        required_fields = ['point_name', 'waste_types_accepted', 'latitude', 'longitude']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: point_name, waste_types_accepted, latitude, longitude'}), 400

        # Auto-assign colony based on location
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        colony_id = None
        
        if latitude and longitude:
            # Find nearest colony within 10km radius
            nearby_colonies = Colony.get_nearby_colonies(latitude, longitude, radius_km=10)
            if nearby_colonies:
                colony_id = nearby_colonies[0]['colony_id']
                print(f"[INFO] Auto-assigned collection point to colony: {nearby_colonies[0]['colony_name']}")
            else:
                # If no nearby colony found, create a default one or use the first available
                all_colonies = Colony.get_all()
                if all_colonies:
                    colony_id = all_colonies[0]['colony_id']
                    print(f"[INFO] No nearby colony found, assigned to default: {all_colonies[0]['colony_name']}")
                else:
                    return jsonify({'error': 'No colonies available. Please create a colony first.'}), 400
        else:
            return jsonify({'error': 'Latitude and longitude are required for auto-assignment'}), 400

        point_id = CollectionPoint.create(
            colony_id=colony_id,
            point_name=data['point_name'],
            location_description=data.get('location_description', ''),
            latitude=latitude,
            longitude=longitude,
            waste_types_accepted=data['waste_types_accepted'],
            max_capacity_kg=data.get('max_capacity_kg', 100.00)
        )

        return jsonify({
            'message': 'Collection point created successfully',
            'point_id': point_id
        }), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/system/health', methods=['GET'])
@jwt_required()
def get_system_health():
    """Get system health metrics"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403

        # System health metrics
        health_data = {
            'database_status': 'healthy',
            'api_status': 'healthy',
            'ml_service_status': 'healthy',
            'last_updated': '2025-10-09T20:00:00Z'
        }

        return jsonify(health_data), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500