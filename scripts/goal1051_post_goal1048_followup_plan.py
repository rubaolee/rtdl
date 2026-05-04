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
from scripts.goal947_v1_rtx_app_status_page import CLAIM_COMMANDS


DATE = "2026-04-28"
GOAL = "Goal1051 post-Goal1048 follow-up plan"


def _claim_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    wording = rt.rtx_public_wording_matrix()
    readiness = rt.optix_app_benchmark_readiness_matrix()
    maturity = rt.rt_core_app_maturity_matrix()
    for app in rt.public_apps():
        ready = readiness[app]
        mature = maturity[app]
        public = wording[app]
        if ready.status == "exclude_from_rtx_app_benchmark":
            continue
        rows.append(
            {
                "app": app,
                "readiness": ready.status,
                "rt_core_status": mature.current_status,
                "public_wording": public.status,
                "allowed_claim": ready.allowed_claim,
                "non_claim": ready.blocker,
                "cloud_policy": mature.cloud_policy,
                "claim_command": CLAIM_COMMANDS[app],
            }
        )
    return rows


def build_plan() -> dict[str, Any]:
    rows = _claim_rows()
    diagnostic_reruns = [
        row
        for row in rows
        if row["app"] in {"facility_knn_assignment", "robot_collision_screening"}
    ]
    same_semantics_review = [
        row
        for row in rows
        if row["public_wording"] == "public_wording_not_reviewed"
    ]
    reviewed_keep = [
        row for row in rows if row["public_wording"] == "public_wording_reviewed"
    ]
    blocked = [
        row for row in rows if row["public_wording"] == "public_wording_blocked"
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": (
            len(rows) == 16
            and [row["app"] for row in diagnostic_reruns]
            == ["facility_knn_assignment", "robot_collision_screening"]
            and len(reviewed_keep) == 12
            and len(blocked) == 2
            and len(same_semantics_review) == 2
        ),
        "inputs": [
            "docs/reports/gemini_v1_0_project_foundational_review_2026-04-27.md",
            "docs/reports/gemini_v2_0_architectural_direction_compute_partnership_2026-04-27.md",
            "docs/reports/goal1050_two_ai_consensus_2026-04-28.md",
            "docs/v1_0_rtx_app_status.md",
            "docs/app_engine_support_matrix.md",
        ],
        "policy": (
            "Do not start paid cloud per app. Use one batched pod only after local "
            "manifest, validation commands, source commit traceability, and artifact "
            "copy-out paths are ready."
        ),
        "diagnostic_reruns": diagnostic_reruns,
        "same_semantics_review_needed": same_semantics_review,
        "reviewed_keep_as_is": reviewed_keep,
        "blocked_public_wording": blocked,
        "next_local_actions": [
            "Create a validation-enabled rerun manifest for facility_knn_assignment and robot_collision_screening.",
            "Package same-semantics baseline-review packets for public_wording_not_reviewed rows before stronger wording.",
            "Keep v1.0 app-first custom native paths as golden references for later v1.5 primitive extraction.",
            "Treat v2.0 compute partnership as future direction only; do not expand v1.0 scope into a magic Python compiler.",
        ],
        "boundary": (
            "This plan does not run cloud, authorize release, or authorize new public "
            "speedup wording. It only defines the next local and cloud-batch work."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1051 Post-Goal1048 Follow-Up Plan",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        "",
        payload["boundary"],
        "",
        "## Policy",
        "",
        payload["policy"],
        "",
        "## Inputs",
        "",
    ]
    lines.extend(f"- `{item}`" for item in payload["inputs"])
    lines.extend(
        [
            "",
            "## Diagnostic Reruns",
            "",
            "| App | Why | Command |",
            "| --- | --- | --- |",
        ]
    )
    for row in payload["diagnostic_reruns"]:
        lines.append(
            f"| `{row['app']}` | `{row['cloud_policy']}` | `{row['claim_command']}` |"
        )
    lines.extend(
        [
            "",
            "## Same-Semantics Review Needed",
            "",
            "| App | Claim Scope | Boundary |",
            "| --- | --- | --- |",
        ]
    )
    for row in payload["same_semantics_review_needed"]:
        lines.append(
            f"| `{row['app']}` | {row['allowed_claim']} | {row['non_claim']} |"
        )
    lines.extend(
        [
            "",
            "## Reviewed Rows To Preserve",
            "",
        ]
    )
    lines.extend(f"- `{row['app']}`" for row in payload["reviewed_keep_as_is"])
    lines.extend(
        [
            "",
            "## Next Local Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["next_local_actions"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1051 follow-up plan.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1051_post_goal1048_followup_plan_2026-04-28.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1051_post_goal1048_followup_plan_2026-04-28.md",
    )
    args = parser.parse_args()
    payload = build_plan()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_json), "md": str(output_md), "valid": payload["valid"]}))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
