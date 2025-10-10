import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '9Kav+QSIYrPNr5HzOyHumTLief4bL/tq/hZ9rXrv2qsnOEWChVOXDtn3itAaizUba6KpZ6fUpvgo6PRez8qiBw==')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'yWpOapJ/6SVTxf8SaHukTm2xWkbxSO6/sY+It/T7wJ3OCVUBJfHYHSjT27L3JAaAHo5+WmKCyMX1jsmqprhZaw==')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours in seconds
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'smartwaste360')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'dheerusri')
    
    # File upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # ML Model
    MODEL_PATH = os.getenv('MODEL_PATH', 'ml-model/mobilenet_waste_classifier.h5')
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'

# In your app.py or config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = 'backend/logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            RotatingFileHandler(
                os.path.join(log_dir, 'smartwaste360.log'),
                maxBytes=10000000,  # 10MB
                backupCount=10
            ),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Initialize logging
logger = setup_logging()