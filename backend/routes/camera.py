# backend/routes/camera.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import uuid
import os
import traceback
from services.ml_service import MLService # <-- CORRECTED IMPORT
from services.points_service import PointsService # <-- CORRECTED IMPORT
from models.waste import WasteLog # <-- CORRECTED IMPORT
from models.user import User # <-- CORRECTED IMPORT
from models.colony import Colony # <-- CORRECTED IMPORT

bp = Blueprint('camera', __name__)

# Initialize services once
ml_service = MLService()
points_service = PointsService()

@bp.route('/capture', methods=['POST'])
@jwt_required()
def capture_image():
    """Handle image capture, classification, and logging with user-provided weight."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 1. Validate incoming data
        image_data = data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # --- GET WEIGHT FROM REQUEST (with a default fallback) ---
        weight = float(data.get('weight', 1.0))
        
        waste_type = data.get('waste_type', 'dry')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # 2. Decode and save the image file
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        filename = f"{uuid.uuid4()}.jpg"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # 3. Call services with the user-provided weight
        result = ml_service.classify_waste(filepath, weight, waste_type)
        points_earned = points_service.calculate_points(result['predicted_category'], weight)
        co2_saved = points_service.get_co_2_savings(result['predicted_category'], weight)
        
        # 4. Log the complete data to the database
        log_id = WasteLog.create_waste_log(
            user_id, filepath, result['predicted_category'], result['confidence'],
            weight, result['waste_type'], points_earned, latitude, longitude,
            result['recyclable'], co2_saved
        )
        
        User.update_user_points(user_id, points_earned, weight)
        
        # Colony points will be updated automatically by the database trigger
        # when the waste log is inserted, so no manual update needed
        
        # 5. Send complete success response to the frontend
        return jsonify({
            'classification': result,
            'points_earned': points_earned,
            'co2_saved': co2_saved,
            'log_id': log_id,
            'message': 'Waste classified successfully'
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f"An internal server error occurred: {e}"}), 500