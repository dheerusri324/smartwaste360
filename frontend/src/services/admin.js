// frontend/src/services/admin.js
import api from './api';

/**
 * Admin login
 */
export const loginAdmin = async (credentials) => {
  const response = await api.post('/admin/login', credentials);
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  return response.data;
};

/**
 * Get admin dashboard overview
 */
export const getAdminOverview = async () => {
  const response = await api.get('/admin/dashboard/overview');
  return response.data;
};

/**
 * Get admin analytics data
 */
export const getAdminAnalytics = async (dateRange = '30d') => {
  const response = await api.get(`/admin/dashboard/analytics?range=${dateRange}`);
  return response.data;
};

/**
 * Get all users with pagination
 */
export const getAllUsers = async (page = 1, limit = 20, search = '') => {
  const params = new URLSearchParams({ page, limit, search });
  const response = await api.get(`/admin/users?${params}`);
  return response.data;
};

/**
 * Get all collectors
 */
export const getAllCollectors = async () => {
  const response = await api.get('/admin/collectors');
  return response.data;
};

/**
 * Get all colonies for admin
 */
export const getAllColonies = async () => {
  const response = await api.get('/admin/colonies');
  return response.data;
};

/**
 * Create new colony
 */
export const createColony = async (colonyData) => {
  const response = await api.post('/admin/colonies', colonyData);
  return response.data;
};

/**
 * Create new collection point
 */
export const createCollectionPoint = async (pointData) => {
  const response = await api.post('/admin/collection-points', pointData);
  return response.data;
};

/**
 * Get system health
 */
export const getSystemHealth = async () => {
  const response = await api.get('/admin/system/health');
  return response.data;
};