import React from 'react';

const MODEL_CATALOG = [
  { name: "VB-MLP_draper", arch: "MLP (Dense)", size: "499.4 MB", domain: "General C/C++ GitHub Benchmark", desc: "Trained on 1.2M+ functions across major CWE categories." },
  { name: "VB-MLP_devign", arch: "MLP (Dense)", size: "499.4 MB", domain: "OS Kernel & Production (Linux/QEMU)", desc: "Best for real-world Linux Kernel and QEMU security bugs." },
  { name: "VB-MLP_mvd", arch: "MLP (Dense)", size: "499.5 MB", domain: "Multi-Class Vulnerability (MVD)", desc: "Categorizes 40 distinct CWE vulnerability classes." },
  { name: "VB-MLP_reveal", arch: "MLP (Dense)", size: "499.4 MB", domain: "Imbalanced Chromium/Debian Code", desc: "Evaluated on rare vulnerability distribution in browser code." },
  { name: "VB-MLP_vuldeepecker", arch: "MLP (Dense)", size: "499.4 MB", domain: "API Misuse & Buffer Violations", desc: "Specialized in library parameter boundary checking." },
  { name: "VB-MLP_d2a", arch: "MLP (Dense)", size: "499.4 MB", domain: "IBM Static Analysis False Positives", desc: "Trained to filter out false alerts from static code scanners." },
  { name: "VB-CNN_mvd", arch: "1D-CNN", size: "178.0 MB", domain: "Multi-Class Convolutional Scanner", desc: "Fast 1D-CNN window feature extractor for 40 CWE classes." },
  { name: "VB-CNN_devign", arch: "1D-CNN", size: "178.0 MB", domain: "Linux Kernel Convolutional Scanner", desc: "Fast 1D-CNN filter scan for production OS kernel code." },
  { name: "VB-CNN_reveal", arch: "1D-CNN", size: "178.0 MB", domain: "Chromium Convolutional Scanner", desc: "Fast 1D-CNN scanner for sparse browser vulnerabilities." },
  { name: "VB-CNN_vuldeepecker", arch: "1D-CNN", size: "178.0 MB", domain: "Buffer Error 1D-CNN Scanner", desc: "Fast convolutional window scan for C API violations." }
];

export default function ModelCatalog() {
  return (
    <div className="models-grid">
      {MODEL_CATALOG.map(m => (
        <div key={m.name} className="model-card">
          <div className="model-header">
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', fontSize: '0.95rem' }}>{m.name}</div>
            <span className="arch-badge">{m.arch}</span>
          </div>
          <div style={{ fontSize: '0.78rem', color: '#818cf8', marginBottom: '8px', fontWeight: '600' }}>Size: {m.size}</div>
          <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginBottom: '6px', fontWeight: '500' }}>{m.domain}</div>
          <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{m.desc}</div>
        </div>
      ))}
    </div>
  );
}
