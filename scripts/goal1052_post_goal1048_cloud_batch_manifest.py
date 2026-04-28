#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal1051_post_goal1048_followup_plan import build_plan as build_goal1051
from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest as build_goal759


DATE = "2026-04-28"
GOAL = "Goal1052 post-Goal1048 cloud batch manifest"
REPORT_DIR = "docs/reports/goal1052_post_goal1048_cloud_batch"


def _strip_skip_validation(command: list[str]) -> list[str]:
    return [part for part in command if part != "--skip-validation"]


def _rewrite_output(command: list[str], path_name: str) -> list[str]:
    rewritten = list(command)
    if "--output-json" not in rewritten:
        return rewritten
    idx = rewritten.index("--output-json")
    if idx + 1 >= len(rewritten):
        return rewritten
    rewritten[idx + 1] = f"{REPORT_DIR}/{path_name}.json"
    return rewritten


def _manifest_rows_by_app() -> dict[str, list[dict[str, Any]]]:
    manifest = build_goal759()
    rows: dict[str, list[dict[str, Any]]] = {}
    for entry in list(manifest["entries"]) + list(manifest["deferred_entries"]):
        rows.setdefault(entry["app"], []).append(entry)
    return rows


def _prepare_row(entry: dict[str, Any], *, batch: str, force_validation: bool) -> dict[str, Any]:
    row = deepcopy(entry)
    command = list(row["command"])
    if force_validation:
        command = _strip_skip_validation(command)
        if row["app"] == "robot_collision_screening":
            command = _make_robot_validation_command(command)
            row["scale"] = {"pose_count": 4096, "obstacle_count": 256, "iterations": 3}
            row["preconditions"] = [
                "OptiX ray/triangle any-hit prepared symbols must be exported.",
                "Use the phase profiler rather than raw app CLI timing for final claim review.",
                "This diagnostic rerun must not include --skip-validation.",
                "Use python_objects input mode because packed_arrays currently rejects oracle validation.",
                "Use pose_flags result mode because pose_count currently rejects oracle validation.",
            ]
    command = _rewrite_output(command, row["path_name"])
    row["command"] = command
    row["batch"] = batch
    row["force_validation_enabled"] = force_validation
    row["contains_skip_validation"] = "--skip-validation" in command
    row["output_json"] = (
        command[command.index("--output-json") + 1]
        if "--output-json" in command and command.index("--output-json") + 1 < len(command)
        else None
    )
    return row


def _replace_arg(command: list[str], option: str, value: str) -> list[str]:
    rewritten = list(command)
    if option not in rewritten:
        rewritten.extend([option, value])
        return rewritten
    idx = rewritten.index(option)
    if idx + 1 >= len(rewritten):
        rewritten.append(value)
    else:
        rewritten[idx + 1] = value
    return rewritten


def _make_robot_validation_command(command: list[str]) -> list[str]:
    """Use the profiler's validation-capable robot mode for diagnostic reruns.

    The large packed-array pose-count path is the clean performance path, but
    the profiler intentionally rejects oracle validation for that compact mode.
    Goal1052 diagnostic reruns are for correctness/parity evidence after
    Goal1048, so the generated pod command must use Python-object pose flags.
    """
    rewritten = _replace_arg(command, "--pose-count", "4096")
    rewritten = _replace_arg(rewritten, "--obstacle-count", "256")
    rewritten = _replace_arg(rewritten, "--iterations", "3")
    rewritten = _replace_arg(rewritten, "--input-mode", "python_objects")
    rewritten = _replace_arg(rewritten, "--result-mode", "pose_flags")
    return rewritten


def build_manifest() -> dict[str, Any]:
    followup = build_goal1051()
    rows_by_app = _manifest_rows_by_app()

    diagnostic_apps = [row["app"] for row in followup["diagnostic_reruns"]]
    review_apps = [row["app"] for row in followup["same_semantics_review_needed"]]

    diagnostic_rows: list[dict[str, Any]] = []
    for app in diagnostic_apps:
        if app not in rows_by_app:
            continue
        diagnostic_rows.append(
            _prepare_row(rows_by_app[app][0], batch="diagnostic_validation_rerun", force_validation=True)
        )

    review_rows: list[dict[str, Any]] = []
    for app in review_apps:
        for entry in rows_by_app.get(app, []):
            review_rows.append(
                _prepare_row(entry, batch="same_semantics_review_candidate", force_validation=False)
            )

    all_rows = diagnostic_rows + review_rows
    duplicate_outputs = sorted(
        {
            row["output_json"]
            for row in all_rows
            if row["output_json"] is not None
            and sum(other["output_json"] == row["output_json"] for other in all_rows) > 1
        }
    )
    diagnostic_without_validation = [
        row["path_name"] for row in diagnostic_rows if row["contains_skip_validation"]
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "source_manifests": [
            "docs/reports/goal1051_post_goal1048_followup_plan_2026-04-28.json",
            "scripts/goal759_rtx_cloud_benchmark_manifest.py",
            "docs/rtx_cloud_single_session_runbook.md",
        ],
        "purpose": (
            "One-pod post-Goal1048 RTX command manifest. It prioritizes validation-enabled "
            "reruns for diagnostic-only facility and robot paths, then packages remaining "
            "not-reviewed rows for same-semantics review evidence."
        ),
        "policy": (
            "Do not start or stop a cloud pod per app. Run this as one batched session, "
            "copy artifacts after each row or small group, and stop the pod before local review."
        ),
        "global_preconditions": [
            "RTX-class NVIDIA GPU with RT cores; do not use GTX 1070-class hardware for claims.",
            "OptiX backend built from the checked-out commit before timing.",
            "RTDL_SOURCE_COMMIT exported and non-empty before running any command.",
            "Bootstrap check passes before app commands.",
            "Diagnostic rerun rows must not include --skip-validation.",
        ],
        "bootstrap_command": [
            "python3",
            "scripts/goal763_rtx_cloud_bootstrap_check.py",
            "--output-json",
            f"{REPORT_DIR}/goal763_rtx_cloud_bootstrap_check.json",
        ],
        "diagnostic_validation_reruns": diagnostic_rows,
        "same_semantics_review_candidates": review_rows,
        "summary": {
            "diagnostic_rerun_count": len(diagnostic_rows),
            "same_semantics_review_candidate_count": len(review_rows),
            "total_command_count": len(all_rows),
            "diagnostic_without_validation": diagnostic_without_validation,
            "duplicate_output_json": duplicate_outputs,
        },
        "valid": (
            diagnostic_apps == ["facility_knn_assignment", "robot_collision_screening"]
            and len(diagnostic_rows) == 2
            and len(review_rows) == 9
            and not diagnostic_without_validation
            and not duplicate_outputs
        ),
        "boundary": (
            "This manifest prepares cloud execution only. It does not run cloud, authorize "
            "release, or authorize new public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1052 Post-Goal1048 Cloud Batch Manifest",
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
        "## Bootstrap",
        "",
        f"`{' '.join(payload['bootstrap_command'])}`",
        "",
        "## Diagnostic Validation Reruns",
        "",
        "| Path | App | Command |",
        "| --- | --- | --- |",
    ]
    for row in payload["diagnostic_validation_reruns"]:
        lines.append(f"| `{row['path_name']}` | `{row['app']}` | `{' '.join(row['command'])}` |")
    lines.extend(
        [
            "",
            "## Same-Semantics Review Candidates",
            "",
            "| Path | App | Command |",
            "| --- | --- | --- |",
        ]
    )
    for row in payload["same_semantics_review_candidates"]:
        lines.append(f"| `{row['path_name']}` | `{row['app']}` | `{' '.join(row['command'])}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- diagnostic reruns: `{payload['summary']['diagnostic_rerun_count']}`",
            f"- same-semantics review candidates: `{payload['summary']['same_semantics_review_candidate_count']}`",
            f"- total commands after bootstrap: `{payload['summary']['total_command_count']}`",
            f"- diagnostic rows with skip-validation: `{payload['summary']['diagnostic_without_validation']}`",
            f"- duplicate output JSON paths: `{payload['summary']['duplicate_output_json']}`",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1052 post-Goal1048 cloud batch manifest.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1052_post_goal1048_cloud_batch_manifest_2026-04-28.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1052_post_goal1048_cloud_batch_manifest_2026-04-28.md",
    )
    args = parser.parse_args()
    payload = build_manifest()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_json), "md": str(output_md), "valid": payload["valid"]}))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
