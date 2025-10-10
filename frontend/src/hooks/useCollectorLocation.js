// frontend/src/hooks/useCollectorLocation.js

import { useState, useEffect } from 'react';
import { getCollectorLocation } from '../services/collector';

/**
 * Hook for managing collector location
 * Provides multiple location strategies for collectors
 */
export const useCollectorLocation = () => {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [locationMethod, setLocationMethod] = useState('saved'); // 'saved', 'current', 'all', 'custom'
  const [savedLocation, setSavedLocation] = useState(null);

  // Get current browser location
  const getCurrentLocation = () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      setLocationMethod('all');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const newLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
          method: 'current'
        };
        setLocation(newLocation);
        setLocationMethod('current');
        setLoading(false);
        console.log('Collector current location:', newLocation);
      },
      (error) => {
        console.warn('Geolocation error:', error);
        setError(`Location access denied: ${error.message}`);
        setLocationMethod('all');
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  // Set custom location (for collectors to set their service area)
  const setCustomLocation = (lat, lng, name = 'Custom Location') => {
    const customLocation = {
      lat,
      lng,
      name,
      method: 'custom'
    };
    setLocation(customLocation);
    setLocationMethod('custom');
    setError(null);
    console.log('Collector custom location set:', customLocation);
  };

  // Show all colonies (no location filter)
  const showAllColonies = () => {
    setLocation(null);
    setLocationMethod('all');
    setError(null);
    console.log('Collector viewing all colonies');
  };

  // Load saved location first, then try current location if no saved location
  useEffect(() => {
    loadSavedLocation();
  }, []);

  const loadSavedLocation = async () => {
    try {
      setLoading(true);
      const response = await getCollectorLocation();
      
      if (response.location && response.location.latitude && response.location.longitude) {
        const savedLoc = {
          lat: parseFloat(response.location.latitude),
          lng: parseFloat(response.location.longitude),
          address: response.location.address,
          city: response.location.city,
          state: response.location.state,
          method: 'saved'
        };
        
        setSavedLocation(savedLoc);
        setLocation(savedLoc);
        setLocationMethod('saved');
        setError(null);
        console.log('Collector saved location loaded:', savedLoc);
      } else {
        // No saved location, try current location
        console.log('No saved location found, trying current location');
        getCurrentLocation();
        return;
      }
    } catch (err) {
      console.warn('Failed to load saved location:', err);
      // Fallback to current location
      getCurrentLocation();
      return;
    } finally {
      setLoading(false);
    }
  };

  return {
    location,
    loading,
    error,
    locationMethod,
    savedLocation,
    getCurrentLocation,
    setCustomLocation,
    showAllColonies,
    loadSavedLocation,
    // Helper methods
    hasLocation: !!location,
    isUsingSavedLocation: locationMethod === 'saved',
    isUsingCurrentLocation: locationMethod === 'current',
    isShowingAll: locationMethod === 'all',
    isUsingCustomLocation: locationMethod === 'custom'
  };
};