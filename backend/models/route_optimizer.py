# backend/models/route_optimizer.py

from config.database import get_db
from psycopg2.extras import RealDictCursor
import math
from datetime import datetime, timedelta

class RouteOptimizer:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r

    @staticmethod
    def get_optimized_route_suggestions(collector_id, max_pickups=5, max_radius=25):
        """Get optimized pickup suggestions for a collector based on their location"""
        try:
            with get_db() as db:
                if not db: 
                    raise ConnectionError("Database connection not available.")
                with db.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get collector's location and preferences
                    cursor.execute("""
                        SELECT latitude, longitude, service_radius_km, waste_types_collected
                        FROM collectors 
                        WHERE collector_id = %s
                    """, (collector_id,))
                    
                    collector = cursor.fetchone()
                    
                    if not collector or not collector['latitude']:
                        return []
                    
                    collector_lat = float(collector['latitude'])
                    collector_lon = float(collector['longitude'])
                    service_radius = float(collector['service_radius_km'] or 50)
                    waste_types = collector['waste_types_collected'] or []
                    
                    # Get ready colonies within service radius
                    cursor.execute("""
                        SELECT c.*, 
                               c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                               c.current_glass_kg, c.current_textile_kg, c.current_organic_kg,
                               CASE 
                                   WHEN c.current_plastic_kg >= 5 THEN 'plastic'
                                   WHEN c.current_paper_kg >= 5 THEN 'paper'
                                   WHEN c.current_metal_kg >= 1 THEN 'metal'
                                   WHEN c.current_glass_kg >= 2 THEN 'glass'
                                   WHEN c.current_textile_kg >= 1 THEN 'textile'
                                   WHEN c.current_organic_kg >= 10 THEN 'organic'
                                   ELSE NULL
                               END as ready_waste_type,
                               GREATEST(c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                                       c.current_glass_kg, c.current_textile_kg, c.current_organic_kg) as max_waste_kg,
                               (6371 * acos(
                                   LEAST(1.0,
                                       cos(radians(%s)) * cos(radians(CAST(c.latitude AS FLOAT))) * 
                                       cos(radians(CAST(c.longitude AS FLOAT)) - radians(%s)) + 
                                       sin(radians(%s)) * sin(radians(CAST(c.latitude AS FLOAT)))
                                   )
                               )) AS distance_from_collector
                        FROM colonies c
                        WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
                          AND (c.current_plastic_kg >= 5 OR c.current_paper_kg >= 5 OR c.current_metal_kg >= 1 
                               OR c.current_glass_kg >= 2 OR c.current_textile_kg >= 1 OR c.current_organic_kg >= 10)
                        HAVING distance_from_collector <= %s
                        ORDER BY distance_from_collector, max_waste_kg DESC
                    """, (collector_lat, collector_lon, collector_lat, service_radius))
                    
                    ready_colonies = cursor.fetchall()
                    
                    if not ready_colonies:
                        return []
                    
                    # Filter by waste types if collector has preferences
                    if waste_types:
                        filtered_colonies = []
                        for colony in ready_colonies:
                            colony_waste_types = []
                            if colony['current_plastic_kg'] >= 5:
                                colony_waste_types.append('plastic')
                            if colony['current_paper_kg'] >= 5:
                                colony_waste_types.append('paper')
                            if colony['current_metal_kg'] >= 1:
                                colony_waste_types.append('metal')
                            if colony['current_glass_kg'] >= 2:
                                colony_waste_types.append('glass')
                            if colony['current_textile_kg'] >= 1:
                                colony_waste_types.append('textile')
                            if colony['current_organic_kg'] >= 10:
                                colony_waste_types.append('organic')
                            
                            # Check if collector can handle any of the colony's waste types
                            if any(wt in waste_types for wt in colony_waste_types):
                                filtered_colonies.append(colony)
                        
                        ready_colonies = filtered_colonies
                    
                    # Generate route suggestions using nearest neighbor algorithm
                    route_suggestions = RouteOptimizer._generate_route_clusters(
                        ready_colonies, collector_lat, collector_lon, max_pickups, max_radius
                    )
                    
                    return route_suggestions
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

    @staticmethod
    def _generate_route_clusters(colonies, start_lat, start_lon, max_pickups, max_radius):
        """Generate optimized route clusters using nearest neighbor approach"""
        if not colonies:
            return []
        
        try:
            routes = []
            remaining_colonies = list(colonies)
            
            # Generate up to 3 route options
            for route_num in range(min(3, len(remaining_colonies))):
                current_route = []
                current_lat, current_lon = start_lat, start_lon
                total_distance = 0
                route_colonies = remaining_colonies.copy()
                
                # Build route using nearest neighbor
                for pickup_num in range(min(max_pickups, len(route_colonies))):
                    nearest_colony = None
                    nearest_distance = float('inf')
                    nearest_index = -1
                    
                    for i, colony in enumerate(route_colonies):
                        try:
                            if colony.get('latitude') and colony.get('longitude'):
                                distance = RouteOptimizer.calculate_distance(
                                    current_lat, current_lon,
                                    float(colony['latitude']), float(colony['longitude'])
                                )
                                
                                if distance < nearest_distance:
                                    nearest_distance = distance
                                    nearest_colony = colony
                                    nearest_index = i
                        except (ValueError, TypeError):
                            continue
                    
                    if nearest_colony is None or nearest_distance > max_radius:
                        break
                    
                    # Add to route
                    pickup_data = dict(nearest_colony)
                    pickup_data.update({
                        'distance_from_previous': nearest_distance,
                        'order_in_route': len(current_route) + 1
                    })
                    current_route.append(pickup_data)
                    
                    total_distance += nearest_distance
                    current_lat = float(nearest_colony['latitude'])
                    current_lon = float(nearest_colony['longitude'])
                    
                    # Remove from available colonies for this route
                    route_colonies.pop(nearest_index)
                
                if current_route:
                    # Calculate return distance to start
                    return_distance = RouteOptimizer.calculate_distance(
                        current_lat, current_lon, start_lat, start_lon
                    )
                    
                    # Calculate total estimated weight
                    total_weight = 0
                    for pickup in current_route:
                        try:
                            weight = float(pickup.get('max_waste_kg', 0))
                            total_weight += weight
                        except (ValueError, TypeError):
                            continue
                    
                    route_data = {
                        'route_id': len(routes) + 1,
                        'pickups': current_route,
                        'total_distance': round(total_distance + return_distance, 2),
                        'estimated_time_hours': round((total_distance + return_distance) / 30 + len(current_route) * 0.5, 1),
                        'total_colonies': len(current_route),
                        'total_estimated_weight': round(total_weight, 2)
                    }
                    
                    # Calculate efficiency score
                    if route_data['total_distance'] > 0:
                        route_data['efficiency_score'] = round(route_data['total_estimated_weight'] / route_data['total_distance'], 2)
                    else:
                        route_data['efficiency_score'] = route_data['total_estimated_weight']
                    
                    routes.append(route_data)
                    
                    # Remove first colony from remaining for next route
                    if remaining_colonies:
                        remaining_colonies.pop(0)
            
            # Sort routes by efficiency score
            routes.sort(key=lambda x: x['efficiency_score'], reverse=True)
            
            return routes
            
        except Exception as e:
            print(f"Error in route clustering: {e}")
            return []

    @staticmethod
    def get_available_time_slots(date, collector_id=None):
        """Get available time slots for a given date"""
        time_slots = [
            {'slot': 'morning', 'time': '09:00-12:00', 'label': 'Morning (9 AM - 12 PM)'},
            {'slot': 'afternoon', 'time': '14:00-17:00', 'label': 'Afternoon (2 PM - 5 PM)'},
            {'slot': 'evening', 'time': '17:00-19:00', 'label': 'Evening (5 PM - 7 PM)'}
        ]
        
        if not collector_id:
            return time_slots
        
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check which slots are already booked
                cursor.execute("""
                    SELECT time_slot, COUNT(*) as booking_count
                    FROM collection_bookings 
                    WHERE collector_id = %s AND booking_date = %s AND status IN ('scheduled', 'in_progress')
                    GROUP BY time_slot
                """, (collector_id, date))
                
                booked_slots = {row['time_slot']: row['booking_count'] for row in cursor.fetchall()}
                
                # Mark availability (assuming max 3 bookings per slot)
                for slot in time_slots:
                    slot['available'] = booked_slots.get(slot['slot'], 0) < 3
                    slot['current_bookings'] = booked_slots.get(slot['slot'], 0)
                
                return time_slots

    @staticmethod
    def schedule_route_batch(collector_id, route_pickups, booking_date, time_slot):
        """Schedule multiple pickups as a batch route"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                booking_ids = []
                
                try:
                    for i, pickup in enumerate(route_pickups):
                        cursor.execute("""
                            INSERT INTO collection_bookings 
                            (colony_id, collector_id, booking_date, time_slot, route_order, batch_id)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING booking_id
                        """, (
                            pickup['colony_id'], 
                            collector_id, 
                            booking_date, 
                            time_slot,
                            pickup.get('order_in_route', i + 1),
                            f"batch_{collector_id}_{booking_date}_{time_slot}"
                        ))
                        
                        result = cursor.fetchone()
                        booking_ids.append(result['booking_id'])
                    
                    db.commit()
                    return booking_ids
                    
                except Exception as e:
                    db.rollback()
                    raise e