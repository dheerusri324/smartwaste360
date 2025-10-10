// frontend/src/components/collector/CollectorProfile.jsx
import React, { useState } from 'react';
import { updateCollectorProfile } from '../../services/collector';
import { User, Truck, Package, Save, X } from 'lucide-react';

const CollectorProfile = ({ collector, onUpdate, onClose }) => {
  const [formData, setFormData] = useState({
    name: collector?.name || '',
    phone: collector?.phone || '',
    vehicle_number: collector?.vehicle_number || '',
    bio: collector?.bio || '',
    waste_types_collected: collector?.waste_types_collected || [],
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const wasteTypes = [
    { value: 'plastic', label: 'Plastic' },
    { value: 'paper', label: 'Paper' },
    { value: 'metal', label: 'Metal' },
    { value: 'glass', label: 'Glass' },
    { value: 'textile', label: 'Textile' },
    { value: 'organic', label: 'Organic' }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleWasteTypeChange = (wasteType) => {
    setFormData(prev => ({
      ...prev,
      waste_types_collected: prev.waste_types_collected.includes(wasteType)
        ? prev.waste_types_collected.filter(type => type !== wasteType)
        : [...prev.waste_types_collected, wasteType]
    }));
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
        name: formData.name,
        phone: formData.phone,
        vehicle_number: formData.vehicle_number,
        bio: formData.bio,
        waste_types_collected: formData.waste_types_collected
      };

      // Only include password if it's provided
      if (formData.password) {
        updateData.password = formData.password;
      }

      const response = await updateCollectorProfile(updateData);
      setMessage('Profile updated successfully!');
      onUpdate(response.collector);
      
      // Clear password fields
      setFormData(prev => ({ ...prev, password: '', confirmPassword: '' }));
    } catch (err) {
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <User className="text-emerald-600" />
            Collector Profile
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="form-label">Full Name</label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
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

          {/* Vehicle Information */}
          <div>
            <label htmlFor="vehicle_number" className="form-label flex items-center gap-2">
              <Truck size={16} />
              Vehicle Number
            </label>
            <input
              id="vehicle_number"
              name="vehicle_number"
              type="text"
              value={formData.vehicle_number}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g., MH12AB1234"
            />
          </div>

          {/* Bio */}
          <div>
            <label htmlFor="bio" className="form-label">Bio / Description</label>
            <textarea
              id="bio"
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              className="form-input"
              rows="3"
              placeholder="Tell us about yourself and your collection experience..."
            />
          </div>

          {/* Waste Types Collected */}
          <div>
            <label className="form-label flex items-center gap-2">
              <Package size={16} />
              Waste Types You Collect
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
              {wasteTypes.map(type => (
                <label key={type.value} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.waste_types_collected.includes(type.value)}
                    onChange={() => handleWasteTypeChange(type.value)}
                    className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                  />
                  <span className="text-sm text-gray-700">{type.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Password Change */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Change Password (Optional)</h3>
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
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center gap-2"
            >
              <Save size={16} />
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CollectorProfile;