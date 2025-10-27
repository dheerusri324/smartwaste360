// frontend/src/components/dashboard/CollectorStatsWidget.jsx

import React, { useState, useEffect } from 'react';
import { getCollectorSummary } from '../../services/analytics';
import { 
  Package, 
  Scale, 
  Zap, 
  Calendar, 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

const CollectorStatsWidget = () => {
  const [summary, setSummary] = useState({
    current_period: {
      collections: 0,
      weight: 0,
      rating: 0,
      pending: 0
    },
    growth_metrics: {
      collection_growth_percent: 0,
      weight_growth_percent: 0
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const response = await getCollectorSummary();
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to load collector summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatWeight = (weight) => {
    if (!weight) return '0 kg';
    const num = parseFloat(weight);
    return num >= 1000 ? `${(num / 1000).toFixed(1)}t` : `${num.toFixed(1)}kg`;
  };

  const formatGrowth = (growth) => {
    if (!growth || growth === 0) return null;
    const isPositive = growth > 0;
    return (
      <span className={`flex items-center gap-1 text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
        {Math.abs(growth).toFixed(1)}%
      </span>
    );
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <p className="text-gray-500 text-center">Unable to load performance data</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Performance Overview</h3>
        <Link 
          to="/collector/analytics"
          className="flex items-center gap-1 text-emerald-600 hover:text-emerald-700 text-sm font-medium"
        >
          <BarChart3 size={16} />
          View Details
          <ArrowRight size={14} />
        </Link>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Collections */}
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Package className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
          <p className="text-xl font-bold text-gray-900">{summary?.current_period?.collections || 0}</p>
          <p className="text-xs text-gray-600">Collections (7d)</p>
          {formatGrowth(summary?.growth_metrics?.collection_growth_percent || 0)}
        </div>

        {/* Weight */}
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Scale className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
          <p className="text-xl font-bold text-gray-900">{formatWeight(summary?.current_period?.weight_collected || 0)}</p>
          <p className="text-xs text-gray-600">Weight Collected</p>
          {formatGrowth(summary?.growth_metrics?.weight_growth_percent || 0)}
        </div>

        {/* Efficiency */}
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Zap className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
          <p className="text-xl font-bold text-gray-900">{summary?.current_period?.efficiency_score || 0}</p>
          <p className="text-xs text-gray-600">Efficiency Score</p>
        </div>

        {/* Active Days */}
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Calendar className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
          <p className="text-xl font-bold text-gray-900">{summary?.current_period?.active_days || 0}</p>
          <p className="text-xs text-gray-600">Active Days</p>
        </div>
      </div>

      {/* Recent Performance Trend */}
      {summary?.performance_trends && summary.performance_trends.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Activity</h4>
          <div className="space-y-1">
            {summary.performance_trends.slice(0, 3).map((day, index) => (
              <div key={index} className="flex justify-between text-xs">
                <span className="text-gray-600">
                  {new Date(day.collection_date).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </span>
                <span className="font-medium">
                  {day.collections_count} collections • {formatWeight(day.daily_weight)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Waste Specialization */}
      {summary?.waste_specialization && summary.waste_specialization.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Top Waste Types</h4>
          <div className="flex gap-2">
            {summary.waste_specialization.slice(0, 3).map((waste, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-full capitalize"
              >
                {waste.waste_type}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CollectorStatsWidget;