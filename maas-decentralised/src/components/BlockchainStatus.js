import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';

const BlockchainStatus = () => {
  const [blockchainStatus, setBlockchainStatus] = useState(null);
  const [contracts, setContracts] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBlockchainData();
    
    // Set up periodic refresh
    const interval = setInterval(loadBlockchainData, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadBlockchainData = async () => {
    try {
      const [statusData, contractsData, transactionsData] = await Promise.all([
        ApiService.getBlockchainStatus(),
        ApiService.getContractAddresses().catch(() => null),
        ApiService.getRecentTransactions().catch(() => [])
      ]);
      
      setBlockchainStatus(statusData);
      setContracts(contractsData);
      setRecentTransactions(transactionsData);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load blockchain data:', error);
      setLoading(false);
    }
  };

  const formatAddress = (address) => {
    if (!address || typeof address !== 'string') return 'N/A';
    if (address.length < 10) return address; // Return as-is if too short to format
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // TODO: Add toast notification
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="loading-spinner"></div>
          <span style={{ marginLeft: '10px' }}>Loading blockchain status...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>Blockchain Status</h2>

      {/* Connection Status */}
      <div className="card">
        <h3>Network Connection</h3>
        <div className="grid grid-2">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <span className={`status-indicator ${blockchainStatus?.connected ? 'status-connected' : 'status-disconnected'}`} />
              <strong>Status:</strong> {blockchainStatus?.connected ? 'Connected' : 'Disconnected'}
            </div>
            <div><strong>Network ID:</strong> {blockchainStatus?.network_id || 'Unknown'}</div>
            <div><strong>Node URL:</strong> {blockchainStatus?.node_url || 'N/A'}</div>
          </div>
          <div>
            <div><strong>Latest Block:</strong> #{blockchainStatus?.latest_block || 0}</div>
            <div><strong>Chain:</strong> Hardhat Local Network</div>
            <div><strong>Gas Price:</strong> 20 Gwei (estimated)</div>
          </div>
        </div>
      </div>

      {/* Smart Contracts */}
      <div className="card">
        <h3>Deployed Smart Contracts</h3>
        {contracts ? (
          <div className="grid grid-2">
            {Object.entries(contracts)
              .filter(([name, address]) => {
                // Filter out non-address fields and ensure it's a valid Ethereum address
                return address &&
                       typeof address === 'string' &&
                       address.startsWith('0x') &&
                       address.length === 42 &&
                       !['network', 'timestamp', 'deployer'].includes(name);
              })
              .map(([name, address]) => (
              <div key={name} style={{ 
                padding: '12px', 
                border: '1px solid #e1e5e9', 
                borderRadius: '6px',
                backgroundColor: '#f8f9fa'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                      {name.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>
                      {formatAddress(address)}
                    </div>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ fontSize: '12px', padding: '4px 8px' }}
                    onClick={() => copyToClipboard(address)}
                    title="Copy full address"
                  >
                    📋
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="alert alert-warning">
            No contracts deployed. Run deployment script first:
            <br />
            <code>npx hardhat run scripts/deploy.js --network localhost</code>
          </div>
        )}
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <h3>Recent Transactions</h3>
        {recentTransactions.length > 0 ? (
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {recentTransactions.map((tx, index) => (
              <div 
                key={index}
                style={{
                  padding: '12px',
                  border: '1px solid #e1e5e9',
                  borderRadius: '6px',
                  marginBottom: '8px',
                  backgroundColor: '#f8f9fa'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                      {tx.type || 'Transaction'}
                    </div>
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>
                      {tx.description || 'Blockchain transaction'}
                    </div>
                    <div style={{ fontSize: '12px', fontFamily: 'monospace', color: '#999' }}>
                      Hash: {formatAddress(tx.hash || '0x1234567890abcdef')}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px', color: '#666' }}>
                    <div>{tx.status || 'Confirmed'}</div>
                    <div>{new Date(tx.timestamp || Date.now()).toLocaleTimeString()}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            No recent transactions. Start a simulation to see blockchain activity.
          </div>
        )}
      </div>

      {/* Network Actions */}
      <div className="card">
        <h3>Network Actions</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={loadBlockchainData}
          >
            🔄 Refresh Status
          </button>
          <button
            className="btn btn-success"
            onClick={() => window.open('http://127.0.0.1:8545', '_blank')}
          >
            🌐 Open Node URL
          </button>
          <button
            className="btn btn-primary"
            onClick={() => {
              // TODO: Implement contract interaction
              alert('Contract interaction coming soon!');
            }}
          >
            📝 Interact with Contracts
          </button>
        </div>
      </div>

      {/* Instructions */}
      <div className="alert alert-info">
        <strong>Getting Started:</strong>
        <ol style={{ marginTop: '10px', marginBottom: 0 }}>
          <li>Make sure Hardhat node is running: <code>npx hardhat node</code></li>
          <li>Deploy contracts: <code>npx hardhat run scripts/deploy.js --network localhost</code></li>
          <li>Start a simulation to see blockchain transactions in action</li>
        </ol>
      </div>
    </div>
  );
};

export default BlockchainStatus;
