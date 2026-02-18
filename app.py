# app.py (in root directory)

import os
import sys
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS  # <-- 1. IMPORT CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

app = Flask(__name__)

# --- CONFIGURATION ---
# SECURITY: Real secrets must come from env vars. These defaults are for local dev only.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-only-insecure-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-only-insecure-jwt-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'backend/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- INITIALIZE EXTENSIONS ---

# 👇 2. INITIALIZE CORS AND ALLOW YOUR REACT APP'S ORIGIN 👇
# Use Flask-CORS with explicit configuration
CORS(app, 
     origins=['*'],  # Allow all origins - Vercel keeps changing URLs
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=False)

# Additional CORS handling for admin routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

jwt = JWTManager(app)

# --- CREATE DIRECTORIES ---
def create_directories():
    directories = ['backend/uploads', 'backend/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

create_directories()

# --- IMPORT & REGISTER BLUEPRINTS (ROUTES) ---
from routes import auth, waste, booking, leaderboard, camera, collector, transaction, health, colony, collection_points, admin, analytics, migration

app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(waste.bp, url_prefix='/api/waste')
app.register_blueprint(booking.bp, url_prefix='/api/booking')
app.register_blueprint(leaderboard.bp, url_prefix='/api/leaderboard')
app.register_blueprint(camera.bp, url_prefix='/api/camera')
app.register_blueprint(collector.bp, url_prefix='/api/collector')
app.register_blueprint(transaction.bp, url_prefix='/api/transaction')
app.register_blueprint(colony.bp, url_prefix='/api/colony')
app.register_blueprint(collection_points.bp, url_prefix='/api/collection-points')
app.register_blueprint(admin.bp, url_prefix='/api/admin')
app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
app.register_blueprint(health.bp, url_prefix='/health')
app.register_blueprint(migration.bp, url_prefix='/api/migration')

# Advanced features temporarily disabled for debugging
# app.register_blueprint(advanced_features.bp, url_prefix='/api/advanced')

# --- ROOT ROUTE ---
@app.route('/')
def home():
    return jsonify({
        'message': 'SmartWaste360 API v6.0.0',
        'version': '6.0.0',
        'status': 'running',
        'cors_enabled': True,
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'cors_origins': 'all_origins_allowed',
        'version': '6.0.0',
    })

# --- REGISTER DEBUG ROUTES (only in development) ---
if os.getenv('FLASK_DEBUG', '1') == '1':
    from routes import database_debug, diagnostic_fixes, debug_logs, debug_routes, setup
    app.register_blueprint(database_debug.bp, url_prefix='/api/database-debug')
    app.register_blueprint(diagnostic_fixes.bp, url_prefix='/api/fixes')
    app.register_blueprint(debug_logs.bp, url_prefix='/api/debug')
    app.register_blueprint(debug_routes.bp)
    app.register_blueprint(setup.bp)
    print("⚠️  DEBUG MODE: Debug and setup endpoints are ENABLED")
else:
    print("🔒 PRODUCTION MODE: Debug and setup endpoints are DISABLED")

# --- VALIDATE PRODUCTION CONFIG ---
from config import Config
Config.validate_production()

# --- RUN THE APP ---
if __name__ == '__main__':
    print("🚀 STARTING SMARTWASTE360 API v6.0.0")
    app.run(debug=os.getenv('FLASK_DEBUG', '1') == '1', host='0.0.0.0', port=5000)