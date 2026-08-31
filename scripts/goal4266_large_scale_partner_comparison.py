#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402


SCHEMA = "rtdl.goal4266.large_scale_cupy_numba_partner_comparison.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4266_large_scale_partner_comparison" / "summary.json"
GROUPED_OPERATIONS = ("segmented_count_i64", "segmented_sum_f64", "segmented_min_f64", "segmented_max_f64")
PARTNERS = ("cupy", "numba")


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "partner_winner_claim_authorized": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    if not values:
        return math.nan
    return float(statistics.median(values))


def _sync_partner(partner: str, modules: dict[str, Any]) -> None:
    if partner == "cupy":
        modules["cupy"].cuda.runtime.deviceSynchronize()
    elif partner == "numba":
        modules["cuda"].synchronize()
    else:
        raise ValueError(f"unsupported partner: {partner}")


def _to_numpy(value: Any, modules: dict[str, Any]) -> Any:
    np = modules["numpy"]
    if hasattr(value, "copy_to_host"):
        return value.copy_to_host()
    if hasattr(value, "get"):
        return value.get()
    return np.asarray(value)


def _time_until_floor(
    *,
    label: str,
    partner: str,
    fn: Callable[[], Any],
    modules: dict[str, Any],
    warmup: int,
    target_hot_total_sec: float,
    max_repeat: int,
    progress_every: int,
) -> tuple[Any, dict[str, Any]]:
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if max_repeat <= 0:
        raise ValueError("max_repeat must be positive")
    if target_hot_total_sec <= 0:
        raise ValueError("target_hot_total_sec must be positive")

    last_result: Any = None
    for iteration in range(warmup):
        last_result = fn()
        _sync_partner(partner, modules)
        print(f"[goal4266] {label} warmup {iteration + 1}/{warmup}", flush=True)

    measured: list[float] = []
    total = 0.0
    for iteration in range(max_repeat):
        started = time.perf_counter()
        last_result = fn()
        _sync_partner(partner, modules)
        elapsed = time.perf_counter() - started
        measured.append(elapsed)
        total += elapsed
        should_print = (
            iteration == 0
            or total >= target_hot_total_sec
            or (progress_every > 0 and (iteration + 1) % progress_every == 0)
        )
        if should_print:
            print(
                f"[goal4266] {label} repeat {iteration + 1}/{max_repeat} "
                f"elapsed={elapsed:.6f}s hot_total={total:.6f}s target={target_hot_total_sec:.3f}s",
                flush=True,
            )
        if total >= target_hot_total_sec:
            break

    return last_result, {
        "hot_total_sec": float(total),
        "hot_median_sec": _median(measured),
        "hot_min_sec": min(measured) if measured else math.nan,
        "hot_max_sec": max(measured) if measured else math.nan,
        "hot_repeat_secs": measured,
        "repeat": len(measured),
        "warmup": warmup,
        "target_hot_total_sec": float(target_hot_total_sec),
        "meets_one_second_floor": bool(total >= 1.0),
        "meets_requested_floor": bool(total >= target_hot_total_sec),
        "max_repeat_exhausted": bool(total < target_hot_total_sec),
    }


def _time_fixed_repeats(
    *,
    label: str,
    partner: str,
    fn: Callable[[], Any],
    modules: dict[str, Any],
    warmup: int,
    repeat: int,
    target_hot_total_sec: float,
    progress_every: int,
) -> tuple[Any, dict[str, Any]]:
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if repeat <= 0:
        raise ValueError("repeat must be positive")

    last_result: Any = None
    for iteration in range(warmup):
        last_result = fn()
        _sync_partner(partner, modules)
        print(f"[goal4266] {label} fixed warmup {iteration + 1}/{warmup}", flush=True)

    measured: list[float] = []
    total = 0.0
    for iteration in range(repeat):
        started = time.perf_counter()
        last_result = fn()
        _sync_partner(partner, modules)
        elapsed = time.perf_counter() - started
        measured.append(elapsed)
        total += elapsed
        should_print = (
            iteration == 0
            or iteration + 1 == repeat
            or (progress_every > 0 and (iteration + 1) % progress_every == 0)
        )
        if should_print:
            print(
                f"[goal4266] {label} fixed repeat {iteration + 1}/{repeat} "
                f"elapsed={elapsed:.6f}s hot_total={total:.6f}s target={target_hot_total_sec:.3f}s",
                flush=True,
            )

    return last_result, {
        "hot_total_sec": float(total),
        "hot_median_sec": _median(measured),
        "hot_min_sec": min(measured) if measured else math.nan,
        "hot_max_sec": max(measured) if measured else math.nan,
        "hot_repeat_secs": measured,
        "repeat": repeat,
        "warmup": warmup,
        "target_hot_total_sec": float(target_hot_total_sec),
        "same_repeat_count_for_both_partners": True,
        "meets_one_second_floor": bool(total >= 1.0),
        "meets_requested_floor": bool(total >= target_hot_total_sec),
        "max_repeat_exhausted": False,
    }


def _calibrate_equal_repeat_count(
    *,
    label: str,
    partner_fns: dict[str, Callable[[], Any]],
    modules: dict[str, Any],
    warmup: int,
    calibration_repeat: int,
    calibration_safety_factor: float,
    target_hot_total_sec: float,
    max_repeat: int,
    progress_every: int,
) -> tuple[int, dict[str, Any]]:
    if calibration_repeat <= 0:
        raise ValueError("calibration_repeat must be positive")
    if calibration_safety_factor < 1.0:
        raise ValueError("calibration_safety_factor must be at least 1.0")
    medians: dict[str, float] = {}
    details: dict[str, Any] = {}
    for partner in PARTNERS:
        _result, timing = _time_fixed_repeats(
            label=f"{label}/{partner}/calibration",
            partner=partner,
            fn=partner_fns[partner],
            modules=modules,
            warmup=warmup,
            repeat=calibration_repeat,
            target_hot_total_sec=0.0,
            progress_every=progress_every,
        )
        medians[partner] = float(timing["hot_median_sec"])
        details[partner] = {
            "calibration_repeat": calibration_repeat,
            "hot_median_sec": timing["hot_median_sec"],
            "hot_total_sec": timing["hot_total_sec"],
        }
    fastest_median = min(value for value in medians.values() if value > 0.0)
    repeat = int(math.ceil(float(target_hot_total_sec) * float(calibration_safety_factor) / fastest_median))
    repeat = max(calibration_repeat, min(int(max_repeat), repeat))
    return repeat, {
        "calibration_label": label,
        "partner_medians_sec": medians,
        "calibrated_equal_repeat": repeat,
        "target_hot_total_sec": float(target_hot_total_sec),
        "calibration_safety_factor": float(calibration_safety_factor),
        "max_repeat": int(max_repeat),
        "max_repeat_exhausted": bool(repeat == int(max_repeat)),
        "details": details,
    }


def _make_grouped_host_columns(row_count: int, group_count: int, modules: dict[str, Any]) -> tuple[Any, Any]:
    np = modules["numpy"]
    indices = np.arange(row_count, dtype=np.int64)
    group_ids = ((indices * 31 + 11) % group_count).astype(np.int64, copy=False)
    values = ((indices % 1009).astype(np.float64) + 1.0).astype(np.float64, copy=False)
    return group_ids, values


def _make_compact_host_columns(row_count: int, modules: dict[str, Any]) -> tuple[Any, Any]:
    np = modules["numpy"]
    indices = np.arange(row_count, dtype=np.int64)
    values = (indices * 5 + 101).astype(np.int64, copy=False)
    mask = (((indices % 11) == 2) | ((indices % 29) == 7) | ((indices % 31) == 13)).astype(np.bool_, copy=False)
    return values, mask


def _partner_columns_from_host(host_group_ids: Any, host_values: Any, modules: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cupy = modules["cupy"]
    cuda = modules["cuda"]
    return {
        "cupy": {
            "group_ids": cupy.asarray(host_group_ids, dtype=cupy.int64),
            "values": cupy.asarray(host_values, dtype=cupy.float64),
        },
        "numba": {
            "group_ids": cuda.to_device(host_group_ids),
            "values": cuda.to_device(host_values),
        },
    }


def _compact_partner_columns_from_host(host_values: Any, host_mask: Any, modules: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cupy = modules["cupy"]
    cuda = modules["cuda"]
    return {
        "cupy": {
            "values": cupy.asarray(host_values, dtype=cupy.int64),
            "mask": cupy.asarray(host_mask, dtype=cupy.bool_),
        },
        "numba": {
            "values": cuda.to_device(host_values),
            "mask": cuda.to_device(host_mask),
        },
    }


def _grouped_expected(host_group_ids: Any, host_values: Any, group_count: int, modules: dict[str, Any]) -> dict[str, Any]:
    np = modules["numpy"]
    counts = np.bincount(host_group_ids, minlength=group_count).astype(np.int64)
    sums = np.bincount(host_group_ids, weights=host_values, minlength=group_count).astype(np.float64)
    mins = np.full((group_count,), np.inf, dtype=np.float64)
    maxes = np.full((group_count,), -np.inf, dtype=np.float64)
    if int(host_group_ids.size):
        np.minimum.at(mins, host_group_ids, host_values)
        np.maximum.at(maxes, host_group_ids, host_values)
    return {"counts": counts, "sums": sums, "mins": mins, "maxes": maxes}


def _dense_from_compacted_minmax(outputs: dict[str, Any], *, name: str, group_count: int, initial: float, modules: dict[str, Any]) -> Any:
    np = modules["numpy"]
    if name in outputs and "group_ids" not in outputs:
        return _to_numpy(outputs[name], modules)
    dense = np.full((group_count,), initial, dtype=np.float64)
    group_ids = _to_numpy(outputs["group_ids"], modules).astype(np.int64, copy=False)
    values = _to_numpy(outputs[name], modules).astype(np.float64, copy=False)
    if group_ids.size:
        dense[group_ids] = values
    return dense


def _validate_grouped_operation(operation: str, result: dict[str, Any], expected: dict[str, Any], *, group_count: int, modules: dict[str, Any]) -> dict[str, Any]:
    np = modules["numpy"]
    outputs = result["outputs"]
    if operation == "segmented_count_i64":
        observed = _to_numpy(outputs["counts"], modules).astype(np.int64, copy=False)
        target = expected["counts"]
        match = bool(np.array_equal(observed, target))
        max_abs_error = 0.0
    elif operation == "segmented_sum_f64":
        observed = _to_numpy(outputs["sums"], modules).astype(np.float64, copy=False)
        target = expected["sums"]
        max_abs_error = float(np.max(np.abs(observed - target))) if target.size else 0.0
        match = bool(np.allclose(observed, target, rtol=1.0e-9, atol=1.0e-7))
    elif operation == "segmented_min_f64":
        observed = _dense_from_compacted_minmax(outputs, name="mins", group_count=group_count, initial=math.inf, modules=modules)
        target = expected["mins"]
        finite = np.isfinite(observed) & np.isfinite(target)
        max_abs_error = float(np.max(np.abs(observed[finite] - target[finite]))) if bool(np.any(finite)) else 0.0
        match = bool(np.allclose(observed, target, rtol=0.0, atol=0.0, equal_nan=True))
    elif operation == "segmented_max_f64":
        observed = _dense_from_compacted_minmax(outputs, name="maxes", group_count=group_count, initial=-math.inf, modules=modules)
        target = expected["maxes"]
        finite = np.isfinite(observed) & np.isfinite(target)
        max_abs_error = float(np.max(np.abs(observed[finite] - target[finite]))) if bool(np.any(finite)) else 0.0
        match = bool(np.allclose(observed, target, rtol=0.0, atol=0.0, equal_nan=True))
    else:
        raise ValueError(f"unsupported grouped operation: {operation}")
    return {
        "match_cpu_oracle": match,
        "max_abs_error": max_abs_error,
    }


def _make_grouped_operation_fn(
    *,
    operation: str,
    partner: str,
    columns: dict[str, Any],
    group_count: int,
    block_size: int,
) -> Callable[[], dict[str, Any]]:
    def run_one() -> dict[str, Any]:
        return rt.execute_grouped_reduction_typed_stream_partner_columns(
            group_ids=columns["group_ids"],
            values=None if operation == "segmented_count_i64" else columns["values"],
            group_count=group_count,
            operation=operation,
            partner=partner,
            stream_id=f"goal4266_{operation}_{partner}",
            producer_primitive="caller_supplied_large_scale_partner_comparison_columns",
            block_size=block_size,
        )

    return run_one


def _run_grouped_suite(args: argparse.Namespace, modules: dict[str, Any]) -> dict[str, Any]:
    print(
        f"[goal4266] grouped suite build rows={args.grouped_rows} groups={args.groups}",
        flush=True,
    )
    host_group_ids, host_values = _make_grouped_host_columns(args.grouped_rows, args.groups, modules)
    expected = _grouped_expected(host_group_ids, host_values, args.groups, modules)
    partner_columns = _partner_columns_from_host(host_group_ids, host_values, modules)
    for partner in PARTNERS:
        _sync_partner(partner, modules)

    rows: list[dict[str, Any]] = []
    for operation in GROUPED_OPERATIONS:
        op_row: dict[str, Any] = {
            "contract": operation,
            "input_rows": int(args.grouped_rows),
            "group_count": int(args.groups),
            "partners": {},
        }
        partner_fns: dict[str, Callable[[], dict[str, Any]]] = {}
        for partner in PARTNERS:
            columns = partner_columns[partner]
            partner_fns[partner] = _make_grouped_operation_fn(
                operation=operation,
                partner=partner,
                columns=columns,
                group_count=args.groups,
                block_size=args.block_size,
            )
        equal_repeat, calibration = _calibrate_equal_repeat_count(
            label=operation,
            partner_fns=partner_fns,
            modules=modules,
            warmup=args.warmup,
            calibration_repeat=args.calibration_repeat,
            calibration_safety_factor=args.calibration_safety_factor,
            target_hot_total_sec=args.target_hot_total_sec,
            max_repeat=args.max_repeat,
            progress_every=args.progress_every,
        )
        op_row["equal_repeat"] = equal_repeat
        op_row["calibration"] = calibration
        for partner in PARTNERS:
            result, timing = _time_fixed_repeats(
                label=f"{operation}/{partner}",
                partner=partner,
                fn=partner_fns[partner],
                modules=modules,
                warmup=0,
                repeat=equal_repeat,
                target_hot_total_sec=args.target_hot_total_sec,
                progress_every=args.progress_every,
            )
            validation = _validate_grouped_operation(operation, result, expected, group_count=args.groups, modules=modules)
            op_row["partners"][partner] = {
                **timing,
                **validation,
                "claim_boundary": _claim_boundary(),
            }
        cupy_total = float(op_row["partners"]["cupy"]["hot_total_sec"])
        numba_total = float(op_row["partners"]["numba"]["hot_total_sec"])
        cupy_median = float(op_row["partners"]["cupy"]["hot_median_sec"])
        numba_median = float(op_row["partners"]["numba"]["hot_median_sec"])
        op_row["numba_speedup_vs_cupy_hot_total"] = cupy_total / numba_total if numba_total > 0.0 else None
        op_row["numba_speedup_vs_cupy_hot_median"] = cupy_median / numba_median if numba_median > 0.0 else None
        op_row["cupy_speedup_vs_numba_hot_total"] = numba_total / cupy_total if cupy_total > 0.0 else None
        op_row["cupy_speedup_vs_numba_hot_median"] = numba_median / cupy_median if cupy_median > 0.0 else None
        op_row["time_ratio_cupy_over_numba_hot_total"] = cupy_total / numba_total if numba_total > 0.0 else None
        op_row["time_ratio_numba_over_cupy_hot_total"] = numba_total / cupy_total if cupy_total > 0.0 else None
        op_row["all_match_cpu_oracle"] = all(bool(op_row["partners"][partner]["match_cpu_oracle"]) for partner in PARTNERS)
        rows.append(op_row)

    suite_totals = {
        partner: float(sum(float(row["partners"][partner]["hot_total_sec"]) for row in rows))
        for partner in PARTNERS
    }
    derived_avg = {
        "contract": "avg_as_sum_count",
        "meaning": "average is represented by the generic sum plus count outputs; no separate partner kernel is timed",
        "input_rows": int(args.grouped_rows),
        "group_count": int(args.groups),
        "partners": {
            partner: {
                "derived_from": ("segmented_sum_f64", "segmented_count_i64"),
                "hot_total_sec": float(
                    next(row for row in rows if row["contract"] == "segmented_sum_f64")["partners"][partner]["hot_total_sec"]
                    + next(row for row in rows if row["contract"] == "segmented_count_i64")["partners"][partner]["hot_total_sec"]
                ),
                "claim_boundary": _claim_boundary(),
            }
            for partner in PARTNERS
        },
    }
    return {
        "suite": "raydb_style_unfused_grouped_reductions",
        "input_rows": int(args.grouped_rows),
        "group_count": int(args.groups),
        "operation_rows": rows,
        "derived_rows": [derived_avg],
        "partner_hot_total_sec": suite_totals,
        "numba_speedup_vs_cupy_suite_hot_total": (
            suite_totals["cupy"] / suite_totals["numba"] if suite_totals["numba"] > 0.0 else None
        ),
        "cupy_speedup_vs_numba_suite_hot_total": (
            suite_totals["numba"] / suite_totals["cupy"] if suite_totals["cupy"] > 0.0 else None
        ),
        "all_match_cpu_oracle": all(bool(row["all_match_cpu_oracle"]) for row in rows),
        "all_partner_totals_meet_one_second_floor": all(
            bool(row["partners"][partner]["meets_one_second_floor"])
            for row in rows
            for partner in PARTNERS
        ),
        "claim_boundary": _claim_boundary(),
    }


def _validate_compact(result: dict[str, Any], expected_values: Any, expected_indices: Any, modules: dict[str, Any]) -> dict[str, Any]:
    np = modules["numpy"]
    outputs = result["outputs"]
    observed_values = _to_numpy(outputs["values"], modules).astype(np.int64, copy=False)
    observed_indices = _to_numpy(outputs["original_indices"], modules).astype(np.int64, copy=False)
    values_match = bool(np.array_equal(observed_values, expected_values))
    indices_match = bool(np.array_equal(observed_indices, expected_indices))
    return {
        "match_cpu_oracle": bool(values_match and indices_match),
        "values_match_cpu_oracle": values_match,
        "indices_match_cpu_oracle": indices_match,
        "selected_count": int(expected_indices.size),
        "first_values": tuple(int(value) for value in observed_values[:5]),
        "last_values": tuple(int(value) for value in observed_values[-5:]),
    }


def _make_compact_operation_fn(
    *,
    partner: str,
    columns: dict[str, Any],
    block_size: int,
) -> Callable[[], dict[str, Any]]:
    def run_one() -> dict[str, Any]:
        return rt.execute_compact_mask_typed_stream_partner_columns(
            values=columns["values"],
            mask=columns["mask"],
            partner=partner,
            stream_id=f"goal4266_compact_mask_{partner}",
            producer_primitive="caller_supplied_large_scale_partner_comparison_columns",
            block_size=block_size,
        )

    return run_one


def _run_compact_suite(args: argparse.Namespace, modules: dict[str, Any]) -> dict[str, Any]:
    np = modules["numpy"]
    print(f"[goal4266] compact-mask suite build rows={args.compact_rows}", flush=True)
    host_values, host_mask = _make_compact_host_columns(args.compact_rows, modules)
    expected_indices = np.nonzero(host_mask)[0].astype(np.int64)
    expected_values = host_values[expected_indices].astype(np.int64, copy=False)
    partner_columns = _compact_partner_columns_from_host(host_values, host_mask, modules)
    for partner in PARTNERS:
        _sync_partner(partner, modules)

    row: dict[str, Any] = {
        "contract": "compact_mask_i64",
        "suite": "triangle_candidate_row_compaction",
        "input_rows": int(args.compact_rows),
        "expected_selected_count": int(expected_indices.size),
        "partners": {},
    }
    for partner in PARTNERS:
        columns = partner_columns[partner]
        row.setdefault("_partner_fns", {})[partner] = _make_compact_operation_fn(
            partner=partner,
            columns=columns,
            block_size=args.block_size,
        )
    equal_repeat, calibration = _calibrate_equal_repeat_count(
        label="compact_mask_i64",
        partner_fns=row.pop("_partner_fns"),
        modules=modules,
        warmup=args.warmup,
        calibration_repeat=args.calibration_repeat,
        calibration_safety_factor=args.calibration_safety_factor,
        target_hot_total_sec=args.target_hot_total_sec,
        max_repeat=args.max_repeat,
        progress_every=args.progress_every,
    )
    row["equal_repeat"] = equal_repeat
    row["calibration"] = calibration
    for partner in PARTNERS:
        columns = partner_columns[partner]
        run_one = _make_compact_operation_fn(
            partner=partner,
            columns=columns,
            block_size=args.block_size,
        )

        result, timing = _time_fixed_repeats(
            label=f"compact_mask_i64/{partner}",
            partner=partner,
            fn=run_one,
            modules=modules,
            warmup=0,
            repeat=equal_repeat,
            target_hot_total_sec=args.target_hot_total_sec,
            progress_every=args.progress_every,
        )
        validation = _validate_compact(result, expected_values, expected_indices, modules)
        row["partners"][partner] = {
            **timing,
            **validation,
            "claim_boundary": _claim_boundary(),
        }

    cupy_total = float(row["partners"]["cupy"]["hot_total_sec"])
    numba_total = float(row["partners"]["numba"]["hot_total_sec"])
    cupy_median = float(row["partners"]["cupy"]["hot_median_sec"])
    numba_median = float(row["partners"]["numba"]["hot_median_sec"])
    row["numba_speedup_vs_cupy_hot_total"] = cupy_total / numba_total if numba_total > 0.0 else None
    row["numba_speedup_vs_cupy_hot_median"] = cupy_median / numba_median if numba_median > 0.0 else None
    row["cupy_speedup_vs_numba_hot_total"] = numba_total / cupy_total if cupy_total > 0.0 else None
    row["cupy_speedup_vs_numba_hot_median"] = numba_median / cupy_median if cupy_median > 0.0 else None
    row["time_ratio_cupy_over_numba_hot_total"] = cupy_total / numba_total if numba_total > 0.0 else None
    row["time_ratio_numba_over_cupy_hot_total"] = numba_total / cupy_total if cupy_total > 0.0 else None
    row["all_match_cpu_oracle"] = all(bool(row["partners"][partner]["match_cpu_oracle"]) for partner in PARTNERS)
    row["all_partner_totals_meet_one_second_floor"] = all(
        bool(row["partners"][partner]["meets_one_second_floor"]) for partner in PARTNERS
    )
    row["claim_boundary"] = _claim_boundary()
    return row


def _load_gpu_modules() -> dict[str, Any]:
    try:
        try:
            import _numba_cuda_redirector  # noqa: F401
        except ImportError:
            pass
        import cupy
        import numpy
        import numba
        from numba import cuda
    except Exception as exc:
        raise RuntimeError(f"required partner modules are unavailable: {exc}") from exc
    if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
        raise RuntimeError("CuPy reports no CUDA device")
    if not cuda.is_available():
        raise RuntimeError("Numba CUDA is not available")
    return {"cupy": cupy, "numpy": numpy, "numba": numba, "cuda": cuda}


def _dry_run(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": "Goal4266",
        "dry_run": True,
        "contracts": {
            "raydb_style_unfused_grouped_reductions": {
                "operations": GROUPED_OPERATIONS,
                "derived": ("avg_as_sum_count",),
                "grouped_rows": int(args.grouped_rows),
                "groups": int(args.groups),
            },
            "triangle_candidate_row_compaction": {
                "operations": ("compact_mask_i64",),
                "compact_rows": int(args.compact_rows),
            },
        },
        "partners": PARTNERS,
        "target_hot_total_sec": float(args.target_hot_total_sec),
        "measurement_rule": "repeat each partner/contract until aggregate hot time reaches the requested floor or max_repeat is exhausted",
        "fair_comparison_rule": "GPU runs calibrate a single repeat count per contract and use that same repeat count for CuPy and Numba",
        "claim_boundary": _claim_boundary(),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.dry_run:
        return _dry_run(args)
    modules = _load_gpu_modules()
    grouped = _run_grouped_suite(args, modules)
    compact = _run_compact_suite(args, modules)
    all_rows: list[dict[str, Any]] = list(grouped["operation_rows"]) + [compact]
    subsecond = [
        {
            "contract": row["contract"],
            "partner": partner,
            "hot_total_sec": float(row["partners"][partner]["hot_total_sec"]),
        }
        for row in all_rows
        for partner in PARTNERS
        if float(row["partners"][partner]["hot_total_sec"]) < 1.0
    ]
    return {
        "schema": SCHEMA,
        "goal": "Goal4266",
        "dry_run": False,
        "generated_at_unix": time.time(),
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_dirty_tracked": _command_output(["git", "status", "--short", "--untracked-files=no"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "toolchain": {
            "python": sys.version.split()[0],
            "cupy": modules["cupy"].__version__,
            "numba": modules["numba"].__version__,
            "numpy": modules["numpy"].__version__,
        },
        "target_hot_total_sec": float(args.target_hot_total_sec),
        "warmup": int(args.warmup),
        "max_repeat": int(args.max_repeat),
        "calibration_repeat": int(args.calibration_repeat),
        "calibration_safety_factor": float(args.calibration_safety_factor),
        "block_size": int(args.block_size),
        "grouped_suite": grouped,
        "compact_mask_suite": compact,
        "summary": {
            "all_match_cpu_oracle": bool(grouped["all_match_cpu_oracle"] and compact["all_match_cpu_oracle"]),
            "all_partner_contract_totals_meet_one_second_floor": not subsecond,
            "subsecond_hot_total_rows": subsecond,
            "numba_speedup_vs_cupy": {
                "grouped_suite_hot_total": grouped["numba_speedup_vs_cupy_suite_hot_total"],
                "compact_mask_hot_total": compact["numba_speedup_vs_cupy_hot_total"],
            },
            "cupy_speedup_vs_numba": {
                "grouped_suite_hot_total": grouped["cupy_speedup_vs_numba_suite_hot_total"],
                "compact_mask_hot_total": compact["cupy_speedup_vs_numba_hot_total"],
            },
            "interpretation_boundary": (
                "Large-scale same-contract partner continuation timings only. These rows do not "
                "claim whole-app speedup, RT-core speedup, release readiness, or universal partner superiority."
            ),
        },
        "claim_boundary": _claim_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal4266 large-scale CuPy vs Numba partner comparison.")
    parser.add_argument("--grouped-rows", type=int, default=4_000_000)
    parser.add_argument("--groups", type=int, default=4096)
    parser.add_argument("--compact-rows", type=int, default=8_000_000)
    parser.add_argument("--target-hot-total-sec", type=float, default=1.25)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--calibration-repeat", type=int, default=10)
    parser.add_argument("--calibration-safety-factor", type=float, default=1.15)
    parser.add_argument("--max-repeat", type=int, default=5000)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if args.grouped_rows <= 0 or args.compact_rows <= 0 or args.groups <= 0:
        raise ValueError("row counts and groups must be positive")
    payload = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal4266] wrote {args.output}", flush=True)
    if not args.dry_run:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
