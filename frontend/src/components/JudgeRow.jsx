import React from 'react';
import JudgeCard from './JudgeCard';

export default function JudgeRow({ models }) {
  if (!models || models.length === 0) return null;

  return (
    <div style={{ marginBottom: '32px' }}>
      <div className="section-label" style={{ marginBottom: '16px' }}>
        PANEL OF JUDGES
      </div>

      <div className="models-grid-3col">
        {models.map((m, idx) => (
          <JudgeCard key={idx} model={m} />
        ))}
      </div>
    </div>
  );
}
