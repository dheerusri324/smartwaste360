// frontend/src/pages/AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import { 
  Truck, 
  MapPin, 
  Phone,
  Mail,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  Plus,
  Users,
  Settings
} from 'lucide-react';
import { getAllCollectors, updateCollectorStatus, getAdminOverview } from '../services/admin';
import CollectionPointsManager from '../components/admin/CollectionPointsManager';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('collectors');
  const [collectors, setCollectors] = useState([]);
  const [overviewData, setOverviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const tabs = [
    { id: 'collectors', label: 'Collectors', icon: Truck },
    { id: 'collection-points', label: 'Collection Points', icon: MapPin },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  useEffect(() => {
    loadCollectors();
  }, []);

  const loadCollectors = async () => {
    setLoading(true);
    setError('');
    try {
      console.log('🔄 [ADMIN DASHBOARD v3.0] Loading admin dashboard data...');
      
      // Load both collectors and overview data
      const [collectorsResponse, overviewResponse] = await Promise.all([
        getAllCollectors(),
        getAdminOverview()
      ]);
      
      console.log('📊 Raw collectors response:', collectorsResponse);
      console.log('📊 Raw overview response:', overviewResponse);
      
      setCollectors(collectorsResponse.collectors || []);
      setOverviewData(overviewResponse);
      
      console.log('✅ Loaded collectors from backend:', collectorsResponse.collectors?.length || 0);
      console.log('✅ Loaded overview data:', overviewResponse);
      
    } catch (err) {
      console.error('❌ Dashboard error:', err);
      console.error('❌ Error details:', err.response?.data || err.message);
      setError('Failed to load dashboard data');
      setCollectors([]);
      setOverviewData(null);
    } finally {
      setLoading(false);
    }
  };

  const filteredCollectors = collectors.filter(collector => {
    const matchesSearch = collector.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         collector.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         collector.vehicle_number?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && collector.is_active) ||
                         (statusFilter === 'inactive' && !collector.is_active);
    
    return matchesSearch && matchesStatus;
  });

  const toggleCollectorStatus = async (collectorId) => {
    try {
      // Find the collector to get current status
      const collector = collectors.find(c => c.collector_id === collectorId);
      if (!collector) return;

      const newStatus = !collector.is_active;

      // Update backend first
      await updateCollectorStatus(collectorId, newStatus);

      // Update local state only after successful backend update
      setCollectors(prev => prev.map(c => 
        c.collector_id === collectorId 
          ? { ...c, is_active: newStatus }
          : c
      ));

      console.log(`✅ Collector ${collector.name} ${newStatus ? 'activated' : 'deactivated'} successfully`);
    } catch (error) {
      console.error('❌ Failed to update collector status:', error);
      // Optionally show error message to user
      alert('Failed to update collector status. Please try again.');
    }
  };

  // Removed unused formatDate function

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600">Manage collectors, collection points, and system settings</p>
        </div>
        <button
          onClick={() => {
            console.log('🔄 Manual refresh triggered');
            loadCollectors();
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Settings size={16} />
          Refresh Data
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-emerald-500 text-emerald-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'collectors' && (
        <div className="space-y-6">
          {/* Collectors Header */}
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Collector Management</h2>
              <p className="text-gray-600">Manage waste collectors and their activities</p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700">
              <Plus size={20} />
              Add New Collector
            </button>
          </div>

      {/* Debug Info */}
      {overviewData && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <h3 className="font-semibold text-yellow-800">Debug Info (Remove in production)</h3>
          <p className="text-sm text-yellow-700">
            Collections: {overviewData?.overview?.total_collections_completed || 'undefined'} | 
            Weight: {overviewData?.overview?.total_weight_collected || 'undefined'} | 
            Users: {overviewData?.overview?.total_users || 'undefined'}
          </p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-gray-900">
                {overviewData?.overview?.total_users || 0}
              </p>
            </div>
            <div className="p-3 rounded-full bg-blue-500">
              <Users size={24} className="text-white" />
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Collectors</p>
              <p className="text-3xl font-bold text-gray-900">
                {overviewData?.overview?.total_collectors || collectors.length}
              </p>
            </div>
            <div className="p-3 rounded-full bg-green-500">
              <Truck size={24} className="text-white" />
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Collections Completed</p>
              <p className="text-3xl font-bold text-gray-900">
                {(() => {
                  const value = overviewData?.overview?.total_collections_completed || 0;
                  console.log('📊 Collections completed value:', value, 'from:', overviewData?.overview);
                  return value;
                })()}
              </p>
            </div>
            <div className="p-3 rounded-full bg-emerald-500">
              <CheckCircle size={24} className="text-white" />
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Weight Collected</p>
              <p className="text-3xl font-bold text-gray-900">
                {parseFloat(overviewData?.overview?.total_weight_collected || 0).toFixed(1)} kg
              </p>
            </div>
            <div className="p-3 rounded-full bg-purple-500">
              <MapPin size={24} className="text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search collectors by name, email, or vehicle number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Collectors Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Collectors ({filteredCollectors.length})
          </h3>
        </div>
        
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
          </div>
        ) : error ? (
          <div className="p-6 text-center text-red-600">{error}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Collector Info
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vehicle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Collections
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCollectors.map((collector) => (
                  <tr key={collector.collector_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center">
                            <Truck className="h-5 w-5 text-emerald-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{collector.name}</div>
                          <div className="text-sm text-gray-500">ID: {collector.collector_id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 flex items-center gap-1">
                        <Mail size={14} className="text-gray-400" />
                        {collector.email}
                      </div>
                      <div className="text-sm text-gray-500 flex items-center gap-1">
                        <Phone size={14} className="text-gray-400" />
                        {collector.phone}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{collector.vehicle_number || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{collector.total_collections || 0}</div>
                      <div className="text-sm text-gray-500">collections</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        collector.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {collector.is_active ? (
                          <>
                            <CheckCircle size={12} className="mr-1" />
                            Active
                          </>
                        ) : (
                          <>
                            <XCircle size={12} className="mr-1" />
                            Inactive
                          </>
                        )}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => toggleCollectorStatus(collector.collector_id)}
                        className={`px-3 py-1 rounded text-xs font-medium ${
                          collector.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {collector.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {!loading && !error && filteredCollectors.length === 0 && (
          <div className="text-center py-12">
            <Truck className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No collectors found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || statusFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by adding a new collector.'
              }
            </p>
          </div>
        )}
      </div>
        </div>
      )}

      {/* Collection Points Tab */}
      {activeTab === 'collection-points' && (
        <CollectionPointsManager />
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">User Management</h3>
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">User Management</h4>
            <p className="text-gray-600">Advanced user management features coming in the next update.</p>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">System Settings</h3>
          <div className="text-center py-12">
            <Settings className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">System Settings</h4>
            <p className="text-gray-600">System configuration options coming in the next update.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;