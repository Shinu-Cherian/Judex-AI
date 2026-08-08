"""
LangGraph Reflection Node Module
Validates the synthesized evaluation output before returning to ensure complete risk coverage,
confidence weighting accuracy, temporal context application, and dependency mapping.
"""

from typing import Dict, Any, List

def run_reflection_node(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates the analysis output against analytical safety criteria.
    """
    checks = []
    content_type = analysis_result.get("content_type", "code_generic")
    
    # Check 1: All 3 models executed
    models = analysis_result.get("models", [])
    has_3_models = len(models) >= 3
    checks.append({
        "check": "3-Model Panel Execution",
        "passed": has_3_models,
        "detail": f"{len(models)}/3 judge models evaluated content successfully."
    })
    
    # Check 2: Confidence scores included & weighted
    judge = analysis_result.get("judge", {})
    weighted_conf = judge.get("weighted_confidence", 0)
    has_confidence = weighted_conf > 0
    checks.append({
        "check": "Confidence-Weighted Consensus Applied",
        "passed": has_confidence,
        "detail": f"Synthesized weighted confidence calculated at {weighted_conf}%."
    })

    # Check 3: Temporal Risk Scoring applied
    temporal = analysis_result.get("temporal", {})
    has_temporal = bool(temporal.get("risk_2026"))
    checks.append({
        "check": "Temporal Context & Standards Drift Applied",
        "passed": has_temporal,
        "detail": f"2020 vs 2026 tech standards drift evaluated ({temporal.get('industry_avg_2026', '2026 standards')})."
    })

    # Check 4: Clause Dependencies mapped
    dependencies = analysis_result.get("dependencies", {})
    ripple_count = dependencies.get("ripple_count", 0)
    has_deps = ripple_count > 0
    type_label = "Code & Asset" if content_type in ["python", "javascript", "code_generic", "html"] else "System & Gateway"
    checks.append({
        "check": f"{type_label} Dependency Ripple Graph Mapped",
        "passed": has_deps,
        "detail": f"Identified {ripple_count} interconnected {type_label.lower()} dependencies."
    })

    # Check 5: Actionable Recommendations generated
    recs = judge.get("recommendations", [])
    has_recs = len(recs) >= 2
    checks.append({
        "check": "Actionable Risk Mitigation Recommendations",
        "passed": has_recs,
        "detail": f"Generated {len(recs)} prioritized mitigation recommendations."
    })

    all_passed = all(c["passed"] for c in checks)

    return {
        "validated": all_passed,
        "status": "PASSED & VALIDATED" if all_passed else "ATTENTION REQUIRED",
        "checks": checks
    }