import React, { useRef, useState } from 'react';
import { Upload, CheckCircle, ChevronDown, Loader2, ArrowRight } from 'lucide-react';

const SAMPLE_SNIPPETS = {
  code: `def process_payment(amount, card_number):
    query = "INSERT INTO payments VALUES ('" + card_number + "', '" + str(amount) + "')"
    db.execute(query)
    return True`,
  specs: `Section 3.2: Data Flow Specification
The system shall process user data through unencrypted messaging queues across distributed internal microservices. All payload transactions must complete within 200ms latency targets.`,
  api: `POST /api/v1/payments HTTP/1.1
Host: api.enterprise.com
Authorization: Bearer bearer_token_xyz
Content-Type: application/json

{ "amount": 100, "card_number": "4111111111111111" }`,
  logs: `[2026-08-07 14:02:11] [SECURITY_ALERT] Failed password attempt for user 'admin' from IP 192.168.1.105 (Attempt 5/5)
[2026-08-07 14:02:15] [WARNING] SQL injection payload pattern detected in query parameters from IP 192.168.1.105`,
};

const CHIP_LABELS = [
  { key: 'code',  label: 'Python Code' },
  { key: 'specs', label: 'Tech Spec' },
  { key: 'api',   label: 'API Contract' },
  { key: 'logs',  label: 'Security Log' },
];

export default function InputSection({
  content, setContent,
  analysisType, setAnalysisType,
  onAnalyze, isAnalyzing,
}) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const processFile = (file) => {
    setSelectedFile({ name: file.name, size: (file.size / 1024).toFixed(1) + ' KB', isZip: file.name.endsWith('.zip'), rawFile: file });
    if (file.name.endsWith('.zip')) {
      setContent(`[REPOSITORY ZIP ARCHIVE: ${file.name}]\nExtracted project zip archive ready for multi-file 4-LLM inspection.`);
      if (window.__setZipFile) window.__setZipFile(file);
    } else {
      if (window.__setZipFile) window.__setZipFile(null);
      const reader = new FileReader();
      reader.onload = (e) => setContent(e.target.result);
      reader.readAsText(file);
    }
  };

  const loadSample = (key) => {
    setContent(SAMPLE_SNIPPETS[key]);
    setAnalysisType(key);
  };

  return (
    <div style={{ marginBottom: '24px', width: '100%' }}>

      {/* Card wrapper */}
      <div className="card" style={{ padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <div className="label" style={{ marginBottom: '4px' }}>CONTENT INPUT</div>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Upload a file or paste content to begin analysis</div>
          </div>

          {/* Sample chips */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-faint)', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.06em' }}>
              TRY A SAMPLE →
            </div>
            <div className="sample-chips">
              {CHIP_LABELS.map(c => (
                <button key={c.key} className="sample-chip" onClick={() => loadSample(c.key)}>
                  {c.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="input-grid">
          {/* Dropzone */}
          <div>
            <div
              className={`upload-dropzone${isDragOver ? ' active' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragOver(false);
                const f = e.dataTransfer.files[0];
                if (f) processFile(f);
              }}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".zip,.py,.js,.java,.txt,.md,.json,.log,.ts,.jsx,.tsx"
                onChange={(e) => { if (e.target.files[0]) processFile(e.target.files[0]); }}
              />

              {selectedFile ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                  <CheckCircle size={30} style={{ color: 'var(--risk-low)' }} />
                  <div style={{ fontSize: '13px', color: 'var(--text-heading)', fontWeight: 500, textAlign: 'center', wordBreak: 'break-all' }}>
                    {selectedFile.name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                    {selectedFile.size}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Click to replace</div>
                </div>
              ) : (
                <>
                  <Upload
                    size={26}
                    style={{ color: isDragOver ? 'var(--text-heading)' : 'var(--text-muted)', marginBottom: '12px' }}
                  />
                  <div style={{ fontSize: '13px', color: 'var(--text-body)', fontWeight: 500, marginBottom: '6px' }}>
                    Drop a file here
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', lineHeight: 1.6 }}>
                    <span style={{ color: '#818cf8', fontWeight: 600 }}>.zip (Project Archives)</span><br />
                    .py .js .ts .java .sql .json .log
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Right column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Textarea */}
            <div style={{ position: 'relative', flex: 1 }}>
              <textarea
                className="custom-textarea"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste code, technical specs, API contracts, or security logs here..."
                style={{ width: '100%' }}
              />
              {/* char count */}
              {content.length > 0 && (
                <div style={{
                  position: 'absolute', bottom: '10px', right: '12px',
                  fontSize: '10px', color: 'var(--text-faint)',
                  fontFamily: 'JetBrains Mono, monospace', pointerEvents: 'none',
                }}>
                  {content.length.toLocaleString()} chars
                </div>
              )}
            </div>

            {/* Controls row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '12px', alignItems: 'end' }}>
              <div>
                <div className="label" style={{ marginBottom: '6px' }}>ANALYSIS TYPE</div>
                <div style={{ position: 'relative' }}>
                  <select
                    className="custom-select"
                    value={analysisType}
                    onChange={(e) => setAnalysisType(e.target.value)}
                  >
                    <option value="auto">Auto-Detect (Recommended)</option>
                    <option value="code">Code Review</option>
                    <option value="specs">Technical Specs</option>
                    <option value="api">API Documentation</option>
                    <option value="logs">Security Logs</option>
                  </select>
                  <ChevronDown
                    size={15}
                    style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }}
                  />
                </div>
              </div>

              <button
                className="btn-analyze"
                onClick={onAnalyze}
                disabled={isAnalyzing || !content.trim()}
                style={{ width: '140px', height: '44px', flexShrink: 0 }}
              >
                {isAnalyzing ? (
                  <><Loader2 size={15} className="spin-icon" /> Running...</>
                ) : (
                  <><ArrowRight size={15} /> Analyze</>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '8px', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.04em' }}>
        4 AI MODELS — 3 domain inspectors + 1 Chief Judge synthesizer — will review each extracted item independently.
      </div>
    </div>
  );
}
