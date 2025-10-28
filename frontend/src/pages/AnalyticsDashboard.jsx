// frontend/src/pages/AnalyticsDashboard.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { 
  getCollectorPerformance, 
  getCollectorSummary,
  getRealtimeDashboard 
} from '../services/analytics';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Package,
  Clock,
  Zap,
  Calendar,
  Scale,
  Recycle,
  Activity
} from 'lucide-react';

const AnalyticsDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      // Load all dashboard data in parallel
      const [summaryData, performanceData, realtimeData] = await Promise.all([
        getCollectorSummary(),
        getCollectorPerformance(selectedPeriod),
        getRealtimeDashboard()
      ]);
      
      setSummary(summaryData.data);
      setPerformance(performanceData.data);
      setRealtimeData(realtimeData.data);
      
    } catch (err) {
      setError('Failed to load dashboard data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [selectedPeriod]);

  useEffect(() => {
    loadDashboardData();
    
    // Set up real-time updates every 30 seconds
    const interval = setInterval(loadRealtimeData, 30000);
    return () => clearInterval(interval);
  }, [loadDashboardData]);

  const loadRealtimeData = async () => {
    try {
      const data = await getRealtimeDashboard();
      setRealtimeData(data.data);
    } catch (err) {
      console.error('Failed to update real-time data:', err);
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
      <span className={`flex items-center gap-1 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
        {Math.abs(growth).toFixed(1)}%
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto"></div>
        <p className="text-center mt-2">Loading analytics...</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            <BarChart3 className="text-emerald-600" />
            Performance Analytics
          </h1>
          <p className="text-gray-600 mt-1">Track your collection efficiency and environmental impact</p>
        </div>
        
        <div className="flex gap-2">
          {[7, 30, 90].map(days => (
            <button
              key={days}
              onClick={() => setSelectedPeriod(days)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedPeriod === days
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {days} Days
            </button>
          ))}
        </div>
      </div>

      {/* Quick Stats Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Collections (7d)</p>
                <p className="text-2xl font-bold text-gray-900">{summary.current_period.collections}</p>
                {formatGrowth(summary.growth_metrics.collection_growth_percent)}
              </div>
              <Package className="h-8 w-8 text-emerald-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Weight Collected</p>
                <p className="text-2xl font-bold text-gray-900">{formatWeight(summary.current_period.weight_collected)}</p>
                {formatGrowth(summary.growth_metrics.weight_growth_percent)}
              </div>
              <Scale className="h-8 w-8 text-emerald-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Efficiency Score</p>
                <p className="text-2xl font-bold text-gray-900">{summary.current_period.efficiency_score}</p>
                <p className="text-xs text-gray-500">Out of 100</p>
              </div>
              <Zap className="h-8 w-8 text-emerald-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Days</p>
                <p className="text-2xl font-bold text-gray-900">{summary.current_period.active_days}</p>
                <p className="text-xs text-gray-500">Last 7 days</p>
              </div>
              <Calendar className="h-8 w-8 text-emerald-600" />
            </div>
          </div>
        </div>
      )}

      {/* Real-time Status */}
      {realtimeData && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Activity className="text-emerald-600" />
            System Status (Real-time)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-600">{realtimeData.today_stats.todays_collections || 0}</p>
              <p className="text-sm text-gray-600">Today's Collections</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{formatWeight(realtimeData.today_stats.todays_weight)}</p>
              <p className="text-sm text-gray-600">Today's Weight</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{realtimeData?.current_status?.pending_collections || realtimeData?.pending_requests || 0}</p>
              <p className="text-sm text-gray-600">Pending Collections</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">{realtimeData.ready_colonies_count || 0}</p>
              <p className="text-sm text-gray-600">Ready Colonies</p>
            </div>
          </div>
        </div>
      )}

      {/* Performance Charts */}
      {performance && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Trends */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Performance Trend</h3>
            <div className="space-y-3">
              {performance.daily_trends.slice(0, 7).map((day, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {new Date(day.collection_date).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-medium">{day.collections_count} collections</span>
                    <span className="text-sm text-gray-500">{formatWeight(day.daily_weight)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Waste Type Breakdown */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Waste Type Specialization</h3>
            <div className="space-y-3">
              {performance.waste_breakdown.slice(0, 5).map((waste, index) => {
                const percentage = performance.waste_breakdown.length > 0 
                  ? (waste.total_weight / performance.waste_breakdown.reduce((sum, w) => sum + parseFloat(w.total_weight), 0)) * 100 
                  : 0;
                
                return (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="capitalize font-medium">{waste.waste_type}</span>
                      <span>{formatWeight(waste.total_weight)} ({percentage.toFixed(1)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-emerald-600 h-2 rounded-full" 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {realtimeData && realtimeData.recent_activity && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Clock className="text-emerald-600" />
            Recent Activity
          </h3>
          
          <div className="space-y-3">
            {realtimeData.recent_activity.slice(0, 5).map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Recycle className="h-5 w-5 text-emerald-600" />
                  <div>
                    <p className="text-sm font-medium">{activity.colony_name}</p>
                    <p className="text-xs text-gray-600">
                      {activity.waste_types && activity.waste_types.length > 0 
                        ? activity.waste_types.join(', ') 
                        : 'Collection completed'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{formatWeight(activity.weight_collected || activity.total_weight_collected || 0)}</p>
                  <p className="text-xs text-gray-500">
                    {activity.time_ago || new Date(activity.completed_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;