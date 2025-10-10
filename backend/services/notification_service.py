# backend/services/notification_service.py

from datetime import datetime, timedelta
from config.database import get_db
from psycopg2.extras import RealDictCursor
from models.achievement import Achievement

class NotificationService:
    
    NOTIFICATION_TYPES = {
        'reminder': {
            'title_template': 'Time to make a difference! 🌱',
            'message_template': 'You haven\'t classified waste in {days} days. Help your colony reach collection goals!',
            'priority': 'medium'
        },
        'achievement': {
            'title_template': 'Achievement Unlocked! 🏆',
            'message_template': 'Congratulations! You earned "{achievement_name}" and {points} points!',
            'priority': 'high'
        },
        'colony_threshold': {
            'title_template': 'Colony Alert! 📦',
            'message_template': 'Your colony is {amount}kg away from {waste_type} collection threshold!',
            'priority': 'medium'
        },
        'collection_scheduled': {
            'title_template': 'Collection Scheduled! 🚛',
            'message_template': 'Waste collection scheduled for {date} at {time}. Get ready!',
            'priority': 'high'
        },
        'collection_completed': {
            'title_template': 'Collection Complete! ✅',
            'message_template': '{weight}kg of waste collected from your colony. Great job everyone!',
            'priority': 'medium'
        },
        'weekly_summary': {
            'title_template': 'Weekly Impact Report 📊',
            'message_template': 'This week you classified {items} items, saved {co2}kg CO2, and earned {points} points!',
            'priority': 'low'
        },
        'streak_milestone': {
            'title_template': 'Streak Milestone! 🔥',
            'message_template': 'Amazing! You\'ve classified waste for {days} consecutive days!',
            'priority': 'high'
        }
    }

    @staticmethod
    def create_notification(user_id, notification_type, **kwargs):
        """Create a new notification for a user"""
        if notification_type not in NotificationService.NOTIFICATION_TYPES:
            raise ValueError(f"Invalid notification type: {notification_type}")
        
        template = NotificationService.NOTIFICATION_TYPES[notification_type]
        
        try:
            title = template['title_template'].format(**kwargs)
            message = template['message_template'].format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for notification: {e}")
        
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, message, type, priority)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING notification_id
                """, (user_id, title, message, notification_type, template['priority']))
                
                notification_id = cursor.fetchone()['notification_id']
                db.commit()
                return notification_id

    @staticmethod
    def send_reminder_notifications():
        """Send reminder notifications to inactive users"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find users who haven't classified waste in 3+ days
                cursor.execute("""
                    SELECT DISTINCT u.user_id, u.username,
                           COALESCE(MAX(wl.created_at), u.created_at) as last_activity,
                           EXTRACT(DAYS FROM NOW() - COALESCE(MAX(wl.created_at), u.created_at)) as days_inactive
                    FROM users u
                    LEFT JOIN waste_logs wl ON u.user_id = wl.user_id
                    WHERE u.is_active = TRUE
                    GROUP BY u.user_id, u.username, u.created_at
                    HAVING EXTRACT(DAYS FROM NOW() - COALESCE(MAX(wl.created_at), u.created_at)) >= 3
                    AND NOT EXISTS (
                        SELECT 1 FROM notifications n 
                        WHERE n.user_id = u.user_id 
                        AND n.type = 'reminder' 
                        AND n.created_at >= NOW() - INTERVAL '24 hours'
                    )
                """)
                
                inactive_users = cursor.fetchall()
                
                notifications_sent = 0
                for user in inactive_users:
                    try:
                        NotificationService.create_notification(
                            user_id=user['user_id'],
                            notification_type='reminder',
                            days=int(user['days_inactive'])
                        )
                        notifications_sent += 1
                    except Exception as e:
                        print(f"Failed to send reminder to user {user['user_id']}: {e}")
                
                return notifications_sent

    @staticmethod
    def send_colony_threshold_notifications(colony_id):
        """Send notifications when colony is close to collection threshold"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get colony waste levels
                cursor.execute("""
                    SELECT colony_name, current_plastic_kg, current_paper_kg, 
                           current_metal_kg, current_glass_kg, current_textile_kg
                    FROM colonies WHERE colony_id = %s
                """, (colony_id,))
                
                colony = cursor.fetchone()
                if not colony:
                    return 0
                
                # Check thresholds
                thresholds = {
                    'plastic': 5,
                    'paper': 5,
                    'metal': 1,
                    'glass': 2,
                    'textile': 1
                }
                
                notifications_sent = 0
                
                for waste_type, threshold in thresholds.items():
                    current_amount = float(colony[f'current_{waste_type}_kg'])
                    remaining = threshold - current_amount
                    
                    # Notify when within 20% of threshold
                    if 0 < remaining <= threshold * 0.2:
                        # Get colony users
                        cursor.execute("""
                            SELECT user_id FROM users 
                            WHERE colony_id = %s AND is_active = TRUE
                        """, (colony_id,))
                        
                        users = cursor.fetchall()
                        
                        for user in users:
                            # Check if notification already sent recently
                            cursor.execute("""
                                SELECT 1 FROM notifications 
                                WHERE user_id = %s AND type = 'colony_threshold' 
                                AND message LIKE %s
                                AND created_at >= NOW() - INTERVAL '24 hours'
                            """, (user['user_id'], f'%{waste_type}%'))
                            
                            if not cursor.fetchone():
                                try:
                                    NotificationService.create_notification(
                                        user_id=user['user_id'],
                                        notification_type='colony_threshold',
                                        amount=round(remaining, 1),
                                        waste_type=waste_type
                                    )
                                    notifications_sent += 1
                                except Exception as e:
                                    print(f"Failed to send threshold notification: {e}")
                
                return notifications_sent

    @staticmethod
    def send_achievement_notification(user_id, achievement_data):
        """Send achievement notification"""
        try:
            return NotificationService.create_notification(
                user_id=user_id,
                notification_type='achievement',
                achievement_name=achievement_data['name'],
                points=achievement_data['points']
            )
        except Exception as e:
            print(f"Failed to send achievement notification: {e}")
            return None

    @staticmethod
    def send_collection_notifications(colony_id, notification_type, **kwargs):
        """Send collection-related notifications to colony users"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get colony users
                cursor.execute("""
                    SELECT user_id FROM users 
                    WHERE colony_id = %s AND is_active = TRUE
                """, (colony_id,))
                
                users = cursor.fetchall()
                notifications_sent = 0
                
                for user in users:
                    try:
                        NotificationService.create_notification(
                            user_id=user['user_id'],
                            notification_type=notification_type,
                            **kwargs
                        )
                        notifications_sent += 1
                    except Exception as e:
                        print(f"Failed to send collection notification: {e}")
                
                return notifications_sent

    @staticmethod
    def send_weekly_summary_notifications():
        """Send weekly summary notifications to active users"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get weekly stats for active users
                cursor.execute("""
                    SELECT u.user_id, u.username,
                           COUNT(wl.log_id) as items_classified,
                           COALESCE(SUM(wl.points_earned), 0) as points_earned,
                           COALESCE(SUM(wl.co2_saved), 0) as co2_saved
                    FROM users u
                    LEFT JOIN waste_logs wl ON u.user_id = wl.user_id 
                        AND wl.created_at >= NOW() - INTERVAL '7 days'
                    WHERE u.is_active = TRUE
                    AND EXISTS (
                        SELECT 1 FROM waste_logs wl2 
                        WHERE wl2.user_id = u.user_id 
                        AND wl2.created_at >= NOW() - INTERVAL '7 days'
                    )
                    GROUP BY u.user_id, u.username
                """)
                
                active_users = cursor.fetchall()
                notifications_sent = 0
                
                for user in active_users:
                    try:
                        NotificationService.create_notification(
                            user_id=user['user_id'],
                            notification_type='weekly_summary',
                            items=user['items_classified'],
                            points=int(user['points_earned']),
                            co2=round(float(user['co2_saved']), 1)
                        )
                        notifications_sent += 1
                    except Exception as e:
                        print(f"Failed to send weekly summary: {e}")
                
                return notifications_sent

    @staticmethod
    def get_user_notifications(user_id, limit=20, unread_only=False):
        """Get notifications for a user"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT notification_id, title, message, type, priority, 
                           is_read, created_at
                    FROM notifications
                    WHERE user_id = %s
                """
                params = [user_id]
                
                if unread_only:
                    query += " AND is_read = FALSE"
                
                query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                notifications = cursor.fetchall()
                
                # Format datetime for JSON
                for notification in notifications:
                    notification['created_at'] = notification['created_at'].isoformat()
                
                return notifications

    @staticmethod
    def mark_notification_read(notification_id, user_id):
        """Mark a notification as read"""
        with get_db() as db:
            with db.cursor() as cursor:
                cursor.execute("""
                    UPDATE notifications 
                    SET is_read = TRUE 
                    WHERE notification_id = %s AND user_id = %s
                """, (notification_id, user_id))
                db.commit()
                return cursor.rowcount > 0

    @staticmethod
    def get_notification_stats(user_id):
        """Get notification statistics for a user"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_notifications,
                        COUNT(CASE WHEN is_read = FALSE THEN 1 END) as unread_count,
                        COUNT(CASE WHEN type = 'achievement' THEN 1 END) as achievement_notifications,
                        COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_notifications
                    FROM notifications
                    WHERE user_id = %s
                """, (user_id,))
                
                return cursor.fetchone()