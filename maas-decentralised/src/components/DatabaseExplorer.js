import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';
import './DatabaseExplorer.css';

const DatabaseExplorer = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({
    runs: [],
    bundles: [],
    commuters: [],
    providers: [],
    requests: [],
    reservations: []
  });
  const [stats, setStats] = useState({});
  const [selectedRun, setSelectedRun] = useState(null);
  const [exportFormat, setExportFormat] = useState('excel');

  useEffect(() => {
    loadDatabaseStats();
    loadData();

    // Refresh stats every 5 seconds
    const interval = setInterval(loadDatabaseStats, 5000);
    return () => clearInterval(interval);
  }, [activeTab]);

  const loadDatabaseStats = async () => {
    try {
      const dbStats = await ApiService.getDatabaseStats();
      setStats(dbStats);
    } catch (error) {
      console.error('Error loading database stats:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await ApiService.getDatabaseData(activeTab);
      setData(prev => ({ ...prev, [activeTab]: response.data || [] }));
      if (response.stats) {
        setStats(prev => ({ ...prev, ...response.stats }));
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (table, format = 'excel') => {
    try {
      setLoading(true);
      const blob = await ApiService.exportDatabaseTable(table, format, selectedRun);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${table}_${selectedRun || 'all'}_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : 'csv'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExportBlockchain = async () => {
    try {
      setLoading(true);
      const blob = await ApiService.exportBlockchainData(exportFormat);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `blockchain_data_${new Date().toISOString().split('T')[0]}.${exportFormat === 'excel' ? 'xlsx' : 'csv'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Blockchain export error:', error);
      alert('Blockchain export failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderOverview = () => (
    <div className="overview-section">
      <h3>📊 Database Overview</h3>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🎮</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_runs || 0}</div>
            <div className="stat-label">Simulation Runs</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🎫</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_bundles || 0}</div>
            <div className="stat-label">Bundles Created</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_commuters || 0}</div>
            <div className="stat-label">Commuters</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🚗</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_providers || 0}</div>
            <div className="stat-label">Providers</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_requests || 0}</div>
            <div className="stat-label">Requests</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_reservations || 0}</div>
            <div className="stat-label">Reservations</div>
          </div>
        </div>
      </div>

      <div className="export-section">
        <h4>📥 Export Options</h4>
        <div className="export-controls">
          <select 
            value={exportFormat} 
            onChange={(e) => setExportFormat(e.target.value)}
            className="export-format-select"
          >
            <option value="excel">Excel (.xlsx)</option>
            <option value="csv">CSV (.csv)</option>
          </select>
          
          <button 
            className="btn btn-primary"
            onClick={() => handleExport('all', exportFormat)}
            disabled={loading}
          >
            📊 Export All Data
          </button>
          
          <button 
            className="btn btn-secondary"
            onClick={handleExportBlockchain}
            disabled={loading}
          >
            🔗 Export Blockchain Data
          </button>
        </div>
      </div>
    </div>
  );

  const renderTable = (tableName, columns, data) => (
    <div className="table-section">
      <div className="table-header">
        <h3>📋 {tableName}</h3>
        <div className="table-actions">
          <button 
            className="btn btn-sm btn-primary"
            onClick={() => handleExport(tableName.toLowerCase(), 'excel')}
            disabled={loading}
          >
            📥 Export Excel
          </button>
          <button 
            className="btn btn-sm btn-secondary"
            onClick={() => handleExport(tableName.toLowerCase(), 'csv')}
            disabled={loading}
          >
            📥 Export CSV
          </button>
          <button 
            className="btn btn-sm btn-info"
            onClick={loadData}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>
      
      {data && data.length > 0 ? (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map(col => (
                  <th key={col.key}>{col.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx}>
                  {columns.map(col => (
                    <td key={col.key}>
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <p>No data available</p>
          <small>Run a simulation with database export enabled</small>
        </div>
      )}
    </div>
  );

  const tabs = [
    { id: 'overview', label: '📊 Overview', icon: '📊' },
    { id: 'runs', label: '🎮 Simulation Runs', icon: '🎮' },
    { id: 'bundles', label: '🎫 Bundles', icon: '🎫' },
    { id: 'commuters', label: '👥 Commuters', icon: '👥' },
    { id: 'providers', label: '🚗 Providers', icon: '🚗' },
    { id: 'requests', label: '📝 Requests', icon: '📝' },
    { id: 'reservations', label: '✅ Reservations', icon: '✅' }
  ];

  const tableConfigs = {
    runs: {
      columns: [
        { key: 'run_id', label: 'Run ID' },
        { key: 'created_at', label: 'Created At', render: (val) => new Date(val).toLocaleString() },
        { key: 'steps', label: 'Steps' },
        { key: 'num_commuters', label: 'Commuters' },
        { key: 'num_providers', label: 'Providers' },
        { key: 'network', label: 'Network' }
      ]
    },
    bundles: {
      columns: [
        { key: 'bundle_id', label: 'Bundle ID' },
        { key: 'origin', label: 'Origin' },
        { key: 'destination', label: 'Destination' },
        { key: 'num_segments', label: 'Segments' },
        { key: 'total_price', label: 'Price', render: (val) => `$${parseFloat(val).toFixed(2)}` },
        { key: 'discount_amount', label: 'Discount', render: (val) => `$${parseFloat(val).toFixed(2)}` }
      ]
    },
    commuters: {
      columns: [
        { key: 'commuter_id', label: 'ID' },
        { key: 'position_x', label: 'X' },
        { key: 'position_y', label: 'Y' },
        { key: 'income_level', label: 'Income' },
        { key: 'created_at', label: 'Created', render: (val) => new Date(val).toLocaleString() }
      ]
    },
    providers: {
      columns: [
        { key: 'provider_id', label: 'ID' },
        { key: 'provider_type', label: 'Type' },
        { key: 'position_x', label: 'X' },
        { key: 'position_y', label: 'Y' },
        { key: 'capacity', label: 'Capacity' }
      ]
    },
    requests: {
      columns: [
        { key: 'request_id', label: 'Request ID' },
        { key: 'commuter_id', label: 'Commuter' },
        { key: 'origin', label: 'Origin' },
        { key: 'destination', label: 'Destination' },
        { key: 'status', label: 'Status' },
        { key: 'created_at', label: 'Created', render: (val) => new Date(val).toLocaleString() }
      ]
    },
    reservations: {
      columns: [
        { key: 'reservation_id', label: 'ID' },
        { key: 'bundle_id', label: 'Bundle' },
        { key: 'commuter_id', label: 'Commuter' },
        { key: 'status', label: 'Status' },
        { key: 'reserved_at', label: 'Reserved', render: (val) => new Date(val).toLocaleString() }
      ]
    }
  };

  return (
    <div className="database-explorer">
      <div className="page-header">
        <h1>🗄️ Database Explorer</h1>
        <p>View and export simulation data from database and blockchain</p>
      </div>

      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="tab-content">
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <span>Loading data...</span>
          </div>
        )}

        {activeTab === 'overview' && renderOverview()}
        {activeTab !== 'overview' && tableConfigs[activeTab] && 
          renderTable(
            tabs.find(t => t.id === activeTab).label,
            tableConfigs[activeTab].columns,
            data[activeTab]
          )
        }
      </div>
    </div>
  );
};

export default DatabaseExplorer;

