# utils/file_utils.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save an uploaded file with a unique filename"""
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the upload directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the file
        file.save(filepath)
        return filepath
    
    return None

def save_base64_image(image_data, filename_prefix="image"):
    """Save a base64 encoded image to a file"""
    import base64
    from datetime import datetime
    
    try:
        # Extract the base64 data (remove data:image/jpeg;base64, prefix if present)
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode the base64 data
        image_bytes = base64.b64decode(image_data)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the upload directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the file
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return filepath
    except Exception as e:
        print(f"Error saving base64 image: {e}")
        return None

def delete_file(filepath):
    """Delete a file from the filesystem"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file {filepath}: {e}")
    
    return False

def get_file_extension(filename):
    """Get the file extension from a filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def get_file_size(filepath):
    """Get the size of a file in bytes"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def cleanup_old_files(directory, max_age_hours=24):
    """Clean up files older than a specified age"""
    import time
    from datetime import datetime, timedelta
    
    try:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if file_time < cutoff_time:
                    delete_file(filepath)
        
        return True
    except Exception as e:
        print(f"Error cleaning up old files: {e}")
        return False