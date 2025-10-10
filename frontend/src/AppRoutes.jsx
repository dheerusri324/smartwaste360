// frontend/src/AppRoutes.jsx

import React from 'react';
import { Routes, Route, Outlet } from 'react-router-dom';

// Import Layouts
import { MainLayout, AuthLayout, DashboardLayout } from './components/layout';
import ProtectedRoute from './components/common/ProtectedRoute';

// Import Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Camera from './pages/Camera';
import Maps from './pages/Maps';
import Leaderboard from './pages/Leaderboard';
import NotFound from './pages/NotFound';
import StatsPage from './pages/StatsPage';
import WasteHistoryPage from './pages/WasteHistoryPage';
import SettingsPage from './pages/SettingsPage';
import CollectorLogin from './pages/CollectorLogin';
import CollectorDashboard from './pages/CollectorDashboard';
import CollectorSettings from './pages/CollectorSettings';
import PickupScheduler from './pages/PickupScheduler';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import LoginSelector from './components/common/LoginSelector';

const AppRoutes = () => (
  <Routes>
    {/* Login Selector */}
    <Route path="/login-selector" element={<LoginSelector />} />

    {/* Routes for Authentication (uses AuthLayout) */}
    <Route element={<AuthLayout><Outlet /></AuthLayout>}>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/collector/login" element={<CollectorLogin />} />
      <Route path="/admin/login" element={<AdminLogin />} />
    </Route>

    {/* Protected Routes for the User Dashboard (uses DashboardLayout) */}
    <Route element={<ProtectedRoute><DashboardLayout><Outlet /></DashboardLayout></ProtectedRoute>}>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/dashboard/stats" element={<StatsPage />} />
      <Route path="/dashboard/history" element={<WasteHistoryPage />} />
      <Route path="/dashboard/settings" element={<SettingsPage />} />
    </Route>
    
    {/* All Other Routes (uses MainLayout) */}
    <Route element={<MainLayout><Outlet /></MainLayout>}>
      <Route path="/" element={<Home />} />
      <Route path="/maps" element={<Maps />} />
      <Route path="/leaderboard" element={<Leaderboard />} />
      
      {/* Protected routes that use the MainLayout */}
      <Route path="/camera" element={<ProtectedRoute><Camera /></ProtectedRoute>} />
      <Route path="/collector/dashboard" element={<ProtectedRoute><CollectorDashboard /></ProtectedRoute>} />
      <Route path="/collector/settings" element={<ProtectedRoute><CollectorSettings /></ProtectedRoute>} />
      <Route path="/collector/scheduler" element={<ProtectedRoute><PickupScheduler /></ProtectedRoute>} />
      <Route path="/collector/analytics" element={<ProtectedRoute><AnalyticsDashboard /></ProtectedRoute>} />
      <Route path="/admin/dashboard" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />

      {/* This is the catch-all route for pages that don't exist */}
      <Route path="*" element={<NotFound />} />
    </Route>
  </Routes>
);

export default AppRoutes;