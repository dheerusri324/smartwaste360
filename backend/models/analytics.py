# backend/models/analytics.py

from config.database import get_db
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json

class Analytics:
    @staticmethod
    def get_collector_performance_metrics(collector_id, days=30):
        """Get comprehensive performance metrics for a collector"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Collection statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_collections,
                        SUM(total_weight_collected) as total_weight,
                        AVG(total_weight_collected) as avg_weight_per_collection,
                        COUNT(DISTINCT DATE(completed_at)) as active_days
                    FROM collection_bookings 
                    WHERE collector_id = %s 
                      AND status = 'completed' 
                      AND completed_at >= %s
                """, (collector_id, start_date))
                
                collection_stats = cursor.fetchone()
                
                # Route efficiency metrics
                cursor.execute("""
                    SELECT 
                        AVG(distance_from_previous_km) as avg_distance_per_pickup,
                        COUNT(DISTINCT batch_id) as total_routes,
                        AVG(estimated_duration_minutes) as avg_duration_per_pickup
                    FROM collection_bookings 
                    WHERE collector_id = %s 
                      AND status = 'completed' 
                      AND completed_at >= %s
                      AND batch_id IS NOT NULL
                """, (collector_id, start_date))
                
                route_stats = cursor.fetchone()
                
                # Daily performance trend
                cursor.execute("""
                    SELECT 
                        DATE(completed_at) as collection_date,
                        COUNT(*) as collections_count,
                        SUM(total_weight_collected) as daily_weight,
                        COUNT(DISTINCT batch_id) as routes_completed
                    FROM collection_bookings 
                    WHERE collector_id = %s 
                      AND status = 'completed' 
                      AND completed_at >= %s
                    GROUP BY DATE(completed_at)
                    ORDER BY collection_date DESC
                    LIMIT 30
                """, (collector_id, start_date))
                
                daily_trends = cursor.fetchall()
                
                # Waste type breakdown
                cursor.execute("""
                    SELECT 
                        waste_type,
                        COUNT(*) as collection_count,
                        SUM(total_weight_collected) as total_weight
                    FROM collection_bookings cb
                    CROSS JOIN LATERAL unnest(cb.waste_types) as waste_type
                    WHERE cb.collector_id = %s 
                      AND cb.status = 'completed' 
                      AND cb.completed_at >= %s
                    GROUP BY waste_type
                    ORDER BY total_weight DESC
                """, (collector_id, start_date))
                
                waste_breakdown = cursor.fetchall()
                
                # Calculate efficiency scores
                efficiency_score = 0
                if collection_stats and collection_stats['total_collections'] > 0:
                    collections_per_day = collection_stats['total_collections'] / max(collection_stats['active_days'], 1)
                    weight_efficiency = float(collection_stats['avg_weight_per_collection'] or 0)
                    efficiency_score = min(100, (collections_per_day * 10) + (weight_efficiency * 2))
                
                return {
                    'period_days': days,
                    'collection_stats': dict(collection_stats) if collection_stats else {},
                    'route_stats': dict(route_stats) if route_stats else {},
                    'daily_trends': [dict(trend) for trend in daily_trends],
                    'waste_breakdown': [dict(waste) for waste in waste_breakdown],
                    'efficiency_score': round(efficiency_score, 1),
                    'generated_at': datetime.now().isoformat()
                }

    @staticmethod
    def get_system_overview_metrics(days=30):
        """Get system-wide analytics for administrators"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Overall system stats
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT u.user_id) as total_users,
                        COUNT(DISTINCT c.collector_id) as total_collectors,
                        COUNT(DISTINCT col.colony_id) as total_colonies,
                        COUNT(DISTINCT cp.point_id) as total_collection_points
                    FROM users u
                    CROSS JOIN collectors c
                    CROSS JOIN colonies col
                    CROSS JOIN collection_points cp
                    WHERE u.is_active = true 
                      AND c.is_active = true 
                      AND cp.is_active = true
                """)
                
                system_stats = cursor.fetchone()
                
                # Collection performance
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_collections,
                        SUM(total_weight_collected) as total_weight_collected,
                        COUNT(DISTINCT collector_id) as active_collectors,
                        AVG(total_weight_collected) as avg_collection_weight
                    FROM collection_bookings 
                    WHERE status = 'completed' 
                      AND completed_at >= %s
                """, (start_date,))
                
                collection_performance = cursor.fetchone()
                
                # Environmental impact
                cursor.execute("""
                    SELECT 
                        SUM(total_weight_collected) as total_waste_diverted,
                        COUNT(DISTINCT cb.colony_id) as colonies_served,
                        SUM(total_weight_collected) * 0.5 as estimated_co2_saved_kg
                    FROM collection_bookings cb
                    WHERE cb.status = 'completed' 
                      AND cb.completed_at >= %s
                """, (start_date,))
                
                environmental_impact = cursor.fetchone()
                
                # Top performing collectors
                cursor.execute("""
                    SELECT 
                        c.name,
                        c.collector_id,
                        COUNT(cb.booking_id) as collections,
                        SUM(cb.total_weight_collected) as total_weight,
                        AVG(cb.total_weight_collected) as avg_weight
                    FROM collectors c
                    JOIN collection_bookings cb ON c.collector_id = cb.collector_id
                    WHERE cb.status = 'completed' 
                      AND cb.completed_at >= %s
                    GROUP BY c.collector_id, c.name
                    ORDER BY total_weight DESC
                    LIMIT 10
                """, (start_date,))
                
                top_collectors = cursor.fetchall()
                
                # Colony activity
                cursor.execute("""
                    SELECT 
                        col.colony_name,
                        col.colony_id,
                        COUNT(cb.booking_id) as collections,
                        SUM(cb.total_weight_collected) as total_weight,
                        col.total_users
                    FROM colonies col
                    LEFT JOIN collection_bookings cb ON col.colony_id = cb.colony_id 
                        AND cb.status = 'completed' 
                        AND cb.completed_at >= %s
                    GROUP BY col.colony_id, col.colony_name, col.total_users
                    ORDER BY total_weight DESC NULLS LAST
                    LIMIT 10
                """, (start_date,))
                
                colony_activity = cursor.fetchall()
                
                return {
                    'period_days': days,
                    'system_stats': dict(system_stats) if system_stats else {},
                    'collection_performance': dict(collection_performance) if collection_performance else {},
                    'environmental_impact': dict(environmental_impact) if environmental_impact else {},
                    'top_collectors': [dict(collector) for collector in top_collectors],
                    'colony_activity': [dict(colony) for colony in colony_activity],
                    'generated_at': datetime.now().isoformat()
                }

    @staticmethod
    def get_waste_trends_analysis(days=90):
        """Analyze waste generation and collection trends"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Weekly waste trends
                cursor.execute("""
                    SELECT 
                        DATE_TRUNC('week', completed_at) as week_start,
                        COUNT(*) as collections,
                        SUM(total_weight_collected) as total_weight,
                        AVG(total_weight_collected) as avg_weight
                    FROM collection_bookings 
                    WHERE status = 'completed' 
                      AND completed_at >= %s
                    GROUP BY DATE_TRUNC('week', completed_at)
                    ORDER BY week_start DESC
                """, (start_date,))
                
                weekly_trends = cursor.fetchall()
                
                # Waste type trends
                cursor.execute("""
                    SELECT 
                        waste_type,
                        DATE_TRUNC('week', cb.completed_at) as week_start,
                        COUNT(*) as collections,
                        SUM(cb.total_weight_collected) as total_weight
                    FROM collection_bookings cb
                    CROSS JOIN LATERAL unnest(cb.waste_types) as waste_type
                    WHERE cb.status = 'completed' 
                      AND cb.completed_at >= %s
                    GROUP BY waste_type, DATE_TRUNC('week', cb.completed_at)
                    ORDER BY week_start DESC, total_weight DESC
                """, (start_date,))
                
                waste_type_trends = cursor.fetchall()
                
                # Colony waste generation patterns
                cursor.execute("""
                    SELECT 
                        col.colony_name,
                        col.total_users,
                        SUM(cb.total_weight_collected) as total_collected,
                        SUM(cb.total_weight_collected) / NULLIF(col.total_users, 0) as waste_per_user,
                        COUNT(cb.booking_id) as collection_frequency
                    FROM colonies col
                    LEFT JOIN collection_bookings cb ON col.colony_id = cb.colony_id 
                        AND cb.status = 'completed' 
                        AND cb.completed_at >= %s
                    WHERE col.total_users > 0
                    GROUP BY col.colony_id, col.colony_name, col.total_users
                    HAVING SUM(cb.total_weight_collected) > 0
                    ORDER BY waste_per_user DESC NULLS LAST
                    LIMIT 20
                """, (start_date,))
                
                colony_patterns = cursor.fetchall()
                
                return {
                    'period_days': days,
                    'weekly_trends': [dict(trend) for trend in weekly_trends],
                    'waste_type_trends': [dict(trend) for trend in waste_type_trends],
                    'colony_patterns': [dict(pattern) for pattern in colony_patterns],
                    'generated_at': datetime.now().isoformat()
                }

    @staticmethod
    def get_real_time_dashboard_data():
        """Get real-time dashboard data for live monitoring"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Today's activity
                today = datetime.now().date()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as todays_collections,
                        SUM(total_weight_collected) as todays_weight,
                        COUNT(DISTINCT collector_id) as active_collectors_today
                    FROM collection_bookings 
                    WHERE status = 'completed' 
                      AND DATE(completed_at) = %s
                """, (today,))
                
                today_stats = cursor.fetchone()
                
                # Current system status
                cursor.execute("""
                    SELECT 
                        COUNT(*) as pending_collections,
                        COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_collections,
                        COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_collections
                    FROM collection_bookings 
                    WHERE status IN ('scheduled', 'in_progress')
                """)
                
                current_status = cursor.fetchone()
                
                # Ready colonies count
                cursor.execute("""
                    SELECT COUNT(*) as ready_colonies
                    FROM colonies 
                    WHERE current_plastic_kg >= 5 
                       OR current_paper_kg >= 5 
                       OR current_metal_kg >= 1 
                       OR current_glass_kg >= 2 
                       OR current_textile_kg >= 1 
                       OR current_organic_kg >= 10
                """)
                
                ready_colonies = cursor.fetchone()
                
                # Recent activity feed
                cursor.execute("""
                    SELECT 
                        cb.booking_id,
                        cb.completed_at,
                        cb.total_weight_collected,
                        cb.waste_types,
                        c.name as collector_name,
                        col.colony_name
                    FROM collection_bookings cb
                    JOIN collectors c ON cb.collector_id = c.collector_id
                    JOIN colonies col ON cb.colony_id = col.colony_id
                    WHERE cb.status = 'completed'
                    ORDER BY cb.completed_at DESC
                    LIMIT 10
                """)
                
                recent_activity = cursor.fetchall()
                
                return {
                    'today_stats': dict(today_stats) if today_stats else {},
                    'current_status': dict(current_status) if current_status else {},
                    'ready_colonies_count': ready_colonies['ready_colonies'] if ready_colonies else 0,
                    'recent_activity': [dict(activity) for activity in recent_activity],
                    'timestamp': datetime.now().isoformat()
                }