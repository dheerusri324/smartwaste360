// frontend/src/services/bookings.js

import api from './api';

/**
 * Creates a new waste collection booking.
 * @param {object} bookingData - The details of the booking.
 */
export const scheduleBooking = async (bookingData) => {
  const response = await api.post('/booking/schedule', bookingData);
  return response.data;
};

/**
 * Fetches all bookings for a specific colony.
 * @param {number} colonyId The ID of the colony.
 */
export const getBookingsByColony = async (colonyId) => {
  const response = await api.get(`/booking/colony/${colonyId}`);
  return response.data;
};

/**
 * Fetches all bookings for a specific collector.
 * @param {string} collectorId The ID of the collector.
 */
export const getBookingsByCollector = async (collectorId) => {
  const response = await api.get(`/booking/collector/${collectorId}`);
  return response.data;
};