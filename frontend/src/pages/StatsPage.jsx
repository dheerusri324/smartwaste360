// frontend/src/pages/StatsPage.jsx

import React, { useState, useEffect } from 'react';
import { getWasteStats } from '../services/waste';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { WASTE_CATEGORIES } from '../utils/constants'; // Import our color constants
import LoadingSpinner from '../components/common/LoadingSpinner';

const StatsPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getWasteStats();
        setStats(response);
      } catch (err) {
        setError("Failed to load statistics.");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64"><LoadingSpinner /></div>;
  }

  if (error) {
    return <div className="text-center text-red-500">{error}</div>;
  }

  const chartData = stats?.by_category.map(item => ({
    name: item.predicted_category,
    value: parseFloat(item.total_weight)
  })) || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Your Recycling Statistics</h1>
        <p className="mt-1 text-gray-600">A detailed breakdown of your contributions.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Pie Chart for Waste Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Waste Distribution by Weight</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={WASTE_CATEGORIES[entry.name]?.color || '#cccccc'} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value.toFixed(2)} kg`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-gray-500 h-full flex items-center justify-center">No data available for chart.</p>
          )}
        </div>

        {/* Detailed Stats Table */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Breakdown by Category</h3>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Weight (kg)</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Scans</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats?.by_category.map(item => (
                <tr key={item.predicted_category}>
                  <td className="px-4 py-2 font-medium capitalize">{item.predicted_category}</td>
                  <td className="px-4 py-2">{parseFloat(item.total_weight).toFixed(2)}</td>
                  <td className="px-4 py-2">{item.total_points}</td>
                  <td className="px-4 py-2">{item.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StatsPage;