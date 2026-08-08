import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function MissingClauses({ clauses }) {
  if (!clauses || clauses.length === 0) return null;

  return (
    <div className="linear-card" style={{ height: '100%' }}>
      <div className="section-header-label" style={{ marginBottom: '20px' }}>
        MISSING LEGAL SAFEGUARDS
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {clauses.map((item, idx) => (
          <div key={idx} className="missing-clause-row">
            <AlertTriangle size={16} color="#ef4444" style={{ flexShrink: 0 }} />
            <span style={{ fontSize: '14px', color: '#f7f8f8', fontWeight: 400 }}>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
