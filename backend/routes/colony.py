# backend/routes/colony.py

from flask import Blueprint, request, jsonify
from models.colony import Colony
import traceback

bp = Blueprint('colony', __name__)

@bp.route('/nearby', methods=['GET'])
def get_nearby_colonies_route():
    """API endpoint to find colonies near a given GPS coordinate."""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', default=10.0, type=float)

        if lat is None or lon is None:
            return jsonify({'error': 'Latitude (lat) and Longitude (lon) are required.'}), 400

        colonies = Colony.get_nearby_colonies(lat, lon, radius)
        return jsonify({'colonies': colonies}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
def get_all_colonies():
    """API endpoint to get a list of all colonies."""
    try:
        colonies = Colony.get_all()
        return jsonify({'colonies': colonies}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:colony_id>', methods=['GET'])
def get_single_colony(colony_id):
    """API endpoint to get details for a single colony."""
    try:
        colony = Colony.get_colony_by_id(colony_id)
        if not colony:
            return jsonify({'error': 'Colony not found'}), 404
        return jsonify({'colony': colony}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500