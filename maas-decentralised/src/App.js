import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import SimulationControl from './components/SimulationControl';
import Analytics from './components/Analytics';
import BlockchainStatus from './components/BlockchainStatus';
import Results from './components/Results';
import BundleVisualization from './components/BundleVisualization';
import EnhancedBundleVisualization from './components/EnhancedBundleVisualization';
import DatabaseExplorer from './components/DatabaseExplorer';
import { ApiService } from './services/ApiService';
import './App.css';

function App() {
  const [systemStatus, setSystemStatus] = useState({
    backend_connected: false,
    blockchain_connected: false,
    simulation_running: false
  });

  const [currentSimulation, setCurrentSimulation] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Check system status on app load
    checkSystemStatus();
    
    // Set up periodic status checks
    const statusInterval = setInterval(checkSystemStatus, 5000);
    
    return () => clearInterval(statusInterval);
  }, []);

  const checkSystemStatus = async () => {
    try {
      const status = await ApiService.getSystemStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to check system status:', error);
      setSystemStatus(prev => ({
        ...prev,
        backend_connected: false
      }));
    }
  };

  const handleSimulationStart = (simulationData) => {
    setCurrentSimulation(simulationData);
  };

  const handleSimulationStop = () => {
    setCurrentSimulation(null);

    // Add completion notification
    const notification = {
      id: Date.now(),
      type: 'success',
      title: 'Simulation Complete!',
      message: 'Your simulation has finished successfully. Check Analytics for results.',
      timestamp: new Date().toISOString()
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-remove notification after 8 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 8000);
  };

  return (
    <Router>
      <div className="App">
        <Header systemStatus={systemStatus} />

        {/* Notification System */}
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 10000,
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}>
          {notifications.map(notification => (
            <div
              key={notification.id}
              style={{
                backgroundColor: notification.type === 'success' ? '#d4edda' : '#f8d7da',
                border: `1px solid ${notification.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
                color: notification.type === 'success' ? '#155724' : '#721c24',
                padding: '16px',
                borderRadius: '8px',
                minWidth: '300px',
                maxWidth: '400px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                animation: 'slideInRight 0.3s ease-out',
                position: 'relative'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{ fontSize: '18px' }}>
                  {notification.type === 'success' ? '🎉' : '⚠️'}
                </span>
                <strong style={{ fontSize: '16px' }}>{notification.title}</strong>
                <button
                  onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                  style={{
                    marginLeft: 'auto',
                    background: 'none',
                    border: 'none',
                    fontSize: '18px',
                    cursor: 'pointer',
                    color: 'inherit',
                    opacity: 0.7
                  }}
                >
                  ×
                </button>
              </div>
              <div style={{ fontSize: '14px', lineHeight: '1.4' }}>
                {notification.message}
              </div>
            </div>
          ))}
        </div>

        <main className="main-content">
          <Routes>
            <Route 
              path="/" 
              element={
                <Dashboard 
                  systemStatus={systemStatus}
                  currentSimulation={currentSimulation}
                />
              } 
            />
            <Route 
              path="/simulation" 
              element={
                <SimulationControl 
                  onSimulationStart={handleSimulationStart}
                  onSimulationStop={handleSimulationStop}
                  currentSimulation={currentSimulation}
                />
              } 
            />
            <Route 
              path="/analytics" 
              element={<Analytics />} 
            />
            <Route
              path="/blockchain"
              element={<BlockchainStatus />}
            />
            <Route
              path="/results"
              element={<Results />}
            />
            <Route
              path="/bundles"
              element={<EnhancedBundleVisualization />}
            />
            <Route
              path="/bundles-old"
              element={<BundleVisualization />}
            />
            <Route
              path="/database"
              element={<DatabaseExplorer />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
