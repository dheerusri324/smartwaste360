// frontend/src/components/layout/AuthLayout.jsx

import React from 'react';
import { Link } from 'react-router-dom';
import customLogo from '../../assets/images/icons/logo.png'; // Make sure this path is correct

const AuthLayout = ({ children }) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link to="/" className="inline-block">
            <img className="h-12 w-auto" src={customLogo} alt="SmartWaste360 Logo" />
          </Link>
        </div>
        <div className="bg-white p-8 rounded-xl shadow-lg">
          {/* The Login or Register form will be rendered here */}
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;