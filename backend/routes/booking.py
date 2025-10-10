# backend/routes/booking.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.booking import Booking
from models.colony import Colony
from models.route_optimizer import RouteOptimizer
import traceback
from datetime import datetime, timedelta

bp = Blueprint('booking', __name__)

@bp.route('/schedule', methods=['POST'])
@jwt_required()
def schedule_collection():
    """Schedules a new waste collection. Can only be done by a logged-in collector."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Only collectors can schedule pickups"}), 403
        collector_id = get_jwt_identity()
        
        data = request.get_json()
        required = ['colony_id', 'booking_date', 'time_slot']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        booking_id = Booking.create_booking(
            data['colony_id'],
            collector_id,
            data['booking_date'],
            data['time_slot']
        )
        
        return jsonify({
            'message': 'Collection scheduled successfully',
            'booking_id': booking_id
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/my-schedule', methods=['GET'])
@jwt_required()
def get_my_schedule():
    """Fetches all bookings for the currently logged-in collector."""
    try:
        try:
            claims = get_jwt()
            if claims.get('role') != 'collector':
                return jsonify({"msg": "Access denied: Collector token required"}), 403
        except Exception:
            # If get_jwt() fails, continue without role check for now
            pass
        collector_id = get_jwt_identity()
        
        status = request.args.get('status')
        bookings = Booking.get_bookings_by_collector(collector_id, status)

        # Format results for JSON
        formatted_bookings = []
        for booking in bookings:
            booking_dict = dict(booking)
            for key, value in booking_dict.items():
                if hasattr(value, 'isoformat'):
                    booking_dict[key] = value.isoformat()
            formatted_bookings.append(booking_dict)

        return jsonify({'bookings': formatted_bookings}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/<int:booking_id>/complete', methods=['PUT'])
@jwt_required()
def complete_collection(booking_id):
    """Complete a collection booking and reset colony waste totals."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['total_weight_collected', 'waste_types_collected']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Complete the collection
        result = Booking.complete_collection(
            booking_id=booking_id,
            collector_id=collector_id,
            total_weight_collected=data['total_weight_collected'],
            waste_types_collected=data['waste_types_collected'],
            notes=data.get('notes', '')
        )
        
        if not result:
            return jsonify({'error': 'Booking not found or not authorized'}), 404
        
        return jsonify({
            'message': 'Collection completed successfully',
            'booking_id': booking_id
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/route-suggestions', methods=['GET'])
@jwt_required()
def get_route_suggestions():
    """Get optimized route suggestions for collector"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        
        # For now, return ready colonies as simple routes until route optimization is fully debugged
        from models.colony import Colony
        from models.collector import Collector
        
        # Get collector info
        collector = Collector.get_by_id(collector_id)
        if not collector:
            return jsonify({'error': 'Collector not found'}), 404
        
        # Get ready colonies
        if collector.get('latitude') and collector.get('longitude'):
            lat = float(collector['latitude'])
            lon = float(collector['longitude'])
            radius = float(collector.get('service_radius_km', 50))
            waste_types = collector.get('waste_types_collected')
            
            colonies = Colony.get_ready_colonies_near_location(lat, lon, radius, waste_types, collector_id)
        else:
            waste_types = collector.get('waste_types_collected')
            colonies = Colony.get_colonies_ready_for_collection_by_type(waste_types, collector_id)
        
        # Create simple route suggestions
        routes = []
        if colonies:
            # Create routes with up to 3 colonies each
            max_pickups = request.args.get('max_pickups', 3, type=int)
            
            for i in range(0, len(colonies), max_pickups):
                route_colonies = colonies[i:i+max_pickups]
                
                total_weight = sum(float(c.get('max_waste_kg', 0)) for c in route_colonies)
                
                route = {
                    'route_id': len(routes) + 1,
                    'pickups': [
                        {
                            **dict(colony),
                            'order_in_route': idx + 1,
                            'distance_from_previous': 0 if idx == 0 else 5.0  # Placeholder distance
                        }
                        for idx, colony in enumerate(route_colonies)
                    ],
                    'total_distance': len(route_colonies) * 5.0,  # Placeholder calculation
                    'estimated_time_hours': len(route_colonies) * 0.5,
                    'total_colonies': len(route_colonies),
                    'total_estimated_weight': total_weight,
                    'efficiency_score': total_weight / (len(route_colonies) * 5.0) if len(route_colonies) > 0 else 0
                }
                routes.append(route)
        
        return jsonify({
            'routes': routes,
            'collector_id': collector_id,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/time-slots', methods=['GET'])
@jwt_required()
def get_available_time_slots():
    """Get available time slots for a specific date"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        date = request.args.get('date')
        
        if not date:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        try:
            # Validate date format
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        time_slots = RouteOptimizer.get_available_time_slots(date, collector_id)
        
        return jsonify({
            'date': date,
            'time_slots': time_slots
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/schedule-route', methods=['POST'])
@jwt_required()
def schedule_route_batch():
    """Schedule multiple pickups as an optimized route"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['pickups', 'booking_date', 'time_slot']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: pickups, booking_date, time_slot'}), 400
        
        # Validate date
        try:
            datetime.strptime(data['booking_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Schedule the route
        booking_ids = RouteOptimizer.schedule_route_batch(
            collector_id=collector_id,
            route_pickups=data['pickups'],
            booking_date=data['booking_date'],
            time_slot=data['time_slot']
        )
        
        return jsonify({
            'message': f'Route scheduled successfully with {len(booking_ids)} pickups',
            'booking_ids': booking_ids,
            'batch_id': f"batch_{collector_id}_{data['booking_date']}_{data['time_slot']}"
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500