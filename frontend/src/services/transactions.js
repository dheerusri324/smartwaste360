// frontend/src/services/transactions.js
import api from './api';

export const getTransactions = async (filters = {}) => {
  let url = '/transaction/';
  const params = new URLSearchParams();
  
  if (filters.status) params.append('status', filters.status);
  if (filters.user_id) params.append('user_id', filters.user_id);
  if (filters.collector_id) params.append('collector_id', filters.collector_id);
  
  if (params.toString()) {
    url += '?' + params.toString();
  }
  
  const response = await api.get(url);
  return response.data;
};

export const getTransactionById = async (transactionId) => {
  const response = await api.get(`/transaction/${transactionId}`);
  return response.data;
};
