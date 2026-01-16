import React from 'react';

const LoadingSpinner = ({ size = 'medium', text = 'Loading...' }) => {
  const sizeClasses = {
    small: { width: '16px', height: '16px' },
    medium: { width: '24px', height: '24px' },
    large: { width: '32px', height: '32px' }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <div 
        className="loading-spinner"
        style={sizeClasses[size]}
      />
      {text && <span>{text}</span>}
    </div>
  );
};

export default LoadingSpinner;
