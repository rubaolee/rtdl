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


GOAL = "Goal841 local baseline collector runner"
DATE = "2026-04-23"


def _match(action: dict[str, Any], *, app: str | None, path_name: str | None, baseline: str | None) -> bool:
    if app is not None and action.get("app") != app:
        return False
    if path_name is not None and action.get("path_name") != path_name:
        return False
    if baseline is not None and action.get("baseline") != baseline:
        return False
    return True


def build_run_plan(*, app: str | None = None, path_name: str | None = None, baseline: str | None = None) -> dict[str, Any]:
    manifest = build_collection_manifest()
    selected = [
        action
        for action in manifest["actions"]
        if action.get("status") == "local_command_ready"
        and _match(action, app=app, path_name=path_name, baseline=baseline)
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "selection": {
            "app": app,
            "path_name": path_name,
            "baseline": baseline,
        },
        "selected_count": len(selected),
        "actions": selected,
        "boundary": (
            "This runner executes only Goal838 local_command_ready artifact collectors. "
            "It does not collect Linux/PostgreSQL baselines, optional SciPy/reference baselines, "
            "or deferred-app baselines."
        ),
    }


def run_plan(plan: dict[str, Any]) -> dict[str, Any]:
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
                "artifact_path": action["artifact_path"],
                "command": command,
                "returncode": completed.returncode,
                "elapsed_sec": elapsed,
                "stdout_tail": completed.stdout.strip().splitlines()[-1:] if completed.stdout else [],
                "stderr_tail": completed.stderr.strip().splitlines()[-20:] if completed.stderr else [],
                "status": "ok" if ok else "failed",
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
        "# Goal841 Local Baseline Collector Runner",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        "## Selection",
        "",
        f"- app: `{payload['selection']['app']}`",
        f"- path_name: `{payload['selection']['path_name']}`",
        f"- baseline: `{payload['selection']['baseline']}`",
        f"- selected actions: `{payload['selected_count']}`",
        f"- failures: `{payload['failure_count']}`",
        "",
        "## Results",
        "",
        "| App | Path | Baseline | Status | Seconds | Artifact |",
        "|---|---|---|---|---:|---|",
    ]
    for result in payload["results"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(result["app"]),
                    str(result["path_name"]),
                    str(result["baseline"]),
                    str(result["status"]),
                    f"{result['elapsed_sec']:.3f}",
                    str(result["artifact_path"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run selected Goal838 local baseline collectors.")
    parser.add_argument("--app")
    parser.add_argument("--path-name")
    parser.add_argument("--baseline")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args(argv)

    plan = build_run_plan(app=args.app, path_name=args.path_name, baseline=args.baseline)
    if args.dry_run:
        payload = {
            **plan,
            "result_count": 0,
            "failure_count": 0,
            "results": [],
            "status": "plan_only",
        }
    else:
        payload = run_plan(plan)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    if args.output_md:
        Path(args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] in {"ok", "plan_only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
