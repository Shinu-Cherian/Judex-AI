import React from 'react';

export default function ChiefJudgeAssessment({ judge }) {
  if (!judge) return null;

  const isHigh = judge.final_risk === 'HIGH';
  const isMedium = judge.final_risk === 'MEDIUM';

  const badgeClass = isHigh
    ? 'risk-large-badge'
    : isMedium
    ? 'risk-large-badge risk-large-badge-medium'
    : 'risk-large-badge risk-large-badge-low';

  const textClass = isHigh
    ? 'risk-badge-text-high'
    : isMedium
    ? 'risk-badge-text-medium'
    : 'risk-badge-text-low';

  return (
    <div className="chief-judge-card" style={{ marginBottom: '32px' }}>
      {/* Left Column: 30% width */}
      <div className={badgeClass}>
        <div className={textClass} style={{ fontSize: '28px', fontWeight: 700, letterSpacing: '0.02em', marginBottom: '12px' }}>
          {judge.final_risk} RISK
        </div>
        <div style={{ fontSize: '16px', color: '#8a8a8e' }} className="font-mono">
          Weighted Confidence: {judge.weighted_confidence}%
        </div>
      </div>

      {/* Right Column: 70% width */}
      <div>
        <div style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', color: '#5c5c5f', marginBottom: '8px', letterSpacing: '0.05em' }}>
          CHIEF JUDGE ASSESSMENT
        </div>

        <p style={{ fontSize: '14px', color: '#f7f8f8', lineHeight: 1.6, marginBottom: '24px' }}>
          {judge.summary}
        </p>

        <div style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', color: '#5c5c5f', marginBottom: '12px', letterSpacing: '0.05em' }}>
          PRIORITIZED RECOMMENDATIONS
        </div>

        <div className="recommendation-list">
          {judge.recommendations.map((rec, idx) => (
            <div key={idx} className="recommendation-row">
              <span className="rec-number font-mono">{idx + 1}.</span>
              <span style={{ fontSize: '14px', color: '#f7f8f8', lineHeight: 1.5 }}>{rec}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
