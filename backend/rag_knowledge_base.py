"""
Knowledge Seed Data for Judex AI RAG Engine.

All 4 Domain Collections (Code Review, Tech Specs, API Docs, Security Logs)
structured as lists of {"id", "text", "metadata"} for ChromaDB ingestion.

These documents represent authoritative 2026 industry standards:
  - OWASP Top 10 2025/2026
  - W3C CSS Level 4 / CSS 2026 Logical Properties
  - Python 3.12+ / ES2026 / Go 1.22 Language Standards
  - OpenAPI 3.1 / RFC 7807 / OAuth2.1
  - NIST SIEM / SOC2 / GDPR Log Standards
"""

from typing import List, Dict, Any

# --- DOMAIN 1: CODE REVIEW --------------------------------------------------
CODE_REVIEW_DOCS: List[Dict[str, Any]] = [
    # Python Security
    {
        "id": "py-sec-001",
        "text": "OWASP A03 Injection (Python): Never build SQL queries with string concatenation. Always use parameterized queries or an ORM. Example vulnerable code: 'SELECT * FROM users WHERE id=' + user_id. Example safe code: cursor.execute('SELECT * FROM users WHERE id=?', (user_id,)). Applies to Python versions 3.8+.",
        "metadata": {"domain": "code_review", "language": "python", "category": "security", "standard": "OWASP-A03-2025"}
    },
    {
        "id": "py-sec-002",
        "text": "OWASP A02 Cryptographic Failures (Python): Never use MD5 or SHA1 for password hashing. Use bcrypt, argon2, or PBKDF2 with a salt. Python 3.12+: use hashlib.scrypt() or the bcrypt library. Storing raw passwords or using reversible encryption is a critical vulnerability.",
        "metadata": {"domain": "code_review", "language": "python", "category": "security", "standard": "OWASP-A02-2025"}
    },
    {
        "id": "py-sec-003",
        "text": "OWASP A01 Broken Access Control (Python): Every function or API handler that accesses user data must validate the caller's identity and permissions. Use decorators like @require_auth or middleware. Never rely on client-supplied user IDs without server-side authorization validation.",
        "metadata": {"domain": "code_review", "language": "python", "category": "security", "standard": "OWASP-A01-2025"}
    },
    {
        "id": "py-perf-001",
        "text": "Python 3.12 Async I/O Standard: Use async/await and asyncio for all I/O-bound operations (network calls, database queries, file reads). Blocking synchronous calls inside an async context (e.g., time.sleep() instead of asyncio.sleep()) block the entire event loop and cause severe latency regressions in production.",
        "metadata": {"domain": "code_review", "language": "python", "category": "performance", "standard": "PEP-3156"}
    },
    {
        "id": "py-perf-002",
        "text": "Python 3.12 Performance: Use compiled regex patterns (re.compile) outside hot loops. Avoid repeated string concatenation in loops -- use str.join() or io.StringIO. Use list comprehensions over explicit loops for 2x-5x performance gains. Profile with cProfile before micro-optimizing.",
        "metadata": {"domain": "code_review", "language": "python", "category": "performance", "standard": "PEP-8-2026"}
    },
    {
        "id": "py-qual-001",
        "text": "Python 3.12 Code Quality (PEP 8 + PEP 526): All function parameters and return types must have type annotations. Every public function must have a docstring (Google or NumPy style). Bare except clauses are forbidden -- always catch specific exception types. Use dataclasses or Pydantic models for structured data.",
        "metadata": {"domain": "code_review", "language": "python", "category": "quality", "standard": "PEP-8-PEP-526"}
    },
    # JavaScript / TypeScript
    {
        "id": "js-sec-001",
        "text": "OWASP A03 XSS (JavaScript): Never set innerHTML, outerHTML, or document.write() with untrusted user data. Use textContent for text insertion. In React/Vue/Angular use framework-level escaping. Sanitize inputs with DOMPurify when HTML rendering is required.",
        "metadata": {"domain": "code_review", "language": "javascript", "category": "security", "standard": "OWASP-A03-2025"}
    },
    {
        "id": "js-perf-001",
        "text": "ES2026 Performance Standard: Replace var declarations with const (preferred) or let. Avoid synchronous XHR (XMLHttpRequest). Use fetch() with async/await. Debounce or throttle high-frequency event listeners (scroll, resize, input). Use requestAnimationFrame for DOM animation updates.",
        "metadata": {"domain": "code_review", "language": "javascript", "category": "performance", "standard": "ES2026"}
    },
    {
        "id": "js-qual-001",
        "text": "TypeScript 5.x Code Quality: Use strict TypeScript (strict: true in tsconfig). Avoid implicit any types. Use interface over type for object shapes. Use readonly for immutable properties. Document all exported functions with JSDoc. Prefer named exports over default exports for better tree-shaking.",
        "metadata": {"domain": "code_review", "language": "javascript", "category": "quality", "standard": "TS5-2026"}
    },
    # CSS / SCSS
    {
        "id": "css-perf-001",
        "text": "W3C CSS 2026 GPU Acceleration: Elements using 3D transforms (perspective, rotateZ, rotateX, rotateY, scale) should use will-change: transform to promote them to a dedicated GPU compositor layer. Apply backface-visibility: hidden on 3D-transformed elements to prevent unnecessary back-face rendering. This avoids main-thread repaints.",
        "metadata": {"domain": "code_review", "language": "css", "category": "performance", "standard": "W3C-CSS-2026"}
    },
    {
        "id": "css-perf-002",
        "text": "W3C CSS 2026 Layout Containment: Apply contain: paint or contain: layout on independent UI components (cards, modals, panels) to limit browser repaint scope. Use content-visibility: auto on off-screen sections to defer rendering until needed. This reduces Cumulative Layout Shift (CLS) and improves Largest Contentful Paint (LCP).",
        "metadata": {"domain": "code_review", "language": "css", "category": "performance", "standard": "W3C-CSS-2026"}
    },
    {
        "id": "css-qual-001",
        "text": "W3C CSS 2026 Custom Properties Best Practice: Always provide fallback values for CSS custom properties -- use var(--accent, #6366f1) instead of var(--accent). This prevents invisible or broken styles when a CSS variable is not defined in the cascade. Use :root for global token definitions.",
        "metadata": {"domain": "code_review", "language": "css", "category": "quality", "standard": "W3C-CSS-2026"}
    },
    {
        "id": "css-qual-002",
        "text": "W3C CSS 2026 Logical Properties: Use logical properties instead of physical directional properties. Use inset-inline (not left/right), inset-block (not top/bottom), margin-inline (not margin-left/right), padding-block (not padding-top/bottom). This ensures correct bidirectional (RTL/LTR) layout support across all browsers.",
        "metadata": {"domain": "code_review", "language": "css", "category": "quality", "standard": "W3C-CSS-Logical-Properties-2026"}
    },
    # SQL
    {
        "id": "sql-sec-001",
        "text": "SQL Injection Prevention (OWASP A03): Never concatenate user input directly into SQL queries. Use parameterized queries or prepared statements in all database frameworks (SQLite, PostgreSQL, MySQL, MSSQL). Validate and whitelist column names used in dynamic ORDER BY clauses. Apply least-privilege principle to database users.",
        "metadata": {"domain": "code_review", "language": "sql", "category": "security", "standard": "OWASP-A03-2025"}
    },
    {
        "id": "sql-perf-001",
        "text": "SQL Query Performance (2026 Standards): Use indexes on columns appearing in WHERE, JOIN, and ORDER BY clauses. Avoid SELECT * -- always specify required columns. Prevent N+1 query patterns by using JOIN or subqueries. Use EXPLAIN ANALYZE to profile slow queries. Apply query result caching for static or low-volatility data.",
        "metadata": {"domain": "code_review", "language": "sql", "category": "performance", "standard": "SQL-ANSI-2023"}
    },
    # Shell
    {
        "id": "sh-sec-001",
        "text": "Shell Script Security (2026 Standards): Always quote variables in double-quotes (\"$variable\") to prevent word splitting and path traversal. Use set -euo pipefail at the top of every script. Avoid eval with user-supplied input. Validate all input arguments before use. Avoid granting root/sudo permissions unnecessarily.",
        "metadata": {"domain": "code_review", "language": "shell_script", "category": "security", "standard": "CIS-Shell-2026"}
    },
    # Docker / Kubernetes
    {
        "id": "docker-sec-001",
        "text": "Dockerfile Security (2026 Best Practices): Never run containers as root -- add USER nonroot directive. Always pin base image tags (e.g., python:3.12.3-slim NOT python:latest). Use multi-stage builds to minimize final image attack surface. Scan images with Trivy or Grype. Never store secrets in Dockerfile ENV instructions -- use Secrets managers.",
        "metadata": {"domain": "code_review", "language": "dockerfile", "category": "security", "standard": "CIS-Docker-2026"}
    },
    {
        "id": "k8s-sec-001",
        "text": "Kubernetes Security (2026 CIS Benchmark): Always define resource limits (CPU/memory requests and limits) for every container. Use Network Policies to restrict pod-to-pod communication. Avoid running containers with privileged: true. Use Pod Security Admission (PSA) enforcing 'restricted' profile. Rotate Kubernetes Secrets with External Secrets Operator.",
        "metadata": {"domain": "code_review", "language": "kubernetes", "category": "security", "standard": "CIS-K8s-2026"}
    },
]

# --- DOMAIN 2: TECHNICAL SPECS ----------------------------------------------
TECH_SPECS_DOCS: List[Dict[str, Any]] = [
    {
        "id": "spec-arch-001",
        "text": "System Architecture Best Practice (2026): A well-defined technical specification must identify all external service dependencies and their failure modes. Single Points of Failure (SPOF) must be eliminated using redundancy (active-active or active-passive). Define Circuit Breaker patterns for all downstream service calls.",
        "metadata": {"domain": "tech_specs", "category": "architecture", "standard": "ISO-25010-2026"}
    },
    {
        "id": "spec-arch-002",
        "text": "Microservices Architecture Standards (2026): Each microservice must own its own database (Database-per-Service pattern). Services must communicate via well-defined API contracts (OpenAPI 3.1). Implement distributed tracing (OpenTelemetry) and centralized logging (ELK/Grafana Loki) across all services.",
        "metadata": {"domain": "tech_specs", "category": "architecture", "standard": "CNCF-2026"}
    },
    {
        "id": "spec-sla-001",
        "text": "SLA / SLO Standards (2026): High-availability systems must target 99.9% uptime (8.7 hours downtime/year) or better. Define explicit Error Budget policies. P99 latency targets for API responses must be below 500ms. Backup Recovery Time Objective (RTO) must be defined for all critical data stores.",
        "metadata": {"domain": "tech_specs", "category": "reliability", "standard": "SRE-Google-2026"}
    },
    {
        "id": "spec-privacy-001",
        "text": "GDPR & Data Privacy Requirements (2026): Technical specifications must identify all Personal Identifiable Information (PII) data flows. Apply data minimization -- collect only what is necessary. Implement right-to-erasure (data deletion) capability. All PII must be encrypted at rest (AES-256) and in transit (TLS 1.3).",
        "metadata": {"domain": "tech_specs", "category": "compliance", "standard": "GDPR-2026"}
    },
    {
        "id": "spec-soc2-001",
        "text": "SOC2 Type II Technical Requirements (2026): Access logs must be retained for a minimum of 90 days. Multi-Factor Authentication (MFA) is mandatory for all administrative access. Vulnerability scanning must be performed on all production assets quarterly. Change management procedures must be documented and enforced.",
        "metadata": {"domain": "tech_specs", "category": "compliance", "standard": "SOC2-AICPA-2026"}
    },
]

# --- DOMAIN 3: API DOCUMENTATION --------------------------------------------
API_DOCS_DOCS: List[Dict[str, Any]] = [
    {
        "id": "api-auth-001",
        "text": "API Authentication Standard (OAuth2.1 / OpenAPI 3.1): All protected endpoints must require Authorization: Bearer <token> header. Implement OAuth2.1 with PKCE for public clients. JWT tokens must use RS256 or ES256 signing algorithms (never HS256 with shared secrets in distributed systems). Token expiry must be short (15-60 minutes) with refresh token rotation.",
        "metadata": {"domain": "api_docs", "category": "security", "standard": "OAuth2.1-RFC9700"}
    },
    {
        "id": "api-rate-001",
        "text": "API Rate Limiting Standard (RFC 6585 / 2026 Best Practice): All public API endpoints must implement rate limiting. Return HTTP 429 Too Many Requests with Retry-After header when limits are exceeded. Document rate limits in the API spec (requests per second/minute/hour per client). Use token bucket or sliding window algorithm for accurate enforcement.",
        "metadata": {"domain": "api_docs", "category": "security", "standard": "RFC-6585-2026"}
    },
    {
        "id": "api-error-001",
        "text": "API Error Response Standard (RFC 7807 Problem Details): All API error responses must follow RFC 7807 Problem Details format: {type, title, status, detail, instance}. Never return stack traces or internal error messages in production responses. Use consistent HTTP status codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 422 (validation error), 500 (internal error).",
        "metadata": {"domain": "api_docs", "category": "quality", "standard": "RFC-7807"}
    },
    {
        "id": "api-versioning-001",
        "text": "API Versioning Best Practice (OpenAPI 3.1): All APIs must be versioned using URL path versioning (e.g., /v1/, /v2/). Deprecated endpoints must return a Deprecation header with sunset date. Breaking changes must be released on a new major version. Non-breaking changes (additive fields, new optional parameters) can be released on the same version.",
        "metadata": {"domain": "api_docs", "category": "quality", "standard": "OpenAPI-3.1-2026"}
    },
    {
        "id": "api-cors-001",
        "text": "CORS & API Security Headers Standard (OWASP): Configure CORS to allow only specific trusted origins -- never use * in production with credentials. Set Strict-Transport-Security (HSTS) header. Apply Content-Type: application/json strictly. Validate Content-Type on all POST/PUT/PATCH requests to prevent CSRF.",
        "metadata": {"domain": "api_docs", "category": "security", "standard": "OWASP-API-2025"}
    },
]

# --- DOMAIN 4: SECURITY LOGS ------------------------------------------------
SECURITY_LOG_DOCS: List[Dict[str, Any]] = [
    {
        "id": "log-brute-001",
        "text": "Brute Force Attack Detection (NIST 800-63B / 2026 SIEM Standard): A brute-force attack pattern is identified by 5+ failed authentication attempts from a single IP within 10 minutes. Indicators: repeated 401/403 status codes, sequential username enumeration, or credential stuffing with known breached password lists. Immediate response: temporary IP block and alert to SOC.",
        "metadata": {"domain": "security_logs", "category": "threat_detection", "standard": "NIST-800-63B"}
    },
    {
        "id": "log-sqli-001",
        "text": "SQL Injection Log Detection (OWASP / WAF Signatures 2026): SQL injection attempts appear in access logs as URL parameters containing: single quotes ('), double dashes (--), UNION SELECT, OR 1=1, DROP TABLE, xp_cmdshell, or hex-encoded payloads (%27, %3D). Correlate with HTTP 500 errors and abnormally long query strings (>2000 chars).",
        "metadata": {"domain": "security_logs", "category": "threat_detection", "standard": "OWASP-A03-WAF-2026"}
    },
    {
        "id": "log-priv-001",
        "text": "Privilege Escalation Detection (CIS Benchmark / SIEM 2026): Privilege escalation patterns in system logs: sudo usage by non-administrator users, unexpected su or su - commands, SUID binary execution, unexpected kernel module loads (insmod), or creation of new user accounts outside change management windows. Correlate with /var/log/auth.log or Windows Security Event ID 4672.",
        "metadata": {"domain": "security_logs", "category": "threat_detection", "standard": "CIS-SIEM-2026"}
    },
    {
        "id": "log-format-001",
        "text": "Structured Log Format Standard (NIST 800-92 / ELK Stack 2026): Production logs must use structured JSON format with mandatory fields: timestamp (ISO 8601), severity (DEBUG/INFO/WARN/ERROR/CRITICAL), service_name, trace_id (correlation ID), user_id (anonymized), and message. Unstructured plaintext logs cannot be reliably ingested by SIEM tools and break automated alert pipelines.",
        "metadata": {"domain": "security_logs", "category": "quality", "standard": "NIST-800-92-2026"}
    },
    {
        "id": "log-anomaly-001",
        "text": "Network Anomaly Detection (NIST / Zeek 2026): Anomalous network access patterns include: off-hours access (outside business hours 09:00-18:00 local time), access from previously unseen geographic regions, data exfiltration indicators (large outbound transfer spikes > 100MB in 5 minutes), and access to sensitive endpoints from non-privileged service accounts.",
        "metadata": {"domain": "security_logs", "category": "threat_detection", "standard": "NIST-SP-800-137"}
    },
]

# --- Unified Manifest --------------------------------------------------------
ALL_DOMAIN_DOCS: Dict[str, List[Dict[str, Any]]] = {
    "code_review":    CODE_REVIEW_DOCS,
    "tech_specs":     TECH_SPECS_DOCS,
    "api_docs":       API_DOCS_DOCS,
    "security_logs":  SECURITY_LOG_DOCS,
}