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

sys.path.insert(0, str(ROOT))

from scripts.goal1030_local_baseline_manifest import build_manifest  # noqa: E402
from scripts.goal1031_local_baseline_smoke_runner import _command_status, _json_summary  # noqa: E402


def _with_copies(command: list[str], copies: int) -> list[str]:
    updated = list(command)
    if "--copies" not in updated:
        return updated
    index = updated.index("--copies")
    if index + 1 >= len(updated):
        return updated
    updated[index + 1] = str(copies)
    return updated


def _backend(command: list[str]) -> str:
    if "--backend" not in command:
        return "unknown"
    index = command.index("--backend")
    if index + 1 >= len(command):
        return "unknown"
    return command[index + 1]


def _select_entries(apps: set[str] | None) -> list[dict[str, Any]]:
    manifest = build_manifest()
    ready = [entry for entry in manifest["entries"] if entry["local_status"] == "baseline_ready"]
    if not apps:
        return ready
    return [entry for entry in ready if entry["app"] in apps]


def _run_command(command: list[str], *, timeout_sec: float) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": "src:."},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
            check=False,
        )
        elapsed = time.perf_counter() - started
        status = _command_status(command, completed.returncode, completed.stderr)
        return {
            "backend": _backend(command),
            "command": command,
            "status": status,
            "returncode": completed.returncode,
            "elapsed_sec": elapsed,
            "json_summary": _json_summary(completed.stdout),
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        return {
            "backend": _backend(command),
            "command": command,
            "status": "timeout",
            "returncode": None,
            "elapsed_sec": elapsed,
            "json_summary": {"json_parse_status": "not_run_timeout"},
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
        }


def _status(rows: list[dict[str, Any]]) -> str:
    failed = [row for row in rows if row["status"] not in {"ok", "optional_dependency_unavailable"}]
    optional = [row for row in rows if row["status"] == "optional_dependency_unavailable"]
    if failed:
        return "needs_attention"
    if optional:
        return "ok_with_optional_dependency_gaps"
    return "ok"


def build_payload(rows: list[dict[str, Any]], *, copies_list: list[int], timeout_sec: float) -> dict[str, Any]:
    return {
        "goal": "Goal1035 local baseline scale ramp",
        "date": DATE,
        "copies_list": copies_list,
        "timeout_sec": timeout_sec,
        "row_count": len(rows),
        "status": _status(rows),
        "rows": rows,
        "boundary": (
            "This scale-ramp runner collects incremental local same-command health and timing evidence. "
            "It does not authorize speedup claims, and same-scale public comparisons still require review."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1035 Local Baseline Scale Ramp",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- copies_list: `{payload['copies_list']}`",
        f"- timeout_sec: `{payload['timeout_sec']}`",
        f"- rows: `{payload['row_count']}`",
        f"- status: `{payload['status']}`",
        "",
        "## Results",
        "",
        "| App | Copies | Backend | Status | Elapsed (s) | Summary |",
        "|---|---:|---|---|---:|---|",
    ]
    for row in payload["rows"]:
        summary = row["json_summary"]
        compact_summary = {
            key: summary[key]
            for key in (
                "app",
                "backend",
                "copies",
                "matches_oracle",
                "summary_mode",
                "native_continuation_active",
                "native_continuation_backend",
                "outlier_count",
                "core_count",
                "covered_household_count",
                "hotspot_event_count",
            )
            if key in summary
        }
        lines.append(
            f"| `{row['app']}` | {row['copies']} | `{row['backend']}` | `{row['status']}` | "
            f"{float(row['elapsed_sec']):.6f} | `{compact_summary}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def write_outputs(rows: list[dict[str, Any]], *, copies_list: list[int], timeout_sec: float, output_json: Path, output_md: Path) -> None:
    payload = build_payload(rows, copies_list=copies_list, timeout_sec=timeout_sec)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")


def run_scale_ramp(
    *,
    apps: set[str] | None,
    copies_list: list[int],
    timeout_sec: float,
    output_json: Path,
    output_md: Path,
) -> dict[str, Any]:
    entries = _select_entries(apps)
    rows: list[dict[str, Any]] = []
    for copies in copies_list:
        for entry in entries:
            for command in entry["commands"]:
                effective = _with_copies(command, copies)
                result = _run_command(effective, timeout_sec=timeout_sec)
                result.update(
                    {
                        "app": entry["app"],
                        "rtx_path": entry["rtx_path"],
                        "copies": copies,
                    }
                )
                rows.append(result)
                write_outputs(
                    rows,
                    copies_list=copies_list,
                    timeout_sec=timeout_sec,
                    output_json=output_json,
                    output_md=output_md,
                )
    return build_payload(rows, copies_list=copies_list, timeout_sec=timeout_sec)


def _parse_copies(raw: str) -> list[int]:
    values = [int(part) for part in raw.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("copies list must not be empty")
    if any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("copies values must be positive")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Run incremental local baselines for baseline-ready apps.")
    parser.add_argument("--apps", default="", help="comma-separated app names; default runs all baseline-ready apps")
    parser.add_argument("--copies-list", type=_parse_copies, default=[50, 500, 2000])
    parser.add_argument("--timeout-sec", type=float, default=180.0)
    parser.add_argument("--output-json", default="docs/reports/goal1035_local_baseline_scale_ramp_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1035_local_baseline_scale_ramp_2026-04-26.md")
    args = parser.parse_args()

    apps = {part.strip() for part in args.apps.split(",") if part.strip()} or None
    payload = run_scale_ramp(
        apps=apps,
        copies_list=args.copies_list,
        timeout_sec=args.timeout_sec,
        output_json=ROOT / args.output_json,
        output_md=ROOT / args.output_md,
    )
    print(to_markdown(payload))
    return 0 if payload["status"] in {"ok", "ok_with_optional_dependency_gaps"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
