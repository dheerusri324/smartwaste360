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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-super-secret-key-for-dev')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'a-super-secret-jwt-key-for-dev')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'backend/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- INITIALIZE EXTENSIONS ---

# 👇 2. INITIALIZE CORS AND ALLOW YOUR REACT APP'S ORIGIN 👇
# Simplified CORS setup for immediate fix
CORS(app, 
     origins=["*"],  # Allow all origins temporarily for debugging
     supports_credentials=False,  # Must be False when using "*"
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

jwt = JWTManager(app)

# --- CREATE DIRECTORIES ---
def create_directories():
    directories = ['backend/uploads', 'backend/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

create_directories()

# --- IMPORT & REGISTER BLUEPRINTS (ROUTES) ---
from routes import auth, waste, booking, leaderboard, camera, collector, transaction, health, colony, collection_points, admin, analytics

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

# Advanced features temporarily disabled for debugging
# app.register_blueprint(advanced_features.bp, url_prefix='/api/advanced')

# --- ROOT ROUTE ---
@app.route('/')
def home():
    return jsonify({
        'message': 'SmartWaste360 API is alive!',
        'version': '1.0.1',
        'status': 'production',
        'deployment': 'auto-deployed from GitHub',
        'timestamp': '2025-10-11',
        'cors_enabled': True
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'cors_origins': 'all_origins_allowed',
        'timestamp': '2025-10-11',
        'version': '1.0.2'
    })

# --- RUN THE APP ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)