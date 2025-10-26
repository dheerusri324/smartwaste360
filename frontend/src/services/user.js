// frontend/src/services/user.js

import api from './api';

/**
 * Get user's location based on their colony
 */
export const getUserLocation = async () => {
  try {
    const response = await api.get('/auth/profile');
    const user = response.data.user;
    
    if (user && user.colony_id) {
      // Get colony details to get location
      const colonyResponse = await api.get(`/colony/${user.colony_id}`);
      const colony = colonyResponse.data.colony;
      
      if (colony && colony.latitude && colony.longitude) {
        return {
          lat: parseFloat(colony.latitude),
          lng: parseFloat(colony.longitude),
          colony_name: colony.colony_name,
          colony_id: colony.colony_id
        };
      }
    }
    
    return null;
  } catch (error) {
    console.error('Failed to get user location:', error);
    return null;
  }
};

/**
 * Get user profile information
 */
export const getUserProfile = async () => {
  const response = await api.get('/auth/profile');
  return response.data;
};

/**
 * Update user profile
 */
export const updateUserProfile = async (profileData) => {
  const response = await api.put('/auth/profile', profileData);
  return response.data;
};
/**

 * Get collection points for users (public endpoint)
 */
export const getUserCollectionPoints = async (filters = {}) => {
  let url = '/collection-points/';
  const params = new URLSearchParams();
  
  console.log('[DEBUG] getUserCollectionPoints called with filters:', filters);
  
  if (filters.waste_types && filters.waste_types.length > 0) {
    filters.waste_types.forEach(type => params.append('waste_types', type));
  }
  if (filters.latitude && filters.longitude) {
    params.append('lat', filters.latitude);
    params.append('lng', filters.longitude);
    if (filters.radius) params.append('radius', filters.radius);
  }
  
  if (params.toString()) {
    url += '?' + params.toString();
  }
  
  console.log('[DEBUG] Final collection points URL:', url);
  const response = await api.get(url);
  return response.data;
};