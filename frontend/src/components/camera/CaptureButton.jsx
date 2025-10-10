// frontend/src/components/camera/CaptureButton.jsx

import React from 'react';
import PropTypes from 'prop-types';

const CaptureButton = ({ onClick }) => {
  return (
    <button 
      onClick={onClick} 
      className="w-20 h-20 bg-white rounded-full border-4 border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-4 focus:ring-offset-black focus:ring-white transition-transform duration-200 active:scale-90"
      aria-label="Capture image"
    />
  );
};

CaptureButton.propTypes = {
  onClick: PropTypes.func.isRequired,
};

export default CaptureButton;