import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, User, AlertCircle, RefreshCw, CheckCircle, XCircle } from 'lucide-react';
import api from '../../services/api';

const ScheduleManager = () => {
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchSchedule();
  }, []);

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/collector/schedule');
      setSchedule(response.data.schedule || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching schedule:', err);
      setError(err.response?.data?.error || 'Failed to fetch schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (id, newStatus) => {
    try {
      await api.patch(`/api/collector/schedule/${id}`, { status: newStatus });
      setSchedule(schedule.map(item => 
        item.booking_id === id ? { ...item, status: newStatus } : item
      ));
    } catch (err) {
      console.error('Error updating status:', err);
      alert(err.response?.data?.error || 'Failed to update status');
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredSchedule = schedule.filter(item => {
    if (filter === 'all') return true;
    return item.status === filter;
  });

  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded flex items-center mb-4">
          <AlertCircle className="mr-2" />
          {error}
        </div>
        <button
          onClick={fetchSchedule}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Schedule Management</h1>
        <div className="flex items-center gap-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-600"
          >
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <button
            onClick={fetchSchedule}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 flex items-center"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>
      
      {filteredSchedule.length === 0 ? (
        <div className="bg-white rounded-lg p-6 shadow-md text-center">
          <p className="text-gray-500">No scheduled pickups found.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredSchedule.map((item) => (
            <div key={item.booking_id} className="bg-white rounded-lg p-4 shadow-md">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">{item.colony_name || 'Unknown Colony'}</h3>
                <span className={`px-3 py-1 rounded-full text-sm ${getStatusClass(item.status)}`}>
                  {item.status}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  {new Date(item.pickup_time).toLocaleString()}
                </div>
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-2" />
                  {item.address || item.colony_name}
                </div>
                <div className="flex items-center">
                  <User className="w-4 h-4 mr-2" />
                  {item.user_name || `User #${item.user_id}`}
                </div>
              </div>

              {item.waste_details && (
                <div className="mb-3">
                  <p className="text-sm font-medium text-gray-700">Waste Details:</p>
                  <p className="text-sm text-gray-600">{item.waste_details}</p>
                </div>
              )}

              {(item.status === 'pending' || item.status === 'confirmed') ? (
                <div className="flex gap-2 mt-4">
                  {item.status === 'pending' && (
                    <button
                      onClick={() => handleStatusUpdate(item.booking_id, 'confirmed')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Confirm
                    </button>
                  )}
                  <button
                    onClick={() => handleStatusUpdate(item.booking_id, 'completed')}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center"
                  >
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Mark Complete
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(item.booking_id, 'cancelled')}
                    className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 flex items-center"
                  >
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancel
                  </button>
                </div>
              ) : (
                <p className="text-sm text-gray-500 mt-2">
                  This pickup has been {item.status}.
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScheduleManager;