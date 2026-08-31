#!/usr/bin/env python3
"""Measure natural Goal5810 PyOptiX shared-context admission leaves on Home.

This is a descriptive engineering diagnostic only.  It reuses the unchanged
Goal5810 two-application PyOptiX path and replaces only its Python context-
admission helper with an operation-for-operation equivalent that records five
leaf call durations.  It does not edit or substitute product/runtime bytes and
does not emit registered performance timings or paper evidence.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

from scripts import goal5810_home_two_app_phase_diagnostic as home


SCHEMA = "rtdl.goal5812.home_pyoptix_context_leaf_diagnostic.v1"
STATUS = "COMPLETE__HOME_PASCAL_NONFORMAL_PYOPTIX_CONTEXT_LEAF_DIAGNOSTIC"
LEAF_ORDER = (
    "cupy.cuda.runtime.free_zero",
    "optix.init",
    "optix.DeviceContextOptions",
    "optix.deviceContextCreate",
    "optix.context.setCacheEnabled",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class _ContextLeafRecorder:
    """Drop-in implementation of Goal5810's natural context admission."""

    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []
        self.admission_start_ns: int | None = None
        self.admission_end_ns: int | None = None
        self._used = False

    def _measure(
        self, name: str, operation: Callable[[], Any],
    ) -> Any:
        start = time.perf_counter_ns()
        outcome = "RETURNED"
        try:
            return operation()
        except BaseException:
            outcome = "RAISED"
            raise
        finally:
            end = time.perf_counter_ns()
            self.events.append({
                "ordinal": len(self.events),
                "operation": name,
                "called": True,
                "outcome": outcome,
                "start_perf_counter_ns": start,
                "end_perf_counter_ns": end,
                "duration_ns": end - start,
                "duration_ms": (end - start) / 1_000_000.0,
            })

    def _record_absent(self, name: str) -> None:
        instant = time.perf_counter_ns()
        self.events.append({
            "ordinal": len(self.events),
            "operation": name,
            "called": False,
            "outcome": "NOT_EXPOSED__NATURAL_PATH_SKIPPED",
            "start_perf_counter_ns": instant,
            "end_perf_counter_ns": instant,
            "duration_ns": 0,
            "duration_ms": 0.0,
        })

    def admit_shared_context(
        self, *, arm: Any, baseline: Any,
    ) -> tuple[Any, Any]:
        """Execute the exact natural helper operations with leaf clocks."""

        if self._used:
            raise RuntimeError("Goal5812 shared-context admission called twice")
        self._used = True
        self.admission_start_ns = time.perf_counter_ns()
        try:
            # Keep this sequence identical to
            # pyoptix_scalar_arm._make_validation_off_context.
            self._measure(
                "cupy.cuda.runtime.free_zero",
                lambda: baseline.cp.cuda.runtime.free(0),
            )
            optix_init = getattr(baseline.optix, "init", None)
            if callable(optix_init):
                self._measure("optix.init", optix_init)
            else:
                self._record_absent("optix.init")
            options = self._measure(
                "optix.DeviceContextOptions",
                baseline.optix.DeviceContextOptions,
            )
            validation_off = getattr(
                baseline.optix, "DEVICE_CONTEXT_VALIDATION_MODE_OFF", None)
            if validation_off is None:
                raise RuntimeError(
                    "PyOptiX does not expose validation-mode OFF")
            options.validationMode = validation_off
            context = self._measure(
                "optix.deviceContextCreate",
                lambda: baseline.optix.deviceContextCreate(0, options),
            )

            # Keep this sequence identical to
            # goal5809_pyoptix_two_app_pilot._admit_shared_context.
            set_cache_enabled = getattr(context, "setCacheEnabled", None)
            if not callable(set_cache_enabled):
                raise RuntimeError(
                    "PyOptiX context does not expose disk-cache disable control")
            self._measure(
                "optix.context.setCacheEnabled",
                lambda: set_cache_enabled(False),
            )
            return context, None
        finally:
            self.admission_end_ns = time.perf_counter_ns()

    def result(self, *, outer_admission_wall_ns: int) -> dict[str, object]:
        if self.admission_start_ns is None or self.admission_end_ns is None:
            raise RuntimeError("Goal5812 context admission was not observed")
        observed_order = tuple(
            str(event["operation"]) for event in self.events)
        if observed_order != LEAF_ORDER:
            raise RuntimeError({
                "Goal5812_context_leaf_order_differs": observed_order,
                "expected": LEAF_ORDER,
            })
        internal_wall = self.admission_end_ns - self.admission_start_ns
        leaf_sum = sum(int(event["duration_ns"]) for event in self.events)
        if leaf_sum > internal_wall or internal_wall > outer_admission_wall_ns:
            raise RuntimeError({
                "Goal5812_context_leaf_accounting_invalid": {
                    "leaf_sum_ns": leaf_sum,
                    "internal_wall_ns": internal_wall,
                    "outer_wall_ns": outer_admission_wall_ns,
                },
            })
        return {
            "clock": "time.perf_counter_ns",
            "events": list(self.events),
            "required_leaf_count": len(LEAF_ORDER),
            "required_leaf_order": list(LEAF_ORDER),
            "shared_context_admission_internal_wall_ns": internal_wall,
            "shared_context_admission_internal_wall_ms": (
                internal_wall / 1_000_000.0),
            "leaf_duration_sum_ns": leaf_sum,
            "leaf_duration_sum_ms": leaf_sum / 1_000_000.0,
            "python_glue_residual_inside_admission_ns": internal_wall - leaf_sum,
            "goal5810_outer_first_session_admission_wall_ns": (
                outer_admission_wall_ns),
            "goal5810_outer_wrapper_residual_ns": (
                outer_admission_wall_ns - internal_wall),
            "leaf_durations_are_sequential_and_additive_within_internal_wall":
                True,
            "no_cuda_or_optix_synchronization_added_by_recorder": True,
        }


def _run(
    *, target_path: Path, target_sha256: str, first_task: str,
) -> dict[str, object]:
    recorder = _ContextLeafRecorder()
    original_admission = home.py_worker._admit_shared_context
    home.py_worker._admit_shared_context = recorder.admit_shared_context
    worker_call_start_ns = time.perf_counter_ns()
    try:
        result = home._run_pyoptix(
            target_path=target_path,
            target_sha256=target_sha256,
            first_task=first_task,
        )
    finally:
        home.py_worker._admit_shared_context = original_admission

    phases = result["phase_times_absolute"]["phases"]
    admission = phases["first_session_admission"]
    first_prepare = phases["first_app_prepare"]
    second_execute = phases["second_app_first_exact_execute"]
    input_admission = phases["input_admission"]
    second_output_end_ns = int(second_execute["end_perf_counter_ns"])
    outer_admission_wall_ns = int(admission["duration_ns"])
    applications = result["applications"]
    if set(applications) != set(home.TASKS) or any(
            row.get("exact_oracle_passed") is not True
            or row.get("device_status_ok") is not True
            for row in applications.values()):
        raise RuntimeError("Goal5812 exact application evidence differs")

    result["context_leaf_timing"] = recorder.result(
        outer_admission_wall_ns=outer_admission_wall_ns)
    result["continuous_walls_through_second_exact_output"] = {
        "worker_call_start_to_second_exact_output_ns": (
            second_output_end_ns - worker_call_start_ns),
        "worker_call_start_to_second_exact_output_ms": (
            second_output_end_ns - worker_call_start_ns) / 1_000_000.0,
        "input_admission_start_to_second_exact_output_ns": (
            second_output_end_ns - int(input_admission["start_perf_counter_ns"])),
        "shared_context_admission_start_to_second_exact_output_ns": (
            second_output_end_ns - int(admission["start_perf_counter_ns"])),
        "first_prepare_start_to_second_exact_output_ns": (
            second_output_end_ns - int(first_prepare["start_perf_counter_ns"])),
        "continuous_wall_includes_all_interphase_gaps": True,
        "second_exact_output_precedes_close": True,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-target-manifest-sha256", required=True)
    parser.add_argument("--first-app", choices=home.TASKS, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5812 output already exists")

    cache_environment = home._isolate_caches(args.cache_root)
    result = _run(
        target_path=args.target_manifest,
        target_sha256=args.expected_target_manifest_sha256,
        first_task=args.first_app,
    )
    result_scope = dict(result["scope"])
    result_scope.update({
        "arm": "PYOPTIX_SHARED_DEVICE_CONTEXT",
        "diagnostic_only": True,
        "home_pascal_only": True,
        "goal5810_outer_two_app_path_reused": True,
        "shared_context_helper_temporarily_replaced_by_timing_equivalent":
            True,
        "natural_context_operation_order_preserved": True,
        "product_source_edited_by_experiment": False,
        "product_runtime_bytes_substituted": False,
        "instrumentation_scope": "PYTHON_CALL_BOUNDARIES_ONLY",
        "formal_evidence": False,
        "paper_evidence": False,
        "claim_authorized": False,
        "threshold_or_pass_fail_gate_present": False,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    })
    result["scope"] = result_scope
    body = {
        "schema": SCHEMA,
        "status": STATUS,
        "process_pid": os.getpid(),
        "python": {
            "executable": str(Path(sys.executable).absolute()),
            "version": sys.version,
        },
        "cuda": home._cuda_identity(),
        "loader_environment": {
            "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH"),
            "LD_PRELOAD": os.environ.get("LD_PRELOAD"),
        },
        "isolated_cache_environment": cache_environment,
        "target_manifest": home._file_row(args.target_manifest),
        "worker_source": home._file_row(Path(__file__)),
        "goal5810_worker_source": home._module_row(home),
        **result,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    sealed = {**body, "diagnostic_sha256": _digest(body)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(_canonical(sealed) + b"\n")
    print(json.dumps({
        "status": STATUS,
        "first_app": args.first_app,
        "output": str(args.output.resolve(strict=True)),
        "diagnostic_sha256": sealed["diagnostic_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
