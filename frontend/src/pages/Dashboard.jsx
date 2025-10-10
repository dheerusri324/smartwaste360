// frontend/src/pages/Dashboard.jsx

import React from 'react';
import { useAuth } from '../context/AuthContext';
import UserStats from '../components/dashboard/UserStats';
import WasteHistory from '../components/dashboard/WasteHistory';
import QuickActions from '../components/dashboard/QuickActions'; // A new component for navigation

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">
          Welcome back, {user?.full_name || 'User'}!
        </h1>
        <p className="mt-1 text-gray-600">Here's a summary of your recycling efforts and contribution.</p>
      </div>
      
      {/* Dynamic Stats Cards */}
      <UserStats />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Dynamic History Table */}
        <div className="lg:col-span-2">
          <WasteHistory />
        </div>
        
        {/* Quick Actions Component */}
        <div>
          <QuickActions />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;