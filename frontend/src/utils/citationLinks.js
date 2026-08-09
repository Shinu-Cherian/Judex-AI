// Maps standard IDs cited by the inspector panel (e.g. "[OWASP-A03-2025]") to
// their real authoritative reference URL, so citations are clickable and verifiable.
export const CITATION_LINKS = {
  'OWASP-A01-2025': 'https://owasp.org/Top10/A01_2021-Broken_Access_Control/',
  'OWASP-A02-2025': 'https://owasp.org/Top10/A02_2021-Cryptographic_Failures/',
  'OWASP-A03-2025': 'https://owasp.org/Top10/A03_2021-Injection/',
  'OWASP-A03-WAF-2026': 'https://owasp.org/Top10/A03_2021-Injection/',
  'OWASP-API-2025': 'https://owasp.org/API-Security/editions/2023/en/0x00-header/',
  'PEP-8-PEP-526': 'https://peps.python.org/pep-0008/',
  'PEP-3156': 'https://peps.python.org/pep-3156/',
  'ES2026': 'https://tc39.es/ecma262/',
  'TS5-2026': 'https://www.typescriptlang.org/tsconfig#strict',
  'W3C-CSS-2026': 'https://www.w3.org/TR/css-will-change-1/',
  'W3C-CSS-Logical-Properties-2026': 'https://www.w3.org/TR/css-logical-1/',
  'SQL-ANSI-2023': 'https://www.iso.org/standard/76583.html',
  'CIS-Shell-2026': 'https://www.cisecurity.org/cis-benchmarks',
  'CIS-Docker-2026': 'https://www.cisecurity.org/benchmark/docker',
  'CIS-K8s-2026': 'https://www.cisecurity.org/benchmark/kubernetes',
  'CIS-SIEM-2026': 'https://www.cisecurity.org/cis-benchmarks',
  'ISO-25010-2026': 'https://www.iso.org/standard/78176.html',
  'CNCF-2026': 'https://www.cncf.io/',
  'SRE-Google-2026': 'https://sre.google/sre-book/table-of-contents/',
  'GDPR-2026': 'https://gdpr.eu/',
  'SOC2-AICPA-2026': 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
  'OAuth2.1-RFC9700': 'https://www.rfc-editor.org/rfc/rfc9700',
  'RFC-6585-2026': 'https://www.rfc-editor.org/rfc/rfc6585',
  'RFC-7807': 'https://www.rfc-editor.org/rfc/rfc7807',
  'OpenAPI-3.1-2026': 'https://spec.openapis.org/oas/v3.1.0',
  'NIST-800-63B': 'https://pages.nist.gov/800-63-3/sp800-63b.html',
  'NIST-800-92-2026': 'https://csrc.nist.gov/pubs/sp/800/92/final',
  'NIST-SP-800-137': 'https://csrc.nist.gov/pubs/sp/800/137/final',
  'NIST Enterprise Baseline': 'https://www.nist.gov/cyberframework',
  'HIPAA': 'https://www.hhs.gov/hipaa/index.html',
  'PCI-DSS': 'https://www.pcisecuritystandards.org/standards/pci-dss/',
};

export function resolveCitationUrl(standard) {
  const clean = standard.trim();
  if (CITATION_LINKS[clean]) return CITATION_LINKS[clean];
  // Unknown standard -- still make it useful instead of a dead link
  return `https://www.google.com/search?q=${encodeURIComponent(clean + ' security standard')}`;
}
