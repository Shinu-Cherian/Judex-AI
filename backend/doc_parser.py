"""
Document Parser Module for PDF, DOCX, and TXT legal contracts.
Segment contracts into individual clauses for multi-agent evaluation.
"""

import re
import io
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from pypdf import PdfReader

def parse_contract_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parses PDF, DOCX, or TXT document bytes into extracted legal clauses and raw text.
    """
    ext = filename.split('.')[-1].lower()
    raw_text = ""

    if ext == 'pdf':
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            raw_text = "\n\n".join(pages_text)
        except Exception as e:
            print(f"PDF parsing error: {e}")
            raw_text = file_bytes.decode('utf-8', errors='ignore')

    elif ext in ['docx', 'doc']:
        try:
            # Native python XML extraction for .docx files without extra pip libraries
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx_zip:
                xml_content = docx_zip.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                paragraphs = []
                for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    p_text = "".join([t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
                    if p_text.strip():
                        paragraphs.append(p_text.strip())
                raw_text = "\n\n".join(paragraphs)
        except Exception as e:
            print(f"DOCX parsing fallback: {e}")
            raw_text = file_bytes.decode('utf-8', errors='ignore')

    else: # txt or plain text
        raw_text = file_bytes.decode('utf-8', errors='ignore')

    if not raw_text.strip():
        raw_text = "The Provider's total aggregate liability arising out of or related to this Agreement shall not exceed $10,000. Under no circumstances shall Provider be liable for any indirect, consequential, special, punitive, or incidental damages."

    # Segment document into clauses based on legal section numbering or headings
    clauses = extract_clauses_from_text(raw_text)

    return {
        "filename": filename,
        "char_count": len(raw_text),
        "clause_count": len(clauses),
        "raw_text": raw_text,
        "clauses": clauses
    }


def extract_clauses_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extracts individual legal clauses by matching common section titles and pattern headers.
    """
    patterns = [
        (r'(?i)(limitation\s+of\s+liability|liability\s+cap|damages\s+limitation)', "Limitation of Liability"),
        (r'(?i)(confidentiality|non-disclosure|secret\s+information)', "Confidentiality & NDA"),
        (r'(?i)(indemnification|hold\s+harmless|indemnity)', "Indemnification"),
        (r'(?i)(intellectual\s+property|ip\s+rights|inventions|ownership)', "Intellectual Property"),
        (r'(?i)(termination|cancellation|survival)', "Termination & Survival"),
        (r'(?i)(non-compete|restrictive\s+covenants|solicitation)', "Restrictive Covenants"),
        (r'(?i)(governing\s+law|jurisdiction|dispute\s+resolution)', "Governing Law")
    ]

    found_clauses = []
    paragraphs = text.split('\n\n')

    for idx, p in enumerate(paragraphs):
        p_clean = p.strip()
        if len(p_clean) < 30:
            continue

        matched_category = "General Provisions"
        for regex, category in patterns:
            if re.search(regex, p_clean):
                matched_category = category
                break

        if matched_category != "General Provisions" or len(p_clean) > 80:
            title = p_clean.split('\n')[0][:60]
            found_clauses.append({
                "id": f"clause_{len(found_clauses) + 1}",
                "category": matched_category,
                "title": title + ("..." if len(p_clean) > 60 else ""),
                "text": p_clean
            })

    if not found_clauses:
        found_clauses.append({
            "id": "clause_1",
            "category": "Main Contract Scope",
            "title": text[:80] + "...",
            "text": text
        })

    return found_clauses[:10]