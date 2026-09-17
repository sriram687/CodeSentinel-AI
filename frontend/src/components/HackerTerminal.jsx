import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Shield, AlertTriangle, CheckCircle, Code, Cpu, Globe, Activity } from 'lucide-react';
import Editor from '@monaco-editor/react';
import './HackerTerminal.css';

const HackerTerminal = () => {
  const [code, setCode] = useState('// Paste C/C++ code here...\n');
  const [logs, setLogs] = useState([
    { type: 'system', text: 'CodeSentinel-AI Terminal Initialized.' },
    { type: 'system', text: 'Awaiting connection to DGX Remote Server...' },
    { type: 'success', text: 'Connection Established: aicentre.sece.ac.in:5050' }
  ]);
  const [isScanning, setIsScanning] = useState(false);
  const logsEndRef = useRef(null);

  // Auto-scroll to bottom of logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (type, text) => {
    setLogs(prev => [...prev, { type, text }]);
  };

  const handleScan = async () => {
    if (!code.trim() || code.trim() === '// Paste C/C++ code here...') {
      addLog('error', 'Error: No valid code provided to scan.');
      return;
    }

    addLog('action', '> Initiating scan sequence...');
    setIsScanning(true);

    try {
      const response = await fetch('http://localhost:5050/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      if (!response.ok) throw new Error('Failed to connect to AI engine.');
      
      const result = await response.json();
      
      addLog('system', `VulBERTa Scan Complete: Risk Score ${result.vuln_score}%`);
      
      if (result.vulnerable) {
        addLog('error', '⚠️ VULNERABILITY DETECTED. Handing over to Qwen Decoder...');
        
        if (result.patch) {
          addLog('success', '✅ Patch Generated Successfully:');
          addLog('code', result.patch);
        } else {
          addLog('error', 'Failed to generate patch.');
        }
      } else {
        addLog('success', '✅ Code is SAFE. No action required.');
      }
      
    } catch (err) {
      addLog('error', `Connection Error: ${err.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const [editorTheme, setEditorTheme] = useState('codesentinel-dark');

  const handleEditorWillMount = (monaco) => {
    monaco.editor.defineTheme('codesentinel-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'ff7b72', fontStyle: 'bold' },
        { token: 'string', foreground: 'a5d6ff' },
        { token: 'number', foreground: '79c0ff' },
        { token: 'type', foreground: 'ffa657' },
        { token: 'function', foreground: 'd2a8ff' },
      ],
      colors: {
        'editor.background': '#121214',
        'editor.foreground': '#e6edf3',
        'editor.lineHighlightBackground': '#1b1f24',
        'editorCursor.foreground': '#00ff80',
        'editorLineNumber.foreground': '#ffffff',
        'editorLineNumber.activeForeground': '#00ff80',
        'editorGutter.background': '#2b2b2e',
      }
    });

    monaco.editor.defineTheme('codesentinel-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6e7681', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'cf222e', fontStyle: 'bold' },
        { token: 'string', foreground: '0a3069' },
        { token: 'number', foreground: '0550ae' },
        { token: 'type', foreground: '953800' },
        { token: 'function', foreground: '8250df' },
      ],
      colors: {
        'editor.background': '#ffffff',
        'editor.foreground': '#24292f',
        'editor.lineHighlightBackground': '#f6f8fa',
        'editorCursor.foreground': '#0969da',
        'editorLineNumber.foreground': '#ffffff',
        'editorLineNumber.activeForeground': '#ffffff',
        'editorGutter.background': '#2b2b2e',
      }
    });
  };

  return (
    <div className="hacker-terminal-container">
      <div className="terminal-header">
        <div className="header-left">
          <div className="window-dots">
            <span className="dot dot-close"></span>
            <span className="dot dot-minimize"></span>
            <span className="dot dot-expand"></span>
          </div>
          <div className="brand-logo">
            <span className="brand-prompt">&gt;_</span>
            <span className="brand-name">codesentinel<span className="brand-ai">-ai</span></span>
          </div>
        </div>

        <div className="header-center">
          <div className="engine-status">
            <span>AI CORE: <strong>VulBERTa + Qwen2.5</strong></span>
          </div>
        </div>

        <div className="header-right">
          <div className="server-badge online">
            <span className="pulse-dot"></span>
            <span>DGX-01 REMOTE [PORT 5050]</span>
          </div>
        </div>
      </div>
      
      <div className="terminal-body">
        <div className="logs-container">
          {logs.map((log, i) => (
            <div key={i} className={`log-line log-${log.type}`}>
              {log.type === 'action' && <span className="prompt-arrow">❯</span>}
              {log.type === 'error' && <AlertTriangle size={14} className="log-icon" />}
              {log.type === 'success' && <CheckCircle size={14} className="log-icon" />}
              {log.type === 'code' ? (
                <pre className="code-patch">{log.text}</pre>
              ) : (
                <span>{log.text}</span>
              )}
            </div>
          ))}
          {isScanning && <div className="log-line log-system blink">Scanning...</div>}
          <div ref={logsEndRef} />
        </div>

        <div className="input-container">
          <div className="input-header">
            <div className="input-header-left">
              <Code size={16} />
              <span>Target Source Code (C/C++)</span>
            </div>
            <select 
              className="theme-select" 
              value={editorTheme} 
              onChange={(e) => setEditorTheme(e.target.value)}
            >
              <option value="codesentinel-dark">Obsidian Cyber</option>
              <option value="hc-black">Pitch Black (HC)</option>
              <option value="vs-dark">VS Code Dark</option>
              <option value="codesentinel-light">Claude Light</option>
            </select>
          </div>
          
          <div className="editor-wrapper">
            <Editor
              height="100%"
              defaultLanguage="cpp"
              theme={editorTheme}
              beforeMount={handleEditorWillMount}
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "'Fira Code', 'Courier New', monospace",
                lineNumbersMinChars: 3,
                scrollBeyondLastLine: false,
                wordWrap: 'on'
              }}
            />
          </div>

          <button 
            className={`scan-button ${isScanning ? 'scanning' : ''}`}
            onClick={handleScan}
            disabled={isScanning}
          >
            <Shield size={16} />
            {isScanning ? 'ANALYZING...' : 'INITIALIZE SCAN'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default HackerTerminal;
