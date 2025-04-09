import React from 'react';
import './EnvironmentalCard.css';

const EnvironmentalCard = ({ title, value, additionalClass = '' }) => {
  return (
    <div className={`environmental-card ${additionalClass}`}>
      <div className="environmental-card-header">
        <h2 className="environmental-card-title">{title}:</h2>
      </div>
      <div className="environmental-card-content">
        <p className="environmental-card-value">{value}</p>
      </div>
    </div>
  );
};

export default EnvironmentalCard;