# backend/routes/migration.py
"""
One-time migration scripts to fix historical data
"""

from flask import Blueprint, jsonify, request
from config.database import get_db
from psycopg2.extras import RealDictCursor
import traceback

bp = Blueprint('migration', __name__)

@bp.route('/backfill-colony-points', methods=['POST'])
def backfill_colony_points():
    """
    Backfill colony points from all historical user points.
    This adds all user points to their respective colonies.
    """
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database connection not available'}), 500
            
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get all users with their points and colony_id
                cursor.execute("""
                    SELECT user_id, username, colony_id, total_points, total_weight_recycled
                    FROM users
                    WHERE colony_id IS NOT NULL AND total_points > 0
                    ORDER BY colony_id, user_id
                """)
                users = cursor.fetchall()
                
                if not users:
                    return jsonify({
                        'status': 'success',
                        'message': 'No users with points found',
                        'users_processed': 0
                    })
                
                # Group users by colony
                colony_updates = {}
                user_details = []
                
                for user in users:
                    colony_id = user['colony_id']
                    user_points = user['total_points']
                    
                    if colony_id not in colony_updates:
                        colony_updates[colony_id] = {
                            'total_points': 0,
                            'user_count': 0,
                            'users': []
                        }
                    
                    colony_updates[colony_id]['total_points'] += user_points
                    colony_updates[colony_id]['user_count'] += 1
                    colony_updates[colony_id]['users'].append({
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'points': user_points
                    })
                    
                    user_details.append({
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'colony_id': colony_id,
                        'points_added': user_points
                    })
                
                # Update each colony's total_points
                colonies_updated = []
                for colony_id, data in colony_updates.items():
                    cursor.execute("""
                        UPDATE colonies 
                        SET total_points = total_points + %s
                        WHERE colony_id = %s
                        RETURNING colony_id, colony_name, total_points
                    """, (data['total_points'], colony_id))
                    
                    colony = cursor.fetchone()
                    if colony:
                        colonies_updated.append({
                            'colony_id': colony['colony_id'],
                            'colony_name': colony['colony_name'],
                            'new_total_points': colony['total_points'],
                            'points_added': data['total_points'],
                            'users_count': data['user_count'],
                            'users': data['users']
                        })
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Colony points backfilled successfully',
                    'users_processed': len(users),
                    'colonies_updated': len(colonies_updated),
                    'colony_details': colonies_updated,
                    'user_details': user_details
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Failed to backfill colony points'
        }), 500

@bp.route('/backfill-colony-waste', methods=['POST'])
def backfill_colony_waste():
    """
    Backfill colony waste amounts from all historical waste logs.
    This recalculates colony waste based on all user classifications.
    """
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database connection not available'}), 500
            
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get waste totals by colony and category
                cursor.execute("""
                    SELECT 
                        u.colony_id,
                        c.colony_name,
                        wl.predicted_category,
                        SUM(wl.weight_kg) as total_weight
                    FROM waste_logs wl
                    JOIN users u ON wl.user_id = u.user_id
                    JOIN colonies c ON u.colony_id = c.colony_id
                    WHERE u.colony_id IS NOT NULL
                    GROUP BY u.colony_id, c.colony_name, wl.predicted_category
                    ORDER BY u.colony_id, wl.predicted_category
                """)
                
                waste_data = cursor.fetchall()
                
                if not waste_data:
                    return jsonify({
                        'status': 'success',
                        'message': 'No waste logs found',
                        'colonies_updated': 0
                    })
                
                # Group by colony
                colony_waste = {}
                for row in waste_data:
                    colony_id = row['colony_id']
                    if colony_id not in colony_waste:
                        colony_waste[colony_id] = {
                            'colony_name': row['colony_name'],
                            'waste': {}
                        }
                    colony_waste[colony_id]['waste'][row['predicted_category']] = float(row['total_weight'])
                
                # Update each colony
                colonies_updated = []
                for colony_id, data in colony_waste.items():
                    waste = data['waste']
                    
                    # Map categories to columns
                    plastic = waste.get('plastic', 0)
                    paper = waste.get('paper', 0) + waste.get('cardboard', 0)
                    metal = waste.get('metal', 0)
                    glass = waste.get('glass', 0)
                    textile = waste.get('textile', 0)
                    
                    cursor.execute("""
                        UPDATE colonies 
                        SET current_plastic_kg = %s,
                            current_paper_kg = %s,
                            current_metal_kg = %s,
                            current_glass_kg = %s,
                            current_textile_kg = %s,
                            current_dry_waste_kg = %s
                        WHERE colony_id = %s
                        RETURNING colony_id, colony_name, 
                                  current_plastic_kg, current_paper_kg, current_metal_kg,
                                  current_glass_kg, current_textile_kg, current_dry_waste_kg
                    """, (plastic, paper, metal, glass, textile, 
                          plastic + paper + metal + glass + textile, colony_id))
                    
                    colony = cursor.fetchone()
                    if colony:
                        colonies_updated.append(dict(colony))
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Colony waste backfilled successfully',
                    'colonies_updated': len(colonies_updated),
                    'colony_details': colonies_updated
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Failed to backfill colony waste'
        }), 500

@bp.route('/migration-status', methods=['GET'])
def migration_status():
    """Check current colony points and waste status"""
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database connection not available'}), 500
            
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get colony stats
                cursor.execute("""
                    SELECT 
                        c.colony_id,
                        c.colony_name,
                        c.total_points,
                        c.total_users,
                        c.current_plastic_kg,
                        c.current_paper_kg,
                        c.current_metal_kg,
                        c.current_glass_kg,
                        c.current_textile_kg,
                        c.current_dry_waste_kg,
                        SUM(u.total_points) as sum_user_points,
                        COUNT(u.user_id) as active_users
                    FROM colonies c
                    LEFT JOIN users u ON c.colony_id = u.colony_id
                    GROUP BY c.colony_id
                    ORDER BY c.colony_id
                """)
                
                colonies = cursor.fetchall()
                
                return jsonify({
                    'status': 'success',
                    'colonies': [dict(c) for c in colonies]
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/fix-collector-bookings', methods=['POST'])
def fix_collector_bookings():
    """Add weight data to completed bookings that are missing it"""
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database connection not available'}), 500
            
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find completed bookings with no weight
                cursor.execute("""
                    SELECT booking_id, collector_id, colony_id
                    FROM collection_bookings
                    WHERE status = 'completed' 
                      AND (total_weight_collected IS NULL OR total_weight_collected = 0)
                """)
                
                bookings = cursor.fetchall()
                
                if not bookings:
                    return jsonify({
                        'status': 'success',
                        'message': 'All completed bookings already have weight data',
                        'bookings_fixed': 0
                    })
                
                # Add default weight (50kg) to each booking
                for booking in bookings:
                    cursor.execute("""
                        UPDATE collection_bookings
                        SET total_weight_collected = 50.0
                        WHERE booking_id = %s
                    """, (booking['booking_id'],))
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': f'Added weight data to {len(bookings)} bookings',
                    'bookings_fixed': len(bookings),
                    'bookings': [dict(b) for b in bookings]
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/check-collector-data', methods=['GET'])
def check_collector_data():
    """Check actual collector data for debugging"""
    try:
        collector_id = request.args.get('collector_id', 'metal')
        
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database connection not available'}), 500
            
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get collector info
                cursor.execute("""
                    SELECT collector_id, name, total_weight_collected
                    FROM collectors
                    WHERE collector_id = %s
                """, (collector_id,))
                collector = cursor.fetchone()
                
                # Get all bookings
                cursor.execute("""
                    SELECT 
                        booking_id,
                        colony_id,
                        status,
                        total_weight_collected,
                        completed_at,
                        created_at
                    FROM collection_bookings
                    WHERE collector_id = %s
                    ORDER BY created_at DESC
                """, (collector_id,))
                bookings = cursor.fetchall()
                
                # Calculate sum
                total_from_bookings = sum(
                    float(b['total_weight_collected'] or 0) 
                    for b in bookings 
                    if b['status'] == 'completed'
                )
                
                return jsonify({
                    'status': 'success',
                    'collector': dict(collector) if collector else None,
                    'bookings': [dict(b) for b in bookings],
                    'total_bookings': len(bookings),
                    'completed_bookings': len([b for b in bookings if b['status'] == 'completed']),
                    'total_weight_from_bookings': total_from_bookings,
                    'collector_total_weight': float(collector['total_weight_collected'] or 0) if collector else 0
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/sync-collector-stats', methods=['POST'])
def sync_collector_stats():
    """Sync collector total_weight_collected from completed bookings"""
    try:
        with get_db() as db:
            if not db:
                return jsonify({'error': 'Database connection not available'}), 500
            
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get all collectors with their completed bookings
                cursor.execute("""
                    SELECT 
                        c.collector_id,
                        c.name,
                        c.total_weight_collected as current_total,
                        COALESCE(SUM(cb.total_weight_collected), 0) as actual_total,
                        COUNT(cb.booking_id) as completed_bookings
                    FROM collectors c
                    LEFT JOIN collection_bookings cb ON c.collector_id = cb.collector_id 
                        AND cb.status = 'completed'
                    GROUP BY c.collector_id, c.name, c.total_weight_collected
                """)
                
                collectors = cursor.fetchall()
                
                updated_collectors = []
                for collector in collectors:
                    actual_total = float(collector['actual_total'] or 0)
                    current_total = float(collector['current_total'] or 0)
                    
                    if actual_total != current_total:
                        # Update collector's total
                        cursor.execute("""
                            UPDATE collectors 
                            SET total_weight_collected = %s
                            WHERE collector_id = %s
                        """, (actual_total, collector['collector_id']))
                        
                        updated_collectors.append({
                            'collector_id': collector['collector_id'],
                            'name': collector['name'],
                            'old_total': current_total,
                            'new_total': actual_total,
                            'completed_bookings': collector['completed_bookings']
                        })
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': f'Synced {len(updated_collectors)} collectors',
                    'collectors_updated': updated_collectors,
                    'total_collectors_checked': len(collectors)
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
