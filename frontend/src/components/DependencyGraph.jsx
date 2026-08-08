import React, { useState } from 'react';
import { ReactFlow, Background, Handle, Position, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ShieldAlert, Zap, Layers } from 'lucide-react';

const CustomNode = ({ data }) => {
  const isSelected = data.isSelected;
  const isCentral = data.isCentral;
  const badgeType = data.badgeType || 'DEPENDENCY OK';

  let borderColor = isCentral ? '#6366f1' : '#27272a';
  let glowStyle = isCentral ? '0 0 12px rgba(99, 102, 241, 0.4)' : 'none';
  let badgeBg = 'rgba(255, 255, 255, 0.05)';
  let badgeColor = '#9ca3af';

  if (badgeType === 'MUST UPDATE' || badgeType === 'HIGH') {
    borderColor = '#ef4444';
    glowStyle = '0 0 14px rgba(239, 68, 68, 0.35)';
    badgeBg = 'rgba(239, 68, 68, 0.15)';
    badgeColor = '#f87171';
  } else if (badgeType === 'REVIEW NEEDED' || badgeType === 'MEDIUM') {
    borderColor = '#f59e0b';
    glowStyle = '0 0 14px rgba(245, 158, 11, 0.35)';
    badgeBg = 'rgba(245, 158, 11, 0.15)';
    badgeColor = '#fbbf24';
  } else if (badgeType === 'DEPENDENCY OK' || badgeType === 'LOW') {
    borderColor = '#10b981';
    glowStyle = '0 0 10px rgba(16, 185, 129, 0.25)';
    badgeBg = 'rgba(16, 185, 129, 0.15)';
    badgeColor = '#34d399';
  }

  if (isSelected) {
    glowStyle += ', 0 0 20px rgba(255, 255, 255, 0.6)';
  }

  return (
    <div style={{
      background: 'rgba(15, 16, 17, 0.95)',
      border: `1.5px solid ${borderColor}`,
      boxShadow: glowStyle,
      borderRadius: '10px',
      padding: '12px 16px',
      color: '#f7f8f8',
      fontSize: '13px',
      fontWeight: 600,
      minWidth: '190px',
      cursor: 'pointer',
      transition: 'all 0.25s ease'
    }}>
      <Handle type="target" position={Position.Left} style={{ background: borderColor, border: 'none', width: '8px', height: '8px' }} />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        <span style={{ fontFamily: isCentral ? 'Outfit, sans-serif' : 'JetBrains Mono, monospace', fontSize: '13px' }}>
          {data.label}
        </span>
        {isCentral && <Layers size={14} style={{ color: '#818cf8' }} />}
      </div>
      {data.badge && (
        <div style={{
          marginTop: '6px',
          padding: '2px 8px',
          borderRadius: '6px',
          fontSize: '10px',
          fontWeight: 700,
          fontFamily: 'JetBrains Mono, monospace',
          background: badgeBg,
          color: badgeColor,
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          letterSpacing: '0.05em'
        }}>
          {badgeType === 'MUST UPDATE' && <ShieldAlert size={10} />}
          {data.badge}
        </div>
      )}
      <Handle type="source" position={Position.Right} style={{ background: borderColor, border: 'none', width: '8px', height: '8px' }} />
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

export default function DependencyGraph({ dependencies, centralTitle = "process_payment" }) {
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  const nodeItems = dependencies?.affected_clauses || [
    { name: "checkout_flow", status: "MUST UPDATE" },
    { name: "retry_payment", status: "MUST UPDATE" },
    { name: "refund_handler", status: "REVIEW NEEDED" }
  ];

  const highRiskCount = nodeItems.filter(i => i.status === 'MUST UPDATE' || i.status === 'HIGH').length;

  const nodes = [
    {
      id: 'center',
      type: 'custom',
      position: { x: 40, y: Math.max(40, (nodeItems.length * 75) / 2 - 20) },
      data: { label: centralTitle, isCentral: true, isSelected: selectedNodeId === 'center' }
    },
    ...nodeItems.map((item, idx) => ({
      id: `child_${idx}`,
      type: 'custom',
      position: { x: 360, y: 20 + idx * 75 },
      data: {
        label: item.name,
        badge: item.status,
        badgeType: item.status,
        isSelected: selectedNodeId === `child_${idx}`
      }
    }))
  ];

  const edges = nodeItems.map((item, idx) => {
    const isMustUpdate = item.status === 'MUST UPDATE';
    const edgeColor = isMustUpdate ? '#ef4444' : item.status === 'REVIEW NEEDED' ? '#f59e0b' : '#34d399';
    return {
      id: `e-center-${idx}`,
      source: 'center',
      target: `child_${idx}`,
      animated: true,
      style: {
        stroke: edgeColor,
        strokeWidth: isMustUpdate ? 2 : 1.5,
        strokeDasharray: isMustUpdate ? 'none' : '5 5'
      }
    };
  });

  return (
    <div className="linear-card" style={{ padding: '24px', minHeight: '340px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="section-label" style={{ margin: 0 }}>
            INTERACTIVE AST BLAST-RADIUS DEPENDENCY GRAPH
          </div>
          <span style={{
            fontSize: '10px', fontFamily: 'JetBrains Mono, monospace',
            color: highRiskCount > 0 ? '#f87171' : '#34d399',
            background: highRiskCount > 0 ? 'rgba(239,68,68,0.1)' : 'rgba(52,211,153,0.1)',
            border: `1px solid ${highRiskCount > 0 ? 'rgba(239,68,68,0.25)' : 'rgba(52,211,153,0.25)'}`,
            borderRadius: '4px', padding: '1px 6px', fontWeight: 600
          }}>
            {highRiskCount > 0 ? `HIGH BLAST RADIUS (${highRiskCount} CRITICAL)` : 'LOW BLAST RADIUS'}
          </span>
        </div>
        <div className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Ripple Effect: {nodeItems.length} items affected
        </div>
      </div>

      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '18px' }}>
        Heat-mapped visual blast-radius showing real-time dependency chain ripples if <span style={{ color: '#818cf8', fontWeight: 600 }}>{centralTitle}</span> is modified
      </div>

      <div style={{ width: '100%', height: '260px', background: '#090a0f', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)', overflow: 'hidden' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodeClick={(_, node) => setSelectedNodeId(node.id)}
          fitView
          attributionPosition="bottom-left"
        >
          <Background color="#1e1e24" gap={18} size={1} />
          <Controls style={{ background: '#0f1011', border: '1px solid #1c1c1f', color: '#8a8a8e' }} />
          <MiniMap style={{ background: '#0a0a0b', border: '1px solid #1c1c1f' }} nodeColor={n => n.id === 'center' ? '#6366f1' : '#ef4444'} />
        </ReactFlow>
      </div>
    </div>
  );
}
