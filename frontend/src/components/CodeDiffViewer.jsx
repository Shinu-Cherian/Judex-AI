import React, { useState } from 'react';
import { Copy, Check, Download, ShieldCheck, Sparkles, FileCode } from 'lucide-react';

export default function CodeDiffViewer({ originalCode, patchedCode, diffLines, summaryOfChanges, filename = "file", zipFile = null, onDownloadPatchedZip = null }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(patchedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadFile = () => {
    const blob = new Blob([patchedCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `patched_${filename}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      background: 'rgba(15,16,20,0.95)',
      border: '1px solid rgba(52,211,153,0.3)',
      borderRadius: '12px',
      padding: '24px',
      marginTop: '20px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
    }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: '8px',
            background: 'rgba(52,211,153,0.15)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', color: '#34d399'
          }}>
            <Sparkles size={18} />
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-heading)', fontFamily: 'Outfit, sans-serif' }}>
              AUTONOMOUS AI SECURITY PATCH
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
              Non-Destructive AST-Preserved Fix · {filename}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={handleCopy}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '6px 12px', borderRadius: '6px', fontSize: '12px',
              fontFamily: 'JetBrains Mono, monospace', background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.12)', color: 'var(--text-heading)', cursor: 'pointer'
            }}
          >
            {copied ? <Check size={14} style={{ color: '#34d399' }} /> : <Copy size={14} />}
            {copied ? 'Copied!' : 'Copy Code'}
          </button>

          <button
            onClick={handleDownloadFile}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '6px 12px', borderRadius: '6px', fontSize: '12px',
              fontFamily: 'JetBrains Mono, monospace', background: 'rgba(52,211,153,0.15)',
              border: '1px solid rgba(52,211,153,0.3)', color: '#34d399', cursor: 'pointer'
            }}
          >
            <Download size={14} />
            Download Patched File
          </button>

          {zipFile && onDownloadPatchedZip && (
            <button
              onClick={onDownloadPatchedZip}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '6px 14px', borderRadius: '6px', fontSize: '12px',
                fontFamily: 'JetBrains Mono, monospace', background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                border: 'none', color: '#ffffff', cursor: 'pointer', fontWeight: 600
              }}
            >
              <FileCode size={14} />
              Download Patched ZIP
            </button>
          )}
        </div>
      </div>

      {/* Summary of Fixes Applied */}
      {summaryOfChanges && summaryOfChanges.length > 0 && (
        <div style={{
          background: 'rgba(52,211,153,0.06)', border: '1px solid rgba(52,211,153,0.2)',
          borderRadius: '8px', padding: '12px 16px', marginBottom: '16px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#34d399', fontFamily: 'JetBrains Mono, monospace', marginBottom: '6px', letterSpacing: '0.05em' }}>
            APPLIED REMEDIATIONS & AST PRESERVATIONS:
          </div>
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: 'var(--text-body)', lineHeight: 1.6 }}>
            {summaryOfChanges.map((change, i) => (
              <li key={i}>{change}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Unified GitHub Code Diff Display */}
      <div style={{
        fontFamily: 'JetBrains Mono, monospace', fontSize: '12px',
        background: '#090a0f', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)',
        padding: '14px', overflowX: 'auto', maxHeight: '400px', lineHeight: 1.6
      }}>
        {diffLines && diffLines.length > 0 ? (
          diffLines.map((line, idx) => {
            let lineBg = 'transparent';
            let lineColor = '#a1a1aa';
            let prefix = ' ';

            if (line.startsWith('+') && !line.startsWith('+++')) {
              lineBg = 'rgba(52,211,153,0.12)';
              lineColor = '#34d399';
              prefix = '+';
            } else if (line.startsWith('-') && !line.startsWith('---')) {
              lineBg = 'rgba(239,68,68,0.12)';
              lineColor = '#f87171';
              prefix = '-';
            } else if (line.startsWith('@@')) {
              lineColor = '#818cf8';
            }

            return (
              <div key={idx} style={{ background: lineBg, color: lineColor, padding: '1px 8px', borderRadius: '3px', whiteSpace: 'pre' }}>
                {line}
              </div>
            );
          })
        ) : (
          <pre style={{ margin: 0, color: '#34d399' }}>{patchedCode}</pre>
        )}
      </div>
    </div>
  );
}
