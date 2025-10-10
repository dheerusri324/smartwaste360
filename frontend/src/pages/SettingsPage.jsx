// frontend/src/pages/SettingsPage.jsx

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { updateUserProfile } from '../services/auth';
import { User, Lock, Save } from 'lucide-react';

const SettingsPage = () => {
  const { user, login } = useAuth();
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    password: '',
    confirmPassword: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    // Validate password if provided
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const updateData = {
        full_name: formData.full_name,
        phone: formData.phone
      };

      // Only include password if it's provided
      if (formData.password) {
        updateData.password = formData.password;
      }

      const response = await updateUserProfile(updateData);
      login(response.user); // Update the global user state with the new info
      setMessage('Profile updated successfully!');
      
      // Clear password fields
      setFormData(prev => ({ ...prev, password: '', confirmPassword: '' }));
    } catch (err) {
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        <User className="text-emerald-600" />
        User Settings
      </h1>
      
      <div className="max-w-2xl bg-white p-8 rounded-lg shadow-md">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800 border-b pb-2">Basic Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="full_name" className="form-label">Full Name</label>
                <input 
                  id="full_name" 
                  name="full_name" 
                  type="text" 
                  value={formData.full_name} 
                  onChange={handleChange} 
                  className="form-input"
                  required
                />
              </div>
              <div>
                <label htmlFor="phone" className="form-label">Phone Number</label>
                <input 
                  id="phone" 
                  name="phone" 
                  type="tel" 
                  value={formData.phone} 
                  onChange={handleChange} 
                  className="form-input"
                />
              </div>
            </div>

            <div>
              <label className="form-label">Email Address</label>
              <input 
                type="email" 
                value={user?.email || ''} 
                disabled 
                className="form-input bg-gray-100 cursor-not-allowed"
              />
              <p className="text-sm text-gray-500 mt-1">Email cannot be changed</p>
            </div>
          </div>

          {/* Password Change */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800 border-b pb-2 flex items-center gap-2">
              <Lock size={18} />
              Change Password (Optional)
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="password" className="form-label">New Password</label>
                <input 
                  id="password" 
                  name="password" 
                  type="password" 
                  value={formData.password} 
                  onChange={handleChange} 
                  className="form-input"
                  placeholder="Leave blank to keep current password"
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="form-label">Confirm New Password</label>
                <input 
                  id="confirmPassword" 
                  name="confirmPassword" 
                  type="password" 
                  value={formData.confirmPassword} 
                  onChange={handleChange} 
                  className="form-input"
                />
              </div>
            </div>
          </div>

          {/* Messages */}
          {message && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button 
            type="submit" 
            disabled={loading} 
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            <Save size={16} />
            {loading ? 'Saving Changes...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SettingsPage;