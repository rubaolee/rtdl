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
DATE = "2026-04-26"
SMOKE_COPIES = "50"

sys.path.insert(0, str(ROOT))

from scripts.goal1030_local_baseline_manifest import build_manifest  # noqa: E402


def _scaled_command(command: list[str], *, mode: str) -> list[str]:
    if mode == "full":
        return list(command)
    scaled = list(command)
    for flag in ("--copies",):
        if flag in scaled:
            index = scaled.index(flag)
            if index + 1 < len(scaled):
                scaled[index + 1] = SMOKE_COPIES
    return scaled


def _json_summary(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {"json_parse_status": "not_json"}
    summary: dict[str, Any] = {"json_parse_status": "ok"}
    for key in (
        "app",
        "backend",
        "copies",
        "point_count",
        "household_count",
        "event_count",
        "matches_oracle",
        "native_continuation_active",
        "native_continuation_backend",
        "rt_core_accelerated",
        "output_mode",
        "summary_mode",
        "covered_household_count",
        "hotspot_event_count",
        "outlier_count",
        "core_count",
    ):
        if key in payload:
            summary[key] = payload[key]
    return summary


def _command_status(command: list[str], returncode: int, stderr: str) -> str:
    if returncode == 0:
        return "ok"
    if "--backend" in command and "scipy" in command and "SciPy is not installed" in stderr:
        return "optional_dependency_unavailable"
    return "failed"


def run_entry(entry: dict[str, Any], *, mode: str, timeout_sec: float) -> dict[str, Any]:
    command_results: list[dict[str, Any]] = []
    for command in entry["commands"]:
        effective = _scaled_command(command, mode=mode)
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                effective,
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": "src:."},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
            )
            elapsed = time.perf_counter() - started
            status = _command_status(effective, completed.returncode, completed.stderr)
            command_results.append(
                {
                    "command": effective,
                    "status": status,
                    "returncode": completed.returncode,
                    "elapsed_sec": elapsed,
                    "stdout_tail": completed.stdout[-4000:],
                    "stderr_tail": completed.stderr[-4000:],
                    "json_summary": _json_summary(completed.stdout),
                }
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - started
            command_results.append(
                {
                    "command": effective,
                    "status": "timeout",
                    "returncode": None,
                    "elapsed_sec": elapsed,
                    "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                    "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
                    "json_summary": {"json_parse_status": "not_run_timeout"},
                }
            )
    failed = [row for row in command_results if row["status"] not in {"ok", "optional_dependency_unavailable"}]
    optional_unavailable = [row for row in command_results if row["status"] == "optional_dependency_unavailable"]
    status = "ok" if not failed and not optional_unavailable else "ok_with_optional_dependency_gaps" if not failed else "needs_attention"
    return {
        "app": entry["app"],
        "rtx_path": entry["rtx_path"],
        "local_status": entry["local_status"],
        "mode": mode,
        "status": status,
        "failed_command_count": len(failed),
        "optional_dependency_unavailable_count": len(optional_unavailable),
        "commands": command_results,
    }


def build_report(*, mode: str, timeout_sec: float, include_partial: bool = False) -> dict[str, Any]:
    manifest = build_manifest()
    selected = [
        entry
        for entry in manifest["entries"]
        if include_partial or entry["local_status"] == "baseline_ready"
    ]
    rows = [run_entry(entry, mode=mode, timeout_sec=timeout_sec) for entry in selected]
    failures = [row for row in rows if row["status"] == "needs_attention"]
    optional_gaps = [row for row in rows if row["status"] == "ok_with_optional_dependency_gaps"]
    status = "ok" if not failures and not optional_gaps else "ok_with_optional_dependency_gaps" if not failures else "needs_attention"
    return {
        "goal": "Goal1031 local baseline smoke runner",
        "date": DATE,
        "mode": mode,
        "timeout_sec": timeout_sec,
        "include_partial": include_partial,
        "entry_count": len(rows),
        "failed_entry_count": len(failures),
        "optional_gap_entry_count": len(optional_gaps),
        "rows": rows,
        "status": status,
        "boundary": (
            "Smoke mode intentionally scales --copies down and only checks local command health. "
            "It is not same-scale baseline evidence and does not authorize speedup claims."
            if mode == "smoke"
            else "Full mode executes manifest commands at their listed scale. It still does not authorize speedup claims without same-semantics review."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1031 Local Baseline Smoke Runner",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- mode: `{payload['mode']}`",
        f"- entries: `{payload['entry_count']}`",
        f"- failed entries: `{payload['failed_entry_count']}`",
        f"- optional dependency gap entries: `{payload['optional_gap_entry_count']}`",
        f"- status: `{payload['status']}`",
        "",
        "## Results",
        "",
        "| App | Status | Commands | Failed | Optional gaps | Elapsed total (s) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        elapsed = sum(float(command["elapsed_sec"]) for command in row["commands"])
        lines.append(
            f"| `{row['app']}` | `{row['status']}` | {len(row['commands'])} | "
            f"{row['failed_command_count']} | {row['optional_dependency_unavailable_count']} | {elapsed:.6f} |"
        )
    lines.extend(["", "## Command Details", ""])
    for row in payload["rows"]:
        lines.append(f"### `{row['app']}`")
        lines.append("")
        for command in row["commands"]:
            lines.append(
                f"- status: `{command['status']}`, elapsed: `{float(command['elapsed_sec']):.6f}s`, "
                f"summary: `{command['json_summary']}`"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute local baseline-ready commands safely.")
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--timeout-sec", type=float, default=60.0)
    parser.add_argument("--include-partial", action="store_true")
    parser.add_argument("--output-json", default="docs/reports/goal1031_local_baseline_smoke_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1031_local_baseline_smoke_2026-04-26.md")
    args = parser.parse_args()
    payload = build_report(mode=args.mode, timeout_sec=args.timeout_sec, include_partial=args.include_partial)
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    (ROOT / args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] in {"ok", "ok_with_optional_dependency_gaps"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
