# backend/routes/debug_logs.py
"""
Debug endpoint to view captured logs without needing Render's professional plan
"""

from flask import Blueprint, jsonify
from utils.log_capture import log_capture

bp = Blueprint('debug_logs', __name__)

@bp.route('/recent-logs', methods=['GET'])
def get_recent_logs():
    """Get all captured logs"""
    logs = log_capture.get_all()
    return jsonify({
        'status': 'success',
        'total_logs': len(logs),
        'logs': logs,
        'message': 'These are the last 100 log entries captured in memory'
    })

@bp.route('/clear-logs', methods=['POST'])
def clear_logs():
    """Clear all captured logs"""
    log_capture.clear()
    return jsonify({
        'status': 'success',
        'message': 'All logs cleared'
    })
