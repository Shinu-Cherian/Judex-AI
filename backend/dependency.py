"""
Multi-Domain Dependency Graph Engine
Maps dependencies across Code, HTML/DOM, CSS, APIs, Security Logs, and Legal Specs.
"""

import re
from typing import Dict, Any, List, Optional


def _extract_function_body(lines_raw: List[str], target_name: str) -> str:
    """
    Return just the target function/class's own body text (from its def/class
    line to the next top-level def/class at the same or shallower indentation),
    instead of the whole pasted file. Without this, a multi-function paste
    would misattribute one function's imports/behavior to a totally different
    function just because both happened to be in the same paste.
    """
    start_idx: Optional[int] = None
    base_indent = 0
    for i, line in enumerate(lines_raw):
        stripped = line.strip()
        if stripped.startswith(('def ', 'class ')) and target_name and target_name in stripped:
            start_idx = i
            base_indent = len(line) - len(line.lstrip())
            break
    if start_idx is None:
        return "\n".join(lines_raw)  # couldn't locate it -- fall back to the whole text

    body_lines = [lines_raw[start_idx]]
    for line in lines_raw[start_idx + 1:]:
        stripped = line.strip()
        if not stripped:
            body_lines.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent and stripped.startswith(('def ', 'class ')):
            break  # reached the next top-level function/class -- stop here
        body_lines.append(line)
    return "\n".join(body_lines)


def build_dependency_graph(clause_text: str, content_type: str = "code_generic") -> Dict[str, Any]:
    """
    Dynamically identifies connected dependencies based on the content type.
    """
    text = clause_text or ""
    t_lower = text.lower()

    nodes = []
    links = []
    affected_items = []

    # Detect primary target name
    lines_raw = text.split('\n')
    lines = [l.strip() for l in lines_raw if l.strip()]
    first_name = "target_input"
    for line in lines:
        if line.startswith(('def ', 'function ', 'class ')):
            parts = line.split()
            if len(parts) >= 2:
                first_name = parts[1].split('(')[0].split(':')[0].replace('()', '')
                break
        elif '<html' in line.lower() or '<!doctype' in line.lower():
            first_name = "index.html"
            break
        elif line.startswith(('.', '#', ':root', '@media')):
            first_name = line.split('{')[0].strip()
            break

    # Root node
    nodes.append({
        "id": "target_item",
        "label": first_name,
        "type": "target",
        "status": "ANALYZED"
    })

    if content_type in ["css"]:
        affected_items = [
            {"id": "dep_tokens", "name": "Design Tokens & CSS Variables (var(--accent))", "status": "STABLE", "reason": "Styles depend on active CSS custom properties and color tokens."},
            {"id": "dep_dom", "name": "HTML Component Class & ID Selectors", "status": "STABLE", "reason": "CSS rules bind directly to matching HTML component structure."},
            {"id": "dep_compositor", "name": "Browser Compositor & Render Pipeline", "status": "OPTIMIZED", "reason": "3D transforms promote element animations to dedicated GPU layers."}
        ]

    elif content_type in ["python", "javascript", "java_or_similar", "code_generic",
                           "c_cpp", "rust", "go", "csharp", "ruby", "php",
                           "sql", "shell_script", "dockerfile", "kubernetes", "json_config"]:
        # Scope dependency detection to the target function's OWN body, not the
        # whole pasted file -- otherwise a multi-function paste misattributes
        # one function's imports/behavior to a different function in the same file.
        scope_text = _extract_function_body(lines_raw, first_name) if first_name != "target_input" else text
        scope_lower = scope_text.lower()

        # Imports are usually declared at file-level (outside any function), so
        # collect all of them, but only keep ones actually referenced by name
        # inside the target function's own body.
        all_imports = list(dict.fromkeys(re.findall(r'(?:import|from|require)\s+([a-zA-Z0-9_\.\-]+)', text)))
        used_imports = [
            imp for imp in all_imports
            if re.search(r'\b' + re.escape(imp.split('.')[0]) + r'\b', scope_text)
        ]

        dep_list = []
        if used_imports:
            for imp in used_imports[:3]:
                dep_list.append({
                    "id": f"dep_{imp}",
                    "name": f"Module: {imp}",
                    "status": "DEPENDENCY OK",
                    "reason": f"External dependency imported by {first_name}."
                })

        # Only flag DB dependency when REAL database libraries or SQL patterns are present
        # (not just the word "query" which appears in FastAPI/HTTP route code)
        _db_imports = any(lib in scope_lower for lib in [
            "sqlalchemy", "psycopg2", "pymysql", "sqlite3", "pymongo",
            "motor", "tortoise", "asyncpg", "aiomysql", "databases",
            "db.execute", "db.query", "session.query", "cursor.execute",
            "connection.execute", "engine.execute"
        ])
        _sql_pattern = ("select " in scope_lower or "insert into" in scope_lower or
                        "update " in scope_lower or "delete from" in scope_lower or
                        "create table" in scope_lower)
        if _db_imports or _sql_pattern:
            dep_list.append({
                "id": "dep_db_driver",
                "name": "Database Connection Pool / ORM",
                "status": "MUST UPDATE",
                "reason": "Database queries depend on active connection pool and parameterized execution safety."
            })
        if ("http" in scope_lower or "fetch(" in scope_lower or "requests." in scope_lower
                or re.search(r'\bapi\b', scope_lower)):
            dep_list.append({
                "id": "dep_http_client",
                "name": "HTTP Client & TLS Handler",
                "status": "REVIEW NEEDED",
                "reason": "Network requests rely on timeout configuration and SSL certificate validation."
            })
        if "auth" in scope_lower or "token" in scope_lower or "password" in scope_lower or "secret" in scope_lower:
            dep_list.append({
                "id": "dep_auth_service",
                "name": "Authentication & Secrets Provider",
                "status": "MUST UPDATE",
                "reason": "Credential handling requires secure vault integration and zero-log policy."
            })

        if not dep_list:
            dep_list = [
                {"id": "dep_runtime", "name": "Runtime Engine & Environment", "status": "STABLE", "reason": "Standard execution environment dependency."},
                {"id": "dep_error_handler", "name": "Global Exception Handler", "status": "REVIEW NEEDED", "reason": "Uncaught errors ripple to top-level exception boundary."},
                {"id": "dep_logger", "name": "System Logger Module", "status": "STABLE", "reason": "Execution outputs depend on logger stream formatting."}
            ]

        affected_items = dep_list[:4]

    elif content_type in ["html"]:
        affected_items = [
            {"id": "dep_css", "name": "CSS Stylesheets & Assets", "status": "STABLE", "reason": "Visual rendering depends on stylesheet asset loads."},
            {"id": "dep_js", "name": "Script Modules & Bundles", "status": "MUST UPDATE", "reason": "Interactive DOM handlers require non-blocking script loading."},
            {"id": "dep_csp", "name": "Content Security Policy (CSP)", "status": "MUST UPDATE", "reason": "Markup security policy bounds inline script execution."}
        ]

    elif content_type in ["security_log"]:
        affected_items = [
            {"id": "dep_auth_server", "name": "Identity & Auth Gateway", "status": "ALERT", "reason": "Log anomalies signal potential breach at auth gateway."},
            {"id": "dep_firewall", "name": "WAF & Network Firewall", "status": "MUST UPDATE", "reason": "Suspicious IP patterns require immediate firewall rule updates."},
            {"id": "dep_siem", "name": "SIEM Alert Pipeline", "status": "REVIEW NEEDED", "reason": "Log format must match SIEM ingestion pattern."}
        ]

    elif content_type in ["api_spec"]:
        affected_items = [
            {"id": "dep_auth_header", "name": "OAuth2 / JWT Gateway", "status": "MUST UPDATE", "reason": "API endpoint authorization depends on token verification middleware."},
            {"id": "dep_db_schema", "name": "Database Schema Model", "status": "REVIEW NEEDED", "reason": "Response payloads map to underlying database schema definitions."},
            {"id": "dep_rate_limiter", "name": "API Rate Limiter / Throttler", "status": "MUST UPDATE", "reason": "Public endpoints require active rate limiting rules."}
        ]

    else:
        affected_items = [
            {"id": "dep_spec_req", "name": "Core Specification Requirements", "status": "REVIEW NEEDED", "reason": "Implementation must comply with specified architectural requirements."},
            {"id": "dep_api_contract", "name": "API Interface Contract", "status": "MUST UPDATE", "reason": "Interface definitions must align across client and server implementations."},
            {"id": "dep_validation", "name": "Input Validation Pipeline", "status": "MUST UPDATE", "reason": "Data contracts rely on strict input validation boundaries."}
        ]

    for item in affected_items:
        nodes.append({
            "id": item["id"],
            "label": item["name"],
            "type": "dependent",
            "status": item["status"]
        })
        links.append({
            "source": "target_item",
            "target": item["id"],
            "label": item["status"]
        })

    return {
        "nodes": nodes,
        "links": links,
        "affected_clauses": affected_items,
        "ripple_count": len(affected_items)
    }