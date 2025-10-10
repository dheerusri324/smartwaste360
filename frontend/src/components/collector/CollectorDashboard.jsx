import React, { useState, useEffect } from 'react';
import { Calendar, DollarSign, Package, CheckCircle, AlertCircle, Users } from 'lucide-react';
import api from '../../services/api';

const CollectorDashboard = () => {
  const [stats, setStats] = useState({
    total_collections: 0,
    pending_requests: 0,
    total_earnings: 0,
    completed_today: 0,
    total_users: 0
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const statsResponse = await api.get('/api/collector/dashboard');
        setStats(statsResponse.data);
        
        const activitiesResponse = await api.get('/api/collector/recent-activities');
        setRecentActivities(activitiesResponse.data.activities || []);
        
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err.response?.data?.error || 'Failed to fetch dashboard data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  const statCards = [
    { icon: Package, label: 'Total Collections', value: stats.total_collections, id: 'collections' },
    { icon: Calendar, label: 'Pending Requests', value: stats.pending_requests, id: 'pending' },
    { icon: DollarSign, label: 'Total Earnings', value: `₹${stats.total_earnings}`, id: 'earnings' },
    { icon: CheckCircle, label: 'Completed Today', value: stats.completed_today, id: 'completed' },
    { icon: Users, label: 'Total Users', value: stats.total_users, id: 'users' }
  ];

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded flex items-center">
          <AlertCircle className="mr-2" />
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Collector Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {statCards.map((card) => (
          <div key={card.id} className="bg-white rounded-lg p-6 shadow-md">
            <card.icon className="w-8 h-8 text-green-600 mb-2" />
            <h3 className="text-lg font-semibold text-gray-700">{card.label}</h3>
            <p className="text-2xl font-bold text-gray-900">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold mb-4">Recent Activities</h2>
          {recentActivities.length > 0 ? (
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div 
                  key={activity.id || `${activity.user_id}-${activity.pickup_time}`} 
                  className="border-b border-gray-200 pb-3 last:border-0"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{activity.user_name}</p>
                      <p className="text-sm text-gray-600">{activity.colony_name}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusClass(activity.status)}`}>
                      {activity.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(activity.pickup_time).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No recent activities</p>
          )}
        </div>

        <div className="bg-white rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 text-left flex items-center">
              <Package className="mr-2 h-5 w-5" />
              View Today's Schedule
            </button>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 text-left flex items-center">
              <DollarSign className="mr-2 h-5 w-5" />
              Record Transaction
            </button>
            <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 text-left flex items-center">
              <Users className="mr-2 h-5 w-5" />
              Manage Collections
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollectorDashboard;