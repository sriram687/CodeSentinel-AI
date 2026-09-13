import React from 'react';

export default function DocumentationView() {
  return (
    <div className="glass-card" style={{ maxWidth: '900px' }}>
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
  );
}
