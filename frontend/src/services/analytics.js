// frontend/src/services/analytics.js

import api from './api';

/**
 * Gets collector performance metrics for a specified period
 */
export const getCollectorPerformance = async (days = 30) => {
  const response = await api.get(`/analytics/collector/performance?days=${days}`);
  return response.data;
};

/**
 * Gets quick summary stats for collector dashboard
 */
export const getCollectorSummary = async () => {
  const response = await api.get('/analytics/collector/summary');
  return response.data;
};

/**
 * Gets system-wide analytics (admin only)
 */
export const getSystemOverview = async (days = 30) => {
  const response = await api.get(`/analytics/system/overview?days=${days}`);
  return response.data;
};

/**
 * Gets waste trends analysis
 */
export const getWasteTrends = async (days = 90) => {
  const response = await api.get(`/analytics/waste/trends?days=${days}`);
  return response.data;
};

/**
 * Gets real-time dashboard data
 */
export const getRealtimeDashboard = async () => {
  const response = await api.get('/analytics/dashboard/realtime');
  return response.data;
};

/**
 * Gets environmental impact metrics
 */
export const getEnvironmentalImpact = async (days = 30) => {
  const response = await api.get(`/analytics/environmental/impact?days=${days}`);
  return response.data;
};

/**
 * Gets collection efficiency analysis
 */
export const getEfficiencyAnalysis = async (collectorId, days = 30) => {
  const params = new URLSearchParams();
  if (collectorId) params.append('collector_id', collectorId);
  params.append('days', days);
  
  const response = await api.get(`/analytics/efficiency/analysis?${params.toString()}`);
  return response.data;
};

/**
 * Gets route optimization insights
 */
export const getRouteInsights = async (days = 30) => {
  const response = await api.get(`/analytics/routes/insights?days=${days}`);
  return response.data;
};

/**
 * Gets colony performance rankings
 */
export const getColonyRankings = async (days = 30, limit = 20) => {
  const response = await api.get(`/analytics/colonies/rankings?days=${days}&limit=${limit}`);
  return response.data;
};

/**
 * Gets waste type distribution analysis
 */
export const getWasteDistribution = async (days = 30) => {
  const response = await api.get(`/analytics/waste/distribution?days=${days}`);
  return response.data;
};

/**
 * Gets collector leaderboard with detailed metrics
 */
export const getCollectorLeaderboard = async (days = 30, limit = 10) => {
  const response = await api.get(`/analytics/collectors/leaderboard?days=${days}&limit=${limit}`);
  return response.data;
};

/**
 * Gets predictive analytics for waste generation
 */
export const getPredictiveAnalytics = async (colonyId = null, days = 90) => {
  const params = new URLSearchParams();
  if (colonyId) params.append('colony_id', colonyId);
  params.append('days', days);
  
  const response = await api.get(`/analytics/predictive/waste?${params.toString()}`);
  return response.data;
};

/**
 * Gets carbon footprint analysis
 */
export const getCarbonFootprint = async (days = 30) => {
  const response = await api.get(`/analytics/environmental/carbon?days=${days}`);
  return response.data;
};

/**
 * Gets collection route efficiency metrics
 */
export const getRouteEfficiency = async (collectorId = null, days = 30) => {
  const params = new URLSearchParams();
  if (collectorId) params.append('collector_id', collectorId);
  params.append('days', days);
  
  const response = await api.get(`/analytics/routes/efficiency?${params.toString()}`);
  return response.data;
};

/**
 * Gets time-based collection patterns
 */
export const getCollectionPatterns = async (days = 90) => {
  const response = await api.get(`/analytics/patterns/collection?days=${days}`);
  return response.data;
};

/**
 * Gets waste generation forecasting
 */
export const getWasteForecast = async (colonyId = null, days = 30) => {
  const params = new URLSearchParams();
  if (colonyId) params.append('colony_id', colonyId);
  params.append('forecast_days', days);
  
  const response = await api.get(`/analytics/forecast/waste?${params.toString()}`);
  return response.data;
};

/**
 * Gets comparative performance analysis
 */
export const getComparativeAnalysis = async (collectorId, compareWith = 'average', days = 30) => {
  const params = new URLSearchParams();
  params.append('collector_id', collectorId);
  params.append('compare_with', compareWith);
  params.append('days', days);
  
  const response = await api.get(`/analytics/comparative/performance?${params.toString()}`);
  return response.data;
};

/**
 * Gets collection density heatmap data
 */
export const getCollectionHeatmap = async (days = 30) => {
  const response = await api.get(`/analytics/heatmap/collections?days=${days}`);
  return response.data;
};

/**
 * Gets operational insights and recommendations
 */
export const getOperationalInsights = async (days = 30) => {
  const response = await api.get(`/analytics/insights/operational?days=${days}`);
  return response.data;
};