// frontend/src/pages/Dashboard.jsx

import React from 'react';
import { useAuth } from '../context/AuthContext';
import UserStats from '../components/dashboard/UserStats';
import WasteHistory from '../components/dashboard/WasteHistory';
import QuickActions from '../components/dashboard/QuickActions'; // A new component for navigation
import AchievementBadges from '../components/leaderboard/AchievementBadges';
import { getUserAchievements } from '../services/advanced';

const Dashboard = () => {
  const { user } = useAuth();
  const [achievements, setAchievements] = React.useState([]);
  const [loadingAchievements, setLoadingAchievements] = React.useState(true);

  React.useEffect(() => {
    const userId = user?.id || user?.user_id || user?.admin_id;
    if (userId) {
      getUserAchievements(userId)
        .then(data => setAchievements(data.achievements || []))
        .catch(err => console.error('Failed to load achievements:', err))
        .finally(() => setLoadingAchievements(false));
    } else {
      setLoadingAchievements(false);
    }
  }, [user]);

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

      {/* Achievement Badges */}
      <AchievementBadges achievements={achievements} loading={loadingAchievements} />

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