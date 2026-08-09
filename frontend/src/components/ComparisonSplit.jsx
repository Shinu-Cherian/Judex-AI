import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { X, Check, Zap, ShieldCheck } from 'lucide-react';

const ROWS = [
  ['One model, one blind perspective', 'Cross-examined by 3 independent inspector nodes'],
  ['Hallucination-prone, no cross-check', 'Automated 5-point reflection loop before every verdict'],
  ['No awareness of what it missed', 'Explicit gap detection — missing items listed'],
  ['Opaque black-box verdict', 'Full per-model audit trail with confidence scores'],
  ['No dependency awareness', 'Ripple dependency graph maps all affected modules'],
];

function Row({ bad, good, i }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 16 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.45, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
      style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}
    >
      <div className="compare-cell compare-cell-bad">
        <X size={15} style={{ color: '#ff6b6b', flexShrink: 0, marginTop: '1px' }} />
        <span>{bad}</span>
      </div>
      <div className="compare-cell compare-cell-good">
        <Check size={15} style={{ color: '#6bcf9f', flexShrink: 0, marginTop: '1px' }} />
        <span><strong>{good}</strong></span>
      </div>
    </motion.div>
  );
}

export default function ComparisonSplit() {
  return (
    <div className="compare-wrap">
      <div className="compare-header">
        <div className="compare-header-cell compare-header-bad">
          <Zap size={15} />
          Single LLM Prompt
        </div>
        <div className="compare-vs">VS</div>
        <div className="compare-header-cell compare-header-good">
          <ShieldCheck size={15} />
          Judex AI — 4-Model Panel
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {ROWS.map(([bad, good], i) => <Row key={i} bad={bad} good={good} i={i} />)}
      </div>
    </div>
  );
}
