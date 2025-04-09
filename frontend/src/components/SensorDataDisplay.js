import React from 'react';
import EnvironmentalCard from './EnvironmentalCard';
import './SensorDataDisplay.css';

const SensorDataDisplay = ({ sensorData }) => {
  return (
    <div className="sensor-data-container">
      <EnvironmentalCard 
        title="Temperature" 
        value={`${sensorData.temperature}°C`} 
        additionalClass="temperature-card"
      />
      <EnvironmentalCard 
        title="Humidity" 
        value={`${sensorData.humidity}%`} 
        additionalClass="humidity-card"
      />
      <EnvironmentalCard 
        title="Luminance" 
        value={`${sensorData.luminance} lux`} 
        additionalClass="luminance-card"
      />
      <EnvironmentalCard 
        title="Last Updated" 
        value={sensorData.lastUpdated} 
        additionalClass="last-updated-card"
      />
    </div>
  );
};

export default SensorDataDisplay;