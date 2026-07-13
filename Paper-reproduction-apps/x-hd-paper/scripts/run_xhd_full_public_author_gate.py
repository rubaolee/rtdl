#!/usr/bin/env python3
"""Run the X-HD author binary on a full public Level-B candidate.

This gate is intentionally author-only: it does not compute an RTDL exact
reference, because the full Dragon/HappyBuddha public candidate has hundreds of
billions of directed point pairs. It checks the author HDResult against the
paper-branch log HDResult recorded in the priority input bridge.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Iterable


def _resolve_bridge_paths(bridge: dict[str, object]) -> tuple[Path, Path]:
    candidates = bridge["public_same_source_candidates"]  # type: ignore[index]
    source_basename = str(bridge.get("source_basename") or "dragon.ply")
    target_basename = str(bridge.get("target_basename") or "happy_buddha.ply")
    if source_basename not in candidates or target_basename not in candidates:  # type: ignore[operator]
        order = bridge.get("author_basename_order")
        if isinstance(order, list) and len(order) >= 2:
            source_basename = str(order[0])
            target_basename = str(order[1])
    source = Path(str(candidates[source_basename]["path"]).replace("\\", "/"))  # type: ignore[index]
    target = Path(str(candidates[target_basename]["path"]).replace("\\", "/"))  # type: ignore[index]
    return source, target


def _run_author(
    *,
    author_bin: Path,
    input1: Path,
    input2: Path,
    author_json: Path,
    n_dims: int,
    input_type: str,
    variant: str,
    execution: str,
) -> dict[str, object]:
    author_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(author_bin),
        "-input1",
        str(input1),
        "-input2",
        str(input2),
        "-n_dims",
        str(n_dims),
        "-input_type",
        input_type,
        "-variant",
        variant,
        "-execution",
        execution,
        "-json",
        str(author_json),
        "-overwrite=true",
        "-check=false",
    ]
    start = time.perf_counter()
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    wall_sec = time.perf_counter() - start
    return {
        "cmd": cmd,
        "returncode": int(completed.returncode),
        "wall_sec": wall_sec,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _load_hd_result(path: Path) -> tuple[float, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "HDResult" not in payload:
        raise KeyError(f"{path} does not contain HDResult")
    return float(payload["HDResult"]), payload


def _first_running_avg_ms(payload: dict[str, object]) -> float | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    value = running.get("AvgTime")
    return None if value is None else float(value)


def _input_counts(payload: dict[str, object]) -> list[int]:
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


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    bridge_path = Path(args.bridge)
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    input1, input2 = _resolve_bridge_paths(bridge)
    if not input1.exists() or not input2.exists():
        raise FileNotFoundError(f"missing full public candidate files: {input1} / {input2}")

    author_json = Path(args.author_json)
    author_run: dict[str, object] | None = None
    if args.author_bin:
        author_run = _run_author(
            author_bin=Path(args.author_bin),
            input1=input1,
            input2=input2,
            author_json=author_json,
            n_dims=int(args.n_dims),
            input_type=args.input_type,
            variant=args.variant,
            execution=args.execution,
        )
    if not author_json.exists():
        raise FileNotFoundError(f"author JSON was not produced: {author_json}")

    author_hd, author_payload = _load_hd_result(author_json)
    paper_log_values = [float(value) for value in bridge["author_log_records"]["hd_results"]]  # type: ignore[index]
    if not paper_log_values:
        raise ValueError("bridge author_log_records.hd_results is empty")
    diffs = [abs(author_hd - value) for value in paper_log_values]
    min_diff = min(diffs)
    matched = bool(min_diff <= float(args.tolerance))
    author_run_failed = bool(author_run is not None and author_run["returncode"] != 0)

    return {
        "schema": "rtdl.paper_reproduction.xhd.full_public_author_gate.v1",
        "goal": args.run_goal,
        "status": "full_public_level_b_author_hd_exec_checked",
        "target": bridge["target"],
        "level": "level_b_same_source_candidate_only",
        "bridge": str(bridge_path),
        "input1": str(input1),
        "input2": str(input2),
        "n_dims": int(args.n_dims),
        "input_type": args.input_type,
        "variant": args.variant,
        "execution": args.execution,
        "author_json": str(author_json),
        "author_hd_result": author_hd,
        "author_running_avg_time_ms": _first_running_avg_ms(author_payload),
        "author_input_point_counts": _input_counts(author_payload),
        "paper_log_hd_results": paper_log_values,
        "paper_log_min_abs_diff": min_diff,
        "tolerance": float(args.tolerance),
        "matched": False if author_run_failed else matched,
        "author_run": author_run,
        "author_run_failed": author_run_failed,
        "claim_boundary": {
            "level_b_same_source_candidate_claimed": True,
            "author_full_public_candidate_run_claimed": True,
            "rtdl_all_source_route_run_claimed": False,
            "rtdl_exact_reference_claimed": False,
            "performance_ratio_claimed": False,
            "figure_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
        "boundary_note": (
            "This gate runs author hd_exec on the full public Stanford "
            "Level-B candidate and compares HDResult to the "
            "paper-branch author log value. It does not compute an RTDL exact "
            "reference and does not prove exact paper input identity."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", required=True, type=Path)
    parser.add_argument("--author-bin")
    parser.add_argument("--author-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--run-goal", default="Goal5186")
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--input-type", default="ply", choices=("wkt", "ply", "off", "image"))
    parser.add_argument("--variant", default="rt")
    parser.add_argument("--execution", default="gpu")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        args.output,
        "matched=",
        summary["matched"],
        "author_hd_result=",
        summary["author_hd_result"],
    )
    if summary["author_run_failed"]:
        return 2
    return 0 if summary["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
