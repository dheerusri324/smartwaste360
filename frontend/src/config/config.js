// frontend/src/config/config.js
// Centralized configuration for the application

const config = {
  // API Configuration - HARDCODED to avoid localhost issues
  API_BASE_URL: 'https://smartwaste360backend-production.up.railway.app/api',
  BACKEND_URL: 'https://smartwaste360backend-production.up.railway.app',
  
  // Environment
  ENVIRONMENT: 'production',
  
  // Debug mode - always show config for now to debug
  DEBUG: true,
  
  // Force cache bust
  VERSION: '2.0.1',
  UPDATED: '2025-10-11'
};

// Always log configuration to debug the issue
console.log('🔧 App Configuration (v2.0.1):', config);
console.log('🔧 Environment Variables:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT,
  NODE_ENV: process.env.NODE_ENV,
});

// Force alert to confirm new build is loaded
console.warn('🚀 NEW BUILD LOADED - API should use Railway, not localhost!');
alert('NEW BUILD LOADED! Check console for API config.');

export default config;