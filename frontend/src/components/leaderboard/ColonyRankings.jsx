import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Crown, TrendingUp, Users, Award, Star } from 'lucide-react';

const ColonyRankings = ({ colonies, loading, onColonySelect }) => {
  const [timeFilter, setTimeFilter] = useState('all'); // 'all', 'month', 'week'

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Colony Rankings</h2>
          <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((item) => (
            <div key={item} className="animate-pulse flex items-center p-4 border border-gray-200 rounded-lg">
              <div className="h-8 w-8 bg-gray-200 rounded-full mr-4"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!colonies || colonies.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Colony Rankings</h2>
        <div className="text-center py-8 text-gray-500">
          <Trophy className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No colony rankings available yet.</p>
          <p className="text-sm">Colonies will appear here as they earn points.</p>
        </div>
      </div>
    );
  }

  // Sort colonies by points
  const sortedColonies = [...colonies].sort((a, b) => b.total_points - a.total_points);

  const getRankIcon = (rank) => {
    if (rank === 1) return <Crown className="w-5 h-5 text-yellow-500 fill-yellow-500" />;
    if (rank === 2) return <Award className="w-5 h-5 text-gray-400 fill-gray-400" />;
    if (rank === 3) return <Award className="w-5 h-5 text-amber-700 fill-amber-700" />;
    return <span className="text-sm font-semibold">{rank}</span>;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'bg-yellow-50 border-yellow-200';
    if (rank === 2) return 'bg-gray-50 border-gray-200';
    if (rank === 3) return 'bg-amber-50 border-amber-200';
    return 'bg-white border-gray-100';
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Colony Rankings</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setTimeFilter('week')}
            className={`px-3 py-1 rounded-lg text-sm ${
              timeFilter === 'week' 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Week
          </button>
          <button
            onClick={() => setTimeFilter('month')}
            className={`px-3 py-1 rounded-lg text-sm ${
              timeFilter === 'month' 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Month
          </button>
          <button
            onClick={() => setTimeFilter('all')}
            className={`px-3 py-1 rounded-lg text-sm ${
              timeFilter === 'all' 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All Time
          </button>
        </div>
      </div>

      <AnimatePresence>
        {sortedColonies.map((colony, index) => (
          <motion.div
            key={colony.colony_id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ delay: index * 0.1 }}
            className={`flex items-center p-4 border rounded-lg mb-3 hover:shadow-md transition-shadow cursor-pointer ${getRankColor(index + 1)}`}
            onClick={() => onColonySelect?.(colony)}
          >
            <div className="w-8 h-8 flex items-center justify-center mr-4">
              {getRankIcon(index + 1)}
            </div>
            
            <div className="flex-1">
              <h3 className="font-semibold text-gray-800">{colony.colony_name}</h3>
              <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                <span className="flex items-center">
                  <Users className="w-3 h-3 mr-1" />
                  {colony.total_users || 0} members
                </span>
                <span className="flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {colony.weekly_growth || 0}% this week
                </span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="flex items-center justify-end space-x-2">
                <Star className="w-4 h-4 text-yellow-500" />
                <span className="font-bold text-lg text-gray-800">
                  {colony.total_points.toLocaleString()}
                </span>
              </div>
              <div className="text-sm text-gray-500 mt-1">points</div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center">
            <Crown className="w-4 h-4 text-yellow-500 fill-yellow-500 mr-1" />
            <span>1st Place</span>
          </div>
          <div className="flex items-center">
            <Award className="w-4 h-4 text-gray-400 fill-gray-400 mr-1" />
            <span>2nd Place</span>
          </div>
          <div className="flex items-center">
            <Award className="w-4 h-4 text-amber-700 fill-amber-700 mr-1" />
            <span>3rd Place</span>
          </div>
        </div>
      </div>
    </div>
  );
};

ColonyRankings.propTypes = {
  colonies: PropTypes.arrayOf(
    PropTypes.shape({
      colony_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      colony_name: PropTypes.string.isRequired,
      total_points: PropTypes.number.isRequired,
      total_users: PropTypes.number,
      weekly_growth: PropTypes.number,
    })
  ),
  loading: PropTypes.bool,
  onColonySelect: PropTypes.func,
};

ColonyRankings.defaultProps = {
  colonies: [],
  loading: false,
};

export default ColonyRankings;