import React from 'react';

export default function ConsensusMap({ heatmap }) {
  if (!heatmap) return null;

  return (
    <div className="linear-card" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div className="section-label" style={{ marginBottom: '4px' }}>
          CONSENSUS MAP
        </div>
        <div style={{ fontSize: '12px', color: '#5c5c5f', marginBottom: '20px' }}>
          Where the models agree and disagree
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {heatmap.map((item, idx) => {
            const isRed = item.disagreement === 'HIGH';
            const isAmber = item.disagreement === 'MEDIUM';
            const barColor = isRed ? '#ef4444' : isAmber ? '#f59e0b' : '#22c55e';
            const pct = isRed ? 100 : isAmber ? 66 : 100;
            const badgeText = isRed ? '3/3' : isAmber ? '2/3' : '3/3';

            return (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '14px', color: '#f7f8f8', fontWeight: 500 }}>{item.topic}</span>
                  <span className="font-mono" style={{
                    fontSize: '13px',
                    padding: '2px 8px',
                    borderRadius: '999px',
                    background: isRed ? 'rgba(239, 68, 68, 0.1)' : isAmber ? 'rgba(245, 158, 11, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                    color: barColor
                  }}>
                    {badgeText}
                  </span>
                </div>

                <div style={{ width: '100%', height: '8px', background: '#1c1c1f', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${pct}%`, height: '100%', background: barColor, borderRadius: '4px' }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: '16px' }}>
        Higher disagreement = more attention needed
      </div>
    </div>
  );
}
