import React from 'react';
import HackerTerminal from './components/HackerTerminal';
import './index.css';

function App() {
  return (
    <div style={{ margin: 0, padding: 0, height: '100vh', width: '100vw', backgroundColor: '#fcfbf9', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <HackerTerminal />
    </div>
  );
}

export default App;
