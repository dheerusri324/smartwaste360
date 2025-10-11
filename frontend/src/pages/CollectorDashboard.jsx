// frontend/src/pages/CollectorDashboard.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { getMySchedule, getReadyColonies, schedulePickup, getCollectorProfile } from '../services/collector';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import BookingModal from '../components/collector/BookingModal';
import CollectorProfile from '../components/collector/CollectorProfile';
import CollectionPointsModal from '../components/collector/CollectionPointsModal';
import CollectionCompletionModal from '../components/collector/CollectionCompletionModal';
import CollectorStatsWidget from '../components/dashboard/CollectorStatsWidget';
import { Calendar, PackageSearch, MapPin, Settings, Navigation, CheckCircle } from 'lucide-react';
import { formatDate } from '../utils/helpers';

const CollectorDashboard = () => {
  const { user } = useAuth();
  const [schedule, setSchedule] = useState([]);
  const [readyColonies, setReadyColonies] = useState([]);
  const [collector, setCollector] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isCollectionPointsOpen, setIsCollectionPointsOpen] = useState(false);
  const [isCompletionModalOpen, setIsCompletionModalOpen] = useState(false);
  const [selectedColony, setSelectedColony] = useState(null);
  const [selectedBooking, setSelectedBooking] = useState(null);

  const loadDashboardData = useCallback(async () => {
    // Only show main loader on the very first load
    if (schedule.length === 0 && readyColonies.length === 0) {
      setLoading(true);
    }
    setError(null);
    try {
      const [scheduleData, readyColoniesData, profileData] = await Promise.all([
        getMySchedule(),
        getReadyColonies(),
        getCollectorProfile()
      ]);
      setSchedule(scheduleData.bookings || []);
      setReadyColonies(readyColoniesData.colonies || []);
      setCollector(profileData.collector || null);
    } catch (err) {
      console.error('Dashboard data error:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [schedule.length, readyColonies.length]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleScheduleClick = (colony) => {
    setSelectedColony(colony);
    setIsModalOpen(true);
  };

  const handleScheduleSubmit = async (bookingData) => {
    await schedulePickup(bookingData);
    await loadDashboardData(); // Refresh all data after booking
  };

  const handleProfileUpdate = (updatedCollector) => {
    setCollector(updatedCollector);
  };

  const handleViewCollectionPoints = (colony) => {
    setSelectedColony(colony);
    setIsCollectionPointsOpen(true);
  };

  const handleCompleteCollection = (booking) => {
    setSelectedBooking(booking);
    setIsCompletionModalOpen(true);
  };

  const handleCollectionCompleted = async () => {
    await loadDashboardData(); // Refresh all data after completion
  };

  if (loading) return <div className="flex justify-center mt-16"><LoadingSpinner /></div>;
  if (error) return <p className="text-center text-red-500 p-6">{error}</p>;

  return (
    <>
      <div className="container mx-auto p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome, {collector?.name || user?.name || 'Collector'}!</h1>
            <p className="text-gray-600">Here are your scheduled pickups and available collection opportunities.</p>
            {collector?.waste_types_collected && collector.waste_types_collected.length > 0 && (
              <div className="mt-2">
                <span className="text-sm text-gray-500">Collecting: </span>
                <span className="text-sm font-medium text-emerald-600">
                  {collector.waste_types_collected.join(', ')}
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setIsProfileOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Settings size={16} />
            Profile Settings
          </button>
        </div>
        
        {/* Analytics Widget */}
        <div className="mb-6">
          <CollectorStatsWidget />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Calendar className="text-emerald-600" /> My Schedule</h2>
            <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
              {schedule.length > 0 ? schedule.map(b => (
                <div key={b.booking_id} className="p-4 border rounded-md">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-bold">{b.colony_name}</p>
                      <p className="text-sm text-gray-500">{formatDate(b.booking_date)} at {b.time_slot}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      b.status === 'scheduled' ? 'bg-blue-100 text-blue-800' : 
                      b.status === 'completed' ? 'bg-green-100 text-green-800' : 
                      'bg-red-100 text-red-800'
                    }`}>
                      {b.status}
                    </span>
                  </div>
                  
                  {b.status === 'scheduled' && (
                    <button
                      onClick={() => handleCompleteCollection(b)}
                      className="flex items-center gap-1 px-3 py-1 bg-emerald-100 text-emerald-700 rounded-md hover:bg-emerald-200 transition-colors text-sm mt-2"
                    >
                      <CheckCircle size={14} />
                      Complete Collection
                    </button>
                  )}
                  
                  {b.status === 'completed' && b.total_weight_collected && (
                    <p className="text-xs text-gray-600 mt-2">
                      Collected: {parseFloat(b.total_weight_collected).toFixed(1)}kg
                    </p>
                  )}
                </div>
              )) : <p className="text-gray-500">You have no scheduled pickups.</p>}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><PackageSearch className="text-emerald-600" /> Find Pickups</h2>
            <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
              {readyColonies.length > 0 ? readyColonies.map(c => (
                <div key={c.colony_id} className="p-4 border rounded-md">
                  <p className="font-bold">{c.colony_name}</p>
                  <p className="text-sm text-gray-500 flex items-center gap-1"><MapPin size={12}/> {c.address || 'Address not available'}</p>
                  
                  {/* Show waste type breakdown */}
                  <div className="mt-2 space-y-1">
                    {c.ready_waste_type && (
                      <p className="text-xs font-medium text-emerald-600 uppercase">
                        Ready for: {c.ready_waste_type}
                      </p>
                    )}
                    <div className="grid grid-cols-2 gap-1 text-xs text-gray-600">
                      {c.current_plastic_kg > 0 && <span>Plastic: {parseFloat(c.current_plastic_kg).toFixed(1)}kg</span>}
                      {c.current_paper_kg > 0 && <span>Paper: {parseFloat(c.current_paper_kg).toFixed(1)}kg</span>}
                      {c.current_metal_kg > 0 && <span>Metal: {parseFloat(c.current_metal_kg).toFixed(1)}kg</span>}
                      {c.current_glass_kg > 0 && <span>Glass: {parseFloat(c.current_glass_kg).toFixed(1)}kg</span>}
                      {c.current_textile_kg > 0 && <span>Textile: {parseFloat(c.current_textile_kg).toFixed(1)}kg</span>}
                    </div>
                    <p className="text-sm text-gray-700">
                      Total: <span className="font-bold text-lg text-emerald-600">{parseFloat(c.max_waste_kg || c.current_dry_waste_kg || 0).toFixed(2)} kg</span>
                    </p>
                  </div>
                  
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => handleScheduleClick(c)} className="btn-primary flex-1 text-sm">
                      Schedule Pickup
                    </button>
                    <button 
                      onClick={() => handleViewCollectionPoints(c)} 
                      className="flex items-center gap-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors text-sm"
                    >
                      <Navigation size={14} />
                      Points
                    </button>
                  </div>
                </div>
              )) : <p className="text-gray-500">No colonies have reached the pickup threshold.</p>}
            </div>
          </div>
        </div>
      </div>
      <BookingModal
        colony={selectedColony}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleScheduleSubmit}
      />
      
      {isProfileOpen && (
        <CollectorProfile
          collector={collector}
          onUpdate={handleProfileUpdate}
          onClose={() => setIsProfileOpen(false)}
        />
      )}
      
      {isCollectionPointsOpen && (
        <CollectionPointsModal
          colony={selectedColony}
          isOpen={isCollectionPointsOpen}
          onClose={() => setIsCollectionPointsOpen(false)}
        />
      )}
      
      {isCompletionModalOpen && (
        <CollectionCompletionModal
          booking={selectedBooking}
          isOpen={isCompletionModalOpen}
          onClose={() => setIsCompletionModalOpen(false)}
          onComplete={handleCollectionCompleted}
        />
      )}
    </>
  );
};

export default CollectorDashboard;