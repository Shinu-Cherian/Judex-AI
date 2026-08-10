"""
Advanced RAG Engine for Judex AI.
Implements:
  1. ChromaDB Vector Store -- 4-domain persistent collections
  2. Lightweight ONNX Embeddings (ChromaDB's bundled MiniLM, no PyTorch dependency)
  3. HyDE (Hypothetical Document Embeddings) -- boosts retrieval recall
  4. Hybrid Retrieval with relevance scoring

Architecture: Runs as a singleton -- initialized once at FastAPI startup.
"""

import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# -- Lazy imports (only loaded when RAG is active) -----------------------------
_chroma_client = None
_embed_fn = None
_collections: Dict[str, Any] = {}
_rag_ready = False

# -- Domain -> Collection Mapping -----------------------------------------------
DOMAIN_TO_COLLECTION = {
    "python":           "code_review",
    "javascript":       "code_review",
    "java_or_similar":  "code_review",
    "code_generic":     "code_review",
    "css":              "code_review",
    "sql":              "code_review",
    "shell_script":     "code_review",
    "dockerfile":       "code_review",
    "kubernetes":       "code_review",
    "json_config":      "code_review",
    "html":             "code_review",
    "tech_specs":       "tech_specs",
    "legal_contract":   "tech_specs",
    "api_spec":         "api_docs",
    "security_log":     "security_logs",
}

COLLECTION_NAMES = ["code_review", "tech_specs", "api_docs", "security_logs"]

# -- Persist Directory ----------------------------------------------------------
_CHROMA_PERSIST_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".judex_rag_db"
)


def _get_seed_hash() -> str:
    """Return a hash of the knowledge base to detect when re-seeding is needed."""
    try:
        from backend.rag_knowledge_base import ALL_DOMAIN_DOCS
        payload = json.dumps(ALL_DOMAIN_DOCS, sort_keys=True)
        return hashlib.md5(payload.encode()).hexdigest()[:12]
    except Exception:
        return "unknown"


def initialize_rag() -> bool:
    """
    Initialize ChromaDB, load embeddings model, seed knowledge base.
    Called once at application startup. Returns True if successful.
    """
    global _chroma_client, _embed_fn, _collections, _rag_ready

    if _rag_ready:
        return True

    try:
        import chromadb
        from chromadb.utils import embedding_functions

        print("[RAG] Initializing ChromaDB persistent client...")
        _chroma_client = chromadb.PersistentClient(path=_CHROMA_PERSIST_DIR)

        print("[RAG] Loading lightweight ONNX embedding model (avoids the full PyTorch/sentence-transformers footprint)...")
        _embed_fn = embedding_functions.DefaultEmbeddingFunction()

        # Create / get all 4 collections
        for name in COLLECTION_NAMES:
            _collections[name] = _chroma_client.get_or_create_collection(
                name=name,
                embedding_function=_embed_fn,
                metadata={"hnsw:space": "cosine"}
            )

        # Seed knowledge base if empty or stale
        _seed_if_needed()
        _rag_ready = True
        print("[RAG] RAG engine ready -- all 4 domain collections loaded.")
        return True

    except ImportError as e:
        print(f"[RAG] WARNING: ChromaDB/onnxruntime not installed: {e}. RAG disabled.")
        return False
    except Exception as e:
        print(f"[RAG] WARNING: Initialization failed: {e}. Continuing without RAG.")
        return False


def _seed_if_needed():
    """Seed knowledge base documents into ChromaDB collections."""
    global _collections

    # Check seed state via a fingerprint file
    fingerprint_path = Path(_CHROMA_PERSIST_DIR) / ".seed_fingerprint"
    current_hash = _get_seed_hash()

    if fingerprint_path.exists() and fingerprint_path.read_text().strip() == current_hash:
        print(f"[RAG] Knowledge base up-to-date (fingerprint: {current_hash}). Skipping re-seed.")
        return

    print(f"[RAG] Seeding knowledge base (fingerprint: {current_hash})...")

    try:
        from backend.rag_knowledge_base import ALL_DOMAIN_DOCS

        for collection_name, docs in ALL_DOMAIN_DOCS.items():
            collection = _collections.get(collection_name)
            if not collection or not docs:
                continue

            ids = [d["id"] for d in docs]
            texts = [d["text"] for d in docs]
            metadatas = [d["metadata"] for d in docs]

            # Upsert to handle re-seeding gracefully
            collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
            print(f"[RAG]   -> Seeded {len(docs)} documents into '{collection_name}'")

        # Write fingerprint
        fingerprint_path.parent.mkdir(parents=True, exist_ok=True)
        fingerprint_path.write_text(current_hash)
        print("[RAG] Knowledge base seeding complete.")

    except Exception as e:
        print(f"[RAG] WARNING: Seeding error: {e}")


def _generate_hyde_query(input_text: str, content_type: str) -> str:
    """
    HyDE (Hypothetical Document Embeddings):
    Generate a hypothetical 'ideal standard rule snippet' that closely resembles
    what a relevant security/performance guideline would look like for the given input.
    This bridges the semantic gap between code and text-based standard rules.
    """
    snippets = {
        "python":          "Python security best practice: use parameterized queries, async I/O, type annotations, specific exception handling.",
        "javascript":      "JavaScript ES2026 best practice: avoid eval/innerHTML XSS vectors, use const/let, async/await, sanitize DOM input.",
        "css":             "W3C CSS 2026 GPU acceleration: use will-change: transform, backface-visibility: hidden on 3D transforms, CSS variable fallbacks.",
        "sql":             "SQL security: parameterized prepared statements, index optimization, avoid SELECT *, prevent N+1 queries.",
        "shell_script":    "Shell script security: quote all variables, use set -euo pipefail, validate all input arguments, avoid eval.",
        "html":            "HTML5 security: Content-Security-Policy header, SRI hashes on CDN scripts, semantic elements, ARIA accessibility.",
        "dockerfile":      "Dockerfile security: non-root USER, pinned base image tags, multi-stage builds, no secrets in ENV.",
        "kubernetes":      "Kubernetes security: resource limits CPU/memory, Network Policies, no privileged containers, Pod Security Admission.",
        "security_log":    "Security log analysis: brute-force patterns, SQL injection signatures in logs, privilege escalation indicators, structured JSON format.",
        "api_spec":        "API security: OAuth2.1 Bearer token authentication, rate limiting, RFC 7807 error responses, CORS configuration.",
        "tech_specs":      "Architecture spec: single points of failure, circuit breakers, microservices DB-per-service, SLA 99.9% uptime.",
        "legal_contract":  "Compliance requirements: GDPR data minimization, SOC2 access controls, AES-256 encryption at rest, TLS 1.3.",
        "java_or_similar": "Java/Go/C# security: thread-safe code, access control enforcement, input validation, no raw SQL concatenation.",
        "code_generic":    "General code security: input validation, error handling, no hardcoded secrets, authentication and authorization checks.",
    }
    # Combine real code extract with a type-targeted hypothesis
    code_extract = input_text[:300].replace("\n", " ")
    hypothesis = snippets.get(content_type, snippets["code_generic"])
    return f"{hypothesis}\n\nCode context: {code_extract}"


def retrieve_context(
    input_text: str,
    content_type: str,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Main retrieval function.
    1. Generates a HyDE query for better semantic matching.
    2. Queries the appropriate ChromaDB collection.
    3. Returns top-k relevant standard documents with relevance scores.
    """
    global _rag_ready, _collections

    if not _rag_ready:
        return []

    collection_name = DOMAIN_TO_COLLECTION.get(content_type, "code_review")
    collection = _collections.get(collection_name)
    if not collection:
        return []

    try:
        # HyDE: Use a hypothetical standard document for query embedding
        hyde_query = _generate_hyde_query(input_text, content_type)

        results = collection.query(
            query_texts=[hyde_query],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if not results or not results.get("documents"):
            return []

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        for doc, meta, dist in zip(docs, metas, dists):
            # Convert cosine distance to similarity score (0-1, higher = more relevant)
            similarity = round(max(0.0, 1.0 - dist), 4)
            retrieved.append({
                "text": doc,
                "metadata": meta,
                "relevance_score": similarity,
            })

        # Filter out low-relevance documents (threshold: 0.3)
        retrieved = [r for r in retrieved if r["relevance_score"] >= 0.3]
        retrieved.sort(key=lambda x: x["relevance_score"], reverse=True)

        print(f"[RAG] Retrieved {len(retrieved)} relevant docs for '{content_type}' (collection: {collection_name})")
        return retrieved

    except Exception as e:
        print(f"[RAG] [WARN]  Retrieval error: {e}")
        return []


def format_rag_context_for_prompt(retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Format retrieved RAG documents into a structured block for LLM injection.
    """
    if not retrieved_docs:
        return ""

    lines = ["=== RELEVANT 2026 INDUSTRY STANDARDS (Retrieved from Knowledge Base) ==="]
    for i, doc in enumerate(retrieved_docs, 1):
        meta = doc.get("metadata", {})
        standard = meta.get("standard", "Industry Standard")
        score = doc.get("relevance_score", 0)
        text = doc.get("text", "")
        lines.append(f"\n[Standard {i}] [{standard}] (Relevance: {score:.0%})\n{text}")

    lines.append("\n=== END OF RETRIEVED STANDARDS ===")
    lines.append("You MUST cite the applicable standard ID (e.g., [OWASP-A03-2025]) in your findings when relevant.")
    return "\n".join(lines)


def is_rag_ready() -> bool:
    """Return whether the RAG engine has been successfully initialized."""
    return _rag_ready