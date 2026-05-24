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

  // Static fallback achievements - shown if API fails
  const FALLBACK_ACHIEVEMENTS = [
    { id: 'first_scan', name: 'First Steps', description: 'Classify your first waste item', category: 'recycling', earned: false, progress: { current: 0, target: 1 } },
    { id: 'eco_warrior', name: 'Eco Warrior', description: 'Classify 100 waste items', category: 'recycling', earned: false, progress: { current: 0, target: 100 } },
    { id: 'recycling_champion', name: 'Recycling Champion', description: 'Help your colony reach collection threshold', category: 'community', earned: false, progress: { current: 0, target: 1 } },
    { id: 'green_streak', name: 'Green Streak', description: 'Classify waste for 7 consecutive days', category: 'streak', earned: false, progress: { current: 0, target: 7 } },
    { id: 'plastic_hunter', name: 'Plastic Hunter', description: 'Classify 50 plastic items', category: 'recycling', earned: false, progress: { current: 0, target: 50 } },
    { id: 'weight_master', name: 'Weight Master', description: 'Process 100kg of waste', category: 'collection', earned: false, progress: { current: 0, target: 100 } },
    { id: 'community_leader', name: 'Community Leader', description: 'Be in top 3 of your colony leaderboard', category: 'community', earned: false, progress: { current: 0, target: 3 } },
  ];

  React.useEffect(() => {
    const userId = user?.id || user?.user_id || user?.admin_id;
    if (userId) {
      getUserAchievements(userId)
        .then(data => {
          const ach = data?.achievements;
          setAchievements(ach && ach.length > 0 ? ach : FALLBACK_ACHIEVEMENTS);
        })
        .catch(err => {
          console.error('Failed to load achievements:', err);
          setAchievements(FALLBACK_ACHIEVEMENTS);
        })
        .finally(() => setLoadingAchievements(false));
    } else {
      setAchievements(FALLBACK_ACHIEVEMENTS);
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