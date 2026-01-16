import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';
import './BundleVisualization.css';

const BundleVisualization = () => {
  const [bundles, setBundles] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBundle, setSelectedBundle] = useState(null);

  useEffect(() => {
    loadBundleData();
  }, []);

  const loadBundleData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [bundleData, statsData] = await Promise.all([
        ApiService.getBundlesList(50, 0),
        ApiService.getBundleStats()
      ]);
      
      setBundles(bundleData.bundles || []);
      setStats(statsData || {});
    } catch (err) {
      console.error('Error loading bundle data:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load bundle data');
    } finally {
      setLoading(false);
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

  const formatCoordinate = (coord) => {
    if (Array.isArray(coord)) {
      return `[${coord[0]}, ${coord[1]}]`;
    }
    return coord;
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="loading-spinner"></div>
          <span style={{ marginLeft: '10px' }}>Loading bundle data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <h2>🎫 MaaS Bundles</h2>
        <div className="alert alert-danger">
          <strong>Error:</strong> {error}
          <br />
          <br />
          <strong>Possible solutions:</strong>
          <ul>
            <li>Make sure PostgreSQL is running and configured</li>
            <li>Run: <code>python setup_database.py</code></li>
            <li>Run a simulation with: <code>--export-db</code> flag</li>
            <li>Install dependencies: <code>pip install sqlalchemy psycopg2-binary</code></li>
          </ul>
        </div>
        <button className="btn btn-primary" onClick={loadBundleData}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>🎫 MaaS Bundles</h2>

      {/* Bundle Statistics */}
      <div className="card">
        <h3>Bundle Statistics</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div className="stat-card">
            <div className="stat-value">{stats.total_bundles || 0}</div>
            <div className="stat-label">Total Bundles</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.avg_segments?.toFixed(2) || '0.00'}</div>
            <div className="stat-label">Avg Segments/Bundle</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{formatPrice(stats.total_savings || 0)}</div>
            <div className="stat-label">Total Savings</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.bundle_match_rate?.toFixed(1) || '0.0'}%</div>
            <div className="stat-label">Bundle Match Rate</div>
          </div>
        </div>
      </div>

      {/* Bundle List */}
      {bundles.length === 0 ? (
        <div className="card">
          <div className="alert alert-info">
            <strong>No bundles found.</strong>
            <br />
            Run a simulation with the <code>--export-db</code> flag to generate bundle data.
            <br />
            <br />
            Example: <code>python abm/agents/run_decentralized_model.py --steps 30 --export-db</code>
          </div>
        </div>
      ) : (
        <div className="card">
          <h3>Bundle List ({bundles.length} bundles)</h3>
          <div className="bundle-grid">
            {bundles.map((bundle) => (
              <div key={bundle.bundle_id} className="bundle-card">
                {/* Bundle Header */}
                <div className="bundle-header">
                  <h4>Bundle #{bundle.bundle_id.substring(0, 8)}...</h4>
                  <span className="bundle-badge">{bundle.num_segments} segments</span>
                </div>

                {/* Route */}
                <div className="bundle-route">
                  <span className="route-point">{formatCoordinate(bundle.origin)}</span>
                  <span className="route-arrow">→</span>
                  <span className="route-point">{formatCoordinate(bundle.destination)}</span>
                </div>

                {/* Segments */}
                <div className="bundle-segments">
                  {bundle.segments && bundle.segments.map((segment, idx) => (
                    <div key={idx} className="segment-item">
                      <span className="segment-icon">{getModeIcon(segment.mode)}</span>
                      <span className="segment-mode">{segment.mode || 'Unknown'}</span>
                      <span className="segment-route">
                        {formatCoordinate(segment.origin)} → {formatCoordinate(segment.destination)}
                      </span>
                      <span className="segment-price">{formatPrice(segment.price)}</span>
                    </div>
                  ))}
                </div>

                {/* Pricing */}
                <div className="bundle-pricing">
                  <div className="pricing-row">
                    <span>Base Price:</span>
                    <span>{formatPrice(bundle.base_price)}</span>
                  </div>
                  <div className="pricing-row discount">
                    <span>Discount ({bundle.discount_percentage}%):</span>
                    <span>-{formatPrice(bundle.discount_amount)}</span>
                  </div>
                  <div className="pricing-row total">
                    <span><strong>Total Price:</strong></span>
                    <span><strong>{formatPrice(bundle.total_price)}</strong></span>
                  </div>
                </div>

                {/* Metadata */}
                {bundle.created_at && (
                  <div className="bundle-metadata">
                    <small>Created: {new Date(bundle.created_at).toLocaleString()}</small>
                  </div>
                )}

                {/* View Details Button */}
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => setSelectedBundle(bundle)}
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bundle Details Modal */}
      {selectedBundle && (
        <div className="modal-overlay" onClick={() => setSelectedBundle(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Bundle Details</h3>
              <button className="modal-close" onClick={() => setSelectedBundle(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-section">
                <h4>Bundle Information</h4>
                <div className="detail-grid">
                  <div><strong>Bundle ID:</strong></div>
                  <div>{selectedBundle.bundle_id}</div>
                  
                  <div><strong>Origin:</strong></div>
                  <div>{formatCoordinate(selectedBundle.origin)}</div>
                  
                  <div><strong>Destination:</strong></div>
                  <div>{formatCoordinate(selectedBundle.destination)}</div>
                  
                  <div><strong>Number of Segments:</strong></div>
                  <div>{selectedBundle.num_segments}</div>
                  
                  <div><strong>Total Duration:</strong></div>
                  <div>{selectedBundle.total_duration} ticks</div>
                  
                  {selectedBundle.utility_score && (
                    <>
                      <div><strong>Utility Score:</strong></div>
                      <div>{selectedBundle.utility_score.toFixed(2)}</div>
                    </>
                  )}
                </div>
              </div>

              <div className="detail-section">
                <h4>Pricing Breakdown</h4>
                <div className="pricing-breakdown">
                  <div className="pricing-row">
                    <span>Base Price:</span>
                    <span>{formatPrice(selectedBundle.base_price)}</span>
                  </div>
                  <div className="pricing-row">
                    <span>Discount Percentage:</span>
                    <span>{selectedBundle.discount_percentage}%</span>
                  </div>
                  <div className="pricing-row discount">
                    <span>Discount Amount:</span>
                    <span>-{formatPrice(selectedBundle.discount_amount)}</span>
                  </div>
                  <div className="pricing-row total">
                    <span><strong>Final Price:</strong></span>
                    <span><strong>{formatPrice(selectedBundle.total_price)}</strong></span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Segments</h4>
                {selectedBundle.segments && selectedBundle.segments.map((segment, idx) => (
                  <div key={idx} className="segment-detail-card">
                    <div className="segment-detail-header">
                      <span className="segment-icon-large">{getModeIcon(segment.mode)}</span>
                      <h5>Segment {idx + 1}: {segment.mode}</h5>
                    </div>
                    <div className="detail-grid">
                      <div><strong>Origin:</strong></div>
                      <div>{formatCoordinate(segment.origin)}</div>
                      
                      <div><strong>Destination:</strong></div>
                      <div>{formatCoordinate(segment.destination)}</div>
                      
                      <div><strong>Price:</strong></div>
                      <div>{formatPrice(segment.price)}</div>
                      
                      <div><strong>Duration:</strong></div>
                      <div>{segment.duration} ticks</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BundleVisualization;

