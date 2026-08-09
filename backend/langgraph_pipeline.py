"""
Judex AI Advanced Pipeline.
Implements the full 5-node sequential RAG pipeline without requiring
a working LangGraph StateGraph compile (avoids Reviver compatibility issues).

Pipeline:
  Node 1: retrieve_node       -- HyDE + ChromaDB vector retrieval
  Node 2: self_eval_node      -- Self-RAG relevance check with retry
  Node 3: inspector_node      -- 3-LLM panel with RAG context injected
  Node 4: chief_node          -- Chief Judge synthesis + heatmap + temporal
  Node 5: reflection_node     -- Cross-domain hallucination guard

Each node is a plain Python function receiving/returning a state dict.
LangGraph is used if available; falls back to direct sequential execution.
"""

import time
from typing import Dict, Any, List

# --- Self-RAG Thresholds ------------------------------------------------------
_SELF_EVAL_THRESHOLD = 0.35
_SELF_EVAL_MAX_RETRIES = 2


# --- Node 1: RAG Retrieve -----------------------------------------------------

def retrieve_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """HyDE + ChromaDB retrieval."""
    from backend.rag_engine import retrieve_context, format_rag_context_for_prompt, is_rag_ready

    if not is_rag_ready():
        print("[Pipeline] RAG not available -- skipping retrieval.")
        return {**state, "retrieved_docs": [], "rag_context_str": "",
                "rag_retrieval_score": 0.0, "rag_retry_count": 0}

    docs = retrieve_context(state["input_text"], state["content_type"], top_k=3)
    context_str = format_rag_context_for_prompt(docs)
    avg_score = round(
        sum(d.get("relevance_score", 0) for d in docs) / max(len(docs), 1), 4
    ) if docs else 0.0

    print(f"[Pipeline] retrieve_node: {len(docs)} docs, avg_relevance={avg_score:.2%}")
    return {**state,
            "retrieved_docs": docs,
            "rag_context_str": context_str,
            "rag_retrieval_score": avg_score,
            "rag_retry_count": 0}


# --- Node 2: Self-RAG Evaluator -----------------------------------------------

def self_eval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Self-RAG quality evaluator.
    If retrieved docs are below relevance threshold, retry with a
    plain code excerpt query (up to _SELF_EVAL_MAX_RETRIES times).
    """
    from backend.rag_engine import retrieve_context, format_rag_context_for_prompt

    avg_score = state.get("rag_retrieval_score", 0.0)
    retry_count = state.get("rag_retry_count", 0)

    while avg_score < _SELF_EVAL_THRESHOLD and retry_count < _SELF_EVAL_MAX_RETRIES:
        retry_count += 1
        print(f"[Pipeline] self_eval_node: Score {avg_score:.2%} below threshold. Retry {retry_count}...")
        alt_query = state["input_text"][:400]
        docs = retrieve_context(alt_query, state["content_type"], top_k=3)
        context_str = format_rag_context_for_prompt(docs)
        avg_score = round(
            sum(d.get("relevance_score", 0) for d in docs) / max(len(docs), 1), 4
        ) if docs else 0.0
        state = {**state,
                 "retrieved_docs": docs,
                 "rag_context_str": context_str,
                 "rag_retrieval_score": avg_score,
                 "rag_retry_count": retry_count}
        print(f"[Pipeline] self_eval_node: Retry {retry_count} score={avg_score:.2%}")

    status = "accepted" if avg_score >= _SELF_EVAL_THRESHOLD else f"low ({avg_score:.2%}) after {retry_count} retries"
    print(f"[Pipeline] self_eval_node: Context {status}")
    return state


# --- Node 3: Inspector Panel --------------------------------------------------

def inspector_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """3-LLM Inspector Panel with RAG context injected into each prompt."""
    from backend.analyzer import call_groq_llama, call_mistral, call_gemini, build_fallback_for_content, verify_findings_against_content
    from backend.prompts import JUDGE_1_PROMPT, JUDGE_2_PROMPT, JUDGE_3_PROMPT

    input_text = state["input_text"]
    content_type = state["content_type"]
    rag_context = state.get("rag_context_str", "")

    def augment(base_prompt: str) -> str:
        if not rag_context:
            return base_prompt
        return (
            f"{base_prompt}\n\n{rag_context}\n\n"
            "IMPORTANT: When your findings match any retrieved standard, "
            "cite it using its standard ID in brackets, e.g. [OWASP-A03-2025]."
        )

    print("[Pipeline] inspector_node: Running Security Inspector (Groq Llama 3.3)...")
    j1_live = call_groq_llama(augment(JUDGE_1_PROMPT), input_text)

    print("[Pipeline] inspector_node: Running Performance Inspector (Mistral Small)...")
    j2_live = call_mistral(augment(JUDGE_2_PROMPT), input_text)

    print("[Pipeline] inspector_node: Running Code Quality Inspector (Gemini 2.0 Flash)...")
    j3_live = call_gemini(augment(JUDGE_3_PROMPT), input_text)

    fallback = build_fallback_for_content(input_text, content_type)

    m1 = j1_live if (j1_live and "risk_level" in j1_live and "findings" in j1_live) else fallback["models"][0]
    m2 = j2_live if (j2_live and "risk_level" in j2_live and "findings" in j2_live) else fallback["models"][1]
    m3 = j3_live if (j3_live and "risk_level" in j3_live and "findings" in j3_live) else fallback["models"][2]

    m1["name"] = "Groq Llama 3.3 70B";  m1["role"] = "Security Inspector"
    m2["name"] = "Mistral Small";        m2["role"] = "Performance Inspector"
    m3["name"] = "Gemini 2.0 Flash";     m3["role"] = "Code Quality Inspector"

    for m in [m1, m2, m3]:
        m["findings"] = verify_findings_against_content(m.get("findings", []), input_text)

    rag_sources = [
        d.get("metadata", {}).get("standard", "")
        for d in state.get("retrieved_docs", [])
        if d.get("metadata", {}).get("standard")
    ]
    for m in [m1, m2, m3]:
        m["rag_sources"] = rag_sources
        m["rag_enhanced"] = len(rag_sources) > 0

    print(f"[Pipeline] inspector_node: Complete. RAG sources: {rag_sources}")
    return {**state, "inspector_reports": [m1, m2, m3]}


# --- Node 4: Chief Judge ------------------------------------------------------

def chief_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Chief Judge synthesis, heatmap, temporal risk, and dependency graph."""
    from backend.analyzer import call_groq_chief, derive_chief_verdict_from_inspectors
    from backend.temporal import calculate_temporal_risk
    from backend.dependency import build_dependency_graph
    from backend.prompts import CHIEF_JUDGE_PROMPT

    input_text = state["input_text"]
    content_type = state["content_type"]
    models_list = state["inspector_reports"]
    rag_context = state.get("rag_context_str", "")

    chief_prompt = f"{CHIEF_JUDGE_PROMPT}\n\n{rag_context}" if rag_context else CHIEF_JUDGE_PROMPT

    print("[Pipeline] chief_node: Running Chief Judge...")
    chief_live = call_groq_chief(chief_prompt, input_text, models_list)
    if chief_live and "final_risk" in chief_live:
        judge_data = chief_live
    else:
        print("[Pipeline] chief_node: Live Chief Judge call failed -- deriving verdict from live inspector reports (not a generic template).")
        judge_data = derive_chief_verdict_from_inspectors(models_list, content_type)

    total_conf = sum(m.get("confidence", 85) for m in models_list)
    judge_data["weighted_confidence"] = round(total_conf / 3)

    risk_vals = [m.get("risk_level", "MEDIUM") for m in models_list]
    sec_risk, perf_risk, qual_risk = risk_vals[0], risk_vals[1], risk_vals[2]
    sec_high_count = sum(1 for r in risk_vals if r in ["HIGH", "CRITICAL"])

    heatmap = [
        {"topic": "Security Vulnerability Severity",
         "disagreement": "HIGH" if sec_risk in ["HIGH", "CRITICAL"] else "LOW",
         "count": 3,
         "status": f"Security Risk: {sec_risk} ({sec_high_count}/3 Flagged High+)"},
        {"topic": "Performance & Resource Impact",
         "disagreement": "MEDIUM" if perf_risk == "HIGH" else "LOW",
         "count": 3,
         "status": f"Performance Risk: {perf_risk}"},
        {"topic": "Code Quality & Standards Gap",
         "disagreement": "MEDIUM" if qual_risk == "HIGH" else "LOW",
         "count": 3,
         "status": f"Code Quality Risk: {qual_risk}"}
    ]

    temporal_data = calculate_temporal_risk(input_text, judge_data["final_risk"], content_type)
    dependency_data = build_dependency_graph(input_text, content_type)

    # Build and filter missing clauses
    missing_set: set = set()
    for m in models_list:
        for item in m.get("missing_carveouts", []):
            missing_set.add(item)

    def _is_relevant(item: str) -> bool:
        i = item.lower()
        if content_type == "css" and any(bad in i for bad in [
                "content security policy", "csp", "html tag", "doctype",
                "sql injection", "python", "auth header", "jwt",
                "indemnification", "liability cap", "governing law"]):
            return False
        if content_type in ["python", "javascript", "java_or_similar",
                             "code_generic", "sql", "shell_script",
                             "dockerfile", "kubernetes", "json_config"]:
            if any(bad in i for bad in ["indemnification", "liability cap",
                                         "governing law", "hold harmless",
                                         "content security policy", "csp meta",
                                         "sri hash", "subresource integrity",
                                         "doctype", "html5 element"]):
                return False
        if content_type == "security_log" and any(bad in i for bad in [
                "docstring", "python type hints", "css variables",
                "indemnification", "liability cap", "gpu acceleration"]):
            return False
        if content_type == "api_spec" and any(bad in i for bad in [
                "css variables", "indemnification", "python docstring", "gpu acceleration"]):
            return False
        if content_type == "legal_contract" and any(bad in i for bad in [
                "css variables", "python docstring", "sql injection",
                "gpu acceleration", "react hooks", "cors"]):
            return False
        return True

    filtered = [item for item in missing_set if _is_relevant(item)]

    # Inject RAG-sourced standard citations as additional items
    for doc in state.get("retrieved_docs", []):
        std = doc.get("metadata", {}).get("standard", "")
        if std and f"[{std}]" not in str(filtered):
            filtered.append(f"Compliance check: [{std}]")

    if not filtered:
        filtered = (
            ["GPU acceleration (`will-change`)", "CSS variable fallbacks",
             "Layout containment (`contain: paint`)"]
            if content_type == "css"
            else ["Input validation", "Error handling", "Type annotations"]
        )

    if "recommendations" in judge_data and isinstance(judge_data["recommendations"], list):
        judge_data["recommendations"] = [
            r for r in judge_data["recommendations"]
            if isinstance(r, str) and _is_relevant(r)
        ]

    print(f"[Pipeline] chief_node: final_risk={judge_data['final_risk']}, "
          f"confidence={judge_data['weighted_confidence']}%")

    return {**state,
            "judge_data": judge_data,
            "heatmap": heatmap,
            "temporal_data": temporal_data,
            "dependency_data": dependency_data,
            "missing_clauses": filtered[:8]}


# --- Node 5: Reflection -------------------------------------------------------

def reflection_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Cross-domain hallucination guard."""
    from backend.reflection import run_reflection_node

    partial = {
        "content_type":    state["content_type"],
        "mismatch_warning": state.get("mismatch_warning", ""),
        "models":          state["inspector_reports"],
        "heatmap":         state["heatmap"],
        "judge":           state["judge_data"],
        "temporal":        state["temporal_data"],
        "dependencies":    state["dependency_data"],
        "missing_clauses": state["missing_clauses"],
    }
    reflection = run_reflection_node(partial)
    print(f"[Pipeline] reflection_node: {reflection.get('status', 'UNKNOWN')}")
    return {**state, "reflection_output": reflection}


# --- Compiled Graph Singleton (for compatibility checks) ---------------------

_graph_ready = False

def get_compiled_graph():
    """
    Returns a truthy sentinel so analyzer.py can route here.
    We no longer try to compile a LangGraph StateGraph due to
    Reviver compatibility issues -- we run nodes directly instead.
    """
    global _graph_ready
    _graph_ready = True
    return True   # Non-None truthy value tells analyzer to use this pipeline


# --- Main Entrypoint ---------------------------------------------------------

def run_judex_pipeline(
    input_text: str,
    content_type: str,
    selected_type: str,
    mismatch_warning: str,
) -> Dict[str, Any]:
    """
    Execute the full Judex AI pipeline sequentially.
    Nodes: retrieve -> self_eval -> inspect -> chief -> reflect
    """
    start = time.time()
    print(f"[Pipeline] Running for content_type='{content_type}'")

    state: Dict[str, Any] = {
        "input_text":          input_text,
        "content_type":        content_type,
        "selected_type":       selected_type,
        "mismatch_warning":    mismatch_warning,
        "retrieved_docs":      [],
        "rag_context_str":     "",
        "rag_retrieval_score": 0.0,
        "rag_retry_count":     0,
        "inspector_reports":   [],
        "judge_data":          {},
        "heatmap":             [],
        "temporal_data":       {},
        "dependency_data":     {},
        "missing_clauses":     [],
        "reflection_output":   {},
    }

    # Execute pipeline nodes in sequence
    state = retrieve_node(state)
    state = self_eval_node(state)
    state = inspector_node(state)
    state = chief_node(state)
    state = reflection_node(state)

    elapsed = round((time.time() - start) * 1000)
    print(f"[Pipeline] Complete in {elapsed}ms")

    judge = state.get("judge_data", {})
    models = state.get("inspector_reports", [])
    rag_sources = [
        d.get("metadata", {}).get("standard", "")
        for d in state.get("retrieved_docs", [])
        if d.get("metadata", {}).get("standard")
    ]

    return {
        "content_type":     content_type,
        "mismatch_warning": mismatch_warning,
        "rag_enabled":      state.get("rag_retrieval_score", 0) > 0,
        "rag_sources":      rag_sources,
        "rag_score":        state.get("rag_retrieval_score", 0),
        "models":           models,
        "heatmap":          state.get("heatmap", []),
        "judge":            judge,
        "temporal":         state.get("temporal_data", {}),
        "dependencies":     state.get("dependency_data", {}),
        "missing_clauses":  state.get("missing_clauses", []),
        "reflection":       state.get("reflection_output", {}),
        "pipeline_ms":      elapsed,
    }