#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest
from scripts.goal761_rtx_cloud_run_all import run_all
from scripts.goal762_rtx_cloud_artifact_report import SUPPORTED_ARTIFACT_APPS


def _git(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout.strip()


def _output_json(command: list[Any]) -> str | None:
    parts = [str(part) for part in command]
    if "--output-json" not in parts:
        return None
    index = parts.index("--output-json")
    if index + 1 >= len(parts):
        return None
    return parts[index + 1]


def run_gate() -> dict[str, Any]:
    manifest = build_manifest()
    active = list(manifest["entries"])
    deferred = list(manifest.get("deferred_entries", ()))
    all_entries = [*active, *deferred]
    active_apps = {str(entry["app"]) for entry in active}
    deferred_apps = {str(entry["app"]) for entry in deferred}
    cloud_apps = active_apps | deferred_apps
    maturity = rt.rt_core_app_maturity_matrix()
    nvidia_target_apps = {
        app
        for app, row in maturity.items()
        if row.target_status != "not_nvidia_rt_core_target"
    }
    non_nvidia_apps = sorted(set(maturity) - nvidia_target_apps)
    missing_cloud_coverage = sorted(nvidia_target_apps - cloud_apps)
    unexpected_cloud_apps = sorted(cloud_apps - nvidia_target_apps)
    unsupported_artifact_apps = sorted(cloud_apps - SUPPORTED_ARTIFACT_APPS)
    entries_without_output_json = sorted(
        str(entry["path_name"])
        for entry in all_entries
        if _output_json(entry.get("command", [])) is None
    )
    output_paths = {
        str(entry["path_name"]): _output_json(entry.get("command", []))
        for entry in all_entries
    }
    duplicate_output_paths: dict[str, list[str]] = {}
    by_path: dict[str, list[str]] = {}
    for path_name, output_path in output_paths.items():
        if output_path is None:
            continue
        by_path.setdefault(output_path, []).append(path_name)
    for output_path, path_names in by_path.items():
        if len(path_names) > 1:
            duplicate_output_paths[output_path] = sorted(path_names)

    full_batch = run_all(dry_run=True, include_deferred=True)
    full_batch_expected_entries = len(all_entries)
    full_batch_errors = []
    if full_batch["status"] != "ok":
        full_batch_errors.append(f"full batch dry-run status is {full_batch['status']}")
    if full_batch["entry_count"] != full_batch_expected_entries:
        full_batch_errors.append(
            f"full batch dry-run entry_count {full_batch['entry_count']} != {full_batch_expected_entries}"
        )
    if not full_batch.get("include_deferred"):
        full_batch_errors.append("full batch dry-run did not include deferred entries")

    errors = {
        "missing_cloud_coverage": missing_cloud_coverage,
        "unexpected_cloud_apps": unexpected_cloud_apps,
        "unsupported_artifact_apps": unsupported_artifact_apps,
        "entries_without_output_json": entries_without_output_json,
        "full_batch_errors": full_batch_errors,
    }
    valid = not any(errors.values())
    return {
        "suite": "goal901_pre_cloud_app_closure_gate",
        "valid": valid,
        "errors": errors,
        "counts": {
            "public_app_count": len(rt.public_apps()),
            "nvidia_target_app_count": len(nvidia_target_apps),
            "non_nvidia_app_count": len(non_nvidia_apps),
            "active_entry_count": len(active),
            "deferred_entry_count": len(deferred),
            "full_batch_entry_count": full_batch["entry_count"],
            "full_batch_unique_command_count": full_batch["unique_command_count"],
            "supported_artifact_app_count": len(SUPPORTED_ARTIFACT_APPS),
        },
        "apps": {
            "active": sorted(active_apps),
            "deferred": sorted(deferred_apps),
            "nvidia_target": sorted(nvidia_target_apps),
            "non_nvidia": non_nvidia_apps,
        },
        "output_paths": output_paths,
        "duplicate_output_paths": duplicate_output_paths,
        "git": {
            "head": _git(["git", "rev-parse", "HEAD"]),
            "status_short": _git(["git", "status", "--short"]),
        },
        "boundary": (
            "Local closure gate only. It confirms app coverage, analyzer coverage, "
            "and full-batch dry-run shape before cloud; it does not start cloud or "
            "authorize performance claims."
        ),
        "next_step_if_valid": (
            "If no further local code/doc issue is found, the next material evidence "
            "requires a real RTX cloud run using docs/rtx_cloud_single_session_runbook.md."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local pre-cloud app closure for RTX batch coverage.")
    parser.add_argument("--output-json", default="docs/reports/goal901_pre_cloud_app_closure_gate_2026-04-24.json")
    args = parser.parse_args(argv)
    payload = run_gate()
    text = json.dumps(payload, indent=2, sort_keys=True)
    Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
