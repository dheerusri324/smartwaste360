// frontend/src/components/collector/CollectorLoginForm.jsx

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const CollectorLoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  

  const { collectorLoginAction } = useAuth(); // Use the specific collector login action from the context

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // This calls the specific collector login logic from the context
      await collectorLoginAction({ email, password });
      // The context will handle navigation on success
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-2xl font-bold text-center text-gray-800">Collector Login</h2>
      {error && <p className="p-3 my-2 text-sm text-red-800 bg-red-100 rounded-lg">{error}</p>}
      
      <div>
        <label htmlFor="email" className="form-label">Email</label>
        <input 
          id="email"
          type="email" 
          placeholder="your-email@example.com" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          required 
          className="form-input" 
        />
      </div>

      <div>
        <label htmlFor="password" className="form-label">Password</label>
        <input 
          id="password"
          type="password" 
          placeholder="••••••••" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
          className="form-input"
        />
      </div>
      
      <button 
        type="submit" 
        disabled={loading} 
        className="btn-primary w-full"
      >
        {loading ? 'Signing In...' : 'Sign In'}
      </button>

      <p className="text-sm text-center text-gray-600">
        Are you a regular user? <Link to="/login" className="font-medium text-emerald-600 hover:underline">Login here</Link>
      </p>
    </form>
  );
};

export default CollectorLoginForm;