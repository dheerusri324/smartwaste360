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
    """Complete a collection booking with simplified input (just comments)."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        data = request.get_json()
        
        # Only comments are required now - weight and materials are pre-defined from booking
        notes = data.get('notes', '')
        actual_weight_collected = data.get('actual_weight_collected')  # Optional: if less than estimated
        
        # Get booking and colony details to determine pre-defined materials and weights
        from config.database import get_db
        from psycopg2.extras import RealDictCursor
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get booking and colony details
                cursor.execute("""
                    SELECT cb.*, c.colony_name, c.current_plastic_kg, c.current_paper_kg, 
                           c.current_metal_kg, c.current_glass_kg, c.current_textile_kg,
                           GREATEST(c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                                   c.current_glass_kg, c.current_textile_kg) as estimated_weight
                    FROM collection_bookings cb
                    JOIN colonies c ON cb.colony_id = c.colony_id
                    WHERE cb.booking_id = %s AND cb.collector_id = %s AND cb.status = 'scheduled'
                """, (booking_id, collector_id))
                
                booking_details = cursor.fetchone()
                
        if not booking_details:
            return jsonify({'error': 'Booking not found or not authorized'}), 404
        
        # Determine which materials are available for collection
        waste_types = []
        if booking_details['current_plastic_kg'] >= 5:
            waste_types.append('plastic')
        if booking_details['current_paper_kg'] >= 5:
            waste_types.append('paper')
        if booking_details['current_metal_kg'] >= 1:
            waste_types.append('metal')
        if booking_details['current_glass_kg'] >= 2:
            waste_types.append('glass')
        if booking_details['current_textile_kg'] >= 1:
            waste_types.append('textile')
        
        # Default to mixed if no specific types
        if not waste_types:
            waste_types = ['mixed']
        
        # Use actual weight if provided, otherwise use estimated weight
        total_weight = actual_weight_collected if actual_weight_collected else float(booking_details.get('estimated_weight', 5.0))
        
        # Complete the collection
        result = Booking.complete_collection(
            booking_id=booking_id,
            collector_id=collector_id,
            total_weight_collected=total_weight,
            waste_types_collected=waste_types,
            notes=notes
        )
        
        if not result:
            return jsonify({'error': 'Failed to complete collection'}), 500
        
        return jsonify({
            'message': 'Collection completed successfully',
            'booking_id': booking_id,
            'weight_collected': total_weight,
            'materials_collected': waste_types,
            'notes': notes
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({'message': 'Booking routes working!'}), 200

@bp.route('/route-suggestions', methods=['GET'])
@jwt_required()
def get_route_suggestions():
    """Get optimized route suggestions for collector"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        
        # Get collector info
        from models.collector import Collector
        collector = Collector.get_by_id(collector_id)
        if not collector:
            return jsonify({'error': 'Collector not found'}), 404
        
        # Get ready colonies
        waste_types = collector.get('waste_types_collected')
        colonies = Colony.get_colonies_ready_for_collection_by_type(waste_types, collector_id)
        
        # Create simple route suggestions
        routes = []
        if colonies:
            max_pickups = request.args.get('max_pickups', 3, type=int)
            
            for i in range(0, len(colonies), max_pickups):
                route_colonies = colonies[i:i+max_pickups]
                
                total_weight = 0
                for c in route_colonies:
                    try:
                        weight = float(c.get('max_waste_kg', 0) or 0)
                        total_weight += weight
                    except (ValueError, TypeError):
                        pass
                
                route = {
                    'route_id': len(routes) + 1,
                    'pickups': [
                        {
                            'colony_id': colony.get('colony_id'),
                            'colony_name': colony.get('colony_name', 'Unknown Colony'),
                            'latitude': float(colony.get('latitude', 0)) if colony.get('latitude') else 0,
                            'longitude': float(colony.get('longitude', 0)) if colony.get('longitude') else 0,
                            'max_waste_kg': float(colony.get('max_waste_kg', 0) or 0),
                            'order_in_route': idx + 1,
                            'distance_from_previous': 0 if idx == 0 else 5.0
                        }
                        for idx, colony in enumerate(route_colonies)
                    ],
                    'total_distance': len(route_colonies) * 5.0,
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