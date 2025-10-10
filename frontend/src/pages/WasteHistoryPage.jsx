// frontend/src/pages/WasteHistoryPage.jsx

import React, { useState, useEffect } from 'react';
import { getWasteHistory } from '../services/waste';
import { formatDate } from '../utils/helpers';
import LoadingSpinner from '../components/common/LoadingSpinner';

const WasteHistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async (currentPage) => {
      setLoading(true);
      try {
        const response = await getWasteHistory(currentPage, 10); // Fetch 10 items per page
        setHistory(prevHistory => currentPage === 1 ? response.logs : [...prevHistory, ...response.logs]);
        setTotalPages(response.total_pages);
      } catch (error) {
        console.error("Error fetching history");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory(page);
  }, [page]);

  const loadMore = () => {
    if (page < totalPages) {
      setPage(prevPage => prevPage + 1);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">My Waste History</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Weight (kg)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {history.map(log => (
              <tr key={log.log_id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(log.created_at)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium capitalize">{log.predicted_category}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{parseFloat(log.weight_kg).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-emerald-600">+{log.points_earned}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {loading && <div className="text-center p-4"><LoadingSpinner /></div>}
        {page < totalPages && !loading && (
          <div className="text-center mt-6">
            <button onClick={loadMore} className="btn-secondary">Load More</button>
          </div>
        )}
        {history.length === 0 && !loading && (
            <p className="text-center p-6 text-gray-500">You haven't scanned any waste yet.</p>
        )}
      </div>
    </div>
  );
};

export default WasteHistoryPage;