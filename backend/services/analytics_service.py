# backend/services/analytics_service.py

import numpy as np
from datetime import datetime, timedelta
from config.database import get_db
from psycopg2.extras import RealDictCursor

class AnalyticsService:
    
    @staticmethod
    def predict_waste_generation(colony_id, days_ahead=7):
        """Predict waste generation for a colony based on historical data"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get historical data for the last 30 days
                cursor.execute("""
                    SELECT DATE(wl.created_at) as date,
                           wl.predicted_category,
                           SUM(wl.weight_kg) as daily_weight,
                           COUNT(*) as daily_count
                    FROM waste_logs wl
                    JOIN users u ON wl.user_id = u.user_id
                    WHERE u.colony_id = %s 
                    AND wl.created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(wl.created_at), wl.predicted_category
                    ORDER BY date, wl.predicted_category
                """, (colony_id,))
                
                historical_data = cursor.fetchall()
                
                if not historical_data:
                    return None
                
                # Process data by waste type
                waste_types = ['plastic', 'paper', 'metal', 'glass', 'organic', 'textile']
                predictions = {}
                
                for waste_type in waste_types:
                    type_data = [row for row in historical_data if row['predicted_category'] == waste_type]
                    
                    if len(type_data) < 3:  # Need at least 3 data points
                        predictions[waste_type] = {
                            'daily_average': 0,
                            'predicted_total': 0,
                            'confidence': 'low'
                        }
                        continue
                    
                    # Calculate daily averages
                    daily_weights = [float(row['daily_weight']) for row in type_data]
                    daily_average = np.mean(daily_weights)
                    daily_std = np.std(daily_weights)
                    
                    # Simple linear trend analysis
                    dates = [row['date'] for row in type_data]
                    weights = [float(row['daily_weight']) for row in type_data]
                    
                    # Convert dates to numeric values for trend calculation
                    date_nums = [(date - dates[0]).days for date in dates]
                    
                    if len(date_nums) > 1:
                        # Calculate linear trend
                        trend_slope = np.polyfit(date_nums, weights, 1)[0]
                        
                        # Predict future values
                        future_prediction = daily_average + (trend_slope * days_ahead / 2)
                        predicted_total = max(0, future_prediction * days_ahead)
                    else:
                        predicted_total = daily_average * days_ahead
                    
                    # Determine confidence based on data consistency
                    coefficient_of_variation = daily_std / daily_average if daily_average > 0 else 1
                    if coefficient_of_variation < 0.3:
                        confidence = 'high'
                    elif coefficient_of_variation < 0.6:
                        confidence = 'medium'
                    else:
                        confidence = 'low'
                    
                    predictions[waste_type] = {
                        'daily_average': round(daily_average, 2),
                        'predicted_total': round(predicted_total, 2),
                        'confidence': confidence,
                        'trend': 'increasing' if trend_slope > 0.1 else 'decreasing' if trend_slope < -0.1 else 'stable'
                    }
                
                return predictions

    @staticmethod
    def get_optimal_collection_schedule(colony_id):
        """Determine optimal collection schedule based on waste generation patterns"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get current waste levels
                cursor.execute("""
                    SELECT current_plastic_kg, current_paper_kg, current_metal_kg,
                           current_glass_kg, current_organic_kg, current_textile_kg,
                           current_dry_waste_kg
                    FROM colonies WHERE colony_id = %s
                """, (colony_id,))
                
                current_levels = cursor.fetchone()
                if not current_levels:
                    return None
                
                # Get predictions
                predictions = AnalyticsService.predict_waste_generation(colony_id, 14)
                if not predictions:
                    return None
                
                # Calculate days until threshold for each waste type
                thresholds = {
                    'plastic': 5,
                    'paper': 5,
                    'metal': 1,
                    'glass': 2,
                    'textile': 1
                }
                
                recommendations = []
                
                for waste_type, threshold in thresholds.items():
                    current_amount = float(current_levels.get(f'current_{waste_type}_kg', 0))
                    daily_generation = predictions[waste_type]['daily_average']
                    
                    if daily_generation > 0:
                        days_to_threshold = max(0, (threshold - current_amount) / daily_generation)
                        
                        if days_to_threshold <= 7:  # Collection needed within a week
                            recommendations.append({
                                'waste_type': waste_type,
                                'current_amount': current_amount,
                                'threshold': threshold,
                                'days_to_threshold': round(days_to_threshold, 1),
                                'priority': 'high' if days_to_threshold <= 3 else 'medium',
                                'recommended_date': (datetime.now() + timedelta(days=int(days_to_threshold))).strftime('%Y-%m-%d')
                            })
                
                return {
                    'colony_id': colony_id,
                    'analysis_date': datetime.now().isoformat(),
                    'recommendations': recommendations,
                    'predictions': predictions
                }

    @staticmethod
    def get_user_engagement_insights(date_range_days=30):
        """Analyze user engagement patterns"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # User activity patterns
                cursor.execute("""
                    SELECT 
                        EXTRACT(HOUR FROM created_at) as hour_of_day,
                        EXTRACT(DOW FROM created_at) as day_of_week,
                        COUNT(*) as activity_count,
                        AVG(weight_kg) as avg_weight
                    FROM waste_logs
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY EXTRACT(HOUR FROM created_at), EXTRACT(DOW FROM created_at)
                    ORDER BY hour_of_day, day_of_week
                """, (date_range_days,))
                
                activity_patterns = cursor.fetchall()
                
                # User retention analysis
                cursor.execute("""
                    WITH user_activity AS (
                        SELECT user_id, 
                               DATE(created_at) as activity_date,
                               COUNT(*) as daily_classifications
                        FROM waste_logs
                        WHERE created_at >= NOW() - INTERVAL '%s days'
                        GROUP BY user_id, DATE(created_at)
                    ),
                    user_streaks AS (
                        SELECT user_id,
                               COUNT(DISTINCT activity_date) as active_days,
                               MAX(daily_classifications) as max_daily_activity,
                               AVG(daily_classifications) as avg_daily_activity
                        FROM user_activity
                        GROUP BY user_id
                    )
                    SELECT 
                        COUNT(*) as total_active_users,
                        AVG(active_days) as avg_active_days,
                        AVG(avg_daily_activity) as avg_classifications_per_day,
                        COUNT(CASE WHEN active_days >= 7 THEN 1 END) as weekly_active_users,
                        COUNT(CASE WHEN active_days >= 30 THEN 1 END) as monthly_active_users
                    FROM user_streaks
                """, (date_range_days,))
                
                engagement_metrics = cursor.fetchone()
                
                # Peak activity times
                peak_hours = {}
                peak_days = {}
                
                for pattern in activity_patterns:
                    hour = int(pattern['hour_of_day'])
                    day = int(pattern['day_of_week'])
                    count = pattern['activity_count']
                    
                    if hour not in peak_hours:
                        peak_hours[hour] = 0
                    peak_hours[hour] += count
                    
                    if day not in peak_days:
                        peak_days[day] = 0
                    peak_days[day] += count
                
                # Find peak times
                peak_hour = max(peak_hours.items(), key=lambda x: x[1])[0] if peak_hours else 12
                peak_day = max(peak_days.items(), key=lambda x: x[1])[0] if peak_days else 1
                
                day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                
                return {
                    'engagement_metrics': engagement_metrics,
                    'peak_activity_hour': peak_hour,
                    'peak_activity_day': day_names[peak_day],
                    'activity_patterns': activity_patterns,
                    'insights': {
                        'best_notification_time': f"{peak_hour}:00",
                        'most_active_day': day_names[peak_day],
                        'user_retention_rate': round((engagement_metrics['weekly_active_users'] / engagement_metrics['total_active_users']) * 100, 1) if engagement_metrics['total_active_users'] > 0 else 0
                    }
                }

    @staticmethod
    def get_environmental_impact_forecast(colony_id=None, days_ahead=30):
        """Forecast environmental impact based on current trends"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Base query for environmental impact
                base_query = """
                    SELECT 
                        predicted_category,
                        SUM(weight_kg) as total_weight,
                        SUM(co2_saved) as total_co2_saved,
                        COUNT(*) as total_items
                    FROM waste_logs wl
                """
                
                params = []
                if colony_id:
                    base_query += " JOIN users u ON wl.user_id = u.user_id WHERE u.colony_id = %s AND"
                    params.append(colony_id)
                else:
                    base_query += " WHERE"
                
                base_query += " wl.created_at >= NOW() - INTERVAL '30 days' GROUP BY predicted_category"
                
                cursor.execute(base_query, params)
                current_impact = cursor.fetchall()
                
                # Calculate daily averages and project forward
                total_daily_weight = sum(float(row['total_weight']) for row in current_impact) / 30
                total_daily_co2 = sum(float(row['total_co2_saved']) for row in current_impact) / 30
                
                # Project forward
                projected_weight = total_daily_weight * days_ahead
                projected_co2 = total_daily_co2 * days_ahead
                
                # Calculate equivalent impacts
                trees_saved = projected_co2 / 22  # 1 tree absorbs ~22kg CO2 per year
                energy_saved = projected_weight * 2.5  # Rough estimate: 2.5 kWh per kg recycled
                water_saved = projected_weight * 15  # Rough estimate: 15 liters per kg recycled
                
                return {
                    'forecast_period_days': days_ahead,
                    'projected_waste_kg': round(projected_weight, 2),
                    'projected_co2_saved_kg': round(projected_co2, 2),
                    'equivalent_impacts': {
                        'trees_equivalent': round(trees_saved, 1),
                        'energy_saved_kwh': round(energy_saved, 1),
                        'water_saved_liters': round(water_saved, 1)
                    },
                    'current_trends': current_impact
                }