import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';
import './EnhancedBundleVisualization.css';

const EnhancedBundleVisualization = () => {
  const [activeView, setActiveView] = useState('bundles'); // 'bundles' or 'scenario'
  const [bundles, setBundles] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedBundle, setSelectedBundle] = useState(null);
  const [filterMode, setFilterMode] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [showHelp, setShowHelp] = useState(false);
  
  // Scenario configuration
  const [scenarioConfig, setScenarioConfig] = useState({
    name: 'Custom Bundle Scenario',
    steps: 30,
    commuters: 5,
    providers: 3,
    export_db: true,
    no_plots: false,
    seed: null,
    // Bundle-specific configuration
    enable_bundles: true,
    max_bundle_segments: 4,
    bundle_discount_rate: 0.05,
    max_bundle_discount: 0.15
  });
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [simulationProgress, setSimulationProgress] = useState(0);

  useEffect(() => {
    if (activeView === 'bundles') {
      loadBundleData();
    }
  }, [activeView, filterMode, sortBy]);

  useEffect(() => {
    let interval;
    if (simulationRunning) {
      interval = setInterval(checkSimulationProgress, 1000);
    }
    return () => clearInterval(interval);
  }, [simulationRunning]);

  const loadBundleData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [bundleData, statsData] = await Promise.all([
        ApiService.getBundlesList(100, 0),
        ApiService.getBundleStats()
      ]);
      
      let filteredBundles = bundleData.bundles || [];
      
      // Apply mode filter
      if (filterMode !== 'all') {
        filteredBundles = filteredBundles.filter(bundle => 
          bundle.segments?.some(seg => seg.mode === filterMode)
        );
      }
      
      // Apply sorting
      filteredBundles.sort((a, b) => {
        if (sortBy === 'price') return a.total_price - b.total_price;
        if (sortBy === 'segments') return b.num_segments - a.num_segments;
        if (sortBy === 'discount') return b.discount_amount - a.discount_amount;
        return new Date(b.created_at) - new Date(a.created_at);
      });
      
      setBundles(filteredBundles);
      setStats(statsData || {});
    } catch (err) {
      console.error('Error loading bundle data:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load bundle data');
    } finally {
      setLoading(false);
    }
  };

  const checkSimulationProgress = async () => {
    try {
      const progress = await ApiService.getSimulationProgress();
      setSimulationProgress(progress.progress_percentage || 0);
      
      if (progress.status === 'completed') {
        setSimulationRunning(false);
        setSimulationProgress(100);
        // Reload bundles after simulation completes
        setTimeout(() => {
          loadBundleData();
          setActiveView('bundles');
        }, 2000);
      }
    } catch (error) {
      console.error('Error checking progress:', error);
    }
  };

  const handleRunScenario = async () => {
    try {
      setSimulationRunning(true);
      setSimulationProgress(0);
      
      const response = await ApiService.startSimulation(scenarioConfig);
      console.log('Simulation started:', response);
    } catch (error) {
      console.error('Error starting simulation:', error);
      alert('Failed to start simulation: ' + error.message);
      setSimulationRunning(false);
    }
  };

  const handleStopSimulation = async () => {
    try {
      await ApiService.stopSimulation();
      setSimulationRunning(false);
      setSimulationProgress(0);
    } catch (error) {
      console.error('Error stopping simulation:', error);
    }
  };

  const getModeIcon = (mode) => {
    const icons = {
      'bike': '🚲',
      'train': '🚇',
      'bus': '🚌',
      'car': '🚗',
      'scooter': '🛴',
      'walk': '🚶',
      'metro': '🚇',
      'tram': '🚊'
    };
    return icons[mode?.toLowerCase()] || '🚗';
  };

  const formatPrice = (price) => {
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const renderHelpModal = () => {
    if (!showHelp) return null;

    return (
      <div className="help-modal-overlay" onClick={() => setShowHelp(false)}>
        <div className="help-modal" onClick={(e) => e.stopPropagation()}>
          <div className="help-header">
            <h2>📚 Bundle Configuration Guide</h2>
            <button className="close-btn" onClick={() => setShowHelp(false)}>✕</button>
          </div>

          <div className="help-content">
            <section className="help-section">
              <h3>🎯 What are MaaS Bundles?</h3>
              <p>
                MaaS (Mobility-as-a-Service) bundles combine multiple transport modes into a single journey.
                For example: <strong>Bike → Train → Bus</strong> to reach your destination.
              </p>
              <div className="help-example">
                <strong>Example:</strong> 🚲 Multi-modal journey: Bike → 🚆 Train → 🚌 Bus ($45.50 with $5.25 discount) • 35 min
              </div>
            </section>

            <section className="help-section">
              <h3>⚙️ Configuration Parameters</h3>

              <div className="param-item">
                <strong>📊 Simulation Steps (10-200)</strong>
                <p>Number of time steps in the simulation. More steps = longer simulation, more data.</p>
                <ul>
                  <li><strong>Quick Test:</strong> 20 steps - Fast, minimal data</li>
                  <li><strong>Standard:</strong> 50 steps - Balanced testing</li>
                  <li><strong>Large Scale:</strong> 100 steps - Comprehensive data</li>
                </ul>
              </div>

              <div className="param-item">
                <strong>👥 Number of Commuters (1-50)</strong>
                <p>Travelers requesting journeys. More commuters = more bundle opportunities.</p>
                <ul>
                  <li><strong>Small:</strong> 3-5 commuters - Simple scenarios</li>
                  <li><strong>Medium:</strong> 10-15 commuters - Realistic testing</li>
                  <li><strong>Large:</strong> 20+ commuters - High traffic simulation</li>
                </ul>
              </div>

              <div className="param-item">
                <strong>🚗 Number of Providers (1-20)</strong>
                <p>Transport service providers (bike, train, bus, car). More providers = more route options.</p>
                <ul>
                  <li><strong>Minimum:</strong> 2-3 providers - Limited options</li>
                  <li><strong>Recommended:</strong> 5-7 providers - Good variety</li>
                  <li><strong>Maximum:</strong> 10+ providers - Maximum flexibility</li>
                </ul>
              </div>

              <div className="param-item">
                <strong>💾 Export to Database</strong>
                <p>Save simulation results to database for viewing and analysis.</p>
                <ul>
                  <li>✅ <strong>Enable</strong> to see bundles in the UI</li>
                  <li>✅ Required for Excel/CSV export</li>
                  <li>✅ Allows historical data comparison</li>
                </ul>
              </div>

              <div className="param-item">
                <strong>📈 Skip Plot Generation</strong>
                <p>Disable chart generation for faster execution.</p>
                <ul>
                  <li>✅ Enable for faster simulations</li>
                  <li>❌ Disable to generate visualization charts</li>
                </ul>
              </div>

              <div className="param-item">
                <strong>🎲 Random Seed</strong>
                <p>Set a seed for reproducible results.</p>
                <ul>
                  <li><strong>Empty:</strong> Random results each time</li>
                  <li><strong>Set value:</strong> Same results with same seed</li>
                </ul>
              </div>
            </section>

            <section className="help-section">
              <h3>🚀 Quick Start Guide</h3>
              <ol className="help-steps">
                <li>
                  <strong>Choose a Preset</strong>
                  <p>Click "Quick Test", "Standard", or "Large Scale" for pre-configured settings</p>
                </li>
                <li>
                  <strong>Customize (Optional)</strong>
                  <p>Adjust parameters to match your testing needs</p>
                </li>
                <li>
                  <strong>Enable Database Export</strong>
                  <p>Make sure "Export to Database" is checked to see results</p>
                </li>
                <li>
                  <strong>Run Simulation</strong>
                  <p>Click "🚀 Run Scenario" and wait for completion</p>
                </li>
                <li>
                  <strong>View Results</strong>
                  <p>Switch to "📊 View Bundles" tab to see generated bundles</p>
                </li>
              </ol>
            </section>

            <section className="help-section">
              <h3>💡 Tips for Best Results</h3>
              <div className="tips-grid">
                <div className="tip-card">
                  <span className="tip-icon">🎯</span>
                  <strong>Multi-Modal Bundles</strong>
                  <p>Use 5+ providers and 10+ commuters for better multi-modal bundle generation</p>
                </div>
                <div className="tip-card">
                  <span className="tip-icon">⚡</span>
                  <strong>Fast Testing</strong>
                  <p>Use "Quick Test" preset with "Skip Plot Generation" enabled</p>
                </div>
                <div className="tip-card">
                  <span className="tip-icon">📊</span>
                  <strong>Data Analysis</strong>
                  <p>Run "Standard" or "Large Scale" with database export enabled</p>
                </div>
                <div className="tip-card">
                  <span className="tip-icon">🔄</span>
                  <strong>Reproducibility</strong>
                  <p>Set a random seed to get consistent results for testing</p>
                </div>
              </div>
            </section>

            <section className="help-section">
              <h3>📋 Understanding Bundle Discounts</h3>
              <p>Multi-modal bundles receive automatic discounts:</p>
              <ul>
                <li><strong>2 segments:</strong> 5% discount</li>
                <li><strong>3 segments:</strong> 10% discount</li>
                <li><strong>4+ segments:</strong> 15% discount (maximum)</li>
              </ul>
              <div className="help-example">
                <strong>Example:</strong> A 3-segment bundle costing $50 gets a $5 discount (10%), final price: $45
              </div>
            </section>

            <section className="help-section">
              <h3>🔍 Viewing and Filtering Bundles</h3>
              <p>After running a simulation:</p>
              <ul>
                <li><strong>Filter by Mode:</strong> Show only bundles using specific transport (bike, train, bus, car)</li>
                <li><strong>Sort Options:</strong> By price, segments, discount, or creation date</li>
                <li><strong>Click Bundle:</strong> View detailed information in modal</li>
                <li><strong>Export Data:</strong> Go to Database page to export to Excel/CSV</li>
              </ul>
            </section>

            <section className="help-section">
              <h3>❓ Troubleshooting</h3>
              <div className="troubleshooting">
                <div className="trouble-item">
                  <strong>No bundles generated?</strong>
                  <p>• Increase number of commuters and providers<br/>
                     • Run more simulation steps<br/>
                     • Ensure "Export to Database" is enabled</p>
                </div>
                <div className="trouble-item">
                  <strong>Simulation taking too long?</strong>
                  <p>• Reduce number of steps<br/>
                     • Enable "Skip Plot Generation"<br/>
                     • Use fewer commuters/providers</p>
                </div>
                <div className="trouble-item">
                  <strong>Only single-mode trips?</strong>
                  <p>• Increase provider diversity<br/>
                     • Run longer simulations (50+ steps)<br/>
                     • Add more commuters for variety</p>
                </div>
              </div>
            </section>
          </div>

          <div className="help-footer">
            <button className="btn btn-primary" onClick={() => setShowHelp(false)}>
              Got it! 👍
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderScenarioBuilder = () => (
    <div className="scenario-builder">
      <div className="scenario-header">
        <div>
          <h3>🎯 Bundle Scenario Configuration</h3>
          <p className="scenario-description">
            Configure and run a custom simulation to generate bundle data
          </p>
        </div>
        <button className="help-button" onClick={() => setShowHelp(true)}>
          ❓ Help
        </button>
      </div>

      <div className="scenario-form">
        <div className="form-group">
          <label>Scenario Name</label>
          <input
            type="text"
            value={scenarioConfig.name}
            onChange={(e) => setScenarioConfig({...scenarioConfig, name: e.target.value})}
            className="form-control"
            placeholder="e.g., High Traffic Bundle Test"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Simulation Steps</label>
            <input
              type="number"
              value={scenarioConfig.steps}
              onChange={(e) => setScenarioConfig({...scenarioConfig, steps: parseInt(e.target.value)})}
              className="form-control"
              min="10"
              max="200"
            />
            <small>Number of time steps (10-200)</small>
          </div>

          <div className="form-group">
            <label>Number of Commuters</label>
            <input
              type="number"
              value={scenarioConfig.commuters}
              onChange={(e) => setScenarioConfig({...scenarioConfig, commuters: parseInt(e.target.value)})}
              className="form-control"
              min="1"
              max="50"
            />
            <small>Active commuters (1-50)</small>
          </div>

          <div className="form-group">
            <label>Number of Providers</label>
            <input
              type="number"
              value={scenarioConfig.providers}
              onChange={(e) => setScenarioConfig({...scenarioConfig, providers: parseInt(e.target.value)})}
              className="form-control"
              min="1"
              max="20"
            />
            <small>Service providers (1-20)</small>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={scenarioConfig.export_db}
                onChange={(e) => setScenarioConfig({...scenarioConfig, export_db: e.target.checked})}
              />
              <span>Export to Database</span>
            </label>
            <small>Save results to database for analysis</small>
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={scenarioConfig.no_plots}
                onChange={(e) => setScenarioConfig({...scenarioConfig, no_plots: e.target.checked})}
              />
              <span>Skip Plot Generation</span>
            </label>
            <small>Faster execution without charts</small>
          </div>
        </div>

        <div className="form-group">
          <label>Random Seed (Optional)</label>
          <input
            type="number"
            value={scenarioConfig.seed || ''}
            onChange={(e) => setScenarioConfig({...scenarioConfig, seed: e.target.value ? parseInt(e.target.value) : null})}
            className="form-control"
            placeholder="Leave empty for random"
          />
          <small>Set seed for reproducible results</small>
        </div>

        {/* Bundle Configuration Section */}
        <div className="bundle-config-section">
          <h4>🎫 Bundle Configuration</h4>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={scenarioConfig.enable_bundles}
                onChange={(e) => setScenarioConfig({...scenarioConfig, enable_bundles: e.target.checked})}
              />
              <span>Enable Multi-Modal Bundles</span>
            </label>
            <small>Allow combining multiple transport modes into bundles</small>
          </div>

          {scenarioConfig.enable_bundles && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label>Max Bundle Segments</label>
                  <input
                    type="number"
                    value={scenarioConfig.max_bundle_segments}
                    onChange={(e) => setScenarioConfig({...scenarioConfig, max_bundle_segments: parseInt(e.target.value)})}
                    className="form-control"
                    min="2"
                    max="6"
                  />
                  <small>Maximum transport modes per bundle (2-6)</small>
                </div>

                <div className="form-group">
                  <label>Discount per Segment (%)</label>
                  <input
                    type="number"
                    value={scenarioConfig.bundle_discount_rate * 100}
                    onChange={(e) => setScenarioConfig({...scenarioConfig, bundle_discount_rate: parseFloat(e.target.value) / 100})}
                    className="form-control"
                    min="0"
                    max="20"
                    step="1"
                  />
                  <small>Discount rate per additional segment (0-20%)</small>
                </div>
              </div>

              <div className="form-group">
                <label>Maximum Total Discount (%)</label>
                <input
                  type="number"
                  value={scenarioConfig.max_bundle_discount * 100}
                  onChange={(e) => setScenarioConfig({...scenarioConfig, max_bundle_discount: parseFloat(e.target.value) / 100})}
                  className="form-control"
                  min="0"
                  max="50"
                  step="5"
                />
                <small>Maximum discount cap for bundles (0-50%)</small>
              </div>

              <div className="bundle-discount-preview">
                <strong>💰 Discount Preview:</strong>
                <div className="discount-examples">
                  <div className="discount-item">
                    <span>2 segments:</span>
                    <span>{(scenarioConfig.bundle_discount_rate * 100).toFixed(0)}% discount</span>
                  </div>
                  <div className="discount-item">
                    <span>3 segments:</span>
                    <span>{Math.min(scenarioConfig.bundle_discount_rate * 2 * 100, scenarioConfig.max_bundle_discount * 100).toFixed(0)}% discount</span>
                  </div>
                  <div className="discount-item">
                    <span>4+ segments:</span>
                    <span>{Math.min(scenarioConfig.bundle_discount_rate * 3 * 100, scenarioConfig.max_bundle_discount * 100).toFixed(0)}% discount (max)</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {simulationRunning ? (
          <div className="simulation-progress">
            <div className="progress-header">
              <span>🔄 Simulation Running...</span>
              <span>{simulationProgress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{width: `${simulationProgress}%`}}
              ></div>
            </div>
            <button 
              className="btn btn-danger"
              onClick={handleStopSimulation}
            >
              ⏹️ Stop Simulation
            </button>
          </div>
        ) : (
          <div className="form-actions">
            <button 
              className="btn btn-primary btn-large"
              onClick={handleRunScenario}
              disabled={loading}
            >
              🚀 Run Scenario
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setScenarioConfig({
                name: 'Custom Bundle Scenario',
                steps: 30,
                commuters: 5,
                providers: 3,
                export_db: true,
                no_plots: false,
                seed: null,
                enable_bundles: true,
                max_bundle_segments: 4,
                bundle_discount_rate: 0.05,
                max_bundle_discount: 0.15
              })}
            >
              🔄 Reset to Defaults
            </button>
          </div>
        )}
      </div>

      <div className="scenario-presets">
        <h4>📋 Quick Presets</h4>
        <div className="preset-buttons">
          <button
            className="preset-btn"
            onClick={() => setScenarioConfig({
              ...scenarioConfig,
              name: 'Quick Test',
              steps: 20,
              commuters: 3,
              providers: 2,
              export_db: true,
              no_plots: true,
              enable_bundles: true
            })}
          >
            ⚡ Quick Test
          </button>
          <button
            className="preset-btn"
            onClick={() => setScenarioConfig({
              ...scenarioConfig,
              name: 'Standard Simulation',
              steps: 50,
              commuters: 10,
              providers: 5,
              export_db: true,
              no_plots: false,
              enable_bundles: true
            })}
          >
            📊 Standard
          </button>
          <button
            className="preset-btn"
            onClick={() => setScenarioConfig({
              ...scenarioConfig,
              name: 'Large Scale Test',
              steps: 100,
              commuters: 20,
              providers: 10,
              export_db: true,
              no_plots: true,
              enable_bundles: true
            })}
          >
            🏢 Large Scale
          </button>
        </div>
      </div>
    </div>
  );

  const renderBundleCard = (bundle) => (
    <div key={bundle.bundle_id} className="bundle-card" onClick={() => setSelectedBundle(bundle)}>
      <div className="bundle-header">
        <span className="bundle-id">#{bundle.bundle_id.substring(0, 8)}</span>
        <span className="bundle-segments-badge">{bundle.num_segments} segments</span>
      </div>

      {bundle.description && (
        <div className="bundle-description">
          <p>{bundle.description}</p>
        </div>
      )}

      <div className="bundle-route">
        <div className="route-point">
          <span className="route-icon">📍</span>
          <span className="route-label">{bundle.origin}</span>
        </div>
        <div className="route-arrow">→</div>
        <div className="route-point">
          <span className="route-icon">🎯</span>
          <span className="route-label">{bundle.destination}</span>
        </div>
      </div>

      <div className="bundle-segments">
        {bundle.segments?.map((seg, idx) => (
          <div key={idx} className="segment-item">
            <span className="segment-icon">{getModeIcon(seg.mode)}</span>
            <span className="segment-mode">{seg.mode}</span>
            <span className="segment-price">{formatPrice(seg.price)}</span>
          </div>
        ))}
      </div>

      <div className="bundle-pricing">
        <div className="price-row">
          <span>Base Price:</span>
          <span>{formatPrice(bundle.base_price)}</span>
        </div>
        {bundle.discount_amount > 0 && (
          <div className="price-row discount">
            <span>Discount:</span>
            <span>-{formatPrice(bundle.discount_amount)}</span>
          </div>
        )}
        <div className="price-row total">
          <span>Total:</span>
          <span>{formatPrice(bundle.total_price)}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="enhanced-bundle-viz">
      {renderHelpModal()}

      <div className="page-header">
        <h1>🎫 MaaS Bundle System</h1>
        <div className="view-toggle">
          <button
            className={`toggle-btn ${activeView === 'bundles' ? 'active' : ''}`}
            onClick={() => setActiveView('bundles')}
          >
            📊 View Bundles
          </button>
          <button
            className={`toggle-btn ${activeView === 'scenario' ? 'active' : ''}`}
            onClick={() => setActiveView('scenario')}
          >
            🎯 Run Scenario
          </button>
        </div>
      </div>

      {activeView === 'scenario' ? (
        renderScenarioBuilder()
      ) : (
        <>
          {/* Stats Dashboard */}
          <div className="stats-dashboard">
            <div className="stat-box">
              <div className="stat-value">{stats.total_bundles || 0}</div>
              <div className="stat-label">Total Bundles</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{(stats.avg_segments || 0).toFixed(1)}</div>
              <div className="stat-label">Avg Segments</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">${(stats.total_savings || 0).toFixed(2)}</div>
              <div className="stat-label">Total Savings</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{(stats.bundle_match_rate || 0).toFixed(1)}%</div>
              <div className="stat-label">Match Rate</div>
            </div>
          </div>

          {/* Filters and Controls */}
          <div className="controls-bar">
            <div className="filter-group">
              <label>Filter by Mode:</label>
              <select value={filterMode} onChange={(e) => setFilterMode(e.target.value)}>
                <option value="all">All Modes</option>
                <option value="bike">🚲 Bike</option>
                <option value="train">🚇 Train</option>
                <option value="bus">🚌 Bus</option>
                <option value="car">🚗 Car</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Sort by:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="created_at">Latest First</option>
                <option value="price">Price (Low to High)</option>
                <option value="segments">Most Segments</option>
                <option value="discount">Highest Discount</option>
              </select>
            </div>

            <button className="btn btn-refresh" onClick={loadBundleData} disabled={loading}>
              🔄 Refresh
            </button>
          </div>

          {/* Bundle Grid */}
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading bundles...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>❌ {error}</p>
              <button className="btn btn-primary" onClick={loadBundleData}>Retry</button>
            </div>
          ) : bundles.length === 0 ? (
            <div className="empty-state">
              <h3>No bundles found</h3>
              <p>Run a scenario to generate bundle data</p>
              <button className="btn btn-primary" onClick={() => setActiveView('scenario')}>
                🎯 Create Scenario
              </button>
            </div>
          ) : (
            <div className="bundle-grid">
              {bundles.map(renderBundleCard)}
            </div>
          )}
        </>
      )}

      {/* Bundle Detail Modal */}
      {selectedBundle && (
        <div className="modal-overlay" onClick={() => setSelectedBundle(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedBundle(null)}>×</button>
            <h2>Bundle Details</h2>
            <div className="modal-body">
              <p><strong>Bundle ID:</strong> {selectedBundle.bundle_id}</p>
              <p><strong>Route:</strong> {selectedBundle.origin} → {selectedBundle.destination}</p>
              <p><strong>Segments:</strong> {selectedBundle.num_segments}</p>
              <p><strong>Total Price:</strong> {formatPrice(selectedBundle.total_price)}</p>
              <p><strong>Discount:</strong> {formatPrice(selectedBundle.discount_amount)}</p>
              
              <h3>Segment Details:</h3>
              {selectedBundle.segments?.map((seg, idx) => (
                <div key={idx} className="segment-detail">
                  <p>{getModeIcon(seg.mode)} <strong>{seg.mode}</strong></p>
                  <p>From: {seg.origin} → To: {seg.destination}</p>
                  <p>Price: {formatPrice(seg.price)}</p>
                  {seg.duration && <p>Duration: {seg.duration} min</p>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedBundleVisualization;

