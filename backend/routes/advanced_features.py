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
        
        achievements = Achievement.get_user_achievements(user_id)
        progress = Achievement.get_user_progress(user_id)
        
        return jsonify({
            'achievements': achievements,
            'progress': progress
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

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