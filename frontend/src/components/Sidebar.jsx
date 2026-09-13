import React from 'react';
import { ShieldAlert, Code2, Cpu, BookOpen } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, apiStatus }) {
  return (
    <aside className="sidebar">
      <div className="brand-header">
        <div className="brand-icon">
          <ShieldAlert size={22} color="#ffffff" />
        </div>
        <div>
          <div className="brand-name">CodeSentinel AI <span className="brand-badge">v1.0</span></div>
        </div>
      </div>
      <div className="nav-section-title">Core Platform</div>
      <div className={`nav-item ${activeTab === 'studio' ? 'active' : ''}`} onClick={() => setActiveTab('studio')}>
        <Code2 size={18} /><span>Vulnerability Studio</span>
      </div>
      <div className={`nav-item ${activeTab === 'models' ? 'active' : ''}`} onClick={() => setActiveTab('models')}>
        <Cpu size={18} /><span>10 Models Explorer</span>
      </div>
      <div className="nav-section-title">Documentation</div>
      <div className={`nav-item ${activeTab === 'docs' ? 'active' : ''}`} onClick={() => setActiveTab('docs')}>
        <BookOpen size={18} /><span>API Guide</span>
      </div>
      <div className="server-status">
        <div className={`status-dot ${apiStatus === 'offline' ? 'offline' : ''}`} />
        <span>{apiStatus === 'online' ? 'Backend API: Online (Port 5000)' : 'Backend API: Connecting/Offline'}</span>
      </div>
    </aside>
  );
}
