// frontend/src/components/auth/LoginForm.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const LoginForm = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { loginAction } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await loginAction({ identifier, password });
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-2xl font-bold text-center text-gray-800">Welcome Back!</h2>
      {error && <p className="p-3 my-2 text-sm text-red-800 bg-red-100 rounded-lg">{error}</p>}
      <input type="text" placeholder="Username or Email" value={identifier} onChange={(e) => setIdentifier(e.target.value)} required className="w-full px-3 py-2 mt-1 border border-gray-300 rounded-md" />
      <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-3 py-2 mt-1 border border-gray-300 rounded-md" />
      <button type="submit" disabled={loading} className="w-full py-3 px-4 font-semibold text-white bg-emerald-600 rounded-md hover:bg-emerald-700 disabled:bg-gray-400">
        {loading ? 'Signing In...' : 'Sign In'}
      </button>
      <p className="text-sm text-center text-gray-600">
        Are you a Waste Collector? <Link to="/collector/login" className="font-medium text-emerald-600 hover:underline">Login here</Link>
      </p>
      <p className="text-sm text-center text-gray-600">
        Don't have an account? <Link to="/register" className="font-medium text-emerald-600">Register</Link>
      </p>
    </form>
  );
};

export default LoginForm;