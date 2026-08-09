import React from 'react';
import { resolveCitationUrl } from '../utils/citationLinks';

const CITATION_RE = /\[([A-Za-z0-9][A-Za-z0-9\-\. ]*)\]/g;

// Renders finding/recommendation text with [STANDARD-ID] tokens turned into
// clickable links to the real authoritative standard -- reinforces that Judex
// AI's findings are citation-backed, not just LLM opinion.
export default function CitationText({ text }) {
  const str = typeof text === 'object' ? JSON.stringify(text) : String(text ?? '');
  const parts = [];
  let lastIndex = 0;
  let match;
  let key = 0;

  CITATION_RE.lastIndex = 0;
  while ((match = CITATION_RE.exec(str)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<React.Fragment key={key++}>{str.slice(lastIndex, match.index)}</React.Fragment>);
    }
    const standard = match[1];
    parts.push(
      <a
        key={key++}
        href={resolveCitationUrl(standard)}
        target="_blank"
        rel="noreferrer"
        onClick={(e) => e.stopPropagation()}
        style={{
          color: '#818cf8',
          textDecoration: 'none',
          borderBottom: '1px dashed rgba(129, 140, 248, 0.5)',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '0.92em',
        }}
        title={`View ${standard} reference`}
      >
        [{standard}]
      </a>
    );
    lastIndex = CITATION_RE.lastIndex;
  }
  if (lastIndex < str.length) {
    parts.push(<React.Fragment key={key++}>{str.slice(lastIndex)}</React.Fragment>);
  }

  return <>{parts.length > 0 ? parts : str}</>;
}
