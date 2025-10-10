import React, { useState, useEffect } from 'react';
import { Scale, DollarSign, Calendar, AlertCircle, User, Package, CheckCircle } from 'lucide-react';
import api from '../../services/api';

const TransactionForm = () => {
  const [formData, setFormData] = useState({
    user_id: '',
    waste_type: '',
    weight: '',
    rate: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [users, setUsers] = useState([]);
  const [wasteTypes, setWasteTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchFormData = async () => {
      try {
        const [usersResponse, wasteTypesResponse] = await Promise.all([
          api.get('/api/collector/users'),
          api.get('/api/waste/types')
        ]);
        
        setUsers(usersResponse.data.users || []);
        setWasteTypes(wasteTypesResponse.data.types || []);
      } catch (err) {
        console.error('Error fetching form data:', err);
        setError(err.response?.data?.error || 'Failed to load form data');
      }
    };
    
    fetchFormData();
  }, []);

  const calculateAmount = () => {
    const weight = parseFloat(formData.weight) || 0;
    const rate = parseFloat(formData.rate) || 0;
    return (weight * rate).toFixed(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const payload = {
        ...formData,
        amount: calculateAmount(),
        transaction_date: formData.date
      };
      
      await api.post('/api/transaction', payload);
      
      setSuccess(true);
      setFormData({
        user_id: '',
        waste_type: '',
        weight: '',
        rate: '',
        amount: '',
        date: new Date().toISOString().split('T')[0],
        notes: ''
      });
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error recording transaction:', err);
      setError(err.response?.data?.error || 'Failed to record transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Record Transaction</h1>
      
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 flex items-center">
          <CheckCircle className="mr-2" />
          Transaction recorded successfully!
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center">
          <AlertCircle className="mr-2" />
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="bg-white rounded-lg p-6 shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label htmlFor="user-select" className="block text-sm font-medium text-gray-700 mb-2">
              User
            </label>
            <div className="relative">
              <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <select
                id="user-select"
                required
                value={formData.user_id}
                onChange={(e) => setFormData({...formData, user_id: e.target.value})}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600"
              >
                <option value="">Select user</option>
                {users.map(user => (
                  <option key={user.user_id} value={user.user_id}>
                    {user.full_name} ({user.user_id})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="waste-type-select" className="block text-sm font-medium text-gray-700 mb-2">
              Waste Type
            </label>
            <div className="relative">
              <Package className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <select
                id="waste-type-select"
                required
                value={formData.waste_type}
                onChange={(e) => setFormData({...formData, waste_type: e.target.value})}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600"
              >
                <option value="">Select waste type</option>
                {wasteTypes.map(type => (
                  <option key={type.id} value={type.name}>
                    {type.name} (₹{type.rate_per_kg}/kg)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="weight-input" className="block text-sm font-medium text-gray-700 mb-2">
              Weight (kg)
            </label>
            <div className="relative">
              <Scale className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <input
                id="weight-input"
                type="number"
                step="0.01"
                min="0"
                required
                value={formData.weight}
                onChange={(e) => setFormData({...formData, weight: e.target.value})}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600"
              />
            </div>
          </div>

          <div>
            <label htmlFor="rate-input" className="block text-sm font-medium text-gray-700 mb-2">
              Rate per kg (₹)
            </label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <input
                id="rate-input"
                type="number"
                step="0.01"
                min="0"
                required
                value={formData.rate}
                onChange={(e) => setFormData({...formData, rate: e.target.value})}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600"
              />
            </div>
          </div>

          <div>
            <label htmlFor="date-input" className="block text-sm font-medium text-gray-700 mb-2">
              Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <input
                id="date-input"
                type="date"
                required
                value={formData.date}
                onChange={(e) => setFormData({...formData, date: e.target.value})}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600"
              />
            </div>
          </div>

          <div>
            <label htmlFor="amount-input" className="block text-sm font-medium text-gray-700 mb-2">
              Total Amount (₹)
            </label>
            <input
              id="amount-input"
              type="text"
              readOnly
              value={calculateAmount()}
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 font-semibold"
            />
          </div>

          <div className="md:col-span-2">
            <label htmlFor="notes-textarea" className="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              id="notes-textarea"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-600 disabled:bg-green-400 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Processing...
            </>
          ) : (
            'Record Transaction'
          )}
        </button>
      </form>
    </div>
  );
};

export default TransactionForm;