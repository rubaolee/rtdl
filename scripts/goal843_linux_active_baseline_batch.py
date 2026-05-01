#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal838_local_baseline_collection_manifest import build_collection_manifest


GOAL = "Goal843 Linux active baseline batch runner"
DATE = "2026-04-23"
LINUX_ACTIVE_STATUSES = (
    "linux_postgresql_required",
    "linux_preferred_for_large_exact_oracle",
)


def build_linux_active_batch_plan() -> dict[str, Any]:
    manifest = build_collection_manifest()
    selected = [
        action
        for action in manifest["actions"]
        if action.get("status") in LINUX_ACTIVE_STATUSES
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "selected_statuses": list(LINUX_ACTIVE_STATUSES),
        "selected_count": len(selected),
        "actions": selected,
        "boundary": (
            "This batch targets the remaining active Linux-only baselines: live PostgreSQL DB compact summaries "
            "and large exact robot pose-count validation. It does not promote deferred apps or authorize speedup claims."
        ),
    }


def run_batch(plan: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failure_count = 0
    for action in plan["actions"]:
        command = [str(item) for item in action["command"]]
        start = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        elapsed = time.perf_counter() - start
        ok = completed.returncode == 0
        if not ok:
            failure_count += 1
        results.append(
            {
                "app": action["app"],
                "path_name": action["path_name"],
                "baseline": action["baseline"],
                "status": "ok" if ok else "failed",
                "artifact_path": action["artifact_path"],
                "command": command,
                "returncode": completed.returncode,
                "elapsed_sec": elapsed,
                "stdout_tail": completed.stdout.strip().splitlines()[-1:] if completed.stdout else [],
                "stderr_tail": completed.stderr.strip().splitlines()[-20:] if completed.stderr else [],
            }
        )
    return {
        **plan,
        "result_count": len(results),
        "failure_count": failure_count,
        "results": results,
        "status": "ok" if failure_count == 0 else "failed",
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal843 Linux Active Baseline Batch",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- selected actions: `{payload['selected_count']}`",
        f"- failures: `{payload['failure_count']}`",
        f"- statuses: `{', '.join(payload['selected_statuses'])}`",
        "",
        "## Actions",
        "",
        "| App | Path | Baseline | Status | Artifact |",
        "|---|---|---|---|---|",
    ]
    for action in payload["actions"]:
        lines.append(
            f"| {action['app']} | {action['path_name']} | {action['baseline']} | {action.get('status', 'planned')} | {action['artifact_path']} |"
        )
    lines.extend(["", "## Commands", ""])
    for action in payload["actions"]:
        lines.append(f"### {action['app']} / {action['baseline']}")
        lines.append("")
        lines.append("```bash")
        lines.append(" ".join(str(part) for part in action["command"]))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan or run the remaining active Linux-only baseline collectors.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args(argv)

    plan = build_linux_active_batch_plan()
    if args.dry_run:
        payload = {
            **plan,
            "result_count": 0,
            "failure_count": 0,
            "results": [],
            "status": "plan_only",
        }
    else:
        payload = run_batch(plan)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    if args.output_md:
        Path(args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] in {"ok", "plan_only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
