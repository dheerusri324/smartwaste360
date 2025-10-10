// frontend/src/components/dashboard/UserStats.jsx

import React, { useState, useEffect } from 'react';
import { getWasteStats } from '../../services/waste';
// --- THIS IS THE FIX: Replaced 'Weight' with 'Dumbbell' ---
import { Star, Dumbbell, Recycle, Leaf } from 'lucide-react';

// A small, reusable card component for displaying a single stat
const StatCard = ({ icon, label, value, unit, colorClass }) => (
  <div className="bg-white p-6 rounded-lg shadow-md flex items-center">
    <div className={`rounded-full p-3 mr-4 ${colorClass}`}>
      {icon}
    </div>
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-800">
        {value} <span className="text-base font-normal text-gray-600">{unit}</span>
      </p>
    </div>
  </div>
);

const UserStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getWasteStats();
        setStats(response.stats);
      } catch (error) {
        console.error("Error fetching stats");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    // Basic loading skeleton
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 animate-pulse">
        {[...Array(4)].map((_, i) => <div key={i} className="h-28 bg-gray-200 rounded-lg"></div>)}
      </div>
    );
  }
  
  if (!stats) {
    return <div className="text-center text-gray-500 p-4">Could not load your statistics.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard icon={<Star className="text-yellow-600" />} label="Total Points" value={stats.total_points || 0} unit="pts" colorClass="bg-yellow-100" />
      {/* --- THIS IS THE FIX: Using the correct Dumbbell icon --- */}
      <StatCard icon={<Dumbbell className="text-blue-600" />} label="Total Weight Recycled" value={parseFloat(stats.total_weight || 0).toFixed(2)} unit="kg" colorClass="bg-blue-100" />
      <StatCard icon={<Recycle className="text-green-600" />} label="Recyclable Weight" value={parseFloat(stats.recyclable_weight || 0).toFixed(2)} unit="kg" colorClass="bg-green-100" />
      <StatCard icon={<Leaf className="text-lime-600" />} label="CO₂ Saved" value={parseFloat(stats.total_co2_saved || 0).toFixed(2)} unit="kg" colorClass="bg-lime-100" />
    </div>
  );
};

export default UserStats;