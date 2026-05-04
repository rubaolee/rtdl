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


DATE = "2026-04-28"
GOAL = "Goal1063 pre-pod local completion audit"
GOAL1060 = ROOT / "docs/reports/goal1060_post_goal1058_speedup_candidate_audit_2026-04-28.json"
GOAL1062 = ROOT / "docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.json"


LOCAL_REMEDIATION: dict[tuple[str, str], dict[str, str]] = {
    ("database_analytics", "prepared_db_session_sales_risk"): {
        "local_next": "Profile and optimize the OptiX prepared DB compact-summary query path against Embree/PostgreSQL baselines before another pod run.",
        "pod_policy": "no_pod_until_code_or_scale_changes",
    },
    ("database_analytics", "prepared_db_session_regional_dashboard"): {
        "local_next": "Profile grouped dashboard aggregation and reduce Python/native transfer overhead before another pod run.",
        "pod_policy": "no_pod_until_code_or_scale_changes",
    },
    ("graph_analytics", "graph_visibility_edges_gate"): {
        "local_next": "Audit graph visibility/BFS/triangle RT mapping and separate RT traversal time from graph bookkeeping before another pod run.",
        "pod_policy": "no_pod_until_code_or_scale_changes",
    },
    ("road_hazard_screening", "road_hazard_native_summary_gate"): {
        "local_next": "Root-cause why Embree same-semantics summary is much faster; optimize segment/polygon OptiX native summary locally first.",
        "pod_policy": "no_pod_until_code_or_scale_changes",
    },
    ("polygon_pair_overlap_area_rows", "polygon_pair_overlap_optix_native_assisted_phase_gate"): {
        "local_next": "Fix native-assisted candidate discovery/chunking before rerun; current OptiX candidate phase is orders slower than PostGIS baseline.",
        "pod_policy": "no_pod_until_code_or_scale_changes",
    },
    ("polygon_set_jaccard", "polygon_set_jaccard_optix_native_assisted_phase_gate"): {
        "local_next": "Fix Jaccard candidate discovery/chunking and exact-area handoff before rerun; current OptiX candidate phase loses badly.",
        "pod_policy": "no_pod_until_code_or_scale_changes",
    },
    ("hausdorff_distance", "directed_threshold_prepared"): {
        "local_next": "Define a larger nontrivial threshold-decision scale where CPU oracle is not microsecond trivial, then validate dry-run semantics before pod.",
        "pod_policy": "no_pod_until_scale_contract_changes",
    },
    ("barnes_hut_force_app", "node_coverage_prepared"): {
        "local_next": "Define a larger Barnes-Hut node-coverage decision contract and avoid trivial CPU-baseline scale before pod.",
        "pod_policy": "no_pod_until_scale_contract_changes",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_audit() -> dict[str, Any]:
    wording = rt.rtx_public_wording_matrix()
    goal1060 = _load_json(GOAL1060)
    goal1062 = _load_json(GOAL1062)

    reviewed = sorted(app for app, row in wording.items() if row.status == "public_wording_reviewed")
    blocked = sorted(app for app, row in wording.items() if row.status == "public_wording_blocked")
    not_reviewed = sorted(app for app, row in wording.items() if row.status == "public_wording_not_reviewed")

    blocked_rows = [
        {
            "app": row["app"],
            "path_name": row["path_name"],
            "phase": row["phase"],
            "output_json": row["output_json"],
            "contains_skip_validation": row["contains_skip_validation"],
            "timing_floor_sec": row["timing_floor_sec"],
        }
        for row in goal1062["rows"]
        if row["app"] in blocked
    ]
    blocked_apps_in_manifest = sorted({row["app"] for row in blocked_rows})

    rejected_rows: list[dict[str, Any]] = []
    stale_candidates: list[dict[str, Any]] = []
    for row in goal1060["rows"]:
        key = (row["app"], row["path_name"])
        if row["recommendation"] == "reject_current_public_speedup_claim" and row["app"] not in reviewed:
            remediation = LOCAL_REMEDIATION.get(key)
            rejected_rows.append(
                {
                    "app": row["app"],
                    "path_name": row["path_name"],
                    "rtx_phase_sec": row["rtx_native_or_query_phase_sec"],
                    "fastest_baseline": row["fastest_baseline"],
                    "fastest_baseline_sec": row["fastest_baseline_sec"],
                    "ratio_baseline_over_rtx": row["fastest_ratio_baseline_over_rtx"],
                    "reason": row["reason"],
                    "local_next": remediation["local_next"] if remediation else "Add local remediation before any pod rerun.",
                    "pod_policy": remediation["pod_policy"] if remediation else "no_pod_until_local_plan_exists",
                }
            )
        elif row["recommendation"] == "candidate_for_separate_2ai_public_claim_review" and row["app"] not in reviewed:
            stale_candidates.append(
                {
                    "app": row["app"],
                    "path_name": row["path_name"],
                    "current_public_wording_status": row["current_public_wording_status"],
                    "warnings": row["warnings"],
                }
            )

    pod_ready_now = bool(blocked_rows) and blocked_apps_in_manifest == blocked and goal1062["valid"]
    local_only_blockers = [
        row for row in rejected_rows
        if row["pod_policy"].startswith("no_pod_until")
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "inputs": [
            str(GOAL1060.relative_to(ROOT)),
            str(GOAL1062.relative_to(ROOT)),
            "rtdsl.rtx_public_wording_matrix()",
        ],
        "summary": {
            "reviewed_public_wording_apps": len(reviewed),
            "blocked_public_wording_apps": len(blocked),
            "not_reviewed_public_wording_apps": len(not_reviewed),
            "rejected_current_speedup_rows": len(rejected_rows),
            "blocked_rows_ready_for_one_pod": len(blocked_rows),
            "local_only_blockers_before_broader_pod": len(local_only_blockers),
        },
        "reviewed_apps": reviewed,
        "blocked_apps": blocked,
        "not_reviewed_apps": not_reviewed,
        "pod_ready_now": pod_ready_now,
        "pod_ready_scope": (
            "No currently blocked public-wording rows from the current matrix are covered by the stale Goal1062 pod manifest. "
            "Do not rerun blocked or rejected not-reviewed rows on paid cloud until local analysis changes code, scale, or the rerun contract."
            if not blocked_rows
            else (
                "Only currently blocked Goal1062 validation plus large timing repeats are pod-ready now. "
                "Do not rerun rejected not-reviewed rows on paid cloud until their listed local work changes code or scale."
            )
        ),
        "goal1062_blocked_rows": blocked_rows,
        "rejected_rows_requiring_local_work": rejected_rows,
        "unreviewed_candidate_rows_requiring_goal1062_pod": stale_candidates,
        "valid": (
            len(reviewed) == 12
            and blocked == ["graph_analytics", "polygon_pair_overlap_area_rows"]
            and len(not_reviewed) == 2
            and len(rejected_rows) == 5
            and len(blocked_rows) == 0
            and not pod_ready_now
            and all(row["pod_policy"].startswith("no_pod_until") for row in rejected_rows)
        ),
        "boundary": (
            "Goal1063 is a local planning/audit artifact. It does not run a pod, "
            "change public wording, authorize release, or authorize speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1063 Pre-Pod Local Completion Audit",
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
            "## Pod-Ready Scope",
            "",
            payload["pod_ready_scope"],
            "",
            "### Goal1062 Rows",
            "",
            "| App | Path | Phase | Skip validation | Timing floor |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for row in payload["goal1062_blocked_rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | "
            f"`{row['contains_skip_validation']}` | `{floor}` |"
        )
    lines.extend(
        [
            "",
            "## Rejected Rows Requiring Local Work Before Broader Pod Use",
            "",
            "| App | Path | Ratio baseline/RTX | Fastest baseline | Pod policy | Local next |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for row in payload["rejected_rows_requiring_local_work"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | "
            f"`{row['ratio_baseline_over_rtx']:.6f}` | `{row['fastest_baseline']}` | "
            f"`{row['pod_policy']}` | {row['local_next']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1063 pre-pod local completion audit.")
    parser.add_argument("--output-json", default="docs/reports/goal1063_pre_pod_local_completion_audit_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1063_pre_pod_local_completion_audit_2026-04-28.md")
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
