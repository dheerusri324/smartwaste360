# backend/services/realtime_service.py

import json
from datetime import datetime
from typing import Dict, List, Any
from config.database import get_db
from psycopg2.extras import RealDictCursor

class RealtimeService:
    """Service for real-time updates and live dashboard data"""
    
    # In a production environment, this would use Redis or similar
    # For now, we'll use in-memory storage
    _active_connections = {}
    _live_stats = {}
    
    @staticmethod
    def get_live_system_stats() -> Dict[str, Any]:
        """Get real-time system statistics"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get stats for the last 24 hours
                cursor.execute("""
                    SELECT 
                        COUNT(*) as classifications_today,
                        COALESCE(SUM(weight_kg), 0) as weight_today,
                        COALESCE(SUM(points_earned), 0) as points_today,
                        COALESCE(SUM(co2_saved), 0) as co2_today,
                        COUNT(DISTINCT user_id) as active_users_today
                    FROM waste_logs
                    WHERE created_at >= CURRENT_DATE
                """)
                today_stats = cursor.fetchone()
                
                # Get active collectors
                cursor.execute("""
                    SELECT COUNT(*) as active_collectors
                    FROM collectors
                    WHERE is_active = TRUE
                    AND collector_id IN (
                        SELECT DISTINCT collector_id 
                        FROM collection_bookings 
                        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                    )
                """)
                active_collectors = cursor.fetchone()
                
                # Get colonies ready for collection
                cursor.execute("""
                    SELECT COUNT(*) as colonies_ready
                    FROM colonies
                    WHERE current_dry_waste_kg >= 10
                    OR current_plastic_kg >= 5
                    OR current_paper_kg >= 5
                    OR current_metal_kg >= 1
                    OR current_glass_kg >= 2
                """)
                ready_colonies = cursor.fetchone()
                
                # Get recent activity (last 10 items)
                cursor.execute("""
                    SELECT u.username, wl.predicted_category, wl.weight_kg, 
                           wl.points_earned, wl.created_at, c.colony_name
                    FROM waste_logs wl
                    JOIN users u ON wl.user_id = u.user_id
                    JOIN colonies c ON u.colony_id = c.colony_id
                    ORDER BY wl.created_at DESC
                    LIMIT 10
                """)
                recent_activity = cursor.fetchall()
                
                # Format recent activity
                formatted_activity = []
                for activity in recent_activity:
                    formatted_activity.append({
                        'username': activity['username'],
                        'category': activity['predicted_category'],
                        'weight': float(activity['weight_kg']),
                        'points': activity['points_earned'],
                        'colony': activity['colony_name'],
                        'timestamp': activity['created_at'].isoformat(),
                        'time_ago': RealtimeService._get_time_ago(activity['created_at'])
                    })
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'today_stats': {
                        'classifications': today_stats['classifications_today'],
                        'weight_kg': float(today_stats['weight_today']),
                        'points': today_stats['points_today'],
                        'co2_saved': float(today_stats['co2_today']),
                        'active_users': today_stats['active_users_today']
                    },
                    'system_status': {
                        'active_collectors': active_collectors['active_collectors'],
                        'colonies_ready': ready_colonies['colonies_ready'],
                        'database_status': 'healthy',
                        'api_status': 'operational'
                    },
                    'recent_activity': formatted_activity
                }
    
    @staticmethod
    def get_live_colony_stats(colony_id: int) -> Dict[str, Any]:
        """Get real-time statistics for a specific colony"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get colony info and current waste levels
                cursor.execute("""
                    SELECT colony_name, total_points, total_users,
                           current_plastic_kg, current_paper_kg, current_metal_kg,
                           current_glass_kg, current_organic_kg, current_textile_kg,
                           current_dry_waste_kg
                    FROM colonies WHERE colony_id = %s
                """, (colony_id,))
                colony_info = cursor.fetchone()
                
                if not colony_info:
                    return {'error': 'Colony not found'}
                
                # Get today's activity for this colony
                cursor.execute("""
                    SELECT COUNT(*) as classifications_today,
                           COALESCE(SUM(wl.weight_kg), 0) as weight_today,
                           COALESCE(SUM(wl.points_earned), 0) as points_today,
                           COUNT(DISTINCT wl.user_id) as active_users_today
                    FROM waste_logs wl
                    JOIN users u ON wl.user_id = u.user_id
                    WHERE u.colony_id = %s AND wl.created_at >= CURRENT_DATE
                """, (colony_id,))
                today_activity = cursor.fetchone()
                
                # Get waste type breakdown for today
                cursor.execute("""
                    SELECT predicted_category, COUNT(*) as count, 
                           COALESCE(SUM(weight_kg), 0) as weight
                    FROM waste_logs wl
                    JOIN users u ON wl.user_id = u.user_id
                    WHERE u.colony_id = %s AND wl.created_at >= CURRENT_DATE
                    GROUP BY predicted_category
                    ORDER BY weight DESC
                """, (colony_id,))
                waste_breakdown = cursor.fetchall()
                
                # Check collection readiness
                thresholds = {
                    'plastic': 5, 'paper': 5, 'metal': 1, 'glass': 2, 'textile': 1
                }
                
                ready_for_collection = []
                for waste_type, threshold in thresholds.items():
                    current_amount = float(colony_info[f'current_{waste_type}_kg'])
                    if current_amount >= threshold:
                        ready_for_collection.append({
                            'waste_type': waste_type,
                            'current_amount': current_amount,
                            'threshold': threshold,
                            'percentage': min(100, (current_amount / threshold) * 100)
                        })
                
                return {
                    'colony_id': colony_id,
                    'colony_name': colony_info['colony_name'],
                    'timestamp': datetime.now().isoformat(),
                    'current_levels': {
                        'plastic': float(colony_info['current_plastic_kg']),
                        'paper': float(colony_info['current_paper_kg']),
                        'metal': float(colony_info['current_metal_kg']),
                        'glass': float(colony_info['current_glass_kg']),
                        'organic': float(colony_info['current_organic_kg']),
                        'textile': float(colony_info['current_textile_kg']),
                        'total_dry': float(colony_info['current_dry_waste_kg'])
                    },
                    'today_activity': {
                        'classifications': today_activity['classifications_today'],
                        'weight_kg': float(today_activity['weight_today']),
                        'points': today_activity['points_today'],
                        'active_users': today_activity['active_users_today']
                    },
                    'waste_breakdown': [
                        {
                            'category': item['predicted_category'],
                            'count': item['count'],
                            'weight': float(item['weight'])
                        } for item in waste_breakdown
                    ],
                    'collection_status': {
                        'ready_for_collection': len(ready_for_collection) > 0,
                        'ready_waste_types': ready_for_collection
                    }
                }
    
    @staticmethod
    def get_live_user_stats(user_id: int) -> Dict[str, Any]:
        """Get real-time statistics for a specific user"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get user info
                cursor.execute("""
                    SELECT u.username, u.full_name, u.total_points, 
                           u.total_weight_recycled, c.colony_name
                    FROM users u
                    LEFT JOIN colonies c ON u.colony_id = c.colony_id
                    WHERE u.user_id = %s
                """, (user_id,))
                user_info = cursor.fetchone()
                
                if not user_info:
                    return {'error': 'User not found'}
                
                # Get today's activity
                cursor.execute("""
                    SELECT COUNT(*) as classifications_today,
                           COALESCE(SUM(weight_kg), 0) as weight_today,
                           COALESCE(SUM(points_earned), 0) as points_today
                    FROM waste_logs
                    WHERE user_id = %s AND created_at >= CURRENT_DATE
                """, (user_id,))
                today_activity = cursor.fetchone()
                
                # Get recent achievements
                cursor.execute("""
                    SELECT achievement_id, points_awarded, earned_at
                    FROM user_achievements
                    WHERE user_id = %s
                    ORDER BY earned_at DESC
                    LIMIT 5
                """, (user_id,))
                recent_achievements = cursor.fetchall()
                
                # Get streak information
                cursor.execute("""
                    SELECT consecutive_days, last_classification_date
                    FROM user_statistics
                    WHERE user_id = %s
                """, (user_id,))
                streak_info = cursor.fetchone()
                
                return {
                    'user_id': user_id,
                    'username': user_info['username'],
                    'full_name': user_info['full_name'],
                    'colony_name': user_info['colony_name'],
                    'timestamp': datetime.now().isoformat(),
                    'total_stats': {
                        'total_points': user_info['total_points'],
                        'total_weight': float(user_info['total_weight_recycled'])
                    },
                    'today_activity': {
                        'classifications': today_activity['classifications_today'],
                        'weight_kg': float(today_activity['weight_today']),
                        'points': today_activity['points_today']
                    },
                    'streak': {
                        'consecutive_days': streak_info['consecutive_days'] if streak_info else 0,
                        'last_classification': streak_info['last_classification_date'].isoformat() if streak_info and streak_info['last_classification_date'] else None
                    },
                    'recent_achievements': [
                        {
                            'achievement_id': ach['achievement_id'],
                            'points': ach['points_awarded'],
                            'earned_at': ach['earned_at'].isoformat()
                        } for ach in recent_achievements
                    ]
                }
    
    @staticmethod
    def _get_time_ago(timestamp: datetime) -> str:
        """Get human-readable time ago string"""
        now = datetime.now()
        if timestamp.tzinfo:
            now = now.replace(tzinfo=timestamp.tzinfo)
        
        diff = now - timestamp
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
    
    @staticmethod
    def get_system_health_metrics() -> Dict[str, Any]:
        """Get detailed system health metrics"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Database performance metrics
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM waste_logs WHERE created_at >= NOW() - INTERVAL '1 hour') as classifications_last_hour,
                        (SELECT COUNT(*) FROM users WHERE last_login >= NOW() - INTERVAL '24 hours') as active_users_24h,
                        (SELECT COUNT(*) FROM collection_bookings WHERE status = 'scheduled') as pending_collections,
                        (SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) 
                         FROM collection_bookings 
                         WHERE status = 'completed' AND completed_at >= NOW() - INTERVAL '7 days') as avg_collection_time_hours
                """)
                metrics = cursor.fetchone()
                
                # Calculate system load indicators
                classifications_per_hour = metrics['classifications_last_hour']
                load_status = 'low' if classifications_per_hour < 10 else 'medium' if classifications_per_hour < 50 else 'high'
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'database': {
                        'status': 'healthy',
                        'response_time_ms': 50,  # This would be measured in real implementation
                        'active_connections': 10  # This would be actual connection count
                    },
                    'api': {
                        'status': 'operational',
                        'requests_per_hour': classifications_per_hour * 3,  # Estimate
                        'load_status': load_status
                    },
                    'ml_service': {
                        'status': 'active',
                        'classifications_last_hour': classifications_per_hour,
                        'average_confidence': 0.85  # This would be calculated from actual data
                    },
                    'collections': {
                        'pending_bookings': metrics['pending_collections'],
                        'average_completion_time_hours': round(float(metrics['avg_collection_time_hours'] or 0), 2)
                    },
                    'user_engagement': {
                        'active_users_24h': metrics['active_users_24h'],
                        'engagement_rate': 'high' if metrics['active_users_24h'] > 50 else 'medium' if metrics['active_users_24h'] > 20 else 'low'
                    }
                }