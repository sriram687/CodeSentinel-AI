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
  Terminal,
  Sun,
  Moon,
  Trash2,
  Copy,
  Check
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
  const [theme, setTheme] = useState('dark'); // 'dark' | 'light'
  const [activeTab, setActiveTab] = useState('studio'); // studio | models | docs
  const [selectedTemplate, setSelectedTemplate] = useState('buffer_overflow');
  const [code, setCode] = useState(CODE_TEMPLATES.buffer_overflow.code);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [apiStatus, setApiStatus] = useState('connecting');
  const [copiedReport, setCopiedReport] = useState(false);

  useEffect(() => {
    document.documentElement.className = theme === 'dark' ? 'dark' : '';
  }, [theme]);

  useEffect(() => {
    fetch('http://localhost:5000/api/health')
      .then(res => res.json())
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleTemplateChange = (e) => {
    const key = e.target.value;
    setSelectedTemplate(key);
    setCode(CODE_TEMPLATES[key].code);
    setScanResult(null);
  };

  const handleClearCode = () => {
    setCode('');
    setScanResult(null);
  };

  const copyAuditReport = () => {
    if (!scanResult) return;
    const reportText = `[CodeSentinel Audit Report]
Status: ${scanResult.status}
Max Risk: ${scanResult.max_risk_score}%
Top Model: ${scanResult.top_model}
Total Models Scanned: ${scanResult.total_models_scanned}

Model Breakdown:
${scanResult.model_results.map(m => `- ${m.model_name} (${m.domain}): ${m.risk_score}% [${m.status}]`).join('\n')}`;

    navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
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
    <div className="app-container">
      {/* Fumadocs Sidebar */}
      <aside className="sidebar">
        <div className="brand-header">
          <div className="brand-title">
            CodeSentinel <span className="brand-badge">v1.0</span>
          </div>
        </div>

        <div className="nav-section-title">Core Studio</div>
        <div 
          className={`nav-item ${activeTab === 'studio' ? 'active' : ''}`}
          onClick={() => setActiveTab('studio')}
        >
          <Code2 size={17} />
          <span>Vulnerability Studio</span>
        </div>

        <div 
          className={`nav-item ${activeTab === 'models' ? 'active' : ''}`}
          onClick={() => setActiveTab('models')}
        >
          <Cpu size={17} />
          <span>10 Models Catalog</span>
        </div>

        <div className="nav-section-title">Documentation</div>
        <div 
          className={`nav-item ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          <BookOpen size={17} />
          <span>API Guide</span>
        </div>

        <button className="theme-toggle-btn" onClick={toggleTheme}>
          <span>Theme: {theme === 'dark' ? 'Midnight Editor' : 'Alabaster Print'}</span>
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
        </button>

        <div className="server-status">
          <div className={`status-dot ${apiStatus === 'offline' ? 'offline' : ''}`} />
          <span>
            {apiStatus === 'online' && 'API: Online (Port 5000)'}
            {apiStatus === 'offline' && 'API: Offline'}
            {apiStatus === 'connecting' && 'Connecting API...'}
          </span>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-title">
            {activeTab === 'studio' && 'Vulnerability Detection Studio'}
            {activeTab === 'models' && 'Model Architecture Catalog (10 Fine-tuned Models)'}
            {activeTab === 'docs' && 'API Documentation Guide'}
          </div>

          <div className="template-selector">
            <span style={{ fontSize: '0.82rem', color: 'var(--muted-fg)' }}>Preset Template:</span>
            <select className="select-dropdown" value={selectedTemplate} onChange={handleTemplateChange}>
              {Object.keys(CODE_TEMPLATES).map(key => (
                <option key={key} value={key}>{CODE_TEMPLATES[key].name}</option>
              ))}
            </select>
          </div>
        </header>

        {/* Workspace Views */}
        <main className="workspace-content animate-fade-in-up">
          {activeTab === 'studio' && (
            <div className="studio-grid">
              {/* Left Column: Code Editor */}
              <div className="editorial-card">
                <div className="card-title">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileCode size={18} />
                    C/C++ Source Code Editor
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--muted-fg)', fontFamily: 'var(--font-mono)' }}>Language: C/C++</span>
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

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    className="primary-btn" 
                    onClick={runVulnerabilityScan}
                    disabled={isScanning}
                    style={{ flex: 1 }}
                  >
                    {isScanning ? (
                      <>
                        <Zap size={18} className="animate-spin" />
                        Running Multi-Model Audit...
                      </>
                    ) : (
                      <>
                        <Play size={18} />
                        Run Security Audit Scan
                      </>
                    )}
                  </button>
                  <button 
                    className="theme-toggle-btn"
                    onClick={handleClearCode}
                    title="Clear editor text"
                    style={{ marginTop: 0, padding: '0 14px' }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* Right Column: Scan Results */}
              <div className="editorial-card">
                <div className="card-title">
                  <span>Security Audit & Max-Risk Analysis</span>
                  {scanResult && (
                    <button 
                      onClick={copyAuditReport} 
                      className="theme-toggle-btn" 
                      style={{ marginTop: 0, padding: '4px 8px', fontSize: '0.75rem' }}
                    >
                      {copiedReport ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                      <span>{copiedReport ? 'Copied' : 'Copy Report'}</span>
                    </button>
                  )}
                </div>

                {scanResult ? (
                  <div>
                    {/* Verdict Banner */}
                    <div className={`verdict-banner ${scanResult.status === 'VULNERABLE' ? 'vulnerable' : 'safe'}`}>
                      <div>
                        <div className="verdict-text">
                          {scanResult.status === 'VULNERABLE' ? '⚠️ VULNERABLE CODE DETECTED' : '✅ CODE APPEARS SAFE'}
                        </div>
                        <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '2px' }}>
                          Highest Flagging Model: <strong>{scanResult.top_model}</strong>
                        </div>
                      </div>
                      <div className="score-chip">
                        {scanResult.max_risk_score}% Max Risk
                      </div>
                    </div>

                    {/* Line Heatmap */}
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', marginBottom: '8px', color: 'var(--fg-color)' }}>
                      Line-Level Attention Heatmap (Encoder Focus):
                    </div>
                    <div className="code-heatmap">
                      {scanResult.line_highlights.map(item => (
                        <div 
                          key={item.line_num} 
                          className={`heatmap-line ${item.is_vulnerable_line ? 'vulnerable-line' : ''}`}
                        >
                          <div className="line-no">{item.line_num}</div>
                          <div className="line-code">{item.code}</div>
                          <div className="line-risk-badge">
                            {item.risk_score}% Risk
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Multi-Model Table */}
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', marginBottom: '8px', color: 'var(--fg-color)' }}>
                      Multi-Model Domain Breakdown ({scanResult.total_models_scanned} Models Scanned):
                    </div>
                    <table className="models-table">
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
                            <td style={{ fontSize: '0.8rem', color: 'var(--muted-fg)' }}>{m.domain}</td>
                            <td style={{ fontWeight: '700' }}>{m.risk_score}%</td>
                            <td>
                              <span style={{
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontSize: '0.72rem',
                                fontWeight: '700',
                                backgroundColor: m.status === 'VULNERABLE' ? 'var(--danger-bg)' : 'var(--safe-bg)',
                                color: m.status === 'VULNERABLE' ? 'var(--danger-color)' : 'var(--safe-color)'
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
                  <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--muted-fg)' }}>
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
              <div className="models-grid">
                {MODEL_CATALOG.map(m => (
                  <div key={m.name} className="model-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', fontSize: '0.95rem' }}>{m.name}</div>
                      <span className="arch-badge">{m.arch}</span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--muted-fg)', marginBottom: '8px', fontWeight: '600' }}>
                      Size: {m.size}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--fg-color)', marginBottom: '6px', fontWeight: '600' }}>
                      {m.domain}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--muted-fg)' }}>
                      {m.desc}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fumadocs Documentation Tab */}
          {activeTab === 'docs' && (
            <div className="editorial-card" style={{ maxWidth: '800px', marginInline: 'auto' }}>
              <h1 style={{ fontSize: '1.8rem', marginBottom: '12px' }}>CodeSentinel AI Documentation</h1>
              <p style={{ color: 'var(--muted-fg)', marginBottom: '24px' }}>
                Developer guide and REST API specification for integrating CodeSentinel deep learning vulnerability scanner into your CI/CD pipeline.
              </p>

              <h2 style={{ fontSize: '1.2rem', marginTop: '24px', marginBottom: '10px' }}>1. Local API Endpoint</h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--fg-color)', marginBottom: '12px' }}>
                Send POST requests to <code>http://localhost:5000/api/scan</code> with your target C/C++ code.
              </p>

              <div style={{ background: 'var(--secondary-bg)', padding: '16px', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', border: '1px solid var(--border-color)', marginBottom: '24px' }}>
                curl -X POST http://localhost:5000/api/scan \<br/>
                &nbsp;&nbsp;-H "Content-Type: application/json" \<br/>
                &nbsp;&nbsp;-d '{'{"code": "void test(char *input) { char buf[32]; strcpy(buf, input); }"}'}'
              </div>

              <h2 style={{ fontSize: '1.2rem', marginTop: '24px', marginBottom: '10px' }}>2. Python Integration</h2>
              <div style={{ background: 'var(--secondary-bg)', padding: '16px', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', border: '1px solid var(--border-color)' }}>
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
