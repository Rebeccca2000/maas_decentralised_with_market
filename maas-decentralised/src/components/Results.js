import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/ApiService';

const Section = ({ title, children }) => (
  <div className="card" style={{ marginBottom: '16px' }}>
    <h3>{title}</h3>
    {children}
  </div>
);

const KeyValue = ({ label, value }) => (
  <div>
    <strong>{label}:</strong> {value}
  </div>
);

const Results = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [bundleStats, setBundleStats] = useState(null);
  const [plots, setPlots] = useState([]);
  const [plotsDir, setPlotsDir] = useState(null);
  const [rawLog, setRawLog] = useState('');
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, files, log, bundles] = await Promise.all([
        ApiService.getSimulationMetrics(),
        ApiService.getSimulationResults(),
        ApiService.getResultsLog().catch(() => ({ log: '' })),
        ApiService.getBundleStats().catch(() => null)
      ]);
      setMetrics(m);
      setPlots(files?.plots || []);
      setPlotsDir(files?.dir || null);
      setRawLog(log?.log || '');
      setBundleStats(bundles);
    } catch (e) {
      setError(e.response?.data?.message || e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const renderKPIs = () => {
    const k = metrics || {};
    // Support either flat KPIs or nested advanced metrics
    const adv = k.advanced || k;
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
        <KeyValue label="Match Rate" value={adv.match_rate != null ? `${Number(adv.match_rate).toFixed(1)}%` : '—'} />
        <KeyValue label="Avg Generalized Cost" value={adv.avg_generalized_cost != null ? `$${adv.avg_generalized_cost.toFixed(2)}` : '—'} />
        <KeyValue label="Avg Bids / Request" value={adv.avg_bids_per_request != null ? adv.avg_bids_per_request.toFixed(2) : '—'} />
        <KeyValue label="HHI" value={adv.hhi != null ? adv.hhi : '—'} />
        <KeyValue label="Total Requests" value={adv.total_requests != null ? adv.total_requests : '—'} />
        <KeyValue label="Total Matches" value={adv.total_matches != null ? adv.total_matches : '—'} />
      </div>
    );
  };

  const renderBundleKPIs = () => {
    if (!bundleStats) {
      return (
        <div className="alert alert-info" style={{ fontSize: '14px' }}>
          <strong>Bundle data not available.</strong>
          <br />
          Run a simulation with the <code>--export-db</code> flag to enable bundle tracking.
          <br />
          Example: <code>python abm/agents/run_decentralized_model.py --steps 30 --export-db</code>
        </div>
      );
    }

    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
        <KeyValue label="Total Bundles" value={bundleStats.total_bundles || 0} />
        <KeyValue label="Avg Segments/Bundle" value={bundleStats.avg_segments ? bundleStats.avg_segments.toFixed(2) : '—'} />
        <KeyValue label="Total Savings" value={bundleStats.total_savings ? `$${bundleStats.total_savings.toFixed(2)}` : '—'} />
        <KeyValue label="Bundle Match Rate" value={bundleStats.bundle_match_rate ? `${bundleStats.bundle_match_rate.toFixed(1)}%` : '—'} />
      </div>
    );
  };

  return (
    <div className="container">
      <h2>Results</h2>

      {error && (
        <div className="alert alert-danger"><strong>Error:</strong> {error}</div>
      )}

      {loading ? (
        <div className="alert alert-info">Loading results…</div>
      ) : (
        <>
          <Section title="Overview KPIs">
            {metrics ? renderKPIs() : <div>No metrics available yet. Run a simulation first.</div>}
          </Section>

          <Section title="🎫 Bundle Metrics">
            {renderBundleKPIs()}
          </Section>

          <Section title="Visualization Plots">
            {plotsDir ? (
              <div style={{ marginBottom: 8 }}>
                <em>Directory:</em> {plotsDir}
              </div>
            ) : null}
            {plots && plots.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                {plots.map((f) => (
                  <div key={f} className="card" style={{ padding: 12 }}>
                    <div style={{ marginBottom: 8, fontWeight: 600 }}>{f}</div>
                    <img
                      src={ApiService.fileDownloadUrl(f)}
                      alt={f}
                      style={{ width: '100%', height: 'auto', borderRadius: 6, border: '1px solid #e0e0e0' }}
                      onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />
                    <div style={{ marginTop: 8 }}>
                      <a className="btn btn-primary" href={`${ApiService.fileDownloadUrl(f)}?download=1`} download={f}>Download</a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div>No plots found yet.</div>
            )}
          </Section>

          <Section title="Detailed Tables (Raw Console Log)">
            {rawLog ? (
              <pre style={{ maxHeight: 400, overflow: 'auto', background: '#0b1020', color: '#e6e6e6', padding: 12, borderRadius: 6, fontSize: 12 }}>
                {rawLog}
              </pre>
            ) : (
              <div>No log captured yet.</div>
            )}
          </Section>
        </>
      )}
    </div>
  );
};

export default Results;

