import React from 'react';
import { ExternalLink } from 'lucide-react';

export default function Header({ setCurrentPage }) {
  return (
    <header className="sticky-header">
      <div className="header-inner">
        <div
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          onClick={() => setCurrentPage('home')}
        >
          <div className="header-wordmark">
            <span>Judex AI</span>
          </div>
        </div>

        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          className="header-link"
        >
          GitHub <ExternalLink size={12} />
        </a>
      </div>
    </header>
  );
}
