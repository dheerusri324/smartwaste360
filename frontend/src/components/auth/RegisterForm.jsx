// frontend/src/components/auth/RegisterForm.jsx

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../services/api';
import { MapPin, User, Truck, Shield } from 'lucide-react';
import { Modal } from '../common';
import LocationPicker from '../maps/LocationPicker';
import { useLocation } from '../../hooks';

const RegisterForm = () => {
  const [role, setRole] = useState('user');
  const [formData, setFormData] = useState({});
  const [location, setLocation] = useState(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { location: initialLocation, loading: locationLoading } = useLocation();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleLocationConfirm = (newLocation) => {
    setLocation(newLocation);
    setIsMapOpen(false);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (role === 'user' && !location) {
      setError("Please pin your location on the map.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Prepare the data payload based on the selected role
      const submissionData = {
        ...formData,
        role: role,
        // Only include location data if the role is 'user'
        ...(role === 'user' && {
          latitude: location?.lat,
          longitude: location?.lng,
        }),
      };
      await api.post('/auth/register', submissionData);
      alert('Registration successful! Please proceed to the correct login page.');
      if (role === 'user') {
        navigate('/login');
      } else if (role === 'collector') {
        navigate('/collector/login');
      } else if (role === 'admin') {
        navigate('/admin/login');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-2xl font-bold text-center text-gray-800">Create Your Account</h2>
        <div className="flex justify-center gap-2 py-2 flex-wrap">
          <button type="button" onClick={() => setRole('user')} className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 ${role === 'user' ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300'}`}>
            <User size={18} /> User
          </button>
          <button type="button" onClick={() => setRole('collector')} className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 ${role === 'collector' ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300'}`}>
            <Truck size={18} /> Collector
          </button>
          <button type="button" onClick={() => setRole('admin')} className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 ${role === 'admin' ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300'}`}>
            <Shield size={18} /> Admin
          </button>
        </div>

        {error && <p className="p-3 my-2 text-sm text-red-800 bg-red-100 rounded-lg">{error}</p>}
        
        {/* Fields for both roles */}
        <input type="email" name="email" placeholder="Email" onChange={handleChange} required className="form-input" />
        <input type="password" name="password" placeholder="Password" onChange={handleChange} required className="form-input" />
        <input type="text" name="full_name" placeholder="Full Name" onChange={handleChange} required className="form-input" />
        <input type="tel" name="phone" placeholder="Phone Number" onChange={handleChange} required className="form-input" />

        {/* Fields specific to each role */}
        {role === 'user' ? (
          <>
            <input type="text" name="username" placeholder="Username" onChange={handleChange} required className="form-input" />
            <div>
              <label className="form-label">Your Location</label>
              <button type="button" onClick={() => setIsMapOpen(true)} className="w-full mt-1 p-2 flex items-center justify-center gap-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                <MapPin size={16} />
                {location ? `Location Pinned` : 'Pin Your Location on Map'}
              </button>
            </div>
          </>
        ) : role === 'collector' ? (
          <input type="text" name="vehicle_number" placeholder="Vehicle Number (Optional)" onChange={handleChange} className="form-input" />
        ) : role === 'admin' ? (
          <input type="text" name="username" placeholder="Admin Username" onChange={handleChange} required className="form-input" />
        ) : null}
        
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
        <p className="text-sm text-center text-gray-600">
          Already have an account? <Link to="/login-selector" className="font-medium text-emerald-600 hover:underline">Sign in</Link>
        </p>
      </form>

      <Modal isOpen={isMapOpen} onClose={() => setIsMapOpen(false)} title="Select Your Location">
        {!locationLoading && initialLocation && (
          <LocationPicker initialPosition={initialLocation} onLocationChange={handleLocationConfirm} />
        )}
      </Modal>
    </>
  );
};

export default RegisterForm;