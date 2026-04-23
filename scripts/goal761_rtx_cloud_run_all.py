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


def _run_command(command: list[str], *, dry_run: bool) -> dict[str, Any]:
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    if dry_run:
        return {
            "command": command,
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
        env={**os.environ, "PYTHONPATH": "src:."},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    elapsed = time.perf_counter() - start
    return {
        "command": command,
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


def run_all(*, dry_run: bool, only: set[str] | None = None) -> dict[str, Any]:
    manifest = build_manifest()
    entries = [
        entry for entry in manifest["entries"]
        if only is None or entry["path_name"] in only or entry["app"] in only
    ]
    command_results = []
    for entry in entries:
        command_results.append(
            {
                "app": entry["app"],
                "path_name": entry["path_name"],
                "claim_scope": entry["claim_scope"],
                "non_claim": entry["non_claim"],
                "result": _run_command(list(entry["command"]), dry_run=dry_run),
            }
        )
    failed = [item for item in command_results if item["result"]["status"] == "failed"]
    return {
        "suite": "goal761_rtx_cloud_run_all",
        "repo": str(ROOT),
        "dry_run": dry_run,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_head": _probe(["git", "rev-parse", "HEAD"]),
        "git_status_short": _probe(["git", "status", "--short"]),
        "nvidia_smi": _probe(["nvidia-smi"]),
        "python_version": _probe([sys.executable, "--version"]),
        "manifest_boundary": manifest["boundary"],
        "global_preconditions": manifest["global_preconditions"],
        "entry_count": len(entries),
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
    parser.add_argument("--only", action="append", help="Limit to an app or manifest path_name. May be repeated.")
    parser.add_argument("--output-json", default="docs/reports/goal761_rtx_cloud_run_all_summary.json")
    args = parser.parse_args(argv)
    payload = run_all(dry_run=args.dry_run, only=set(args.only) if args.only else None)
    text = json.dumps(payload, indent=2, sort_keys=True)
    Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
