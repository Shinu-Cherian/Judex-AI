import React from 'react';

export default function DisagreementHeatmap({ heatmap }) {
  if (!heatmap) return null;

  return (
    <div className="linear-card" style={{ height: '100%' }}>
      <div className="section-header-label" style={{ marginBottom: '20px' }}>
        CONSENSUS MAP
      </div>

      <div style={{ marginBottom: '20px' }}>
        {heatmap.map((item, idx) => {
          const barColor = item.disagreement === 'HIGH' ? '#ef4444' : item.disagreement === 'MEDIUM' ? '#f59e0b' : '#22c55e';
          const pct = item.disagreement === 'HIGH' ? 100 : item.disagreement === 'MEDIUM' ? 66 : 33;

          return (
            <div key={idx} style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '14px', color: '#f7f8f8', fontWeight: 400 }}>{item.topic}</span>
                <span className="font-mono" style={{ fontSize: '13px', color: '#8a8a8e' }}>
                  {item.disagreement === 'HIGH' ? '3/3' : item.disagreement === 'MEDIUM' ? '2/3' : '3/3'}
                </span>
              </div>

              <div className="consensus-bar-track">
                <div 
                  className="consensus-bar-fill" 
                  style={{ width: `${pct}%`, backgroundColor: barColor }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: 'auto' }}>
        Higher disagreement = more attention needed
      </div>
    </div>
  );
}
