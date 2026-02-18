// frontend/src/components/common/ProtectedRoute.jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * ProtectedRoute - Guards routes by authentication and optional role check.
 * @param {string[]} allowedRoles - If provided, only these roles can access the route.
 *   Unauthorized roles are redirected to their own dashboard.
 */
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Role-based access control
  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    // Redirect to the user's own dashboard based on their role
    const redirectMap = {
      admin: '/admin/dashboard',
      collector: '/collector/dashboard',
      user: '/dashboard',
    };
    const redirect = redirectMap[user?.role] || '/dashboard';
    return <Navigate to={redirect} replace />;
  }

  return children ? children : <Outlet />;
};

export default ProtectedRoute;
