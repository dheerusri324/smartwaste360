# backend/routes/collection_points.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.collection_point import CollectionPoint
import traceback

bp = Blueprint('collection_points', __name__)

@bp.route('/', methods=['GET'])
def get_collection_points():
    """Get all active collection points or filter by waste types."""
    try:
        waste_types = request.args.getlist('waste_types')
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lng', type=float)
        radius = request.args.get('radius', 5, type=float)
        
        if latitude and longitude:
            # Get nearby collection points
            points = CollectionPoint.get_nearby(latitude, longitude, radius)
        elif waste_types:
            # Filter by waste types
            points = CollectionPoint.get_by_waste_type(waste_types)
        else:
            # Get all active points
            points = CollectionPoint.get_all_active()
        
        # Format the response
        formatted_points = []
        for point in points:
            point_dict = dict(point)
            # Convert any datetime objects to strings
            for key, value in point_dict.items():
                if hasattr(value, 'isoformat'):
                    point_dict[key] = value.isoformat()
                elif hasattr(value, 'strftime'):
                    point_dict[key] = value.strftime('%Y-%m-%d')
            formatted_points.append(point_dict)
        
        return jsonify({'collection_points': formatted_points}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/colony/<int:colony_id>', methods=['GET'])
def get_colony_collection_points(colony_id):
    """Get collection points for a specific colony."""
    try:
        points = CollectionPoint.get_by_colony(colony_id)
        
        # Format the response
        formatted_points = []
        for point in points:
            point_dict = dict(point)
            # Convert any datetime objects to strings
            for key, value in point_dict.items():
                if hasattr(value, 'isoformat'):
                    point_dict[key] = value.isoformat()
                elif hasattr(value, 'strftime'):
                    point_dict[key] = value.strftime('%Y-%m-%d')
            formatted_points.append(point_dict)
        
        return jsonify({'collection_points': formatted_points}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_collection_point():
    """Create a new collection point (admin/collector only)."""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['collector', 'admin']:
            return jsonify({"msg": "Access denied: Collector or admin access required"}), 403
        
        data = request.get_json()
        required_fields = ['colony_id', 'point_name', 'waste_types_accepted']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        point_id = CollectionPoint.create(
            colony_id=data['colony_id'],
            point_name=data['point_name'],
            location_description=data.get('location_description', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
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