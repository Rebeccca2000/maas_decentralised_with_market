import React from 'react';

const StatusIndicator = ({ 
  status, 
  label, 
  showLabel = true, 
  size = 'medium' 
}) => {
  const getStatusClass = (status) => {
    switch (status) {
      case 'connected':
      case 'success':
      case 'active':
        return 'status-connected';
      case 'disconnected':
      case 'error':
      case 'failed':
        return 'status-disconnected';
      case 'pending':
      case 'loading':
      case 'running':
        return 'status-pending';
      default:
        return 'status-disconnected';
    }
  };

  const sizeStyles = {
    small: { width: '8px', height: '8px' },
    medium: { width: '12px', height: '12px' },
    large: { width: '16px', height: '16px' }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span 
        className={`status-indicator ${getStatusClass(status)}`}
        style={sizeStyles[size]}
        title={`Status: ${status}`}
      />
      {showLabel && label && <span>{label}</span>}
    </div>
  );
};

export default StatusIndicator;
