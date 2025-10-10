// frontend/src/components/common/LoginSelector.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { User, Truck, Shield } from 'lucide-react';

const LoginSelector = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Welcome to SmartWaste360
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Choose your login type to continue
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* User Login */}
          <Link
            to="/login"
            className="group relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-emerald-500"
          >
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-emerald-600 rounded-full flex items-center justify-center group-hover:bg-emerald-700 transition-colors">
                <User className="h-8 w-8 text-white" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900">User Login</h3>
              <p className="mt-2 text-sm text-gray-600">
                For residents and citizens to classify waste and track their environmental impact
              </p>
              <div className="mt-4 text-emerald-600 font-medium group-hover:text-emerald-700">
                Login as User →
              </div>
            </div>
          </Link>

          {/* Collector Login */}
          <Link
            to="/collector/login"
            className="group relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-blue-500"
          >
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center group-hover:bg-blue-700 transition-colors">
                <Truck className="h-8 w-8 text-white" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900">Collector Login</h3>
              <p className="mt-2 text-sm text-gray-600">
                For waste collectors to manage schedules, routes, and collection activities
              </p>
              <div className="mt-4 text-blue-600 font-medium group-hover:text-blue-700">
                Login as Collector →
              </div>
            </div>
          </Link>

          {/* Admin Login */}
          <Link
            to="/admin/login"
            className="group relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-purple-500"
          >
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-purple-600 rounded-full flex items-center justify-center group-hover:bg-purple-700 transition-colors">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900">Admin Login</h3>
              <p className="mt-2 text-sm text-gray-600">
                For system administrators to manage the platform and monitor operations
              </p>
              <div className="mt-4 text-purple-600 font-medium group-hover:text-purple-700">
                Login as Admin →
              </div>
            </div>
          </Link>
        </div>

        {/* Test Credentials */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Test Credentials</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <h5 className="font-medium text-emerald-600">User Accounts</h5>
              <p>Email: john@example.com</p>
              <p>Password: password123</p>
            </div>
            <div>
              <h5 className="font-medium text-blue-600">Collector Accounts</h5>
              <p>Email: paper@gmail.com</p>
              <p>Password: password123</p>
            </div>
            <div>
              <h5 className="font-medium text-purple-600">Admin Account</h5>
              <p>Email: admin@smartwaste360.com</p>
              <p>Password: password123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginSelector;