// frontend/src/config/config.js
// Centralized configuration for the application

const config = {
  // API Configuration - Use environment variables for flexibility
  API_BASE_URL: process.env.REACT_APP_API_URL || 'https://smartwaste360-backend.onrender.com/api',
  BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'https://smartwaste360-backend.onrender.com',
  
  // Environment
  ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT || 'development',
  
  // Debug mode - always show config for now to debug
  DEBUG: true,
  
  // Force cache bust
  VERSION: '3.0.1',
  UPDATED: '2025-10-26-DATABASE-SYNC-FIX-' + Date.now()
};

// Always log configuration to debug the issue
console.log('🔧 App Configuration (v2.1.0):', config);
console.log('🔧 Environment Variables:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT,
  NODE_ENV: process.env.NODE_ENV,
});

// Mobile debugging
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
console.log('📱 Device Info:', {
  isMobile: isMobile,
  userAgent: navigator.userAgent,
  platform: navigator.platform,
  onLine: navigator.onLine
});

// Force alert to confirm new build is loaded
console.warn('🔄 DATABASE SYNC FIX v3.0.1 LOADED - API URL: ' + config.API_BASE_URL);
console.warn('🎯 TIMESTAMP: ' + config.UPDATED);
console.warn('🗄️ FIXING DATABASE SYNC AND UI ISSUES!');
if (isMobile) {
  alert('💥 NUCLEAR REDEPLOY v3.0.0! API: ' + config.API_BASE_URL);
}

export default config;