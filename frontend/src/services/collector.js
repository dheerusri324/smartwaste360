// frontend/src/services/collector.js
import api from './api';

export const loginCollector = async (credentials) => {
    const response = await api.post('/collector/login', credentials);
    if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
};

export const getMySchedule = async () => {
    const response = await api.get('/booking/my-schedule');
    return response.data;
};

export const schedulePickup = async (bookingData) => {
    const response = await api.post('/booking/schedule', bookingData);
    return response.data;
};
/**
 * Fetches colonies that are ready for waste collection.
 * If location is provided, it filters for nearby colonies.
 * @param {object} location - Optional object with lat and lng properties.
 */
export const getReadyColonies = async (location = null) => {
  let url = '/collector/ready-colonies';
  if (location) {
    const params = new URLSearchParams();
    params.append('lat', location.lat);
    params.append('lon', location.lng);
    if (location.radius) {
      params.append('radius', location.radius);
    }
    url += `?${params.toString()}`;
  }
  const response = await api.get(url);
  return response.data;
};

/**
 * Gets the collector's profile information.
 */
export const getCollectorProfile = async () => {
  const response = await api.get('/collector/profile');
  return response.data;
};

/**
 * Updates the collector's profile information.
 */
export const updateCollectorProfile = async (profileData) => {
  const response = await api.put('/collector/profile', profileData);
  return response.data;
};

/**
 * Gets the collector's location information.
 */
export const getCollectorLocation = async () => {
  const response = await api.get('/collector/location');
  return response.data;
};

/**
 * Updates the collector's location information.
 */
export const updateCollectorLocation = async (locationData) => {
  const response = await api.put('/collector/location', locationData);
  return response.data;
};

/**
 * Gets route optimization suggestions for the collector.
 */
export const getRouteOptimizationSuggestions = async (params = {}) => {
  let url = '/booking/route-suggestions';
  const searchParams = new URLSearchParams();
  
  if (params.max_pickups) searchParams.append('max_pickups', params.max_pickups);
  if (params.max_radius) searchParams.append('max_radius', params.max_radius);
  
  if (searchParams.toString()) {
    url += `?${searchParams.toString()}`;
  }
  
  const response = await api.get(url);
  return response.data;
};

/**
 * Gets available time slots for a specific date.
 */
export const getAvailableTimeSlots = async (date) => {
  const response = await api.get(`/booking/time-slots?date=${date}`);
  return response.data;
};

/**
 * Schedules multiple pickups as an optimized route batch.
 */
export const scheduleRouteBatch = async (routeData) => {
  const response = await api.post('/booking/schedule-route', routeData);
  return response.data;
};

/**
 * Gets collection points for a specific colony.
 */
export const getCollectionPoints = async (colonyId) => {
  const response = await api.get(`/collection-points/colony/${colonyId}`);
  return response.data;
};

/**
 * Gets all collection points with optional filtering.
 */
export const getAllCollectionPoints = async (filters = {}) => {
  let url = '/collection-points/';
  const params = new URLSearchParams();
  
  console.log('[DEBUG] getAllCollectionPoints called with filters:', filters);
  
  if (filters.waste_types && filters.waste_types.length > 0) {
    filters.waste_types.forEach(type => params.append('waste_types', type));
  }
  if (filters.latitude && filters.longitude) {
    params.append('lat', filters.latitude);
    params.append('lng', filters.longitude);
    if (filters.radius) params.append('radius', filters.radius);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  console.log('[DEBUG] Final URL:', url);
  
  try {
    const response = await api.get(url);
    console.log('[DEBUG] API response:', response);
    return response.data;
  } catch (error) {
    console.error('[DEBUG] API error:', error);
    console.error('[DEBUG] Error details:', {
      message: error.message,
      response: error.response,
      request: error.request
    });
    throw error;
  }
};

/**
 * Completes a collection booking.
 */
export const completeCollection = async (bookingId, collectionData) => {
  const response = await api.put(`/booking/${bookingId}/complete`, collectionData);
  return response.data;
};