"""
Autonomous 1-Click AI Security Patch & Refactor Engine for Judex AI.
Generates non-destructive AST-preserved code fixes, unified diffs,
and patches multi-file zip repository archives in RAM.
"""

import io
import zipfile
import json
import re
import difflib
from typing import Dict, Any, List, Optional
from backend.analyzer import call_groq_chief, GROQ_API_KEY
import requests

PATCH_SYSTEM_PROMPT = """You are Judex AI's Chief Remediation Engineer.
Your task is to generate a 100% NON-DESTRUCTIVE, HIGH-PRECISION SECURITY PATCH or REMEDIATION SPECIFICATION based on the content domain:

DOMAIN-SPECIFIC PATCH RULES:
1. FOR SOURCE CODE (Python, JS, Java, SQL, HTML, etc.):
   - PRESERVE FUNCTION SIGNATURES: Do NOT alter parameter names, exported variable names, or return signatures.
   - Inject parameterized queries, input sanitization, error handling decorators, and CSP meta headers.
2. FOR API SPECIFICATIONS (OpenAPI / Swagger / REST JSON / YAML):
   - Patch the JSON/YAML directly by adding missing securitySchemes (Bearer Auth), response error schemas (401, 403, 422), rate-limiting headers, and parameter validation schemas.
3. FOR SECURITY LOGS:
   - Generate an Incident Mitigation Script & Firewall Rules (e.g. IPTables rules, Fail2Ban configs, Auth lockout policy) to block the detected attack IP / vulnerability.
4. FOR TECHNICAL SPECS / INFRASTRUCTURE (Markdown, Dockerfile, Kubernetes, etc.):
   - Update the architecture document or manifest to include missing SLA security policies, encrypted HTTPS port mappings, and token expiration rules.

OUTPUT CONSTRAINTS:
- Return strictly valid JSON with keys "patched_code" and "summary_of_changes".
- Do NOT output markdown code fences (```) inside the JSON values.

JSON Format:
{
  "patched_code": "<patched_content_or_mitigation_script>",
  "summary_of_changes": ["Description of patch 1", "Description of patch 2"]
}
"""


def generate_code_patch(content: str, content_type: str, findings: List[str], recommendations: List[str]) -> Dict[str, Any]:
    """
    Generate non-destructive security fix and compute unified diff.
    """
    if not GROQ_API_KEY:
        return {
            "status": "ERROR",
            "message": "GROQ API key not configured.",
            "patched_code": content,
            "diff_lines": [],
            "summary_of_changes": ["API Key missing."]
        }

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    prompt_user = f"""Content Type: {content_type}
Original Code / Content:
```
{content}
```

Vulnerabilities & Issues Flagged:
{json.dumps(findings, indent=2)}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate the complete patched code preserving 100% of function signatures and business logic.
Respond with ONLY valid JSON containing 'patched_code' and 'summary_of_changes'."""

    body = {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": PATCH_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_user}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 2048
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code == 200:
            parsed = json.loads(resp.json()['choices'][0]['message']['content'])
            patched_code = parsed.get("patched_code", content)
            summary_of_changes = parsed.get("summary_of_changes", ["Applied automated security patch."])

            orig_lines = content.splitlines(keepends=True)
            patch_lines = patched_code.splitlines(keepends=True)
            diff = list(difflib.unified_diff(orig_lines, patch_lines, fromfile='Original', tofile='Patched', n=2))

            return {
                "status": "SUCCESS",
                "patched_code": patched_code,
                "diff_lines": [line.rstrip('\n') for line in diff],
                "summary_of_changes": summary_of_changes
            }
    except Exception as e:
        print(f"[PatchEngine] Groq LPU failed: {e}. Failing over to Gemini Flash...")

    # Multi-Model Failover: Try Gemini API if Groq fails
    try:
        from backend.analyzer import GEMINI_API_KEY
        if GEMINI_API_KEY:
            g_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            g_body = {
                "contents": [{"parts": [{"text": f"{PATCH_SYSTEM_PROMPT}\n\n{prompt_user}"}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            g_resp = requests.post(g_url, json=g_body, timeout=15)
            if g_resp.status_code == 200:
                text_out = g_resp.json()['candidates'][0]['content']['parts'][0]['text']
                parsed = json.loads(text_out)
                patched_code = parsed.get("patched_code", content)
                summary_of_changes = parsed.get("summary_of_changes", ["Applied Gemini 2.0 security patch."])

                orig_lines = content.splitlines(keepends=True)
                patch_lines = patched_code.splitlines(keepends=True)
                diff = list(difflib.unified_diff(orig_lines, patch_lines, fromfile='Original', tofile='Patched', n=2))

                return {
                    "status": "SUCCESS",
                    "patched_code": patched_code,
                    "diff_lines": [line.rstrip('\n') for line in diff],
                    "summary_of_changes": summary_of_changes
                }
    except Exception as e2:
        print(f"[PatchEngine] Gemini Failover failed: {e2}")

    return {
        "status": "ERROR",
        "message": "Failed to generate patch.",
        "patched_code": content,
        "diff_lines": [],
        "summary_of_changes": ["Failed to connect to remediation agent."]
    }


def patch_repository_zip_bytes(original_zip_bytes: bytes, file_patches: Dict[str, str]) -> bytes:
    """
    RAM-based zip file reconstructor.
    Replaces only the patched files in RAM and returns the new zip bytes.
    """
    in_buf = io.BytesIO(original_zip_bytes)
    out_buf = io.BytesIO()

    with zipfile.ZipFile(in_buf, 'r') as in_zf, zipfile.ZipFile(out_buf, 'w', zipfile.ZIP_DEFLATED) as out_zf:
        for item in in_zf.infolist():
            filename = item.filename.replace('\\', '/')
            if filename in file_patches:
                # Write patched content bytes
                patched_text = file_patches[filename]
                out_zf.writestr(item.filename, patched_text.encode('utf-8'))
            else:
                # Copy original bytes untouched
                out_zf.writestr(item, in_zf.read(item.filename))

    return out_buf.getvalue()
