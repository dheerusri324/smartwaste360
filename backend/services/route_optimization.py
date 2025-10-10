# backend/services/route_optimization.py

import math
import itertools
from typing import List, Dict, Tuple
from config.database import get_db
from psycopg2.extras import RealDictCursor

class RouteOptimizer:
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    @staticmethod
    def create_distance_matrix(locations: List[Dict]) -> List[List[float]]:
        """Create distance matrix for all locations"""
        n = len(locations)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = RouteOptimizer.calculate_distance(
                        locations[i]['latitude'],
                        locations[i]['longitude'],
                        locations[j]['latitude'],
                        locations[j]['longitude']
                    )
        
        return matrix

    @staticmethod
    def solve_tsp_nearest_neighbor(distance_matrix: List[List[float]], start_index: int = 0) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor heuristic"""
        n = len(distance_matrix)
        if n <= 1:
            return [0], 0.0
        
        unvisited = set(range(n))
        current = start_index
        route = [current]
        unvisited.remove(current)
        total_distance = 0.0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            total_distance += distance_matrix[current][nearest]
            current = nearest
            route.append(current)
            unvisited.remove(current)
        
        # Return to start
        total_distance += distance_matrix[current][start_index]
        route.append(start_index)
        
        return route, total_distance

    @staticmethod
    def solve_tsp_2opt(distance_matrix: List[List[float]], initial_route: List[int]) -> Tuple[List[int], float]:
        """Improve TSP solution using 2-opt optimization"""
        def calculate_route_distance(route):
            distance = 0
            for i in range(len(route) - 1):
                distance += distance_matrix[route[i]][route[i + 1]]
            return distance
        
        def two_opt_swap(route, i, k):
            new_route = route[:i] + route[i:k+1][::-1] + route[k+1:]
            return new_route
        
        best_route = initial_route[:]
        best_distance = calculate_route_distance(best_route)
        improved = True
        
        while improved:
            improved = False
            for i in range(1, len(best_route) - 2):
                for k in range(i + 1, len(best_route) - 1):
                    new_route = two_opt_swap(best_route, i, k)
                    new_distance = calculate_route_distance(new_route)
                    
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
        
        return best_route, best_distance

    @staticmethod
    def optimize_collection_route(collector_id: str, collection_points: List[Dict], 
                                collector_location: Dict = None) -> Dict:
        """Optimize collection route for a collector"""
        
        if len(collection_points) <= 1:
            return {
                'optimized_route': collection_points,
                'total_distance_km': 0,
                'estimated_time_hours': 0,
                'fuel_cost_estimate': 0,
                'optimization_savings': 0
            }
        
        # Add collector's starting location if provided
        locations = []
        if collector_location:
            locations.append({
                'id': 'start',
                'name': 'Starting Location',
                'latitude': collector_location['latitude'],
                'longitude': collector_location['longitude'],
                'type': 'start'
            })
        
        # Add collection points
        for point in collection_points:
            locations.append({
                'id': point.get('point_id', point.get('colony_id')),
                'name': point.get('point_name', point.get('colony_name')),
                'latitude': float(point['latitude']),
                'longitude': float(point['longitude']),
                'type': 'collection_point',
                'waste_amount': point.get('max_waste_kg', 0),
                'priority': point.get('priority', 'medium')
            })
        
        # Create distance matrix
        distance_matrix = RouteOptimizer.create_distance_matrix(locations)
        
        # Solve TSP
        start_index = 0 if collector_location else 0
        initial_route, initial_distance = RouteOptimizer.solve_tsp_nearest_neighbor(distance_matrix, start_index)
        optimized_route, optimized_distance = RouteOptimizer.solve_tsp_2opt(distance_matrix, initial_route)
        
        # Create optimized route with location details
        route_details = []
        for i, location_index in enumerate(optimized_route[:-1]):  # Exclude the return to start
            location = locations[location_index]
            route_details.append({
                'order': i + 1,
                'location_id': location['id'],
                'name': location['name'],
                'latitude': location['latitude'],
                'longitude': location['longitude'],
                'type': location['type'],
                'estimated_arrival_time': i * 0.5,  # Assume 30 minutes per stop
                'distance_from_previous': distance_matrix[optimized_route[i-1]][location_index] if i > 0 else 0
            })
        
        # Calculate estimates
        estimated_time_hours = len(collection_points) * 0.5 + optimized_distance / 30  # 30 km/h average speed
        fuel_cost_estimate = optimized_distance * 0.15  # Assume $0.15 per km
        
        # Calculate savings compared to unoptimized route
        unoptimized_distance = sum(distance_matrix[i][i+1] for i in range(len(locations)-1))
        optimization_savings = max(0, unoptimized_distance - optimized_distance)
        
        return {
            'optimized_route': route_details,
            'total_distance_km': round(optimized_distance, 2),
            'estimated_time_hours': round(estimated_time_hours, 2),
            'fuel_cost_estimate': round(fuel_cost_estimate, 2),
            'optimization_savings_km': round(optimization_savings, 2),
            'optimization_savings_percent': round((optimization_savings / unoptimized_distance * 100), 1) if unoptimized_distance > 0 else 0
        }

    @staticmethod
    def get_optimal_collection_schedule(collector_id: str, days_ahead: int = 7) -> Dict:
        """Get optimal collection schedule for multiple days"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get collector's waste type preferences
                cursor.execute("""
                    SELECT waste_types_collected, name, phone
                    FROM collectors WHERE collector_id = %s
                """, (collector_id,))
                
                collector = cursor.fetchone()
                if not collector:
                    return {'error': 'Collector not found'}
                
                # Get colonies ready for collection based on collector's preferences
                from models.colony import Colony
                ready_colonies = Colony.get_colonies_ready_for_collection_by_type(
                    collector['waste_types_collected'], collector_id
                )
                
                if not ready_colonies:
                    return {
                        'collector_id': collector_id,
                        'schedule': [],
                        'message': 'No colonies ready for collection'
                    }
                
                # Group colonies by priority and location
                high_priority = []
                medium_priority = []
                low_priority = []
                
                for colony in ready_colonies:
                    if colony.get('max_waste_kg', 0) >= 50:
                        high_priority.append(colony)
                    elif colony.get('max_waste_kg', 0) >= 20:
                        medium_priority.append(colony)
                    else:
                        low_priority.append(colony)
                
                # Create daily schedules
                daily_schedules = []
                all_colonies = high_priority + medium_priority + low_priority
                
                # Distribute colonies across days
                colonies_per_day = max(1, len(all_colonies) // days_ahead)
                
                for day in range(days_ahead):
                    start_idx = day * colonies_per_day
                    end_idx = start_idx + colonies_per_day
                    
                    if day == days_ahead - 1:  # Last day gets remaining colonies
                        day_colonies = all_colonies[start_idx:]
                    else:
                        day_colonies = all_colonies[start_idx:end_idx]
                    
                    if day_colonies:
                        # Optimize route for this day
                        route_optimization = RouteOptimizer.optimize_collection_route(
                            collector_id, day_colonies
                        )
                        
                        daily_schedules.append({
                            'day': day + 1,
                            'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                            'colonies_count': len(day_colonies),
                            'total_distance_km': route_optimization['total_distance_km'],
                            'estimated_time_hours': route_optimization['estimated_time_hours'],
                            'fuel_cost_estimate': route_optimization['fuel_cost_estimate'],
                            'optimized_route': route_optimization['optimized_route']
                        })
                
                return {
                    'collector_id': collector_id,
                    'collector_name': collector['name'],
                    'schedule_period_days': days_ahead,
                    'total_colonies': len(all_colonies),
                    'daily_schedules': daily_schedules,
                    'summary': {
                        'total_distance_km': sum(day['total_distance_km'] for day in daily_schedules),
                        'total_estimated_time_hours': sum(day['estimated_time_hours'] for day in daily_schedules),
                        'total_fuel_cost_estimate': sum(day['fuel_cost_estimate'] for day in daily_schedules)
                    }
                }

    @staticmethod
    def get_traffic_aware_route(route_points: List[Dict], departure_time: str = None) -> Dict:
        """Get traffic-aware route optimization (placeholder for Google Maps API integration)"""
        # This would integrate with Google Maps API for real traffic data
        # For now, return basic optimization with traffic estimates
        
        base_optimization = RouteOptimizer.optimize_collection_route('', route_points)
        
        # Add traffic multipliers based on time of day
        from datetime import datetime
        if departure_time:
            departure_hour = datetime.fromisoformat(departure_time).hour
        else:
            departure_hour = datetime.now().hour
        
        # Traffic multipliers by hour (rush hours have higher multipliers)
        traffic_multipliers = {
            range(6, 9): 1.5,    # Morning rush
            range(9, 16): 1.0,   # Normal hours
            range(16, 19): 1.4,  # Evening rush
            range(19, 24): 1.1,  # Evening
            range(0, 6): 0.9     # Night
        }
        
        traffic_multiplier = 1.0
        for time_range, multiplier in traffic_multipliers.items():
            if departure_hour in time_range:
                traffic_multiplier = multiplier
                break
        
        # Apply traffic adjustment
        adjusted_time = base_optimization['estimated_time_hours'] * traffic_multiplier
        adjusted_fuel_cost = base_optimization['fuel_cost_estimate'] * traffic_multiplier
        
        return {
            **base_optimization,
            'estimated_time_hours': round(adjusted_time, 2),
            'fuel_cost_estimate': round(adjusted_fuel_cost, 2),
            'traffic_multiplier': traffic_multiplier,
            'departure_time': departure_time or datetime.now().isoformat(),
            'traffic_conditions': 'heavy' if traffic_multiplier > 1.3 else 'moderate' if traffic_multiplier > 1.1 else 'light'
        }