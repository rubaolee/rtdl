#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest


def _run_command(command: list[str], *, dry_run: bool, env_overrides: dict[str, str] | None = None) -> dict[str, Any]:
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    env_overrides = dict(env_overrides or {})
    if dry_run:
        return {
            "command": command,
            "env_overrides": env_overrides,
            "status": "dry_run",
            "started_at": started,
            "elapsed_sec": 0.0,
            "returncode": 0,
            "stdout_tail": "",
            "stderr_tail": "",
        }
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "src:.", **env_overrides},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    elapsed = time.perf_counter() - start
    return {
        "command": command,
        "env_overrides": env_overrides,
        "status": "ok" if completed.returncode == 0 else "failed",
        "started_at": started,
        "elapsed_sec": elapsed,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def _probe(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return completed.stdout.strip()[-4000:]
    except Exception as exc:
        return f"probe failed: {exc}"


def run_all(*, dry_run: bool, only: set[str] | None = None, include_deferred: bool = False) -> dict[str, Any]:
    manifest = build_manifest()
    active_entries = [
        {**entry, "_manifest_section": "entries"}
        for entry in manifest["entries"]
    ]
    deferred_entries = [
        {**entry, "_manifest_section": "deferred_entries"}
        for entry in manifest.get("deferred_entries", ())
    ] if include_deferred else []
    entries = [
        entry for entry in [*active_entries, *deferred_entries]
        if only is None or entry["path_name"] in only or entry["app"] in only
    ]
    command_results = []
    command_cache: dict[tuple[tuple[str, ...], tuple[tuple[str, str], ...]], dict[str, Any]] = {}
    for entry in entries:
        env_overrides = {
            str(key): str(value)
            for key, value in entry.get("env", {}).items()
        }
        command_key = (
            tuple(str(part) for part in entry["command"]),
            tuple(sorted(env_overrides.items())),
        )
        if command_key in command_cache:
            result = dict(command_cache[command_key])
            result["execution_mode"] = "reused_command_result"
        else:
            result = _run_command(list(entry["command"]), dry_run=dry_run, env_overrides=env_overrides)
            result["execution_mode"] = "executed"
            command_cache[command_key] = dict(result)
        command_results.append(
            {
                "app": entry["app"],
                "path_name": entry["path_name"],
                "manifest_section": entry["_manifest_section"],
                "claim_scope": entry["claim_scope"],
                "non_claim": entry["non_claim"],
                "baseline_review_contract": entry.get("baseline_review_contract"),
                "result": result,
            }
        )
    failed = [item for item in command_results if item["result"]["status"] == "failed"]
    return {
        "suite": "goal761_rtx_cloud_run_all",
        "repo": str(ROOT),
        "dry_run": dry_run,
        "include_deferred": include_deferred,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_head": _probe(["git", "rev-parse", "HEAD"]),
        "git_status_short": _probe(["git", "status", "--short"]),
        "nvidia_smi": _probe(["nvidia-smi"]),
        "python_version": _probe([sys.executable, "--version"]),
        "manifest_boundary": manifest["boundary"],
        "global_preconditions": manifest["global_preconditions"],
        "entry_count": len(entries),
        "unique_command_count": len(command_cache),
        "results": command_results,
        "status": "ok" if not failed else "failed",
        "failed_count": len(failed),
        "boundary": (
            "This runner executes the manifest contract. It does not authorize RTX speedup claims; "
            "claims require review of generated JSON, phase separation, and hardware metadata."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all Goal759 RTX cloud benchmark commands and collect metadata.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-deferred", action="store_true", help="Also run manifest deferred_entries readiness gates.")
    parser.add_argument("--only", action="append", help="Limit to an app or manifest path_name. May be repeated.")
    parser.add_argument("--output-json", default="docs/reports/goal761_rtx_cloud_run_all_summary.json")
    args = parser.parse_args(argv)
    payload = run_all(
        dry_run=args.dry_run,
        only=set(args.only) if args.only else None,
        include_deferred=args.include_deferred,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
