import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

export default function ExtractedItems({ items, selectedItem, onSelectItem }) {
  if (!items || items.length === 0) return null;

  return (
    <div style={{ marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <span className="section-label" style={{ margin: 0 }}>EXTRACTED ITEMS</span>
        <span className="font-mono" style={{
          fontSize: '12px',
          background: 'rgba(99, 102, 241, 0.1)',
          color: '#6366f1',
          padding: '2px 8px',
          borderRadius: '999px',
          fontWeight: 500
        }}>
          {items.length}
        </span>
      </div>

      <div className="items-scroll-row">
        {items.map((item, idx) => {
          const isSelected = selectedItem?._idx === idx;
          const snippetText = String(item.snippet || item.title || '');
          return (
            <motion.div
              key={`item-${idx}-${item.title}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.05 }}
              className={`item-card ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelectItem && onSelectItem({ ...item, _idx: idx })}
            >
              {isSelected && (
                <div style={{ position: 'absolute', top: '12px', right: '12px' }}>
                  <Check size={14} color="#6366f1" />
                </div>
              )}

              <div style={{ fontSize: '14px', fontWeight: 600, color: '#f7f8f8', marginBottom: '6px', paddingRight: '16px' }}>
                {item.title || 'Code Snippet'}
              </div>

              <div style={{ fontSize: '12px', color: '#5c5c5f', lineHeight: 1.4, marginBottom: '12px' }}>
                {snippetText.substring(0, 55)}{snippetText.length > 55 ? '...' : ''}
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '11px', textTransform: 'uppercase', color: '#5c5c5f', fontWeight: 500 }}>
                  {item.type || 'CODE'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div style={{ fontSize: '12px', color: '#5c5c5f', marginTop: '8px' }}>
        Click any item to run the Panel of Judges analysis
      </div>
    </div>
  );
}
