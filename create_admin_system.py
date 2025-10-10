#!/usr/bin/env python3
"""
Create admin system with database schema
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

def create_admin_system():
    """Create admin system database schema"""
    try:
        from config.database import get_db
        
        print("Creating admin system...")
        
        with get_db() as db:
            with db.cursor() as cursor:
                # Create admins table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        admin_id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        role VARCHAR(20) DEFAULT 'admin',
                        permissions TEXT[], -- Array of permissions
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    );
                """)
                print("✅ Created admins table")
                
                # Add admin activity logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_activity_logs (
                        log_id SERIAL PRIMARY KEY,
                        admin_id INT REFERENCES admins(admin_id),
                        action VARCHAR(100) NOT NULL,
                        target_type VARCHAR(50), -- 'user', 'collector', 'colony', etc.
                        target_id VARCHAR(50),
                        details JSONB,
                        ip_address INET,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("✅ Created admin activity logs table")
                
                # Add ban/suspension functionality to existing tables
                cursor.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS ban_reason TEXT;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS banned_at TIMESTAMP;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS banned_by INT REFERENCES admins(admin_id);
                """)
                print("✅ Added ban functionality to users table")
                
                cursor.execute("""
                    ALTER TABLE collectors ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;
                    ALTER TABLE collectors ADD COLUMN IF NOT EXISTS ban_reason TEXT;
                    ALTER TABLE collectors ADD COLUMN IF NOT EXISTS banned_at TIMESTAMP;
                    ALTER TABLE collectors ADD COLUMN IF NOT EXISTS banned_by INT REFERENCES admins(admin_id);
                """)
                print("✅ Added ban functionality to collectors table")
                
                # Create default super admin
                cursor.execute("""
                    INSERT INTO admins (username, email, password_hash, full_name, permissions)
                    VALUES ('admin', 'admin@smartwaste360.com', '$2b$12$LQv3c1yqBwVHLwuERFXo8ue4YVmGryCdCvBhyn6jlSURAjNjTtqHW', 'System Administrator', ARRAY['manage_users', 'manage_collectors', 'manage_colonies', 'view_analytics', 'system_settings'])
                    ON CONFLICT (username) DO NOTHING;
                """)
                print("✅ Created default admin (username: admin, password: secret)")
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_activity_admin ON admin_activity_logs(admin_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_activity_created ON admin_activity_logs(created_at);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_banned ON users(is_banned);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_collectors_banned ON collectors(is_banned);")
                
                db.commit()
                print("🎉 Admin system created successfully!")
                print("\n📋 Default Admin Credentials:")
                print("   Username: admin")
                print("   Password: secret")
                print("   Email: admin@smartwaste360.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_admin_system()