# backend/routes/health.py

from flask import Blueprint, jsonify
import psutil
import socket
from datetime import datetime
from backend.config.database import get_db

bp = Blueprint('health', __name__)

@bp.route('', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint with safe DB connection."""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'services': {}
    }
    
    # Check database connection using the safe context manager
    try:
        with get_db() as db:
            if not db:
                raise ConnectionError("Failed to get connection from pool.")
            with db.cursor() as cursor:
                cursor.execute('SELECT 1')
        status['services']['database'] = 'connected'
    except Exception as e:
        status['services']['database'] = f'error: {str(e)}'
        status['status'] = 'degraded'
    
    # Check system metrics
    status['disk'] = psutil.disk_usage('/')._asdict()
    status['memory'] = psutil.virtual_memory()._asdict()
    
    http_status_code = 503 if status['status'] == 'degraded' else 200
    return jsonify(status), http_status_code