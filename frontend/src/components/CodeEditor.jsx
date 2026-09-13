import React from 'react';
import { FileCode, Play, Zap } from 'lucide-react';

export default function CodeEditor({ code, setCode, isScanning, onScan }) {
  const lineCount = code.split('\n').length;
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  return (
    <div className="glass-card">
      <div className="card-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileCode size={18} color="#8b5cf6" />
          C/C++ Source Code Editor
        </span>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Language: C/C++</span>
      </div>
      <div className="editor-container">
        <div className="editor-header">
          <span>tmp.c</span>
          <span>{lineCount} Lines | UTF-8</span>
        </div>
        <div className="editor-body">
          <div className="line-numbers">
            {lineNumbers.map(n => <div key={n}>{n}</div>)}
          </div>
          <textarea
            className="code-textarea"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={14}
            placeholder="// Type or paste C/C++ function code here..."
          />
        </div>
      </div>
      <button className="scan-btn" onClick={onScan} disabled={isScanning}>
        {isScanning ? (
          <><Zap size={18} className="animate-spin" /> Running Multi-Model Max-Risk Audit...</>
        ) : (
          <><Play size={18} /> Run Security Audit Scan</>
        )}
      </button>
    </div>
  );
}
