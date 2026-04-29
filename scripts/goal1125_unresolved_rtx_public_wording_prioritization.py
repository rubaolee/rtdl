#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


DATE = "2026-04-29"
GOAL = "Goal1125 unresolved RTX public-wording prioritization"
GOAL1060 = ROOT / "docs/reports/goal1060_post_goal1058_speedup_candidate_audit_2026-04-28.json"
GOAL1109 = ROOT / "docs/reports/goal1109_v1_rtx_readiness_status_after_baselines_2026-04-29.json"
GOAL1123 = ROOT / "docs/reports/goal1123_public_wording_review_after_goal1121_2026-04-29.json"


LOCAL_OPTIMIZATION_FIRST = "local_optimization_first"
NEEDS_BASELINE_REVIEW = "needs_same_scale_or_normalized_baseline_review"
NEEDS_SCALE_CONTRACT = "needs_larger_nontrivial_scale_contract"


APP_PLANS: dict[str, dict[str, str]] = {
    "robot_collision_screening": {
        "action_bucket": NEEDS_BASELINE_REVIEW,
        "priority": "p0",
        "why": (
            "Goal1121 gives a real RT-core prepared pose-flag path above the timing floor, "
            "but Goal1123 intentionally blocked public wording until a same-scale or explicitly "
            "accepted normalized baseline review exists."
        ),
        "next_local_action": (
            "Decide whether the 64M RTX versus 36M Embree normalized comparison is acceptable. "
            "If not, prepare a same-scale Embree/native baseline contract before the next pod."
        ),
        "pod_policy": "pod_after_baseline_review_decision",
    },
    "database_analytics": {
        "action_bucket": LOCAL_OPTIMIZATION_FIRST,
        "priority": "p1",
        "why": (
            "Both compact-summary RTX rows are slower than Embree compact-summary baselines in "
            "Goal1060, so another paid pod run would mostly remeasure known overhead."
        ),
        "next_local_action": (
            "Profile prepared DB compact-summary transfer and aggregation overhead; reduce "
            "Python row materialization before a broader RTX rerun."
        ),
        "pod_policy": "no_pod_until_code_or_contract_changes",
    },
    "graph_analytics": {
        "action_bucket": LOCAL_OPTIMIZATION_FIRST,
        "priority": "p1",
        "why": (
            "Goal1060 shows the graph visibility RTX gate slower than the Embree graph-ray "
            "baseline, and graph bookkeeping phases are not cleanly separated enough for wording."
        ),
        "next_local_action": (
            "Split RT traversal timing from BFS/triangle bookkeeping and reduce host-side frontier "
            "or set-intersection overhead before retesting on RTX."
        ),
        "pod_policy": "no_pod_until_phase_split_or_code_changes",
    },
    "road_hazard_screening": {
        "action_bucket": LOCAL_OPTIMIZATION_FIRST,
        "priority": "p1",
        "why": (
            "The prepared road-hazard RTX summary is far slower than the same-semantics Embree "
            "summary in Goal1060."
        ),
        "next_local_action": (
            "Root-cause segment/polygon batching and summary-return overhead; keep claim scope to "
            "the prepared compact summary gate."
        ),
        "pod_policy": "no_pod_until_code_or_batching_changes",
    },
    "polygon_pair_overlap_area_rows": {
        "action_bucket": LOCAL_OPTIMIZATION_FIRST,
        "priority": "p2",
        "why": (
            "The native-assisted RTX candidate-discovery phase loses badly to the PostGIS "
            "same-unit-cell contract in Goal1060."
        ),
        "next_local_action": (
            "Fix candidate discovery/chunking and exact-area handoff. Public wording can only cover "
            "candidate discovery unless exact-area refinement becomes native."
        ),
        "pod_policy": "no_pod_until_candidate_chunking_changes",
    },
    "polygon_set_jaccard": {
        "action_bucket": LOCAL_OPTIMIZATION_FIRST,
        "priority": "p2",
        "why": (
            "The native-assisted RTX Jaccard candidate phase is slower than the Embree candidate "
            "baseline in Goal1060."
        ),
        "next_local_action": (
            "Fix Jaccard candidate discovery/chunking and document that exact set-area/Jaccard "
            "refinement remains CPU/Python-owned until a native reducer exists."
        ),
        "pod_policy": "no_pod_until_candidate_chunking_changes",
    },
    "hausdorff_distance": {
        "action_bucket": NEEDS_SCALE_CONTRACT,
        "priority": "p2",
        "why": (
            "The current threshold-decision RTX row is real but too small/trivial; Goal1060 compares "
            "it against a microsecond CPU oracle and flags it as rejected."
        ),
        "next_local_action": (
            "Define a larger nontrivial directed-threshold decision contract and dry-run correctness "
            "locally before spending pod time."
        ),
        "pod_policy": "no_pod_until_scale_contract_changes",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _goal1060_rows_by_app() -> dict[str, list[dict[str, Any]]]:
    payload = _load_json(GOAL1060)
    rows: dict[str, list[dict[str, Any]]] = {}
    for row in payload["rows"]:
        rows.setdefault(row["app"], []).append(row)
    return rows


def _support_row(app: str, goal1060_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    wording = rt.rtx_public_wording_status(app)
    readiness = rt.optix_app_benchmark_readiness(app)
    maturity = rt.rt_core_app_maturity(app)
    performance = rt.optix_app_performance_support(app)
    plan = APP_PLANS[app]
    evidence_rows = goal1060_rows.get(app, [])
    rejected_rows = [
        row for row in evidence_rows
        if row.get("recommendation") == "reject_current_public_speedup_claim"
    ]
    candidate_rows = [
        row for row in evidence_rows
        if row.get("recommendation") == "candidate_for_separate_2ai_public_claim_review"
    ]
    return {
        "app": app,
        "public_wording_status": wording.status,
        "readiness_status": readiness.status,
        "rt_core_status": maturity.current_status,
        "performance_class": performance.performance_class,
        "allowed_claim": readiness.allowed_claim,
        "current_boundary": wording.boundary,
        "action_bucket": plan["action_bucket"],
        "priority": plan["priority"],
        "why": plan["why"],
        "next_local_action": plan["next_local_action"],
        "pod_policy": plan["pod_policy"],
        "goal1060_rejected_rows": [
            {
                "path_name": row["path_name"],
                "rtx_phase_sec": row["rtx_native_or_query_phase_sec"],
                "fastest_baseline": row["fastest_baseline"],
                "fastest_baseline_sec": row["fastest_baseline_sec"],
                "ratio_baseline_over_rtx": row["fastest_ratio_baseline_over_rtx"],
                "reason": row["reason"],
            }
            for row in rejected_rows
        ],
        "goal1060_candidate_rows": [
            {
                "path_name": row["path_name"],
                "rtx_phase_sec": row["rtx_native_or_query_phase_sec"],
                "fastest_baseline": row["fastest_baseline"],
                "fastest_baseline_sec": row["fastest_baseline_sec"],
                "ratio_baseline_over_rtx": row["fastest_ratio_baseline_over_rtx"],
                "warnings": row["warnings"],
            }
            for row in candidate_rows
        ],
    }


def build_audit() -> dict[str, Any]:
    wording = rt.rtx_public_wording_matrix()
    unresolved = sorted(
        app for app, row in wording.items()
        if row.status in {"public_wording_blocked", "public_wording_not_reviewed"}
    )
    goal1060_rows = _goal1060_rows_by_app()
    rows = [_support_row(app, goal1060_rows) for app in unresolved]
    bucket_counts: dict[str, int] = {}
    for row in rows:
        bucket_counts[row["action_bucket"]] = bucket_counts.get(row["action_bucket"], 0) + 1
    return {
        "goal": GOAL,
        "date": DATE,
        "inputs": [
            str(GOAL1060.relative_to(ROOT)),
            str(GOAL1109.relative_to(ROOT)),
            str(GOAL1123.relative_to(ROOT)),
            "rtdsl.rtx_public_wording_matrix()",
            "rtdsl.optix_app_benchmark_readiness_matrix()",
            "rtdsl.rt_core_app_maturity_matrix()",
        ],
        "summary": {
            "unresolved_nvidia_public_wording_apps": len(rows),
            "public_wording_blocked": sum(1 for row in rows if row["public_wording_status"] == "public_wording_blocked"),
            "public_wording_not_reviewed": sum(1 for row in rows if row["public_wording_status"] == "public_wording_not_reviewed"),
            "local_optimization_first": bucket_counts.get(LOCAL_OPTIMIZATION_FIRST, 0),
            "needs_same_scale_or_normalized_baseline_review": bucket_counts.get(NEEDS_BASELINE_REVIEW, 0),
            "needs_larger_nontrivial_scale_contract": bucket_counts.get(NEEDS_SCALE_CONTRACT, 0),
        },
        "rows": rows,
        "recommended_order": [
            "robot_collision_screening",
            "database_analytics",
            "graph_analytics",
            "road_hazard_screening",
            "hausdorff_distance",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ],
        "valid": (
            len(rows) == 7
            and {row["app"] for row in rows} == set(APP_PLANS)
            and bucket_counts.get(LOCAL_OPTIMIZATION_FIRST, 0) == 5
            and bucket_counts.get(NEEDS_BASELINE_REVIEW, 0) == 1
            and bucket_counts.get(NEEDS_SCALE_CONTRACT, 0) == 1
            and all(row["rt_core_status"] == "rt_core_ready" for row in rows)
            and all(row["readiness_status"] == "ready_for_rtx_claim_review" for row in rows)
        ),
        "boundary": (
            "Goal1125 is a prioritization audit only. It does not edit public wording, "
            "authorize speedup claims, start cloud resources, or release v1.0."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1125 Unresolved RTX Public-Wording Prioritization",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Recommended Order",
            "",
        ]
    )
    for app in payload["recommended_order"]:
        lines.append(f"- `{app}`")
    lines.extend(
        [
            "",
            "## Unresolved Rows",
            "",
            "| App | Status | Bucket | Priority | Performance class | Pod policy | Next action |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    by_app = {row["app"]: row for row in payload["rows"]}
    for app in payload["recommended_order"]:
        row = by_app[app]
        lines.append(
            f"| `{row['app']}` | `{row['public_wording_status']}` | `{row['action_bucket']}` | "
            f"`{row['priority']}` | `{row['performance_class']}` | `{row['pod_policy']}` | "
            f"{row['next_local_action']} |"
        )
    lines.extend(["", "## Evidence Notes", ""])
    for app in payload["recommended_order"]:
        row = by_app[app]
        lines.append(f"### `{app}`")
        lines.append("")
        lines.append(row["why"])
        lines.append("")
        if row["goal1060_rejected_rows"]:
            lines.append("Goal1060 rejected rows:")
            lines.append("")
            for evidence in row["goal1060_rejected_rows"]:
                lines.append(
                    f"- `{evidence['path_name']}`: RTX `{evidence['rtx_phase_sec']:.6f}s`, "
                    f"fastest baseline `{evidence['fastest_baseline']}` "
                    f"`{evidence['fastest_baseline_sec']:.6f}s`, "
                    f"ratio baseline/RTX `{evidence['ratio_baseline_over_rtx']:.6f}`."
                )
            lines.append("")
        if row["goal1060_candidate_rows"]:
            lines.append("Goal1060 candidate rows:")
            lines.append("")
            for evidence in row["goal1060_candidate_rows"]:
                lines.append(
                    f"- `{evidence['path_name']}`: RTX `{evidence['rtx_phase_sec']:.6f}s`, "
                    f"fastest baseline `{evidence['fastest_baseline']}` "
                    f"`{evidence['fastest_baseline_sec']:.6f}s`, "
                    f"ratio baseline/RTX `{evidence['ratio_baseline_over_rtx']:.6f}`; "
                    f"warnings `{evidence['warnings']}`."
                )
            lines.append("")
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1125 unresolved RTX public-wording prioritization audit.")
    parser.add_argument("--output-json", default="docs/reports/goal1125_unresolved_rtx_public_wording_prioritization_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1125_unresolved_rtx_public_wording_prioritization_2026-04-29.md")
    args = parser.parse_args(argv)

    payload = build_audit()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "valid": payload["valid"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
