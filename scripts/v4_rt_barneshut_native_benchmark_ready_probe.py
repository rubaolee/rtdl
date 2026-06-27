from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rt_barneshut_author_contract import (  # noqa: E402
    load_rt_barneshut_author_dataset,
    parse_rt_barneshut_author_stdout,
    write_trimmed_rt_barneshut_author_dataset,
)
from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    run_v4_rt_barneshut_native_author_route,
)


def _tail(text: str, *, count: int = 40) -> tuple[str, ...]:
    return tuple(text.splitlines()[-count:])


def _rt_force_seconds(run: dict[str, Any]) -> float | None:
    phase = run.get("phase_seconds", {})
    if not isinstance(phase, dict):
        return None
    value = phase.get("rt_force_seconds")
    return float(value) if value is not None else None


def _execution_seconds(run: dict[str, Any]) -> float | None:
    phase = run.get("phase_seconds", {})
    if not isinstance(phase, dict):
        return None
    value = phase.get("execution_seconds")
    return float(value) if value is not None else None


def _author_checksum_validation(
    *,
    native_checksum: float,
    native_abs_checksum: float,
    parsed_stdout: dict[str, float | int],
) -> dict[str, object]:
    if "rt_force_checksum" not in parsed_stdout:
        return {
            "available": False,
            "reason": "author binary did not emit rt_force_checksum",
            "passes_float_output_tolerance": False,
        }
    author_checksum = float(parsed_stdout["rt_force_checksum"])
    checksum_relative_error = abs(native_checksum - author_checksum) / max(abs(author_checksum), 1.0)
    payload: dict[str, object] = {
        "available": True,
        "native_force_checksum": native_checksum,
        "author_rt_force_checksum": author_checksum,
        "checksum_relative_error": checksum_relative_error,
        "passes_float_output_tolerance": checksum_relative_error <= 1.0e-4,
    }
    if "rt_force_abs_checksum" in parsed_stdout:
        author_abs_checksum = float(parsed_stdout["rt_force_abs_checksum"])
        payload.update(
            {
                "native_force_abs_checksum": native_abs_checksum,
                "author_rt_force_abs_checksum": author_abs_checksum,
                "abs_checksum_relative_error": abs(native_abs_checksum - author_abs_checksum)
                / max(abs(author_abs_checksum), 1.0),
            }
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Goal4766 benchmark-ready probe for the native V4 RT-BarnesHut "
            "author-semantics RT-core candidate. Splits cold/warm native runs "
            "and optionally compares checksum/timing with the authors' binary. "
            "This does not authorize public speed or paper-reproduction claims."
        )
    )
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--file-type", required=True, choices=("treelogy", "csv"))
    parser.add_argument("--limit", required=True, type=int)
    parser.add_argument("--optix-lib", default=None, type=Path)
    parser.add_argument("--repeat", default=3, type=int)
    parser.add_argument("--author-binary", default=None, type=Path)
    parser.add_argument("--author-command-prefix", nargs="*", default=())
    parser.add_argument("--trimmed-dataset", default=None, type=Path)
    parser.add_argument("--goal-label", default="Goal4766")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.repeat < 2:
        raise ValueError("repeat must be at least 2 so cold and warm runs can be separated")
    if args.limit <= 0:
        raise ValueError("limit must be positive")

    try:
        import cupy as cp
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Goal4766 native benchmark-ready probe requires cupy and numpy") from exc

    dataset = load_rt_barneshut_author_dataset(
        args.dataset,
        file_type=args.file_type,
        limit=args.limit,
    )
    point_ids = cp.asarray(np.asarray([point.id for point in dataset.points], dtype=np.uint64))
    point_x = cp.asarray(np.asarray([point.x for point in dataset.points], dtype=np.float32))
    point_y = cp.asarray(np.asarray([point.y for point in dataset.points], dtype=np.float32))
    point_z = cp.asarray(np.asarray([point.z for point in dataset.points], dtype=np.float32))
    point_mass = cp.asarray(np.asarray([point.mass for point in dataset.points], dtype=np.float32))

    native_runs = []
    for iteration in range(args.repeat):
        start = time.perf_counter()
        route = run_v4_rt_barneshut_native_author_route(
            point_ids_device_ptr=int(point_ids.data.ptr),
            point_x_device_ptr=int(point_x.data.ptr),
            point_y_device_ptr=int(point_y.data.ptr),
            point_z_device_ptr=int(point_z.data.ptr),
            point_mass_device_ptr=int(point_mass.data.ptr),
            point_count=dataset.point_count,
            theta=0.5,
            optix_library=args.optix_lib,
        )
        wall = time.perf_counter() - start
        row = route.as_dict()
        row["iteration"] = iteration + 1
        row["python_wall_seconds"] = wall
        native_runs.append(row)

    cold_run = native_runs[0]
    warm_runs = native_runs[1:]
    warm_rt_seconds = [
        value for value in (_rt_force_seconds(run) for run in warm_runs) if value is not None
    ]
    warm_execution_seconds = [
        value for value in (_execution_seconds(run) for run in warm_runs) if value is not None
    ]
    warm_checksums = [float(run["force_checksum"]) for run in warm_runs]
    checksum_stable = max(warm_checksums) - min(warm_checksums) <= max(abs(warm_checksums[0]), 1.0) * 1.0e-6

    author_payload: dict[str, object] | None = None
    if args.author_binary is not None:
        if args.trimmed_dataset is None:
            raise ValueError("--trimmed-dataset is required when --author-binary is provided")
        trimmed = write_trimmed_rt_barneshut_author_dataset(
            args.dataset,
            args.trimmed_dataset,
            file_type=args.file_type,
            limit=args.limit,
        )
        cmd = tuple(
            str(part)
            for part in (
                *tuple(args.author_command_prefix),
                args.author_binary,
                args.file_type,
                trimmed,
            )
        )
        start = time.perf_counter()
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        author_wall = time.perf_counter() - start
        parsed = parse_rt_barneshut_author_stdout(proc.stdout)
        author_payload = {
            "cmd": cmd,
            "returncode": proc.returncode,
            "wall_seconds": author_wall,
            "parsed_stdout": parsed,
            "stdout_tail": _tail(proc.stdout),
            "stderr_tail": _tail(proc.stderr),
            "checksum_validation_against_native_warm_last": _author_checksum_validation(
                native_checksum=float(warm_runs[-1]["force_checksum"]),
                native_abs_checksum=float(warm_runs[-1]["force_abs_checksum"]),
                parsed_stdout=parsed,
            ),
        }

    payload: dict[str, object] = {
        "goal": args.goal_label,
        "probe": "native_rt_barneshut_author_benchmark_ready",
        "dataset": dataset.without_points(),
        "repeat": args.repeat,
        "native_runs": native_runs,
        "summary": {
            "cold_rt_force_seconds": _rt_force_seconds(cold_run),
            "cold_execution_seconds": _execution_seconds(cold_run),
            "warm_rt_force_seconds_min": min(warm_rt_seconds) if warm_rt_seconds else None,
            "warm_rt_force_seconds_median": statistics.median(warm_rt_seconds)
            if warm_rt_seconds
            else None,
            "warm_execution_seconds_min": min(warm_execution_seconds)
            if warm_execution_seconds
            else None,
            "warm_execution_seconds_median": statistics.median(warm_execution_seconds)
            if warm_execution_seconds
            else None,
            "warm_checksum_stable": checksum_stable,
            "implementation_status_codes": sorted(
                {int(run["implementation_status_code"]) for run in native_runs}
            ),
            "all_native_runs_rt_core": all(
                bool(run["claim_boundary"]["rt_core_execution"]) for run in native_runs
            ),
            "any_native_run_host_fallback": any(
                bool(run["claim_boundary"]["host_fallback_used"]) for run in native_runs
            ),
            "public_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
        "author_binary": author_payload,
        "claim_boundary": {
            "same_input_author_contract": True,
            "rt_core_execution": True,
            "native_v4_operator_candidate": True,
            "host_fallback_used": False,
            "input_columns_downloaded_for_tree_build": True,
            "public_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "v2_v3_v4_author_speed_table_authorized": False,
            "purpose": "benchmark-readiness evidence, not release authorization",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))

    if not checksum_stable:
        return 2
    if author_payload is not None:
        if int(author_payload["returncode"]) != 0:
            return 3
        validation = author_payload["checksum_validation_against_native_warm_last"]
        if isinstance(validation, dict) and validation.get("available") and not validation.get(
            "passes_float_output_tolerance"
        ):
            return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
