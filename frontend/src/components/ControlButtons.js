import React, { useState } from 'react';
import './ControlButtons.css';

function ControlButtons({ acStatus, lightsStatus, onToggleAC, onToggleLights }) {
  const [acLoading, setAcLoading] = useState(false);
  const [lightsLoading, setLightsLoading] = useState(false);

  const handleACToggle = async () => {
    setAcLoading(true);
    await onToggleAC();
    setAcLoading(false);
  };

  const handleLightsToggle = async () => {
    setLightsLoading(true);
    await onToggleLights();
    setLightsLoading(false);
  };

  return (
    <div className="control-buttons-container">
      <button
        className={`control-button control-button-ac ${acStatus ? 'active' : ''}`}
        onClick={handleACToggle}
        disabled={acLoading}
      >
        {acLoading ? <span className="spinner"></span> : acStatus ? 'Turn AC Off' : 'Turn AC On'}
      </button>

      <button
        className={`control-button control-button-lights ${lightsStatus ? 'active' : ''}`}
        onClick={handleLightsToggle}
        disabled={lightsLoading}
      >
        {lightsLoading ? <span className="spinner"></span> : lightsStatus ? 'Turn Lights Off' : 'Turn Lights On'}
      </button>
    </div>
  );
}

export default ControlButtons;
