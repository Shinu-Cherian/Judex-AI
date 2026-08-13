"""
Hand-labeled benchmark set for the Judex AI evaluation harness (eval_harness.py).

Each case is a real code/API/log snippet paired with ground-truth issue tags
from a fixed taxonomy (ISSUE_TAG_KEYWORDS below). "Clean" cases (empty
expected_tags) exist specifically to measure false-positive / hallucination
rate, not just recall on vulnerable code.

Grading is keyword-based against ISSUE_TAG_KEYWORDS -- an approximation of
human labeling, not a perfect semantic grader. This is a standard, honest
trade-off for an automatable eval harness with no human-in-the-loop grading
step; see eval_harness.py's docstring for how the trade-off is handled.
"""

from typing import List, Dict, Any

# Fixed vocabulary of issue tags this harness can grade, and the keyword
# synonyms used to detect whether a piece of finding text is "about" that tag.
ISSUE_TAG_KEYWORDS: Dict[str, List[str]] = {
    "sql_injection": ["sql injection", "string concatenation", "parameteriz"],
    "hardcoded_secret": ["hardcoded", "hard-coded", "secret", "api key", "api_key"],
    "weak_hash": ["md5", "sha1", "weak hash", "insecure hash"],
    "xss": ["xss", "cross-site scripting", "innerhtml", "eval("],
    "command_injection": ["command injection", "shell=true", "os.system"],
    "missing_auth": ["missing auth", "no authentication", "authorization", "auth scheme"],
    "bare_except": ["bare except", "broad exception", "except:"],
}

BENCHMARK_CASES: List[Dict[str, Any]] = [
    # --- SQL injection ---
    {
        "id": "py-sqli-vuln-1", "content_type": "python", "expected_tags": ["sql_injection"],
        "code": "def get_user(user_id):\n    query = \"SELECT * FROM users WHERE id=\" + user_id\n    return db.execute(query)",
    },
    {
        "id": "py-sqli-clean-1", "content_type": "python", "expected_tags": [],
        "code": "def get_user(user_id):\n    query = \"SELECT * FROM users WHERE id=?\"\n    return db.execute(query, (user_id,))",
    },
    # --- Hardcoded secrets ---
    {
        "id": "py-secret-vuln-1", "content_type": "python", "expected_tags": ["hardcoded_secret"],
        "code": "API_SECRET = \"sk_live_51H8xyz1234567890abcdef\"\n\ndef call_api():\n    headers = {\"Authorization\": f\"Bearer {API_SECRET}\"}\n    return requests.get(\"https://api.example.com\", headers=headers)",
    },
    {
        "id": "py-secret-clean-1", "content_type": "python", "expected_tags": [],
        "code": "import os\nAPI_SECRET = os.environ[\"API_SECRET\"]\n\ndef call_api():\n    headers = {\"Authorization\": f\"Bearer {API_SECRET}\"}\n    return requests.get(\"https://api.example.com\", headers=headers)",
    },
    # --- Weak hashing ---
    {
        "id": "py-hash-vuln-1", "content_type": "python", "expected_tags": ["weak_hash"],
        "code": "import hashlib\n\ndef store_password(password):\n    hashed = hashlib.md5(password.encode()).hexdigest()\n    db.save(hashed)",
    },
    {
        "id": "py-hash-clean-1", "content_type": "python", "expected_tags": [],
        "code": "import bcrypt\n\ndef store_password(password):\n    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())\n    db.save(hashed)",
    },
    # --- XSS ---
    {
        "id": "js-xss-vuln-1", "content_type": "javascript", "expected_tags": ["xss"],
        "code": "function renderComment(comment) {\n  document.getElementById('feed').innerHTML = comment;\n}",
    },
    {
        "id": "js-xss-clean-1", "content_type": "javascript", "expected_tags": [],
        "code": "function renderComment(comment) {\n  document.getElementById('feed').textContent = comment;\n}",
    },
    # --- eval() ---
    {
        "id": "js-eval-vuln-1", "content_type": "javascript", "expected_tags": ["xss"],
        "code": "function runExpr(userInput) {\n  return eval(userInput);\n}",
    },
    {
        "id": "js-eval-clean-1", "content_type": "javascript", "expected_tags": [],
        "code": "function add(a, b) {\n  return a + b;\n}",
    },
    # --- Command injection ---
    {
        "id": "py-cmdi-vuln-1", "content_type": "python", "expected_tags": ["command_injection"],
        "code": "import subprocess\n\ndef backup(filename):\n    subprocess.call(\"tar -czf backup.tar.gz \" + filename, shell=True)",
    },
    {
        "id": "py-cmdi-clean-1", "content_type": "python", "expected_tags": [],
        "code": "import subprocess\n\ndef backup(filename):\n    subprocess.call([\"tar\", \"-czf\", \"backup.tar.gz\", filename], shell=False)",
    },
    # --- SQL raw text ---
    {
        "id": "sql-vuln-1", "content_type": "sql", "expected_tags": ["sql_injection"],
        "code": "SELECT * FROM accounts WHERE username = '\" + username + \"' AND password = '\" + password + \"'",
    },
    {
        "id": "sql-clean-1", "content_type": "sql", "expected_tags": [],
        "code": "SELECT id, username FROM accounts WHERE id = ? AND active = 1",
    },
    # --- API spec auth ---
    {
        "id": "api-vuln-1", "content_type": "api_spec", "expected_tags": ["missing_auth"],
        "code": "openapi: 3.1.0\npaths:\n  /users/{id}:\n    get:\n      summary: Get user by id\n      responses:\n        '200':\n          description: OK",
    },
    {
        "id": "api-clean-1", "content_type": "api_spec", "expected_tags": [],
        "code": "openapi: 3.1.0\npaths:\n  /users/{id}:\n    get:\n      summary: Get user by id\n      security:\n        - bearerAuth: []\n      responses:\n        '200':\n          description: OK\n        '401':\n          description: Unauthorized",
    },
    # --- Security log ---
    {
        "id": "log-vuln-1", "content_type": "security_log", "expected_tags": ["sql_injection"],
        "code": "[2026-08-10 03:14:02] [WARNING] GET /search?q=' OR 1=1 -- from 203.0.113.5\n[2026-08-10 03:14:03] [ERROR] Query failed: syntax error near 'OR'\n[2026-08-10 03:14:05] [WARNING] GET /search?q=UNION SELECT * FROM users-- from 203.0.113.5",
    },
    {
        "id": "log-clean-1", "content_type": "security_log", "expected_tags": [],
        "code": "[2026-08-10 09:00:01] [INFO] GET /dashboard 200 45ms user_id=8841\n[2026-08-10 09:00:04] [INFO] POST /api/save 200 112ms user_id=8841\n[2026-08-10 09:00:09] [INFO] GET /logout 200 12ms user_id=8841",
    },
    # --- Bare except ---
    {
        "id": "py-except-vuln-1", "content_type": "python", "expected_tags": ["bare_except"],
        "code": "def load_config(path):\n    try:\n        with open(path) as f:\n            return json.load(f)\n    except:\n        return {}",
    },
    {
        "id": "py-except-clean-1", "content_type": "python", "expected_tags": [],
        "code": "def load_config(path):\n    try:\n        with open(path) as f:\n            return json.load(f)\n    except FileNotFoundError:\n        return {}\n    except json.JSONDecodeError as e:\n        raise ValueError(f\"Invalid config: {e}\")",
    },
]
