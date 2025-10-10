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