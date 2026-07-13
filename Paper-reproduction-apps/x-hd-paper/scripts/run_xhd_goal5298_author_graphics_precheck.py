#!/usr/bin/env python3
"""Run Goal5298 author-only graphics value prechecks on POD data.

This script is intentionally app-owned.  It invokes the pinned author
``hd_exec`` binary on public Stanford graphics candidates that have been copied
to the POD, then records HDResult, point counts, and author timing fields.

It does not run RTDL, does not compute a performance ratio, and does not claim
exact paper dataset identity.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any


CASES: list[dict[str, Any]] = [
    {
        "case_id": "dragon_happy",
        "paper_log_pair": ["dragon.ply", "happy_buddha.ply"],
        "input1": "dragon.ply",
        "input2": "happy_buddha.ply",
        "paper_log_hd_result": 0.12572969496250153,
        "paper_log_relative_path": "expr/logs/end2end/rt_gpu/graphics/dragon.ply_happy_buddha.ply.json",
    },
    {
        "case_id": "dragon_asian_scaled",
        "paper_log_pair": ["dragon.ply", "asian_dragon.ply"],
        "input1": "dragon.ply",
        "input2": "asian_dragon_scaled_1e-3.ply",
        "paper_log_hd_result": 0.06536811590194702,
        "paper_log_relative_path": "expr/logs/end2end/rt_gpu/graphics/dragon.ply_asian_dragon.ply.json",
        "local_mapping_note": "author log basename asian_dragon.ply is represented by local scaled public file",
    },
    {
        "case_id": "thai_happy_scaled",
        "paper_log_pair": ["thai_statuette.ply", "happy_buddha.ply"],
        "input1": "thai_statuette_scaled_1e-3.ply",
        "input2": "happy_buddha.ply",
        "paper_log_hd_result": 0.21912434697151184,
        "paper_log_relative_path": "expr/logs/end2end/rt_gpu/graphics/thai_statuette.ply_happy_buddha.ply.json",
        "local_mapping_note": "author log basename thai_statuette.ply is represented by local scaled public file",
    },
    {
        "case_id": "thai_asian_scaled",
        "paper_log_pair": ["thai_statuette.ply", "asian_dragon.ply"],
        "input1": "thai_statuette_scaled_1e-3.ply",
        "input2": "asian_dragon_scaled_1e-3.ply",
        "paper_log_hd_result": 0.28763845562934875,
        "paper_log_relative_path": "expr/logs/end2end/rt_gpu/graphics/thai_statuette.ply_asian_dragon.ply.json",
        "local_mapping_note": "author log basenames are represented by local scaled public files",
    },
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _running_avg_time_ms(payload: dict[str, Any]) -> float | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    value = running.get("AvgTime")
    return None if value is None else float(value)


def _reported_time_ms(payload: dict[str, Any]) -> float | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats:
        return None
    first = repeats[0]
    if not isinstance(first, dict):
        return None
    value = first.get("ReportedTime")
    return None if value is None else float(value)


def _input_counts(payload: dict[str, Any]) -> list[int]:
    input_payload = payload.get("Input")
    if not isinstance(input_payload, dict):
        return []
    files = input_payload.get("Files")
    if not isinstance(files, list):
        return []
    counts: list[int] = []
    for item in files:
        if isinstance(item, dict) and "NumPoints" in item:
            counts.append(int(item["NumPoints"]))
    return counts


def _memory(payload: dict[str, Any]) -> dict[str, Any] | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats:
        return None
    first = repeats[0]
    if not isinstance(first, dict):
        return None
    memory = first.get("Memory")
    return memory if isinstance(memory, dict) else None


def _run_case(
    *,
    author_bin: Path,
    data_dir: Path,
    output_dir: Path,
    serialize_dir: Path,
    case: dict[str, Any],
    tolerance: float,
    lb: int,
    repeat: int,
) -> dict[str, Any]:
    input1 = data_dir / str(case["input1"])
    input2 = data_dir / str(case["input2"])
    if not input1.exists():
        raise FileNotFoundError(input1)
    if not input2.exists():
        raise FileNotFoundError(input2)

    author_json = output_dir / f"{case['case_id']}_author.json"
    cmd = [
        str(author_bin),
        "-input1",
        str(input1),
        "-input2",
        str(input2),
        "-input_type",
        "ply",
        "-n_dims",
        "3",
        "-serialize",
        str(serialize_dir),
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "-repeat",
        str(repeat),
        "-json",
        str(author_json),
        "-overwrite=true",
        "-check=false",
        "-normalize=false",
        f"-lb={lb}",
    ]
    start = time.perf_counter()
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    wall_sec = time.perf_counter() - start
    author_payload: dict[str, Any] | None = None
    author_hd: float | None = None
    if author_json.exists():
        author_payload = _read_json(author_json)
        if "HDResult" in author_payload:
            author_hd = float(author_payload["HDResult"])

    paper_log_hd = float(case["paper_log_hd_result"])
    abs_diff = None if author_hd is None else abs(author_hd - paper_log_hd)
    matched = bool(completed.returncode == 0 and abs_diff is not None and abs_diff <= tolerance)
    return {
        **case,
        "input1_path": str(input1),
        "input2_path": str(input2),
        "author_json": str(author_json),
        "author_returncode": int(completed.returncode),
        "author_stdout_tail": completed.stdout[-2000:],
        "author_stderr_tail": completed.stderr[-2000:],
        "author_process_wall_sec": wall_sec,
        "author_hd_result": author_hd,
        "paper_log_abs_diff": abs_diff,
        "tolerance": tolerance,
        "matched_paper_log_value": matched,
        "author_running_avg_time_ms": None if author_payload is None else _running_avg_time_ms(author_payload),
        "author_reported_time_ms": None if author_payload is None else _reported_time_ms(author_payload),
        "author_input_point_counts": [] if author_payload is None else _input_counts(author_payload),
        "author_memory": None if author_payload is None else _memory(author_payload),
        "cmd": cmd,
    }


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    serialize_dir = Path(args.serialize_dir)
    serialize_dir.mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.data_dir)
    author_bin = Path(args.author_bin)
    results = [
        _run_case(
            author_bin=author_bin,
            data_dir=data_dir,
            output_dir=output_dir,
            serialize_dir=serialize_dir,
            case=case,
            tolerance=float(args.tolerance),
            lb=int(args.lb),
            repeat=int(args.repeat),
        )
        for case in CASES
    ]
    matched_count = sum(1 for row in results if row["matched_paper_log_value"])
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5298.author_graphics_precheck.v1",
        "goal": "Goal5298",
        "status": "author_only_level_b_graphics_precheck_complete",
        "level": "level_b_same_source_author_only_precheck",
        "author_bin": str(author_bin),
        "data_dir": str(data_dir),
        "output_dir": str(output_dir),
        "serialize_dir": str(serialize_dir),
        "lb": int(args.lb),
        "repeat": int(args.repeat),
        "tolerance": float(args.tolerance),
        "case_count": len(results),
        "matched_paper_log_value_count": matched_count,
        "all_cases_matched_paper_log_value": matched_count == len(results),
        "cases": results,
        "claim_boundary": {
            "author_only_precheck_claimed": True,
            "level_b_same_source_candidate_claimed": True,
            "rtdl_route_run": False,
            "rtdl_author_performance_ratio_claimed": False,
            "figure_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
        "boundary_note": (
            "This is an author-only Level-B graphics precheck on public Stanford "
            "files copied to the current POD.  It records whether current author "
            "reruns match paper-branch author-log HDResult values.  It does not "
            "run RTDL and does not prove exact paper dataset identity."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author-bin", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--serialize-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--lb", type=int, default=256)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()

    summary = build_summary(args)
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        summary_path,
        "matched",
        f"{summary['matched_paper_log_value_count']}/{summary['case_count']}",
    )
    return 0 if summary["all_cases_matched_paper_log_value"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
