import React from 'react';
import { LoaderCircle } from 'lucide-react';

export default function ClauseInput({ clause, setClause, samples = [], onAnalyze, loading }) {
  const handleSampleSelect = (e) => {
    const selectedId = e.target.value;
    const found = samples.find(s => s.id === selectedId);
    if (found) {
      setClause(found.text);
    }
  };

  return (
    <div style={{ marginBottom: '32px' }}>
      <div className="linear-card" style={{ padding: '24px' }}>
        <div className="input-grid">
          {/* Left Column: 70% width */}
          <div>
            <textarea
              className="clause-textarea"
              value={clause}
              onChange={(e) => setClause(e.target.value)}
              placeholder="Paste a contract clause to analyze..."
            />
          </div>

          {/* Right Column: 30% width */}
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <select className="clause-select" onChange={handleSampleSelect} defaultValue="">
                <option value="" disabled>Preset Samples</option>
                {samples.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                  </option>
                ))}
              </select>
            </div>

            <button className="analyze-button" onClick={onAnalyze} disabled={loading || !clause.trim()}>
              {loading ? (
                <>
                  <LoaderCircle size={16} className="spin-icon" />
                  Analyzing...
                </>
              ) : (
                'Analyze'
              )}
            </button>
          </div>
        </div>
      </div>

      <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: '8px' }}>
        3 AI models will independently analyze this clause, then a Chief Judge synthesizes their findings.
      </div>
    </div>
  );
}
