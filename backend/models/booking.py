# backend/models/booking.py

from config.database import get_db
from psycopg2.extras import RealDictCursor

class Booking:
    @staticmethod
    def create_booking(colony_id, collector_id, booking_date, time_slot):
        """Create a new collection booking"""
        sql = """
            INSERT INTO collection_bookings 
            (colony_id, collector_id, booking_date, time_slot)
            VALUES (%s, %s, %s, %s)
            RETURNING booking_id
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (colony_id, collector_id, booking_date, time_slot))
                result = cursor.fetchone()
                booking_id = result['booking_id']
                db.commit()
                return booking_id

    @staticmethod
    def get_booking_details(booking_id, collector_id):
        """Get booking details including estimated materials and weight"""
        sql = """
            SELECT cb.*, c.colony_name, c.current_plastic_kg, c.current_paper_kg, 
                   c.current_metal_kg, c.current_glass_kg, c.current_textile_kg,
                   GREATEST(c.current_plastic_kg, c.current_paper_kg, c.current_metal_kg, 
                           c.current_glass_kg, c.current_textile_kg) as estimated_weight
            FROM collection_bookings cb
            JOIN colonies c ON cb.colony_id = c.colony_id
            WHERE cb.booking_id = %s AND cb.collector_id = %s AND cb.status = 'scheduled'
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (booking_id, collector_id))
                booking = cursor.fetchone()
                
                if booking:
                    # Determine which materials are available for collection
                    scheduled_materials = []
                    if booking['current_plastic_kg'] >= 5:
                        scheduled_materials.append('plastic')
                    if booking['current_paper_kg'] >= 5:
                        scheduled_materials.append('paper')
                    if booking['current_metal_kg'] >= 1:
                        scheduled_materials.append('metal')
                    if booking['current_glass_kg'] >= 2:
                        scheduled_materials.append('glass')
                    if booking['current_textile_kg'] >= 1:
                        scheduled_materials.append('textile')
                    
                    booking_dict = dict(booking)
                    booking_dict['scheduled_materials'] = scheduled_materials
                    return booking_dict
                
                return None

    @staticmethod
    def get_bookings_by_colony(colony_id, status=None):
        """Get bookings for a colony, optionally filtered by status"""
        sql = """
            SELECT cb.*, c.colony_name, col.name as collector_name
            FROM collection_bookings cb
            JOIN colonies c ON cb.colony_id = c.colony_id
            JOIN collectors col ON cb.collector_id = col.collector_id
            WHERE cb.colony_id = %s
        """
        params = [colony_id]
        if status:
            sql += " AND cb.status = %s"
            params.append(status)
        sql += " ORDER BY cb.booking_date, cb.time_slot"

        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()

    @staticmethod
    def get_bookings_by_collector(collector_id, status=None):
        """Get bookings for a collector, optionally filtered by status"""
        sql = """
            SELECT cb.*, c.colony_name
            FROM collection_bookings cb
            JOIN colonies c ON cb.colony_id = c.colony_id
            WHERE cb.collector_id = %s
        """
        params = [collector_id]
        if status:
            sql += " AND cb.status = %s"
            params.append(status)
        sql += " ORDER BY cb.booking_date, cb.time_slot"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()

    @staticmethod
    def update_booking_status(booking_id, status):
        """Update booking status"""
        if status == 'completed':
            sql = "UPDATE collection_bookings SET status = %s, completed_at = NOW() WHERE booking_id = %s"
        else:
            sql = "UPDATE collection_bookings SET status = %s WHERE booking_id = %s"
            
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (status, booking_id))
                db.commit()

    @staticmethod
    def add_collected_weight(booking_id, weight):
        """Add weight to collected total"""
        sql = "UPDATE collection_bookings SET total_weight_collected = total_weight_collected + %s WHERE booking_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (weight, booking_id))
                db.commit()

    @staticmethod
    def complete_collection(booking_id, collector_id, total_weight_collected, waste_types_collected, notes=''):
        """Complete a collection booking and reset colony waste totals."""
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # First, verify the booking belongs to this collector and is scheduled
                cursor.execute("""
                    SELECT cb.*, c.colony_id 
                    FROM collection_bookings cb
                    JOIN colonies c ON cb.colony_id = c.colony_id
                    WHERE cb.booking_id = %s AND cb.collector_id = %s AND cb.status = 'scheduled'
                """, (booking_id, collector_id))
                
                booking = cursor.fetchone()
                if not booking:
                    return False
                
                colony_id = booking['colony_id']
                
                # Update booking status and details
                cursor.execute("""
                    UPDATE collection_bookings 
                    SET status = 'completed', 
                        completed_at = NOW(),
                        total_weight_collected = %s,
                        waste_types = %s,
                        notes = %s
                    WHERE booking_id = %s
                """, (total_weight_collected, waste_types_collected, notes, booking_id))
                
                # Reset colony waste totals for collected waste types
                reset_updates = []
                for waste_type in waste_types_collected:
                    if waste_type == 'plastic':
                        reset_updates.append("current_plastic_kg = 0")
                    elif waste_type == 'paper':
                        reset_updates.append("current_paper_kg = 0")
                    elif waste_type == 'metal':
                        reset_updates.append("current_metal_kg = 0")
                    elif waste_type == 'glass':
                        reset_updates.append("current_glass_kg = 0")
                    elif waste_type == 'textile':
                        reset_updates.append("current_textile_kg = 0")
                    elif waste_type == 'organic':
                        reset_updates.append("current_organic_kg = 0")
                
                if reset_updates:
                    # Reset the specified waste types
                    reset_sql = f"""
                        UPDATE colonies 
                        SET {', '.join(reset_updates)}
                        WHERE colony_id = %s
                    """
                    cursor.execute(reset_sql, (colony_id,))
                    
                    # Recalculate total dry waste after reset
                    cursor.execute("""
                        UPDATE colonies 
                        SET current_dry_waste_kg = current_plastic_kg + current_paper_kg + current_metal_kg + current_glass_kg + current_textile_kg
                        WHERE colony_id = %s
                    """, (colony_id,))
                
                # Update collector's total weight collected
                cursor.execute("""
                    UPDATE collectors 
                    SET total_weight_collected = total_weight_collected + %s 
                    WHERE collector_id = %s
                """, (total_weight_collected, collector_id))
                
                db.commit()
                return True