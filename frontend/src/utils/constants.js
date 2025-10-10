// frontend/src/utils/constants.js

export const APP_NAME = 'SmartWaste360';

// Default map coordinates (centered on Hyderabad)
export const DEFAULT_MAP_CENTER = {
  lat: 17.3850,
  lng: 78.4867,
};

// Waste category information for consistent UI
export const WASTE_CATEGORIES = {
  plastic: { label: 'Plastic', color: '#3B82F6' }, // blue
  paper: { label: 'Paper', color: '#10B981' }, // green
  cardboard: { label: 'Cardboard', color: '#A16207' }, // yellow-dark
  metal: { label: 'Metal', color: '#6B7280' }, // gray
  glass: { label: 'Glass', color: '#06B6D4' }, // cyan
  organic: { label: 'Organic', color: '#84CC16' }, // lime
  other: { label: 'Other', color: '#F97316' }, // orange
};