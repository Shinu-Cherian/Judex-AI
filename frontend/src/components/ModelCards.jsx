import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';

export default function ModelCards({ models }) {
  if (!models || models.length === 0) return null;

  return (
    <div style={{ marginBottom: '32px' }}>
      <div className="section-header-label" style={{ marginBottom: '16px' }}>
        PANEL OF JUDGES
      </div>

      <div className="models-grid-3col">
        {models.map((m, idx) => {
          const chartData = [{ name: 'Confidence', value: m.confidence, fill: '#6366f1' }];
          const riskClass = m.risk_level === 'HIGH' ? 'pill-high' : m.risk_level === 'MEDIUM' ? 'pill-medium' : 'pill-low';

          return (
            <div key={idx} className="linear-card linear-card-hover">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#f7f8f8' }}>{m.name}</div>
                  <div style={{ fontSize: '12px', fontWeight: 400, color: '#8a8a8e', marginTop: '2px' }}>{m.role}</div>
                </div>
              </div>

              <div className="model-card-divider"></div>

              {/* Recharts Circular Confidence Ring */}
              <div className="ring-container">
                <ResponsiveContainer width={90} height={90}>
                  <RadialBarChart
                    innerRadius="75%"
                    outerRadius="100%"
                    data={chartData}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <RadialBar
                      clockWise
                      dataKey="value"
                      cornerRadius={10}
                      background={{ fill: '#1c1c1f' }}
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="ring-text font-mono">{m.confidence}%</div>
              </div>

              <div style={{ textAlign: 'left' }}>
                <span className={`pill-risk-badge ${riskClass}`}>
                  {m.risk_level} RISK
                </span>
              </div>

              <div className="bullet-list">
                {m.findings.map((f, fIdx) => (
                  <div key={fIdx} className="bullet-item">
                    <div className="bullet-dot"></div>
                    <div>{f}</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
