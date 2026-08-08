import React from 'react';

export default function TemporalRisk({ temporal }) {
  if (!temporal) return null;

  return (
    <div className="linear-card" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div className="section-label" style={{ marginBottom: '4px' }}>
          TEMPORAL RISK ANALYSIS
        </div>
        <div style={{ fontSize: '12px', color: '#5c5c5f', marginBottom: '20px' }}>
          How risk has changed over time
        </div>

        <div className="stat-grid-2x2">
          <div className="stat-mini-card">
            <div style={{ fontSize: '11px', fontWeight: 500, color: '#5c5c5f', textTransform: 'uppercase', marginBottom: '4px' }}>
              2020 STANDARD
            </div>
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#22c55e' }}>
              {temporal.risk_2020}
            </div>
          </div>

          <div className="stat-mini-card">
            <div style={{ fontSize: '11px', fontWeight: 500, color: '#5c5c5f', textTransform: 'uppercase', marginBottom: '4px' }}>
              2026 STANDARD
            </div>
            <div style={{ fontSize: '18px', fontWeight: 600, color: temporal.risk_2026 === 'CRITICAL' ? '#dc2626' : '#ef4444' }}>
              {temporal.risk_2026}
            </div>
          </div>

          <div className="stat-mini-card">
            <div style={{ fontSize: '11px', fontWeight: 500, color: '#5c5c5f', textTransform: 'uppercase', marginBottom: '4px' }}>
              STANDARDS DRIFT
            </div>
            <div className="font-mono" style={{ fontSize: '18px', fontWeight: 600, color: '#f7f8f8' }}>
              {temporal.drift || '2 levels'}
            </div>
          </div>

          <div className="stat-mini-card">
            <div style={{ fontSize: '11px', fontWeight: 500, color: '#5c5c5f', textTransform: 'uppercase', marginBottom: '4px' }}>
              DEPRECATED APIS
            </div>
            <div className="font-mono" style={{ fontSize: '18px', fontWeight: 600, color: '#f7f8f8' }}>
              {temporal.deprecated || '3 found'}
            </div>
          </div>
        </div>
      </div>

      <div style={{ fontSize: '13px', color: '#8a8a8e', lineHeight: 1.5, marginTop: '16px' }}>
        {temporal.explanation}
      </div>
    </div>
  );
}
