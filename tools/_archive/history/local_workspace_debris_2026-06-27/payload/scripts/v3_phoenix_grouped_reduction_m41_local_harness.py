#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402


SCHEMA = "rtdl.phoenix_v3.grouped_reduction_m41.local_harness.v1"
ALLCLOSE_ATOL = 1e-6
ALLCLOSE_RTOL = 1e-9
STATUS_DRY_RUN_NOT_RELEASE = "grouped_reduction_m41_harness_ready_not_pod_run"
STATUS_RUN_COMPLETE_NOT_RELEASE = "grouped_reduction_m41_local_run_complete_not_release"
STATUS_RUN_FAILED_NOT_RELEASE = "grouped_reduction_m41_local_run_failed_not_release"
SERIOUS_ROW_FLOOR = 262_144
CPU_CONTROL = "cpu_numpy_same_contract_grouped_vector_sum_control"
LEGACY = "legacy_numba_one_shot_grouped_vector_sum"
RUNNER = "productized_prepared_execution_runner"
ALL_VARIANTS = (CPU_CONTROL, LEGACY, RUNNER)
DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_m41_local_harness_20260623"
)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = run_packet(args)
    for variant, row in payload["variants"].items():
        (args.output_dir / f"{variant}.json").write_text(
            json.dumps(_json_ready(row), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (args.output_dir / "summary.json").write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(_readme(payload), encoding="utf-8")
    print(json.dumps(_json_ready(payload["summary"]), indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phoenix V3 M41 grouped-reduction local harness. It prepares the "
            "second-family Step-2 review packet and does not authorize POD, "
            "release, all-app, or public speedup claims."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--variant", choices=("all", *ALL_VARIANTS), default="all")
    parser.add_argument("--row-count", type=int, default=SERIOUS_ROW_FLOOR)
    parser.add_argument("--group-count", type=int, default=1024)
    parser.add_argument("--partner", choices=("numba", "cupy"), default="numba")
    parser.add_argument("--seed", type=int, default=20260623)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument("--trust-row-offsets", action="store_true")
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    validate_args(args)
    selected = ALL_VARIANTS if args.variant == "all" else (str(args.variant),)
    if bool(args.dry_run):
        variants = {variant: dry_run_variant_payload(args, variant=variant) for variant in selected}
        return build_payload(args=args, data_set=data_set_metadata(args, generated=False), variant_payloads=variants, run_errors={}, selected_variants=selected)

    rows = make_grouped_vector_rows(
        row_count=int(args.row_count),
        group_count=int(args.group_count),
        seed=int(args.seed),
    )
    data_set = data_set_metadata(args, generated=True, fingerprint=rows["fingerprint"])
    variant_payloads: dict[str, dict[str, Any]] = {}
    run_errors: dict[str, str] = {}
    for variant in selected:
        try:
            if variant == CPU_CONTROL:
                row = run_cpu_control(args, rows)
            elif variant == LEGACY:
                row = run_legacy_one_shot(args, rows)
            elif variant == RUNNER:
                row = run_productized_runner(args, rows)
            else:  # pragma: no cover - argparse prevents this.
                raise ValueError(f"unsupported variant: {variant}")
            variant_payloads[variant] = row
        except Exception as exc:  # pragma: no cover - environment dependent.
            run_errors[variant] = repr(exc)
    return build_payload(args=args, data_set=data_set, variant_payloads=variant_payloads, run_errors=run_errors, selected_variants=selected)


def validate_args(args: argparse.Namespace) -> None:
    if int(args.row_count) < SERIOUS_ROW_FLOOR and not bool(args.allow_non_serious_local_smoke):
        raise SystemExit(
            "row-count is below the M41 serious floor; pass "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )
    if int(args.group_count) <= 0:
        raise SystemExit("group-count must be positive")
    if int(args.group_count) > int(args.row_count):
        raise SystemExit("group-count must not exceed row-count")
    if int(args.repeat) < 5:
        raise SystemExit("repeat must be >= 5 for reviewed focused evidence")
    if int(args.warmup) < 0:
        raise SystemExit("warmup must be non-negative")


def dry_run_variant_payload(args: argparse.Namespace, *, variant: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "variant": variant,
        "status": "dry_run",
        "command": build_command(args, variant=variant),
        "row_count": int(args.row_count),
        "group_count": int(args.group_count),
        "partner": str(args.partner),
        "same_generated_grouped_rows_enforced": True,
        "same_rows_per_process": True,
        "generic_grouped_reduction_contract": True,
        "app_specific_route_logic_allowed": False,
        "vector_sum_signature": None,
        "hot_query_median_sec": None,
        "inclusive_wall_sec": None,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_pod_spend_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "focused_pod_spend_conditions": (
            "external review must accept a serious-scale free local CUDA run "
            "at row_count >= 262144, failed_check_count == 0, "
            "step2_local_runner_contract_candidate == true, and no CPU-hot "
            "inversion blocker before a separate paid-POD request"
        ),
        "true_zero_copy_claim_authorized": False,
        "v4_work_authorized": False,
        "embedding_work_authorized": False,
        "c_abi_work_authorized": False,
    }


def build_command(args: argparse.Namespace, *, variant: str) -> list[str]:
    command = [
        sys.executable,
        "scripts/v3_phoenix_grouped_reduction_m41_local_harness.py",
        "--variant",
        variant,
        "--row-count",
        str(int(args.row_count)),
        "--group-count",
        str(int(args.group_count)),
        "--partner",
        str(args.partner),
        "--seed",
        str(int(args.seed)),
        "--warmup",
        str(int(args.warmup)),
        "--repeat",
        str(int(args.repeat)),
        "--output-dir",
        str(args.output_dir),
    ]
    if bool(getattr(args, "trust_row_offsets", False)):
        command.append("--trust-row-offsets")
    return command


def make_grouped_vector_rows(*, row_count: int, group_count: int, seed: int) -> dict[str, Any]:
    import numpy as np

    counts = np.full((group_count,), row_count // group_count, dtype=np.int64)
    counts[: row_count % group_count] += 1
    row_offsets = np.empty((group_count + 1,), dtype=np.int64)
    row_offsets[0] = 0
    np.cumsum(counts, out=row_offsets[1:])
    group_ids = np.repeat(np.arange(group_count, dtype=np.int64), counts)
    rng = np.random.default_rng(int(seed))
    values_x = rng.normal(loc=0.0, scale=1.0, size=row_count).astype(np.float64)
    values_y = rng.normal(loc=0.0, scale=1.0, size=row_count).astype(np.float64)
    fingerprint = hashlib.sha256()
    for array in (group_ids, row_offsets, values_x, values_y):
        fingerprint.update(array.tobytes())
    return {
        "group_ids": group_ids,
        "row_offsets": row_offsets,
        "values_x": values_x,
        "values_y": values_y,
        "fingerprint": {
            "kind": "presegmented_grouped_vector_rows_2d",
            "sha256": fingerprint.hexdigest(),
            "row_count": int(row_count),
            "group_count": int(group_count),
            "seed": int(seed),
        },
    }


def run_cpu_control(args: argparse.Namespace, rows: dict[str, Any]) -> dict[str, Any]:
    measured: list[float] = []
    started = time.perf_counter()
    output = None
    for iteration in range(int(args.warmup) + int(args.repeat)):
        run_start = time.perf_counter()
        output = numpy_grouped_vector_sum(rows)
        elapsed = time.perf_counter() - run_start
        if iteration >= int(args.warmup):
            measured.append(elapsed)
    wall = time.perf_counter() - started
    assert output is not None
    return variant_payload(
        args,
        variant=CPU_CONTROL,
        status="ok",
        hot_query_median_sec=statistics.median(measured),
        inclusive_wall_sec=wall,
        vector_sum_signature=vector_sum_signature(output),
        timing_breakdown_sec={
            "numpy_presegmented_reduce_sec": statistics.median(measured),
        },
        extra_metadata={
            "expected_route": "CPU NumPy same-contract grouped vector-sum control",
            "productized_execution_path": None,
        },
    )


def run_legacy_one_shot(args: argparse.Namespace, rows: dict[str, Any]) -> dict[str, Any]:
    columns = partner_columns(rows, str(args.partner))
    measured: list[float] = []
    started = time.perf_counter()
    output = None
    for iteration in range(int(args.warmup) + int(args.repeat)):
        run_start = time.perf_counter()
        output = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=int(args.group_count),
            partner=str(args.partner),
            validate_row_offsets=not bool(args.trust_row_offsets),
            return_metadata=True,
        )
        sync_partner(str(args.partner))
        elapsed = time.perf_counter() - run_start
        if iteration >= int(args.warmup):
            measured.append(elapsed)
    wall = time.perf_counter() - started
    assert output is not None
    return variant_payload(
        args,
        variant=LEGACY,
        status="ok",
        hot_query_median_sec=statistics.median(measured),
        inclusive_wall_sec=wall,
        vector_sum_signature=vector_sum_signature(output["columns"]),
        timing_breakdown_sec={
            "legacy_one_shot_grouped_vector_sum_sec": statistics.median(measured),
        },
        extra_metadata={
            "expected_route": f"legacy one-shot grouped_vector_sum_2d_partner_columns/{args.partner}",
            "adapter": output["metadata"].get("adapter"),
            "partner": output["metadata"].get("partner"),
            "row_count": output["metadata"].get("row_count"),
            "group_count": output["metadata"].get("group_count"),
        },
    )


def run_productized_runner(args: argparse.Namespace, rows: dict[str, Any]) -> dict[str, Any]:
    columns = partner_columns(rows, str(args.partner))
    cache = rt.ExplicitPreparedSessionCache(max_entries=1)

    def prepare_session() -> Any:
        return rt.prepare_grouped_vector_sum_2d_partner_columns_session(
            columns,
            group_count=int(args.group_count),
            partner=str(args.partner),
            validate_row_offsets=not bool(args.trust_row_offsets),
        )

    started = time.perf_counter()
    result = rt.run_grouped_vector_sum_2d_prepared_session(
        vector_columns_fingerprint=rows["fingerprint"],
        row_offsets_fingerprint={
            "kind": "row_offsets",
            "sha256": hashlib.sha256(rows["row_offsets"].tobytes()).hexdigest(),
            "group_count": int(args.group_count),
        },
        row_count=int(args.row_count),
        group_count=int(args.group_count),
        partner=str(args.partner),
        cache=cache,
        prepare_session=prepare_session,
        device="cuda",
        warmup_count=int(args.warmup),
        measured_repeat_count=int(args.repeat),
    )
    sync_partner(str(args.partner))
    wall = time.perf_counter() - started
    metadata = result.to_metadata()
    runner_hot_sec = float(metadata.get("measured_median_sec", math.nan))
    return variant_payload(
        args,
        variant=RUNNER,
        status="ok",
        hot_query_median_sec=runner_hot_sec,
        inclusive_wall_sec=wall,
        vector_sum_signature=vector_sum_signature(result.output["columns"]),
        timing_breakdown_sec={
            "prepare_sec": float(metadata.get("outer_prepare_sec", 0.0)),
            "cache_load_sec": float(metadata.get("outer_cache_load_sec", 0.0)),
            "warmup_sec": _prepared_report_phase_seconds(metadata, "warmup"),
            "prepared_runner_executor_sec": runner_hot_sec,
            "measured_total_sec": float(metadata.get("measured_total_sec", 0.0)),
            "validation_sec": _prepared_report_phase_seconds(metadata, "validation"),
        },
        extra_metadata={
            "expected_route": f"productized run_grouped_vector_sum_2d_prepared_session/{args.partner}",
            "adapter_contract_verification": {
                "adapter_row_count": metadata.get("adapter_row_count"),
                "adapter_group_count": metadata.get("adapter_group_count"),
                "adapter_counts_present": bool(metadata.get("adapter_counts_present")),
                "output_counts_match_requested": bool(metadata.get("output_counts_match_requested")),
            },
            "prepared_execution_session_runner_metadata": metadata,
        },
        runner_metadata=metadata,
    )


def numpy_grouped_vector_sum(rows: dict[str, Any]) -> dict[str, Any]:
    import numpy as np

    offsets = rows["row_offsets"]
    sum_x = np.add.reduceat(rows["values_x"], offsets[:-1])
    sum_y = np.add.reduceat(rows["values_y"], offsets[:-1])
    return {
        "group_ids": np.arange(len(offsets) - 1, dtype=np.int64),
        "sum_x": sum_x,
        "sum_y": sum_y,
    }


def numba_columns(rows: dict[str, Any]) -> dict[str, Any]:
    from numba import cuda

    return {
        "group_ids": cuda.to_device(rows["group_ids"]),
        "row_offsets": cuda.to_device(rows["row_offsets"]),
        "values_x": cuda.to_device(rows["values_x"]),
        "values_y": cuda.to_device(rows["values_y"]),
    }


def cupy_columns(rows: dict[str, Any]) -> dict[str, Any]:
    import cupy

    return {
        "group_ids": cupy.asarray(rows["group_ids"]),
        "row_offsets": cupy.asarray(rows["row_offsets"]),
        "values_x": cupy.asarray(rows["values_x"]),
        "values_y": cupy.asarray(rows["values_y"]),
    }


def partner_columns(rows: dict[str, Any], partner: str) -> dict[str, Any]:
    if partner == "cupy":
        return cupy_columns(rows)
    return numba_columns(rows)


def sync_partner(partner: str) -> None:
    if partner == "cupy":
        import cupy

        cupy.cuda.Stream.null.synchronize()
        return
    from numba import cuda

    cuda.synchronize()


def variant_payload(
    args: argparse.Namespace,
    *,
    variant: str,
    status: str,
    hot_query_median_sec: float,
    inclusive_wall_sec: float,
    vector_sum_signature: dict[str, Any],
    timing_breakdown_sec: dict[str, float],
    extra_metadata: dict[str, Any],
    runner_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema": SCHEMA,
        "variant": variant,
        "status": status,
        "row_count": int(args.row_count),
        "group_count": int(args.group_count),
        "seed": int(args.seed),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "hot_query_median_sec": float(hot_query_median_sec),
        "inclusive_wall_sec": float(inclusive_wall_sec),
        "vector_sum_signature": vector_sum_signature,
        "timing_breakdown_sec": timing_breakdown_sec,
        "extra_metadata": extra_metadata,
        "same_generated_grouped_rows_enforced": True,
        "same_rows_per_process": True,
        "generic_grouped_reduction_contract": True,
        "app_specific_route_logic_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_pod_spend_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "focused_pod_spend_conditions": (
            "external review must accept a serious-scale free local CUDA run "
            "at row_count >= 262144, failed_check_count == 0, "
            "step2_local_runner_contract_candidate == true, and no CPU-hot "
            "inversion blocker before a separate paid-POD request"
        ),
        "true_zero_copy_claim_authorized": False,
        "v4_work_authorized": False,
        "embedding_work_authorized": False,
        "c_abi_work_authorized": False,
    }
    if runner_metadata is not None:
        payload.update(
            {
                "runtime_executed": bool(runner_metadata.get("runtime_executed")),
                "runtime_trunk_executes_end_to_end": bool(
                    runner_metadata.get("runtime_trunk_executes_end_to_end")
                ),
                "productized_execution_path": runner_metadata.get("productized_execution_path"),
                "primitive_family": runner_metadata.get("primitive_family"),
                "continuation_contract": runner_metadata.get("continuation_contract"),
                "internal_device_residency_between_rtdl_phases": bool(
                    runner_metadata.get("internal_device_residency_between_rtdl_phases")
                ),
                "hot_path_host_materialization": bool(
                    runner_metadata.get("hot_path_host_materialization")
                ),
                "output_counts_match_requested": bool(
                    runner_metadata.get("output_counts_match_requested")
                ),
                "adapter_row_count": runner_metadata.get("adapter_row_count"),
                "adapter_group_count": runner_metadata.get("adapter_group_count"),
                "adapter_counts_present": bool(runner_metadata.get("adapter_counts_present")),
                "output_columns_reused": bool(runner_metadata.get("output_columns_reused")),
            }
        )
    return payload


def vector_sum_signature(output: dict[str, Any]) -> dict[str, Any]:
    import numpy as np

    sum_x = _to_numpy(output["sum_x"]).astype(np.float64, copy=False)
    sum_y = _to_numpy(output["sum_y"]).astype(np.float64, copy=False)
    rounded = np.round(np.column_stack([sum_x, sum_y]), 9)
    return {
        "group_count": int(len(sum_x)),
        "sum_x_total": float(sum_x.sum()),
        "sum_y_total": float(sum_y.sum()),
        "sum_x_values": [float(item) for item in sum_x.tolist()],
        "sum_y_values": [float(item) for item in sum_y.tolist()],
        "rounded_sha256": hashlib.sha256(rounded.tobytes()).hexdigest(),
    }


def _to_numpy(values: Any):
    import numpy as np

    if hasattr(values, "copy_to_host"):
        return values.copy_to_host()
    if hasattr(values, "detach"):
        return values.detach().cpu().numpy()
    module_name = type(values).__module__.split(".", 1)[0]
    if module_name == "cupy":
        import cupy

        return cupy.asnumpy(values)
    return np.asarray(values)


def _prepared_report_phase_seconds(metadata: dict[str, Any], phase_name: str) -> float:
    report = metadata.get("prepared_execution_report", {})
    phases = report.get("phases", ()) if isinstance(report, dict) else ()
    for phase in phases:
        if isinstance(phase, dict) and phase.get("phase") == phase_name:
            return float(phase.get("seconds", 0.0))
    return 0.0


def build_payload(
    *,
    args: argparse.Namespace,
    data_set: dict[str, Any],
    variant_payloads: dict[str, dict[str, Any]],
    run_errors: dict[str, str],
    selected_variants: Iterable[str],
) -> dict[str, Any]:
    selected = tuple(selected_variants)
    comparisons = comparison_payload(variant_payloads)
    failed_checks = failure_checks(
        variant_payloads,
        comparisons,
        run_errors,
        selected_variants=selected,
        dry_run=bool(args.dry_run),
    )
    status = payload_status(args=args, failed_checks=failed_checks)
    summary = {
        "schema": SCHEMA,
        "status": status,
        "dry_run": bool(args.dry_run),
        "selected_variants": selected,
        "variant_count": len(variant_payloads),
        "failed_check_count": len(failed_checks),
        "same_generated_grouped_rows_enforced": bool(args.variant == "all"),
        "same_rows_per_process": True,
        "generic_grouped_reduction_contract": True,
        "m41_second_family_selected": "grouped_vector_sum_2d",
        "m41_step2_local_work_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_pod_spend_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "focused_pod_spend_conditions": (
            "external review must accept a serious-scale free local CUDA run "
            "at row_count >= 262144, failed_check_count == 0, "
            "step2_local_runner_contract_candidate == true, and no CPU-hot "
            "inversion blocker before a separate paid-POD request"
        ),
        "true_zero_copy_claim_authorized": False,
        "v4_work_authorized": False,
        "embedding_work_authorized": False,
        "c_abi_work_authorized": False,
        "comparisons": comparisons,
    }
    return {
        "schema": SCHEMA,
        "tool": "v3_phoenix_grouped_reduction_m41_local_harness",
        "status": status,
        "date": "2026-06-23",
        "args": {
            "variant": str(args.variant),
            "row_count": int(args.row_count),
            "group_count": int(args.group_count),
            "partner": str(args.partner),
            "trust_row_offsets": bool(getattr(args, "trust_row_offsets", False)),
            "seed": int(args.seed),
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "dry_run": bool(args.dry_run),
        },
        "data_set": data_set,
        "variants": variant_payloads,
        "run_errors": run_errors,
        "comparisons": comparisons,
        "failed_checks": failed_checks,
        "summary": summary,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "focused_pod_spend_authorized_now": False,
            "focused_pod_spend_conditions": (
                "external review must accept a serious-scale free local CUDA run "
                "at row_count >= 262144, failed_check_count == 0, "
                "step2_local_runner_contract_candidate == true, and no CPU-hot "
                "inversion blocker before a separate paid-POD request"
            ),
            "all_app_pod_spend_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_work_authorized": False,
            "embedding_work_authorized": False,
            "c_abi_work_authorized": False,
        },
        "goal_level_decision_audit": {
            "decision": "select grouped vector-sum/reduction as the M41 second-family Step-2 local harness target",
            "was_i_foolish": "No.",
            "foolish_actions": (
                "It would be foolish to spend another POD run or claim V3 release "
                "before proving the second family locally and getting external review."
            ),
            "other_path": (
                "Jump to RayJoin or RTNN route tuning. That risks re-entering app-shaped work "
                "instead of proving reusable continuation-runner discipline."
            ),
            "different_path_now": (
                "Use grouped reduction because it is a different primitive family from "
                "component union and already has a generic M36 core node awaiting focused harness evidence."
            ),
        },
    }


def payload_status(*, args: argparse.Namespace, failed_checks: list[str]) -> str:
    if bool(args.dry_run):
        return STATUS_DRY_RUN_NOT_RELEASE
    if failed_checks:
        return STATUS_RUN_FAILED_NOT_RELEASE
    return STATUS_RUN_COMPLETE_NOT_RELEASE


def comparison_payload(variant_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if {CPU_CONTROL, LEGACY, RUNNER} - set(variant_payloads):
        if any(row.get("status") == "dry_run" for row in variant_payloads.values()):
            return {"status": "dry_run_no_performance_interpretation"}
        return {"status": "missing_variants_no_performance_interpretation"}
    if any(variant_payloads[item].get("status") == "dry_run" for item in ALL_VARIANTS):
        return {"status": "dry_run_no_performance_interpretation"}
    cpu = variant_payloads[CPU_CONTROL]
    legacy = variant_payloads[LEGACY]
    runner = variant_payloads[RUNNER]
    strict_hash_match = (
        cpu.get("vector_sum_signature")
        == legacy.get("vector_sum_signature")
        == runner.get("vector_sum_signature")
        and cpu.get("vector_sum_signature") is not None
    )
    signatures_allclose = _signatures_allclose(
        cpu.get("vector_sum_signature"),
        legacy.get("vector_sum_signature"),
        runner.get("vector_sum_signature"),
    )
    runner_vs_legacy_hot = _safe_div(
        legacy.get("hot_query_median_sec"),
        runner.get("hot_query_median_sec"),
    )
    runner_vs_legacy_wall = _safe_div(
        legacy.get("inclusive_wall_sec"),
        runner.get("inclusive_wall_sec"),
    )
    runner_vs_cpu_hot = _safe_div(
        cpu.get("hot_query_median_sec"),
        runner.get("hot_query_median_sec"),
    )
    return {
        "status": "computed",
        "all_variant_vector_sum_signatures_match": signatures_allclose,
        "all_variant_vector_sum_signatures_hash_match": strict_hash_match,
        "all_variant_vector_sum_signatures_allclose": signatures_allclose,
        "vector_sum_allclose_tolerance": {
            "atol": ALLCLOSE_ATOL,
            "rtol": ALLCLOSE_RTOL,
            "rationale": (
                "grouped vector sums are double-precision reductions; strict "
                "hash equality is diagnostic, while allclose tolerates valid "
                "floating-point accumulation-order differences across CPU and CUDA paths"
            ),
        },
        "runner_vs_legacy_hot_speedup": runner_vs_legacy_hot,
        "runner_vs_legacy_wall_speedup": runner_vs_legacy_wall,
        "runner_vs_cpu_hot_speedup": runner_vs_cpu_hot,
        "step2_local_runner_contract_candidate": bool(
            signatures_allclose
            and runner.get("runtime_trunk_executes_end_to_end")
            and runner.get("internal_device_residency_between_rtdl_phases")
            and not runner.get("hot_path_host_materialization")
            and runner.get("output_counts_match_requested")
            and runner.get("output_columns_reused")
        ),
        "material_performance_claim_authorized": False,
    }


def failure_checks(
    variant_payloads: dict[str, dict[str, Any]],
    comparisons: dict[str, Any],
    run_errors: dict[str, str],
    *,
    selected_variants: Iterable[str],
    dry_run: bool,
) -> list[str]:
    failed: list[str] = []
    if run_errors:
        failed.append("variant_run_errors_present")
    missing = set(selected_variants) - set(variant_payloads)
    if missing:
        failed.append("missing_variants:" + ",".join(sorted(missing)))
    if dry_run:
        return failed
    for variant in selected_variants:
        row = variant_payloads.get(variant, {})
        if row.get("status") != "ok":
            failed.append(f"{variant}_status_not_ok")
        if not bool(row.get("generic_grouped_reduction_contract")):
            failed.append(f"{variant}_generic_grouped_reduction_contract_missing")
        if row.get("vector_sum_signature") is None:
            failed.append(f"{variant}_vector_sum_signature_missing")
        if bool(row.get("app_specific_route_logic_allowed")):
            failed.append(f"{variant}_app_specific_route_logic_allowed")
    if set(selected_variants) == set(ALL_VARIANTS):
        if not bool(comparisons.get("all_variant_vector_sum_signatures_allclose")):
            failed.append("vector_sum_signatures_not_allclose")
        runner = variant_payloads.get(RUNNER, {})
        if not bool(runner.get("runtime_trunk_executes_end_to_end")):
            failed.append("runner_runtime_trunk_not_end_to_end")
        if not bool(runner.get("internal_device_residency_between_rtdl_phases")):
            failed.append("runner_internal_device_residency_missing")
        if bool(runner.get("hot_path_host_materialization")):
            failed.append("runner_hot_path_host_materialization")
        if not bool(runner.get("output_counts_match_requested")):
            failed.append("runner_output_counts_do_not_match")
        if not bool(runner.get("adapter_counts_present")):
            failed.append("runner_adapter_counts_missing")
        if not bool(runner.get("output_columns_reused")):
            failed.append("runner_output_columns_not_reused")
    return failed


def data_set_metadata(
    args: argparse.Namespace,
    *,
    generated: bool,
    fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "row_count": int(args.row_count),
        "group_count": int(args.group_count),
            "partner": str(args.partner),
            "trust_row_offsets": bool(getattr(args, "trust_row_offsets", False)),
            "seed": int(args.seed),
        "generated_once_in_process": bool(generated),
        "same_generated_grouped_rows_required": True,
        "fingerprint": fingerprint,
    }


def _safe_div(numerator: Any, denominator: Any) -> float | None:
    try:
        numerator_value = float(numerator)
        denominator_value = float(denominator)
        if not math.isfinite(numerator_value) or not math.isfinite(denominator_value):
            return None
        if denominator_value <= 0.0:
            return None
        return numerator_value / denominator_value
    except (TypeError, ValueError):
        return None


def _signatures_allclose(*signatures: Any, atol: float = ALLCLOSE_ATOL, rtol: float = ALLCLOSE_RTOL) -> bool:
    try:
        import numpy as np

        if any(not isinstance(signature, dict) for signature in signatures):
            return False
        first = signatures[0]
        first_x = np.asarray(first["sum_x_values"], dtype=np.float64)
        first_y = np.asarray(first["sum_y_values"], dtype=np.float64)
        for signature in signatures[1:]:
            if int(signature.get("group_count", -1)) != int(first.get("group_count", -2)):
                return False
            other_x = np.asarray(signature["sum_x_values"], dtype=np.float64)
            other_y = np.asarray(signature["sum_y_values"], dtype=np.float64)
            if not np.allclose(first_x, other_x, atol=atol, rtol=rtol):
                return False
            if not np.allclose(first_y, other_y, atol=atol, rtol=rtol):
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    try:
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
    except Exception:
        pass
    return value


def _readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    comparisons = payload["comparisons"]
    return "\n".join(
        [
            "# Phoenix V3 M41 Grouped-Reduction Local Harness",
            "",
            f"Status: `{summary['status']}`",
            "",
            "This is local Step-2 harness evidence only. It does not authorize release, all-app POD, public speedup wording, V4, embedding, C ABI, or true-zero-copy claims.",
            "",
            "## Summary",
            "",
            f"- row_count: `{payload['args']['row_count']}`",
            f"- group_count: `{payload['args']['group_count']}`",
            f"- failed_check_count: `{summary['failed_check_count']}`",
            f"- comparisons: `{json.dumps(_json_ready(comparisons), sort_keys=True)}`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
