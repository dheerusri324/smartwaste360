# backend/models/colony.py

from config.database import get_db
from psycopg2.extras import RealDictCursor

class Colony:
    @staticmethod
    def get_by_id(colony_id):
        """Get colony by ID"""
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM colonies WHERE colony_id = %s", (colony_id,))
                return cursor.fetchone()
    
    @staticmethod
    def find_or_create(colony_name, latitude=None, longitude=None):
        """
        Smart colony detection with location-based grouping.
        Groups users by larger geographic areas for better community building.
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Step 1: Try exact name match
                cursor.execute("SELECT colony_id, colony_name FROM colonies WHERE LOWER(colony_name) = LOWER(%s)", (colony_name,))
                existing_colony = cursor.fetchone()
                
                if existing_colony:
                    print(f"[INFO] Found exact match: {existing_colony['colony_name']}")
                    return existing_colony['colony_id']
                
                # Step 2: Try partial name matching for similar areas
                if colony_name and colony_name != 'Unknown Area':
                    # Check if colony name contains or is contained in existing colony names
                    cursor.execute("""
                        SELECT colony_id, colony_name
                        FROM colonies
                        WHERE LOWER(colony_name) LIKE LOWER(%s) 
                           OR LOWER(%s) LIKE LOWER(colony_name)
                           OR LOWER(colony_name) LIKE LOWER(%s)
                        ORDER BY LENGTH(colony_name)
                        LIMIT 1
                    """, (f'%{colony_name}%', f'%{colony_name}%', f'%{colony_name.split()[0]}%'))
                    
                    similar_colony = cursor.fetchone()
                    if similar_colony:
                        print(f"[INFO] Found similar area: {similar_colony['colony_name']} (matches: {colony_name})")
                        return similar_colony['colony_id']
                
                # Step 3: Location-based grouping with larger radius for major areas
                if latitude is not None and longitude is not None:
                    # First check within 3km for major area grouping
                    cursor.execute("""
                        SELECT colony_id, colony_name, distance
                        FROM (
                            SELECT colony_id, colony_name,
                                (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * 
                                cos(radians(longitude) - radians(%s)) + 
                                sin(radians(%s)) * sin(radians(latitude)))) AS distance
                            FROM colonies
                            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                        ) AS colonies_with_distance
                        WHERE distance <= 3.0
                        ORDER BY distance
                        LIMIT 1
                    """, (latitude, longitude, latitude))
                    
                    nearby_colony = cursor.fetchone()
                    if nearby_colony:
                        print(f"[INFO] Grouping with nearby area: {nearby_colony['colony_name']} ({nearby_colony['distance']:.2f}km away)")
                        
                        # Update the colony's center point to be more central
                        Colony._update_colony_center(nearby_colony['colony_id'], latitude, longitude)
                        return nearby_colony['colony_id']
                
                # Step 4: Create new colony only if no suitable grouping found
                print(f"[INFO] Creating new area colony: {colony_name}")
                
                # Get better location details for new colony
                city, state = Colony._get_city_state_from_coords(latitude, longitude)
                
                sql = """
                    INSERT INTO colonies (colony_name, latitude, longitude, city, state, pincode, address, total_points, total_users)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING colony_id
                """
                params = (colony_name, latitude, longitude, city, state, '000000', f'{colony_name}, {city}', 0, 1)
                cursor.execute(sql, params)
                new_colony = cursor.fetchone()
                db.commit()
                return new_colony['colony_id']
    
    @staticmethod
    def _update_colony_center(colony_id, new_lat, new_lng):
        """Update colony center to be more representative of all users"""
        with get_db() as db:
            if not db: return
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get current colony location and user count
                cursor.execute("SELECT latitude, longitude, total_users FROM colonies WHERE colony_id = %s", (colony_id,))
                colony = cursor.fetchone()
                
                if colony and colony['latitude'] and colony['longitude']:
                    # Calculate weighted average of locations
                    current_users = colony['total_users'] or 1
                    current_lat = float(colony['latitude'])
                    current_lng = float(colony['longitude'])
                    
                    # Weight: existing center vs new location
                    weight_existing = current_users
                    weight_new = 1
                    total_weight = weight_existing + weight_new
                    
                    new_center_lat = (current_lat * weight_existing + new_lat * weight_new) / total_weight
                    new_center_lng = (current_lng * weight_existing + new_lng * weight_new) / total_weight
                    
                    # Update colony center and user count
                    cursor.execute("""
                        UPDATE colonies 
                        SET latitude = %s, longitude = %s, total_users = total_users + 1
                        WHERE colony_id = %s
                    """, (new_center_lat, new_center_lng, colony_id))
                    db.commit()
    
    @staticmethod
    def _get_city_state_from_coords(latitude, longitude):
        """Get city and state from coordinates"""
        try:
            import requests
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
            headers = {'User-Agent': 'SmartWaste360/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            address = data.get('address', {})
            
            city = address.get('city') or address.get('town') or address.get('village') or 'Unknown'
            state = address.get('state') or 'Unknown'
            
            return city, state
        except:
            return 'Unknown', 'Unknown'
    @staticmethod
    def update_waste_weight(colony_id, weight_change, is_recyclable):
        """Adds or subtracts weight from a colony's current dry waste total."""
        # We only add weight if the item is recyclable (dry waste)
        if not is_recyclable:
            return

        sql = "UPDATE colonies SET current_dry_waste_kg = current_dry_waste_kg + %s WHERE colony_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (weight_change, colony_id))
                db.commit()

    @staticmethod
    def get_ready_for_collection(threshold=50.0, lat=None, lon=None, radius=10.0):
        """
        Finds colonies with waste above a threshold.
        If lat/lon are provided, it also filters by distance.
        """
        params = [threshold]
        
        # Start with the base query
        sql = """
            SELECT *,
                (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + 
                sin(radians(%s)) * sin(radians(latitude)))) AS distance
            FROM colonies
            WHERE current_dry_waste_kg >= %s
        """
        
        # If location is provided, add the distance filter
        if lat is not None and lon is not None:
            # Add location parameters for both the distance calculation and the HAVING clause
            params = [lat, lon, lat] + params + [lat, lon, lat, radius]
            sql += """
                HAVING distance <= %s
                ORDER BY distance
            """
        else:
            # If no location, just add the base location parameters
            params = [0, 0, 0] + params # Placeholder lat/lon for distance calculation
            sql += " ORDER BY current_dry_waste_kg DESC"


        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
    @staticmethod
    def create_colony(colony_name, address, city, state, pincode, latitude, longitude):
        """Create a new colony (typically used by an admin)."""
        sql = """
            INSERT INTO colonies 
            (colony_name, address, city, state, pincode, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING colony_id
        """
        params = (colony_name, address, city, state, pincode, latitude, longitude)
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                colony_id = cursor.fetchone()['colony_id']
                db.commit()
                return colony_id

    @staticmethod
    def get_colony_by_id(colony_id):
        """Get a single colony by its ID."""
        sql = "SELECT * FROM colonies WHERE colony_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (colony_id,))
                return cursor.fetchone()
    
    @staticmethod
    def get_all():
        """Get a list of all colonies from the database."""
        sql = "SELECT * FROM colonies ORDER BY colony_name"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

    @staticmethod
    def get_nearby_colonies(latitude, longitude, radius_km=10):
        """Get colonies within a certain radius using the Haversine formula."""
        sql = """
            SELECT *, distance
            FROM (
                SELECT *,
                    (6371 * acos(
                        LEAST(1.0,
                            cos(radians(%s)) * cos(radians(CAST(latitude AS FLOAT))) * 
                            cos(radians(CAST(longitude AS FLOAT)) - radians(%s)) + 
                            sin(radians(%s)) * sin(radians(CAST(latitude AS FLOAT)))
                        )
                    )) AS distance
                FROM colonies
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ) AS colonies_with_distance
            WHERE distance <= %s
            ORDER BY distance
        """
        params = (latitude, longitude, latitude, radius_km)
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()

    @staticmethod
    def update_colony_points(colony_id, points):
        """Update a colony's total points."""
        sql = "UPDATE colonies SET total_points = total_points + %s WHERE colony_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (points, colony_id))
                db.commit()

    @staticmethod
    def update_colony_user_count(colony_id, change=1):
        """Update the number of users in a colony."""
        sql = "UPDATE colonies SET total_users = total_users + %s WHERE colony_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (change, colony_id))
                db.commit()

    @staticmethod
    def get_colonies_ready_for_collection_by_type(waste_types=None, collector_id=None):
        """Get colonies ready for collection, excluding those with scheduled bookings."""
        base_sql = """
            SELECT c.*, 
                   c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                   c.current_glass_kg, c.current_textile_kg, c.current_dry_waste_kg,
                   CASE 
                       WHEN c.current_plastic_kg >= 5 THEN 'plastic'
                       WHEN c.current_paper_kg >= 5 THEN 'paper'
                       WHEN c.current_metal_kg >= 1 THEN 'metal'
                       WHEN c.current_glass_kg >= 2 THEN 'glass'
                       WHEN c.current_textile_kg >= 1 THEN 'textile'
                       WHEN c.current_dry_waste_kg >= 10 THEN 'mixed'
                       ELSE NULL
                   END as ready_waste_type,
                   GREATEST(c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                           c.current_glass_kg, c.current_textile_kg) as max_waste_kg
            FROM colonies c
            LEFT JOIN collection_bookings cb ON c.colony_id = cb.colony_id AND cb.status = 'scheduled'
            WHERE (c.current_plastic_kg >= 5 
               OR c.current_paper_kg >= 5 
               OR c.current_metal_kg >= 1 
               OR c.current_glass_kg >= 2 
               OR c.current_textile_kg >= 1 
               OR c.current_dry_waste_kg >= 10)
            AND cb.booking_id IS NULL
        """
        
        # Add waste type filtering if collector has preferences
        if waste_types and len(waste_types) > 0:
            type_conditions = []
            if 'plastic' in waste_types:
                type_conditions.append("c.current_plastic_kg >= 5")
            if 'paper' in waste_types:
                type_conditions.append("c.current_paper_kg >= 5")
            if 'metal' in waste_types:
                type_conditions.append("c.current_metal_kg >= 1")
            if 'glass' in waste_types:
                type_conditions.append("c.current_glass_kg >= 2")
            if 'textile' in waste_types:
                type_conditions.append("c.current_textile_kg >= 1")
            
            if type_conditions:
                base_sql = base_sql.replace(
                    "WHERE c.current_plastic_kg >= 5 OR c.current_paper_kg >= 5 OR c.current_metal_kg >= 1 OR c.current_glass_kg >= 2 OR c.current_textile_kg >= 1 OR c.current_dry_waste_kg >= 10",
                    f"WHERE ({' OR '.join(type_conditions)})"
                )
        
        base_sql += " ORDER BY max_waste_kg DESC"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(base_sql)
                return cursor.fetchall()

    @staticmethod
    def get_ready_colonies_near_location(latitude, longitude, radius_km, waste_types=None, collector_id=None):
        """Get colonies ready for collection near a specific location."""
        base_sql = """
            SELECT *, distance
            FROM (
                SELECT c.*, 
                       c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                       c.current_glass_kg, c.current_textile_kg, c.current_dry_waste_kg,
                       CASE 
                           WHEN c.current_plastic_kg >= 5 THEN 'plastic'
                           WHEN c.current_paper_kg >= 5 THEN 'paper'
                           WHEN c.current_metal_kg >= 1 THEN 'metal'
                           WHEN c.current_glass_kg >= 2 THEN 'glass'
                           WHEN c.current_textile_kg >= 1 THEN 'textile'
                           WHEN c.current_dry_waste_kg >= 10 THEN 'mixed'
                           ELSE NULL
                       END as ready_waste_type,
                       GREATEST(c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                               c.current_glass_kg, c.current_textile_kg) as max_waste_kg,
                       (6371 * acos(
                           LEAST(1.0,
                               cos(radians(%s)) * cos(radians(CAST(c.latitude AS FLOAT))) * 
                               cos(radians(CAST(c.longitude AS FLOAT)) - radians(%s)) + 
                               sin(radians(%s)) * sin(radians(CAST(c.latitude AS FLOAT)))
                           )
                       )) AS distance
                FROM colonies c
                LEFT JOIN collection_bookings cb ON c.colony_id = cb.colony_id AND cb.status = 'scheduled'
                WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
                  AND (c.current_plastic_kg >= 5 
                       OR c.current_paper_kg >= 5 
                       OR c.current_metal_kg >= 1 
                       OR c.current_glass_kg >= 2 
                       OR c.current_textile_kg >= 1 
                       OR c.current_dry_waste_kg >= 10)
                  AND cb.booking_id IS NULL
            ) AS ready_colonies_with_distance
            WHERE distance <= %s
        """
        
        params = [latitude, longitude, latitude, radius_km]
        
        # Add waste type filtering if collector has preferences
        if waste_types and len(waste_types) > 0:
            type_conditions = []
            if 'plastic' in waste_types:
                type_conditions.append("current_plastic_kg >= 5")
            if 'paper' in waste_types:
                type_conditions.append("current_paper_kg >= 5")
            if 'metal' in waste_types:
                type_conditions.append("current_metal_kg >= 1")
            if 'glass' in waste_types:
                type_conditions.append("current_glass_kg >= 2")
            if 'textile' in waste_types:
                type_conditions.append("current_textile_kg >= 1")
            
            if type_conditions:
                base_sql += f" AND ({' OR '.join(type_conditions)})"
        
        base_sql += " ORDER BY distance, max_waste_kg DESC"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(base_sql, params)
                return cursor.fetchall()

    @staticmethod
    def get_leaderboard(limit=10):
        """Get the top colonies ranked by total points."""
        sql = """
            SELECT colony_id, colony_name, total_points, total_users
            FROM colonies
            ORDER BY total_points DESC
            LIMIT %s
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (limit,))
                return cursor.fetchall()