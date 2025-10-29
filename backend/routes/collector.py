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

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_collector_dashboard():
    """Get collector dashboard statistics"""
    try:
        collector_id = get_jwt_identity()
        claims = get_jwt()

        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403

        from config.database import get_db
        from psycopg2.extras import RealDictCursor
        
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get total collections
                cursor.execute("""
                    SELECT COUNT(*) as total_collections
                    FROM collection_bookings
                    WHERE collector_id = %s AND status = 'completed'
                """, (collector_id,))
                total_collections = cursor.fetchone()['total_collections'] or 0
                
                # Get pending requests
                cursor.execute("""
                    SELECT COUNT(*) as pending_requests
                    FROM collection_bookings
                    WHERE collector_id = %s AND status = 'scheduled'
                """, (collector_id,))
                pending_requests = cursor.fetchone()['pending_requests'] or 0
                
                # Get completed today
                cursor.execute("""
                    SELECT COUNT(*) as completed_today
                    FROM collection_bookings
                    WHERE collector_id = %s 
                    AND status = 'completed'
                    AND DATE(completed_at) = CURRENT_DATE
                """, (collector_id,))
                completed_today = cursor.fetchone()['completed_today'] or 0
                
                # Get total weight collected
                cursor.execute("""
                    SELECT COALESCE(total_weight_collected, 0) as total_weight
                    FROM collectors
                    WHERE collector_id = %s
                """, (collector_id,))
                total_weight = float(cursor.fetchone()['total_weight'] or 0)
                
                # Get total users served (unique users from transactions)
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as total_users
                    FROM user_transactions
                    WHERE collector_id = %s
                """, (collector_id,))
                total_users = cursor.fetchone()['total_users'] or 0
                
                # Calculate earnings (example: $0.50 per kg)
                total_earnings = total_weight * 0.50
                
                return jsonify({
                    'total_collections': total_collections,
                    'pending_requests': pending_requests,
                    'total_earnings': round(total_earnings, 2),
                    'completed_today': completed_today,
                    'total_users': total_users,
                    'total_weight_collected': round(total_weight, 2)
                }), 200
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch dashboard data: {str(e)}'}), 500

@bp.route('/recent-activities', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """Get recent collection activities for collector"""
    try:
        collector_id = get_jwt_identity()
        claims = get_jwt()

        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403

        from config.database import get_db
        from psycopg2.extras import RealDictCursor
        
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        cb.booking_id,
                        cb.booking_date,
                        cb.time_slot,
                        cb.status,
                        cb.total_weight_collected,
                        cb.completed_at,
                        c.colony_name,
                        c.colony_id
                    FROM collection_bookings cb
                    JOIN colonies c ON cb.colony_id = c.colony_id
                    WHERE cb.collector_id = %s
                    ORDER BY cb.created_at DESC
                    LIMIT 10
                """, (collector_id,))
                
                activities = cursor.fetchall()
                
                # Format activities
                formatted_activities = []
                for activity in activities:
                    formatted_activities.append({
                        'id': activity['booking_id'],
                        'colony_name': activity['colony_name'],
                        'colony_id': activity['colony_id'],
                        'user_name': f"Colony {activity['colony_id']}",  # Placeholder
                        'status': activity['status'],
                        'pickup_time': activity['booking_date'].isoformat() if activity['booking_date'] else None,
                        'weight_collected': float(activity['total_weight_collected']) if activity['total_weight_collected'] else 0,
                        'completed_at': activity['completed_at'].isoformat() if activity['completed_at'] else None
                    })
                
                return jsonify({'activities': formatted_activities}), 200
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch activities: {str(e)}'}), 500

@bp.route('/complete-collection', methods=['POST'])
@jwt_required()
def complete_collection():
    """Complete a waste collection and update colony waste amounts"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Only collectors can complete collections"}), 403
        
        collector_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['colony_id', 'total_weight', 'waste_types']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: colony_id, total_weight, waste_types'}), 400
        
        colony_id = data['colony_id']
        total_weight = float(data['total_weight'])
        waste_types = data['waste_types']  # Dict with waste type amounts
        notes = data.get('notes', '')
        
        # Simplified approach - just update colony waste amounts
        from config.database import get_db
        from psycopg2.extras import RealDictCursor
        
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if colony exists
                cursor.execute("SELECT colony_id FROM colonies WHERE colony_id = %s", (colony_id,))
                if not cursor.fetchone():
                    return jsonify({'error': 'Colony not found'}), 404
                
                # Update colony waste amounts (reduce by collected amounts)
                update_fields = []
                update_values = []
                
                if waste_types.get('plastic', 0) > 0:
                    update_fields.append("current_plastic_kg = GREATEST(0, current_plastic_kg - %s)")
                    update_values.append(float(waste_types['plastic']))
                
                if waste_types.get('paper', 0) > 0:
                    update_fields.append("current_paper_kg = GREATEST(0, current_paper_kg - %s)")
                    update_values.append(float(waste_types['paper']))
                
                if waste_types.get('metal', 0) > 0:
                    update_fields.append("current_metal_kg = GREATEST(0, current_metal_kg - %s)")
                    update_values.append(float(waste_types['metal']))
                
                if waste_types.get('glass', 0) > 0:
                    update_fields.append("current_glass_kg = GREATEST(0, current_glass_kg - %s)")
                    update_values.append(float(waste_types['glass']))
                
                if waste_types.get('textile', 0) > 0:
                    update_fields.append("current_textile_kg = GREATEST(0, current_textile_kg - %s)")
                    update_values.append(float(waste_types['textile']))
                
                if waste_types.get('organic', 0) > 0:
                    update_fields.append("current_dry_waste_kg = GREATEST(0, current_dry_waste_kg - %s)")
                    update_values.append(float(waste_types['organic']))
                
                if update_fields:
                    update_sql = f"""
                        UPDATE colonies 
                        SET {', '.join(update_fields)}, last_collection_date = CURRENT_TIMESTAMP
                        WHERE colony_id = %s
                    """
                    update_values.append(colony_id)
                    cursor.execute(update_sql, update_values)
                    
                # Recalculate total dry waste after collection
                cursor.execute("""
                    UPDATE colonies 
                    SET current_dry_waste_kg = current_plastic_kg + current_paper_kg + current_metal_kg + current_glass_kg + current_textile_kg
                    WHERE colony_id = %s
                """, (colony_id,))
                
                # Update collector's total weight collected
                cursor.execute("""
                    UPDATE collectors 
                    SET total_weight_collected = total_weight_collected + %s
                    WHERE collector_id = %s
                """, (total_weight, collector_id))
                
                db.commit()
                
                return jsonify({
                    'message': 'Collection completed successfully',
                    'total_weight': total_weight,
                    'colony_updated': True,
                    'collector_updated': True,
                    'waste_collected': waste_types
                }), 200
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Collection completion failed: {str(e)}'}), 500