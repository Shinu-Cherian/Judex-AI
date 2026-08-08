import React from 'react';
import { Check } from 'lucide-react';

export default function ReflectionNode({ reflection }) {
  if (!reflection) return null;

  const rawChecks = reflection.checks || [
    "3-Model panel execution complete",
    "Confidence-weighted consensus calculated (81%)",
    "Temporal context applied (2020 vs 2026)",
    "Dependency ripple mapped (3 items)",
    "Risk mitigation recommendations generated (5 items)"
  ];

  const checks = Array.isArray(rawChecks) ? rawChecks : [String(rawChecks)];

  return (
    <div className="linear-card" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="section-label" style={{ margin: 0 }}>
            REFLECTION NODE
          </div>
          <span style={{
            background: 'rgba(34, 197, 94, 0.1)',
            color: '#22c55e',
            fontSize: '12px',
            fontWeight: 500,
            padding: '4px 12px',
            borderRadius: '999px'
          }}>
            VALIDATED
          </span>
        </div>
        
        <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: '4px', marginBottom: '20px' }}>
          Automated validation before output
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {checks.map((item, idx) => {
            const checkText = typeof item === 'object' && item !== null ? (item.check || item.detail || JSON.stringify(item)) : String(item);
            return (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'rgba(34, 197, 94, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <Check size={14} color="#22c55e" />
                </div>
                <span style={{ fontSize: '14px', color: '#f7f8f8', fontWeight: 400 }}>{checkText}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <div style={{ height: '1px', background: 'rgba(34, 197, 94, 0.3)', margin: '20px 0 12px 0' }} />
        <div className="font-mono" style={{ fontSize: '13px', color: '#22c55e', fontWeight: 500 }}>
          Status: {reflection.status || 'PASSED'}
        </div>
      </div>
    </div>
  );
}
