import React, { useState, useEffect } from 'react';
import SensorDataDisplay from './components/SensorDataDisplay';
import ControlButtons from './components/ControlButtons';
import './App.css';

function App() {
  const [sensorData, setSensorData] = useState({
    temperature: 0,
    humidity: 0,
    luminance: 0,
    lastUpdated: 'Loading...'
  });

  const [acStatus, setAcStatus] = useState(false);
  const [lightsStatus, setLightsStatus] = useState(false);
  const [error, setError] = useState('');

  const fetchSensorData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/sensors?deviceId=esp32_01`);
    
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Sensor data received:", data);

      if (data && typeof data === 'object') {
        setSensorData({
          temperature: data.temperature || 0,
          humidity: data.humidity || 0,
          luminance: data.luminance || 0,
          lastUpdated: data.time || new Date().toLocaleString()
        });
        setError('');
        
      } else {
        throw new Error('Invalid data format received');
      }
      
    } catch (error) {
      console.error('Error fetching sensor data:', error);
      setError(`Error fetching sensor data: ${error.message}`);
    }
  };

  const toggleAC = async () => {
    try {
      const newStatus = !acStatus;
      console.log("Toggling AC to:", newStatus);
      
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/control/ac`, { 
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus }) 
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle AC: ${response.status}`);
      }
      
      const result = await response.json();
      console.log("AC toggle result:", result);

      if (result.success) {
        setAcStatus(newStatus);
      }
      
    } catch (error) {
      console.error('Error toggling AC:', error);
      setError(`Error toggling AC: ${error.message}`);
    }
  };

  const toggleLights = async () => {
    try {
      const newStatus = !lightsStatus;
      console.log("Toggling lights to:", newStatus);

      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/control/lights`, { 
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus }) 
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle lights: ${response.status}`);
      }

      const result = await response.json();
      console.log("Lights toggle result:", result);

      if (result.success) {
        setLightsStatus(newStatus);
      }

    } catch (error) {
      console.error('Error toggling lights:', error);
      setError(`Error toggling lights: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchSensorData();

    const sensorInterval = setInterval(fetchSensorData, 10000);

    return () => {
      clearInterval(sensorInterval);
    };
  }, []);

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Building Dashboard</h1>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <SensorDataDisplay sensorData={sensorData} />

      <ControlButtons 
        acStatus={acStatus} 
        lightsStatus={lightsStatus} 
        onToggleAC={toggleAC} 
        onToggleLights={toggleLights} 
      />
    </div>
  );
}

export default App;