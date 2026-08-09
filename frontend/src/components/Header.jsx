import React from 'react';
import { ExternalLink } from 'lucide-react';

const NAV_ITEMS = [
  { key: 'features', label: 'Features' },
  { key: 'how-it-works', label: 'How It Works' },
  { key: 'analyzer', label: 'Live Analyzer' },
];

export default function Header({ onNavigate }) {
  return (
    <header className="sticky-header">
      <div className="header-inner">
        <div
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          onClick={() => onNavigate('home')}
        >
          <div className="header-wordmark">
            <span>Judex AI</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
          <nav className="nav-links header-nav">
            {NAV_ITEMS.map((item) => (
              <button key={item.key} className="nav-link-btn" onClick={() => onNavigate(item.key)}>
                {item.label}
              </button>
            ))}
          </nav>

          <a
            href="https://github.com/Shinu-Cherian/judex-AI"
            target="_blank"
            rel="noreferrer"
            className="header-link"
          >
            GitHub <ExternalLink size={12} />
          </a>
        </div>
      </div>
    </header>
  );
}
