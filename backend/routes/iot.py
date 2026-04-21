# backend/routes/iot.py
# IoT sensor data ingestion endpoints for SmartWaste360

import os
import traceback
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify
from config.database import get_db
from psycopg2.extras import RealDictCursor

bp = Blueprint('iot', __name__)

# ============================
# IoT AUTHENTICATION
# ============================

IOT_API_KEY = os.getenv('IOT_API_KEY', 'smartwaste-iot-demo-key-2026')

def iot_auth_required(f):
    """Simple API key authentication for IoT devices."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-IoT-API-Key')
        if not api_key:
            return jsonify({'error': 'Missing X-IoT-API-Key header'}), 401
        if api_key != IOT_API_KEY:
            return jsonify({'error': 'Invalid API key'}), 403
        return f(*args, **kwargs)
    return decorated


# ============================
# ENDPOINT: Bin Fill-Level (from ESP32)
# ============================

@bp.route('/bin-level', methods=['POST'])
@iot_auth_required
def receive_bin_level():
    """
    Receive fill-level data from an ultrasonic sensor.
    Updates BOTH the sensor_readings log AND the collection_points table.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON payload provided'}), 400

        required = ['device_id', 'fill_percentage', 'estimated_weight_kg']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        device_id        = data['device_id']
        fill_percentage   = float(data['fill_percentage'])
        estimated_weight  = float(data['estimated_weight_kg'])
        distance_cm       = float(data.get('distance_cm', 0))
        bin_height_cm     = float(data.get('bin_height_cm', 0))
        battery_level     = int(data.get('battery_level', 100))
        waste_type        = data.get('waste_type', 'general').lower()
        # Optional: link to collection point directly
        point_name        = data.get('point_name', '')
        colony_id         = data.get('colony_id')

        # Sanity checks
        if fill_percentage < 0 or fill_percentage > 100:
            return jsonify({'error': 'fill_percentage must be between 0 and 100'}), 400
        if estimated_weight < 0 or estimated_weight > 500:
            return jsonify({'error': 'estimated_weight_kg out of range'}), 400

        # --- Log the reading ---
        _log_sensor_reading(device_id, colony_id, waste_type, fill_percentage,
                           estimated_weight, distance_cm, battery_level)

        # --- Update collection point if point_name is given ---
        point_updated = False
        point_info = None
        if point_name:
            point_info = _update_collection_point_by_name(point_name, fill_percentage, estimated_weight)
            point_updated = point_info is not None

        # --- Also update colony if colony_id is given ---
        if colony_id:
            _update_colony_waste_level(int(colony_id), waste_type, estimated_weight)

        print(f"[IoT] {device_id}: fill={fill_percentage:.1f}%, weight={estimated_weight:.2f}kg, point={'updated' if point_updated else 'N/A'}")

        return jsonify({
            'status': 'ok',
            'message': 'Sensor data received',
            'device_id': device_id,
            'fill_percentage': fill_percentage,
            'estimated_weight_kg': estimated_weight,
            'collection_point_updated': point_updated,
            'timestamp': datetime.now().isoformat()
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


# ============================
# ENDPOINT: Live fill level for frontend (polled every 5 seconds)
# ============================

@bp.route('/live/<point_name>', methods=['GET'])
def get_live_fill_level(point_name):
    """
    Get the latest sensor reading for a collection point by name.
    Frontend polls this every 5 seconds for live updates.
    No auth required — public data for the dashboard.
    """
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database not available'}), 503
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get the collection point info
                cursor.execute("""
                    SELECT cp.point_id, cp.point_name, cp.max_capacity_kg, cp.current_capacity_kg,
                           cp.colony_id, c.colony_name,
                           cp.waste_types_accepted
                    FROM collection_points cp
                    LEFT JOIN colonies c ON cp.colony_id = c.colony_id
                    WHERE LOWER(cp.point_name) = LOWER(%s) AND cp.is_active = TRUE
                    LIMIT 1
                """, (point_name,))
                point = cursor.fetchone()

                if not point:
                    return jsonify({'error': f'Collection point "{point_name}" not found'}), 404

                # Get latest sensor reading for this device
                cursor.execute("""
                    SELECT fill_percentage, estimated_weight_kg, distance_cm, 
                           battery_level, device_id, recorded_at
                    FROM sensor_readings
                    WHERE colony_id = %s
                    ORDER BY recorded_at DESC
                    LIMIT 1
                """, (point['colony_id'],))
                latest = cursor.fetchone()

                # Calculate fill percentage from collection point data
                max_cap = float(point['max_capacity_kg'] or 100)
                current_cap = float(point['current_capacity_kg'] or 0)
                db_fill_pct = min(100.0, (current_cap / max_cap) * 100.0) if max_cap > 0 else 0.0

                # Use sensor data if available, otherwise use DB data
                if latest:
                    fill_pct = float(latest['fill_percentage'])
                    weight = float(latest['estimated_weight_kg'])
                    distance = float(latest['distance_cm']) if latest['distance_cm'] else 0
                    device_id = latest['device_id']
                    last_update = latest['recorded_at'].isoformat() if latest['recorded_at'] else None
                    source = 'sensor'
                else:
                    fill_pct = db_fill_pct
                    weight = current_cap
                    distance = 0
                    device_id = None
                    last_update = None
                    source = 'database'

                # Get reading history (last 20 readings for chart)
                cursor.execute("""
                    SELECT fill_percentage, estimated_weight_kg, recorded_at
                    FROM sensor_readings
                    WHERE colony_id = %s
                    ORDER BY recorded_at DESC
                    LIMIT 20
                """, (point['colony_id'],))
                history = cursor.fetchall()
                
                history_data = []
                for h in reversed(history):
                    history_data.append({
                        'fill': float(h['fill_percentage']),
                        'weight': float(h['estimated_weight_kg']),
                        'time': h['recorded_at'].strftime('%H:%M:%S') if h['recorded_at'] else ''
                    })

                return jsonify({
                    'point_name': point['point_name'],
                    'point_id': point['point_id'],
                    'colony_name': point['colony_name'],
                    'max_capacity_kg': max_cap,
                    'fill_percentage': round(fill_pct, 1),
                    'estimated_weight_kg': round(weight, 2),
                    'distance_cm': round(distance, 1),
                    'device_id': device_id,
                    'last_update': last_update,
                    'source': source,
                    'history': history_data,
                    'timestamp': datetime.now().isoformat()
                }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================
# ENDPOINT: Get latest readings for a colony
# ============================

@bp.route('/readings/<int:colony_id>', methods=['GET'])
def get_colony_readings(colony_id):
    """Get latest sensor readings for a colony."""
    try:
        limit = request.args.get('limit', 20, type=int)
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database not available'}), 503
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT device_id, waste_type, fill_percentage, estimated_weight_kg,
                           distance_cm, battery_level, recorded_at
                    FROM sensor_readings
                    WHERE colony_id = %s
                    ORDER BY recorded_at DESC
                    LIMIT %s
                """, (colony_id, limit))
                readings = cursor.fetchall()
                for r in readings:
                    if r.get('recorded_at'):
                        r['recorded_at'] = r['recorded_at'].isoformat()
                return jsonify({'colony_id': colony_id, 'readings': readings, 'count': len(readings)}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================
# ENDPOINT: List all IoT devices
# ============================

@bp.route('/devices', methods=['GET'])
def get_iot_devices():
    """Get a summary of all IoT devices and their last reading."""
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database not available'}), 503
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT ON (device_id)
                        device_id, colony_id, waste_type, fill_percentage, 
                        estimated_weight_kg, battery_level, recorded_at
                    FROM sensor_readings
                    ORDER BY device_id, recorded_at DESC
                """)
                devices = cursor.fetchall()
                for d in devices:
                    if d.get('recorded_at'):
                        d['recorded_at'] = d['recorded_at'].isoformat()
                return jsonify({'devices': devices, 'count': len(devices)}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================
# HELPER FUNCTIONS
# ============================

def _log_sensor_reading(device_id, colony_id, waste_type, fill_pct, weight_kg, distance_cm, battery):
    """Store sensor reading in the sensor_readings table."""
    try:
        with get_db() as db:
            if not db:
                return
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sensor_readings 
                    (device_id, colony_id, waste_type, fill_percentage, estimated_weight_kg, 
                     distance_cm, battery_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (device_id, colony_id, waste_type, fill_pct, weight_kg, distance_cm, battery))
                db.commit()
    except Exception as e:
        print(f"[IoT] WARNING: Failed to log sensor reading: {e}")


def _update_collection_point_by_name(point_name, fill_percentage, weight_kg):
    """Update a collection point's current capacity using sensor data."""
    try:
        with get_db() as db:
            if not db:
                return None
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find the collection point
                cursor.execute("""
                    SELECT point_id, max_capacity_kg FROM collection_points
                    WHERE LOWER(point_name) = LOWER(%s) AND is_active = TRUE
                    LIMIT 1
                """, (point_name,))
                point = cursor.fetchone()
                
                if not point:
                    print(f"[IoT] WARNING: Collection point '{point_name}' not found")
                    return None
                
                # Set current capacity based on fill percentage
                max_cap = float(point['max_capacity_kg'] or 100)
                current_capacity = (fill_percentage / 100.0) * max_cap
                
                cursor.execute("""
                    UPDATE collection_points
                    SET current_capacity_kg = %s
                    WHERE point_id = %s
                """, (current_capacity, point['point_id']))
                db.commit()
                
                print(f"[IoT] Collection point '{point_name}' (ID:{point['point_id']}): {fill_percentage:.1f}% → {current_capacity:.2f}/{max_cap:.0f} kg")
                return point
    except Exception as e:
        print(f"[IoT] WARNING: Failed to update collection point: {e}")
        return None


def _update_colony_waste_level(colony_id, waste_type, weight_kg):
    """Update colony waste level using ABSOLUTE mode."""
    column_map = {
        'plastic': 'current_plastic_kg', 'paper': 'current_paper_kg',
        'cardboard': 'current_paper_kg', 'metal': 'current_metal_kg',
        'glass': 'current_glass_kg', 'textile': 'current_textile_kg',
        'organic': 'current_dry_waste_kg', 'general': 'current_dry_waste_kg'
    }
    column = column_map.get(waste_type)
    if not column:
        return
    try:
        with get_db() as db:
            if not db:
                return
            with db.cursor() as cursor:
                cursor.execute(f"UPDATE colonies SET {column} = %s WHERE colony_id = %s", (weight_kg, colony_id))
                cursor.execute("""
                    UPDATE colonies 
                    SET current_dry_waste_kg = current_plastic_kg + current_paper_kg + 
                                               current_metal_kg + current_glass_kg + current_textile_kg
                    WHERE colony_id = %s
                """, (colony_id,))
                db.commit()
    except Exception as e:
        print(f"[IoT] WARNING: Failed to update colony: {e}")
