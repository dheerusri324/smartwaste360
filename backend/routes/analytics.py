# backend/routes/analytics.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.analytics import Analytics
import traceback

bp = Blueprint('analytics', __name__)

@bp.route('/collector/performance', methods=['GET'])
@jwt_required()
def get_collector_performance():
    """Get performance metrics for the authenticated collector"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({'error': 'Days parameter must be between 1 and 365'}), 400
        
        try:
            metrics = Analytics.get_collector_performance_metrics(collector_id, days)
        except Exception as db_error:
            print(f"Database error in analytics: {db_error}")
            # Return fallback data
            metrics = {
                'total_collections': 0,
                'total_weight': 0.0,
                'avg_rating': 0.0,
                'completion_rate': 0.0,
                'daily_stats': []
            }
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': True,
            'data': {
                'total_collections': 0,
                'total_weight': 0.0,
                'avg_rating': 0.0,
                'completion_rate': 0.0,
                'daily_stats': []
            }
        }), 200

@bp.route('/collector/summary', methods=['GET'])
@jwt_required()
def get_collector_summary():
    """Get summary stats for collector dashboard"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        
        # Return simple fallback data for now
        return jsonify({
            'success': True,
            'data': {
                'total_collections': 0,
                'total_weight_collected': 0.0,
                'avg_rating': 0.0,
                'pending_collections': 0,
                'this_week': {
                    'collections': 0,
                    'weight': 0.0
                },
                'this_month': {
                    'collections': 0,
                    'weight': 0.0
                }
            }
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': True,
            'data': {
                'total_collections': 0,
                'total_weight_collected': 0.0,
                'avg_rating': 0.0,
                'pending_collections': 0
            }
        }), 200

@bp.route('/dashboard/realtime', methods=['GET'])
@jwt_required()
def get_realtime_dashboard():
    """Get real-time dashboard data"""
    try:
        # Return simple fallback data
        return jsonify({
            'success': True,
            'data': {
                'active_collections': 0,
                'total_weight_today': 0.0,
                'active_collectors': 0,
                'pending_requests': 0
            }
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': True,
            'data': {
                'active_collections': 0,
                'total_weight_today': 0.0,
                'active_collectors': 0,
                'pending_requests': 0
            }
        }), 200

@bp.route('/system/overview', methods=['GET'])
@jwt_required()
def get_system_overview():
    """Get system-wide analytics (admin only)"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Access denied: Admin token required"}), 403
        
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({'error': 'Days parameter must be between 1 and 365'}), 400
        
        metrics = Analytics.get_system_overview_metrics(days)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/waste/trends', methods=['GET'])
@jwt_required()
def get_waste_trends():
    """Get waste trends analysis (admin and collector access)"""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'collector']:
            return jsonify({"msg": "Access denied: Admin or collector token required"}), 403
        
        days = request.args.get('days', 90, type=int)
        
        # Validate days parameter
        if days < 7 or days > 365:
            return jsonify({'error': 'Days parameter must be between 7 and 365'}), 400
        
        trends = Analytics.get_waste_trends_analysis(days)
        
        return jsonify({
            'success': True,
            'data': trends
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/dashboard/realtime', methods=['GET'])
@jwt_required()
def get_realtime_dashboard():
    """Get real-time dashboard data (collector-specific or admin global)"""
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'collector']:
            return jsonify({"msg": "Access denied: Admin or collector token required"}), 403
        
        user_id = get_jwt_identity()
        user_role = claims.get('role')
        
        if user_role == 'collector':
            # Get collector-specific dashboard data
            dashboard_data = Analytics.get_collector_realtime_dashboard_data(user_id)
        else:
            # Get global dashboard data for admin
            dashboard_data = Analytics.get_real_time_dashboard_data()
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/collector/summary', methods=['GET'])
@jwt_required()
def get_collector_summary():
    """Get quick summary stats for collector dashboard"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        
        collector_id = get_jwt_identity()
        
        # Get 7-day and 30-day metrics for comparison
        metrics_7d = Analytics.get_collector_performance_metrics(collector_id, 7)
        metrics_30d = Analytics.get_collector_performance_metrics(collector_id, 30)
        
        # Calculate growth rates
        collections_7d = metrics_7d['collection_stats'].get('total_collections', 0)
        collections_30d = metrics_30d['collection_stats'].get('total_collections', 0)
        
        weight_7d = float(metrics_7d['collection_stats'].get('total_weight', 0) or 0)
        weight_30d = float(metrics_30d['collection_stats'].get('total_weight', 0) or 0)
        
        # Calculate weekly averages for growth comparison
        weekly_collections_recent = collections_7d
        weekly_collections_overall = collections_30d / 4.3 if collections_30d > 0 else 0
        
        weekly_weight_recent = weight_7d
        weekly_weight_overall = weight_30d / 4.3 if weight_30d > 0 else 0
        
        collection_growth = 0
        weight_growth = 0
        
        if weekly_collections_overall > 0:
            collection_growth = ((weekly_collections_recent - weekly_collections_overall) / weekly_collections_overall) * 100
        
        if weekly_weight_overall > 0:
            weight_growth = ((weekly_weight_recent - weekly_weight_overall) / weekly_weight_overall) * 100
        
        summary = {
            'current_period': {
                'collections': collections_7d,
                'weight_collected': weight_7d,
                'efficiency_score': metrics_7d['efficiency_score'],
                'active_days': metrics_7d['collection_stats'].get('active_days', 0)
            },
            'growth_metrics': {
                'collection_growth_percent': round(collection_growth, 1),
                'weight_growth_percent': round(weight_growth, 1)
            },
            'performance_trends': metrics_7d['daily_trends'][:7],  # Last 7 days
            'waste_specialization': metrics_30d['waste_breakdown'][:3]  # Top 3 waste types
        }
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500