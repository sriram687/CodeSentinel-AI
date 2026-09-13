import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Code2, 
  Cpu, 
  BookOpen, 
  Play, 
  Zap, 
  FileCode, 
  CheckCircle2, 
  AlertTriangle,
  Layers,
  Terminal,
  Server
} from 'lucide-react';

const CODE_TEMPLATES = {
  buffer_overflow: {
    name: "Buffer Overflow (Unbounded Copy)",
    code: `void process_user_input(char *user_data) {
    char dest_buffer[32];
    // Unbounded string copy vulnerability
    strcpy(dest_buffer, user_data);
    printf("User Data: %s\\n", dest_buffer);
}`
  },
  null_pointer: {
    name: "Null Pointer Dereference",
    code: `void execute_command(char *cmd_ptr) {
    // Dereferencing without checking if null
    if (*cmd_ptr == 'A') {
        printf("Command A executed\\n");
    }
}`
  },
  use_after_free: {
    name: "Use-After-Free Memory Bug",
    code: `void memory_cleanup(char *resource) {
    free(resource);
    // Accessing resource after free
    printf("Resource tag: %c\\n", resource[0]);
}`
  },
  safe_code: {
    name: "Safe Bounded Copy (Non-Vulnerable)",
    code: `void safe_user_handler(const char *input_str) {
    char safe_buf[64];
    // Safe strncpy with boundary check
    strncpy(safe_buf, input_str, sizeof(safe_buf) - 1);
    safe_buf[sizeof(safe_buf) - 1] = '\\0';
}`
  }
};

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

export default function App() {
  const [activeTab, setActiveTab] = useState('studio'); // studio | models | docs
  const [selectedTemplate, setSelectedTemplate] = useState('buffer_overflow');
  const [code, setCode] = useState(CODE_TEMPLATES.buffer_overflow.code);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [apiStatus, setApiStatus] = useState('connecting'); // online | offline | connecting

  // Check API status
  useEffect(() => {
    fetch('http://localhost:5000/api/health')
      .then(res => res.json())
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

  const handleTemplateChange = (e) => {
    const key = e.target.value;
    setSelectedTemplate(key);
    setCode(CODE_TEMPLATES[key].code);
    setScanResult(null);
  };

  const runVulnerabilityScan = async () => {
    if (!code.trim()) return;
    setIsScanning(true);

    try {
      const response = await fetch('http://localhost:5000/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      if (response.ok) {
        const data = await response.json();
        setScanResult(data);
      } else {
        alert("Error performing scan. Ensure api_server.py is running on port 5000.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to connect to backend server. Make sure http://localhost:5000 is active.");
    } finally {
      setIsScanning(false);
    }
  };

  const lineCount = code.split('\n').length;
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  return (
    <div class="app-container">
      {/* Fumadocs Sidebar */}
      <aside class="sidebar">
        <div class="brand-header">
          <div class="brand-icon">
            <ShieldAlert size={22} color="#ffffff" />
          </div>
          <div>
            <div class="brand-name">CodeSentinel AI <span class="brand-badge">v1.0</span></div>
          </div>
        </div>

        <div class="nav-section-title">Core Platform</div>
        <div 
          class={`nav-item ${activeTab === 'studio' ? 'active' : ''}`}
          onClick={() => setActiveTab('studio')}
        >
          <Code2 size={18} />
          <span>Vulnerability Studio</span>
        </div>

        <div 
          class={`nav-item ${activeTab === 'models' ? 'active' : ''}`}
          onClick={() => setActiveTab('models')}
        >
          <Cpu size={18} />
          <span>10 Models Explorer</span>
        </div>

        <div class="nav-section-title">Documentation</div>
        <div 
          class={`nav-item ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          <BookOpen size={18} />
          <span>Fumadocs Docs & API</span>
        </div>

        <div class="server-status">
          <div class={`status-dot ${apiStatus === 'offline' ? 'offline' : ''}`} />
          <span>
            {apiStatus === 'online' && 'Backend API: Online (Port 5000)'}
            {apiStatus === 'offline' && 'Backend API: Offline'}
            {apiStatus === 'connecting' && 'Connecting to API...'}
          </span>
        </div>
      </aside>

      {/* Main Workspace Wrapper */}
      <div class="main-wrapper">
        {/* Fumadocs Top Header */}
        <header class="top-header">
          <div class="header-title">
            {activeTab === 'studio' && 'Vulnerability Detection Studio'}
            {activeTab === 'models' && 'Model Architecture Catalog (10 Fine-tuned Models)'}
            {activeTab === 'docs' && 'Fumadocs Framework Documentation'}
          </div>

          <div class="template-selector">
            <span style={{ fontSize: '0.82rem', color: '#94a3b8' }}>Preset Template:</span>
            <select class="select-dropdown" value={selectedTemplate} onChange={handleTemplateChange}>
              {Object.keys(CODE_TEMPLATES).map(key => (
                <option key={key} value={key}>{CODE_TEMPLATES[key].name}</option>
              ))}
            </select>
          </div>
        </header>

        {/* Workspace Content View */}
        <main class="workspace-content">
          {activeTab === 'studio' && (
            <div class="studio-grid">
              {/* Left Column: Code Editor Workspace */}
              <div class="glass-card">
                <div class="card-title">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileCode size={18} color="#8b5cf6" />
                    C/C++ Source Code Editor
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Language: C/C++</span>
                </div>

                <div class="editor-container">
                  <div class="editor-header">
                    <span>tmp.c</span>
                    <span>{lineCount} Lines | UTF-8</span>
                  </div>
                  <div class="editor-body">
                    <div class="line-numbers">
                      {lineNumbers.map(n => <div key={n}>{n}</div>)}
                    </div>
                    <textarea 
                      class="code-textarea"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      rows={14}
                      placeholder="// Type or paste C/C++ function code here..."
                    />
                  </div>
                </div>

                <button 
                  class="scan-btn" 
                  onClick={runVulnerabilityScan}
                  disabled={isScanning}
                >
                  {isScanning ? (
                    <>
                      <Zap size={18} class="animate-spin" />
                      Running Multi-Model Max-Risk Audit...
                    </>
                  ) : (
                    <>
                      <Play size={18} />
                      Run Security Audit Scan
                    </>
                  )}
                </button>
              </div>

              {/* Right Column: Scan Results & Multi-Model Breakdown */}
              <div class="glass-card">
                <div class="card-title">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Layers size={18} color="#6366f1" />
                    Security Audit Results & Max-Risk Analysis
                  </span>
                </div>

                {scanResult ? (
                  <div>
                    {/* Verdict Banner */}
                    <div class={`verdict-banner ${scanResult.status === 'VULNERABLE' ? 'vulnerable' : 'safe'}`}>
                      <div>
                        <div class="verdict-text">
                          {scanResult.status === 'VULNERABLE' ? '⚠️ VULNERABLE CODE DETECTED' : '✅ CODE APPEARS SAFE'}
                        </div>
                        <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '2px' }}>
                          Highest Flagging Model: <strong>{scanResult.top_model}</strong>
                        </div>
                      </div>
                      <div class="score-chip">
                        {scanResult.max_risk_score}% Max Risk
                      </div>
                    </div>

                    {/* Line-Level Heatmap */}
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', marginBottom: '8px', color: '#cbd5e1' }}>
                      Line-Level Attention Heatmap (Encoder Focus):
                    </div>
                    <div class="code-heatmap">
                      {scanResult.line_highlights.map(item => (
                        <div 
                          key={item.line_num} 
                          class={`heatmap-line ${item.is_vulnerable_line ? 'vulnerable-line' : ''}`}
                        >
                          <div class="line-no">{item.line_num}</div>
                          <div class="line-code">{item.code}</div>
                          <div class="line-risk-badge">
                            {item.risk_score}% Risk
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Multi-Model Breakdown Table */}
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', marginBottom: '8px', color: '#cbd5e1' }}>
                      Multi-Model Domain Breakdown ({scanResult.total_models_scanned} Models Scanned):
                    </div>
                    <table class="models-table">
                      <thead>
                        <tr>
                          <th>Model Name</th>
                          <th>Target Domain</th>
                          <th>Risk Conf</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {scanResult.model_results.map(m => (
                          <tr key={m.model_name}>
                            <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '600' }}>{m.model_name}</td>
                            <td style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{m.domain}</td>
                            <td style={{ fontWeight: '700' }}>{m.risk_score}%</td>
                            <td>
                              <span style={{
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontSize: '0.72rem',
                                fontWeight: '700',
                                backgroundColor: m.status === 'VULNERABLE' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                                color: m.status === 'VULNERABLE' ? '#f43f5e' : '#10b981'
                              }}>
                                {m.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
                    <Terminal size={48} style={{ opacity: 0.3, marginBottom: '12px' }} />
                    <div>Click <strong>"Run Security Audit Scan"</strong> to analyze the code across all models.</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Model Catalog Explorer View */}
          {activeTab === 'models' && (
            <div>
              <div class="models-grid">
                {MODEL_CATALOG.map(m => (
                  <div key={m.name} class="model-card">
                    <div class="model-header">
                      <div style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', fontSize: '0.95rem' }}>{m.name}</div>
                      <span class="arch-badge">{m.arch}</span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#818cf8', marginBottom: '8px', fontWeight: '600' }}>
                      Size: {m.size}
                    </div>
                    <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginBottom: '6px', fontWeight: '500' }}>
                      {m.domain}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
                      {m.desc}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fumadocs Documentation Tab */}
          {activeTab === 'docs' && (
            <div class="glass-card" style={{ maxWidth: '900px' }}>
              <h1 style={{ fontSize: '1.6rem', marginBottom: '10px' }}>CodeSentinel-AI Fumadocs Framework</h1>
              <p style={{ color: '#94a3b8', marginBottom: '20px' }}>
                Developer guide and REST API specification for integrating CodeSentinel deep learning vulnerability scanner into your CI/CD pipeline.
              </p>

              <h2 style={{ fontSize: '1.1rem', marginTop: '20px', marginBottom: '10px', color: '#a5b4fc' }}>1. Local API Endpoint</h2>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '10px' }}>
                Send POST requests to <code>http://localhost:5000/api/scan</code> with your target C/C++ code.
              </p>

              <div style={{ background: '#0b0d14', padding: '16px', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
                curl -X POST http://localhost:5000/api/scan \<br/>
                &nbsp;&nbsp;-H "Content-Type: application/json" \<br/>
                &nbsp;&nbsp;-d '{'{"code": "void test(char *input) { char buf[32]; strcpy(buf, input); }"}'}'
              </div>

              <h2 style={{ fontSize: '1.1rem', marginTop: '20px', marginBottom: '10px', color: '#a5b4fc' }}>2. Python Integration</h2>
              <div style={{ background: '#0b0d14', padding: '16px', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', border: '1px solid var(--border-color)' }}>
                import requests<br/>
                response = requests.post("http://localhost:5000/api/scan", json=&#123;"code": code_str&#125;)<br/>
                data = response.json()<br/>
                print(f"Max Risk: &#123;data['max_risk_score']&#125;% | Status: &#123;data['status']&#125;")
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
