# backend/services/points_service.py

from config.database import get_db
import json
from psycopg2.extras import RealDictCursor

class PointsService:
    def __init__(self):
        """
        Initializes the service and loads points configuration from the database.
        """
        self.points_config = self._load_points_config()

    def _load_points_config(self):
        """
        Loads waste categories and their point values from the database.
        """
        config = {}
        try:
            with get_db() as db:
                if not db:
                    print("[WARN] Database connection not available for loading points config.")
                    return {}
                with db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT material_type, points_per_kg FROM points_config")
                    for row in cursor.fetchall():
                        config[row['material_type']] = float(row['points_per_kg'])
            
            # --- THIS IS THE FIX ---
            # Replaced emoji with simple text
            print("[OK] Points configuration loaded successfully from database.")
            return config
        except Exception as e:
            # --- THIS IS THE FIX ---
            # Replaced emoji with simple text
            print(f"[ERROR] Error loading points config from database: {e}")
            return {}

    def calculate_points(self, category, weight_kg):
        """
        Calculates points based on the waste category and weight.
        """
        points_per_kg = self.points_config.get(category, 0)
        return round(points_per_kg * weight_kg)

    def calculate_transaction_points(self, materials_json_string):
        """
        Calculates total points from a JSON string of materials and weights.
        """
        try:
            materials = json.loads(materials_json_string)
            total_points = 0
            for category, weight_kg in materials.items():
                total_points += self.calculate_points(category, float(weight_kg))
            return total_points
        except Exception:
            return 0

    def get_co2_savings(self, category, weight_kg):
        """
        Calculates CO2 savings based on waste category and weight.
        """
        co2_factors = {
            'plastic': 2.0,
            'paper': 0.9,
            'cardboard': 0.9,
            'metal': 5.0,
            'glass': 0.3,
            'organic': 0.1
        }
        return co2_factors.get(category, 0) * weight_kg
    
    def get_co_2_savings(self, category, weight_kg):
        """
        Alias for get_co2_savings for compatibility.
        """
        return self.get_co2_savings(category, weight_kg)