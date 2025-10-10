// frontend/src/context/AuthContext.jsx

import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
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
          localStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };
    verifyToken();
  }, []);

  // Login actions now call the standardized backend and set state correctly
  const loginAction = async (credentials) => {
    console.log('🔍 User login attempt:', credentials);
    try {
      const response = await api.post('/auth/login', credentials);
      console.log('✅ User login response:', response.data);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        setUser({ ...response.data.user, role: 'user' });
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('❌ User login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const collectorLoginAction = async (credentials) => {
    console.log('🔍 Collector login attempt:', credentials);
    try {
      const response = await api.post('/collector/login', credentials);
      console.log('✅ Collector login response:', response.data);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        setUser({ ...response.data.collector, role: 'collector' });
        navigate('/collector/dashboard');
      }
    } catch (error) {
      console.error('❌ Collector login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const adminLoginAction = async (credentials) => {
    console.log('🔍 Admin login attempt:', credentials);
    try {
      const response = await api.post('/admin/login', credentials);
      console.log('✅ Admin login response:', response.data);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        setUser({ ...response.data.admin, role: 'admin' });
        navigate('/admin/dashboard');
      }
    } catch (error) {
      console.error('❌ Admin login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const logoutAction = () => {
    setUser(null);
    localStorage.removeItem('token');
    navigate('/login');
  };

  const value = { user, loginAction, collectorLoginAction, adminLoginAction, logoutAction, isAuthenticated: !!user };

  if (loading) return <div>Loading Application...</div>;

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);