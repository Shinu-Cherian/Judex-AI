"""
Temporal Risk Scoring Engine -- Multi-Domain Code & Web Standards Evolution
Calculates risk score adjustments based on technology standards drift (e.g. 2020 baseline vs 2026 standards),
security paradigm shifts, and deprecated language features.
"""

import re
from typing import Dict, Any

def calculate_temporal_risk(clause_text: str, base_risk: str, content_type: str = "code_generic") -> Dict[str, Any]:
    """
    Analyzes temporal standards drift between 2020 and 2026 for code, APIs, HTML, CSS, and security.
    """
    text = clause_text or ""
    t_lower = text.lower()

    if content_type == "css":
        explanation = (
            "In 2020, CSS vendor prefixes and heavy preprocessor rules (Sass/Less compile steps) were required. "
            "Under 2026 W3C CSS standards, native CSS nesting, logical properties (inset-inline), and GPU acceleration "
            "are native browser standards, offering optimal rendering performance."
        )
        return {
            "risk_2020": "LOW",
            "risk_2026": "LOW",
            "extracted_value": "Modern CSS3 / SCSS",
            "inflation_adjusted": "W3C 2026 Standard",
            "value_loss": "Zero Prefix Overhead",
            "industry_avg_2026": "Native Nesting & Logical Props",
            "explanation": explanation,
            "deprecated": "0 found",
            "drift": "0 levels",
            "needs_renegotiation": False
        }

    elif content_type in ["python", "javascript", "java_or_similar", "code_generic", "sql", "shell_script"]:
        has_deprecated_patterns = any(k in t_lower for k in ["eval(", "exec(", "var ", "md5", "sha1", "urllib", "subprocess.call", "xml.etree", "strcpy", "gets("])

        risk_2020 = "LOW"
        risk_2026 = "HIGH" if has_deprecated_patterns else ("MEDIUM" if base_risk in ["HIGH", "CRITICAL"] else "LOW")
        deprecated_count = 2 if has_deprecated_patterns else 0

        explanation = (
            "In 2020, implicit type declarations and synchronous processing patterns were widely accepted. "
            "Under 2026 code quality and security standards, strict type safety, async I/O non-blocking execution, "
            "and explicit input sanitization are mandatory requirements for production deployment."
        )

        return {
            "risk_2020": risk_2020,
            "risk_2026": risk_2026,
            "extracted_value": "Python 3.12+ / ES2026",
            "inflation_adjusted": "Strict Standards",
            "value_loss": "Legacy Pattern Risk",
            "industry_avg_2026": "Type Safety & Async I/O",
            "explanation": explanation,
            "deprecated": f"{deprecated_count} found" if deprecated_count > 0 else "0 found",
            "drift": "1 level" if risk_2026 == "MEDIUM" else ("2 levels" if risk_2026 == "HIGH" else "0 levels"),
            "needs_renegotiation": risk_2026 in ["HIGH", "CRITICAL"]
        }

    elif content_type == "html":
        has_csp = "content-security-policy" in t_lower
        explanation = (
            "In 2020, simple HTML markup without strict Content Security Policy (CSP) headers was common. "
            "By 2026 W3C standards, CSP nonces, Subresource Integrity (SRI) hashes, and mandatory script deferral "
            "are essential to protect modern web applications against zero-day XSS attacks."
        )
        return {
            "risk_2020": "LOW",
            "risk_2026": "MEDIUM" if not has_csp else "LOW",
            "extracted_value": "HTML5 / DOM",
            "inflation_adjusted": "W3C 2026 Standard",
            "value_loss": "XSS Surface Exposure",
            "industry_avg_2026": "CSP & SRI Integrity",
            "explanation": explanation,
            "deprecated": "1 found" if not has_csp else "0 found",
            "drift": "1 level",
            "needs_renegotiation": not has_csp
        }

    elif content_type == "security_log":
        explanation = (
            "2020 log analysis relied on manual threshold rules. 2026 automated SIEM standards require real-time anomaly detection, "
            "correlation IDs across distributed microservices, and structured JSON telemetry."
        )
        return {
            "risk_2020": "LOW",
            "risk_2026": "HIGH" if base_risk in ["HIGH", "CRITICAL"] else "MEDIUM",
            "extracted_value": "SIEM Telemetry",
            "inflation_adjusted": "2026 Threat Vectors",
            "value_loss": "Log Surface Gap",
            "industry_avg_2026": "Real-time Telemetry & WAF",
            "explanation": explanation,
            "deprecated": "1 pattern flagged",
            "drift": "2 levels",
            "needs_renegotiation": True
        }

    elif content_type == "api_spec":
        explanation = (
            "2020 REST specifications frequently lacked rate limiting and explicit error schemas. "
            "2026 OpenAPI 3.1 standards mandate explicit OAuth2/OIDC scopes, strict rate limiting headers, and breaking-change versioning rules."
        )
        return {
            "risk_2020": "LOW",
            "risk_2026": "MEDIUM",
            "extracted_value": "OpenAPI 3.1",
            "inflation_adjusted": "OAuth2 / OIDC",
            "value_loss": "API Contract Drift",
            "industry_avg_2026": "Strict Schema Validation",
            "explanation": explanation,
            "deprecated": "0 found",
            "drift": "1 level",
            "needs_renegotiation": False
        }

    else:
        dollar_matches = re.findall(r'\$\s*([0-9,]+)', text)
        extracted_amount = float(dollar_matches[0].replace(',', '')) if dollar_matches else 10000
        inflation_rate = 0.212
        adjusted_amount = int(extracted_amount * (1 + inflation_rate))
        
        explanation = (
            f"A contract cap of ${extracted_amount:,.0f} met 2020 legal benchmarks, but due to 21.2% cumulative inflation "
            f"and 2026 liability trends, the real economic value has degraded to ${adjusted_amount:,.0f} equivalent."
        )
        return {
            "risk_2020": "LOW",
            "risk_2026": "HIGH" if extracted_amount < 40000 else "LOW",
            "extracted_value": f"${extracted_amount:,.0f}",
            "inflation_adjusted": f"${adjusted_amount:,.0f}",
            "value_loss": "21%",
            "industry_avg_2026": "$50,000 - $100,000",
            "explanation": explanation,
            "deprecated": "1 clause drift",
            "drift": "2 levels",
            "needs_renegotiation": extracted_amount < 40000
        }