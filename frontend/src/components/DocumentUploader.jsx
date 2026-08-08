import React, { useRef } from 'react';
import { UploadCloud, Layers } from 'lucide-react';

export default function DocumentUploader({ onDocumentParsed, clauses, selectedClause, onSelectClause }) {
  const fileInputRef = useRef(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      onDocumentParsed(null, true);
      const res = await fetch('/api/upload-document', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error('Failed to parse document');
      const data = await res.json();
      onDocumentParsed(data, false);
    } catch (err) {
      console.error('Error uploading document:', err);
      onDocumentParsed(null, false, 'Failed to parse document format.');
    }
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <div 
        className="file-dropzone" 
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept=".pdf,.docx,.doc,.txt" 
          onChange={handleFileChange}
        />
        <UploadCloud size={32} color="#C2ECE2" style={{ margin: '0 auto 8px' }} />
        <div style={{ fontSize: '0.88rem', color: '#eaf7f4', fontWeight: 500 }}>
          Drag & drop legal contract (.pdf, .docx, .txt) or click to browse
        </div>
        <div style={{ fontSize: '0.78rem', color: '#94bdb5', marginTop: '4px' }}>
          Automated multi-agent clause segmentation
        </div>
      </div>

      {clauses && clauses.length > 0 && (
        <div style={{ marginBottom: '14px' }}>
          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#C2ECE2', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={14} color="#017374" />
            Extracted Clauses ({clauses.length}):
          </div>

          <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '6px' }}>
            {clauses.map((c) => (
              <button 
                key={c.id} 
                onClick={() => onSelectClause(c)}
                style={{
                  padding: '8px 12px',
                  background: selectedClause?.id === c.id ? '#017374' : '#091718',
                  border: '1px solid var(--card-border)',
                  borderRadius: '6px',
                  color: selectedClause?.id === c.id ? '#ffffff' : '#94bdb5',
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                [{c.category}] {c.title.substring(0, 30)}...
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
