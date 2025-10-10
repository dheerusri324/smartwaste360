// src/components/common/LoadingSpinner.jsx

import React from 'react';
import PropTypes from 'prop-types';

const LoadingSpinner = ({ size = '8', color = 'emerald-500' }) => {
  const sizeClasses = {
    '4': 'h-4 w-4',
    '6': 'h-6 w-6',
    '8': 'h-8 w-8',
    '12': 'h-12 w-12',
    '16': 'h-16 w-16',
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={`animate-spin rounded-full ${sizeClasses[size]} border-t-2 border-b-2 border-${color}`}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
};

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['4', '6', '8', '12', '16']),
  color: PropTypes.string,
};

export default LoadingSpinner;