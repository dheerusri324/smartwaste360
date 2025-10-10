// frontend/src/components/collector/CollectionCompletionModal.jsx
import React, { useState } from 'react';
import { completeCollection } from '../../services/collector';
import { CheckCircle, Package, Scale, X } from 'lucide-react';

const CollectionCompletionModal = ({ booking, isOpen, onClose, onComplete }) => {
  const [collectionData, setCollectionData] = useState({
    total_weight_collected: '',
    waste_types_collected: [],
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const wasteTypes = [
    { value: 'plastic', label: 'Plastic', color: 'bg-blue-100 text-blue-800' },
    { value: 'paper', label: 'Paper', color: 'bg-green-100 text-green-800' },
    { value: 'metal', label: 'Metal', color: 'bg-gray-100 text-gray-800' },
    { value: 'glass', label: 'Glass', color: 'bg-purple-100 text-purple-800' },
    { value: 'textile', label: 'Textile', color: 'bg-pink-100 text-pink-800' },
    { value: 'organic', label: 'Organic', color: 'bg-yellow-100 text-yellow-800' }
  ];

  const handleWasteTypeToggle = (wasteType) => {
    setCollectionData(prev => ({
      ...prev,
      waste_types_collected: prev.waste_types_collected.includes(wasteType)
        ? prev.waste_types_collected.filter(type => type !== wasteType)
        : [...prev.waste_types_collected, wasteType]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!collectionData.total_weight_collected || collectionData.waste_types_collected.length === 0) {
      setError('Please enter weight and select at least one waste type');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      await completeCollection(booking.booking_id, {
        ...collectionData,
        total_weight_collected: parseFloat(collectionData.total_weight_collected)
      });
      
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
          {/* Weight Collected */}
          <div>
            <label htmlFor="weight" className="form-label flex items-center gap-2">
              <Scale size={16} />
              Total Weight Collected (kg)
            </label>
            <input
              id="weight"
              type="number"
              step="0.1"
              min="0"
              value={collectionData.total_weight_collected}
              onChange={(e) => setCollectionData(prev => ({ ...prev, total_weight_collected: e.target.value }))}
              className="form-input"
              placeholder="Enter total weight in kg"
              required
            />
          </div>

          {/* Waste Types Collected */}
          <div>
            <label className="form-label flex items-center gap-2">
              <Package size={16} />
              Waste Types Collected
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
              {wasteTypes.map(type => (
                <label key={type.value} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={collectionData.waste_types_collected.includes(type.value)}
                    onChange={() => handleWasteTypeToggle(type.value)}
                    className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                  />
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${type.color}`}>
                    {type.label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="form-label">Notes (Optional)</label>
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