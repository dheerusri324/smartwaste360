import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECURITY: Use env vars for all secrets. Dev defaults are NOT real credentials.
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-insecure-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-only-insecure-jwt-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours in seconds
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'smartwaste360')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    @staticmethod
    def validate_production():
        """Raise error if critical env vars are missing in production."""
        if os.getenv('FLASK_ENV') == 'production':
            required = ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL']
            missing = [v for v in required if not os.getenv(v)]
            if missing:
                raise RuntimeError(
                    f"SECURITY ERROR: Missing required env vars for production: {missing}. "
                    f"Set them in your hosting platform's environment variables."
                )
    
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