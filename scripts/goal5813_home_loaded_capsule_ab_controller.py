#!/usr/bin/env python3
"""Run a non-formal Home A/B matrix over two exact RTDL source roots.

Every child executes the existing Goal5810 worker with ``--arm rtdl`` in a
fresh process and cache root.  The controller changes only ``PYTHONPATH`` and
the child working directory to select either the predecessor or successor
source.  It then verifies the implementation module actually imported by the
worker against the source arm's predeclared SHA-256.

The matrix is descriptive engineering evidence only.  It has no threshold,
pass/fail performance claim, formal timing, retry, replacement, or row
selection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, Mapping

from scripts import goal5810_home_two_app_diagnostic_controller as goal5810


SCHEMA = "rtdl.goal5813.home_loaded_capsule_ab_matrix.v1"
STATUS = "COMPLETE__HOME_PASCAL_NONFORMAL_LOADED_CAPSULE_AB_MATRIX"
ARMS = ("predecessor", "successor")
FIRST_APPS = ("relation", "triangle")
PHASES = goal5810.PHASES
IMPLEMENTATION_RELATIVE_PATH = Path("src/rtdsl/v4_rtdlexe.py")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _file_row(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _require_sha256(value: str, *, label: str) -> str:
    normalized = value.lower()
    if len(normalized) != 64 \
            or any(character not in "0123456789abcdef"
                   for character in normalized):
        raise RuntimeError(f"Goal5813 invalid {label} SHA-256")
    return normalized


def _admit_source_arm(
    *, name: str, root: Path, expected_implementation_sha256: str,
) -> dict[str, Any]:
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise RuntimeError(f"Goal5813 {name} source root is not a directory")
    implementation = (resolved_root / IMPLEMENTATION_RELATIVE_PATH).resolve(
        strict=True)
    expected = _require_sha256(
        expected_implementation_sha256,
        label=f"{name} implementation")
    observed = _sha(implementation)
    if observed != expected:
        raise RuntimeError({
            "Goal5813_source_implementation_sha256_differs": name,
            "expected": expected,
            "observed": observed,
            "path": str(implementation),
        })
    return {
        "name": name,
        "source_root": resolved_root,
        "src_root": (resolved_root / "src").resolve(strict=True),
        "implementation": implementation,
        "expected_implementation_sha256": expected,
    }


def _duration(result: Mapping[str, Any], phase: str) -> int:
    value = result["phase_times_absolute"]["phases"][phase]["duration_ns"]
    if type(value) is not int or value <= 0:
        raise RuntimeError(f"Goal5813 invalid phase duration: {phase}")
    return value


def _edge(result: Mapping[str, Any], phase: str, edge: str) -> int:
    value = result["phase_times_absolute"]["phases"][phase][
        f"{edge}_perf_counter_ns"]
    if type(value) is not int or value < 0:
        raise RuntimeError(f"Goal5813 invalid phase edge: {phase}.{edge}")
    return value


def _continuous_walls(result: Mapping[str, Any]) -> dict[str, int]:
    second_output_end = _edge(
        result, "second_app_first_exact_execute", "end")
    values = {
        "input_admission_start_to_second_exact_output": (
            second_output_end - _edge(result, "input_admission", "start")),
        "first_session_admission_start_to_second_exact_output": (
            second_output_end
            - _edge(result, "first_session_admission", "start")),
        "first_app_prepare_start_to_second_exact_output": (
            second_output_end - _edge(result, "first_app_prepare", "start")),
    }
    if any(type(value) is not int or value <= 0 for value in values.values()):
        raise RuntimeError("Goal5813 invalid continuous wall")
    return values


def _condition_summary(rows: list[dict[str, Any]]) -> dict[str, object]:
    if not rows:
        raise RuntimeError("Goal5813 condition has no retained rows")
    phase_medians = {
        phase: statistics.median(_duration(row, phase) for row in rows)
        for phase in PHASES
    }
    continuous_medians = {
        name: statistics.median(
            _continuous_walls(row)[name] for row in rows)
        for name in _continuous_walls(rows[0])
    }
    return {
        "sample_count": len(rows),
        "all_structurally_valid_rows_retained": True,
        "phase_median_ns": phase_medians,
        "phase_median_ms": {
            key: value / 1_000_000.0
            for key, value in phase_medians.items()
        },
        "continuous_median_ns": continuous_medians,
        "continuous_median_ms": {
            key: value / 1_000_000.0
            for key, value in continuous_medians.items()
        },
    }


def _child_environment(arm: Mapping[str, Any]) -> dict[str, str]:
    environment = os.environ.copy()
    # Deliberately do not append an inherited PYTHONPATH: the selected exact
    # source root is the complete experiment-side import authority.
    environment["PYTHONPATH"] = os.pathsep.join((
        str(arm["src_root"]), str(arm["source_root"]),
    ))
    return environment


def _verify_worker_arm(
    result: Mapping[str, Any], *, arm: Mapping[str, Any], first_app: str,
) -> None:
    if result.get("scope", {}).get("arm") != "RTDL_SHARED_RUNTIME_SESSION" \
            or result.get("app_order", [None])[0] != first_app:
        raise RuntimeError("Goal5813 worker condition differs")
    module = result.get("runtime", {}).get("implementation_module")
    if not isinstance(module, Mapping):
        raise RuntimeError("Goal5813 worker implementation identity absent")
    expected_path = arm["implementation"]
    try:
        observed_path = Path(str(module.get("path"))).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise RuntimeError(
            "Goal5813 worker implementation path is unavailable") from error
    if module.get("sha256") != arm["expected_implementation_sha256"] \
            or observed_path != expected_path \
            or _sha(observed_path) != arm["expected_implementation_sha256"]:
        raise RuntimeError({
            "Goal5813_worker_imported_wrong_implementation": arm["name"],
            "expected_path": str(expected_path),
            "expected_sha256": arm["expected_implementation_sha256"],
            "observed": dict(module),
        })


def _ratio(numerator: float | int, denominator: float | int) -> float:
    if denominator <= 0:
        raise RuntimeError("Goal5813 ratio denominator is nonpositive")
    return numerator / denominator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--expected-target-manifest-sha256", required=True)
    parser.add_argument(
        "--predecessor-source-root", "--predecessor-root",
        dest="predecessor_source_root", type=Path, required=True)
    parser.add_argument(
        "--expected-predecessor-implementation-sha256",
        "--predecessor-implementation-sha256",
        dest="predecessor_implementation_sha256", required=True)
    parser.add_argument(
        "--successor-source-root", "--successor-root",
        dest="successor_source_root", type=Path, required=True)
    parser.add_argument(
        "--expected-successor-implementation-sha256",
        "--successor-implementation-sha256",
        dest="successor_implementation_sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--blocks", type=int, default=4)
    args = parser.parse_args()

    if args.blocks < 1 or args.blocks > 16:
        raise RuntimeError("Goal5813 block count is outside 1..16")
    output_root = args.output_root.absolute()
    output_path = args.output.absolute()
    if output_root.exists() or output_path.exists():
        raise RuntimeError("Goal5813 controller output already exists")

    worker = args.worker.resolve(strict=True)
    target = args.target_manifest.resolve(strict=True)
    target_sha256 = _require_sha256(
        args.expected_target_manifest_sha256, label="target manifest")
    if _sha(target) != target_sha256:
        raise RuntimeError("Goal5813 controller target SHA-256 differs")

    arm_rows = {
        "predecessor": _admit_source_arm(
            name="predecessor", root=args.predecessor_source_root,
            expected_implementation_sha256=(
                args.predecessor_implementation_sha256)),
        "successor": _admit_source_arm(
            name="successor", root=args.successor_source_root,
            expected_implementation_sha256=(
                args.successor_implementation_sha256)),
    }
    if arm_rows["predecessor"]["expected_implementation_sha256"] \
            == arm_rows["successor"]["expected_implementation_sha256"]:
        raise RuntimeError("Goal5813 predecessor and successor are identical")

    output_root.mkdir(parents=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    journal: list[dict[str, Any]] = []
    results: dict[tuple[str, str], list[dict[str, Any]]] = {
        (first, arm): [] for first in FIRST_APPS for arm in ARMS
    }
    worker_index = 0
    for block in range(args.blocks):
        first_apps = (
            FIRST_APPS if block % 2 == 0 else tuple(reversed(FIRST_APPS)))
        source_order = (
            ("predecessor", "successor", "predecessor", "successor")
            if block % 2 == 0 else
            ("successor", "predecessor", "successor", "predecessor")
        )
        for first_app in first_apps:
            for slot, arm_name in enumerate(source_order):
                arm = arm_rows[arm_name]
                stem = (
                    f"worker_{worker_index:03d}_block_{block:02d}_"
                    f"{first_app}_first_{arm_name}_slot_{slot}")
                output = output_root / f"{stem}.json"
                cache = output_root / f"{stem}_cache"
                stdout_path = output_root / f"{stem}.stdout"
                stderr_path = output_root / f"{stem}.stderr"
                command = [
                    sys.executable, "-B", str(worker),
                    "--arm", "rtdl",
                    "--target-manifest", str(target),
                    "--expected-target-manifest-sha256", target_sha256,
                    "--first-app", first_app,
                    "--cache-root", str(cache),
                    "--output", str(output),
                ]
                child_environment = _child_environment(arm)
                process = subprocess.run(
                    command, text=True, capture_output=True, check=False,
                    cwd=str(arm["source_root"]), env=child_environment)
                stdout_path.write_text(process.stdout, encoding="utf-8")
                stderr_path.write_text(process.stderr, encoding="utf-8")
                row: dict[str, Any] = {
                    "worker_index": worker_index,
                    "block": block,
                    "first_app": first_app,
                    "source_arm": arm_name,
                    "slot": slot,
                    "returncode": process.returncode,
                    "child_cwd": str(arm["source_root"]),
                    "child_pythonpath": child_environment["PYTHONPATH"],
                    "output_path": str(output),
                    "stdout": _file_row(stdout_path),
                    "stderr": _file_row(stderr_path),
                }
                journal.append(row)
                if process.returncode != 0:
                    raise RuntimeError({"Goal5813_worker_failed": row})
                result = goal5810._read_result(output)
                _verify_worker_arm(
                    result, arm=arm, first_app=first_app)
                row["output"] = _file_row(output)
                row["process_pid"] = result["process_pid"]
                row["implementation_module"] = dict(
                    result["runtime"]["implementation_module"])
                results[(first_app, arm_name)].append(result)
                worker_index += 1

    expected_per_condition = args.blocks * 2
    if any(len(rows) != expected_per_condition for rows in results.values()):
        raise RuntimeError("Goal5813 did not retain every scheduled valid row")

    conditions = {
        f"{first_app}_first/{arm_name}": _condition_summary(
            results[(first_app, arm_name)])
        for first_app in FIRST_APPS for arm_name in ARMS
    }
    comparisons: dict[str, Any] = {}
    for first_app in FIRST_APPS:
        predecessor = conditions[f"{first_app}_first/predecessor"]
        successor = conditions[f"{first_app}_first/successor"]
        comparisons[first_app] = {
            "phase_ratio_of_medians_successor_over_predecessor": {
                phase: _ratio(
                    successor["phase_median_ns"][phase],
                    predecessor["phase_median_ns"][phase])
                for phase in PHASES
            },
            "continuous_ratio_of_medians_successor_over_predecessor": {
                name: _ratio(
                    successor["continuous_median_ns"][name],
                    predecessor["continuous_median_ns"][name])
                for name in predecessor["continuous_median_ns"]
            },
            "descriptive_only": True,
            "threshold_or_pass_fail_interpretation": None,
        }

    body = {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "diagnostic_only": True,
            "home_pascal_only": True,
            "rt_core_evidence": False,
            "formal_evidence": False,
            "paper_evidence": False,
            "claim_authorized": False,
            "threshold_or_pass_fail_gate_present": False,
            "all_structurally_valid_results_retained": True,
            "retry_count": 0,
            "replacement_count": 0,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
        },
        "design": {
            "block_count": args.blocks,
            "worker_count": worker_index,
            "fresh_process_per_worker": True,
            "fresh_cache_root_per_worker": True,
            "worker_arm_always_rtdl": True,
            "source_arm_order_alternates_within_each_first_app": True,
            "source_arm_start_reversed_by_block": True,
            "first_app_order_reversed_by_block": True,
            "first_app_orders": list(FIRST_APPS),
            "source_arms": list(ARMS),
            "condition_sample_count": expected_per_condition,
            "continuous_walls": list(_continuous_walls(
                next(iter(results.values()))[0])),
            "every_goal5810_phase_median_reported": True,
        },
        "inputs": {
            "controller": _file_row(Path(__file__)),
            "worker": _file_row(worker),
            "target_manifest": _file_row(target),
            "python_executable": _file_row(Path(sys.executable)),
            "source_arms": {
                name: {
                    "source_root": str(row["source_root"]),
                    "src_root": str(row["src_root"]),
                    "implementation_module": _file_row(row["implementation"]),
                }
                for name, row in arm_rows.items()
            },
        },
        "conditions": conditions,
        "descriptive_comparisons": comparisons,
        "journal": journal,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    result = {**body, "matrix_sha256": _digest(body)}
    with output_path.open("xb") as handle:
        handle.write(_canonical(result) + b"\n")
    print(json.dumps({
        "status": STATUS,
        "worker_count": worker_index,
        "matrix_sha256": result["matrix_sha256"],
        "output": str(output_path.resolve(strict=True)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
