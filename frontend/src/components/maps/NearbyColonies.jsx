// frontend/src/components/maps/NearbyColonies.jsx
import React from 'react';
import { Package } from 'lucide-react';

const NearbyColonies = ({ colonies, loading, isCollector }) => {
  if (loading) return <p>Searching for locations...</p>;

  return (
    <div>
      <ul className="space-y-3">
        {colonies.length > 0 ? (
          colonies.map(colony => (
            <li key={colony.colony_id} className="p-3 bg-gray-50 rounded-md border">
              <p className="font-semibold text-emerald-700">{colony.colony_name}</p>
              <p className="text-sm text-gray-600">
                {isCollector 
                  ? `Weight: ${parseFloat(colony.current_dry_waste_kg).toFixed(2)} kg`
                  : `Points: ${colony.total_points || 0}`
                }
              </p>
            </li>
          ))
        ) : (
          <div className="text-center text-gray-500 p-6">
            <Package size={48} className="mx-auto mb-2 text-gray-400" />
            <p>No locations found matching your criteria.</p>
          </div>
        )}
      </ul>
    </div>
  );
};

export default NearbyColonies;