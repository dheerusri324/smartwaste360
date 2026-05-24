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
  Settings,
  Award,
  Activity,
  Database,
  Server,
  Cpu,
  Leaf,
  Recycle
} from 'lucide-react';
import { getAllCollectors, updateCollectorStatus, getAdminOverview, getAllUsers, updateUserStatus, getSystemHealth, getPointsConfig } from '../services/admin';
import CollectionPointsManager from '../components/admin/CollectionPointsManager';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('collectors');
  const [collectors, setCollectors] = useState([]);
  const [overviewData, setOverviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [users, setUsers] = useState([]);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [userStatusFilter, setUserStatusFilter] = useState('all');
  const [usersLoading, setUsersLoading] = useState(false);
  const [healthData, setHealthData] = useState(null);
  const [pointsConfig, setPointsConfig] = useState([]);
  const [settingsLoading, setSettingsLoading] = useState(false);

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
      // Load both collectors and overview data
      const [collectorsResponse, overviewResponse] = await Promise.all([
        getAllCollectors(),
        getAdminOverview()
      ]);
      
      setCollectors(collectorsResponse.collectors || []);
      setOverviewData(overviewResponse);
      
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
            <button 
              onClick={() => {
                const name = prompt("Collector Name:");
                if (!name) return;
                const email = prompt("Email:");
                if (!email) return;
                const phone = prompt("Phone:");
                if (!phone) return;
                const password = prompt("Password:");
                if (!password) return;
                
                // Call API to create collector
                fetch(`${process.env.REACT_APP_API_URL || 'https://smartwaste360-backend.onrender.com/api'}/admin/collectors`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                  },
                  body: JSON.stringify({ name, email, phone, password })
                })
                .then(res => res.json())
                .then(data => {
                  if (data.error) {
                    alert(`Error: ${data.error}`);
                  } else {
                    alert(`Collector created successfully! ID: ${data.collector.collector_id}`);
                    window.location.reload();
                  }
                })
                .catch(err => alert(`Failed to create collector: ${err.message}`));
              }}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
            >
              <Plus size={20} />
              Add New Collector
            </button>
          </div>

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
      {activeTab === 'users' && <UsersTab
        users={users}
        setUsers={setUsers}
        usersLoading={usersLoading}
        setUsersLoading={setUsersLoading}
        userSearchTerm={userSearchTerm}
        setUserSearchTerm={setUserSearchTerm}
        userStatusFilter={userStatusFilter}
        setUserStatusFilter={setUserStatusFilter}
      />}

      {/* Settings Tab */}
      {activeTab === 'settings' && <SettingsTab
        healthData={healthData}
        setHealthData={setHealthData}
        pointsConfig={pointsConfig}
        setPointsConfig={setPointsConfig}
        settingsLoading={settingsLoading}
        setSettingsLoading={setSettingsLoading}
      />}
    </div>
  );
};

/* ─── Users Tab Component ─── */
const UsersTab = ({ users, setUsers, usersLoading, setUsersLoading, userSearchTerm, setUserSearchTerm, userStatusFilter, setUserStatusFilter }) => {
  useEffect(() => {
    const fetchUsers = async () => {
      setUsersLoading(true);
      try {
        const response = await getAllUsers();
        setUsers(response.users || []);
      } catch (err) {
        console.error('Failed to load users:', err);
        setUsers([]);
      } finally {
        setUsersLoading(false);
      }
    };
    fetchUsers();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      await updateUserStatus(userId, !currentStatus);
      setUsers(prev => prev.map(u =>
        u.user_id === userId ? { ...u, is_active: !currentStatus } : u
      ));
    } catch (err) {
      console.error('Failed to update user status:', err);
      alert('Failed to update user status.');
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = (user.full_name || '').toLowerCase().includes(userSearchTerm.toLowerCase()) ||
      (user.email || '').toLowerCase().includes(userSearchTerm.toLowerCase()) ||
      (user.username || '').toLowerCase().includes(userSearchTerm.toLowerCase());
    const matchesStatus = userStatusFilter === 'all' ||
      (userStatusFilter === 'active' && user.is_active) ||
      (userStatusFilter === 'inactive' && !user.is_active);
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <p className="text-gray-600">View and manage registered users</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm border p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{users.length}</p>
            </div>
            <div className="p-3 rounded-full bg-blue-100"><Users size={20} className="text-blue-600" /></div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-2xl font-bold text-emerald-600">{users.filter(u => u.is_active).length}</p>
            </div>
            <div className="p-3 rounded-full bg-emerald-100"><CheckCircle size={20} className="text-emerald-600" /></div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Inactive Users</p>
              <p className="text-2xl font-bold text-red-600">{users.filter(u => !u.is_active).length}</p>
            </div>
            <div className="p-3 rounded-full bg-red-100"><XCircle size={20} className="text-red-600" /></div>
          </div>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search users by name, email, or username..."
              value={userSearchTerm}
              onChange={(e) => setUserSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-gray-400" />
            <select
              value={userStatusFilter}
              onChange={(e) => setUserStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Users ({filteredUsers.length})</h3>
        </div>
        {usersLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Colony</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recycled</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-semibold text-sm">
                            {(user.full_name || user.username || '?').charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{user.full_name || user.username}</div>
                          <div className="text-sm text-gray-500 flex items-center gap-1">
                            <Mail size={12} className="text-gray-400" /> {user.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{user.colony_name || '—'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <Award size={14} className="text-yellow-500" />
                        <span className="text-sm font-medium text-gray-900">{user.total_points || 0}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {parseFloat(user.total_weight_recycled || 0).toFixed(1)} kg
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? <><CheckCircle size={12} className="mr-1" /> Active</> : <><XCircle size={12} className="mr-1" /> Inactive</>}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-500">
                        {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleToggleUserStatus(user.user_id, user.is_active)}
                        className={`px-3 py-1 rounded text-xs font-medium ${
                          user.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!usersLoading && filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {userSearchTerm || userStatusFilter !== 'all' ? 'Try adjusting your search or filter.' : 'No registered users yet.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

/* ─── Settings Tab Component ─── */
const SettingsTab = ({ healthData, setHealthData, pointsConfig, setPointsConfig, settingsLoading, setSettingsLoading }) => {
  const loadSettingsData = async () => {
    setSettingsLoading(true);
    try {
      const [healthRes, pointsRes] = await Promise.all([
        getSystemHealth(),
        getPointsConfig()
      ]);
      setHealthData(healthRes);
      setPointsConfig(pointsRes.points_config || []);
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setSettingsLoading(false);
    }
  };

  useEffect(() => {
    loadSettingsData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const StatusBadge = ({ status }) => {
    const isHealthy = status === 'healthy';
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
        isHealthy ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
      }`}>
        <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
        {isHealthy ? 'Healthy' : 'Unhealthy'}
      </span>
    );
  };

  if (settingsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">System Settings</h2>
          <p className="text-gray-600">Monitor system health and configuration</p>
        </div>
        <button
          onClick={loadSettingsData}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm"
        >
          <Activity size={16} /> Refresh Status
        </button>
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Activity size={20} className="text-emerald-600" /> System Health
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <Database size={20} className="text-blue-600" />
              <span className="font-medium text-gray-700">Database</span>
            </div>
            <StatusBadge status={healthData?.database_status || 'unknown'} />
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <Server size={20} className="text-purple-600" />
              <span className="font-medium text-gray-700">API Server</span>
            </div>
            <StatusBadge status={healthData?.api_status || 'unknown'} />
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <Cpu size={20} className="text-orange-600" />
              <span className="font-medium text-gray-700">ML Service</span>
            </div>
            <StatusBadge status={healthData?.ml_service_status || 'unknown'} />
          </div>
        </div>
        {healthData?.last_updated && (
          <p className="text-xs text-gray-400 mt-3">Last checked: {new Date(healthData.last_updated).toLocaleString()}</p>
        )}
      </div>

      {/* Database Stats */}
      {healthData?.database_details && healthData.database_status === 'healthy' && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Database size={20} className="text-blue-600" /> Database Statistics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Users', value: healthData.database_details.total_users, icon: Users, color: 'blue' },
              { label: 'Collectors', value: healthData.database_details.total_collectors, icon: Truck, color: 'green' },
              { label: 'Colonies', value: healthData.database_details.total_colonies, icon: MapPin, color: 'purple' },
              { label: 'Bookings', value: healthData.database_details.total_bookings, icon: CheckCircle, color: 'emerald' }
            ].map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="text-center p-4 bg-gray-50 rounded-lg">
                <Icon size={24} className={`mx-auto mb-2 text-${color}-500`} />
                <p className="text-2xl font-bold text-gray-900">{value ?? 0}</p>
                <p className="text-xs text-gray-500">{label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Points Configuration */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Award size={20} className="text-yellow-500" /> Points Configuration
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Material Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points/kg</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recyclable</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CO₂ Factor</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pointsConfig.map((item) => (
                <tr key={item.material_type} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Recycle size={16} className="text-emerald-500" />
                      <span className="text-sm font-medium text-gray-900 capitalize">{item.material_type}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800">
                      {item.points_per_kg} pts
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.is_recyclable ? (
                      <span className="inline-flex items-center gap-1 text-emerald-600 text-sm"><Leaf size={14} /> Yes</span>
                    ) : (
                      <span className="text-gray-400 text-sm">No</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-700">{parseFloat(item.co2_factor).toFixed(2)} kg CO₂/kg</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {pointsConfig.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <Award className="mx-auto mb-2 h-8 w-8" />
            <p className="text-sm">No points configuration found.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;