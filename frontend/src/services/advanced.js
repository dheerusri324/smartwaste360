// frontend/src/services/advanced.js
import api from './api';

export const getUserAchievements = async (userId) => {
  const response = await api.get(`/advanced/achievements/user/${userId}`);
  return response.data;
};

export const getCollectorAchievements = async (collectorId) => {
  const response = await api.get(`/advanced/achievements/collector/${collectorId}`);
  return response.data;
};
