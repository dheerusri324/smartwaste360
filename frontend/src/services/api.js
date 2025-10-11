// frontend/src/services/api.js

import axios from 'axios';
import config from '../config/config.js';

// Use the centralized configuration
const API_BASE_URL = config.API_BASE_URL;

// Debug logging
console.log('🔧 API Configuration:', {
  API_BASE_URL: API_BASE_URL,
  config: config,
  env_REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  NODE_ENV: process.env.NODE_ENV
});

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Axios interceptor to add the JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;