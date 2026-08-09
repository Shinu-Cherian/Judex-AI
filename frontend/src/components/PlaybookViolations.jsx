import React from 'react';
import { ShieldAlert, ShieldCheck, CheckCircle2 } from 'lucide-react';
import CitationText from './CitationText';

export default function PlaybookViolations({ playbook }) {
  if (!playbook || !playbook.enabled) return null;

  const violations = playbook.violations || [];
  const passed = playbook.passed || [];
  const hasViolations = violations.length > 0;

  return (
    <div className="linear-card" style={{ marginBottom: '32px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {hasViolations ? <ShieldAlert size={18} color="#ef4444" /> : <ShieldCheck size={18} color="#22c55e" />}
          <div>
            <div className="section-label" style={{ margin: 0 }}>
              JUDEX PLAYBOOK COMPLIANCE {playbook.profile_name ? `— ${playbook.profile_name}` : ''}
            </div>
            <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: '2px' }}>
              Your org's own rules, enforced on every audit — not generic AI findings.
            </div>
          </div>
        </div>
        <span style={{
          fontSize: '11px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700,
          color: hasViolations ? '#ef4444' : '#22c55e',
          background: hasViolations ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)',
          border: `1px solid ${hasViolations ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)'}`,
          padding: '4px 12px', borderRadius: '999px'
        }}>
          {hasViolations ? `${violations.length} RULE${violations.length > 1 ? 'S' : ''} VIOLATED` : 'ALL RULES PASSED'}
        </span>
      </div>

      {hasViolations && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '18px' }}>
          {violations.map((v) => (
            <div key={v.id} style={{
              border: '1px solid rgba(239,68,68,0.25)', background: 'rgba(239,68,68,0.04)',
              borderRadius: '8px', padding: '12px 16px'
            }}>
              <div style={{ fontSize: '13px', color: '#f7f8f8', fontWeight: 600 }}>
                ❌ Rule violated: {v.title}
              </div>
              <div style={{ fontSize: '12px', color: '#8a8a8e', marginTop: '4px' }}>
                {v.evidence} · <CitationText text={`[${v.standard}]`} />
              </div>
              <div style={{ fontSize: '12px', color: '#c7d2fe', marginTop: '6px' }}>
                Fix: {v.fix_hint}
              </div>
            </div>
          ))}
        </div>
      )}

      {passed.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: hasViolations ? '16px' : '18px' }}>
          {passed.map((p) => (
            <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#8a8a8e' }}>
              <CheckCircle2 size={13} color="#22c55e" style={{ flexShrink: 0 }} />
              {p.title}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
