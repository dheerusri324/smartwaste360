// frontend/src/pages/Leaderboard.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getColonyLeaderboard, getCollectorLeaderboard } from '../services/leaderboard'; // Use a dedicated service
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Trophy } from 'lucide-react';

const Leaderboard = () => {
  const { user } = useAuth();
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isCollector = user?.role === 'collector';

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        let data;
        if (isCollector) {
          data = await getCollectorLeaderboard();
        } else {
          data = await getColonyLeaderboard();
        }
        setLeaderboardData(data.leaderboard || []);
      } catch (err) {
        setError('Failed to load leaderboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [isCollector]); // Refetch if the user role changes

  if (loading) return <div className="flex justify-center mt-16"><LoadingSpinner /></div>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  const title = isCollector ? "National Collector Rankings" : "Top Colony Rankings";
  const subtitle = isCollector ? "Ranked by total weight collected" : "Ranked by total points earned";

  return (
    <div className="container mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800">{title}</h1>
        <p className="text-gray-600">{subtitle}</p>
      </div>
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <ul className="space-y-4">
          {leaderboardData.map((item, index) => (
            <li key={item.colony_id || item.collector_id} className="flex items-center p-4 border rounded-md">
              <div className="text-2xl font-bold w-12 text-center">
                {index < 3 ? <Trophy className={`w-8 h-8 ${index === 0 ? 'text-yellow-400' : index === 1 ? 'text-gray-400' : 'text-yellow-600'}`} /> : `#${index + 1}`}
              </div>
              <div className="flex-1">
                <p className="font-bold text-lg text-gray-900">{item.colony_name || item.name}</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-emerald-600">
                  {isCollector ? `${parseFloat(item.total_weight_collected).toFixed(2)} kg` : `${item.total_points} pts`}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Leaderboard;