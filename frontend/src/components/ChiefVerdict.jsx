import React from 'react';
import CitationText from './CitationText';

export default function ChiefVerdict({ judge }) {
  if (!judge) return null;

  const getRiskStyle = (risk) => {
    switch (risk) {
      case 'CRITICAL':
        return { bg: 'rgba(220, 38, 38, 0.1)', border: '1px solid #dc2626', color: '#dc2626' };
      case 'HIGH':
        return { bg: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#ef4444' };
      case 'MEDIUM':
        return { bg: 'rgba(245, 158, 11, 0.1)', border: '1px solid #f59e0b', color: '#f59e0b' };
      default:
        return { bg: 'rgba(34, 197, 94, 0.1)', border: '1px solid #22c55e', color: '#22c55e' };
    }
  };

  const riskLevel = judge.final_risk || 'MEDIUM';
  const confidence = judge.weighted_confidence ?? 85;
  const rStyle = getRiskStyle(riskLevel);
  const recs = Array.isArray(judge.recommendations) ? judge.recommendations : [String(judge.recommendations || 'Review findings')];

  return (
    <div className="chief-verdict-card" style={{ marginBottom: '32px' }}>
      {/* Left Column (30% width) */}
      <div style={{ flex: '30%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{
          background: rStyle.bg,
          border: rStyle.border,
          color: rStyle.color,
          borderRadius: '8px',
          padding: '16px 24px',
          textAlign: 'center',
          fontSize: '28px',
          fontWeight: 700,
          marginBottom: '16px'
        }}>
          {riskLevel}
        </div>

        <div style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', color: '#5c5c5f', marginBottom: '4px' }}>
          WEIGHTED CONFIDENCE
        </div>

        <div className="font-mono" style={{ fontSize: '32px', fontWeight: 600, color: '#f7f8f8', marginBottom: '8px' }}>
          {confidence}%
        </div>

        <div style={{ width: '100%', height: '4px', background: '#1c1c1f', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ width: `${Math.min(100, Math.max(0, confidence))}%`, height: '100%', background: '#6366f1' }} />
        </div>
      </div>

      {/* Right Column (70% width) */}
      <div style={{ flex: '70%' }}>
        <div style={{ fontSize: '14px', fontWeight: 600, textTransform: 'uppercase', color: '#8a8a8e', letterSpacing: '0.05em' }}>
          CHIEF JUDGE ASSESSMENT
        </div>

        <div style={{ fontSize: '14px', color: '#f7f8f8', lineHeight: 1.6, marginTop: '8px' }}>
          <CitationText text={judge.summary || 'Analysis complete.'} />
        </div>

        <div style={{ height: '1px', background: '#1c1c1f', margin: '20px 0' }} />

        <div style={{ fontSize: '14px', fontWeight: 600, textTransform: 'uppercase', color: '#8a8a8e', letterSpacing: '0.05em' }}>
          PRIORITIZED RECOMMENDATIONS
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
          {recs.map((rec, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <span className="font-mono" style={{ fontSize: '14px', color: '#6366f1', fontWeight: 500, minWidth: '20px' }}>
                {idx + 1}.
              </span>
              <span style={{ fontSize: '14px', color: '#f7f8f8', lineHeight: 1.5 }}>
                <CitationText text={rec} />
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
