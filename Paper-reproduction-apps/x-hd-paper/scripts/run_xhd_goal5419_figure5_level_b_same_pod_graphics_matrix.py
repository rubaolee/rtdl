#!/usr/bin/env python3
"""Run the Goal5419 Figure-5-like Level-B graphics matrix on one POD.

This is app-owned orchestration.  It consumes the Goal5418 dry-run packet,
executes author ``hd_exec`` and RTDL hd_exec-compatible commands on the same
machine, and writes a phase-separated matrix.  It does not compute or publish
author-vs-RTDL ratios.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
DEFAULT_PACKET = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json"
)
DEFAULT_SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _replace_prefix(parts: list[str], old: str, new: str) -> list[str]:
    return [part.replace(old, new) if isinstance(part, str) else part for part in parts]


def _adapt_command(
    command: list[str],
    *,
    old_output_root: str,
    new_output_root: str,
    python_executable: str,
) -> list[str]:
    adapted = _replace_prefix([str(part) for part in command], old_output_root, new_output_root)
    if adapted and adapted[0] == "py":
        adapted[0] = python_executable
    return adapted


def _run_command(command: list[str], *, cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=str(cwd), env=env, check=False, text=True)
    elapsed = time.perf_counter() - started
    return {
        "command": command,
        "returncode": completed.returncode,
        "process_wall_sec": elapsed,
    }


def _author_columns(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    running = data.get("Running", {})
    return {
        "json_path": str(path),
        "hd_result": data.get("HDResult"),
        "running_avg_time_ms": running.get("AvgTime"),
        "reported_time_ms": running.get("ReportedTime"),
        "running": running,
    }


def _rtdl_columns(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    rtdl = data.get("RTDL", {})
    route = rtdl.get("route", {})
    phases = rtdl.get("run_phases") or route.get("run_phases") or {}
    return {
        "json_path": str(path),
        "hd_result": data.get("HDResult"),
        "route_label": rtdl.get("route_label") or route.get("route_label"),
        "rtdl_route_wall_sec": phases.get("rtdl_route_sec"),
        "rtdl_process_wall_sec": phases.get("entrypoint_total_sec") or phases.get("total_sec"),
        "rtdl_input_load_sec": phases.get("load_input_sec"),
        "per_source_witness_exact": route.get("per_source_witness_exact"),
        "witness_contract": route.get("witness_contract"),
        "running_avg_time_ms": (data.get("Running") or {}).get("AvgTime"),
        "running_time_semantics": (data.get("Running") or {}).get("TimeSemantics"),
    }


def _json_path_from_command(command: list[str]) -> Path:
    try:
        return Path(command[command.index("-json") + 1])
    except (ValueError, IndexError) as exc:
        raise ValueError(f"command has no -json output path: {command}") from exc


def build_matrix(args: argparse.Namespace) -> dict[str, Any]:
    packet = _read_json(Path(args.packet))
    if not bool(packet.get("dry_run_only")):
        raise ValueError("Goal5419 expects a Goal5418 dry-run packet as input")

    output_root = str(args.remote_output_dir)
    serialize_root = str(args.remote_serialize_dir)
    Path(output_root).mkdir(parents=True, exist_ok=True)
    Path(serialize_root).mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(args.pythonpath)
    env["RTDL_OPTIX_LIBRARY"] = str(args.rtdl_optix_library)
    cwd = Path(args.cwd)
    tolerance = float(args.tolerance)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for case in packet["graphics_execution_rows"]:
        case_id = str(case["case_id"])
        author_command = _adapt_command(
            case["author_command"],
            old_output_root="/tmp/xhd_goal5418",
            new_output_root=output_root.rsplit("/", 1)[0],
            python_executable=str(args.python_executable),
        )
        author_command = _replace_prefix(author_command, "/tmp/xhd_goal5418/ser", serialize_root)
        author_run = _run_command(author_command, cwd=cwd, env=env)
        if author_run["returncode"] != 0:
            failures.append({"case_id": case_id, "runner": "author", **author_run})
            continue
        author_json = _author_columns(_json_path_from_command(author_command))

        rtdl_rows: list[dict[str, Any]] = []
        for route in case["rtdl_route_commands"]:
            command = _adapt_command(
                route["command"],
                old_output_root="/tmp/xhd_goal5418",
                new_output_root=output_root.rsplit("/", 1)[0],
                python_executable=str(args.python_executable),
            )
            run = _run_command(command, cwd=cwd, env=env)
            route_label = route["route_label"]
            if run["returncode"] != 0:
                failures.append({"case_id": case_id, "runner": "rtdl", "route_label": route_label, **run})
                continue
            rtdl_json = _rtdl_columns(_json_path_from_command(command))
            abs_diff_author = (
                abs(float(rtdl_json["hd_result"]) - float(author_json["hd_result"]))
                if rtdl_json["hd_result"] is not None and author_json["hd_result"] is not None
                else None
            )
            rtdl_rows.append(
                {
                    "route_label": route_label,
                    "condition": route["condition"],
                    "command": command,
                    "process_wall_sec": run["process_wall_sec"],
                    "rtdl": rtdl_json,
                    "abs_diff_vs_author_rerun": abs_diff_author,
                    "matched_author_rerun": abs_diff_author is not None and abs_diff_author <= tolerance,
                    "ratio_authorized": False,
                }
            )

        author_paper = case.get("paper_log_hd_result_if_available")
        abs_diff_author_paper = (
            abs(float(author_json["hd_result"]) - float(author_paper))
            if author_json["hd_result"] is not None and author_paper is not None
            else None
        )
        rows.append(
            {
                "case_id": case_id,
                "category": case["category"],
                "input_identity_level": case["input_identity_level"],
                "point_counts": case["point_counts"],
                "required_rtdl_preprocessing": case.get("required_rtdl_preprocessing", []),
                "author_command": author_command,
                "author_process_wall_sec": author_run["process_wall_sec"],
                "author": author_json,
                "paper_log_hd_result_if_available": author_paper,
                "abs_diff_author_rerun_vs_paper_log": abs_diff_author_paper,
                "author_rerun_matches_paper_log": (
                    abs_diff_author_paper is not None and abs_diff_author_paper <= tolerance
                ),
                "rtdl_routes": rtdl_rows,
                "ratio_authorized": False,
            }
        )

    all_route_matches = all(
        route["matched_author_rerun"] for row in rows for route in row["rtdl_routes"]
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5419.figure5_level_b_same_pod_graphics_matrix.v1",
        "goal": "Goal5419",
        "status": (
            "figure5_level_b_same_pod_graphics_matrix_executed"
            if not failures
            else "figure5_level_b_same_pod_graphics_matrix_failed"
        ),
        "matched": not failures and all_route_matches,
        "source_packet": str(args.packet),
        "same_pod_execution_claimed": True,
        "matrix_rows_executed": len(rows),
        "graphics_case_count": len(rows),
        "route_result_count": sum(len(row["rtdl_routes"]) for row in rows),
        "tolerance": tolerance,
        "pod": {
            "hostname": os.uname().nodename if hasattr(os, "uname") else None,
            "cwd": str(cwd),
            "rtdl_optix_library": str(args.rtdl_optix_library),
        },
        "rows": rows,
        "failures": failures,
        "claim_boundary": {
            "figure5_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--cwd", type=Path, default=ROOT)
    parser.add_argument("--pythonpath", default="src:.")
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--rtdl-optix-library", required=True)
    parser.add_argument("--remote-output-dir", default="/tmp/xhd_goal5419/results")
    parser.add_argument("--remote-serialize-dir", default="/tmp/xhd_goal5419/ser")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_matrix(args)
    _write_json(Path(args.summary), payload)
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
