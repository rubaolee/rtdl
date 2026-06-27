#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import statistics
import sys
import threading
import time
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.rt_dbscan import (  # noqa: E402
    rtdl_rt_dbscan_benchmark_app as rt_dbscan_app,
)
from scripts import v3_optix_hardware_gate  # noqa: E402


SCHEMA = "rtdl.phoenix_v3.component_union_m38_pod_ab.v1"
STATUS_DRY_RUN_NOT_RELEASE = "component_union_m39_harness_ready_not_pod_run"
STATUS_RUN_COMPLETE_NOT_RELEASE = "component_union_m39_focused_pod_run_complete_not_release"
STATUS_RUN_FAILED_NOT_RELEASE = "component_union_m39_focused_pod_run_failed_not_release"
STATUS_NOT_RELEASE = STATUS_DRY_RUN_NOT_RELEASE
DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_component_union_m39_focused_pod_ab_20260623"
)
SERIOUS_POINT_FLOOR = 262_144
EMBREE = "embree_same_contract_component_union_control"
LEGACY = "legacy_optix_grouped_stream_component_labels"
RUNNER = "productized_prepared_execution_runner"
ALL_VARIANTS = (EMBREE, LEGACY, RUNNER)
OUTPUT_CONTRACT = "generic_prepared_optix_numba_grouped_stream_component_labels_3d"


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
            "Phoenix V3 M39 focused component-union harness. It implements the "
            "M38 protocol locally; it does not authorize release or all-app POD."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--variant", choices=("all", *ALL_VARIANTS), default="all")
    parser.add_argument("--dataset", choices=("clustered3d", "road3d", "ngsim_dense", "tiny"), default="clustered3d")
    parser.add_argument("--point-count", type=int, default=SERIOUS_POINT_FLOOR)
    parser.add_argument("--radius", type=float, default=3.0)
    parser.add_argument("--min-neighbors", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260623)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--heartbeat-sec", type=float, default=30.0)
    parser.add_argument("--hard-cap-sec", type=float, default=7200.0)
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    validate_args(args)
    started = time.perf_counter()
    selected_variants = ALL_VARIANTS if args.variant == "all" else (str(args.variant),)
    environment = environment_payload(require_rt_hardware=bool(args.require_rt_hardware))
    if bool(args.require_rt_hardware) and environment["hardware_gate"].get("status") != "pass":
        return build_payload(
            args=args,
            environment=environment,
            point_set=point_set_metadata(args, fingerprint=None, generated=False),
            variant_payloads={},
            run_errors={
                "optix_hardware_gate": environment["hardware_gate"].get("fail_closed_reason")
                or "OptiX RT hardware gate failed"
            },
            selected_variants=selected_variants,
        )

    if bool(args.dry_run):
        variants = {
            variant: dry_run_variant_payload(args, variant=variant)
            for variant in selected_variants
        }
        return build_payload(
            args=args,
            environment=environment,
            point_set=point_set_metadata(args, fingerprint=None, generated=False),
            variant_payloads=variants,
            run_errors={},
            selected_variants=selected_variants,
        )

    with hard_cap_watchdog(args):
        points = rt_dbscan_app.make_rt_dbscan_points(
            str(args.dataset),
            point_count=int(args.point_count),
            seed=int(args.seed),
        )
        point_fingerprint = rt.make_prepared_input_fingerprint(tuple(points))
        point_set = point_set_metadata(args, fingerprint=point_fingerprint, generated=True)
        variant_payloads: dict[str, dict[str, Any]] = {}
        run_errors: dict[str, str] = {}
        for variant in selected_variants:
            ensure_hard_cap(started, args=args)
            try:
                print(
                    f"[phoenix-v3-component-union-m39] variant={variant} "
                    f"point_count={int(args.point_count)} repeat={int(args.repeat)}",
                    flush=True,
                )
                with heartbeat(variant, interval_sec=float(args.heartbeat_sec)):
                    row = run_variant(args, variant=variant, points=points, point_fingerprint=point_fingerprint)
                variant_payloads[variant] = row
                (args.output_dir / f"{variant}.json").write_text(
                    json.dumps(_json_ready(row), indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            except Exception as exc:  # pragma: no cover - hardware/environment dependent
                run_errors[variant] = repr(exc)
                (args.output_dir / f"{variant}.error.txt").write_text(
                    repr(exc) + "\n",
                    encoding="utf-8",
                )

    return build_payload(
        args=args,
        environment=environment,
        point_set=point_set,
        variant_payloads=variant_payloads,
        run_errors=run_errors,
        selected_variants=selected_variants,
    )


def validate_args(args: argparse.Namespace) -> None:
    if int(args.point_count) < SERIOUS_POINT_FLOOR and not bool(args.allow_non_serious_local_smoke):
        raise SystemExit(
            "point-count is below the M38 serious floor; pass "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )
    if float(args.radius) <= 0.0:
        raise SystemExit("radius must be positive")
    if int(args.min_neighbors) < 1:
        raise SystemExit("min-neighbors must be at least 1")
    if int(args.repeat) < 5:
        raise SystemExit("repeat must be >= 5 for the reviewed M38 focused protocol")
    if int(args.warmup) < 0:
        raise SystemExit("warmup must be non-negative")
    if float(args.hard_cap_sec) <= 0.0:
        raise SystemExit("hard-cap-sec must be positive")


def dry_run_variant_payload(args: argparse.Namespace, *, variant: str) -> dict[str, Any]:
    return {
        "variant": variant,
        "status": "dry_run",
        "command": build_command(args, variant=variant),
        "component_labels_contract": True,
        "component_label_outputs_present": None,
        "component_signature_substituted_for_labels": False,
        "canonical_component_signature": None,
        "hot_query_median_sec": None,
        "runner_inclusive_wall_median_sec": None,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "all_app_pod_spend_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "external_embedding_or_zero_copy_claim_authorized": False,
    }


def build_command(args: argparse.Namespace, *, variant: str) -> list[str]:
    command = [
        sys.executable,
        "scripts/v3_phoenix_component_union_m38_pod_ab.py",
        "--variant",
        variant,
        "--dataset",
        str(args.dataset),
        "--point-count",
        str(int(args.point_count)),
        "--radius",
        str(float(args.radius)),
        "--min-neighbors",
        str(int(args.min_neighbors)),
        "--seed",
        str(int(args.seed)),
        "--warmup",
        str(int(args.warmup)),
        "--repeat",
        str(int(args.repeat)),
        "--output-dir",
        str(args.output_dir),
    ]
    if bool(args.require_rt_hardware):
        command.append("--require-rt-hardware")
    return command


def run_variant(
    args: argparse.Namespace,
    *,
    variant: str,
    points: tuple[Any, ...],
    point_fingerprint: Any,
) -> dict[str, Any]:
    if variant == EMBREE:
        return run_embree_same_contract_control(args, points=points)
    if variant == LEGACY:
        return run_legacy_optix_grouped_stream_labels(args, points=points)
    if variant == RUNNER:
        return run_productized_prepared_execution_runner(
            args,
            points=points,
            point_fingerprint=point_fingerprint,
        )
    raise ValueError(f"unsupported variant: {variant}")


def run_embree_same_contract_control(args: argparse.Namespace, *, points: tuple[Any, ...]) -> dict[str, Any]:
    import numpy as np
    from numba import cuda

    prepared_grid = None
    prepared_threshold = None
    measured_rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        prepare_start = time.perf_counter()
        point_columns = rt.point_rows_to_partner_columns(points, partner="numba")
        prepared_grid = rt.prepare_radius_graph_components_3d_numba_grid_partner_columns(
            point_columns,
            radius=float(args.radius),
            partner="numba",
        )
        prepared_threshold = rt.prepare_embree_fixed_radius_count_threshold_3d(points)
        prepare_sec = time.perf_counter() - prepare_start
        point_index_by_id = {int(point.id): index for index, point in enumerate(points)}
        total_iterations = int(args.warmup) + int(args.repeat)
        for iteration in range(total_iterations):
            run_start = time.perf_counter()
            embree_start = time.perf_counter()
            threshold_rows = prepared_threshold.run_raw(
                points,
                radius=float(args.radius),
                threshold=int(args.min_neighbors),
            )
            try:
                counts_host = np.zeros((len(points),), dtype=np.uint32)
                flags_host = np.zeros((len(points),), dtype=np.uint32)
                for row_index in range(len(threshold_rows)):
                    row = threshold_rows.rows_ptr[row_index]
                    query_index = point_index_by_id[int(row.query_id)]
                    counts_host[query_index] = int(row.neighbor_count)
                    flags_host[query_index] = int(row.threshold_reached)
                embree_threshold_row_count = len(threshold_rows)
            finally:
                threshold_rows.close()
            embree_sec = time.perf_counter() - embree_start
            upload_start = time.perf_counter()
            neighbor_counts_device = cuda.to_device(counts_host)
            core_flags_device = cuda.to_device(flags_host)
            cuda.synchronize()
            upload_sec = time.perf_counter() - upload_start
            continuation_start = time.perf_counter()
            result = rt.radius_graph_components_3d_numba_prepared_grid_partner_columns(
                prepared_grid,
                min_neighbors=int(args.min_neighbors),
                core_flags=core_flags_device,
                neighbor_counts=neighbor_counts_device,
                core_flag_source="embree_prepared_fixed_radius_count_threshold_3d_compact_rows",
                return_metadata=True,
            )
            continuation_sec = time.perf_counter() - continuation_start
            signature_start = time.perf_counter()
            signature = signature_from_numba_label_columns(result["columns"], point_count=len(points))
            signature_sec = time.perf_counter() - signature_start
            measured_rows.append(
                {
                    "iteration": iteration,
                    "is_warmup": iteration < int(args.warmup),
                    "elapsed_sec": time.perf_counter() - run_start,
                    "signature": signature,
                    "timing_sec": {
                        "embree_threshold_compact_rows_sec": embree_sec,
                        "embree_native_traversal_sec": float(
                            getattr(prepared_threshold, "last_traversal_seconds", 0.0)
                        ),
                        "embree_threshold_columns_upload_sec": upload_sec,
                        "numba_component_label_continuation_sec": continuation_sec,
                        "canonical_signature_from_labels_sec": signature_sec,
                    },
                    "metadata": dict(result["metadata"]),
                    "embree_threshold_row_count": embree_threshold_row_count,
                }
            )
    finally:
        if prepared_threshold is not None:
            prepared_threshold.close()
        close = getattr(prepared_grid, "close", None)
        if callable(close):
            close()
    return finalize_variant_payload(
        args,
        variant=EMBREE,
        started=started,
        prepare_sec=prepare_sec,
        measured_rows=measured_rows,
        extra_metadata={
            "component_union_control_backend": "embree",
            "expected_route": "embree prepared fixed-radius core flags plus generic numba component-label continuation",
        },
    )


def run_legacy_optix_grouped_stream_labels(args: argparse.Namespace, *, points: tuple[Any, ...]) -> dict[str, Any]:
    measured_rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    prepare_start = time.perf_counter()
    with rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
        points,
        radius=float(args.radius),
        component_threshold=int(args.min_neighbors),
        backend="optix",
        partner="numba",
        strategy="grouped_stream",
    ) as prepared:
        prepare_sec = time.perf_counter() - prepare_start
        total_iterations = int(args.warmup) + int(args.repeat)
        for iteration in range(total_iterations):
            run_start = time.perf_counter()
            adapter_start = time.perf_counter()
            result = rt.fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=int(args.min_neighbors),
                return_metadata=True,
            )
            adapter_sec = time.perf_counter() - adapter_start
            signature_start = time.perf_counter()
            signature = signature_from_numba_label_columns(result["columns"], point_count=len(points))
            signature_sec = time.perf_counter() - signature_start
            measured_rows.append(
                {
                    "iteration": iteration,
                    "is_warmup": iteration < int(args.warmup),
                    "elapsed_sec": time.perf_counter() - run_start,
                    "signature": signature,
                    "timing_sec": {
                        "legacy_grouped_stream_label_adapter_sec": adapter_sec,
                        "canonical_signature_from_labels_sec": signature_sec,
                    },
                    "metadata": dict(result["metadata"]),
                }
            )
    return finalize_variant_payload(
        args,
        variant=LEGACY,
        started=started,
        prepare_sec=prepare_sec,
        measured_rows=measured_rows,
        extra_metadata={
            "expected_route": "existing optix grouped-stream component-label route",
            "legacy_optix_grouped_stream_label_control": True,
        },
    )


def run_productized_prepared_execution_runner(
    args: argparse.Namespace,
    *,
    points: tuple[Any, ...],
    point_fingerprint: Any,
) -> dict[str, Any]:
    started = time.perf_counter()
    cache = rt.ExplicitPreparedSessionCache(max_entries=1)
    try:
        result = rt.run_radius_graph_component_union_3d_prepared_session(
            point_rows=points,
            point_rows_fingerprint=point_fingerprint,
            radius=float(args.radius),
            min_neighbors=int(args.min_neighbors),
            partner="numba",
            cache=cache,
            warmup_count=int(args.warmup),
            measured_repeat_count=int(args.repeat),
            retain_repeat_outputs=True,
        )
        metadata = result.to_metadata()
        outputs = tuple(result.output)
        measured_seconds = tuple(float(value) for value in metadata.get("measured_repeat_seconds", ()))
        if len(outputs) != int(args.repeat):
            raise RuntimeError("productized runner output count does not match repeat")
        if len(measured_seconds) != int(args.repeat):
            raise RuntimeError("productized runner measured timing count does not match repeat")
        measured_rows: list[dict[str, Any]] = []
        for index, output in enumerate(outputs):
            signature_start = time.perf_counter()
            signature = signature_from_numba_label_columns(output["columns"], point_count=len(points))
            signature_sec = time.perf_counter() - signature_start
            measured_rows.append(
                {
                    "iteration": int(args.warmup) + index,
                    "is_warmup": False,
                    "elapsed_sec": measured_seconds[index] + signature_sec,
                    "signature": signature,
                    "timing_sec": {
                        "prepared_runner_measured_sec": measured_seconds[index],
                        "canonical_signature_from_labels_sec": signature_sec,
                    },
                    "metadata": dict(output.get("metadata", {})),
                }
            )
        prepare_sec = float(metadata.get("outer_prepare_or_cache_sec", 0.0))
        payload = finalize_variant_payload(
            args,
            variant=RUNNER,
            started=started,
            prepare_sec=prepare_sec,
            measured_rows=measured_rows,
            extra_metadata={
                "expected_route": "productized run_radius_graph_component_union_3d_prepared_session",
                "prepared_execution_session_runner_metadata": metadata,
            },
        )
        payload["prepared_execution_session_runner_metadata"] = metadata
        payload["runtime_executed"] = bool(metadata.get("runtime_executed"))
        payload["runtime_trunk_executes_end_to_end"] = bool(
            metadata.get("runtime_trunk_executes_end_to_end")
        )
        payload["productized_execution_path"] = metadata.get("productized_execution_path")
        payload["primitive_family"] = metadata.get("primitive_family")
        payload["continuation_contract"] = metadata.get("continuation_contract")
        payload["component_union_phase_accounting_visible"] = bool(
            metadata.get("component_union_phase_accounting_visible")
        )
        payload["component_label_columns_present"] = bool(
            metadata.get("component_label_columns_present")
        )
        payload["component_signature_pass_executed"] = bool(
            metadata.get("component_signature_pass_executed")
        )
        payload["internal_device_residency_between_rtdl_phases"] = bool(
            metadata.get("internal_device_residency_between_rtdl_phases")
        )
        payload["hot_path_host_materialization"] = bool(metadata.get("hot_path_host_materialization"))
        payload["component_label_pass_accounted"] = bool(metadata.get("component_label_pass_accounted"))
        return payload
    finally:
        cache.clear()


def finalize_variant_payload(
    args: argparse.Namespace,
    *,
    variant: str,
    started: float,
    prepare_sec: float,
    measured_rows: list[dict[str, Any]],
    extra_metadata: dict[str, Any],
) -> dict[str, Any]:
    measured = [row for row in measured_rows if not bool(row["is_warmup"])]
    if len(measured) != int(args.repeat):
        raise RuntimeError(f"{variant} measured row count does not match repeat")
    signatures = [canonical_component_signature(row["signature"]) for row in measured]
    stable_signature = len({json.dumps(sig, sort_keys=True) for sig in signatures}) == 1
    phase_names = sorted({name for row in measured for name in row["timing_sec"]})
    timing_breakdown = {
        name: float(statistics.median(float(row["timing_sec"][name]) for row in measured if name in row["timing_sec"]))
        for name in phase_names
    }
    timing_breakdown["prepare_sec"] = float(prepare_sec)
    metadata_rows = [dict(row.get("metadata", {})) for row in measured]
    return {
        "variant": variant,
        "status": "ok" if stable_signature else "failed",
        "schema": SCHEMA,
        "dataset": str(args.dataset),
        "point_count": int(args.point_count),
        "radius": float(args.radius),
        "min_neighbors": int(args.min_neighbors),
        "seed": int(args.seed),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "component_labels_contract": True,
        "component_label_outputs_present": True,
        "component_signature_substituted_for_labels": False,
        "canonical_component_signature": signatures[-1],
        "canonical_component_signature_stable": stable_signature,
        "hot_query_median_sec": float(statistics.median(float(row["elapsed_sec"]) for row in measured)),
        "runner_inclusive_wall_median_sec": time.perf_counter() - started,
        "timing_breakdown_sec": timing_breakdown,
        "metadata_sample": metadata_rows[-1] if metadata_rows else {},
        "extra_metadata": extra_metadata,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "all_app_pod_spend_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "external_embedding_or_zero_copy_claim_authorized": False,
    }


def signature_from_numba_label_columns(columns: dict[str, object], *, point_count: int) -> dict[str, Any]:
    return dict(
        rt_dbscan_app._cluster_signature_from_numba_label_columns(  # noqa: SLF001
            columns,
            point_count=int(point_count),
        )
    )


def canonical_component_signature(signature: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(signature, dict):
        return None
    cluster_sizes = signature.get("cluster_sizes")
    if not isinstance(cluster_sizes, dict):
        return None
    return {
        "cluster_sizes": tuple(sorted(int(value) for value in cluster_sizes.values() if int(value) > 0)),
        "core_count": int(signature.get("core_count", -1)),
        "noise_count": int(signature.get("noise_count", -1)),
    }


def build_payload(
    *,
    args: argparse.Namespace,
    environment: dict[str, Any],
    point_set: dict[str, Any],
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
        "component_union_m39_harness_exists": True,
        "same_generated_point_set_enforced": bool(args.variant == "all"),
        "component_labels_contract": True,
        "component_signature_shortcut_blocked": True,
        "material_set_a_candidate": bool(comparisons.get("material_set_a_candidate", False)),
        "legacy_no_regression": bool(comparisons.get("legacy_no_regression", False)),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "all_app_pod_spend_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "external_embedding_or_zero_copy_claim_authorized": False,
        "comparisons": comparisons,
    }
    return {
        "schema": SCHEMA,
        "tool": "v3_phoenix_component_union_m38_pod_ab",
        "status": status,
        "date": "2026-06-23",
        "args": {
            "variant": str(args.variant),
            "dataset": str(args.dataset),
            "point_count": int(args.point_count),
            "radius": float(args.radius),
            "min_neighbors": int(args.min_neighbors),
            "seed": int(args.seed),
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "dry_run": bool(args.dry_run),
            "require_rt_hardware": bool(args.require_rt_hardware),
            "hard_cap_sec": float(args.hard_cap_sec),
        },
        "environment": environment,
        "point_set": point_set,
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
            "all_app_pod_spend_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "external_embedding_or_zero_copy_claim_authorized": False,
            "v4_work_authorized": False,
            "c_abi_work_authorized": False,
            "embedding_work_authorized": False,
        },
        "goal_level_decision_audit": {
            "decision": "implement M39 local harness before spending the focused POD budget",
            "was_i_foolish": "No.",
            "foolish_actions": (
                "It would be foolish to treat the M38 protocol as data or to run the pod "
                "before the local harness proves same input, label outputs, metadata, and cap handling."
            ),
            "other_path": "Run the focused POD immediately from the fresh M37 helper. That could repeat the old unreviewed-harness failure.",
            "different_path_now": "Use this harness to gate local correctness and only then run the single focused POD allowed by M38 consensus.",
        },
    }


def payload_status(*, args: argparse.Namespace, failed_checks: list[str]) -> str:
    if bool(args.dry_run):
        return STATUS_DRY_RUN_NOT_RELEASE
    if failed_checks:
        return STATUS_RUN_FAILED_NOT_RELEASE
    return STATUS_RUN_COMPLETE_NOT_RELEASE


def comparison_payload(variant_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if {EMBREE, LEGACY, RUNNER} - set(variant_payloads):
        if any(row.get("status") == "dry_run" for row in variant_payloads.values()):
            return {"status": "dry_run_no_performance_interpretation"}
        return {"status": "missing_variants_no_performance_interpretation"}
    if any(variant_payloads[item].get("status") == "dry_run" for item in ALL_VARIANTS):
        return {"status": "dry_run_no_performance_interpretation"}
    embree = variant_payloads[EMBREE]
    legacy = variant_payloads[LEGACY]
    runner = variant_payloads[RUNNER]
    embree_sig = embree.get("canonical_component_signature")
    legacy_sig = legacy.get("canonical_component_signature")
    runner_sig = runner.get("canonical_component_signature")
    all_signatures_match = embree_sig == legacy_sig == runner_sig and embree_sig is not None
    runner_vs_embree_hot = _safe_div(embree.get("hot_query_median_sec"), runner.get("hot_query_median_sec"))
    runner_vs_embree_wall = _safe_div(
        embree.get("runner_inclusive_wall_median_sec"),
        runner.get("runner_inclusive_wall_median_sec"),
    )
    runner_vs_legacy_wall = _safe_div(
        legacy.get("runner_inclusive_wall_median_sec"),
        runner.get("runner_inclusive_wall_median_sec"),
    )
    runner_vs_legacy_hot = _safe_div(
        legacy.get("hot_query_median_sec"),
        runner.get("hot_query_median_sec"),
    )
    material = (
        all_signatures_match
        and _at_least(runner_vs_embree_hot, 1.20)
        and _at_least(runner_vs_embree_wall, 1.20)
        and bool(runner.get("runtime_trunk_executes_end_to_end"))
        and bool(runner.get("component_label_columns_present"))
        and not bool(runner.get("component_signature_pass_executed"))
    )
    legacy_no_regression = _at_least(runner_vs_legacy_wall, 0.98)
    return {
        "status": "computed",
        "all_variant_canonical_component_signatures_match": all_signatures_match,
        "runner_vs_embree_hot_speedup": runner_vs_embree_hot,
        "runner_vs_embree_wall_speedup": runner_vs_embree_wall,
        "runner_vs_legacy_hot_speedup": runner_vs_legacy_hot,
        "runner_vs_legacy_wall_speedup": runner_vs_legacy_wall,
        "material_set_a_candidate": bool(material and legacy_no_regression),
        "legacy_no_regression": bool(legacy_no_regression),
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
        if not bool(row.get("component_labels_contract")):
            failed.append(f"{variant}_component_labels_contract_missing")
        if row.get("canonical_component_signature") is None:
            failed.append(f"{variant}_canonical_signature_missing")
        if bool(row.get("component_signature_substituted_for_labels")):
            failed.append(f"{variant}_signature_substituted_for_labels")
    if set(selected_variants) == set(ALL_VARIANTS):
        if not bool(comparisons.get("all_variant_canonical_component_signatures_match")):
            failed.append("canonical_component_signatures_do_not_match")
        if not _at_least(comparisons.get("runner_vs_embree_hot_speedup"), 1.20):
            failed.append("runner_vs_embree_hot_below_1_20x")
        if not _at_least(comparisons.get("runner_vs_embree_wall_speedup"), 1.20):
            failed.append("runner_vs_embree_wall_below_1_20x")
        if not _at_least(comparisons.get("runner_vs_legacy_wall_speedup"), 0.98):
            failed.append("runner_vs_legacy_wall_below_0_98x")
        runner = variant_payloads.get(RUNNER, {})
        if not bool(runner.get("runtime_trunk_executes_end_to_end")):
            failed.append("runner_runtime_trunk_not_end_to_end")
        if not bool(runner.get("component_union_phase_accounting_visible")):
            failed.append("runner_component_union_phase_accounting_missing")
        if not bool(runner.get("component_label_columns_present")):
            failed.append("runner_component_label_columns_missing")
        if bool(runner.get("component_signature_pass_executed")):
            failed.append("runner_component_signature_pass_executed")
        if bool(runner.get("hot_path_host_materialization")):
            failed.append("runner_hot_path_host_materialization")
    return failed


def point_set_metadata(args: argparse.Namespace, *, fingerprint: Any | None, generated: bool) -> dict[str, Any]:
    return {
        "dataset": str(args.dataset),
        "point_count": int(args.point_count),
        "seed": int(args.seed),
        "radius": float(args.radius),
        "min_neighbors": int(args.min_neighbors),
        "generated_once_in_process": bool(generated),
        "same_generated_point_set_required": True,
        "point_rows_fingerprint": fingerprint,
    }


def environment_payload(*, require_rt_hardware: bool) -> dict[str, Any]:
    return {
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "hardware_gate": v3_optix_hardware_gate.build_payload(
            require_rt_hardware=bool(require_rt_hardware),
            sample_nvidia_smi=None,
        ),
    }


def ensure_hard_cap(started: float, *, args: argparse.Namespace) -> None:
    elapsed = time.perf_counter() - started
    if elapsed > float(args.hard_cap_sec):
        raise TimeoutError(f"M39 hard cap exceeded before next variant: {elapsed:.1f}s")


@contextmanager
def hard_cap_watchdog(args: argparse.Namespace):
    if bool(args.dry_run):
        yield
        return

    def expire() -> None:
        print(
            f"[phoenix-v3-component-union-m39] hard-cap exceeded: "
            f"{float(args.hard_cap_sec):.1f}s; exiting 124",
            flush=True,
        )
        os._exit(124)

    timer = threading.Timer(float(args.hard_cap_sec), expire)
    timer.daemon = True
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


@contextmanager
def heartbeat(label: str, *, interval_sec: float):
    stop = threading.Event()
    started = time.perf_counter()

    def run() -> None:
        while not stop.wait(max(1.0, float(interval_sec))):
            print(
                f"[phoenix-v3-component-union-m39] heartbeat variant={label} "
                f"elapsed={time.perf_counter() - started:.1f}s",
                flush=True,
            )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=1.0)


def _safe_div(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if float(denominator) <= 0.0 or not math.isfinite(float(denominator)):
        return None
    return float(numerator) / float(denominator)


def _at_least(value: Any, threshold: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) >= float(threshold)


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _readme(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Component-Union M39 Focused Harness",
        "",
        f"Status: `{payload['status']}`",
        "",
        "```json",
        json.dumps(_json_ready(payload["summary"]), indent=2, sort_keys=True),
        "```",
        "",
        "This harness does not authorize V3 release, all-app POD, public speedup",
        "wording, broad V3-over-V2 wording, true-zero-copy wording, V4 work, C ABI",
        "work, or embedding work.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
