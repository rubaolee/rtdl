#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest


DATE = "2026-04-26"
GOAL = "Goal1025 pre-cloud RTX app batch readiness"


def _entry_rows(entries: list[dict[str, Any]], bucket: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        rows.append(
            {
                "bucket": bucket,
                "app": entry["app"],
                "path_name": entry["path_name"],
                "benchmark_readiness": entry["benchmark_readiness"],
                "claim_scope": entry["claim_scope"],
                "non_claim": entry["non_claim"],
                "command": entry["command"],
            }
        )
    return rows


def build_audit() -> dict[str, Any]:
    apps = list(rt.public_apps())
    manifest = build_manifest()
    active_rows = _entry_rows(manifest["entries"], "active")
    deferred_rows = _entry_rows(manifest["deferred_entries"], "deferred")
    all_rows = active_rows + deferred_rows
    rows_by_app: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        rows_by_app[row["app"]].append(row)

    app_rows: list[dict[str, Any]] = []
    missing_nvidia_targets: list[str] = []
    unexpected_non_nvidia_targets: list[str] = []
    for app in apps:
        readiness = rt.optix_app_benchmark_readiness(app)
        maturity = rt.rt_core_app_maturity(app)
        public_wording = rt.rtx_public_wording_status(app)
        is_nvidia_target = readiness.status != "exclude_from_rtx_app_benchmark"
        manifest_rows = rows_by_app.get(app, [])
        if is_nvidia_target and not manifest_rows:
            missing_nvidia_targets.append(app)
        if not is_nvidia_target and manifest_rows:
            unexpected_non_nvidia_targets.append(app)
        app_rows.append(
            {
                "app": app,
                "readiness": readiness.status,
                "maturity": maturity.current_status,
                "public_wording": public_wording.status,
                "manifest_bucket_count": len(manifest_rows),
                "manifest_buckets": sorted({row["bucket"] for row in manifest_rows}),
                "path_names": [row["path_name"] for row in manifest_rows],
            }
        )

    readiness_counts = Counter(row["readiness"] for row in app_rows)
    maturity_counts = Counter(row["maturity"] for row in app_rows)
    public_wording_counts = Counter(row["public_wording"] for row in app_rows)
    duplicate_commands = []
    command_map: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for row in all_rows:
        command_map[tuple(row["command"])].append(row["path_name"])
    for command, path_names in command_map.items():
        if len(path_names) > 1:
            duplicate_commands.append(
                {
                    "path_names": path_names,
                    "command": list(command),
                    "reason": "runner may reuse duplicate command output in one paid session",
                }
            )

    public_wording_reviewed = [
        row["app"] for row in app_rows if row["public_wording"] == "public_wording_reviewed"
    ]
    public_wording_blocked = [
        row["app"] for row in app_rows if row["public_wording"] == "public_wording_blocked"
    ]
    global_preconditions = manifest["global_preconditions"]
    manifest_boundary = manifest["boundary"]
    has_rtx_hardware_precondition = any(
        "RTX-class NVIDIA hardware with RT cores" in item for item in global_preconditions
    )
    manifest_blocks_speedup_claims = "does not authorize RTX speedup claims" in manifest_boundary
    valid = (
        len(apps) == 18
        and readiness_counts["ready_for_rtx_claim_review"] == 16
        and readiness_counts["exclude_from_rtx_app_benchmark"] == 2
        and maturity_counts["rt_core_ready"] == 16
        and maturity_counts["not_nvidia_rt_core_target"] == 2
        and public_wording_counts["public_wording_reviewed"] == 7
        and public_wording_counts["public_wording_blocked"] == 1
        and public_wording_blocked == ["robot_collision_screening"]
        and not missing_nvidia_targets
        and not unexpected_non_nvidia_targets
        and has_rtx_hardware_precondition
        and manifest_blocks_speedup_claims
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "public_app_count": len(apps),
        "readiness_counts": dict(readiness_counts),
        "maturity_counts": dict(maturity_counts),
        "public_wording_counts": dict(public_wording_counts),
        "active_manifest_entry_count": len(active_rows),
        "deferred_manifest_entry_count": len(deferred_rows),
        "active_apps": sorted({row["app"] for row in active_rows}),
        "deferred_apps": sorted({row["app"] for row in deferred_rows}),
        "excluded_apps": sorted(manifest["excluded_apps"]),
        "missing_nvidia_targets": missing_nvidia_targets,
        "unexpected_non_nvidia_targets": unexpected_non_nvidia_targets,
        "public_wording_reviewed_apps": sorted(public_wording_reviewed),
        "public_wording_blocked_apps": public_wording_blocked,
        "duplicate_commands": duplicate_commands,
        "manifest_global_preconditions": global_preconditions,
        "manifest_boundary": manifest_boundary,
        "has_rtx_hardware_precondition": has_rtx_hardware_precondition,
        "manifest_blocks_speedup_claims": manifest_blocks_speedup_claims,
        "app_rows": app_rows,
        "cloud_policy": (
            "Do not start a paid pod for one app. The next pod should run the manifest "
            "as one consolidated active+deferred regression/tuning batch after local "
            "checks are clean."
        ),
        "valid": valid,
        "boundary": (
            "This pre-cloud audit checks readiness coverage only. It does not run cloud, "
            "tag, release, or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1025 Pre-Cloud RTX App Batch Readiness",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- public apps: `{payload['public_app_count']}`",
        f"- active manifest entries: `{payload['active_manifest_entry_count']}`",
        f"- deferred manifest entries: `{payload['deferred_manifest_entry_count']}`",
        f"- missing NVIDIA targets: `{len(payload['missing_nvidia_targets'])}`",
        f"- unexpected non-NVIDIA manifest targets: `{len(payload['unexpected_non_nvidia_targets'])}`",
        f"- public wording reviewed apps: `{len(payload['public_wording_reviewed_apps'])}`",
        f"- public wording blocked apps: `{payload['public_wording_blocked_apps']}`",
        f"- RTX hardware precondition present: `{payload['has_rtx_hardware_precondition']}`",
        f"- manifest blocks speedup claims: `{payload['manifest_blocks_speedup_claims']}`",
        "",
        "## Cloud Policy",
        "",
        payload["cloud_policy"],
        "",
        "## App Rows",
        "",
        "| App | Readiness | Maturity | Public wording | Manifest buckets | Paths |",
        "|---|---|---|---|---|---:|",
    ]
    for row in payload["app_rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['readiness']}` | `{row['maturity']}` | "
            f"`{row['public_wording']}` | `{','.join(row['manifest_buckets'])}` | "
            f"{len(row['path_names'])} |"
        )
    if payload["duplicate_commands"]:
        lines.extend(["", "## Duplicate Commands", ""])
        for row in payload["duplicate_commands"]:
            lines.append(
                f"- `{', '.join(row['path_names'])}` reuse one command; {row['reason']}."
            )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit pre-cloud RTX app batch readiness.")
    parser.add_argument("--output-json", default="docs/reports/goal1025_pre_cloud_rtx_app_batch_readiness_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1025_pre_cloud_rtx_app_batch_readiness_2026-04-26.md")
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
