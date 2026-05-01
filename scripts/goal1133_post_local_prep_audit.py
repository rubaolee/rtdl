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

import rtdsl as rt


GOAL = "Goal1133 post-local-prep RTX app audit"
DATE = "2026-04-29"


LOCAL_GOALS = (
    {
        "goal": "Goal1128",
        "apps": ("database_analytics",),
        "local_change": "Embree compact-summary wrappers remove row materialization from local DB summary baselines.",
        "reports": (
            "docs/reports/goal1128_embree_db_compact_summary_optimization_2026-04-29.md",
            "docs/reports/goal1128_two_ai_consensus_2026-04-29.md",
        ),
        "tests": ("tests/goal1128_embree_db_compact_summary_contract_test.py",),
        "cloud_next": "Rerun prepared DB compact-summary paths on RTX only as part of a consolidated pod batch.",
    },
    {
        "goal": "Goal1129",
        "apps": ("graph_analytics",),
        "local_change": "Graph app emits phase split for visibility query/materialization and postprocess stages.",
        "reports": (
            "docs/reports/goal1129_graph_phase_split_local_2026-04-29.md",
            "docs/reports/goal1129_two_ai_consensus_2026-04-29.md",
        ),
        "tests": ("tests/goal1129_graph_phase_split_contract_test.py",),
        "cloud_next": "Rerun visibility-edge RTX path after phase split; do not claim BFS/triangle whole-app speedup.",
    },
    {
        "goal": "Goal1130",
        "apps": ("road_hazard_screening",),
        "local_change": "Native OptiX summary uses prepared threshold count instead of materializing hit-count rows.",
        "reports": (
            "docs/reports/goal1130_road_hazard_native_summary_count_path_2026-04-29.md",
            "docs/reports/goal1130_two_ai_consensus_2026-04-29.md",
        ),
        "tests": ("tests/goal1130_road_hazard_native_summary_count_test.py",),
        "cloud_next": "Collect real RTX summary timing; priority-segment id mode remains row-materializing.",
    },
    {
        "goal": "Goal1131",
        "apps": ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"),
        "local_change": "Polygon apps expose RT candidate discovery vs exact continuation phases; Jaccard adds summary output.",
        "reports": (
            "docs/reports/goal1131_polygon_app_phase_and_summary_contract_2026-04-29.md",
            "docs/reports/goal1131_two_ai_consensus_2026-04-29.md",
        ),
        "tests": ("tests/goal1131_polygon_app_phase_contract_test.py",),
        "cloud_next": "Measure OptiX LSI/PIP candidate discovery separately from exact CPU/native continuation.",
    },
    {
        "goal": "Goal1132",
        "apps": ("hausdorff_distance",),
        "local_change": "Hausdorff threshold and Embree directed-summary paths expose app-level phases.",
        "reports": (
            "docs/reports/goal1132_hausdorff_phase_contract_2026-04-29.md",
            "docs/reports/goal1132_two_ai_consensus_2026-04-29.md",
        ),
        "tests": ("tests/goal1132_hausdorff_phase_contract_test.py",),
        "cloud_next": "Treat Hausdorff as capability/phase evidence unless a non-analytic speed baseline is designed.",
    },
)


def _exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def _goal_row(item: dict[str, Any]) -> dict[str, Any]:
    missing_reports = [path for path in item["reports"] if not _exists(path)]
    missing_tests = [path for path in item["tests"] if not _exists(path)]
    app_states = []
    for app in item["apps"]:
        app_states.append(
            {
                "app": app,
                "readiness": rt.optix_app_benchmark_readiness(app).status,
                "maturity": rt.rt_core_app_maturity(app).current_status,
                "public_wording": rt.rtx_public_wording_status(app).status,
            }
        )
    return {
        "goal": item["goal"],
        "apps": list(item["apps"]),
        "local_change": item["local_change"],
        "reports": list(item["reports"]),
        "tests": list(item["tests"]),
        "missing_reports": missing_reports,
        "missing_tests": missing_tests,
        "app_states": app_states,
        "cloud_next": item["cloud_next"],
        "closed_locally": not missing_reports and not missing_tests,
    }


def build_audit() -> dict[str, Any]:
    rows = [_goal_row(item) for item in LOCAL_GOALS]
    tracked_apps = sorted({app for row in rows for app in row["apps"]})
    public_wording_boundary_respected = all(
        (
            rt.rtx_public_wording_status(app).status == "public_wording_reviewed"
            if app == "road_hazard_screening"
            else rt.rtx_public_wording_status(app).status == "public_wording_not_reviewed"
        )
        for app in tracked_apps
    )
    ready_for_review = all(
        rt.optix_app_benchmark_readiness(app).status == "ready_for_rtx_claim_review"
        and rt.rt_core_app_maturity(app).current_status == "rt_core_ready"
        for app in tracked_apps
    )
    all_goal_artifacts_present = all(row["closed_locally"] for row in rows)
    return {
        "goal": GOAL,
        "date": DATE,
        "rows": rows,
        "tracked_apps": tracked_apps,
        "summary": {
            "goal_count": len(rows),
            "tracked_app_count": len(tracked_apps),
            "all_goal_artifacts_present": all_goal_artifacts_present,
            "ready_for_review": ready_for_review,
            "public_wording_boundary_respected": public_wording_boundary_respected,
        },
        "valid": all_goal_artifacts_present and ready_for_review and public_wording_boundary_respected,
        "cloud_policy": (
            "The next pod should be one consolidated RTX run for changed paths only. "
            "Do not start/stop pods per app. Do not use these local changes as public "
            "RTX speedup claims without real RTX artifacts, same-semantics baselines, "
            "and 2-AI review."
        ),
        "boundary": (
            "Goal1133 is a local post-prep audit. It does not run cloud, tag, release, "
            "or authorize public RTX wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1133 Post-Local-Prep RTX App Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{str(payload['valid']).lower()}`",
        f"- goals checked: `{payload['summary']['goal_count']}`",
        f"- tracked apps: `{payload['summary']['tracked_app_count']}`",
        f"- all goal artifacts present: `{str(payload['summary']['all_goal_artifacts_present']).lower()}`",
        f"- ready for review: `{str(payload['summary']['ready_for_review']).lower()}`",
        f"- public wording boundary respected: `{str(payload['summary']['public_wording_boundary_respected']).lower()}`",
        "",
        "## Cloud Policy",
        "",
        payload["cloud_policy"],
        "",
        "## Rows",
        "",
        "| Goal | Apps | Local change | Closed locally | Cloud next |",
        "|---|---|---|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['goal']}` | `{', '.join(row['apps'])}` | {row['local_change']} | "
            f"`{str(row['closed_locally']).lower()}` | {row['cloud_next']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit post-local-prep RTX app readiness.")
    parser.add_argument("--output-json", default="docs/reports/goal1133_post_local_prep_audit_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1133_post_local_prep_audit_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(output_json), "md": str(output_md), "valid": payload["valid"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
