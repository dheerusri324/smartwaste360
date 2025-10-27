# backend/routes/database_debug.py
"""
EXPERT TEAM DATABASE DIAGNOSTIC SYSTEM
======================================
Team 1: Database Schema Expert - Analyzes table structures
Team 2: Data Integrity Expert - Checks data consistency
Team 3: Query Performance Expert - Identifies slow queries
Team 4: Migration Expert - Detects schema mismatches
Team 5: Production Data Expert - Compares localhost vs production
"""

from flask import Blueprint, jsonify
from config.database import get_db
from psycopg2.extras import RealDictCursor
import traceback

bp = Blueprint('database_debug', __name__)

@bp.route('/full-diagnostic', methods=['GET'])
def full_diagnostic():
    """Comprehensive database diagnostic by 5 expert teams"""
    try:
        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # TEAM 1: Schema Expert - Check all tables and columns
                cursor.execute("""
                    SELECT 
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position
                """)
                schema_info = {}
                for row in cursor.fetchall():
                    table = row['table_name']
                    if table not in schema_info:
                        schema_info[table] = []
                    schema_info[table].append({
                        'column': row['column_name'],
                        'type': row['data_type'],
                        'nullable': row['is_nullable'],
                        'default': row['column_default']
                    })
                
                # TEAM 2: Data Integrity Expert - Check record counts and recent data
                data_counts = {}
                recent_data = {}
                
                tables_to_check = [
                    'users', 'collectors', 'admins', 'colonies', 
                    'collection_bookings', 'waste_logs', 'user_transactions',
                    'notifications', 'collection_points'
                ]
                
                for table in tables_to_check:
                    try:
                        # Total count
                        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                        data_counts[table] = cursor.fetchone()['count']
                        
                        # Recent records (last 30 days)
                        if table in ['users', 'collectors', 'admins']:
                            cursor.execute(f"""
                                SELECT COUNT(*) as count FROM {table}
                                WHERE created_at > NOW() - INTERVAL '30 days'
                            """)
                            recent_data[table] = cursor.fetchone()['count']
                        elif table == 'collection_bookings':
                            cursor.execute(f"""
                                SELECT COUNT(*) as count FROM {table}
                                WHERE booking_date > NOW() - INTERVAL '30 days'
                            """)
                            recent_data[table] = cursor.fetchone()['count']
                        elif table == 'waste_logs':
                            cursor.execute(f"""
                                SELECT COUNT(*) as count FROM {table}
                                WHERE created_at > NOW() - INTERVAL '30 days'
                            """)
                            recent_data[table] = cursor.fetchone()['count']
                    except Exception as e:
                        data_counts[table] = f"Error: {str(e)}"
                        recent_data[table] = 0
                
                # TEAM 3: Query Performance Expert - Check for missing indexes
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname
                """)
                indexes = {}
                for row in cursor.fetchall():
                    table = row['tablename']
                    if table not in indexes:
                        indexes[table] = []
                    indexes[table].append({
                        'name': row['indexname'],
                        'definition': row['indexdef']
                    })
                
                # TEAM 4: Migration Expert - Check for missing columns in critical tables
                critical_columns = {
                    'collection_bookings': ['total_weight', 'notes', 'waste_types_collected', 'waste_types'],
                    'colonies': ['current_plastic_kg', 'current_paper_kg', 'current_metal_kg', 
                                'current_glass_kg', 'current_textile_kg', 'current_dry_waste_kg'],
                    'collectors': ['password_hash', 'total_weight_collected', 'is_active']
                }
                
                missing_columns = {}
                for table, required_cols in critical_columns.items():
                    if table in schema_info:
                        existing_cols = [col['column'] for col in schema_info[table]]
                        missing = [col for col in required_cols if col not in existing_cols]
                        if missing:
                            missing_columns[table] = missing
                
                # TEAM 5: Production Data Expert - Sample recent bookings
                cursor.execute("""
                    SELECT 
                        cb.booking_id,
                        cb.booking_date,
                        cb.time_slot,
                        cb.status,
                        cb.created_at,
                        c.colony_name,
                        col.name as collector_name
                    FROM collection_bookings cb
                    LEFT JOIN colonies c ON cb.colony_id = c.colony_id
                    LEFT JOIN collectors col ON cb.collector_id = col.collector_id
                    ORDER BY cb.created_at DESC
                    LIMIT 10
                """)
                recent_bookings = []
                for row in cursor.fetchall():
                    booking = dict(row)
                    # Convert dates to strings
                    for key, value in booking.items():
                        if hasattr(value, 'isoformat'):
                            booking[key] = value.isoformat()
                    recent_bookings.append(booking)
                
                # Check oldest booking
                cursor.execute("""
                    SELECT 
                        MIN(created_at) as oldest_booking,
                        MAX(created_at) as newest_booking,
                        COUNT(*) as total_bookings
                    FROM collection_bookings
                """)
                booking_timeline = cursor.fetchone()
                if booking_timeline:
                    for key, value in booking_timeline.items():
                        if hasattr(value, 'isoformat'):
                            booking_timeline[key] = value.isoformat()
                
                return jsonify({
                    'status': 'success',
                    'diagnostic_version': '5.0.0',
                    'teams': {
                        'team_1_schema': {
                            'tables_found': len(schema_info),
                            'table_list': list(schema_info.keys()),
                            'detailed_schema': schema_info
                        },
                        'team_2_data_integrity': {
                            'record_counts': data_counts,
                            'recent_records_30_days': recent_data,
                            'total_records': sum([v for v in data_counts.values() if isinstance(v, int)])
                        },
                        'team_3_performance': {
                            'indexes_found': sum([len(v) for v in indexes.values()]),
                            'indexes_by_table': indexes
                        },
                        'team_4_migration': {
                            'missing_columns': missing_columns,
                            'migration_needed': len(missing_columns) > 0
                        },
                        'team_5_production_data': {
                            'recent_bookings': recent_bookings,
                            'booking_timeline': booking_timeline,
                            'oldest_data_age_days': None  # Will calculate if data exists
                        }
                    },
                    'critical_issues': {
                        'missing_columns': missing_columns,
                        'empty_tables': [k for k, v in data_counts.items() if v == 0],
                        'old_data_detected': booking_timeline.get('oldest_booking', '') < '2025-10-01' if booking_timeline else False
                    }
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@bp.route('/fix-missing-columns', methods=['POST'])
def fix_missing_columns():
    """Automatically fix missing columns in production database"""
    try:
        with get_db() as db:
            with db.cursor() as cursor:
                fixes_applied = []
                
                # Fix collection_bookings table
                try:
                    cursor.execute("""
                        ALTER TABLE collection_bookings 
                        ADD COLUMN IF NOT EXISTS total_weight DECIMAL(10,2) DEFAULT 0
                    """)
                    fixes_applied.append('collection_bookings.total_weight')
                except Exception as e:
                    fixes_applied.append(f'collection_bookings.total_weight FAILED: {str(e)}')
                
                try:
                    cursor.execute("""
                        ALTER TABLE collection_bookings 
                        ADD COLUMN IF NOT EXISTS notes TEXT
                    """)
                    fixes_applied.append('collection_bookings.notes')
                except Exception as e:
                    fixes_applied.append(f'collection_bookings.notes FAILED: {str(e)}')
                
                try:
                    cursor.execute("""
                        ALTER TABLE collection_bookings 
                        ADD COLUMN IF NOT EXISTS waste_types_collected TEXT[]
                    """)
                    fixes_applied.append('collection_bookings.waste_types_collected')
                except Exception as e:
                    fixes_applied.append(f'collection_bookings.waste_types_collected FAILED: {str(e)}')
                
                try:
                    cursor.execute("""
                        ALTER TABLE collection_bookings 
                        ADD COLUMN IF NOT EXISTS waste_types TEXT
                    """)
                    fixes_applied.append('collection_bookings.waste_types')
                except Exception as e:
                    fixes_applied.append(f'collection_bookings.waste_types FAILED: {str(e)}')
                
                # Fix colonies table
                waste_columns = [
                    "current_plastic_kg DECIMAL(10,2) DEFAULT 0",
                    "current_paper_kg DECIMAL(10,2) DEFAULT 0",
                    "current_metal_kg DECIMAL(10,2) DEFAULT 0",
                    "current_glass_kg DECIMAL(10,2) DEFAULT 0",
                    "current_textile_kg DECIMAL(10,2) DEFAULT 0",
                    "current_dry_waste_kg DECIMAL(10,2) DEFAULT 0",
                    "last_collection_date TIMESTAMP",
                    "collection_frequency_days INTEGER DEFAULT 7"
                ]
                
                for column_def in waste_columns:
                    try:
                        cursor.execute(f"""
                            ALTER TABLE colonies 
                            ADD COLUMN IF NOT EXISTS {column_def}
                        """)
                        fixes_applied.append(f'colonies.{column_def.split()[0]}')
                    except Exception as e:
                        fixes_applied.append(f'colonies.{column_def.split()[0]} FAILED: {str(e)}')
                
                # Fix collectors table
                try:
                    cursor.execute("""
                        ALTER TABLE collectors 
                        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)
                    """)
                    fixes_applied.append('collectors.password_hash')
                except Exception as e:
                    fixes_applied.append(f'collectors.password_hash FAILED: {str(e)}')
                
                try:
                    cursor.execute("""
                        ALTER TABLE collectors 
                        ADD COLUMN IF NOT EXISTS total_weight_collected DECIMAL(10,2) DEFAULT 0
                    """)
                    fixes_applied.append('collectors.total_weight_collected')
                except Exception as e:
                    fixes_applied.append(f'collectors.total_weight_collected FAILED: {str(e)}')
                
                try:
                    cursor.execute("""
                        ALTER TABLE collectors 
                        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
                    """)
                    fixes_applied.append('collectors.is_active')
                except Exception as e:
                    fixes_applied.append(f'collectors.is_active FAILED: {str(e)}')
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Database schema fixes applied',
                    'fixes_applied': fixes_applied,
                    'total_fixes': len(fixes_applied)
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/clear-old-data', methods=['POST'])
def clear_old_data():
    """Clear data older than 7 days (for testing fresh deployment)"""
    try:
        with get_db() as db:
            with db.cursor() as cursor:
                deleted_counts = {}
                
                # Delete old bookings (>7 days)
                cursor.execute("""
                    DELETE FROM collection_bookings
                    WHERE created_at < NOW() - INTERVAL '7 days'
                    RETURNING booking_id
                """)
                deleted_counts['collection_bookings'] = len(cursor.fetchall())
                
                # Delete old waste logs (>7 days)
                cursor.execute("""
                    DELETE FROM waste_logs
                    WHERE created_at < NOW() - INTERVAL '7 days'
                    RETURNING log_id
                """)
                deleted_counts['waste_logs'] = len(cursor.fetchall())
                
                # Delete old transactions (>7 days)
                cursor.execute("""
                    DELETE FROM user_transactions
                    WHERE created_at < NOW() - INTERVAL '7 days'
                    RETURNING transaction_id
                """)
                deleted_counts['user_transactions'] = len(cursor.fetchall())
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Old data cleared successfully (>7 days)',
                    'deleted_records': deleted_counts,
                    'total_deleted': sum(deleted_counts.values())
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/clear-all-bookings', methods=['POST'])
def clear_all_bookings():
    """Clear ALL bookings (use with caution!)"""
    try:
        with get_db() as db:
            with db.cursor() as cursor:
                deleted_counts = {}
                
                # Delete ALL bookings
                cursor.execute("""
                    DELETE FROM collection_bookings
                    RETURNING booking_id
                """)
                deleted_counts['collection_bookings'] = len(cursor.fetchall())
                
                # Delete ALL waste logs
                cursor.execute("""
                    DELETE FROM waste_logs
                    RETURNING log_id
                """)
                deleted_counts['waste_logs'] = len(cursor.fetchall())
                
                # Delete ALL transactions
                cursor.execute("""
                    DELETE FROM user_transactions
                    RETURNING transaction_id
                """)
                deleted_counts['user_transactions'] = len(cursor.fetchall())
                
                db.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'ALL data cleared successfully',
                    'deleted_records': deleted_counts,
                    'total_deleted': sum(deleted_counts.values())
                }), 200
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
