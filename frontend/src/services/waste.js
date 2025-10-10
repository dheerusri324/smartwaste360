// frontend/src/services/waste.js

import api from './api';

/**
 * Sends a captured image and its weight to the backend for classification.
 * @param {string} imageDataUrl The base64 encoded image string.
 * @param {number} weight The estimated weight of the item in kg.
 * @returns {Promise<object>} The classification result from the server.
 */
export const classifyWasteImage = async (imageDataUrl, weight) => {
  try {
    const response = await api.post('/camera/capture', { 
      image: imageDataUrl, 
      weight: weight 
    });
    return response.data;
  } catch (error) {
    console.error('Image classification API error:', error.response?.data || error.message);
    throw error.response?.data || new Error('Failed to classify image.');
  }
};

/**
 * Fetches waste statistics for the logged-in user.
 */
export const getWasteStats = async () => {
  try {
    const response = await api.get('/waste/stats');
    return response.data;
  } catch (error) {
    console.error("Failed to fetch user stats:", error);
    throw error;
  }
};

/**
 * Fetches the waste classification history for the logged-in user.
 */
export const getWasteHistory = async (page = 1, limit = 5) => {
  try {
    const response = await api.get(`/waste/history?page=${page}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch waste history:", error);
    throw error;
  }
};