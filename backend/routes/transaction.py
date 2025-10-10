# backend/routes/transaction.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.transaction import Transaction
from models.user import User
from models.colony import Colony
from models.collector import Collector
from models.booking import Booking
from services.points_service import PointsService
import json
import traceback

bp = Blueprint('transaction', __name__)

@bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit_waste():
    """
    Records a waste deposit. Must be initiated by a logged-in collector
    on behalf of a specific user.
    """
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Only collectors can record deposits"}), 403
        collector_id = get_jwt_identity()

        data = request.get_json()
        required = ['user_id', 'booking_id', 'weight_deposited', 'materials']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields (user_id, booking_id, weight_deposited, materials)'}), 400
        
        user_id = data['user_id']
        weight = data['weight_deposited']
        
        points_service = PointsService()
        points_earned = points_service.calculate_transaction_points(
            json.dumps(data['materials'])
        )
        
        transaction_id = Transaction.create_transaction(
            user_id=user_id,
            booking_id=data['booking_id'],
            collector_id=collector_id,
            weight_deposited=weight,
            points_earned=points_earned,
            materials=data['materials'],
            verification_code=data.get('verification_code', '')
        )
        
        # Update points for the user and their colony
        User.update_user_points(user_id, points_earned, weight)
        user = User.get_user_by_id(user_id)
        if user and user.get('colony_id'):
            Colony.update_colony_points(user['colony_id'], points_earned)
        
        # Mark the booking as complete
        Collector.update_weight_collected(collector_id, weight)

        Booking.update_booking_status(data['booking_id'], 'completed')
    
        return jsonify({
            'message': 'Deposit recorded successfully',
            'transaction_id': transaction_id,
            'points_earned': points_earned
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_user_transactions():
    """Fetches transaction history for the currently logged-in user."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'user':
            return jsonify({"msg": "Access denied: User token required"}), 403
        user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        result = Transaction.get_user_transactions(user_id, page, limit)

        # Format data for JSON response
        for tx in result.get('transactions', []):
            if tx.get('created_at'):
                tx['created_at'] = tx['created_at'].isoformat()
            if tx.get('materials') and isinstance(tx['materials'], str):
                tx['materials'] = json.loads(tx['materials'])
        
        return jsonify(result), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/collector/history', methods=['GET'])
@jwt_required()
def get_collector_transactions():
    """Fetches transaction history for the currently logged-in collector."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'collector':
            return jsonify({"msg": "Access denied: Collector token required"}), 403
        collector_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        result = Transaction.get_transactions_by_collector(collector_id, page, limit)

        # Format data for JSON response
        for tx in result.get('transactions', []):
            if tx.get('created_at'):
                tx['created_at'] = tx['created_at'].isoformat()
            if tx.get('materials') and isinstance(tx['materials'], str):
                tx['materials'] = json.loads(tx['materials'])
        
        return jsonify(result), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500