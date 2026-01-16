import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = ({ systemStatus }) => {
  const location = useLocation();

  const getStatusIndicator = (connected) => (
    <span 
      className={`status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`}
      title={connected ? 'Connected' : 'Disconnected'}
    />
  );

  const isActive = (path) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-content">
        <div>
          <h1>🚀 MaaS Decentralized Platform</h1>
          <div className="header-subtitle">
            Mobility-as-a-Service with Blockchain & Agent-Based Modeling
          </div>
        </div>

        <nav>
          <ul className="nav-links">
            <li>
              <Link 
                to="/" 
                className={isActive('/') ? 'active' : ''}
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link 
                to="/simulation" 
                className={isActive('/simulation') ? 'active' : ''}
              >
                Simulation
              </Link>
            </li>
            <li>
              <Link 
                to="/analytics" 
                className={isActive('/analytics') ? 'active' : ''}
              >
                Analytics
              </Link>
            </li>
            <li>
              <Link
                to="/blockchain"
                className={isActive('/blockchain') ? 'active' : ''}
              >
                Blockchain
              </Link>
            </li>
            <li>
              <Link
                to="/results"
                className={isActive('/results') ? 'active' : ''}
              >
                Results
              </Link>
            </li>
            <li>
              <Link
                to="/bundles"
                className={isActive('/bundles') ? 'active' : ''}
              >
                🎫 Bundles
              </Link>
            </li>
            <li>
              <Link
                to="/database"
                className={isActive('/database') ? 'active' : ''}
              >
                🗄️ Database
              </Link>
            </li>
          </ul>
        </nav>

        <div className="status-bar">
          <div className="status-item">
            {getStatusIndicator(systemStatus.backend_connected)}
            Backend
          </div>
          <div className="status-item">
            {getStatusIndicator(systemStatus.blockchain_connected)}
            Blockchain
          </div>
          <div className="status-item">
            {systemStatus.simulation_running ? (
              <>
                <span className="status-indicator status-pending" />
                Simulation Running
              </>
            ) : (
              <>
                <span className="status-indicator status-connected" />
                Ready
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
