// frontend/src/components/dashboard/WasteHistory.jsx

import React, { useState, useEffect } from 'react';
import { getWasteHistory } from '../../services/waste';
import { formatDate } from '../../utils/helpers';

const WasteHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        // Fetch only the 5 most recent items for the dashboard
        const response = await getWasteHistory(1, 5);
        setHistory(response.logs || []);
      } catch (error) {
        console.error("Error fetching history");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) {
    return <div className="bg-white p-6 rounded-lg shadow-md h-96 animate-pulse"></div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Activity</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight (kg)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {history.length > 0 ? (
              history.map(log => (
                <tr key={log.log_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(log.created_at)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">{log.predicted_category}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{parseFloat(log.weight_kg).toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-emerald-600">+{log.points_earned}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                  No activity yet. Use the camera to scan some waste!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default WasteHistory;