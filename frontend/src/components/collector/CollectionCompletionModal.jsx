// frontend/src/components/collector/CollectionCompletionModal.jsx
import React, { useState } from 'react';
import { completeCollection } from '../../services/collector';
import { CheckCircle, Scale, X } from 'lucide-react';

const CollectionCompletionModal = ({ booking, isOpen, onClose, onComplete }) => {
  const [collectionData, setCollectionData] = useState({
    notes: '',
    actual_weight_collected: '' // Optional: only if different from estimated
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);
    setError('');
    
    try {
      const completionData = {
        notes: collectionData.notes
      };
      
      // Only include actual weight if provided and different from estimated
      if (collectionData.actual_weight_collected && collectionData.actual_weight_collected.trim() !== '') {
        completionData.actual_weight_collected = parseFloat(collectionData.actual_weight_collected);
      }
      
      await completeCollection(booking.booking_id, completionData);
      
      onComplete();
      onClose();
      
      // Reset form
      setCollectionData({
        total_weight_collected: '',
        waste_types_collected: [],
        notes: ''
      });
    } catch (err) {
      setError('Failed to complete collection. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !booking) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <CheckCircle className="text-emerald-600" />
            Complete Collection
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800">{booking.colony_name}</h3>
          <p className="text-sm text-gray-600">
            Scheduled: {new Date(booking.booking_date).toLocaleDateString()} at {booking.time_slot}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Booking Summary */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">Collection Summary</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>Colony:</strong> {booking?.colony_name || 'Unknown'}</p>
              <p><strong>Date:</strong> {booking?.booking_date}</p>
              <p><strong>Time:</strong> {booking?.time_slot}</p>
              <p className="text-xs text-gray-500 mt-2">
                Materials and estimated weight are pre-defined from your booking.
              </p>
            </div>
          </div>

          {/* Optional: Actual Weight if Different */}
          <div>
            <label htmlFor="actual_weight" className="form-label flex items-center gap-2">
              <Scale size={16} />
              Actual Weight Collected (Optional)
            </label>
            <input
              id="actual_weight"
              type="number"
              step="0.1"
              min="0"
              value={collectionData.actual_weight_collected}
              onChange={(e) => setCollectionData(prev => ({ ...prev, actual_weight_collected: e.target.value }))}
              className="form-input"
              placeholder="Only if different from estimated weight"
            />
            <p className="text-xs text-gray-500 mt-1">
              Leave empty to use the estimated weight from your booking
            </p>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="form-label">Collection Notes</label>
            <textarea
              id="notes"
              value={collectionData.notes}
              onChange={(e) => setCollectionData(prev => ({ ...prev, notes: e.target.value }))}
              className="form-input"
              rows="3"
              placeholder="Any additional notes about the collection..."
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center gap-2"
            >
              <CheckCircle size={16} />
              {loading ? 'Completing...' : 'Complete Collection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CollectionCompletionModal;