// frontend/src/services/colonies.js

import api from './api';

/**
 * Fetches a list of all colonies from the backend.
 * Used for populating the map.
 */
export const getColonies = async () => {
  try {
    const response = await api.get('/colony/');
    return response.data;
  } catch (error) {
    console.error("Failed to fetch colonies:", error);
    throw error;
  }
};

/**
 * Fetches the colony leaderboard from the backend.
 * @param {number} limit The number of top colonies to retrieve.
 */
export const getColonyLeaderboard = async (limit = 10) => {
  try {
    const response = await api.get(`/leaderboard/colonies?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch colony leaderboard:", error);
    throw error;
  }
};

/**
 * Fetches the user leaderboard for a specific colony from the backend.
 * @param {number} colonyId The ID of the colony.
 * @param {number} limit The number of top users to retrieve.
 */
export const getUserLeaderboard = async (colonyId, limit = 10) => {
  try {
    const response = await api.get(`/leaderboard/users?colony_id=${colonyId}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch user leaderboard:", error);
    throw error;
  }
};

/**
 * Fetches colonies near a specific geographic point.
 * @param {number} lat - Latitude.
 * @param {number} lon - Longitude.
 * @param {number} radius - Radius in kilometers.
 */
export const getNearbyColonies = async (lat, lon, radius = 25) => {
  const response = await api.get(`/colony/nearby?lat=${lat}&lon=${lon}&radius=${radius}`);
  return response.data;
};