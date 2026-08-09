import React from 'react';
import { Database, ShieldCheck, Sparkles, History, CheckCircle2 } from 'lucide-react';
import { resolveCitationUrl } from '../utils/citationLinks';

export default function PrecedentMemoryCard({ precedent }) {
  if (!precedent) return null;

  const {
    matched_pattern = "SQL Query Interpolation in Data Access Layer",
    historical_resolution = "In prior enterprise production audits, raw query concatenation was remediated using Parameterized Statements & HikariCP Connection Pooling.",
    benchmark_standard = "OWASP-A03-2025 / Enterprise Baseline",
    confidence_score = 96,
    has_precedent = true
  } = precedent;

  return (
    <div style={{
      background: 'rgba(15, 17, 26, 0.95)',
      border: '1px solid rgba(129, 140, 248, 0.3)',
      borderRadius: '12px',
      padding: '20px 24px',
      marginTop: '20px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: '8px',
            background: 'rgba(129, 140, 248, 0.15)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', color: '#818cf8'
          }}>
            <History size={18} />
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-heading)', fontFamily: 'Outfit, sans-serif', letterSpacing: '0.04em' }}>
              INSTITUTIONAL AUDIT PRECEDENT MEMORY
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
              Recursive Security Context Engineering · Enterprise Historical Precedents
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700,
            color: '#34d399', background: 'rgba(52, 211, 153, 0.12)',
            border: '1px solid rgba(52, 211, 153, 0.3)', padding: '3px 10px', borderRadius: '999px',
            display: 'inline-flex', alignItems: 'center', gap: '4px'
          }}>
            <CheckCircle2 size={12} /> {confidence_score}% PRECEDENT MATCH
          </span>
        </div>
      </div>

      {/* Main Body */}
      {has_precedent ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px', padding: '12px 16px'
          }}>
            <div style={{ fontSize: '10px', fontWeight: 700, color: '#818cf8', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.06em', marginBottom: '4px' }}>
              MATCHED PATTERN & STANDARD
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-heading)', fontWeight: 600, fontFamily: 'Outfit, sans-serif' }}>
              {matched_pattern} <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 400 }}>
                ({benchmark_standard.split('/').map((s, i, arr) => (
                  <React.Fragment key={i}>
                    <a
                      href={resolveCitationUrl(s.trim())}
                      target="_blank"
                      rel="noreferrer"
                      style={{ color: '#818cf8', textDecoration: 'none', borderBottom: '1px dashed rgba(129, 140, 248, 0.5)' }}
                    >
                      {s.trim()}
                    </a>
                    {i < arr.length - 1 ? ' / ' : ''}
                  </React.Fragment>
                ))})
              </span>
            </div>
          </div>

          <div style={{
            background: 'rgba(129, 140, 248, 0.05)',
            border: '1px solid rgba(129, 140, 248, 0.2)',
            borderRadius: '8px', padding: '12px 16px'
          }}>
            <div style={{ fontSize: '10px', fontWeight: 700, color: '#c7d2fe', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.06em', marginBottom: '4px' }}>
              HISTORICAL AUDIT RESOLUTION PRECEDENT
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-body)', lineHeight: 1.6 }}>
              {historical_resolution}
            </div>
          </div>
        </div>
      ) : (
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
          No historical security precedent violation found — Code adheres to clean production baseline standards.
        </div>
      )}
    </div>
  );
}
