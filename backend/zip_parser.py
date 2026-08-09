"""
In-Memory Zip Repository Parser & AST Filter for Judex AI.
Extracts project zip files in RAM without disk I/O, filters out build junk
(node_modules, .git, binaries), and ranks files by technical audit priority.
"""

import io
import os
import zipfile
import re
from typing import Dict, Any, List, Tuple

# Ignore non-code, binary, or heavy vendor directories
IGNORED_DIRS = {
    'node_modules', '.git', '.github', 'dist', 'build', '__pycache__',
    '.venv', 'venv', 'env', '.idea', '.vscode', 'coverage', '.next'
}

IGNORED_FILENAMES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'composer.lock',
    'poetry.lock', 'pipfile.lock', 'cargo.lock'
}

IGNORED_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.zip',
    '.tar', '.gz', '.7z', '.exe', '.dll', '.so', '.dylib', '.pyc',
    '.lock', '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4'
}

EXTENSION_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'javascript',
    '.tsx': 'javascript',
    '.css': 'css',
    '.scss': 'css',
    '.sql': 'sql',
    '.sh': 'shell_script',
    '.html': 'html',
    '.htm': 'html',
    '.json': 'json_config',
    'dockerfile': 'dockerfile',
    '.yaml': 'kubernetes',   # refined further in _detect_file_content_type()
    '.yml':  'kubernetes',   # refined further in _detect_file_content_type()
}


def _detect_file_content_type(file_path: str, content: str) -> str:
    """Detect content domain for an extracted file."""
    fname_lower = os.path.basename(file_path).lower()
    if fname_lower in ['dockerfile', 'dockerfile.dev', 'dockerfile.prod']:
        return 'dockerfile'
    if any(k in content.lower() for k in ['openapi', 'swagger', '"paths"', 'endpoints', 'requestbody']):
        return 'api_spec'
    if any(k in content.lower() for k in ['[security_alert]', '[failed password]', 'brute force', 'unauthorized access']):
        return 'security_log'

    # Refine YAML: distinguish Kubernetes from GitHub Actions / Docker Compose
    _, ext = os.path.splitext(fname_lower)
    if ext in ['.yaml', '.yml']:
        c_lower = content.lower()
        if any(k in c_lower for k in ['apiversion:', 'kind: deployment', 'kind: service', 'kind: pod', 'kind: ingress']):
            return 'kubernetes'
        elif any(k in c_lower for k in ['on:\n', 'jobs:\n', 'runs-on:', 'uses:', 'workflow_dispatch']):
            return 'shell_script'  # GitHub Actions → treat as script/config
        elif 'services:' in c_lower and 'image:' in c_lower:
            return 'dockerfile'   # Docker Compose
        else:
            return 'json_config'  # Generic YAML config

    return EXTENSION_MAP.get(ext, 'code_generic')


def _calculate_audit_priority(file_path: str, content: str, c_type: str) -> int:
    """
    Rank file audit priority (higher score = more critical to inspect first).
    Files containing routes, auth, database calls, or API specs get top priority.
    """
    score = 10
    c_lower = content.lower()

    # Route / Endpoint files
    if any(k in c_lower for k in ['@app.', 'router.', 'express()', 'app.post', 'app.get', 'fetch(', 'axios.']):
        score += 30
    # Auth / Secret / Token files
    if any(k in c_lower for k in ['auth', 'password', 'jwt', 'token', 'secret', 'session', 'login', 'bearer']):
        score += 35
    # Database / SQL files
    if any(k in c_lower for k in ['select ', 'insert into', 'update ', 'delete ', 'db.execute', 'query =', 'sqlalchemy', 'mongoose']):
        score += 25
    # Main entrypoints
    fname = os.path.basename(file_path).lower()
    if fname in ['main.py', 'app.py', 'server.js', 'index.js', 'app.js', 'dockerfile', 'api_spec.json']:
        score += 20

    # Short/empty files get lower score
    if len(content.strip()) < 30:
        score -= 15

    return max(1, score)


def parse_repository_zip(zip_bytes: bytes, zip_filename: str = "project.zip") -> Dict[str, Any]:
    """
    Extracts zip in memory and returns structured repository tree with prioritized files.
    """
    extracted_files: List[Dict[str, Any]] = []
    ignored_count = 0
    total_raw_files = 0

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            infolist = zf.infolist()
            total_raw_files = len(infolist)

            for member in infolist:
                # Skip directories
                if member.is_dir():
                    continue

                clean_path = member.filename.replace('\\', '/')
                path_parts = clean_path.split('/')

                # Check ignored directories
                if any(part.lower() in IGNORED_DIRS for part in path_parts[:-1]):
                    ignored_count += 1
                    continue

                fname = path_parts[-1]
                _, ext = os.path.splitext(fname.lower())

                # Check ignored extensions & filenames
                if fname.lower() in IGNORED_FILENAMES or ext in IGNORED_EXTS or fname.startswith('.'):
                    ignored_count += 1
                    continue

                # Read file content safely
                try:
                    raw_data = zf.read(member)
                    # Decode text files only
                    text_content = raw_data.decode('utf-8', errors='ignore')
                except Exception:
                    ignored_count += 1
                    continue

                if not text_content.strip() or len(text_content) > 500000:  # Skip empty or massive >500KB files
                    ignored_count += 1
                    continue

                content_type = _detect_file_content_type(clean_path, text_content)
                priority = _calculate_audit_priority(clean_path, text_content, content_type)

                # Extract top symbols (functions/classes)
                symbols = re.findall(r'(?:def|class|function)\s+([a-zA-Z0-9_]+)', text_content)

                extracted_files.append({
                    "path": clean_path,
                    "filename": fname,
                    "content": text_content,
                    "content_type": content_type,
                    "size_bytes": len(raw_data),
                    "line_count": len(text_content.splitlines()),
                    "priority": priority,
                    "symbols": symbols[:5],
                })

        # Sort extracted files by audit priority (highest priority first)
        extracted_files.sort(key=lambda x: x["priority"], reverse=True)

        print(f"[ZipParser] Parsed '{zip_filename}': {len(extracted_files)} files kept, {ignored_count} ignored out of {total_raw_files} total.")

        return {
            "zip_filename": zip_filename,
            "total_files_extracted": len(extracted_files),
            "total_files_ignored": ignored_count,
            "files": extracted_files,
        }

    except Exception as e:
        print(f"[ZipParser] Error extracting zip '{zip_filename}': {e}")
        return {
            "zip_filename": zip_filename,
            "error": f"Failed to extract zip file: {str(e)}",
            "total_files_extracted": 0,
            "files": [],
        }
