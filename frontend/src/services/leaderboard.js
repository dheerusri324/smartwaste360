// frontend/src/services/leaderboard.js

import api from './api';

/**
 * Fetches the colony leaderboard, ranked by points.
 * @param {number} limit The number of top colonies to fetch.
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
 * Fetches the collector leaderboard, ranked by weight collected.
 * @param {number} limit The number of top collectors to fetch.
 */
export const getCollectorLeaderboard = async (limit = 100) => {
  try {
    const response = await api.get(`/leaderboard/collectors?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch collector leaderboard:", error);
    throw error;
  }
};