from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


DEFAULT_PARTNERS = ("cupy", "numba")
EXPECTED_EXECUTION_PATH = "generic_grouped_vector_sum_typed_stream_partner_columns"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M32 Barnes-Hut grouped-vector partner-dual evidence."
    )
    parser.add_argument("--group-count", type=int, default=262_144)
    parser.add_argument("--rows-per-group", type=int, default=8)
    parser.add_argument("--partners", default="cupy,numba")
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=80)
    parser.add_argument("--validate-row-offsets", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4429_v3_0_m32_barnes_hut_grouped_vector_partner_dual.json"),
    )
    args = parser.parse_args()

    _validate_args(args)
    partners = tuple(item.strip().lower() for item in args.partners.split(",") if item.strip())
    unsupported = sorted(set(partners) - set(DEFAULT_PARTNERS))
    if unsupported:
        raise ValueError(f"unsupported partner(s): {', '.join(unsupported)}")

    planned_rows = tuple(
        {
            "partner": partner,
            "group_count": int(args.group_count),
            "rows_per_group": int(args.rows_per_group),
            "row_count": int(args.group_count) * int(args.rows_per_group),
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "presegmented_offsets": True,
            "validate_row_offsets": bool(args.validate_row_offsets),
            "caller_supplied_partner_columns": True,
        }
        for partner in partners
    )

    if args.dry_run:
        payload = _base_payload(args=args, partners=partners)
        payload.update(
            {
                "status": "dry_run",
                "planned_rows": planned_rows,
                "descriptor_policy": _descriptor_policy_snapshot(partners),
                "rows": (),
                "comparison": {
                    "all_output_signatures_match_reference": None,
                    "all_outputs_match_reference_with_tolerance": None,
                    "all_front_doors_report_no_hidden_host_rows": None,
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": payload["status"], "planned_rows": planned_rows}, indent=2))
        return 0

    host_workload = _build_host_workload(
        group_count=int(args.group_count),
        rows_per_group=int(args.rows_per_group),
    )
    reference = _reference_sums(host_workload)
    rows = []
    for partner in partners:
        rows.append(
            _run_partner(
                partner=partner,
                host_workload=host_workload,
                reference=reference,
                warmup=int(args.warmup),
                repeat=int(args.repeat),
                validate_row_offsets=bool(args.validate_row_offsets),
            )
        )

    comparison = _compare_rows(rows)
    payload = _base_payload(args=args, partners=partners)
    payload.update(
        {
            "status": "ok",
            "planned_rows": planned_rows,
            "descriptor_policy": _descriptor_policy_snapshot(partners),
            "rows": tuple(rows),
            "comparison": comparison,
        }
    )
    if not comparison["all_outputs_match_reference_with_tolerance"]:
        raise RuntimeError("M32 Barnes-Hut grouped-vector partner-dual evidence found output mismatch")
    if not comparison["all_front_doors_report_no_hidden_host_rows"]:
        raise RuntimeError("M32 Barnes-Hut grouped-vector partner-dual evidence found hidden host materialization")
    _write_payload(payload, args.output)
    print(json.dumps({"status": payload["status"], "comparison": comparison, "rows": rows}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.group_count <= 0:
        raise ValueError("--group-count must be positive")
    if args.rows_per_group <= 0:
        raise ValueError("--rows-per-group must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")


def _base_payload(*, args: argparse.Namespace, partners: tuple[str, ...]) -> dict[str, object]:
    return {
        "version": "rtdl.v3_0.barnes_hut_grouped_vector_partner_dual.m32",
        "goal": "Goal4429 V3.0 M32 Barnes-Hut grouped-vector partner-dual refresh",
        "parameters": {
            "group_count": int(args.group_count),
            "rows_per_group": int(args.rows_per_group),
            "row_count": int(args.group_count) * int(args.rows_per_group),
            "partners": partners,
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "validate_row_offsets": bool(args.validate_row_offsets),
            "presegmented_offsets": True,
        },
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "benchmark_app": "barnes_hut",
            "bridge_debt_target": "grouped_vector_sum_partner_continuation_front_door",
            "primitive_first_contract": True,
            "partner_continuation_required": True,
            "best_partner_plus_numba_reference_required": True,
            "caller_supplied_partner_columns_no_hidden_host_rows": True,
            "native_rt_traversal_executed": False,
            "rt_core_speedup_claim_authorized": False,
            "embree_comparison_claim_authorized": False,
            "full_rt_barneshut_paper_reproduction": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
        },
    }


def _build_host_workload(*, group_count: int, rows_per_group: int) -> dict[str, Any]:
    import numpy as np

    row_count = group_count * rows_per_group
    group_ids = np.repeat(np.arange(group_count, dtype=np.int64), rows_per_group)
    row_offsets = np.arange(0, row_count + 1, rows_per_group, dtype=np.int64)
    row_index = np.arange(row_count, dtype=np.float64)
    group_index = np.repeat(np.arange(group_count, dtype=np.float64), rows_per_group)
    lane_index = row_index - group_index * float(rows_per_group)
    values_x = ((group_index % 97.0) - 48.0) * 0.125 + (lane_index + 1.0) * 0.001
    values_y = ((group_index % 89.0) - 44.0) * -0.0625 + (lane_index + 1.0) * -0.002
    return {
        "group_ids": group_ids,
        "row_offsets": row_offsets,
        "values_x": values_x.astype(np.float64, copy=False),
        "values_y": values_y.astype(np.float64, copy=False),
        "group_count": int(group_count),
        "rows_per_group": int(rows_per_group),
        "row_count": int(row_count),
    }


def _reference_sums(host_workload: dict[str, Any]) -> dict[str, Any]:
    import numpy as np

    group_count = int(host_workload["group_count"])
    rows_per_group = int(host_workload["rows_per_group"])
    sum_x = np.asarray(host_workload["values_x"], dtype=np.float64).reshape(group_count, rows_per_group).sum(axis=1)
    sum_y = np.asarray(host_workload["values_y"], dtype=np.float64).reshape(group_count, rows_per_group).sum(axis=1)
    return {
        "sum_x": sum_x,
        "sum_y": sum_y,
        "signature": _signature(sum_x, sum_y),
        "checksum_x": float(sum_x.sum()),
        "checksum_y": float(sum_y.sum()),
    }


def _run_partner(
    *,
    partner: str,
    host_workload: dict[str, Any],
    reference: dict[str, Any],
    warmup: int,
    repeat: int,
    validate_row_offsets: bool,
) -> dict[str, object]:
    from examples.current.research_benchmarks.barnes_hut import (
        rtdl_barnes_hut_benchmark_app as barnes_hut,
    )

    setup_started = perf_counter()
    device_inputs = _to_partner_inputs(partner, host_workload)
    setup_sec = perf_counter() - setup_started
    _sync_partner(partner)

    warmup_durations = []
    timed_durations = []
    last_payload: dict[str, Any] | None = None
    for index in range(warmup + repeat):
        started = perf_counter()
        payload = barnes_hut.run_barnes_hut_grouped_vector_sum_typed_stream_preview(
            {
                **device_inputs,
                "group_count": int(host_workload["group_count"]),
                "stream_id": f"goal4429_m32_barnes_hut_{partner}_{index}",
            },
            partner=partner,
            validate_row_offsets=bool(validate_row_offsets),
        )
        _sync_partner(partner)
        elapsed = perf_counter() - started
        if index < warmup:
            warmup_durations.append(elapsed)
        else:
            timed_durations.append(elapsed)
            last_payload = payload
    if last_payload is None:
        raise RuntimeError("no measured payload was produced")

    sum_x = _to_numpy(last_payload["outputs"]["sum_x"])
    sum_y = _to_numpy(last_payload["outputs"]["sum_y"])
    signature = _signature(sum_x, sum_y)
    partner_metadata = dict(last_payload["partner_metadata"])
    continuation_plan = dict(last_payload["continuation_plan"])
    typed_stream = dict(last_payload["typed_stream"])
    return {
        "partner": partner,
        "status": last_payload["status"],
        "contract_version": last_payload["contract_version"],
        "execution_path": last_payload["execution_path"],
        "operation": last_payload["operation"],
        "source_materialization": last_payload["source_materialization"],
        "group_count": int(host_workload["group_count"]),
        "row_count": int(host_workload["row_count"]),
        "rows_per_group": int(host_workload["rows_per_group"]),
        "warmup": int(warmup),
        "repeat": int(repeat),
        "device_input_setup_sec": float(setup_sec),
        "warmup_total_sec": float(sum(warmup_durations)),
        "timed_total_sec": float(sum(timed_durations)),
        "timed_median_sec": float(statistics.median(timed_durations)),
        "timed_min_sec": float(min(timed_durations)),
        "timed_max_sec": float(max(timed_durations)),
        "timed_mean_sec": float(statistics.mean(timed_durations)),
        "output_signature": signature,
        "reference_signature": reference["signature"],
        "matches_reference_signature": signature == reference["signature"],
        "matches_reference_tolerance": (
            float(abs(sum_x - reference["sum_x"]).max()) <= 1.0e-9
            and float(abs(sum_y - reference["sum_y"]).max()) <= 1.0e-9
        ),
        "reference_tolerance_abs": 1.0e-9,
        "max_abs_diff_x": float(abs(sum_x - reference["sum_x"]).max()),
        "max_abs_diff_y": float(abs(sum_y - reference["sum_y"]).max()),
        "checksum_x": float(sum_x.sum()),
        "checksum_y": float(sum_y.sum()),
        "reference_checksum_x": float(reference["checksum_x"]),
        "reference_checksum_y": float(reference["checksum_y"]),
        "typed_stream_column_count": len(tuple(typed_stream["columns"])),
        "continuation_plan_partner": continuation_plan["user_selected_partner"],
        "partner_metadata_partner": partner_metadata["partner"],
        "partner_metadata_adapter": partner_metadata["adapter"],
        "partner_metadata_kernel": _kernel_name(partner_metadata),
        "partner_metadata_presegmented_offsets_used": _presegmented_used(partner_metadata),
        "partner_metadata_global_atomic_add_used": _global_atomic_add_used(partner_metadata),
        "partner_metadata_row_offset_validation_host_sync_used": partner_metadata.get(
            "v2_5_numba_row_offset_validation_host_sync_used"
        ),
        "front_door_reports_no_hidden_host_rows": (
            last_payload["source_materialization"] == "caller_supplied_partner_columns_no_hidden_host_rows"
        ),
        "claim_boundary": {
            "native_rt_traversal_executed": False,
            "rt_core_speedup_claim_authorized": False,
            "full_rt_barneshut_paper_reproduction": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def _to_partner_inputs(partner: str, host_workload: dict[str, Any]) -> dict[str, Any]:
    if partner == "cupy":
        import cupy

        return {
            "group_ids": cupy.asarray(host_workload["group_ids"], dtype=cupy.int64),
            "row_offsets": cupy.asarray(host_workload["row_offsets"], dtype=cupy.int64),
            "values_x": cupy.asarray(host_workload["values_x"], dtype=cupy.float64),
            "values_y": cupy.asarray(host_workload["values_y"], dtype=cupy.float64),
            "producer_primitive": "aggregate_frontier_weighted_vector_columns_2d",
        }
    if partner == "numba":
        try:
            import _numba_cuda_redirector  # noqa: F401
        except ImportError:
            pass
        from numba import cuda

        return {
            "group_ids": cuda.to_device(host_workload["group_ids"]),
            "row_offsets": cuda.to_device(host_workload["row_offsets"]),
            "values_x": cuda.to_device(host_workload["values_x"]),
            "values_y": cuda.to_device(host_workload["values_y"]),
            "producer_primitive": "aggregate_frontier_weighted_vector_columns_2d",
        }
    raise ValueError(f"unsupported partner: {partner}")


def _sync_partner(partner: str) -> None:
    if partner == "cupy":
        import cupy

        cupy.cuda.runtime.deviceSynchronize()
        return
    if partner == "numba":
        from numba import cuda

        cuda.synchronize()
        return
    raise ValueError(f"unsupported partner: {partner}")


def _to_numpy(value: Any):
    import numpy as np

    if hasattr(value, "copy_to_host"):
        return np.asarray(value.copy_to_host(), dtype=np.float64)
    if hasattr(value, "get"):
        return np.asarray(value.get(), dtype=np.float64)
    if hasattr(value, "detach"):
        return np.asarray(value.detach().cpu().numpy(), dtype=np.float64)
    return np.asarray(value, dtype=np.float64)


def _signature(sum_x: Any, sum_y: Any) -> str:
    import numpy as np

    digest = hashlib.sha256()
    digest.update(np.asarray(sum_x, dtype=np.float64).tobytes())
    digest.update(np.asarray(sum_y, dtype=np.float64).tobytes())
    return digest.hexdigest()


def _kernel_name(metadata: dict[str, Any]) -> str | None:
    return (
        metadata.get("v2_5_cupy_adapter_kernel")
        or metadata.get("v2_5_numba_adapter_kernel")
        or metadata.get("v2_5_triton_adapter_kernel")
    )


def _presegmented_used(metadata: dict[str, Any]) -> bool:
    return bool(
        metadata.get("v2_5_cupy_presegmented_offsets_used")
        or metadata.get("v2_5_numba_presegmented_offsets_used")
        or metadata.get("v2_5_triton_presegmented_offsets_used")
    )


def _global_atomic_add_used(metadata: dict[str, Any]) -> bool | None:
    value = (
        metadata.get("v2_5_cupy_global_atomic_add_used")
        if metadata.get("v2_5_cupy_global_atomic_add_used") is not None
        else metadata.get("v2_5_numba_global_atomic_add_used")
    )
    if value is None:
        value = metadata.get("v2_5_triton_global_atomic_add_used")
    return None if value is None else bool(value)


def _descriptor_policy_snapshot(partners: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    from examples.current.research_benchmarks.barnes_hut import (
        rtdl_barnes_hut_benchmark_app as barnes_hut,
    )

    rows = []
    for partner in partners:
        descriptor = barnes_hut.describe_barnes_hut_grouped_vector_sum_typed_stream(partner=partner)
        rows.append(
            {
                "partner": partner,
                "execution_path": descriptor["execution_path"],
                "operation": descriptor["operation"],
                "source_materialization": descriptor["source_materialization"],
                "supported_partners": tuple(descriptor["partner_policy"]["supported_partners"]),
                "numba_status": descriptor["partner_policy"]["numba_status"],
                "numba_reference_partner_supported": bool(
                    descriptor["partner_policy"]["numba_reference_partner_supported"]
                ),
                "rt_core_speedup_claim_authorized": bool(
                    descriptor["claim_boundary"]["rt_core_speedup_claim_authorized"]
                ),
            }
        )
    return tuple(rows)


def _compare_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_partner = {str(row["partner"]): row for row in rows}
    comparison: dict[str, object] = {
        "partners": tuple(sorted(by_partner)),
        "all_output_signatures_match_reference": all(
            bool(row["matches_reference_signature"]) for row in rows
        ),
        "all_outputs_match_reference_with_tolerance": all(
            bool(row["matches_reference_tolerance"]) for row in rows
        ),
        "all_front_doors_report_no_hidden_host_rows": all(
            bool(row["front_door_reports_no_hidden_host_rows"]) for row in rows
        ),
        "all_presegmented_offsets_used": all(
            bool(row["partner_metadata_presegmented_offsets_used"]) for row in rows
        ),
        "all_global_atomic_add_avoided": all(
            bool(row["partner_metadata_global_atomic_add_used"]) is False for row in rows
        ),
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if {"cupy", "numba"}.issubset(by_partner):
        cupy_median = float(by_partner["cupy"]["timed_median_sec"])
        numba_median = float(by_partner["numba"]["timed_median_sec"])
        comparison["numba_over_cupy_median"] = numba_median / cupy_median if cupy_median else None
        comparison["cupy_over_numba_median"] = cupy_median / numba_median if numba_median else None
        comparison["signatures_match_between_cupy_and_numba"] = (
            by_partner["cupy"]["output_signature"] == by_partner["numba"]["output_signature"]
        )
    return comparison


def _environment_snapshot() -> dict[str, object]:
    return {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "git_head": _git_head(),
    }


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _write_payload(payload: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
