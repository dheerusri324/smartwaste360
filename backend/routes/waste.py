# backend/routes/waste.py

from flask import Blueprint, request, jsonify, current_app
# --- THIS IS THE FIX: Added 'get_jwt' to the import line ---
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt 
from werkzeug.utils import secure_filename
import os
import uuid
import traceback
from services.ml_service import MLService
from services.points_service import PointsService
from models.waste import WasteLog
from models.user import User
from models.colony import Colony
from utils.log_capture import log_capture

bp = Blueprint('waste', __name__)

ml_service = MLService()
points_service = PointsService()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/test', methods=['GET'])
def test_waste_endpoint():
    """Test endpoint to verify waste routes are accessible"""
    log_capture.add('INFO', 'Waste test endpoint accessed')
    return jsonify({
        'status': 'success',
        'message': 'Waste classification endpoint is reachable',
        'ml_service_active': ml_service.model is not None,
        'version': '5.4.0'
    })

@bp.route('/classify', methods=['POST'])
@jwt_required()
def classify_waste_route():
    """Handles waste classification from a multipart/form-data request."""
    try:
        # Log that request was received
        log_capture.add('INFO', 'Classification request received', 
                       method=request.method, 
                       content_type=request.content_type,
                       origin=request.headers.get('Origin'))
        print(f"[INFO] Classification request received from {request.headers.get('Origin')}")
        
        identity = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'user':
            log_capture.add('WARNING', 'Non-user tried to classify waste', identity=identity, role=claims.get('role'))
            return jsonify({"msg": "Only users can classify waste"}), 403
        user_id = identity
        
        log_capture.add('INFO', f'User {user_id} authenticated for classification', user_id=user_id)

        if 'image' not in request.files:
            return jsonify({'error': 'No image file part in request'}), 400
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid or no file selected'}), 400
        
        weight = float(request.form.get('weight', 1.0))
        waste_type = request.form.get('waste_type', 'dry')  # Get from form, default to 'dry'
        
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Debug logging with capture
        log_capture.add('DEBUG', f"Classifying waste: weight={weight}, waste_type={waste_type}", user_id=user_id)
        print(f"[DEBUG] Classifying waste: weight={weight}, waste_type={waste_type}")
        
        result = ml_service.classify_waste(filepath, weight, waste_type)
        
        log_capture.add('DEBUG', f"ML service result: {result}", user_id=user_id)
        print(f"[DEBUG] ML service result: {result}")
        
        # Debug: Check if result has the expected structure
        if 'predicted_category' not in result:
            log_capture.add('ERROR', f"ML service result missing 'predicted_category': {result}", user_id=user_id)
            print(f"ERROR: ML service result missing 'predicted_category': {result}")
            return jsonify({'error': f'ML service error: missing predicted_category in result: {result}'}), 500
        
        points_earned = points_service.calculate_points(result['predicted_category'], weight)
        co2_saved = points_service.get_co_2_savings(result['predicted_category'], weight)
        
        # Use ML-determined waste_type, not user input
        final_waste_type = result['waste_type']
        
        WasteLog.create_waste_log(
            user_id, filepath, result['predicted_category'], result['confidence'],
            weight, final_waste_type, points_earned, None, None,
            result['recyclable'], co2_saved
        )
        
        User.update_user_points(user_id, points_earned, weight)
        
        # Update colony waste amounts based on predicted category
        log_capture.add('DEBUG', f"Getting user {user_id} to update colony waste", user_id=user_id)
        print(f"[DEBUG] Getting user {user_id} to update colony waste")
        user = User.get_user_by_id(user_id)
        log_capture.add('DEBUG', f"User data: colony_id={user.get('colony_id') if user else None}", user_id=user_id, user_data=user)
        print(f"[DEBUG] User: {user}")
        if user and user.get('colony_id'):
            log_capture.add('DEBUG', f"Calling Colony.add_waste_to_colony({user['colony_id']}, {result['predicted_category']}, {weight})", 
                          user_id=user_id, colony_id=user['colony_id'], category=result['predicted_category'], weight=weight)
            print(f"[DEBUG] Calling Colony.add_waste_to_colony({user['colony_id']}, {result['predicted_category']}, {weight})")
            Colony.add_waste_to_colony(user['colony_id'], result['predicted_category'], weight)
            log_capture.add('INFO', f"Added {weight}kg of {result['predicted_category']} to colony {user['colony_id']}", 
                          user_id=user_id, colony_id=user['colony_id'])
            print(f"[DEBUG] Colony waste update completed")
        else:
            log_capture.add('WARNING', f"User has no colony_id! Cannot update colony waste", user_id=user_id, user_data=user)
            print(f"[DEBUG] User has no colony_id! User data: {user}")
        
        return jsonify({
            'classification': result,
            'points_earned': points_earned,
            'co2_saved': co2_saved,
            'message': 'Waste classified successfully'
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500
@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_waste_stats():
    """Fetches overall waste statistics for the logged-in user."""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'user':
             return jsonify({"msg": "Access denied: User token required"}), 403

        stats = WasteLog.get_waste_stats(user_id)
        
        overall_stats = stats.get('overall', {})
        
        return jsonify({
            'stats': overall_stats,
            'by_category': stats.get('by_category', [])
        }), 200
        
    except Exception as e:
        print(f"ERROR in /stats route: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_waste_history():
    """Fetches the paginated waste classification history for the logged-in user."""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'user':
             return jsonify({"msg": "Access denied: User token required"}), 403

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 5, type=int)
        
        history = WasteLog.get_user_waste_logs(user_id, page, limit)
        
        for log in history.get('logs', []):
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat()

        return jsonify(history), 200
        
    except Exception as e:
        print(f"ERROR in /history route: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred'}), 500