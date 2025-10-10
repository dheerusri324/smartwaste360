// frontend/src/services/auth.js

import api from './api';

/**
 * Sends a registration request to the backend.
 * @param {object} userData The new user's information.
 */
export const registerUser = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

/**
 * Sends a login request to the backend.
 * @param {object} credentials The user's login details.
 */
export const loginUser = async (credentials) => {
  const response = await api.post('/auth/login', credentials);
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  return response.data;
};

/**
 * Logs the user out by removing the token from local storage.
 */
export const logoutUser = () => {
  localStorage.removeItem('token');
};

/**
 * Fetches the profile of the currently logged-in user.
 */
export const getProfile = async () => {
    const response = await api.get('/auth/profile');
    return response.data;
};

/**
 * Sends updated user data to the backend.
 * @param {object} userData - The fields to update (e.g., { full_name, phone }).
 */
export const updateUserProfile = async (userData) => {
    const response = await api.put('/auth/profile', userData);
    return response.data;
};