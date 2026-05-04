#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1188 next RTX pod gap analysis"

APP_NEXT_ACTIONS: dict[str, dict[str, str]] = {
    "database_analytics": {
        "gap": "public wording not reviewed; latest DB compact-summary timing is just below the 0.1s review floor",
        "next_local": "prepare a larger same-contract DB compact-summary scale or repeat-count plan that clears the timing floor without changing semantics",
        "next_pod": "rerun compact_summary prepared warm-query with same-contract CPU/Embree baseline and enough work to exceed the public-review timing floor",
    },
    "polygon_set_jaccard": {
        "gap": "public wording not reviewed; chunked candidate discovery is bounded and exact Jaccard continuation remains separate",
        "next_local": "choose a stable chunk-size contract and same-contract candidate baseline; keep exact Jaccard outside the claim",
        "next_pod": "collect safe-chunk candidate-discovery timing with baseline and explicit chunk metadata",
    },
}

TIMING_ONLY_FOLLOWUPS: dict[str, dict[str, str]] = {
    "ann_candidate_search": {
        "status": "public wording reviewed for prepared candidate-coverage decision; Goal1184 ANN row is timing-only",
        "next_action": "do not promote Goal1184 ANN timing-only row; only rerun if a future claim needs same-contract oracle/baseline at larger scale",
    },
    "robot_collision_screening": {
        "status": "public wording reviewed only for normalized per-pose prepared pose flags; Goal1184 robot row is timing-only",
        "next_action": "do not promote Goal1184 robot timing-only row into same-total-work speedup; rerun only with normalized baseline contract if wording changes are requested",
    },
}


def build_analysis() -> dict[str, Any]:
    public_apps = rt.public_apps()
    rows: list[dict[str, Any]] = []
    for app in public_apps:
        maturity = rt.rt_core_app_maturity(app)
        wording = rt.rtx_public_wording_status(app)
        readiness = rt.optix_app_benchmark_readiness(app)
        perf = rt.optix_app_performance_support(app)
        if maturity.current_status == "not_nvidia_rt_core_target":
            bucket = "non_nvidia_target"
        elif wording.status == "public_wording_reviewed":
            bucket = "reviewed_wording"
        elif wording.status == "public_wording_not_reviewed":
            bucket = "needs_public_wording_evidence"
        elif wording.status == "public_wording_blocked":
            bucket = "blocked_public_wording"
        else:
            bucket = "other"
        rows.append(
            {
                "app": app,
                "rt_core_status": maturity.current_status,
                "public_wording_status": wording.status,
                "readiness_status": readiness.status,
                "performance_class": perf.performance_class,
                "bucket": bucket,
                "gap": APP_NEXT_ACTIONS.get(app, {}).get("gap", ""),
                "next_local": APP_NEXT_ACTIONS.get(app, {}).get("next_local", ""),
                "next_pod": APP_NEXT_ACTIONS.get(app, {}).get("next_pod", ""),
            }
        )
    needs_public_wording = [row for row in rows if row["bucket"] == "needs_public_wording_evidence"]
    reviewed = [row for row in rows if row["bucket"] == "reviewed_wording"]
    non_nvidia = [row for row in rows if row["bucket"] == "non_nvidia_target"]
    blockers: list[str] = []
    if len(needs_public_wording) != len(APP_NEXT_ACTIONS):
        blockers.append("unexpected needs-public-wording app count")
    missing_actions = [row["app"] for row in needs_public_wording if not row["next_local"] or not row["next_pod"]]
    if missing_actions:
        blockers.append(f"missing next action for: {', '.join(missing_actions)}")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not blockers,
        "public_app_count": len(public_apps),
        "rt_core_ready_count": sum(1 for row in rows if row["rt_core_status"] == "rt_core_ready"),
        "reviewed_public_wording_count": len(reviewed),
        "needs_public_wording_evidence_count": len(needs_public_wording),
        "non_nvidia_target_count": len(non_nvidia),
        "blocked_public_wording_count": sum(1 for row in rows if row["bucket"] == "blocked_public_wording"),
        "needs_public_wording_apps": [row["app"] for row in needs_public_wording],
        "timing_only_followups": TIMING_ONLY_FOLLOWUPS,
        "rows": rows,
        "blockers": blockers,
        "pod_recommendation": (
            "Do not spend another pod session until the two needs_public_wording_evidence "
            "apps have explicit same-contract baseline commands and timing-floor scale choices. "
            "The next pod should batch those two rows plus optional ANN/robot timing-only "
            "replacements only if their wording contract changes."
        ),
        "boundary": (
            "This is a planning/gap analysis only. It does not authorize public RTX speedup "
            "wording, release, tagging, or another pod run by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1188 Next RTX Pod Gap Analysis",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- public apps: `{payload['public_app_count']}`",
        f"- RT-core ready apps: `{payload['rt_core_ready_count']}`",
        f"- reviewed public wording apps: `{payload['reviewed_public_wording_count']}`",
        f"- apps needing public-wording evidence: `{payload['needs_public_wording_evidence_count']}`",
        f"- non-NVIDIA targets: `{payload['non_nvidia_target_count']}`",
        f"- blocked public wording apps: `{payload['blocked_public_wording_count']}`",
        "",
        "## Next Pod Recommendation",
        "",
        payload["pod_recommendation"],
        "",
        "## Apps Needing Evidence",
        "",
        "| App | Gap | Local prep before pod | Next pod row |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        if row["bucket"] != "needs_public_wording_evidence":
            continue
        lines.append(
            f"| `{row['app']}` | {row['gap']} | {row['next_local']} | {row['next_pod']} |"
        )
    lines.extend(["", "## Timing-Only Followups", "", "| App | Status | Next action |", "| --- | --- | --- |"])
    for app, item in payload["timing_only_followups"].items():
        lines.append(f"| `{app}` | {item['status']} | {item['next_action']} |")
    lines.extend(["", "## Full Matrix", "", "| App | RT-core | Public wording | Readiness | Perf class | Bucket |", "| --- | --- | --- | --- | --- | --- |"])
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['rt_core_status']}` | `{row['public_wording_status']}` | "
            f"`{row['readiness_status']}` | `{row['performance_class']}` | `{row['bucket']}` |"
        )
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in payload["blockers"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build next RTX pod gap analysis.")
    parser.add_argument("--output-json", default="docs/reports/goal1188_next_rtx_pod_gap_analysis_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1188_next_rtx_pod_gap_analysis_2026-04-30.md")
    args = parser.parse_args()

    payload = build_analysis()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "json": str(output_json), "md": str(output_md)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
