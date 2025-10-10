// frontend/src/components/common/Navbar.jsx

import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { FaUserCircle, FaCamera } from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';
import customLogo from '../../assets/images/icons/logo.png';

const Navbar = () => {
  const { isAuthenticated, user, logoutAction } = useAuth();

  // --- THIS IS THE FIX ---
  // Determine the correct dashboard path based on the user's role.
  const getDashboardPath = () => {
    if (user?.role === 'collector') return '/collector/dashboard';
    if (user?.role === 'admin') return '/admin/dashboard';
    return '/dashboard'; // Default for regular users
  };
  
  const dashboardPath = getDashboardPath();

  const navLinkClass = ({ isActive }) => `px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-emerald-700 text-white' : 'text-gray-300 hover:bg-emerald-600'}`;

  return (
    <nav className="bg-emerald-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center text-white">
              <img className="h-10 w-auto" src={customLogo} alt="Logo" />
              <span className="ml-2 text-xl font-bold">SmartWaste360</span>
            </Link>
            <div className="hidden md:block ml-10 flex items-baseline space-x-4">
              {/* The NavLink now uses the dynamic dashboardPath */}
              {isAuthenticated && <NavLink to={dashboardPath} className={navLinkClass}>Dashboard</NavLink>}
              <NavLink to="/maps" className={navLinkClass}>Map</NavLink>
              <NavLink to="/leaderboard" className={navLinkClass}>Leaderboard</NavLink>
              {/* Collector-specific links */}
              {isAuthenticated && user?.role === 'collector' && (
                <>
                  <NavLink to="/collector/scheduler" className={navLinkClass}>Scheduler</NavLink>
                  <NavLink to="/collector/analytics" className={navLinkClass}>Analytics</NavLink>
                  <NavLink to="/collector/settings" className={navLinkClass}>Settings</NavLink>
                </>
              )}
            </div>
          </div>
          
          <div className="flex items-center">
            {/* The camera button is only for regular users, not collectors */}
            {isAuthenticated && user?.role === 'user' && (
              <NavLink to="/camera" className="hidden md:flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-full hover:bg-emerald-500 mx-4">
                <FaCamera className="h-5 w-5" />
                <span className="font-semibold">Scan Waste</span>
              </NavLink>
            )}
            <div className="hidden md:block">
              {isAuthenticated ? (
                <div className="ml-4 flex items-center space-x-4">
                  <span className="text-white flex items-center">
                    <FaUserCircle className="mr-2 h-6 w-6"/> {user?.name || user?.full_name || 'Profile'}
                  </span>
                  <button onClick={logoutAction} className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-red-600">
                    Logout
                  </button>
                </div>
              ) : (
                <div className="space-x-2">
                  <Link to="/login-selector" className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-emerald-600">Login</Link>
                  <Link to="/register" className="px-3 py-2 rounded-md text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-500">Register</Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;