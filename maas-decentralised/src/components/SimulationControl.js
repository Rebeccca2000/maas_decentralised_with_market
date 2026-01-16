import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';
import ProgressDisplay from './ProgressDisplay';

const SimulationControl = ({ onSimulationStart, onSimulationStop, currentSimulation }) => {
  const [config, setConfig] = useState({
    steps: 50,
    commuters: 10,
    providers: 5,
    debug: false,
    no_plots: false,
    export_db: false,
    seed: null,
    network: 'localhost',
    rpc_url: '',
    chain_id: null,
    // Bundle configuration
    enable_bundles: true,
    max_bundle_segments: 4,
    bundle_discount_rate: 0.05,
    max_bundle_discount: 0.15
  });

  const [presets] = useState([
    { name: 'Debug Mode', steps: 20, commuters: 5, providers: 3, debug: true },
    { name: 'Small Test', steps: 30, commuters: 8, providers: 4, debug: false },
    { name: 'Medium Test', steps: 50, commuters: 15, providers: 8, debug: false },
    { name: 'Large Scale', steps: 100, commuters: 25, providers: 12, debug: false },
    { name: 'Research Mode', steps: 200, commuters: 50, providers: 20, debug: false }
  ]);

  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState(null);
  const [showNetworkHelp, setShowNetworkHelp] = useState(false);

  useEffect(() => {
    loadDefaultConfig();
  }, []);

  const loadDefaultConfig = async () => {
    try {
      const defaultConfig = await ApiService.getDefaultConfig();
      setConfig(prev => ({ ...prev, ...defaultConfig }));
    } catch (error) {
      console.error('Failed to load default config:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setConfig(prev => {
      const newConfig = {
        ...prev,
        [field]: value
      };

      // Auto-enable export_db when bundles are enabled
      if (field === 'enable_bundles' && value === true) {
        newConfig.export_db = true;
      }

      return newConfig;
    });
  };

  const handlePresetSelect = (preset) => {
    setConfig(prev => ({
      ...prev,
      ...preset,
      seed: prev.seed // Keep the current seed
    }));
  };

  const handleStartSimulation = async () => {
    setIsStarting(true);
    setError(null);

    try {
      const result = await ApiService.startSimulation(config);
      onSimulationStart({
        ...config,
        id: result.simulation_id,
        start_time: new Date().toISOString()
      });
    } catch (error) {
      setError(error.response?.data?.message || error.message);
    } finally {
      setIsStarting(false);
    }
  };

  const handleStopSimulation = async () => {
    try {
      await ApiService.stopSimulation();
      onSimulationStop();
    } catch (error) {
      setError(error.response?.data?.message || error.message);
    }
  };

  const generateRandomSeed = () => {
    const seed = Math.floor(Math.random() * 100000);
    handleInputChange('seed', seed);
  };

  return (
    <div className="container">
      <h2>Simulation Control</h2>

      {error && (
        <div className="alert alert-danger">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Preset Configurations */}
      <div className="card">
        <h3>Quick Start Presets</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {presets.map((preset, index) => (
            <button
              key={index}
              className="btn btn-primary"
              onClick={() => handlePresetSelect(preset)}
              style={{ fontSize: '14px' }}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>

      {/* Configuration Form */}
      <div className="simulation-form">
        <h3>Simulation Configuration</h3>
        
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Simulation Steps</label>
            <input
              type="number"
              className="form-input"
              value={config.steps}
              onChange={(e) => handleInputChange('steps', parseInt(e.target.value))}
              min="1"
              max="1000"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Number of Commuters</label>
            <input
              type="number"
              className="form-input"
              value={config.commuters}
              onChange={(e) => handleInputChange('commuters', parseInt(e.target.value))}
              min="1"
              max="100"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Number of Providers</label>
            <input
              type="number"
              className="form-input"
              value={config.providers}
              onChange={(e) => handleInputChange('providers', parseInt(e.target.value))}
              min="1"
              max="50"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Random Seed (optional)</label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="number"
                className="form-input"
                value={config.seed || ''}
                onChange={(e) => handleInputChange('seed', e.target.value ? parseInt(e.target.value) : null)}
                placeholder="Leave empty for random"
              />
              <button
                type="button"
                className="btn btn-primary"
                onClick={generateRandomSeed}
              >
                Generate
              </button>
            </div>
          </div>
        </div>

        {/* Blockchain Network Selection */}
        <div className="card" style={{ marginTop: '20px', backgroundColor: '#f8f9fa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3 style={{ margin: 0 }}>⛓️ Blockchain Network</h3>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setShowNetworkHelp(!showNetworkHelp)}
              style={{ fontSize: '12px', padding: '5px 10px' }}
            >
              {showNetworkHelp ? '❌ Hide Help' : '❓ Show Help'}
            </button>
          </div>

          {showNetworkHelp && (
            <div style={{
              backgroundColor: '#e7f3ff',
              border: '2px solid #2196F3',
              borderRadius: '8px',
              padding: '15px',
              marginBottom: '20px'
            }}>
              <h4 style={{ marginTop: 0, color: '#1976d2' }}>📚 How to Connect to L2 Blockchain</h4>

              <div style={{ marginBottom: '15px' }}>
                <strong>🏠 Option 1: Localhost (Easiest - No Setup)</strong>
                <ol style={{ marginBottom: '10px', paddingLeft: '20px' }}>
                  <li>Make sure Hardhat is running: <code>npx hardhat node</code></li>
                  <li>Select "Localhost (Hardhat)" from dropdown</li>
                  <li>Click "Start Simulation" - Done! ✅</li>
                </ol>
                <div style={{ backgroundColor: '#d4edda', padding: '8px', borderRadius: '4px', fontSize: '13px' }}>
                  ✅ <strong>Best for:</strong> Testing, development, quick iterations
                </div>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>🌐 Option 2: L2 Network (Requires Setup)</strong>
                <ol style={{ marginBottom: '10px', paddingLeft: '20px' }}>
                  <li><strong>Get Testnet ETH:</strong>
                    <ul style={{ fontSize: '13px', marginTop: '5px' }}>
                      <li>Optimism: <a href="https://app.optimism.io/faucet" target="_blank" rel="noopener noreferrer">app.optimism.io/faucet</a></li>
                      <li>Base: <a href="https://www.coinbase.com/faucets/base-ethereum-goerli-faucet" target="_blank" rel="noopener noreferrer">coinbase.com/faucets</a></li>
                      <li>Arbitrum: <a href="https://faucet.quicknode.com/arbitrum/sepolia" target="_blank" rel="noopener noreferrer">faucet.quicknode.com</a></li>
                    </ul>
                  </li>
                  <li><strong>Deploy Contracts:</strong>
                    <pre style={{
                      backgroundColor: '#2d2d2d',
                      color: '#f8f8f2',
                      padding: '10px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      overflow: 'auto'
                    }}>
{`# Add private key to .env file
echo "PRIVATE_KEY=your_key" > .env

# Deploy to Optimism Sepolia
npx hardhat run scripts/deploy.js --network optimism-sepolia

# Update blockchain_config.json with addresses`}
                    </pre>
                  </li>
                  <li><strong>Select Network:</strong> Choose from dropdown below</li>
                  <li><strong>Optional:</strong> Add custom RPC URL (Alchemy/Infura) for better performance</li>
                  <li><strong>Start Simulation:</strong> Click "Start Simulation" button</li>
                </ol>
                <div style={{ backgroundColor: '#fff3cd', padding: '8px', borderRadius: '4px', fontSize: '13px' }}>
                  ⚡ <strong>Fastest L2:</strong> Arbitrum Sepolia (~0.25s blocks)
                </div>
              </div>

              <div style={{ marginBottom: '10px' }}>
                <strong>🔗 Get Custom RPC (Optional but Recommended):</strong>
                <ul style={{ fontSize: '13px', marginTop: '5px' }}>
                  <li><strong>Alchemy:</strong> <a href="https://www.alchemy.com/" target="_blank" rel="noopener noreferrer">alchemy.com</a> - Free tier available</li>
                  <li><strong>Infura:</strong> <a href="https://infura.io/" target="_blank" rel="noopener noreferrer">infura.io</a> - Free tier available</li>
                  <li>Copy HTTPS endpoint and paste in "Custom RPC URL" field below</li>
                </ul>
              </div>

              <div style={{ backgroundColor: '#f8d7da', padding: '8px', borderRadius: '4px', fontSize: '13px' }}>
                ⚠️ <strong>Important:</strong> L2 simulations are slower (~2-5 min) vs localhost (~1-2 min) due to block confirmation times
              </div>
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Network</label>
              <select
                className="form-input"
                value={config.network}
                onChange={(e) => handleInputChange('network', e.target.value)}
              >
                <option value="localhost">🏠 Localhost (Hardhat) - Instant & Free</option>
                <option value="optimism-sepolia">🌐 Optimism Sepolia - L2 Testnet (~2s blocks)</option>
                <option value="base-sepolia">🌐 Base Sepolia - L2 Testnet (~2s blocks)</option>
                <option value="arbitrum-sepolia">⚡ Arbitrum Sepolia - L2 Testnet (~0.25s blocks)</option>
              </select>
              <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
                {config.network === 'localhost' && '✅ No setup required - Just make sure Hardhat is running'}
                {config.network === 'optimism-sepolia' && '🔧 Requires: Deployed contracts + Testnet ETH'}
                {config.network === 'base-sepolia' && '🔧 Requires: Deployed contracts + Testnet ETH'}
                {config.network === 'arbitrum-sepolia' && '⚡ Fastest L2 - Requires: Deployed contracts + Testnet ETH'}
              </small>
            </div>
          </div>

          {config.network !== 'localhost' && (
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Custom RPC URL (optional but recommended)
                  <span style={{ fontSize: '11px', color: '#666', marginLeft: '5px' }}>
                    - Get from Alchemy or Infura for better performance
                  </span>
                </label>
                <input
                  type="text"
                  className="form-input"
                  value={config.rpc_url}
                  onChange={(e) => handleInputChange('rpc_url', e.target.value)}
                  placeholder="e.g., https://opt-sepolia.g.alchemy.com/v2/YOUR_API_KEY"
                />
                <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
                  💡 Leave empty to use default public endpoint (may be slower)
                </small>
              </div>
            </div>
          )}

          {config.network !== 'localhost' && (
            <div className="alert" style={{
              backgroundColor: '#fff3cd',
              border: '2px solid #ffc107',
              borderRadius: '8px',
              padding: '12px',
              marginTop: '10px'
            }}>
              <strong>⚠️ L2 Network Checklist:</strong>
              <ul style={{ marginBottom: 0, paddingLeft: '20px', marginTop: '8px' }}>
                <li>✅ Smart contracts deployed on {config.network}</li>
                <li>✅ blockchain_config.json updated with contract addresses</li>
                <li>✅ Testnet ETH available in your wallet</li>
                <li>✅ (Optional) Custom RPC URL for better performance</li>
              </ul>
              <div style={{ marginTop: '10px', fontSize: '12px', color: '#856404' }}>
                📖 <strong>Need help?</strong> Click "Show Help" button above for step-by-step instructions
              </div>
            </div>
          )}

          {config.network === 'localhost' && (
            <div className="alert" style={{
              backgroundColor: '#d4edda',
              border: '2px solid #28a745',
              borderRadius: '8px',
              padding: '12px',
              marginTop: '10px'
            }}>
              <strong>✅ Localhost Mode - Ready to Go!</strong>
              <div style={{ marginTop: '8px', fontSize: '13px' }}>
                Make sure Hardhat is running: <code style={{ backgroundColor: '#fff', padding: '2px 6px', borderRadius: '3px' }}>npx hardhat node</code>
              </div>
            </div>
          )}
        </div>

        {/* Bundle Configuration */}
        <div className="card" style={{ marginTop: '20px', backgroundColor: '#f0f8ff' }}>
          <h3 style={{ marginBottom: '15px' }}>🎫 Bundle Configuration</h3>

          <div className="form-row">
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <input
                  type="checkbox"
                  checked={config.enable_bundles}
                  onChange={(e) => handleInputChange('enable_bundles', e.target.checked)}
                />
                <strong>Enable Bundle System</strong>
              </label>
              <small style={{ color: '#666', fontSize: '12px', display: 'block', marginLeft: '28px' }}>
                Allow commuters to combine multiple transport segments into discounted bundles
              </small>
            </div>
          </div>

          {config.enable_bundles && (
            <>
              <div className="alert" style={{
                backgroundColor: '#fff3cd',
                border: '2px solid #ffc107',
                borderRadius: '8px',
                padding: '12px',
                marginTop: '15px',
                marginBottom: '15px'
              }}>
                <strong>📊 Recommended Minimum Values for Bundle Creation:</strong>
                <div style={{ marginTop: '8px', fontSize: '13px' }}>
                  <div>• <strong>Steps:</strong> 50+ (more opportunities for segment alignment)</div>
                  <div>• <strong>Commuters:</strong> 10+ (sufficient demand for multi-modal trips)</div>
                  <div>• <strong>Providers:</strong> 5+ (diverse transport modes available)</div>
                </div>
                <div style={{ marginTop: '10px', fontSize: '12px', color: '#856404' }}>
                  💡 <strong>Tip:</strong> Higher values increase the probability of creating bundles. For guaranteed bundle creation, use 100+ steps with 20+ commuters and 10+ providers.
                </div>
              </div>

              <div className="form-row" style={{ marginTop: '15px' }}>
                <div className="form-group">
                  <label className="form-label">
                    Max Bundle Segments
                    <span style={{ fontSize: '11px', color: '#666', marginLeft: '5px' }}>
                      (Maximum number of transport modes in a bundle)
                    </span>
                  </label>
                  <input
                    type="number"
                    className="form-input"
                    value={config.max_bundle_segments}
                    onChange={(e) => handleInputChange('max_bundle_segments', parseInt(e.target.value))}
                    min="2"
                    max="10"
                  />
                  <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
                    💡 Recommended: 3-5 segments for realistic multi-modal journeys
                  </small>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Bundle Discount Rate
                    <span style={{ fontSize: '11px', color: '#666', marginLeft: '5px' }}>
                      (Discount per additional segment)
                    </span>
                  </label>
                  <input
                    type="number"
                    className="form-input"
                    value={config.bundle_discount_rate}
                    onChange={(e) => handleInputChange('bundle_discount_rate', parseFloat(e.target.value))}
                    min="0"
                    max="0.5"
                    step="0.01"
                  />
                  <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
                    💡 Example: 0.05 = 5% discount per segment
                  </small>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Max Bundle Discount
                    <span style={{ fontSize: '11px', color: '#666', marginLeft: '5px' }}>
                      (Maximum total discount cap)
                    </span>
                  </label>
                  <input
                    type="number"
                    className="form-input"
                    value={config.max_bundle_discount}
                    onChange={(e) => handleInputChange('max_bundle_discount', parseFloat(e.target.value))}
                    min="0"
                    max="0.9"
                    step="0.01"
                  />
                  <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
                    💡 Example: 0.15 = Maximum 15% total discount
                  </small>
                </div>
              </div>

              <div className="alert" style={{
                backgroundColor: '#e7f3ff',
                border: '2px solid #2196F3',
                borderRadius: '8px',
                padding: '12px',
                marginTop: '15px'
              }}>
                <strong>📊 Bundle Pricing Example:</strong>
                <div style={{ marginTop: '8px', fontSize: '13px', fontFamily: 'monospace' }}>
                  <div>Bus ($2) + Train ($5) + Scooter ($3) = $10 original</div>
                  <div style={{ color: '#28a745', marginTop: '4px' }}>
                    With 5% discount rate: $10 - (2 segments × 5%) = $9.00 (10% off)
                  </div>
                  <div style={{ color: '#666', marginTop: '4px', fontSize: '11px' }}>
                    Capped at max discount: {(config.max_bundle_discount * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={config.debug}
                onChange={(e) => handleInputChange('debug', e.target.checked)}
              />
              Debug Mode (detailed logging)
            </label>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={config.no_plots}
                onChange={(e) => handleInputChange('no_plots', e.target.checked)}
              />
              Skip Plot Generation (faster execution)
            </label>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={config.export_db}
                onChange={(e) => handleInputChange('export_db', e.target.checked)}
              />
              Export to Database (for analysis & tracking)
            </label>
          </div>
        </div>

        {/* Control Buttons */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          {!currentSimulation ? (
            <button
              className="btn btn-success"
              onClick={handleStartSimulation}
              disabled={isStarting}
              style={{ minWidth: '120px' }}
            >
              {isStarting ? (
                <>
                  <span className="loading-spinner" style={{ marginRight: '8px' }}></span>
                  Starting...
                </>
              ) : (
                'Start Simulation'
              )}
            </button>
          ) : (
            <button
              className="btn btn-danger"
              onClick={handleStopSimulation}
            >
              Stop Simulation
            </button>
          )}
        </div>
      </div>

      {/* Current Configuration Summary */}
      <div className="card">
        <h3>Current Configuration</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div><strong>Steps:</strong> {config.steps}</div>
          <div><strong>Commuters:</strong> {config.commuters}</div>
          <div><strong>Providers:</strong> {config.providers}</div>
          <div><strong>Debug Mode:</strong> {config.debug ? 'Yes' : 'No'}</div>
          <div><strong>Generate Plots:</strong> {config.no_plots ? 'No' : 'Yes'}</div>
          <div><strong>Export to Database:</strong> {config.export_db ? 'Yes' : 'No'}</div>
          <div><strong>Random Seed:</strong> {config.seed || 'Random'}</div>
        </div>
      </div>

      {/* Progress Display */}
      <div className="card">
        <h3>📊 Simulation Progress</h3>
        <ProgressDisplay
          isRunning={!!currentSimulation}
          simulationData={config}
        />
      </div>

      {/* Information */}
      <div className="alert alert-info">
        <strong>Note:</strong> The simulation will run in the background. You can monitor progress on the Dashboard page.
        Results and visualizations will be available in the Analytics section once completed.
      </div>
    </div>
  );
};

export default SimulationControl;
