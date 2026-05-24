# backend/routes/advanced_features.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import traceback
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService
from services.route_optimization import RouteOptimizer
from services.realtime_service import RealtimeService
from models.achievement import Achievement

bp = Blueprint('advanced', __name__)

# Achievement System Routes
@bp.route('/achievements/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_achievements(user_id):
    """Get achievements for a user"""
    try:
        claims = get_jwt()
        current_user_id = int(get_jwt_identity())
        
        # Users can only see their own achievements, admins can see any
        if claims.get('role') != 'admin' and current_user_id != user_id:
            return jsonify({"msg": "Access denied"}), 403
        
        # Safely fetch earned achievements and progress
        earned_achievements = []
        progress = {}
        try:
            earned_achievements = Achievement.get_user_achievements(user_id) or []
        except Exception as db_err:
            print(f"[WARN] Could not fetch user_achievements (table may not exist): {db_err}")
        
        try:
            progress = Achievement.get_user_progress(user_id) or {}
        except Exception as db_err:
            print(f"[WARN] Could not fetch user_statistics (table may not exist): {db_err}")
        
        # Build unified array for the frontend — always returns all 7 achievements
        unified_achievements = []
        earned_ids = set()
        for a in earned_achievements:
            # Match by achievement_id key if present, else fallback to name
            if 'criteria' in a:
                # This is from the ACHIEVEMENTS dict spread
                for aid, adata in Achievement.ACHIEVEMENTS.items():
                    if adata['name'] == a.get('name'):
                        earned_ids.add(aid)
                        break
            else:
                earned_ids.add(a.get('achievement_id', a.get('id', '')))
        
        for ach_id, ach_data in Achievement.ACHIEVEMENTS.items():
            is_earned = ach_id in earned_ids
            target_val = list(ach_data['criteria'].values())[0]
            
            if is_earned:
                current_val = target_val
            else:
                prog_data = progress.get(ach_id, {})
                prog_percent = prog_data.get('progress', 0)
                current_val = (prog_percent / 100.0) * target_val
                current_val = int(current_val) if isinstance(target_val, int) else round(current_val, 2)
                
            unified_achievements.append({
                'id': ach_id,
                'name': ach_data['name'],
                'description': ach_data['description'],
                'category': ach_data.get('category', 'recycling'),
                'earned': is_earned,
                'progress': {
                    'current': current_val,
                    'target': target_val
                }
            })
        
        return jsonify({
            'achievements': unified_achievements,
            'progress': progress
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        # FALLBACK: Even if everything explodes, return the static achievements
        fallback = []
        for ach_id, ach_data in Achievement.ACHIEVEMENTS.items():
            target_val = list(ach_data['criteria'].values())[0]
            fallback.append({
                'id': ach_id,
                'name': ach_data['name'],
                'description': ach_data['description'],
                'category': ach_data.get('category', 'recycling'),
                'earned': False,
                'progress': {'current': 0, 'target': target_val}
            })
        return jsonify({'achievements': fallback, 'progress': {}}), 200

@bp.route('/achievements/backfill', methods=['GET', 'POST'])
def backfill_achievements():
    """One-time backfill: compute user_statistics from waste_logs and award achievements"""
    try:
        from config.database import get_db
        from psycopg2.extras import RealDictCursor
        
        results = {'users_processed': 0, 'achievements_awarded': [], 'errors': []}
        
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Compute stats from waste_logs for ALL users
                cursor.execute("""
                    SELECT 
                        user_id,
                        COUNT(*) as waste_classifications,
                        COUNT(*) FILTER (WHERE LOWER(predicted_category) = 'plastic') as plastic_classifications,
                        COUNT(*) FILTER (WHERE LOWER(predicted_category) = 'paper') as paper_classifications,
                        COUNT(*) FILTER (WHERE LOWER(predicted_category) = 'metal') as metal_classifications,
                        COUNT(*) FILTER (WHERE LOWER(predicted_category) = 'glass') as glass_classifications,
                        COUNT(*) FILTER (WHERE LOWER(predicted_category) = 'organic') as organic_classifications,
                        COUNT(*) FILTER (WHERE LOWER(predicted_category) = 'textile') as textile_classifications,
                        COALESCE(SUM(weight_kg), 0) as total_weight_kg,
                        MAX(created_at::date) as last_classification_date
                    FROM waste_logs
                    GROUP BY user_id
                """)
                user_stats = cursor.fetchall()
                
                for stats in user_stats:
                    uid = stats['user_id']
                    try:
                        # UPSERT into user_statistics
                        cursor.execute("""
                            INSERT INTO user_statistics (
                                user_id, waste_classifications, plastic_classifications,
                                paper_classifications, metal_classifications, glass_classifications,
                                organic_classifications, textile_classifications,
                                total_weight_kg, last_classification_date, consecutive_days,
                                colony_collections_triggered, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 0, CURRENT_TIMESTAMP)
                            ON CONFLICT (user_id) DO UPDATE SET
                                waste_classifications = EXCLUDED.waste_classifications,
                                plastic_classifications = EXCLUDED.plastic_classifications,
                                paper_classifications = EXCLUDED.paper_classifications,
                                metal_classifications = EXCLUDED.metal_classifications,
                                glass_classifications = EXCLUDED.glass_classifications,
                                organic_classifications = EXCLUDED.organic_classifications,
                                textile_classifications = EXCLUDED.textile_classifications,
                                total_weight_kg = EXCLUDED.total_weight_kg,
                                last_classification_date = EXCLUDED.last_classification_date,
                                updated_at = CURRENT_TIMESTAMP
                        """, (
                            uid,
                            stats['waste_classifications'],
                            stats['plastic_classifications'],
                            stats['paper_classifications'],
                            stats['metal_classifications'],
                            stats['glass_classifications'],
                            stats['organic_classifications'],
                            stats['textile_classifications'],
                            stats['total_weight_kg'],
                            stats['last_classification_date']
                        ))
                        results['users_processed'] += 1
                    except Exception as user_err:
                        results['errors'].append(f"User {uid}: {str(user_err)}")
                
                db.commit()
        
        # Now run achievement checks for all processed users
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT user_id FROM user_statistics")
                all_users = cursor.fetchall()
        
        for u in all_users:
            try:
                new_achs = Achievement.check_and_award_achievements(u['user_id'])
                if new_achs:
                    for ach in new_achs:
                        results['achievements_awarded'].append({
                            'user_id': u['user_id'],
                            'achievement': ach['name'],
                            'points': ach['points']
                        })
            except Exception as ach_err:
                results['errors'].append(f"Achievement check for user {u['user_id']}: {str(ach_err)}")
        
        return jsonify({
            'message': 'Backfill completed!',
            'results': results
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Backfill failed: {str(e)}'}), 500

@bp.route('/achievements/check/<int:user_id>', methods=['POST'])
@jwt_required()
def check_achievements(user_id):
    """Check and award new achievements for a user"""
    try:
        claims = get_jwt()
        current_user_id = int(get_jwt_identity())
        
        # Users can only check their own achievements
        if claims.get('role') not in ['admin', 'system'] and current_user_id != user_id:
            return jsonify({"msg": "Access denied"}), 403
        
        new_achievements = Achievement.check_and_award_achievements(user_id)
        
        # Send notifications for new achievements
        for achievement in new_achievements:
            NotificationService.send_achievement_notification(user_id, achievement)
        
        return jsonify({
            'new_achievements': new_achievements,
            'count': len(new_achievements)
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

# Analytics Routes
@bp.route('/analytics/waste-prediction/<int:colony_id>', methods=['GET'])
@jwt_required()
def get_waste_prediction(colony_id):
    """Get waste generation predictions for a colony"""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'collector']:
            return jsonify({"msg": "Access denied: Admin or collector access required"}), 403
        
        days_ahead = request.args.get('days', 7, type=int)
        predictions = AnalyticsService.predict_waste_generation(colony_id, days_ahead)
        
        if not predictions:
            return jsonify({'error': 'Insufficient data for predictions'}), 404
        
        return jsonify({
            'colony_id': colony_id,
            'days_ahead': days_ahead,
            'predictions': predictions
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/analytics/collection-schedule/<int:colony_id>', methods=['GET'])
@jwt_required()
def get_optimal_collection_schedule(colony_id):
    """Get optimal collection schedule for a colony"""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'collector']:
            return jsonify({"msg": "Access denied: Admin or collector access required"}), 403
        
        schedule = AnalyticsService.get_optimal_collection_schedule(colony_id)
        
        if not schedule:
            return jsonify({'error': 'Unable to generate schedule'}), 404
        
        return jsonify(schedule), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/analytics/user-engagement', methods=['GET'])
@jwt_required()
def get_user_engagement_insights():
    """Get user engagement analytics"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403
        
        date_range = request.args.get('days', 30, type=int)
        insights = AnalyticsService.get_user_engagement_insights(date_range)
        
        return jsonify(insights), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/analytics/environmental-impact', methods=['GET'])
@jwt_required()
def get_environmental_impact_forecast():
    """Get environmental impact forecast"""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'user', 'collector']:
            return jsonify({"msg": "Access denied"}), 403
        
        colony_id = request.args.get('colony_id', type=int)
        days_ahead = request.args.get('days', 30, type=int)
        
        forecast = AnalyticsService.get_environmental_impact_forecast(colony_id, days_ahead)
        
        return jsonify(forecast), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

# Notification Routes
@bp.route('/notifications/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_notifications(user_id):
    """Get notifications for a user"""
    try:
        claims = get_jwt()
        current_user_id = int(get_jwt_identity())
        
        # Users can only see their own notifications
        if claims.get('role') != 'admin' and current_user_id != user_id:
            return jsonify({"msg": "Access denied"}), 403
        
        limit = request.args.get('limit', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notifications = NotificationService.get_user_notifications(user_id, limit, unread_only)
        stats = NotificationService.get_notification_stats(user_id)
        
        return jsonify({
            'notifications': notifications,
            'stats': stats
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        user_id = int(get_jwt_identity())
        success = NotificationService.mark_notification_read(notification_id, user_id)
        
        if success:
            return jsonify({'message': 'Notification marked as read'}), 200
        else:
            return jsonify({'error': 'Notification not found or access denied'}), 404
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

# Route Optimization Routes
@bp.route('/route-optimization/collector/<collector_id>', methods=['POST'])
@jwt_required()
def optimize_collection_route(collector_id):
    """Optimize collection route for a collector"""
    try:
        claims = get_jwt()
        current_collector_id = get_jwt_identity()
        
        # Collectors can only optimize their own routes, admins can optimize any
        if claims.get('role') != 'admin' and current_collector_id != collector_id:
            return jsonify({"msg": "Access denied"}), 403
        
        data = request.get_json()
        collection_points = data.get('collection_points', [])
        collector_location = data.get('collector_location')
        
        if not collection_points:
            return jsonify({'error': 'No collection points provided'}), 400
        
        optimization = RouteOptimizer.optimize_collection_route(
            collector_id, collection_points, collector_location
        )
        
        return jsonify(optimization), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/route-optimization/schedule/<collector_id>', methods=['GET'])
@jwt_required()
def get_optimal_schedule(collector_id):
    """Get optimal collection schedule for a collector"""
    try:
        claims = get_jwt()
        current_collector_id = get_jwt_identity()
        
        # Collectors can only see their own schedules, admins can see any
        if claims.get('role') != 'admin' and current_collector_id != collector_id:
            return jsonify({"msg": "Access denied"}), 403
        
        days_ahead = request.args.get('days', 7, type=int)
        schedule = RouteOptimizer.get_optimal_collection_schedule(collector_id, days_ahead)
        
        return jsonify(schedule), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

# Real-time Data Routes
@bp.route('/realtime/system-stats', methods=['GET'])
@jwt_required()
def get_live_system_stats():
    """Get real-time system statistics"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403
        
        stats = RealtimeService.get_live_system_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/realtime/colony-stats/<int:colony_id>', methods=['GET'])
@jwt_required()
def get_live_colony_stats(colony_id):
    """Get real-time colony statistics"""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'collector']:
            return jsonify({"msg": "Access denied"}), 403
        
        stats = RealtimeService.get_live_colony_stats(colony_id)
        return jsonify(stats), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/realtime/user-stats/<int:user_id>', methods=['GET'])
@jwt_required()
def get_live_user_stats(user_id):
    """Get real-time user statistics"""
    try:
        claims = get_jwt()
        current_user_id = int(get_jwt_identity())
        
        # Users can only see their own stats, admins can see any
        if claims.get('role') != 'admin' and current_user_id != user_id:
            return jsonify({"msg": "Access denied"}), 403
        
        stats = RealtimeService.get_live_user_stats(user_id)
        return jsonify(stats), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/realtime/system-health', methods=['GET'])
@jwt_required()
def get_system_health():
    """Get detailed system health metrics"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403
        
        health = RealtimeService.get_system_health_metrics()
        return jsonify(health), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

# Batch Operations for System Maintenance
@bp.route('/system/send-reminders', methods=['POST'])
@jwt_required()
def send_reminder_notifications():
    """Send reminder notifications to inactive users"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403
        
        count = NotificationService.send_reminder_notifications()
        return jsonify({
            'message': f'Sent {count} reminder notifications',
            'count': count
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/system/send-weekly-summaries', methods=['POST'])
@jwt_required()
def send_weekly_summaries():
    """Send weekly summary notifications"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin access required"}), 403
        
        count = NotificationService.send_weekly_summary_notifications()
        return jsonify({
            'message': f'Sent {count} weekly summary notifications',
            'count': count
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500