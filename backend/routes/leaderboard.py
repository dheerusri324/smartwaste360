# backend/routes/leaderboard.py

from flask import Blueprint, request, jsonify
from models.colony import Colony
from models.collector import Collector
import traceback

bp = Blueprint('leaderboard', __name__)

@bp.route('/colonies', methods=['GET'])
def get_colony_leaderboard():
    """Get colony leaderboard, ranked by total points."""
    try:
        limit = request.args.get('limit', 10, type=int)
        leaderboard = Colony.get_leaderboard(limit)
        return jsonify({'leaderboard': leaderboard}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/collectors', methods=['GET'])
def get_collector_leaderboard():
    """Get national collector leaderboard, ranked by total weight collected."""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        try:
            leaderboard = Collector.get_leaderboard(limit)
            
            # Format the data to ensure consistency if needed
            formatted_leaderboard = []
            for item in leaderboard:
                item_dict = dict(item)
                if item_dict.get('total_weight_collected'):
                    # Convert from Decimal to float for JSON
                    item_dict['total_weight_collected'] = float(item_dict['total_weight_collected'])
                formatted_leaderboard.append(item_dict)

            return jsonify({'leaderboard': formatted_leaderboard}), 200
            
        except Exception as db_error:
            print(f"Database error in collector leaderboard: {db_error}")
            # Return empty leaderboard as fallback
            return jsonify({'leaderboard': []}), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'leaderboard': []}), 200