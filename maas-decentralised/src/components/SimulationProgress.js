import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';

const SimulationProgress = ({ simulation }) => {
  const [progress, setProgress] = useState({
    current_step: 0,
    total_steps: 0,
    progress_percentage: 0,
    estimated_time_remaining: 0,
    status: 'running'
  });
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);
  const [previousStatus, setPreviousStatus] = useState('running');

  // Function to play beep sound
  const playBeepSound = () => {
    try {
      // Create audio context for beep sound
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800; // Frequency in Hz
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
      console.log('Could not play beep sound:', error);
    }
  };

  // Function to show browser notification
  const showBrowserNotification = () => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🎉 Simulation Complete!', {
        body: 'Your MaaS simulation has finished successfully. Click to view results.',
        icon: '/favicon.ico',
        tag: 'simulation-complete',
        requireInteraction: true
      });
    } else if ('Notification' in window && Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification('🎉 Simulation Complete!', {
            body: 'Your MaaS simulation has finished successfully. Click to view results.',
            icon: '/favicon.ico',
            tag: 'simulation-complete',
            requireInteraction: true
          });
        }
      });
    }
  };

  // Request notification permission on component mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  useEffect(() => {
    if (!simulation) return;

    const fetchProgress = async () => {
      try {
        const progressData = await ApiService.getSimulationProgress();

        // Check if simulation just completed
        if (previousStatus === 'running' &&
            (progressData.status === 'completed' || progressData.progress_percentage >= 100)) {
          setShowCompletionMessage(true);
          playBeepSound();
          showBrowserNotification();

          // Hide completion message after 10 seconds
          setTimeout(() => {
            setShowCompletionMessage(false);
          }, 10000);
        }

        setPreviousStatus(progressData.status);
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
  }, [simulation, previousStatus]);

  if (!simulation) return null;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

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
    <>
      {/* Completion Message Modal */}
      {showCompletionMessage && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          animation: 'fadeIn 0.3s ease-in'
        }}>
          <div style={{
            backgroundColor: '#fff',
            padding: '40px',
            borderRadius: '16px',
            textAlign: 'center',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
            maxWidth: '500px',
            margin: '20px',
            animation: 'slideIn 0.3s ease-out'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>🎉</div>
            <h2 style={{
              color: '#28a745',
              margin: '0 0 16px 0',
              fontSize: '28px',
              fontWeight: 'bold'
            }}>
              Simulation Complete!
            </h2>
            <p style={{
              fontSize: '18px',
              color: '#666',
              margin: '0 0 24px 0',
              lineHeight: '1.5'
            }}>
              Your simulation has finished successfully.<br/>
              Check the Analytics page for detailed results!
            </p>
            <div style={{
              backgroundColor: '#f8f9fa',
              padding: '16px',
              borderRadius: '8px',
              marginBottom: '24px'
            }}>
              <div style={{ fontSize: '14px', color: '#666' }}>
                <strong>Configuration:</strong> {simulation.commuters} commuters, {simulation.providers} providers, {simulation.steps} steps
              </div>
            </div>
            <button
              onClick={() => setShowCompletionMessage(false)}
              style={{
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#218838'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#28a745'}
            >
              View Results
            </button>
          </div>
        </div>
      )}

      <div className={`simulation-status ${progress.status === 'completed' ? 'completed' : 'running'}`}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '20px' }}>
              {getStatusIcon(progress.status)}
            </span>
            <div>
              <h3 style={{ margin: 0, color: '#2c3e50' }}>
                {progress.status === 'completed' ? 'Simulation Complete!' : 'Simulation Running'}
              </h3>
              <div style={{ fontSize: '14px', color: '#666' }}>
                {simulation.commuters} commuters, {simulation.providers} providers, {simulation.steps} steps
              </div>
            </div>
          </div>
        
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: getStatusColor(progress.status) }}>
            {progress.progress_percentage}%
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            Step {progress.current_step} of {progress.total_steps}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ 
        width: '100%', 
        height: '8px', 
        backgroundColor: '#e9ecef', 
        borderRadius: '4px',
        overflow: 'hidden',
        marginBottom: '12px'
      }}>
        <div style={{
          width: `${progress.progress_percentage}%`,
          height: '100%',
          backgroundColor: getStatusColor(progress.status),
          transition: 'width 0.3s ease'
        }} />
      </div>

      {/* Additional Info */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', color: '#666' }}>
        <span>
          Status: <strong style={{ color: getStatusColor(progress.status) }}>
            {progress.status.charAt(0).toUpperCase() + progress.status.slice(1)}
          </strong>
        </span>
        {progress.estimated_time_remaining > 0 && (
          <span>
            ETA: <strong>{formatTime(progress.estimated_time_remaining)}</strong>
          </span>
        )}
      </div>

      {/* Add CSS animations */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-50px) scale(0.9);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        .simulation-status.completed {
          border-left-color: #28a745 !important;
          background: #d4edda !important;
        }
      `}</style>
    </div>
    </>
  );
};

export default SimulationProgress;
