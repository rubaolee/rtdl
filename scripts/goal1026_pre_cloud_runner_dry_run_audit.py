#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal761_rtx_cloud_run_all import run_all


DATE = "2026-04-26"
GOAL = "Goal1026 pre-cloud RTX runner dry-run audit"


def build_audit() -> dict[str, Any]:
    dry_run = run_all(dry_run=True, include_deferred=True)
    results = dry_run["results"]
    section_counts = Counter(row["manifest_section"] for row in results)
    result_status_counts = Counter(row["result"]["status"] for row in results)
    execution_mode_counts = Counter(row["result"]["execution_mode"] for row in results)
    apps = sorted({row["app"] for row in results})
    path_names = [row["path_name"] for row in results]
    duplicate_paths = sorted(
        path for path, count in Counter(path_names).items() if count > 1
    )
    command_result_reuse_paths = sorted(
        row["path_name"]
        for row in results
        if row["result"]["execution_mode"] == "reused_command_result"
    )
    valid = (
        dry_run["status"] == "ok"
        and dry_run["dry_run"] is True
        and dry_run["include_deferred"] is True
        and dry_run["entry_count"] == 17
        and dry_run["unique_command_count"] == 16
        and section_counts["entries"] == 8
        and section_counts["deferred_entries"] == 9
        and result_status_counts["dry_run"] == 17
        and dry_run["failed_count"] == 0
        and duplicate_paths == []
        and command_result_reuse_paths == ["prepared_fixed_radius_core_flags"]
        and "does not authorize RTX speedup claims" in dry_run["manifest_boundary"]
        and any(
            "RTX-class NVIDIA hardware with RT cores" in item
            for item in dry_run["global_preconditions"]
        )
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "dry_run_status": dry_run["status"],
        "entry_count": dry_run["entry_count"],
        "unique_command_count": dry_run["unique_command_count"],
        "section_counts": dict(section_counts),
        "result_status_counts": dict(result_status_counts),
        "execution_mode_counts": dict(execution_mode_counts),
        "failed_count": dry_run["failed_count"],
        "apps": apps,
        "path_names": path_names,
        "duplicate_paths": duplicate_paths,
        "command_result_reuse_paths": command_result_reuse_paths,
        "git_head": dry_run["git_head"],
        "source_commit": dry_run["source_commit"],
        "manifest_boundary": dry_run["manifest_boundary"],
        "global_preconditions": dry_run["global_preconditions"],
        "cloud_policy": (
            "The next pod session should run OOM-safe small groups from the "
            "single-session runbook, not isolated per-app pod restarts."
        ),
        "boundary": (
            "This is a local dry-run audit only. It does not start cloud, run "
            "benchmarks, tag, release, or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1026 Pre-Cloud RTX Runner Dry-Run Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- dry-run status: `{payload['dry_run_status']}`",
        f"- entry count: `{payload['entry_count']}`",
        f"- unique command count: `{payload['unique_command_count']}`",
        f"- section counts: `{payload['section_counts']}`",
        f"- result status counts: `{payload['result_status_counts']}`",
        f"- execution mode counts: `{payload['execution_mode_counts']}`",
        f"- failed count: `{payload['failed_count']}`",
        f"- reused command paths: `{payload['command_result_reuse_paths']}`",
        "",
        "## Apps Covered",
        "",
    ]
    for app in payload["apps"]:
        lines.append(f"- `{app}`")
    lines.extend(
        [
            "",
            "## Cloud Policy",
            "",
            payload["cloud_policy"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the pre-cloud RTX runner dry run.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1026_pre_cloud_runner_dry_run_audit_2026-04-26.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1026_pre_cloud_runner_dry_run_audit_2026-04-26.md",
    )
    args = parser.parse_args()

    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
