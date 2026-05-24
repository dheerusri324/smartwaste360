// frontend/src/context/AuthContext.jsx

import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';

const AuthContext = createContext(null);

const safeStorage = {
  getItem: (key) => {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  },
  setItem: (key, value) => {
    try { localStorage.setItem(key, value); } catch (e) { console.warn('localStorage error', e); }
  },
  removeItem: (key) => {
    try { localStorage.removeItem(key); } catch (e) { console.warn('localStorage error', e); }
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async () => {
      const token = safeStorage.getItem('token');
      if (token) {
        try {
          const decoded = jwtDecode(token);
          
          // --- FIX: Read the role from the top-level claim ---
          if (decoded.role === 'collector') {
            const response = await api.get('/collector/profile');
            setUser({ ...response.data.collector, role: 'collector' });
          } else if (decoded.role === 'admin') {
            const response = await api.get('/admin/profile');
            setUser({ ...response.data.admin, role: 'admin' });
          } else {
            const response = await api.get('/auth/profile');
            setUser({ ...response.data.user, role: 'user' });
          }
        } catch (error) {
          safeStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };
    verifyToken();
  }, []);

  // Login actions now call the standardized backend and set state correctly
  const loginAction = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response.data.access_token) {
        safeStorage.setItem('token', response.data.access_token);
        setUser({ ...response.data.user, role: 'user' });
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('❌ User login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const collectorLoginAction = async (credentials) => {
    try {
      const response = await api.post('/collector/login', credentials);
      if (response.data.access_token) {
        safeStorage.setItem('token', response.data.access_token);
        setUser({ ...response.data.collector, role: 'collector' });
        navigate('/collector/dashboard');
      }
    } catch (error) {
      console.error('❌ Collector login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const adminLoginAction = async (credentials) => {
    try {
      // Use the regular auth/login endpoint which handles admin users
      const response = await api.post('/auth/login', {
        identifier: credentials.email,
        password: credentials.password
      });
      if (response.data.access_token) {
        const decoded = jwtDecode(response.data.access_token);
        if (decoded.role !== 'admin') {
          throw new Error('Access denied: Admin privileges required');
        }
        safeStorage.setItem('token', response.data.access_token);
        // Check if response has admin or user data
        const userData = response.data.admin || response.data.user;
        setUser({ ...userData, role: 'admin' });
        navigate('/admin/dashboard');
      }
    } catch (error) {
      console.error('❌ Admin login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const logoutAction = () => {
    setUser(null);
    safeStorage.removeItem('token');
    navigate('/login');
  };

  const value = { user, loginAction, collectorLoginAction, adminLoginAction, logoutAction, isAuthenticated: !!user };

  if (loading) return <div>Loading Application...</div>;

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);