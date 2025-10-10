import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Award, TrendingUp, Star, Calendar } from 'lucide-react';

const UserRankings = ({ users, currentUserId, loading, timeFilter: initialTimeFilter = 'all' }) => {
  const [timeFilter, setTimeFilter] = useState(initialTimeFilter); // 'all', 'month', 'week'

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">User Rankings</h2>
          <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((item) => (
            <div key={item} className="animate-pulse flex items-center p-4 border border-gray-200 rounded-lg">
              <div className="h-10 w-10 bg-gray-200 rounded-full mr-4"></div>
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

  if (!users || users.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">User Rankings</h2>
        <div className="text-center py-8 text-gray-500">
          <User className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No user rankings available yet.</p>
          <p className="text-sm">Users will appear here as they earn points.</p>
        </div>
      </div>
    );
  }

  // Sort users by points
  const sortedUsers = [...users].sort((a, b) => b.total_points - a.total_points);

  const getRankBadge = (rank) => {
    if (rank === 1) return { color: 'bg-yellow-100 text-yellow-800', text: '1st' };
    if (rank === 2) return { color: 'bg-gray-100 text-gray-800', text: '2nd' };
    if (rank === 3) return { color: 'bg-amber-100 text-amber-800', text: '3rd' };
    return { color: 'bg-gray-100 text-gray-800', text: rank };
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">User Rankings</h2>
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
        {sortedUsers.map((user, index) => {
          const rank = index + 1;
          const rankBadge = getRankBadge(rank);
          const isCurrentUser = user.user_id === currentUserId;
          
          return (
            <motion.div
              key={user.user_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-center p-4 border rounded-lg mb-3 ${
                isCurrentUser 
                  ? 'bg-green-50 border-green-200 ring-2 ring-green-100' 
                  : 'bg-white border-gray-100'
              }`}
            >
              <div className={`w-8 h-8 flex items-center justify-center rounded-full ${rankBadge.color} mr-4`}>
                <span className="text-xs font-bold">{rankBadge.text}</span>
              </div>
              
              <div className="flex-1">
                <div className="flex items-center">
                  <h3 className="font-semibold text-gray-800">
                    {user.full_name || user.username}
                  </h3>
                  {isCurrentUser && (
                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      You
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                  <span className="flex items-center">
                    <Calendar className="w-3 h-3 mr-1" />
                    Joined {new Date(user.created_at).toLocaleDateString()}
                  </span>
                  <span className="flex items-center">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {user.weekly_points || 0} this week
                  </span>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center justify-end space-x-2">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="font-bold text-lg text-gray-800">
                    {user.total_points.toLocaleString()}
                  </span>
                </div>
                <div className="text-sm text-gray-500 mt-1">points</div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};

UserRankings.propTypes = {
  users: PropTypes.arrayOf(
    PropTypes.shape({
      user_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      username: PropTypes.string.isRequired,
      full_name: PropTypes.string,
      total_points: PropTypes.number.isRequired,
      weekly_points: PropTypes.number,
      created_at: PropTypes.string,
    })
  ),
  currentUserId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  loading: PropTypes.bool,
  timeFilter: PropTypes.oneOf(['all', 'month', 'week']),
};

UserRankings.defaultProps = {
  users: [],
  loading: false,
  timeFilter: 'all',
};

export default UserRankings;