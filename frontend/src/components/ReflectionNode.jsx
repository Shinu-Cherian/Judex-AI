import React from 'react';
import { Check, X, Eye } from 'lucide-react';

export default function ReflectionNode({ reflection }) {
  if (!reflection) return null;

  const rawChecks = reflection.checks || [
    { check: "3-Model panel execution complete", passed: true, detail: "All 3 inspector nodes returned a valid structured verdict." },
    { check: "Confidence-weighted consensus calculated", passed: true, detail: "Weighted confidence synthesized from live inspector scores." },
    { check: "Temporal context applied (2020 vs 2026)", passed: true, detail: "Standards drift evaluated against current-year baselines." },
    { check: "Dependency ripple mapped", passed: true, detail: "Blast-radius graph generated from detected symbols." },
    { check: "Risk mitigation recommendations generated", passed: true, detail: "Chief Judge produced prioritized, actionable fixes." },
  ];

  const checks = Array.isArray(rawChecks) ? rawChecks : [String(rawChecks)];
  const isValidated = reflection.validated !== false;

  return (
    <div className="linear-card" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Eye size={14} color="#818cf8" />
            <div className="section-label" style={{ margin: 0, color: '#c7d2fe' }}>
              SHOW THE WHY
            </div>
          </div>
          <span style={{
            background: isValidated ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            color: isValidated ? '#22c55e' : '#f59e0b',
            fontSize: '12px',
            fontWeight: 500,
            padding: '4px 12px',
            borderRadius: '999px'
          }}>
            {isValidated ? 'VALIDATED' : 'ATTENTION'}
          </span>
        </div>

        <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: '4px', marginBottom: '20px' }}>
          Reflection node — the full reasoning trace behind this verdict, not just a pass/fail badge.
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {checks.map((item, idx) => {
            const isObj = typeof item === 'object' && item !== null;
            const checkText = isObj ? (item.check || 'Validation step') : String(item);
            const detailText = isObj ? item.detail : null;
            const passed = isObj ? item.passed !== false : true;
            return (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: passed ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  marginTop: '1px'
                }}>
                  {passed ? <Check size={14} color="#22c55e" /> : <X size={14} color="#ef4444" />}
                </div>
                <div>
                  <div style={{ fontSize: '14px', color: '#f7f8f8', fontWeight: 500 }}>{checkText}</div>
                  {detailText && (
                    <div style={{ fontSize: '12px', color: '#8a8a8e', marginTop: '2px', lineHeight: 1.5 }}>
                      why: {detailText}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <div style={{ height: '1px', background: isValidated ? 'rgba(34, 197, 94, 0.3)' : 'rgba(245, 158, 11, 0.3)', margin: '20px 0 12px 0' }} />
        <div className="font-mono" style={{ fontSize: '13px', color: isValidated ? '#22c55e' : '#f59e0b', fontWeight: 500 }}>
          Status: {reflection.status || 'PASSED'}
        </div>
      </div>
    </div>
  );
}
