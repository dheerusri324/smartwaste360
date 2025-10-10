// frontend/src/hooks/useApi.js

import { useState, useEffect, useCallback } from 'react';

/**
 * A generic hook to fetch data from an API endpoint.
 * @param {function} apiFunc - The API service function to call (e.g., getWasteHistory).
 * @param {Array} params - An array of parameters to pass to the API function.
 * @returns {{data: any, loading: boolean, error: object|null, refetch: function}}
 */
export const useApi = (apiFunc, params = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFunc(...params);
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiFunc, ...params]); // Refetch when the function or its params change

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};