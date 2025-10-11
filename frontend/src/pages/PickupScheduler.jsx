// frontend/src/pages/PickupScheduler.jsx

import React, { useState, useEffect } from 'react';
import { 
  getRouteOptimizationSuggestions, 
  getAvailableTimeSlots, 
  scheduleRouteBatch 
} from '../services/collector';
import { 
  MapPin, 
  Clock, 
  Map, 
  Calendar, 
  Package, 
  Navigation,
  CheckCircle,
  AlertCircle,
  Zap
} from 'lucide-react';

const PickupScheduler = () => {
  const [routeSuggestions, setRouteSuggestions] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTimeSlot, setSelectedTimeSlot] = useState('');
  const [availableTimeSlots, setAvailableTimeSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scheduling, setScheduling] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Set default date to tomorrow
  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setSelectedDate(tomorrow.toISOString().split('T')[0]);
  }, []);

  // Load route suggestions on component mount
  useEffect(() => {
    loadRouteSuggestions();
  }, []);

  // Load time slots when date changes
  useEffect(() => {
    const loadTimeSlots = async () => {
      try {
        const response = await getAvailableTimeSlots(selectedDate);
        setAvailableTimeSlots(response.time_slots || []);
      } catch (err) {
        console.error('Failed to load time slots:', err);
      }
    };

    if (selectedDate) {
      loadTimeSlots();
    }
  }, [selectedDate]);

  const loadRouteSuggestions = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await getRouteOptimizationSuggestions({
        max_pickups: 5,
        max_radius: 25
      });
      
      setRouteSuggestions(response.routes || []);
      
      if (response.routes && response.routes.length > 0) {
        setSelectedRoute(response.routes[0]); // Auto-select best route
      }
      
    } catch (err) {
      setError('Failed to load route suggestions: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };



  const handleScheduleRoute = async () => {
    if (!selectedRoute || !selectedDate || !selectedTimeSlot) {
      setError('Please select a route, date, and time slot');
      return;
    }

    try {
      setScheduling(true);
      setError('');
      
      const response = await scheduleRouteBatch({
        pickups: selectedRoute.pickups,
        booking_date: selectedDate,
        time_slot: selectedTimeSlot
      });
      
      setMessage(`✅ Route scheduled successfully! ${response.booking_ids.length} pickups booked.`);
      
      // Refresh data
      await loadRouteSuggestions();
      await loadTimeSlots();
      
      // Reset selections
      setSelectedRoute(null);
      setSelectedTimeSlot('');
      
    } catch (err) {
      setError('Failed to schedule route: ' + (err.message || 'Unknown error'));
    } finally {
      setScheduling(false);
    }
  };

  const getWasteTypeColor = (wasteType) => {
    const colors = {
      plastic: 'bg-blue-100 text-blue-800',
      paper: 'bg-green-100 text-green-800',
      metal: 'bg-gray-100 text-gray-800',
      glass: 'bg-purple-100 text-purple-800',
      textile: 'bg-pink-100 text-pink-800',
      organic: 'bg-yellow-100 text-yellow-800'
    };
    return colors[wasteType] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto"></div>
        <p className="text-center mt-2">Loading route suggestions...</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Map className="text-emerald-600" />
            Smart Pickup Scheduler
          </h1>
          <p className="text-gray-600 mt-1">
            AI-optimized routes for efficient waste collection
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Date and Time Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline w-4 h-4 mr-1" />
                Pickup Date
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="inline w-4 h-4 mr-1" />
                Time Slot
              </label>
              <select
                value={selectedTimeSlot}
                onChange={(e) => setSelectedTimeSlot(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">Select time slot</option>
                {availableTimeSlots.map(slot => (
                  <option 
                    key={slot.slot} 
                    value={slot.slot}
                    disabled={!slot.available}
                  >
                    {slot.label} {!slot.available && '(Fully booked)'}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Route Suggestions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Zap className="text-emerald-600" />
              Optimized Route Suggestions
            </h3>

            {routeSuggestions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Package size={48} className="mx-auto mb-4 text-gray-300" />
                <p>No pickup opportunities available in your area</p>
                <p className="text-sm mt-2">Check back later or expand your service radius in settings</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                {routeSuggestions.map((route, index) => (
                  <div
                    key={route.route_id}
                    onClick={() => setSelectedRoute(route)}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedRoute?.route_id === route.route_id
                        ? 'border-emerald-500 bg-emerald-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-semibold text-gray-800">
                        Route {route.route_id}
                        {index === 0 && (
                          <span className="ml-2 px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-full">
                            Recommended
                          </span>
                        )}
                      </h4>
                      <div className="text-right text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin size={12} />
                          {route.total_distance.toFixed(1)} km
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock size={12} />
                          {route.estimated_time_hours.toFixed(1)}h
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between text-sm">
                        <span>Pickups:</span>
                        <span className="font-medium">{route.total_colonies}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Est. Weight:</span>
                        <span className="font-medium">{route.total_estimated_weight.toFixed(1)} kg</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Efficiency:</span>
                        <span className="font-medium">{route.efficiency_score.toFixed(2)} kg/km</span>
                      </div>
                    </div>

                    <div className="space-y-1">
                      {route.pickups.slice(0, 3).map((pickup, i) => (
                        <div key={i} className="text-xs text-gray-600 flex items-center gap-1">
                          <span className="w-4 h-4 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-xs font-medium">
                            {pickup.order_in_route}
                          </span>
                          <span className="truncate">{pickup.colony_name}</span>
                          <span className={`px-1 py-0.5 rounded text-xs ${getWasteTypeColor(pickup.ready_waste_type)}`}>
                            {pickup.ready_waste_type}
                          </span>
                        </div>
                      ))}
                      {route.pickups.length > 3 && (
                        <div className="text-xs text-gray-500">
                          +{route.pickups.length - 3} more pickups
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Selected Route Details */}
          {selectedRoute && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Navigation className="text-emerald-600" />
                Route {selectedRoute.route_id} Details
              </h4>
              
              <div className="space-y-2">
                {selectedRoute.pickups.map((pickup, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 bg-emerald-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        {pickup.order_in_route}
                      </span>
                      <div>
                        <div className="font-medium text-gray-800">{pickup.colony_name}</div>
                        <div className="text-sm text-gray-600">{pickup.address || 'Address not available'}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 rounded text-sm ${getWasteTypeColor(pickup.ready_waste_type)}`}>
                        {pickup.ready_waste_type} ({pickup.max_waste_kg}kg)
                      </span>
                      {pickup.distance_from_previous > 0 && (
                        <div className="text-xs text-gray-500 mt-1">
                          {pickup.distance_from_previous.toFixed(1)}km from previous
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Schedule Button */}
          <div className="flex gap-4 pt-4">
            <button
              onClick={handleScheduleRoute}
              disabled={scheduling || !selectedRoute || !selectedDate || !selectedTimeSlot}
              className="flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              <CheckCircle size={16} />
              {scheduling ? 'Scheduling...' : 'Schedule Selected Route'}
            </button>
            
            <button
              onClick={loadRouteSuggestions}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 transition-colors"
            >
              <Map size={16} />
              Refresh Routes
            </button>
          </div>

          {/* Messages */}
          {message && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded flex items-center gap-2">
              <AlertCircle size={16} />
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PickupScheduler;