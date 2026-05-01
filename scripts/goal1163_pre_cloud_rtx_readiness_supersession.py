#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1163 pre-cloud RTX readiness supersession"
SCHEMA_VERSION = "goal1163_pre_cloud_rtx_readiness_supersession_v1"


def _source_commit() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode == 0:
        value = completed.stdout.strip()
        return value or None
    return None


ROWS: tuple[dict[str, object], ...] = (
    {
        "app": "database_analytics",
        "previous_goal1125_bucket": "local_optimization_first",
        "current_pre_cloud_status": "local_pre_cloud_complete_next_pod_batch",
        "rt_path": "OptiX compact summary for DB count/sum/group summaries",
        "local_remedy_goals": ("Goal1155", "Goal1156", "Goal1157"),
        "next_pod_action": "run real OptiX compact-summary batch with same-source artifact intake",
        "public_wording_status": "blocked_until_real_rtx_artifact_and_review",
    },
    {
        "app": "graph_analytics",
        "previous_goal1125_bucket": "local_optimization_first",
        "current_pre_cloud_status": "local_pre_cloud_complete_next_pod_batch",
        "rt_path": "OptiX graph ray traversal with raw row-view summary metadata",
        "local_remedy_goals": ("Goal1158", "Goal1159"),
        "next_pod_action": "run graph visibility/BFS/triangle gate and verify raw-view phase metadata",
        "public_wording_status": "blocked_until_real_rtx_artifact_and_review",
    },
    {
        "app": "road_hazard_screening",
        "previous_goal1125_bucket": "local_optimization_first",
        "current_pre_cloud_status": "local_pre_cloud_complete_next_pod_batch",
        "rt_path": "prepared OptiX segment/polygon compact hit-count summary",
        "local_remedy_goals": ("Goal1160",),
        "next_pod_action": "run road hazard native OptiX gate and verify summary no-row-materialization metadata",
        "public_wording_status": "blocked_until_real_rtx_artifact_and_review",
    },
    {
        "app": "hausdorff_distance",
        "previous_goal1125_bucket": "needs_larger_nontrivial_scale_contract",
        "current_pre_cloud_status": "local_pre_cloud_complete_next_pod_batch",
        "rt_path": "prepared OptiX fixed-radius Hausdorff threshold-decision traversal",
        "local_remedy_goals": ("Goal1161",),
        "next_pod_action": "run non-analytic Hausdorff threshold contract in OptiX mode",
        "public_wording_status": "blocked_until_real_rtx_artifact_and_review",
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "previous_goal1125_bucket": "local_optimization_first",
        "current_pre_cloud_status": "local_pre_cloud_complete_next_pod_batch",
        "rt_path": "OptiX LSI/PIP candidate discovery plus native exact bounded area continuation",
        "local_remedy_goals": ("Goal1162",),
        "next_pod_action": "rerun v2 polygon pair gate artifact with source/schema metadata",
        "public_wording_status": "blocked_until_real_rtx_artifact_and_review",
    },
    {
        "app": "polygon_set_jaccard",
        "previous_goal1125_bucket": "local_optimization_first",
        "current_pre_cloud_status": "local_pre_cloud_complete_next_pod_batch",
        "rt_path": "OptiX LSI/PIP candidate discovery plus native exact bounded Jaccard continuation",
        "local_remedy_goals": ("Goal1162",),
        "next_pod_action": "rerun v2 polygon Jaccard gate artifact with source/schema metadata",
        "public_wording_status": "blocked_until_real_rtx_artifact_and_review",
    },
)


def build_payload() -> dict[str, Any]:
    rows = [dict(row) for row in ROWS]
    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_commit": _source_commit(),
        "supersedes": "docs/reports/goal1125_unresolved_rtx_public_wording_prioritization_2026-04-29.md",
        "rows": rows,
        "summary": {
            "tracked_apps": len(rows),
            "local_pre_cloud_complete_next_pod_batch": sum(
                1 for row in rows if row["current_pre_cloud_status"] == "local_pre_cloud_complete_next_pod_batch"
            ),
            "public_wording_authorized": 0,
        },
        "valid": (
            len(rows) == 6
            and all(row["current_pre_cloud_status"] == "local_pre_cloud_complete_next_pod_batch" for row in rows)
            and all(row["public_wording_status"] == "blocked_until_real_rtx_artifact_and_review" for row in rows)
        ),
        "boundary": (
            "Goal1163 supersedes the stale Goal1125 pre-cloud prioritization state. "
            "It does not run cloud, does not authorize public RTX speedup wording, "
            "and does not mark release readiness. It only records that the local "
            "pre-cloud remedies for the six previously unresolved app rows are now "
            "complete enough for a consolidated pod batch."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1163 Pre-Cloud RTX Readiness Supersession",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- Tracked apps: {payload['summary']['tracked_apps']}",
        f"- Local pre-cloud complete for next pod batch: {payload['summary']['local_pre_cloud_complete_next_pod_batch']}",
        f"- Public wording authorized by this goal: {payload['summary']['public_wording_authorized']}",
        "",
        "## Rows",
        "",
        "| App | Previous Goal1125 Bucket | Current Status | RT Path | Remedy Goals | Next Pod Action | Public Wording |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {app} | {previous_goal1125_bucket} | {current_pre_cloud_status} | {rt_path} | {goals} | {next_pod_action} | {public_wording_status} |".format(
                app=row["app"],
                previous_goal1125_bucket=row["previous_goal1125_bucket"],
                current_pre_cloud_status=row["current_pre_cloud_status"],
                rt_path=row["rt_path"],
                goals=", ".join(row["local_remedy_goals"]),
                next_pod_action=row["next_pod_action"],
                public_wording_status=row["public_wording_status"],
            )
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1163 pre-cloud RTX readiness supersession.")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "docs/reports/goal1163_pre_cloud_rtx_readiness_supersession_2026-04-30.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=ROOT / "docs/reports/goal1163_pre_cloud_rtx_readiness_supersession_2026-04-30.md",
    )
    args = parser.parse_args(argv)
    payload = build_payload()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "output_json": str(args.output_json), "output_md": str(args.output_md)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
