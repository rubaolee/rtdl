#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal971_post_goal969_baseline_speedup_review_package import build_package
import rtdsl as rt


GOAL = "Goal978 RTX speedup claim candidate audit"
DATE = "2026-04-26"

RTX_CANDIDATE = "candidate_for_separate_2ai_public_claim_review"
INTERNAL_ONLY = "internal_only_margin_or_scale"
REJECT = "reject_current_public_speedup_claim"
NEEDS_TIMING = "needs_timing_baseline_repair"
NEEDS_GRAPH_CORRECTNESS = "needs_graph_correctness_repair"
NOT_READY = "not_ready"

COMPARABLE_PHASE_KEYS = (
    "native_anyhit_query",
    "native_threshold_query",
    "native_query",
    "optix_query",
    "optix_query_sec",
    "cpu_reference_total_sec",
    "optix_candidate_discovery_sec",
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _positive_number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and float(value) > 0.0:
        return float(value)
    return None


def _comparable_phase_seconds(artifact: dict[str, Any]) -> tuple[str | None, float | None]:
    phases = artifact.get("phase_seconds", {})
    if not isinstance(phases, dict):
        return None, None
    for key in COMPARABLE_PHASE_KEYS:
        value = _positive_number(phases.get(key))
        if value is not None:
            return key, value
    return None, None


def _baseline_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    baselines = []
    for check in row.get("baseline_checks", ()):
        if check.get("status") != "valid":
            continue
        artifact = _load_json(check["path"])
        source_backend = str(artifact.get("source_backend", ""))
        if source_backend == "optix":
            # A self-comparison cannot support a speedup claim.
            continue
        phase_key, phase_sec = _comparable_phase_seconds(artifact)
        baselines.append(
            {
                "baseline": check.get("baseline"),
                "source_backend": source_backend,
                "path": check.get("path"),
                "phase_key": phase_key,
                "phase_sec": phase_sec,
                "correctness_parity": artifact.get("correctness_parity"),
                "claim_limit": artifact.get("claim_limit"),
            }
        )
    return baselines


def _classify(row: dict[str, Any], baselines: list[dict[str, Any]]) -> dict[str, Any]:
    rtx_sec = _positive_number(row.get("rtx_native_or_query_phase_sec"))
    valid_times = [b for b in baselines if b["phase_sec"] is not None]
    missing_times = [b for b in baselines if b["phase_sec"] is None]

    if row.get("app") == "graph_analytics":
        graph_audit = ROOT / "docs" / "reports" / "goal980_graph_baseline_correctness_audit_2026-04-26.json"
        if graph_audit.exists():
            payload = _load_json(graph_audit)
            if payload.get("status") == "blocked":
                return {
                    "recommendation": NEEDS_GRAPH_CORRECTNESS,
                    "reason": (
                        "Goal980 found CPU/Embree graph summary mismatches; graph speedup review is blocked "
                        "until native graph correctness is repaired and same-scale timings are recollected."
                    ),
                    "fastest_baseline": None,
                    "fastest_baseline_sec": None,
                    "fastest_ratio_baseline_over_rtx": None,
                    "warnings": ["Goal980 graph baseline correctness audit is blocked"],
                }

    if not row.get("baseline_complete_for_speedup_review") or row.get("rtx_artifact_status") != "ok":
        return {
            "recommendation": NOT_READY,
            "reason": "RTX artifact or same-semantics baseline set is not complete.",
            "fastest_baseline": None,
            "fastest_baseline_sec": None,
            "fastest_ratio_baseline_over_rtx": None,
            "warnings": [],
        }
    if rtx_sec is None:
        return {
            "recommendation": NEEDS_TIMING,
            "reason": "RTX artifact has no positive comparable query/native phase.",
            "fastest_baseline": None,
            "fastest_baseline_sec": None,
            "fastest_ratio_baseline_over_rtx": None,
            "warnings": [],
        }
    if not valid_times:
        return {
            "recommendation": NEEDS_TIMING,
            "reason": "No non-OptiX same-semantics baseline exposes a positive comparable phase.",
            "fastest_baseline": None,
            "fastest_baseline_sec": None,
            "fastest_ratio_baseline_over_rtx": None,
            "warnings": [f"{b['baseline']} lacks comparable timing" for b in missing_times],
        }

    fastest = min(valid_times, key=lambda item: float(item["phase_sec"]))
    fastest_sec = float(fastest["phase_sec"])
    ratio = fastest_sec / rtx_sec
    warnings: list[str] = []
    if rtx_sec < 0.01:
        warnings.append("RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.")
    if missing_times:
        warnings.extend(f"{b['baseline']} lacks comparable timing" for b in missing_times)

    if ratio >= 1.20:
        if missing_times:
            recommendation = INTERNAL_ONLY
            reason = (
                "RTX is faster than the fastest timed non-OptiX baseline, but at least one required "
                "baseline lacks comparable timing; repair timing before public claim review."
            )
        else:
            recommendation = RTX_CANDIDATE
            reason = (
                "RTX query/native phase is at least 20% faster than every timed non-OptiX "
                "same-semantics baseline; separate 2-AI review is still required."
            )
    elif ratio >= 1.0:
        recommendation = INTERNAL_ONLY
        reason = "RTX is not slower than the fastest baseline, but the margin is below the 20% candidate threshold."
    else:
        recommendation = REJECT
        reason = "RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence."

    return {
        "recommendation": recommendation,
        "reason": reason,
        "fastest_baseline": fastest["baseline"],
        "fastest_baseline_sec": fastest_sec,
        "fastest_ratio_baseline_over_rtx": ratio,
        "warnings": warnings,
    }


def build_audit() -> dict[str, Any]:
    source = build_package()
    rows: list[dict[str, Any]] = []
    for row in source["rows"]:
        baselines = _baseline_rows(row)
        decision = _classify(row, baselines)
        public_wording = rt.rtx_public_wording_status(str(row["app"]))
        rows.append(
            {
                "app": row["app"],
                "path_name": row["path_name"],
                "claim_scope": row.get("claim_scope"),
                "non_claim": row.get("non_claim"),
                "rtx_native_or_query_phase_sec": row.get("rtx_native_or_query_phase_sec"),
                "baseline_status": row.get("baseline_status"),
                "public_speedup_claim_authorized": False,
                "current_public_wording_status": public_wording.status,
                "current_public_wording_boundary": public_wording.boundary,
                "recommendation": decision["recommendation"],
                "reason": decision["reason"],
                "fastest_baseline": decision["fastest_baseline"],
                "fastest_baseline_sec": decision["fastest_baseline_sec"],
                "fastest_ratio_baseline_over_rtx": decision["fastest_ratio_baseline_over_rtx"],
                "warnings": decision["warnings"],
                "timed_non_optix_baselines": [
                    b for b in baselines if b["phase_sec"] is not None
                ],
                "untimed_non_optix_baselines": [
                    b for b in baselines if b["phase_sec"] is None
                ],
            }
        )

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["recommendation"]] = counts.get(row["recommendation"], 0) + 1

    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_package": "docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json",
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "row_count": len(rows),
        "recommendation_counts": counts,
        "public_speedup_claim_authorized_count": 0,
        "candidate_count": counts.get(RTX_CANDIDATE, 0),
        "needs_timing_repair_count": counts.get(NEEDS_TIMING, 0),
        "rows": rows,
        "boundary": (
            "Goal978 classifies RTX speedup-claim candidates after Goal836 reached 50/50 baseline readiness. "
            "It does not authorize public speedup claims; it only selects rows for later 2-AI claim review "
            "or identifies rows that need timing repair or rejection."
        ),
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal978 RTX Speedup Claim Candidate Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rows audited: `{payload['row_count']}`",
        f"- candidate rows for later 2-AI public-claim review: `{payload['candidate_count']}`",
        f"- rows needing timing repair: `{payload['needs_timing_repair_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        f"- recommendation counts: `{payload['recommendation_counts']}`",
        "",
        "## App/Path Decisions",
        "",
        "| App | Path | RTX phase (s) | Fastest non-OptiX baseline | Ratio | Recommendation |",
        "| --- | --- | ---: | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        baseline = row["fastest_baseline"] or ""
        ratio = row["fastest_ratio_baseline_over_rtx"]
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | {_fmt(row['rtx_native_or_query_phase_sec'])} | "
            f"`{baseline}` {_fmt(row['fastest_baseline_sec'])} | {_fmt(ratio)} | "
            f"`{row['recommendation']}` |"
        )

    lines.extend(["", "## Detail", ""])
    for row in payload["rows"]:
        lines.append(f"### {row['app']} / {row['path_name']}")
        lines.append("")
        lines.append(f"- recommendation: `{row['recommendation']}`")
        lines.append(f"- current public wording status: `{row['current_public_wording_status']}`")
        lines.append(f"- current public wording boundary: {row['current_public_wording_boundary']}")
        lines.append(f"- reason: {row['reason']}")
        lines.append(f"- public speedup authorized: `{row['public_speedup_claim_authorized']}`")
        if row["warnings"]:
            for warning in row["warnings"]:
                lines.append(f"- warning: {warning}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal978 RTX speedup claim candidate audit.")
    parser.add_argument("--output-json", default="docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.md")
    args = parser.parse_args(argv)

    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(to_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
