"""
Judex AI Evaluation Harness.

Runs every case in eval_benchmark.py through the REAL analysis pipeline
(analyze_contract_clause -- the same function backend/main.py's /api/analyze
route calls) and grades the output against hand-labeled ground truth, using
a fixed issue-tag taxonomy (see eval_benchmark.ISSUE_TAG_KEYWORDS).

Metrics computed, per-tag and overall:
  - Recall:    of the issues that SHOULD have been flagged, how many were?
  - Precision: of the issues that WERE flagged, how many should have been?
  - F1:        harmonic mean of precision and recall.
  - Hallucination rate: the fraction of all flagged tag-claims that were
    false positives (flagged on a case whose ground truth didn't include
    that tag at all) -- a case-level proxy for how often the panel claims
    something that isn't there, complementary to (not a replacement for)
    the finding-level substring guard in analyzer.py.

Grading is keyword-based, not a human-graded semantic check -- an honest,
documented approximation given there's no human-in-the-loop grading step.
A finding is counted as "about" a tag if any of that tag's keyword synonyms
appears in the finding/summary/recommendation text (case-insensitive). This
mirrors the same style of substring-based verification already used by
analyzer.py's own hallucination guard, applied here at the eval level
instead of the per-finding level.

KNOWN GRADER LIMITATION (found from real run evidence, not theoretical):
this keyword grader is negation-blind. A model correctly stating "this code
is NOT vulnerable to SQL injection, it uses parameterized queries" contains
the same keywords ("sql injection") as a model incorrectly claiming SQL
injection IS present -- both get counted as a positive match on that tag.
Inspecting false_positive_evidence in a generated report shows this pattern
directly on several "clean" benchmark cases: the panel correctly identified
the code as safe, but the grader still counted it as a false positive
because the safety confirmation used the same vocabulary as a vulnerability
claim would. This means the measured hallucination_rate in a report is an
upper bound on the panel's actual false-claim rate, not a precise measure
of it -- some of what's counted as a "false positive" here is really the
panel correctly praising secure code. A v2 grader would need either
negation-aware phrase matching or an LLM-as-judge grading pass to separate
these two cases; this version does not attempt that.

Usage (from the project root, so the `backend` package resolves):
    python -m backend.eval_harness
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Set

from backend.eval_benchmark import BENCHMARK_CASES, ISSUE_TAG_KEYWORDS
from backend.analyzer import analyze_contract_clause

_REPORT_PATH = Path(__file__).parent / "eval_report.json"


def _collect_findings_text(result: Dict[str, Any]) -> str:
    """Concatenate every piece of text the pipeline produced for this case
    (all 3 inspectors' findings, the Chief Judge's summary + recommendations)
    into one lowercase blob to grade against."""
    parts: List[str] = []
    for model in result.get("models", []):
        parts.extend(model.get("findings", []))
    judge = result.get("judge", {})
    parts.append(judge.get("summary", ""))
    parts.extend(judge.get("recommendations", []))
    return " ".join(str(p) for p in parts).lower()


def _detected_tags(findings_text: str) -> Dict[str, str]:
    """Which fixed-vocabulary issue tags does this findings text touch on,
    and which specific keyword triggered each match (kept for auditability --
    a false positive is only meaningful to report if you can see exactly what
    text caused it)."""
    detected: Dict[str, str] = {}
    for tag, keywords in ISSUE_TAG_KEYWORDS.items():
        for kw in keywords:
            if kw in findings_text:
                detected[tag] = kw
                break
    return detected


def run_evaluation() -> Dict[str, Any]:
    # Match production: the RAG engine is normally initialized once by FastAPI's
    # startup lifespan hook (backend/main.py). A standalone script has no such
    # hook, so without this call every case would silently run with retrieval
    # skipped -- a materially different (weaker) pipeline than what's deployed.
    from backend.rag_engine import initialize_rag
    rag_ready = initialize_rag()
    print(f"[Eval] RAG engine ready: {rag_ready}")

    all_tags = set(ISSUE_TAG_KEYWORDS.keys())
    per_case_results: List[Dict[str, Any]] = []

    # Confusion counts, aggregated across all (case, tag) pairs
    tp = fp = fn = tn = 0
    per_tag_counts: Dict[str, Dict[str, int]] = {t: {"tp": 0, "fp": 0, "fn": 0, "tn": 0} for t in all_tags}

    start = time.time()
    for case in BENCHMARK_CASES:
        expected = set(case["expected_tags"])
        print(f"[Eval] Running case '{case['id']}' ({case['content_type']})...")

        case_start = time.time()
        result = analyze_contract_clause(case["code"], selected_type="auto")
        case_ms = round((time.time() - case_start) * 1000)
        # Small pacing delay -- back-to-back cases with no gap were tripping
        # Groq's per-minute rate limit on the larger Chief Judge model,
        # which looked like a broken model but was actually 429 throttling.
        time.sleep(3.5)

        findings_text = _collect_findings_text(result)
        detected_evidence = _detected_tags(findings_text)
        detected = set(detected_evidence.keys())

        case_tp = expected & detected
        case_fp = detected - expected
        case_fn = expected - detected
        case_tn = all_tags - expected - detected

        tp += len(case_tp); fp += len(case_fp); fn += len(case_fn); tn += len(case_tn)
        for t in case_tp: per_tag_counts[t]["tp"] += 1
        for t in case_fp: per_tag_counts[t]["fp"] += 1
        for t in case_fn: per_tag_counts[t]["fn"] += 1
        for t in case_tn: per_tag_counts[t]["tn"] += 1

        per_case_results.append({
            "id": case["id"],
            "content_type": case["content_type"],
            "expected_tags": sorted(expected),
            "detected_tags": sorted(detected),
            "true_positives": sorted(case_tp),
            "false_positives": sorted(case_fp),
            "false_negatives": sorted(case_fn),
            "false_positive_evidence": {t: detected_evidence[t] for t in case_fp},
            "correct": case_fp == set() and case_fn == set(),
            "pipeline_ms": case_ms,
        })

    total_ms = round((time.time() - start) * 1000)

    precision = round(tp / (tp + fp), 4) if (tp + fp) else None
    recall = round(tp / (tp + fn), 4) if (tp + fn) else None
    f1 = round(2 * precision * recall / (precision + recall), 4) if precision and recall and (precision + recall) else None
    hallucination_rate = round(fp / (tp + fp), 4) if (tp + fp) else 0.0
    cases_fully_correct = sum(1 for c in per_case_results if c["correct"])

    per_tag_report = {}
    for t, c in per_tag_counts.items():
        t_prec = round(c["tp"] / (c["tp"] + c["fp"]), 4) if (c["tp"] + c["fp"]) else None
        t_rec = round(c["tp"] / (c["tp"] + c["fn"]), 4) if (c["tp"] + c["fn"]) else None
        per_tag_report[t] = {**c, "precision": t_prec, "recall": t_rec}

    report = {
        "benchmark_size": len(BENCHMARK_CASES),
        "cases_fully_correct": cases_fully_correct,
        "cases_fully_correct_pct": round(cases_fully_correct / len(BENCHMARK_CASES) * 100, 1),
        "overall": {
            "true_positives": tp, "false_positives": fp, "false_negatives": fn, "true_negatives": tn,
            "precision": precision, "recall": recall, "f1": f1,
            "hallucination_rate": hallucination_rate,
        },
        "per_tag": per_tag_report,
        "per_case": per_case_results,
        "total_runtime_ms": total_ms,
    }

    _REPORT_PATH.write_text(json.dumps(report, indent=2))

    print("\n" + "=" * 60)
    print("JUDEX AI EVALUATION REPORT")
    print("=" * 60)
    print(f"Benchmark size:        {report['benchmark_size']} cases")
    print(f"Fully correct cases:   {cases_fully_correct}/{len(BENCHMARK_CASES)} ({report['cases_fully_correct_pct']}%)")
    print(f"Overall precision:     {precision}")
    print(f"Overall recall:        {recall}")
    print(f"Overall F1:            {f1}")
    print(f"Hallucination rate:    {hallucination_rate}  (false positives / all flagged tags)")
    print(f"Total runtime:         {total_ms}ms")
    print(f"Report written to:     {_REPORT_PATH}")
    print("=" * 60)

    return report


if __name__ == "__main__":
    run_evaluation()
