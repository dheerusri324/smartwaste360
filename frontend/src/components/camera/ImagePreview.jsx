// frontend/src/components/camera/ImagePreview.jsx

import React, { useState } from 'react';
import PropTypes from 'prop-types';

const ImagePreview = ({ imageDataUrl, onRetake, onUsePhoto }) => {
  // Add state to manage the weight input
  const [weight, setWeight] = useState('1.0');

  return (
    <div className="w-full max-w-lg flex flex-col items-center justify-center p-4">
      <img src={imageDataUrl} alt="Captured preview" className="w-full h-auto rounded-lg mb-6 shadow-lg" />
      
      {/* --- NEW: Weight Input Field --- */}
      <div className="w-full mb-6">
        <label htmlFor="weight" className="block text-sm font-medium text-white mb-2">
          Estimated Weight (kg)
        </label>
        <input
          type="number"
          id="weight"
          name="weight"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          step="0.1"
          min="0.1"
          required
          className="w-full px-3 py-2 text-gray-800 bg-gray-100 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>
      
      <div className="flex gap-x-6">
        <button 
          onClick={onRetake} 
          className="px-8 py-3 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700"
        >
          Retake
        </button>
        <button 
          // Pass the current weight when the button is clicked
          onClick={() => onUsePhoto(parseFloat(weight))} 
          className="px-8 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700"
        >
          Use Photo
        </button>
      </div>
    </div>
  );
};

ImagePreview.propTypes = {
  imageDataUrl: PropTypes.string.isRequired,
  onRetake: PropTypes.func.isRequired,
  onUsePhoto: PropTypes.func.isRequired,
};

export default ImagePreview;