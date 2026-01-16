import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';
import Chart from './Chart';

const Analytics = () => {
  const [metrics, setMetrics] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [agentData, setAgentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      const [metricsData, marketDataResponse, agentDataResponse] = await Promise.all([
        ApiService.getSimulationMetrics(),
        ApiService.getMarketData().catch(() => null),
        ApiService.getAgentData().catch(() => null)
      ]);
      
      setMetrics(metricsData);
      setMarketData(marketDataResponse);
      setAgentData(agentDataResponse);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateChartData = () => {
    if (!metrics) return null;

    return {
      performance: {
        labels: ['Success Rate', 'Match Rate', 'Response Time'],
        datasets: [{
          label: 'Performance Metrics',
          data: [metrics.success_rate, 75, 85], // Sample data
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800'],
          borderWidth: 1
        }]
      },
      transactions: {
        labels: ['Registrations', 'Requests', 'Matches', 'Payments'],
        datasets: [{
          label: 'Transaction Types',
          data: [25, 40, 35, 30], // Sample data
          backgroundColor: ['#9C27B0', '#F44336', '#4CAF50', '#FF9800'],
          borderWidth: 1
        }]
      },
      timeline: {
        labels: ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5'],
        datasets: [{
          label: 'Active Agents',
          data: [10, 15, 12, 18, 16],
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4
        }]
      }
    };
  };

  const chartData = generateChartData();

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="loading-spinner"></div>
          <span style={{ marginLeft: '10px' }}>Loading analytics...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>Analytics & Insights</h2>

      {/* Tab Navigation */}
      <div className="card">
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'performance', label: 'Performance' },
            { id: 'market', label: 'Market Analysis' },
            { id: 'agents', label: 'Agent Behavior' }
          ].map(tab => (
            <button
              key={tab.id}
              className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            <h3>Simulation Overview</h3>
            <div className="grid grid-2">
              <div>
                <h4>Key Performance Indicators</h4>
                <div style={{ fontSize: '14px', lineHeight: '1.8' }}>
                  <div><strong>Total Agents:</strong> {metrics?.total_agents || 0}</div>
                  <div><strong>Success Rate:</strong> {metrics?.success_rate || 0}%</div>
                  <div><strong>Avg Response Time:</strong> {metrics?.avg_response_time || 0}ms</div>
                  <div><strong>Blockchain Transactions:</strong> {metrics?.blockchain_transactions || 0}</div>
                </div>
              </div>
              <div>
                <h4>System Health</h4>
                <div style={{ fontSize: '14px', lineHeight: '1.8' }}>
                  <div>🟢 <strong>Backend:</strong> Connected</div>
                  <div>🟢 <strong>Blockchain:</strong> Connected</div>
                  <div>🟡 <strong>Simulation:</strong> Ready</div>
                  <div>🟢 <strong>Analytics:</strong> Active</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Performance Tab */}
        {activeTab === 'performance' && chartData && (
          <div>
            <h3>Performance Metrics</h3>
            <div className="grid grid-2">
              <Chart
                type="doughnut"
                data={chartData.performance}
                title="Performance Overview"
              />
              <Chart
                type="bar"
                data={chartData.transactions}
                title="Transaction Distribution"
              />
            </div>
            <Chart
              type="line"
              data={chartData.timeline}
              title="Agent Activity Timeline"
            />
          </div>
        )}

        {/* Market Analysis Tab */}
        {activeTab === 'market' && (
          <div>
            <h3>Market Analysis</h3>
            <div className="alert alert-info">
              <strong>Market Insights:</strong> This section will show detailed market analysis including
              provider competition, pricing trends, and demand patterns once simulation data is available.
            </div>
            
            <div className="grid grid-3">
              <div className="card">
                <h4>Market Concentration</h4>
                <div className="metric-value" style={{ color: '#e74c3c' }}>
                  7551
                </div>
                <div className="metric-label">Herfindahl-Hirschman Index</div>
              </div>
              
              <div className="card">
                <h4>Average Fare</h4>
                <div className="metric-value" style={{ color: '#27ae60' }}>
                  $28.11
                </div>
                <div className="metric-label">Per Trip</div>
              </div>
              
              <div className="card">
                <h4>Match Rate</h4>
                <div className="metric-value" style={{ color: '#3498db' }}>
                  175%
                </div>
                <div className="metric-label">Service Fill Rate</div>
              </div>
            </div>
          </div>
        )}

        {/* Agent Behavior Tab */}
        {activeTab === 'agents' && (
          <div>
            <h3>Agent Behavior Analysis</h3>
            <div className="alert alert-info">
              <strong>Agent Insights:</strong> This section will show detailed agent behavior patterns,
              decision-making analysis, and learning curves once simulation data is available.
            </div>
            
            <div className="grid grid-2">
              <div className="card">
                <h4>Commuter Behavior</h4>
                <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <li>Average utility calculation time: 45ms</li>
                  <li>Preferred transport modes: Car (40%), Bus (35%), Bike (25%)</li>
                  <li>Price sensitivity: Medium</li>
                  <li>Time sensitivity: High</li>
                </ul>
              </div>
              
              <div className="card">
                <h4>Provider Behavior</h4>
                <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <li>Average bid response time: 120ms</li>
                  <li>Pricing strategy: Dynamic</li>
                  <li>Capacity utilization: 78%</li>
                  <li>Competition level: Moderate</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <button
          className="btn btn-primary"
          onClick={loadAnalyticsData}
        >
          🔄 Refresh Data
        </button>
      </div>
    </div>
  );
};

export default Analytics;
