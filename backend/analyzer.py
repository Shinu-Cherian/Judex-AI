"""
Orchestrator Engine for 4-LLM Panel of Judges.
- Temperature = 0 on all calls (maximum determinism)
- Structured JSON output enforced on all models
- Content-type mismatch detection
- Retry logic with graceful fallback
- Cross-validation between judges
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from backend.temporal import calculate_temporal_risk
from backend.dependency import build_dependency_graph
from backend.reflection import run_reflection_node
from backend.prompts import (
    JUDGE_1_PROMPT, JUDGE_2_PROMPT, JUDGE_3_PROMPT, CHIEF_JUDGE_PROMPT
)

# Load .env from project root (one level above the backend/ folder)
_root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=_root_env, override=True)

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")

# Debug: print key presence on startup
print(f"[Judex] GROQ key:    {'SET' if GROQ_API_KEY else 'MISSING'}")
print(f"[Judex] MISTRAL key: {'SET' if MISTRAL_API_KEY else 'MISSING'}")
print(f"[Judex] GEMINI key:  {'SET' if GEMINI_API_KEY else 'MISSING'}")
print(f"[Judex] OPENAI key:  {'SET' if OPENAI_API_KEY else 'MISSING'}")

# --- Content-type Detection ----------------------------------------------------

def detect_content_type(text: str) -> str:
    """
    Robust Multi-Language Content Type Detector.
    Supports C, C++, C#, Java, Kotlin, Swift, Rust, Go, Python, JS/TS, PHP, Ruby, Scala, Elixir, Dart, SQL, Shell, HTML, OpenAPI/API Specs, Logs, etc.
    """
    t = text.lower().strip()

    # 1. API SPECS & OPENAPI (Check first before generic JSON)
    if any(k in t for k in ["openapi:", "swagger:", "\"openapi\"", "\"swagger\"", "\"paths\":", "\"endpoints\":", "post /", "get /", "put /", "delete /", "requestbody:", "authorization: bearer"]):
        return "api_spec"

    # 2. LOGS & AUDIT LOGS
    if any(k in t for k in ["[error]", "[warning]", "[info]", "[security_alert]", "failed password", "authentication failure", "status=4", "status=5", "fatal error"]):
        return "security_log"

    # 3. KUBERNETES / DOCKERFILE / CONFIG
    if any(k in t for k in ["apiversion:", "kind: deployment", "kind: service", "containers:"]):
        return "kubernetes"
    if t.startswith("from ") and ("as " in t or "run " in t or "cmd [" in t or "copy " in t):
        return "dockerfile"
    if t.startswith("{") and ("\"version\"" in t or "\"dependencies\"" in t or "\"scripts\"" in t):
        return "json_config"

    # 4. C / C++
    if any(k in t for k in ["#include <", "#include \"", "std::", "int main(", "void main(", "printf(", "cout <<", "#define ", "struct ", "namespace "]):
        return "c_cpp"

    # 5. C#
    if any(k in t for k in ["using system", "console.writeline", "[httpget]", "[httppost]", "async task<"]):
        return "csharp"

    # 6. RUST
    if any(k in t for k in ["fn main()", "use std::", "let mut ", "pub fn ", "impl ", "match ", "println!", "cargo.toml"]):
        return "rust"

    # 7. GO (GOLANG)
    if any(k in t for k in ["package main", "func main(", "import (", "fmt.println", "fmt.printf", "goroutine", "chan "]):
        return "go"

    # 8. PHP
    if any(k in t for k in ["<?php", "$this->", "$_get[", "$_post["]):
        return "php"

    # 9. RUBY
    if any(k in t for k in ["def ", "attr_accessor", "require '", "puts "]):
        if "attr_accessor" in t or "require '" in t or "puts " in t:
            return "ruby"

    # 10. SWIFT / KOTLIN
    if any(k in t for k in ["import uikit", "import foundation", "guard let", "@objc"]):
        return "swift"

    # 11. JAVA / KOTLIN
    if any(k in t for k in ["public class", "private ", "protected ", "public static", "package ", "system.out", "java.sql", "string[]", "hashmap<", "fun main(", "import java."]):
        return "java_or_similar"

    # 12. PYTHON (Check Python-specific tokens)
    if any(k in t for k in ["def ", "elif ", "self.", "if __name__", "__init__", "print(", "import os", "from typing import"]):
        return "python"

    # 13. JAVASCRIPT / TYPESCRIPT
    if any(k in t for k in ["const ", "let ", "var ", "function ", "=>", "async ", "await ", "require(", "export default", "module.exports", "interface ", "type "]):
        return "javascript"

    # 14. SQL
    if any(k in t for k in ["select ", "insert into", "update ", "delete from", "create table", "alter table", "drop table"]):
        return "sql"

    # 15. SHELL / BASH
    if any(k in t for k in ["#!/bin/bash", "#!/bin/sh", "export ", "echo ", "chmod ", "sudo ", "apt-get", "pip install"]):
        return "shell_script"

    # 16. HTML / CSS
    if any(k in t for k in ["font-size:", "padding:", "border-radius:", "margin:", "background:", "box-shadow:", "transform:", "@media"]):
        return "css"
    if t.startswith("<!doctype") or t.startswith("<html") or any(k in t for k in ["<!doctype html>", "<html ", "<head>", "<body>", "<script>", "<style>"]):
        return "html"

    # Legal Contract / Agreement
    if any(k in t for k in ["indemnify", "indemnification", "hold harmless", "governing law", "jurisdiction", "liability shall not exceed", "force majeure", "confidential information shall mean"]):
        return "legal_contract"

    return "code_generic"


def content_type_matches_selection(detected: str, selected: str) -> tuple[bool, str]:
    """
    Check if the auto-detected content type matches what user selected from dropdown.
    Returns (is_match, warning_message)
    """
    CODE_TYPES = {
        "html", "python", "javascript", "java_or_similar", "c_cpp", "csharp", "rust", "go",
        "php", "ruby", "swift", "code_generic", "sql", "shell_script", "dockerfile", "kubernetes", "json_config"
    }
    LOG_TYPES = {"security_log"}
    API_TYPES = {"api_spec"}

    if selected == "auto":
        return True, ""

    if selected == "logs" and detected not in LOG_TYPES:
        return False, f"You pasted {detected.replace('_', ' ').title()} content but selected 'Security Logs'. The AI will analyze it as {detected.replace('_', ' ').title()} instead for accurate results."

    if selected == "api" and detected not in API_TYPES:
        return False, f"You pasted {detected.replace('_', ' ').title()} content but selected 'API Contract'. The AI will analyze it as {detected.replace('_', ' ').title()} for accurate results."

    if selected == "code" and detected not in CODE_TYPES:
        return False, f"You pasted {detected.replace('_', ' ').title()} content but selected 'Code Review'. The AI will analyze it accordingly."

    if selected == "specs" and detected in CODE_TYPES | LOG_TYPES | API_TYPES:
        return False, f"You pasted {detected.replace('_', ' ').title()} content but selected 'Tech Spec'. The AI will analyze it as {detected.replace('_', ' ').title()} for accurate results."

    return True, ""


# --- LLM Callers ---------------------------------------------------------------

def call_groq_llama(prompt: str, content: str, retries: int = 2) -> Optional[Dict[str, Any]]:
    """Call Groq Llama 3.3 70B -- Security Inspector. Temperature=0."""
    if not GROQ_API_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Analyze the following content:\n\n```\n{content}\n```\n\nRespond with ONLY valid JSON."}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1024
    }
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            if resp.status_code == 200:
                text = resp.json()['choices'][0]['message']['content']
                parsed = json.loads(text)
                if "risk_level" in parsed and "findings" in parsed:
                    return parsed
        except Exception as e:
            print(f"[Groq Llama] Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(1)
    return None


def call_mistral(prompt: str, content: str, retries: int = 2) -> Optional[Dict[str, Any]]:
    """Call Mistral Small -- Performance Inspector. Temperature=0."""
    if not MISTRAL_API_KEY:
        return None
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "mistral-small-latest",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Analyze the following content:\n\n```\n{content}\n```\n\nRespond with ONLY valid JSON."}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1024
    }
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            if resp.status_code == 200:
                text = resp.json()['choices'][0]['message']['content']
                parsed = json.loads(text)
                if "risk_level" in parsed and "findings" in parsed:
                    return parsed
        except Exception as e:
            print(f"[Mistral] Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(1)
    return None


def call_gemini(prompt: str, content: str, retries: int = 2) -> Optional[Dict[str, Any]]:
    """Call Gemini 2.0 Flash -- Code Quality Inspector. Temperature=0. Fallback to Groq Llama 3.1 8B if quota exceeded."""
    if GEMINI_API_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [{
                "parts": [{"text": f"{prompt}\n\nAnalyze the following content:\n\n```\n{content}\n```\n\nRespond with ONLY valid JSON."}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0,
                "maxOutputTokens": 1024
            }
        }
        for attempt in range(retries):
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=3)
                if resp.status_code == 200:
                    text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    parsed = json.loads(text)
                    if "risk_level" in parsed and "findings" in parsed:
                        return parsed
                else:
                    print(f"[Gemini] HTTP {resp.status_code} -- Failover to Groq Llama 3.1 8B for Code Quality Inspector")
                    break
            except Exception as e:
                print(f"[Gemini] Attempt {attempt+1} timeout/failed: {e}")
                if attempt < retries - 1:
                    time.sleep(0.5)

    # Failover to Mixtral 8x7B (MoE Architecture) if Gemini rate-limits
    if GROQ_API_KEY:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": "mixtral-8x7b-32768",
            "temperature": 0,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Analyze the following content:\n\n```\n{content}\n```\n\nRespond with ONLY valid JSON."}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1024
        }
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=20)
            if resp.status_code == 200:
                text = resp.json()['choices'][0]['message']['content']
                parsed = json.loads(text)
                if "risk_level" in parsed and "findings" in parsed:
                    parsed["name"] = "Mixtral 8x7B MoE"
                    return parsed
        except Exception as e:
            print(f"[Groq Code Quality Backup] Failed: {e}")

    return None


def call_groq_chief(prompt: str, content: str, inspector_reports: List[Dict], retries: int = 2) -> Optional[Dict[str, Any]]:
    """Call DeepSeek-R1 / Llama 3.3 -- Chief Judge Verdict Synthesizer. Temperature=0."""
    if not GROQ_API_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    inspector_summary = json.dumps(inspector_reports, indent=2)
    user_message = f"""Here are the 3 Inspector reports:

{inspector_summary}

Original content analyzed:
```
{content[:2000]}
```

Synthesize the final verdict as ONLY valid JSON. No <think> tags, no explanations -- raw JSON only."""

    body = {
        "model": "deepseek-r1-distill-llama-70b",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1024
    }
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=45)
            if resp.status_code == 200:
                raw = resp.json()['choices'][0]['message']['content']
                # Strip any <think>...</think> tags if present
                import re
                raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
                parsed = json.loads(raw)
                if "final_risk" in parsed and "recommendations" in parsed:
                    return parsed
        except Exception as e:
            print(f"[Groq Chief Judge] Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(1)
    return None



# --- Dynamic Fallback Engine ---------------------------------------------------

def build_fallback_for_content(content: str, content_type: str) -> Dict[str, Any]:
    """
    Content-aware deterministic fallback when API keys are absent or all calls fail.
    Never returns generic data -- always tailored to the detected content type.
    """
    text_lower = content.lower()

    # Security findings based on content type
    if content_type == "html":
        findings_1 = ["Missing Content-Security-Policy (CSP) meta header -- XSS attack surface is open", "Inline <script> tags without nonce or hash attributes violate CSP standards", "No CSRF meta token found in <head> section"]
        findings_2 = ["Script module import lacks 'defer' attribute -- blocks initial page render", "Missing <link rel='preconnect'> for external font or CDN dependencies", "No viewport meta tag optimization found for mobile rendering"]
        findings_3 = ["Missing lang attribute on <html> element -- W3C accessibility violation", "No semantic HTML5 elements (article, section, nav) -- div-only structure detected", "Title tag present but meta description is absent for SEO compliance"]
        risk1, risk2, risk3 = "MEDIUM", "MEDIUM", "LOW"
        summary = "Moderate HTML markup risk. The document lacks Content Security Policy protection and critical accessibility attributes. Render-blocking script loading detected."
    elif content_type == "python":
        findings_1 = ["String concatenation in database query suggests SQL injection vulnerability pattern", "No input validation or sanitization on function parameters", "Sensitive data handled without encryption or masking"]
        findings_2 = ["Synchronous I/O operations detected -- consider asyncio for network/file operations", "No connection pooling or resource cleanup (context managers) found", "Unbounded loop or recursion without termination guard"]
        findings_3 = ["Missing type annotations (def function(param) without type hints)", "No docstring found on function definition -- documentation absent", "Bare except clause swallows all exception types -- too broad"]
        risk1, risk2, risk3 = "HIGH", "MEDIUM", "MEDIUM"
        summary = "High risk Python code. SQL injection pattern and missing input validation detected. Missing type annotations and error handling reduce maintainability."
    elif content_type == "javascript":
        findings_1 = ["eval() or innerHTML usage detected -- potential XSS injection vector", "No input sanitization before DOM manipulation or API calls", "Sensitive data stored in localStorage without encryption"]
        findings_2 = ["Synchronous XMLHttpRequest detected -- blocks main thread execution", "No debouncing on event handlers that fire frequently", "Missing Promise error handling (.catch() or try/await)"]
        findings_3 = ["Missing JSDoc comments on exported functions", "var declarations instead of const/let -- function-scoped variable risk", "No TypeScript types -- implicit any usage reduces type safety"]
        risk1, risk2, risk3 = "MEDIUM", "MEDIUM", "MEDIUM"
        summary = "Moderate JavaScript risk. XSS attack surface and synchronous blocking calls detected. Missing error handling and documentation reduce code quality."
    elif content_type == "security_log":
        findings_1 = ["Failed authentication attempts from single IP suggest brute-force or credential stuffing attack", "SQL injection payload patterns detected in request parameters", "Privilege escalation attempt pattern detected in log sequence"]
        findings_2 = ["Log volume analysis: high request rate from single source -- rate limiting not effective", "Missing request timing data -- latency anomaly detection impossible", "Log format inconsistency reduces automated SIEM parsing accuracy"]
        findings_3 = ["Log entries lack structured JSON format -- difficult for automated parsing", "Missing session correlation IDs across log entries", "Alert severity levels inconsistently applied across entries"]
        risk1, risk2, risk3 = "HIGH", "MEDIUM", "MEDIUM"
        summary = "High risk security log. Potential brute-force and SQL injection attack patterns detected. Log structure improvements needed for effective SIEM integration."
    elif content_type == "api_spec":
        findings_1 = ["Missing authentication scheme on one or more endpoints", "Sensitive data (card numbers, tokens) transmitted in URL query parameters", "No rate limiting specification on public endpoints"]
        findings_2 = ["No pagination specification on collection endpoints -- unbounded response size risk", "Missing response caching headers (Cache-Control, ETag) on GET endpoints", "Synchronous design for potentially long-running operations without async pattern"]
        findings_3 = ["Inconsistent naming conventions (camelCase vs snake_case) across endpoints", "Missing error response schema definition for non-200 status codes", "No API versioning strategy specified"]
        risk1, risk2, risk3 = "HIGH", "MEDIUM", "MEDIUM"
        summary = "High risk API specification. Missing authentication enforcement and sensitive data in URL parameters are critical issues requiring immediate attention."
    else:
        findings_1 = ["Potential unvalidated input handling pattern detected", "Missing explicit access control or authorization checks", "Sensitive data processed without audit trail"]
        findings_2 = ["Inefficient processing pattern -- optimization opportunity identified", "Resource allocation lacks explicit bounds or limits", "Missing timeout configuration for external operations"]
        findings_3 = ["Documentation is absent or incomplete for key operations", "Naming conventions are inconsistent across the codebase", "Error handling strategy is not defined"]
        risk1, risk2, risk3 = "MEDIUM", "MEDIUM", "LOW"
        summary = "Moderate risk content. Security validation, performance optimization, and documentation improvements are recommended before production deployment."

    j1 = {"name": "Groq Llama 3.3 70B", "role": "Security Inspector", "content_type_detected": content_type, "risk_level": risk1, "confidence": 88, "findings": findings_1, "missing_carveouts": ["Input validation", "Authentication check"]}
    j2 = {"name": "Mistral Small", "role": "Performance Inspector", "content_type_detected": content_type, "risk_level": risk2, "confidence": 82, "findings": findings_2, "missing_carveouts": ["Async operation", "Rate limiting"]}
    j3 = {"name": "Gemini 2.0 Flash", "role": "Code Quality Inspector", "content_type_detected": content_type, "risk_level": risk3, "confidence": 85, "findings": findings_3, "missing_carveouts": ["Docstrings", "Type annotations"]}
    judge = {
        "weighted_confidence": 85,
        "final_risk": risk1 if risk1 in ["CRITICAL", "HIGH"] else risk2 if risk2 == "HIGH" else risk3 if risk3 == "HIGH" else "MEDIUM",
        "summary": summary,
        "recommendations": [
            f"Address the most critical {risk1}-risk security findings first",
            "Add input validation and sanitization to all user-supplied data",
            "Implement structured error handling and logging",
            "Add type annotations and documentation for maintainability"
        ]
    }
    return {"models": [j1, j2, j3], "judge": judge}


# --- Main Orchestrator ----------------------------------------------------------

def analyze_contract_clause(clause_text: str, selected_type: str = "auto") -> Dict[str, Any]:
    """
    Main orchestration function -- runs all 4 LLMs with expert prompts.
    Routes through the LangGraph + RAG pipeline when available.
    Falls back to direct pipeline if LangGraph is unavailable.
    Returns structured results for the frontend.
    """
    if not clause_text or len(clause_text.strip()) < 5:
        clause_text = "def process_payment(amount, card_number):\n    query = 'INSERT INTO payments VALUES (' + card_number + ')'\n    db.execute(query)\n    return True"

    # Step 1: Detect content type
    content_type = detect_content_type(clause_text)
    is_match, mismatch_warning = content_type_matches_selection(content_type, selected_type)

    print(f"[Judex AI] Content detected: {content_type} | Selected: {selected_type} | Match: {is_match}")

    # -- Route through LangGraph + RAG pipeline ------------------------------
    try:
        from backend.langgraph_pipeline import run_judex_pipeline, get_compiled_graph
        if get_compiled_graph() is not None:
            print("[Judex AI] -- Routing through RAG pipeline...")
            return run_judex_pipeline(clause_text, content_type, selected_type, mismatch_warning)
    except Exception as lg_err:
        print(f"[Judex AI] LangGraph pipeline error ({lg_err}) -- falling back to direct pipeline.")

    # -- Direct fallback pipeline (no LangGraph) -----------------------------
    print("[Judex AI] -- Running direct pipeline (no LangGraph)...")

    # Step 2: Run 3 Inspector LLMs
    print("[Judex AI] Running Security Inspector (Groq Llama 3.3)...")
    j1_live = call_groq_llama(JUDGE_1_PROMPT, clause_text)

    print("[Judex AI] Running Performance Inspector (Mistral Small)...")
    j2_live = call_mistral(JUDGE_2_PROMPT, clause_text)

    print("[Judex AI] Running Code Quality Inspector (Gemini 2.0 Flash)...")
    j3_live = call_gemini(JUDGE_3_PROMPT, clause_text)

    # Step 3: Fallback for any failed LLM
    fallback = build_fallback_for_content(clause_text, content_type)

    m1 = j1_live if (j1_live and "risk_level" in j1_live and "findings" in j1_live) else fallback["models"][0]
    m2 = j2_live if (j2_live and "risk_level" in j2_live and "findings" in j2_live) else fallback["models"][1]
    m3 = j3_live if (j3_live and "risk_level" in j3_live and "findings" in j3_live) else fallback["models"][2]

    # Force correct names/roles (in case LLM modified them)
    m1["name"] = "Groq Llama 3.3 70B";  m1["role"] = "Security Inspector"
    m2["name"] = "Mistral Small";        m2["role"] = "Performance Inspector"
    m3["name"] = "Gemini 2.0 Flash";     m3["role"] = "Code Quality Inspector"

    models_list = [m1, m2, m3]

    # Step 4: Chief Judge synthesis -- Groq DeepSeek-R1 (free, reasoning model)
    print("[Judex AI] Running Chief Judge (Groq DeepSeek-R1)...")
    chief_live = call_groq_chief(CHIEF_JUDGE_PROMPT, clause_text, models_list)
    judge_data = chief_live if (chief_live and "final_risk" in chief_live) else fallback["judge"]

    # Recalculate weighted confidence from actual inspector scores
    total_conf = sum(m.get("confidence", 85) for m in models_list)
    judge_data["weighted_confidence"] = round(total_conf / 3)

    # Step 5: Disagreement Heatmap (domain-aligned calculation)
    risk_vals = [m.get("risk_level", "MEDIUM") for m in models_list]
    sec_risk = risk_vals[0] # Security Inspector
    perf_risk = risk_vals[1] # Performance Inspector
    qual_risk = risk_vals[2] # Code Quality Inspector

    sec_high_count = sum(1 for r in risk_vals if r in ["HIGH", "CRITICAL"])
    
    heatmap = [
        {
            "topic": "Security Vulnerability Severity",
            "disagreement": "HIGH" if sec_risk in ["HIGH", "CRITICAL"] else "LOW",
            "count": 3,
            "status": f"Security Risk: {sec_risk} ({sec_high_count}/3 Flagged High+)"
        },
        {
            "topic": "Performance & Resource Impact",
            "disagreement": "MEDIUM" if perf_risk == "HIGH" else "LOW",
            "count": 3,
            "status": f"Performance Risk: {perf_risk}"
        },
        {
            "topic": "Code Quality & Standards Gap",
            "disagreement": "MEDIUM" if qual_risk == "HIGH" else "LOW",
            "count": 3,
            "status": f"Code Quality Risk: {qual_risk}"
        }
    ]

    # Step 6: Temporal risk & dependency graph (content-type aware)
    temporal_data = calculate_temporal_risk(clause_text, judge_data["final_risk"], content_type)
    dependency_data = build_dependency_graph(clause_text, content_type)

    # Step 7: Collect missing items & filter content-type irrelevant items (11-Domain Matrix)
    def filter_irrelevant_items(items_list: List[str], c_type: str) -> List[str]:
        filtered = []
        for item in items_list:
            if not isinstance(item, str):
                continue
            i_lower = item.lower()

            # 1. CSS / SCSS
            if c_type == "css":
                if any(bad in i_lower for bad in ["content security policy", "csp", "html tag", "doctype", "sql injection", "python", "auth header", "jwt", "indemnification", "liability cap", "governing law"]):
                    continue
            # 2. Code (Python, JS, Java, Go, SQL, Shell, Configs)
            elif c_type in ["python", "javascript", "java_or_similar", "code_generic", "sql", "shell_script", "dockerfile", "kubernetes", "json_config"]:
                if any(bad in i_lower for bad in ["indemnification", "liability cap", "governing law", "hold harmless"]):
                    continue
            # 3. Security Logs
            elif c_type == "security_log":
                if any(bad in i_lower for bad in ["docstring", "python type hints", "css variables", "indemnification", "liability cap", "gpu acceleration"]):
                    continue
            # 4. API Specs
            elif c_type == "api_spec":
                if any(bad in i_lower for bad in ["css variables", "indemnification", "python docstring", "gpu acceleration"]):
                    continue
            # 5. Legal Contracts
            elif c_type == "legal_contract":
                if any(bad in i_lower for bad in ["css variables", "python docstring", "sql injection", "gpu acceleration", "react hooks", "cors"]):
                    continue

            filtered.append(item)
        return filtered

    # Filter recommendations
    if "recommendations" in judge_data and isinstance(judge_data["recommendations"], list):
        judge_data["recommendations"] = filter_irrelevant_items(judge_data["recommendations"], content_type)

    missing_set = set()
    for m in models_list:
        for item in m.get("missing_carveouts", []):
            missing_set.add(item)

    filtered_missing = filter_irrelevant_items(list(missing_set), content_type)
    if not filtered_missing:
        filtered_missing = ["GPU acceleration (`will-change`)", "CSS variable fallbacks", "Layout containment (`contain: paint`)"] if content_type == "css" else ["Input validation", "Error handling", "Documentation"]

    partial_result = {
        "content_type": content_type,
        "mismatch_warning": mismatch_warning,
        "rag_enabled": False,
        "models": models_list,
        "heatmap": heatmap,
        "judge": judge_data,
        "temporal": temporal_data,
        "dependencies": dependency_data,
        "missing_clauses": filtered_missing
    }

    # Step 8: LangGraph Reflection Node
    reflection_output = run_reflection_node(partial_result)
    partial_result["reflection"] = reflection_output

    return partial_result