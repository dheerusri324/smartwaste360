// frontend/src/services/api.js

import axios from 'axios';
import config from '../config/config.js';

// Use the centralized configuration
const API_BASE_URL = config.API_BASE_URL;



const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Axios interceptor to add the JWT token to every request
api.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      console.warn('localStorage error', e);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {

    return Promise.reject(error);
  }
);

export default api;