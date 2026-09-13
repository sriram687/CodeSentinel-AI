import React from 'react';

export default function VerdictBanner({ scanResult }) {
  const isVuln = scanResult.status === 'VULNERABLE';
  return (
    <div className={`verdict-banner ${isVuln ? 'vulnerable' : 'safe'}`}>
      <div>
        <div className="verdict-text">
          {isVuln ? '⚠️ VULNERABLE CODE DETECTED' : '✅ CODE APPEARS SAFE'}
        </div>
        <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '2px' }}>
          Highest Flagging Model: <strong>{scanResult.top_model}</strong>
        </div>
      </div>
      <div className="score-chip">
        {scanResult.max_risk_score}% Max Risk
      </div>
    </div>
  );
}
