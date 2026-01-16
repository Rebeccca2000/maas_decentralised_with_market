import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';
// Using existing AnimatedMap.css for styling

const ProgressDisplay = ({ isRunning, simulationData }) => {
  const [progress, setProgress] = useState({
    current_step: 0,
    total_steps: 0,
    progress_percentage: 0,
    status: 'stopped'
  });

  // Fetch progress data when simulation is running
  useEffect(() => {
    if (!isRunning) {
      setProgress({
        current_step: 0,
        total_steps: 0,
        progress_percentage: 0,
        status: 'stopped'
      });
      return;
    }

    const fetchProgress = async () => {
      try {
        const progressData = await ApiService.getSimulationProgress();
        setProgress(progressData);
      } catch (error) {
        console.error('Failed to fetch simulation progress:', error);
      }
    };

    // Initial fetch
    fetchProgress();

    // Set up periodic updates
    const interval = setInterval(fetchProgress, 1000);

    return () => clearInterval(interval);
  }, [isRunning]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return '#ffc107';
      case 'completed': return '#28a745';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return '🔄';
      case 'completed': return '✅';
      case 'error': return '❌';
      default: return '⏸️';
    }
  };

  return (
    <div className="animated-map">
      <div style={{
        width: '100%',
        maxWidth: '800px',
        margin: '20px auto',
        padding: '40px',
        backgroundColor: '#f8f9fa',
        borderRadius: '12px',
        border: '2px solid #e9ecef',
        textAlign: 'center'
      }}>
        {/* Status Icon and Title */}
        <div style={{ marginBottom: '30px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>
            {getStatusIcon(progress.status)}
          </div>
          <h3 style={{ 
            margin: 0, 
            color: '#2c3e50',
            fontSize: '24px',
            fontWeight: 'bold'
          }}>
            {progress.status === 'running' ? 'Simulation Running' : 
             progress.status === 'completed' ? 'Simulation Complete!' : 
             'Simulation Stopped'}
          </h3>
        </div>

        {/* Progress Information */}
        {isRunning && (
          <>
            {/* Large Progress Percentage */}
            <div style={{
              fontSize: '72px',
              fontWeight: 'bold',
              color: getStatusColor(progress.status),
              marginBottom: '20px',
              fontFamily: 'monospace'
            }}>
              {progress.progress_percentage}%
            </div>

            {/* Progress Bar */}
            <div style={{
              width: '100%',
              height: '20px',
              backgroundColor: '#e9ecef',
              borderRadius: '10px',
              overflow: 'hidden',
              marginBottom: '20px',
              border: '1px solid #dee2e6'
            }}>
              <div style={{
                width: `${progress.progress_percentage}%`,
                height: '100%',
                backgroundColor: getStatusColor(progress.status),
                transition: 'width 0.5s ease',
                borderRadius: '10px'
              }} />
            </div>

            {/* Step Information */}
            <div style={{
              fontSize: '18px',
              color: '#666',
              marginBottom: '20px'
            }}>
              Step {progress.current_step} of {progress.total_steps}
            </div>
          </>
        )}

        {/* Simulation Configuration */}
        {simulationData && (
          <div style={{
            backgroundColor: '#fff',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #dee2e6',
            marginTop: '20px'
          }}>
            <h4 style={{ margin: '0 0 16px 0', color: '#495057' }}>Configuration</h4>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '16px',
              fontSize: '14px'
            }}>
              <div>
                <strong>Commuters:</strong><br/>
                <span style={{ color: '#007bff', fontSize: '18px', fontWeight: 'bold' }}>
                  {simulationData.commuters}
                </span>
              </div>
              <div>
                <strong>Providers:</strong><br/>
                <span style={{ color: '#28a745', fontSize: '18px', fontWeight: 'bold' }}>
                  {simulationData.providers}
                </span>
              </div>
              <div>
                <strong>Steps:</strong><br/>
                <span style={{ color: '#ffc107', fontSize: '18px', fontWeight: 'bold' }}>
                  {simulationData.steps}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Status Message */}
        {!isRunning && (
          <div style={{
            backgroundColor: '#e9ecef',
            padding: '20px',
            borderRadius: '8px',
            marginTop: '20px',
            color: '#6c757d',
            fontSize: '16px'
          }}>
            {progress.status === 'completed' ? 
              '🎉 Simulation completed successfully! Check Analytics for detailed results.' :
              '⏸️ No simulation running. Start a simulation to see progress here.'
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressDisplay;
