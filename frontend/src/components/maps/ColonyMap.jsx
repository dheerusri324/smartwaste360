// frontend/src/components/maps/ColonyMap.jsx

import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import PropTypes from 'prop-types';

// This is a crucial fix for a known issue with React-Leaflet and Webpack/Create React App.
// It ensures the default marker icons are loaded correctly.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const ColonyMap = ({ center, colonies, userLocation, isCollector }) => {
  return (
    <MapContainer center={center} zoom={13} scrollWheelZoom={true} style={{ height: "100%", width: "100%" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* Show a marker for the user's current location if it exists */}
      {userLocation && (
        <Marker position={[userLocation.lat, userLocation.lng]}>
          <Popup>You are here.</Popup>
        </Marker>
      )}

      {/* Map over the colonies array to display a marker for each one */}
      {colonies.map(colony => (
        // Only render the marker if the colony has valid latitude and longitude
        (colony.latitude && colony.longitude) &&
        <Marker key={colony.colony_id} position={[colony.latitude, colony.longitude]}>
          <Popup>
            <b>{colony.colony_name}</b><br />
            {isCollector 
              ? `Current Weight: ${parseFloat(colony.current_dry_waste_kg).toFixed(2)} kg`
              : `Total Points: ${colony.total_points || 0}`
            }
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

// Define prop types for the component to prevent errors and add clarity
ColonyMap.propTypes = {
  center: PropTypes.arrayOf(PropTypes.number).isRequired,
  colonies: PropTypes.array.isRequired,
  userLocation: PropTypes.shape({
    lat: PropTypes.number,
    lng: PropTypes.number,
  }),
  isCollector: PropTypes.bool,
};

export default ColonyMap;