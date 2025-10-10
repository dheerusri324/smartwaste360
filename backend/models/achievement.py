# backend/models/achievement.py

from config.database import get_db
from psycopg2.extras import RealDictCursor

class Achievement:
    # Define achievement types and criteria
    ACHIEVEMENTS = {
        'first_scan': {
            'name': 'First Steps',
            'description': 'Classify your first waste item',
            'points': 50,
            'icon': 'camera',
            'criteria': {'waste_classifications': 1}
        },
        'eco_warrior': {
            'name': 'Eco Warrior',
            'description': 'Classify 100 waste items',
            'points': 500,
            'icon': 'shield',
            'criteria': {'waste_classifications': 100}
        },
        'recycling_champion': {
            'name': 'Recycling Champion',
            'description': 'Help your colony reach collection threshold',
            'points': 200,
            'icon': 'award',
            'criteria': {'colony_collections_triggered': 1}
        },
        'green_streak': {
            'name': 'Green Streak',
            'description': 'Classify waste for 7 consecutive days',
            'points': 300,
            'icon': 'calendar',
            'criteria': {'consecutive_days': 7}
        },
        'plastic_hunter': {
            'name': 'Plastic Hunter',
            'description': 'Classify 50 plastic items',
            'points': 250,
            'icon': 'target',
            'criteria': {'plastic_classifications': 50}
        },
        'weight_master': {
            'name': 'Weight Master',
            'description': 'Process 100kg of waste',
            'points': 400,
            'icon': 'scale',
            'criteria': {'total_weight_kg': 100}
        },
        'community_leader': {
            'name': 'Community Leader',
            'description': 'Be in top 3 of your colony leaderboard',
            'points': 350,
            'icon': 'crown',
            'criteria': {'colony_rank': 3}
        }
    }

    @staticmethod
    def create_tables():
        """Create achievement-related tables"""
        with get_db() as db:
            with db.cursor() as cursor:
                # User achievements table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_achievements (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
                        achievement_id VARCHAR(50) NOT NULL,
                        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        points_awarded INT DEFAULT 0,
                        UNIQUE(user_id, achievement_id)
                    );
                """)
                
                # User statistics table for tracking progress
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_statistics (
                        user_id INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                        waste_classifications INT DEFAULT 0,
                        plastic_classifications INT DEFAULT 0,
                        paper_classifications INT DEFAULT 0,
                        metal_classifications INT DEFAULT 0,
                        glass_classifications INT DEFAULT 0,
                        organic_classifications INT DEFAULT 0,
                        textile_classifications INT DEFAULT 0,
                        total_weight_kg DECIMAL(10,2) DEFAULT 0,
                        consecutive_days INT DEFAULT 0,
                        last_classification_date DATE,
                        colony_collections_triggered INT DEFAULT 0,
                        current_colony_rank INT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                db.commit()

    @staticmethod
    def check_and_award_achievements(user_id):
        """Check if user has earned any new achievements"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get user statistics
                cursor.execute("SELECT * FROM user_statistics WHERE user_id = %s", (user_id,))
                stats = cursor.fetchone()
                
                if not stats:
                    return []
                
                # Get already earned achievements
                cursor.execute("SELECT achievement_id FROM user_achievements WHERE user_id = %s", (user_id,))
                earned = {row['achievement_id'] for row in cursor.fetchall()}
                
                new_achievements = []
                
                # Check each achievement
                for achievement_id, achievement in Achievement.ACHIEVEMENTS.items():
                    if achievement_id in earned:
                        continue
                    
                    criteria = achievement['criteria']
                    earned_achievement = True
                    
                    # Check criteria
                    for criterion, required_value in criteria.items():
                        if criterion == 'waste_classifications':
                            if stats['waste_classifications'] < required_value:
                                earned_achievement = False
                                break
                        elif criterion == 'plastic_classifications':
                            if stats['plastic_classifications'] < required_value:
                                earned_achievement = False
                                break
                        elif criterion == 'total_weight_kg':
                            if stats['total_weight_kg'] < required_value:
                                earned_achievement = False
                                break
                        elif criterion == 'consecutive_days':
                            if stats['consecutive_days'] < required_value:
                                earned_achievement = False
                                break
                        elif criterion == 'colony_collections_triggered':
                            if stats['colony_collections_triggered'] < required_value:
                                earned_achievement = False
                                break
                        elif criterion == 'colony_rank':
                            if not stats['current_colony_rank'] or stats['current_colony_rank'] > required_value:
                                earned_achievement = False
                                break
                    
                    if earned_achievement:
                        # Award achievement
                        cursor.execute("""
                            INSERT INTO user_achievements (user_id, achievement_id, points_awarded)
                            VALUES (%s, %s, %s)
                        """, (user_id, achievement_id, achievement['points']))
                        
                        # Update user points
                        cursor.execute("""
                            UPDATE users SET total_points = total_points + %s WHERE user_id = %s
                        """, (achievement['points'], user_id))
                        
                        new_achievements.append({
                            'id': achievement_id,
                            'name': achievement['name'],
                            'description': achievement['description'],
                            'points': achievement['points'],
                            'icon': achievement['icon']
                        })
                
                db.commit()
                return new_achievements

    @staticmethod
    def update_user_statistics(user_id, waste_category, weight_kg):
        """Update user statistics after waste classification"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get or create user statistics
                cursor.execute("SELECT * FROM user_statistics WHERE user_id = %s", (user_id,))
                stats = cursor.fetchone()
                
                if not stats:
                    cursor.execute("""
                        INSERT INTO user_statistics (user_id, waste_classifications, total_weight_kg, last_classification_date)
                        VALUES (%s, 1, %s, CURRENT_DATE)
                    """, (user_id, weight_kg))
                else:
                    # Update statistics
                    category_field = f"{waste_category}_classifications"
                    
                    # Calculate consecutive days
                    consecutive_days = stats['consecutive_days']
                    if stats['last_classification_date']:
                        days_diff = (cursor.execute("SELECT CURRENT_DATE - %s", (stats['last_classification_date'],)).fetchone()[0]).days
                        if days_diff == 1:
                            consecutive_days += 1
                        elif days_diff > 1:
                            consecutive_days = 1
                    else:
                        consecutive_days = 1
                    
                    # Update query
                    update_sql = f"""
                        UPDATE user_statistics 
                        SET waste_classifications = waste_classifications + 1,
                            {category_field} = {category_field} + 1,
                            total_weight_kg = total_weight_kg + %s,
                            consecutive_days = %s,
                            last_classification_date = CURRENT_DATE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """
                    cursor.execute(update_sql, (weight_kg, consecutive_days, user_id))
                
                db.commit()

    @staticmethod
    def get_user_achievements(user_id):
        """Get all achievements for a user"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT achievement_id, earned_at, points_awarded
                    FROM user_achievements
                    WHERE user_id = %s
                    ORDER BY earned_at DESC
                """, (user_id,))
                
                earned_achievements = cursor.fetchall()
                
                # Add achievement details
                achievements = []
                for earned in earned_achievements:
                    achievement_data = Achievement.ACHIEVEMENTS.get(earned['achievement_id'])
                    if achievement_data:
                        achievements.append({
                            **achievement_data,
                            'earned_at': earned['earned_at'],
                            'points_awarded': earned['points_awarded']
                        })
                
                return achievements

    @staticmethod
    def get_user_progress(user_id):
        """Get user progress towards achievements"""
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM user_statistics WHERE user_id = %s", (user_id,))
                stats = cursor.fetchone()
                
                if not stats:
                    return {}
                
                # Get earned achievements
                cursor.execute("SELECT achievement_id FROM user_achievements WHERE user_id = %s", (user_id,))
                earned = {row['achievement_id'] for row in cursor.fetchall()}
                
                progress = {}
                for achievement_id, achievement in Achievement.ACHIEVEMENTS.items():
                    if achievement_id in earned:
                        progress[achievement_id] = {'completed': True, 'progress': 100}
                        continue
                    
                    criteria = achievement['criteria']
                    min_progress = 100
                    
                    for criterion, required_value in criteria.items():
                        current_value = 0
                        if criterion == 'waste_classifications':
                            current_value = stats['waste_classifications']
                        elif criterion == 'plastic_classifications':
                            current_value = stats['plastic_classifications']
                        elif criterion == 'total_weight_kg':
                            current_value = float(stats['total_weight_kg'])
                        elif criterion == 'consecutive_days':
                            current_value = stats['consecutive_days']
                        elif criterion == 'colony_collections_triggered':
                            current_value = stats['colony_collections_triggered']
                        elif criterion == 'colony_rank':
                            current_value = stats['current_colony_rank'] or 999
                            # For rank, lower is better
                            current_progress = max(0, (required_value - current_value + 1) / required_value * 100)
                            min_progress = min(min_progress, current_progress)
                            continue
                        
                        current_progress = min(100, (current_value / required_value) * 100)
                        min_progress = min(min_progress, current_progress)
                    
                    progress[achievement_id] = {
                        'completed': False,
                        'progress': min_progress
                    }
                
                return progress