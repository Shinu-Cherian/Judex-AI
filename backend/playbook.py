"""
Judex Playbook -- Org Security Policy Memory.
Deterministic rule-based compliance checking so results are 100% reproducible
and never hallucinated (unlike an LLM-judged custom policy would be).

Each rule is checked by simple case-insensitive pattern matching against the
pasted content. Two modes:
  - "forbidden": violated if ANY bad pattern IS present   (e.g. "no MD5 hashing")
  - "required":  violated if NONE of the patterns are present (e.g. "auth must be documented")

Rules are also tagged with the input "domain" they apply to (code / api / logs / specs)
so a Fintech profile checks different things on pasted Python code vs. a pasted
OpenAPI spec vs. a pasted log file -- instead of one-size-fits-all code rules.
"""

import re
from typing import Dict, Any, List, Optional

# -- Content-type -> domain bucket (mirrors analyzer.py's own grouping) ---------
CODE_CONTENT_TYPES = {
    "python", "javascript", "java_or_similar", "code_generic", "sql", "shell_script",
    "dockerfile", "kubernetes", "json_config", "html", "css", "c_cpp", "csharp",
    "rust", "go", "php", "ruby", "swift",
}
API_CONTENT_TYPES = {"api_spec"}
LOG_CONTENT_TYPES = {"security_log"}
# Anything else (legal_contract, or generic prose that isn't code) is treated as "specs"


def domain_of(content_type: Optional[str]) -> str:
    """Map a detected content_type into one of the 4 playbook rule domains."""
    if content_type in API_CONTENT_TYPES:
        return "api"
    if content_type in LOG_CONTENT_TYPES:
        return "logs"
    if content_type in CODE_CONTENT_TYPES:
        return "code"
    return "specs"


def _rule(rule_id, title, mode, patterns, fix_hint, standard, domains=("code",), applies_if=None):
    return {
        "id": rule_id,
        "title": title,
        "mode": mode,  # "forbidden" | "required"
        "patterns": patterns,
        "fix_hint": fix_hint,
        "standard": standard,
        "domains": set(domains),
        "applies_if": applies_if,  # optional: rule only scored if one of these substrings is present
    }


PLAYBOOK_PROFILES: Dict[str, Dict[str, Any]] = {
    "fintech": {
        "name": "Fintech / Payments",
        "description": "PCI-DSS aligned rules for payment and transaction handling -- code, APIs, logs, and specs.",
        "rules": [
            # -- code --
            _rule("no-weak-hash", "Passwords must use bcrypt or argon2, never MD5/SHA1", "forbidden",
                  ["md5(", "hashlib.md5", "digest::md5", "md5.hexdigest", "md5.digest", "sha1(", "hashlib.sha1", "digest::sha1", "sha1.hexdigest"],
                  "import bcrypt; bcrypt.hashpw(password.encode(), bcrypt.gensalt())", "OWASP-A02-2025"),
            _rule("no-raw-sql", "All SQL must use parameterized queries, not string concatenation", "forbidden",
                  ["' + ", "\" + ", "% (", "f\"select", "f'select", "f\"insert", "f'insert"],
                  "db.execute(\"INSERT INTO payments VALUES (?)\", (value,))", "OWASP-A03-2025"),
            _rule("audit-trail", "Every payment/transaction function must emit an audit log", "required",
                  ["log", "audit"], "Add structured audit logging (log.info(...)) before returning from the function.",
                  "SOC2-AICPA-2026", applies_if=["payment", "transaction", "transfer"]),
            _rule("no-secrets", "No hardcoded API keys or secrets in source", "forbidden",
                  ["sk_live_", "api_key=\"", "api_key='", "password=\"", "password='", "aws_secret", "akia"],
                  "Move secrets to environment variables or a secrets vault (.env / AWS Secrets Manager).", "CIS-SIEM-2026"),
            _rule("rate-limiting", "Public API endpoints must implement rate limiting", "required",
                  ["limiter", "rate_limit", "throttle"],
                  "Add a rate limiter (e.g. slowapi, express-rate-limit) to this endpoint.", "RFC-6585-2026",
                  applies_if=["@app.route", "@app.post", "@app.get", "router.post", "router.get"]),
            # -- api --
            _rule("api-auth-scheme", "Payment API endpoints must declare Bearer/OAuth2 authentication", "required",
                  ["bearer", "oauth", "authorization:"],
                  "Add securitySchemes (bearerAuth) and require it on every payment endpoint.",
                  "OAuth2.1-RFC9700", domains=("api",)),
            _rule("api-rate-limit-doc", "Rate limiting must be documented for payment endpoints", "required",
                  ["rate limit", "x-ratelimit", "429", "throttle"],
                  "Document a 429 Too Many Requests response and rate-limit headers.",
                  "RFC-6585-2026", domains=("api",)),
            _rule("api-card-in-url", "Card data must never be passed as a URL query parameter", "forbidden",
                  ["?card_number=", "&card_number=", "?cvv="],
                  "Move sensitive fields into the request body, never the URL.",
                  "OWASP-API-2025", domains=("api",)),
            # -- logs --
            _rule("log-no-raw-card", "Raw card numbers must not appear in log entries", "forbidden",
                  ["card_number=", "\"card_number\":", "pan="],
                  "Mask card numbers to last 4 digits before logging.", "CIS-SIEM-2026", domains=("logs",)),
            _rule("log-failed-payment-alert", "Failed payment attempts must be flagged for alerting", "required",
                  ["alert", "notify", "siem", "sentry"],
                  "Emit an alert/notification when a payment attempt fails or is declined.",
                  "NIST-800-92-2026", domains=("logs",), applies_if=["failed", "declined", "error"]),
            # -- specs --
            _rule("spec-pci-dss", "Spec must state PCI-DSS compliance requirement", "required",
                  ["pci-dss", "pci dss"], "Add an explicit PCI-DSS compliance requirement section.",
                  "PCI-DSS", domains=("specs",)),
            _rule("spec-encryption", "Spec must state encryption at rest/in transit for payment data", "required",
                  ["encrypt", "aes-256", "tls"], "State AES-256 at rest and TLS 1.3 in transit for payment data.",
                  "GDPR-2026", domains=("specs",)),
        ],
    },
    "healthcare": {
        "name": "Healthcare / HIPAA",
        "description": "HIPAA-aligned rules for handling patient health information -- code, APIs, logs, and specs.",
        "rules": [
            # -- code --
            _rule("no-phi-in-logs", "No patient identifiers in log/print statements", "forbidden",
                  ["print(patient", "log.info(patient", "print(ssn", "print(dob", "logging.info(patient"],
                  "Log an anonymized/hashed reference instead of the raw patient identifier.", "NIST-800-92-2026"),
            _rule("no-weak-hash", "Passwords must use bcrypt or argon2, never MD5/SHA1", "forbidden",
                  ["md5(", "hashlib.md5", "digest::md5", "md5.hexdigest", "md5.digest", "sha1(", "hashlib.sha1", "digest::sha1", "sha1.hexdigest"],
                  "import bcrypt; bcrypt.hashpw(password.encode(), bcrypt.gensalt())", "OWASP-A02-2025"),
            _rule("no-raw-sql", "All SQL must use parameterized queries, not string concatenation", "forbidden",
                  ["' + ", "\" + ", "% (", "f\"select", "f'select"],
                  "Use parameterized queries or an ORM for all patient record access.", "OWASP-A03-2025"),
            _rule("no-secrets", "No hardcoded API keys or secrets in source", "forbidden",
                  ["sk_live_", "api_key=\"", "api_key='", "password=\"", "password='", "aws_secret", "akia"],
                  "Move secrets to environment variables or a secrets vault.", "CIS-SIEM-2026"),
            _rule("access-control", "Patient data access must be behind an auth/permission check", "required",
                  ["require_auth", "@login_required", "permission", "authorize"],
                  "Add an explicit @require_auth / permission check before returning patient data.",
                  "OWASP-A01-2025", applies_if=["def get_patient", "def get_record", "/patient/", "/records/"]),
            # -- api --
            _rule("api-auth-scheme", "Patient data endpoints must declare an auth scheme", "required",
                  ["bearer", "oauth", "authorization:"],
                  "Require Bearer/OAuth2 auth on every endpoint returning patient data.",
                  "OWASP-API-2025", domains=("api",)),
            _rule("api-error-no-phi", "API errors must use a generic schema, not leak patient data", "required",
                  ["problem+json", "error schema", "rfc 7807"],
                  "Define a generic error schema (RFC 7807) that never echoes back PHI fields.",
                  "RFC-7807", domains=("api",)),
            # -- logs --
            _rule("log-no-phi", "Patient identifiers must not appear in log fields", "forbidden",
                  ["patient_id=", "ssn=", "\"patient_id\":"],
                  "Log a hashed/anonymized reference instead of raw patient identifiers.",
                  "NIST-800-92-2026", domains=("logs",)),
            _rule("log-access-audit", "Record access must be logged with timestamp + user id", "required",
                  ["timestamp", "user_id", "trace_id"],
                  "Every record-access log line must include timestamp, user_id, and trace_id.",
                  "NIST-800-92-2026", domains=("logs",)),
            # -- specs --
            _rule("spec-hipaa", "Spec must state HIPAA compliance requirement", "required",
                  ["hipaa"], "Add an explicit HIPAA compliance requirement section.",
                  "HIPAA", domains=("specs",)),
            _rule("spec-encryption", "Spec must state encryption at rest for PHI", "required",
                  ["encrypt", "aes-256"], "State AES-256 encryption at rest for PHI.",
                  "GDPR-2026", domains=("specs",)),
        ],
    },
    "startup": {
        "name": "Startup / OWASP Top 10 Baseline",
        "description": "General-purpose OWASP Top 10 baseline for early-stage teams -- code, APIs, logs, and specs.",
        "rules": [
            # -- code --
            _rule("no-raw-sql", "All SQL must use parameterized queries, not string concatenation", "forbidden",
                  ["' + ", "\" + ", "% (", "f\"select", "f'select", "f\"insert", "f'insert"],
                  "Use parameterized queries or an ORM (SQLAlchemy, Prisma, etc.).", "OWASP-A03-2025"),
            _rule("no-xss", "No eval() / innerHTML / document.write() with untrusted input", "forbidden",
                  ["eval(", "innerhtml", "document.write("],
                  "Use textContent, or sanitize with DOMPurify before inserting HTML.", "OWASP-A03-2025"),
            _rule("no-secrets", "No hardcoded API keys or secrets in source", "forbidden",
                  ["sk_live_", "api_key=\"", "api_key='", "password=\"", "password='", "aws_secret", "akia"],
                  "Move secrets to environment variables (.env) or a secrets manager.", "CIS-SIEM-2026"),
            _rule("bare-except", "No bare except clauses that swallow all errors", "forbidden",
                  ["except:", "except Exception:"],
                  "Catch the specific exception type and handle or re-raise it.", "PEP-8-PEP-526"),
            # -- api --
            _rule("api-auth-scheme", "Endpoints must declare an authentication scheme", "required",
                  ["bearer", "oauth", "authorization:", "api key", "apikey"],
                  "Add an auth scheme (Bearer/API key) to the spec.", "OWASP-API-2025", domains=("api",)),
            _rule("api-error-schema", "Error responses must follow a consistent schema", "required",
                  ["problem+json", "error schema", "rfc 7807", "400", "401", "404"],
                  "Define consistent error response schema (RFC 7807 recommended).",
                  "RFC-7807", domains=("api",)),
            # -- logs --
            _rule("log-structured", "Logs should be structured (JSON), not plaintext", "required",
                  ["\"timestamp\"", "\"level\"", "\"message\""],
                  "Emit logs as structured JSON with timestamp/level/message fields.",
                  "NIST-800-92-2026", domains=("logs",)),
            _rule("log-no-secrets", "Secrets/tokens must not appear in log lines", "forbidden",
                  ["api_key=", "token=", "password="],
                  "Redact secrets before logging.", "CIS-SIEM-2026", domains=("logs",)),
            # -- specs --
            _rule("spec-sla", "Spec should define a failure mode / SLA", "required",
                  ["sla", "uptime", "rto", "failure mode"],
                  "Add an explicit SLA / failure-mode section.", "SRE-Google-2026", domains=("specs",)),
            _rule("spec-owasp", "Spec should reference an OWASP Top 10 baseline", "required",
                  ["owasp"], "Reference OWASP Top 10 as the baseline security requirement.",
                  "OWASP-A03-2025", domains=("specs",)),
        ],
    },
    "enterprise": {
        "name": "Enterprise / Bank (PCI-DSS)",
        "description": "PCI-DSS aligned rules for institutions handling card data at scale -- code, APIs, logs, and specs.",
        "rules": [
            # -- code --
            _rule("no-raw-card", "Raw card numbers must never be logged or stored in plaintext", "forbidden",
                  ["print(card", "log.info(card", "card_number +", "card_number)"],
                  "Mask card numbers (show last 4 digits only) before logging or persisting.",
                  "CIS-SIEM-2026", applies_if=["card_number", "card number", "cardnumber"]),
            _rule("no-weak-hash", "Passwords must use bcrypt or argon2, never MD5/SHA1", "forbidden",
                  ["md5(", "hashlib.md5", "digest::md5", "md5.hexdigest", "md5.digest", "sha1(", "hashlib.sha1", "digest::sha1", "sha1.hexdigest"],
                  "import bcrypt; bcrypt.hashpw(password.encode(), bcrypt.gensalt())", "OWASP-A02-2025"),
            _rule("no-raw-sql", "All SQL must use parameterized queries, not string concatenation", "forbidden",
                  ["' + ", "\" + ", "% (", "f\"select", "f'select"],
                  "Use parameterized queries or an ORM for all data access.", "OWASP-A03-2025"),
            _rule("no-secrets", "No hardcoded API keys or secrets in source", "forbidden",
                  ["sk_live_", "api_key=\"", "api_key='", "password=\"", "password='", "aws_secret", "akia"],
                  "Move secrets to environment variables or a secrets vault.", "CIS-SIEM-2026"),
            _rule("rate-limiting", "Public API endpoints must implement rate limiting", "required",
                  ["limiter", "rate_limit", "throttle"],
                  "Add a rate limiter to this endpoint.", "RFC-6585-2026",
                  applies_if=["@app.route", "@app.post", "@app.get", "router.post", "router.get"]),
            # -- api --
            _rule("api-auth-scheme", "Endpoints must declare Bearer/OAuth2 authentication", "required",
                  ["bearer", "oauth", "authorization:"],
                  "Require OAuth2.1 Bearer auth on all endpoints.", "OAuth2.1-RFC9700", domains=("api",)),
            _rule("api-rate-limit-doc", "Rate limiting must be documented", "required",
                  ["rate limit", "x-ratelimit", "429"],
                  "Document rate limiting and 429 responses.", "RFC-6585-2026", domains=("api",)),
            # -- logs --
            _rule("log-no-raw-card", "Raw card numbers must not appear in logs", "forbidden",
                  ["card_number=", "pan=", "\"card_number\":"],
                  "Mask card numbers before logging.", "CIS-SIEM-2026", domains=("logs",)),
            _rule("log-privesc-alert", "Privilege escalation attempts must be logged with alerting", "required",
                  ["alert", "sudo", "privilege"],
                  "Correlate privilege-escalation indicators with SOC alerting.",
                  "CIS-SIEM-2026", domains=("logs",), applies_if=["sudo", "admin", "root"]),
            # -- specs --
            _rule("spec-pci-dss", "Spec must state PCI-DSS compliance", "required",
                  ["pci-dss", "pci dss"], "Add PCI-DSS compliance requirement section.",
                  "PCI-DSS", domains=("specs",)),
            _rule("spec-mfa", "Spec must state MFA requirement for admin access", "required",
                  ["mfa", "multi-factor", "2fa"], "Require MFA for all administrative access.",
                  "SOC2-AICPA-2026", domains=("specs",)),
        ],
    },
}


def list_profiles() -> List[Dict[str, Any]]:
    """Return lightweight profile metadata for the frontend selector dropdown."""
    return [
        {
            "id": pid,
            "name": p["name"],
            "description": p["description"],
            "rule_count": len(p["rules"]),
        }
        for pid, p in PLAYBOOK_PROFILES.items()
    ]


def _normalize_custom_rule(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convert a frontend-submitted custom rule {title, bad_patterns, fix_hint} into the internal schema."""
    title = str(raw.get("title", "")).strip()
    patterns = raw.get("bad_patterns", [])
    if isinstance(patterns, str):
        patterns = [p.strip() for p in patterns.split(",") if p.strip()]
    patterns = [str(p).strip().lower() for p in patterns if str(p).strip()]
    if not title or not patterns:
        return None
    return _rule(
        rule_id=f"custom-{re.sub(r'[^a-z0-9]+', '-', title.lower())[:40]}",
        title=title,
        mode="forbidden",
        patterns=patterns,
        fix_hint=str(raw.get("fix_hint", "")).strip() or "Review and remediate this pattern per your org policy.",
        standard="ORG-PLAYBOOK",
        domains=("code", "api", "logs", "specs"),  # custom rules are user-authored -- apply regardless of domain
    )


def get_rules(profile_id: Optional[str], custom_rules: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Resolve a profile id + optional custom rules into a combined ruleset."""
    rules: List[Dict[str, Any]] = []
    profile_name = None

    if profile_id and profile_id in PLAYBOOK_PROFILES:
        profile = PLAYBOOK_PROFILES[profile_id]
        profile_name = profile["name"]
        rules.extend(profile["rules"])

    if custom_rules:
        for raw in custom_rules:
            normalized = _normalize_custom_rule(raw)
            if normalized:
                rules.append(normalized)

    return {"profile_name": profile_name, "rules": rules}


def evaluate_playbook(
    content: str,
    profile_id: Optional[str],
    custom_rules: Optional[List[Dict[str, Any]]],
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run deterministic playbook compliance checks against the pasted content.
    Only rules tagged for the detected content's domain (code/api/logs/specs) are scored --
    e.g. a Fintech profile checks different things on pasted code vs. a pasted API spec.
    Returns {enabled, profile_name, violations: [...], passed: [...], rule_count}.
    """
    resolved = get_rules(profile_id, custom_rules)
    all_rules = resolved["rules"]

    if not all_rules:
        return {"enabled": False, "profile_name": None, "violations": [], "passed": [], "rule_count": 0}

    domain = domain_of(content_type)
    rules = [r for r in all_rules if domain in r["domains"]]

    if not rules:
        return {
            "enabled": True, "profile_name": resolved["profile_name"],
            "violations": [], "passed": [], "rule_count": 0,
        }

    text_lower = content.lower()
    violations = []
    passed = []

    for rule in rules:
        applies_if = rule.get("applies_if")
        if applies_if and not any(a in text_lower for a in applies_if):
            continue  # precondition not present in this content -- not applicable, skip scoring

        any_hit = next((p for p in rule["patterns"] if p in text_lower), None)
        entry = {
            "id": rule["id"],
            "title": rule["title"],
            "standard": rule["standard"],
            "fix_hint": rule["fix_hint"],
        }

        if rule["mode"] == "forbidden":
            violated = any_hit is not None
            evidence = f"Matched pattern: \"{any_hit}\"" if any_hit else None
        else:  # "required"
            violated = any_hit is None
            evidence = "None of the required patterns were found." if violated else f"Found: \"{any_hit}\""

        if violated:
            entry["evidence"] = evidence
            violations.append(entry)
        else:
            passed.append(entry)

    return {
        "enabled": True,
        "profile_name": resolved["profile_name"],
        "violations": violations,
        "passed": passed,
        "rule_count": len(rules),
    }
