import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function MissingItems({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="linear-card" style={{ height: '100%' }}>
      <div className="section-label" style={{ marginBottom: '4px' }}>
        MISSING BEST PRACTICES
      </div>
      <div style={{ fontSize: '12px', color: '#5c5c5f', marginBottom: '20px' }}>
        Critical items not found in this code
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {items.map((item, idx) => (
          <div key={idx} className="missing-item-row">
            <AlertTriangle size={16} color="#ef4444" style={{ flexShrink: 0 }} />
            <span style={{ fontSize: '14px', color: '#f7f8f8', fontWeight: 500 }}>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
