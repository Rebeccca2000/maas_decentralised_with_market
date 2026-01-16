import React from 'react';

const MetricCard = ({ title, value, icon, color = '#3498db', subtitle }) => {
  return (
    <div className="dashboard-card">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '24px', marginRight: '12px' }}>{icon}</span>
        <h3 style={{ margin: 0, color: '#2c3e50' }}>{title}</h3>
      </div>
      
      <div className="metric-value" style={{ color }}>
        {value}
      </div>
      
      {subtitle && (
        <div className="metric-label">
          {subtitle}
        </div>
      )}
    </div>
  );
};

export default MetricCard;
