import React from 'react';
import { Cpu } from 'lucide-react';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';

export default function JudgeCard({ model }) {
  if (!model) return null;

  const confidenceVal = typeof model.confidence === 'number' ? model.confidence : 85;
  const chartData = [{ name: 'Confidence', value: confidenceVal, fill: '#6366f1' }];

  const getPillStyle = (risk) => {
    switch (risk) {
      case 'CRITICAL': return { bg: 'rgba(220, 38, 38, 0.1)', color: '#dc2626' };
      case 'HIGH': return { bg: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' };
      case 'MEDIUM': return { bg: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' };
      default: return { bg: 'rgba(34, 197, 94, 0.1)', color: '#22c55e' };
    }
  };

  const pStyle = getPillStyle(model.risk_level || 'LOW');
  const findingsList = Array.isArray(model.findings) ? model.findings : [String(model.findings || 'Analysis completed')];

  return (
    <div className="linear-card linear-card-hover" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '14px', fontWeight: 600, color: '#f7f8f8' }}>{model.name || 'AI Inspector'}</div>
        <Cpu size={16} color="#5c5c5f" />
      </div>

      <div style={{ fontSize: '12px', fontWeight: 400, color: '#8a8a8e', marginTop: '2px' }}>
        {model.role || 'Inspector'}
      </div>

      <div style={{ height: '1px', background: '#1c1c1f', margin: '16px 0' }} />

      <div className="ring-container">
        <ResponsiveContainer width={100} height={100}>
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
              animationDuration={800}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="ring-text font-mono">{confidenceVal}%</div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '12px', marginBottom: '16px' }}>
        <span
          className="pill-badge"
          style={{ background: pStyle.bg, color: pStyle.color }}
        >
          {model.risk_level || 'LOW'} RISK
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
        {findingsList.map((f, idx) => (
          <div key={idx} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
            <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#5c5c5f', marginTop: '7px', flexShrink: 0 }} />
            <div style={{ fontSize: '13px', color: '#8a8a8e', lineHeight: 1.5 }}>{typeof f === 'object' ? JSON.stringify(f) : String(f)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
