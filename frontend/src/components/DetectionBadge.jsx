import React from 'react';
import { motion } from 'framer-motion';

export default function DetectionBadge({ domain, confidence, isMismatch, selectedType }) {
  if (!domain) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="detection-badge-bar"
      style={{ marginBottom: '24px' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div 
          className="pulse-dot" 
          style={{ background: isMismatch ? '#f59e0b' : '#6366f1' }}
        />
        <span style={{ fontSize: '14px', fontWeight: 500, color: isMismatch ? '#f59e0b' : '#f7f8f8' }}>
          {isMismatch 
            ? `Mismatch detected: Content looks like ${domain} but you selected ${selectedType}. Switching to ${domain}.`
            : `Detected: ${domain}`}
        </span>
      </div>

      <span className="font-mono" style={{ fontSize: '14px', color: '#8a8a8e' }}>
        Confidence: {confidence}%
      </span>
    </motion.div>
  );
}
