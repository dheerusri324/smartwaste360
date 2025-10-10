// frontend/src/components/camera/ClassificationResult.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { CheckCircle, Recycle, Leaf } from 'lucide-react';

const ClassificationResult = ({ result, onDone }) => {
  // --- THIS IS THE FIX ---
  // We provide default values to prevent crashes if the 'result' prop is incomplete.
  // We use optional chaining (?.) and nullish coalescing (??) for safety.
  const { classification = {}, points_earned = 0, co2_saved = 0 } = result || {};
  const confidencePercent = (classification.confidence * 100)?.toFixed(1);

  return (
    <div className="w-full max-w-md p-6 bg-white rounded-2xl shadow-xl text-center animate-fadeInUp">
      <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
      <h2 className="text-3xl font-bold text-gray-800 capitalize">
        {classification.predicted_category || 'Unknown'}
      </h2>
      
      {/* Only show confidence if it exists */}
      {confidencePercent && (
        <p className="text-gray-500 mb-6">
          Confidence: {confidencePercent}%
        </p>
      )}

      <div className="grid grid-cols-2 gap-4 my-6 text-left">
        <div className="p-4 bg-emerald-50 rounded-lg">
          <p className="text-sm text-emerald-700 font-semibold">Points Earned</p>
          <p className="text-2xl font-bold text-emerald-900">{points_earned}</p>
        </div>
        <div className="p-4 bg-emerald-50 rounded-lg">
          <p className="text-sm text-emerald-700 font-semibold">CO₂ Saved</p>
          <p className="text-2xl font-bold text-emerald-900">
            {co2_saved?.toFixed(2) ?? '0.00'} kg
          </p>
        </div>
      </div>
      
      {classification.recyclable ? (
        <p className="flex items-center justify-center gap-2 text-blue-600 font-medium my-4">
          <Recycle size={20} /> This item is recyclable!
        </p>
      ) : (
        <p className="flex items-center justify-center gap-2 text-amber-700 font-medium my-4">
          <Leaf size={20} /> This item is organic waste.
        </p>
      )}

      <button
        onClick={onDone}
        className="w-full mt-4 px-8 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700"
      >
        Scan Another Item
      </button>
    </div>
  );
};

ClassificationResult.propTypes = {
  result: PropTypes.object.isRequired,
  onDone: PropTypes.func.isRequired,
};

export default ClassificationResult;