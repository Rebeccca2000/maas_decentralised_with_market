import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiService } from '../services/ApiService';
import MetricCard from './MetricCard';
import SimulationProgress from './SimulationProgress';

const Dashboard = ({ systemStatus, currentSimulation }) => {
  const [metrics, setMetrics] = useState({
    total_agents: 0,
    active_requests: 0,
    completed_matches: 0,
    blockchain_transactions: 0,
    success_rate: 0,
    avg_response_time: 0
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    
    // Set up periodic data refresh
    const interval = setInterval(loadDashboardData, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [metricsData, activityData] = await Promise.all([
        ApiService.getSimulationMetrics(),
        ApiService.getRecentTransactions()
      ]);
      
      setMetrics(metricsData);
      setRecentActivity(activityData.slice(0, 10)); // Show last 10 activities
      setLoading(false);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'registration': return '👤';
      case 'request': return '🚗';
      case 'match': return '✅';
      case 'payment': return '💰';
      default: return '📝';
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="loading-spinner"></div>
          <span style={{ marginLeft: '10px' }}>Loading dashboard...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      {/* System Status Alert */}
      {!systemStatus.backend_connected && (
        <div className="alert alert-danger">
          ⚠️ Backend connection lost. Some features may not work properly.
        </div>
      )}

      {!systemStatus.blockchain_connected && (
        <div className="alert alert-warning">
          ⚠️ Blockchain not connected. Make sure Hardhat node is running.
        </div>
      )}

      {/* Current Simulation Status */}
      {currentSimulation && (
        <SimulationProgress simulation={currentSimulation} />
      )}

      {/* Key Metrics */}
      <div className="dashboard-grid">
        <MetricCard
          title="Total Agents"
          value={metrics.total_agents}
          icon="🤖"
          color="#3498db"
        />
        <MetricCard
          title="Active Requests"
          value={metrics.active_requests}
          icon="🚗"
          color="#e74c3c"
        />
        <MetricCard
          title="Completed Matches"
          value={metrics.completed_matches}
          icon="✅"
          color="#27ae60"
        />
        <MetricCard
          title="Blockchain Transactions"
          value={metrics.blockchain_transactions}
          icon="⛓️"
          color="#9b59b6"
        />
        <MetricCard
          title="Success Rate"
          value={`${metrics.success_rate}%`}
          icon="📊"
          color="#f39c12"
        />
        <MetricCard
          title="Avg Response Time"
          value={`${metrics.avg_response_time}ms`}
          icon="⚡"
          color="#1abc9c"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-2">
        <div className="card">
          <h3>Quick Actions</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <Link to="/simulation" className="btn btn-primary">
              Start New Simulation
            </Link>
            <Link to="/analytics" className="btn btn-success">
              View Analytics
            </Link>
            <Link to="/blockchain" className="btn btn-primary">
              Blockchain Status
            </Link>
          </div>
        </div>

        <div className="card">
          <h3>System Information</h3>
          <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
            <div><strong>Backend:</strong> {systemStatus.backend_connected ? '✅ Connected' : '❌ Disconnected'}</div>
            <div><strong>Blockchain:</strong> {systemStatus.blockchain_connected ? '✅ Connected' : '❌ Disconnected'}</div>
            <div><strong>Simulation:</strong> {systemStatus.simulation_running ? '🔄 Running' : '⏸️ Stopped'}</div>
            <div><strong>Mode:</strong> React Web Interface</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3>Recent Activity</h3>
        {recentActivity.length > 0 ? (
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {recentActivity.map((activity, index) => (
              <div 
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: index < recentActivity.length - 1 ? '1px solid #eee' : 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '18px' }}>
                    {getActivityIcon(activity.type)}
                  </span>
                  <div>
                    <div style={{ fontWeight: '500' }}>{activity.description}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {activity.details}
                    </div>
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  {formatTime(activity.timestamp)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            No recent activity. Start a simulation to see live updates.
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
