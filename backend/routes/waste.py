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

bp = Blueprint('waste', __name__)

ml_service = MLService()
points_service = PointsService()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/classify', methods=['POST'])
@jwt_required()
def classify_waste_route():
    """Handles waste classification from a multipart/form-data request."""
    try:
        identity = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'user':
            return jsonify({"msg": "Only users can classify waste"}), 403
        user_id = identity

        if 'image' not in request.files:
            return jsonify({'error': 'No image file part in request'}), 400
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid or no file selected'}), 400
        
        weight = float(request.form.get('weight', 1.0))
        
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = ml_service.classify_waste(filepath, weight, 'dry')
        points_earned = points_service.calculate_points(result['predicted_category'], weight)
        co2_saved = points_service.get_co_2_savings(result['predicted_category'], weight)
        
        WasteLog.create_waste_log(
            user_id, filepath, result['predicted_category'], result['confidence'],
            weight, 'dry', points_earned, None, None,
            result['recyclable'], co2_saved
        )
        
        User.update_user_points(user_id, points_earned, weight)
        
        # Colony points will be updated automatically by the database trigger
        # when the waste log is inserted, so no manual update needed
        
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