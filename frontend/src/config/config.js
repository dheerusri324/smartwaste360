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
};

// Always log configuration to debug the issue
console.log('🔧 App Configuration:', config);
console.log('🔧 Environment Variables:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT,
  NODE_ENV: process.env.NODE_ENV,
});

export default config;