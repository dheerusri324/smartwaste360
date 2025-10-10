// src/components/common/Notification.jsx

import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { FaCheckCircle, FaExclamationCircle, FaInfoCircle, FaTimes } from 'react-icons/fa';

const notificationConfig = {
  success: {
    icon: <FaCheckCircle />,
    style: 'bg-green-100 border-green-400 text-green-700',
  },
  error: {
    icon: <FaExclamationCircle />,
    style: 'bg-red-100 border-red-400 text-red-700',
  },
  info: {
    icon: <FaInfoCircle />,
    style: 'bg-blue-100 border-blue-400 text-blue-700',
  },
};

const Notification = ({ message, type = 'info', onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000); // Auto-close after 5 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  if (!message) return null;

  const { icon, style } = notificationConfig[type];

  return (
    <div className={`fixed top-5 right-5 z-50 border-l-4 p-4 rounded-md shadow-lg ${style}`} role="alert">
      <div className="flex items-center">
        <div className="py-1">{icon}</div>
        <div className="ml-3">
          <p className="text-sm font-medium">{message}</p>
        </div>
        <button onClick={onClose} className="ml-auto -mx-1.5 -my-1.5 p-1.5 rounded-full hover:bg-gray-200">
          <FaTimes />
        </button>
      </div>
    </div>
  );
};

Notification.propTypes = {
  message: PropTypes.string,
  type: PropTypes.oneOf(['success', 'error', 'info']),
  onClose: PropTypes.func.isRequired,
};

export default Notification;