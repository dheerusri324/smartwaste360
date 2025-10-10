import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { Award, Trophy, Star, Zap, Flame, Target, CheckCircle, Lock } from 'lucide-react';

const AchievementBadges = ({ achievements, loading }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Achievement Badges</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((item) => (
            <div key={item} className="animate-pulse bg-gray-100 rounded-lg p-4 aspect-square flex flex-col items-center justify-center">
              <div className="h-12 w-12 bg-gray-200 rounded-full mb-3"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!achievements || achievements.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Achievement Badges</h2>
        <div className="text-center py-8 text-gray-500">
          <Trophy className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No achievements yet.</p>
          <p className="text-sm">Complete challenges to earn badges!</p>
        </div>
      </div>
    );
  }

  const categories = ['all', 'recycling', 'community', 'collection', 'streak'];
  
  const filteredAchievements = selectedCategory === 'all' 
    ? achievements 
    : achievements.filter(achievement => achievement.category === selectedCategory);

  const getAchievementIcon = (type) => {
    const icons = {
      recycling: <Zap className="w-8 h-8" />,
      community: <Star className="w-8 h-8" />,
      collection: <Target className="w-8 h-8" />,
      streak: <Flame className="w-8 h-8" />,
    };
    return icons[type] || <Award className="w-8 h-8" />;
  };

  const getAchievementColor = (type) => {
    const colors = {
      recycling: 'text-green-500 bg-green-100',
      community: 'text-blue-500 bg-blue-100',
      collection: 'text-purple-500 bg-purple-100',
      streak: 'text-orange-500 bg-orange-100',
    };
    return colors[type] || 'text-gray-500 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Achievement Badges</h2>
      
      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-3 py-1 rounded-full text-sm capitalize ${
              selectedCategory === category 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {category}
          </button>
        ))}
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredAchievements.map((achievement, index) => (
          <motion.div
            key={achievement.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`flex flex-col items-center p-4 rounded-lg border ${
              achievement.earned 
                ? 'bg-white border-green-200' 
                : 'bg-gray-50 border-gray-200 opacity-60'
            }`}
          >
            <div className={`p-3 rounded-full mb-3 ${getAchievementColor(achievement.category)}`}>
              {achievement.earned ? (
                getAchievementIcon(achievement.category)
              ) : (
                <Lock className="w-8 h-8" />
              )}
            </div>
            
            <h3 className="font-semibold text-center text-gray-800 mb-1">
              {achievement.name}
            </h3>
            
            <p className="text-xs text-center text-gray-600 mb-2">
              {achievement.description}
            </p>
            
            {achievement.earned ? (
              <div className="flex items-center text-green-600 text-xs">
                <CheckCircle className="w-3 h-3 mr-1" />
                <span>Earned</span>
              </div>
            ) : (
              <div className="text-xs text-gray-500 text-center">
                {achievement.progress && (
                  <div className="w-full bg-gray-200 rounded-full h-1.5 mb-1">
                    <div 
                      className="bg-green-500 h-1.5 rounded-full" 
                      style={{ width: `${(achievement.progress.current / achievement.progress.target) * 100}%` }}
                    ></div>
                  </div>
                )}
                <span>
                  {achievement.progress 
                    ? `${achievement.progress.current}/${achievement.progress.target}` 
                    : 'Locked'
                  }
                </span>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

AchievementBadges.propTypes = {
  achievements: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      name: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      category: PropTypes.oneOf(['recycling', 'community', 'collection', 'streak']).isRequired,
      earned: PropTypes.bool.isRequired,
      progress: PropTypes.shape({
        current: PropTypes.number,
        target: PropTypes.number,
      }),
    })
  ),
  loading: PropTypes.bool,
};

AchievementBadges.defaultProps = {
  achievements: [],
  loading: false,
};

export default AchievementBadges;