import React from 'react';

export default function ModelBreakdownTable({ modelResults }) {
  return (
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
        {modelResults.map(m => (
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
  );
}
