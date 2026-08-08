import React, { useState } from 'react';
import { Key, Save, X, Info } from 'lucide-react';

export default function ApiKeyModal({ isOpen, onClose, keys, setKeys, onSave }) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div className="glass-card" style={{ maxWidth: '540px', width: '100%', marginBottom: 0, background: '#121824', border: '1px solid rgba(255, 255, 255, 0.15)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div className="section-title" style={{ margin: 0 }}>
            <Key size={20} color="#10b981" />
            Configure Free LLM API Keys
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ fontSize: '0.86rem', color: '#9ca3af', marginBottom: '20px', lineHeight: '1.5', background: 'rgba(6, 182, 212, 0.08)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
          <Info size={16} color="#06b6d4" style={{ display: 'inline', marginRight: '6px' }} />
          Enter your free API keys below. They are passed directly to live AI models (Google Gemini & Groq).
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, marginBottom: '6px', color: '#f3f4f6' }}>
            Google Gemini API Key (Gemini 2.0 Flash / 1.5 Pro)
          </label>
          <input
            type="password"
            value={keys.geminiKey}
            onChange={(e) => setKeys({ ...keys, geminiKey: e.target.value })}
            placeholder="AIzaSy..."
            style={{
              width: '100%',
              padding: '12px 14px',
              background: 'rgba(10, 13, 20, 0.9)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#f3f4f6',
              fontFamily: 'monospace',
              outline: 'none'
            }}
          />
          <span style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px', display: 'block' }}>
            Free key from <a href="https://aistudio.google.com" target="_blank" rel="noreferrer" style={{ color: '#06b6d4' }}>aistudio.google.com</a>
          </span>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, marginBottom: '6px', color: '#f3f4f6' }}>
            Groq API Key (Llama 3.3 70B & Mixtral 8x7B)
          </label>
          <input
            type="password"
            value={keys.groqKey}
            onChange={(e) => setKeys({ ...keys, groqKey: e.target.value })}
            placeholder="gsk_..."
            style={{
              width: '100%',
              padding: '12px 14px',
              background: 'rgba(10, 13, 20, 0.9)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#f3f4f6',
              fontFamily: 'monospace',
              outline: 'none'
            }}
          />
          <span style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px', display: 'block' }}>
            Free key from <a href="https://console.groq.com" target="_blank" rel="noreferrer" style={{ color: '#06b6d4' }}>console.groq.com</a>
          </span>
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button 
            onClick={onClose}
            style={{
              padding: '10px 18px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#9ca3af',
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>
          <button 
            onClick={onSave}
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #06b6d4, #8b5cf6)',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Save size={16} />
            Save & Connect Live LLMs
          </button>
        </div>
      </div>
    </div>
  );
}
