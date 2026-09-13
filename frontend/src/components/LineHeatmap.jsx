import React from 'react';

export default function LineHeatmap({ lineHighlights }) {
  return (
    <div className="code-heatmap">
      {lineHighlights.map(item => (
        <div key={item.line_num} className={`heatmap-line ${item.is_vulnerable_line ? 'vulnerable-line' : ''}`}>
          <div className="line-no">{item.line_num}</div>
          <div className="line-code">{item.code}</div>
          <div className="line-risk-badge">{item.risk_score}% Risk</div>
        </div>
      ))}
    </div>
  );
}
