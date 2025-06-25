import React, { useState, useEffect } from 'react';
import './App.css';
// import logo from './logo.svg';

const MODULES = [
  '會計', '成本', '派工', '維修', 'FAQ', '合約', '促案', '設備', '人員'
];

interface HistoryItem {
  query: string;
  module: string;
  answer: string;
  time: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [selectedModule, setSelectedModule] = useState('');
  const [result, setResult] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [health, setHealth] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);
  const [user] = useState('admin');

  useEffect(() => {
    fetch('/health').then(r => r.json()).then(d => setHealth(d.status || 'OK'));
    fetch('/notice').then(r => r.json()).then(d => setNotice(d.notice || ''));
    fetch('/history').then(r => r.json()).then(d => setHistory(d.history || []));
  }, []);

  const handleModuleClick = (mod: string) => {
    setSelectedModule(mod);
    setQuery(`請查詢${mod}相關資訊`);
  };

  const handleAsk = async () => {
    if (!query) return;
    setLoading(true);
    setResult('');
    try {
      const res = await fetch('/ai_ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, module: selectedModule })
      });
      const data = await res.json();
      setResult(data.answer || '無回應');
      setHistory(h => [{ query, module: selectedModule, answer: data.answer, time: new Date().toLocaleString() }, ...h]);
    } catch (e) {
      setResult('查詢失敗，請稍後再試');
    }
    setLoading(false);
  };

  return (
    <div className="app-bg">
      <header className="app-header">
        <img src={process.env.PUBLIC_URL + '/favicon.svg'} className="app-logo" alt="logo" />
        <div className="brand-title">智慧瓦斯管理系統 <span className="team">by Jy技術團隊</span></div>
        <div className="user-info">👤 {user}</div>
      </header>
      <div className="notice-bar">{notice}</div>
      <div className="main-content">
        <div className="module-cards">
          {MODULES.map(mod => (
            <div key={mod} className={`module-card${selectedModule===mod?' selected':''}`} onClick={() => handleModuleClick(mod)}>
              {mod}
            </div>
          ))}
        </div>
        <div className="query-area">
          <input
            className="query-input"
            type="text"
            placeholder="請輸入查詢內容..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key==='Enter' && handleAsk()}
          />
          <button className="ask-btn" onClick={handleAsk} disabled={loading}>{loading ? '查詢中...' : '查詢'}</button>
        </div>
        <div className="result-area">
          <div className="result-title">查詢結果</div>
          <div className="result-content">{result}</div>
        </div>
        <div className="history-area">
          <div className="history-title">查詢歷史</div>
          <ul className="history-list">
            {history.slice(0, 10).map((h, i) => (
              <li key={i} className="history-item">
                <span className="history-time">{h.time}</span>
                <span className="history-module">[{h.module}]</span>
                <span className="history-query">{h.query}</span>
                <span className="history-answer">→ {h.answer}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="status-bar">
          <span>系統健康狀態：<b className={health==='OK'?'ok':'fail'}>{health}</b></span>
        </div>
      </div>
    </div>
  );
}

export default App;
