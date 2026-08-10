"""Private RTDL 3.0 end-to-end driver for the locked RayDB workload."""

import json
from pathlib import Path
import sys
import time

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_raydb_migration", APP_DIR / "rtdl3_action_migration.py")
_app = load_app_module("rtdl3_raydb_app", APP_DIR / "raydb_reproduction.py")
_packet = load_app_module("rtdl3_raydb_packet", APP_DIR / "run_ssb_packet_rtdl.py")


def run_v3_app(*, execution_mode: str = "reference"):
    if execution_mode == "reference":
        pair = _migration.run_local_semantic_pair()
        selected = "action_cpu_reference"
    elif execution_mode == "compiler":
        pair = _migration.run_optix_semantic_pair()
        selected = "compiler_selected_action"
    else:
        raise ValueError("RayDB execution_mode must be reference or compiler")
    return build_locked_workload_driver_result(
        app="raydb",
        workload="bounded_q21_predicate_grouped_signed_i64_sum",
        requested_execution_mode=execution_mode,
        selected_execution=selected,
        stages=(
            {"kind": "input", "name": "locked_q21_triangle_and_fact_columns", "owner": "app"},
            {"kind": "spatial_producer", "name": "stable_ray_triangle_candidates_3d", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "typed_predicate_grouped_i64_sum_action", "owner": "rtdl"},
            {"kind": "output", "name": "canonical_grouped_sum_rows", "owner": "app"},
        ),
        output=pair["actual_rows"],
        matched=bool(pair["matched"]),
        source_result=pair,
    )


def run_v3_rows(
    rows,
    predicate,
    *,
    execution_mode: str = "reference",
    collect_phase_trace: bool = False,
):
    rows = tuple(rows)
    if execution_mode == "reference":
        pair = _migration.run_reference_rows(rows, predicate)
    elif execution_mode == "compiler":
        pair = _migration.run_optix_rows(
            rows, predicate, collect_phase_trace=collect_phase_trace
        )
    else:
        raise ValueError("RayDB execution_mode must be reference or compiler")
    return {
        "schema": "rtdl.research.v3.paper_app_driver.raydb_rows.v1",
        "app": "raydb",
        "requested_execution_mode": execution_mode,
        "selected_execution": pair["backend"],
        "application_selected_backend": False,
        "stages": (
            {"kind": "input", "name": "flat_relation_rows_and_exact_list_predicate", "owner": "app"},
            {"kind": "spatial_producer", "name": "stable_ray_triangle_candidates_3d", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "typed_predicate_grouped_i64_sum_action", "owner": "rtdl"},
            {"kind": "output", "name": "canonical_grouped_sum_rows", "owner": "app"},
        ),
        "output": pair["actual_rows"],
        "matched": bool(pair["matched"]),
        "source_result": pair,
        "real_input_frontdoor_supported": True,
        "arbitrary_fixed_schema_rows_supported": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def run_v3_packet_partitioned(
    packet_path,
    *,
    partition_rows: int = 5_000_000,
    collect_phase_trace: bool = True,
):
    """Run one packet through one compiler plan and bounded partition scenes."""

    import numpy as np
    from rtdsl import (
        exact_dense_ordinal_encode_integral,
        exact_dense_row_ordinal_encode_integral,
        pack_triangles_3d_from_arrays,
    )
    from rtdsl.action_phase_trace import ActionPhaseTrace, action_phase

    if (
        not isinstance(partition_rows, int)
        or isinstance(partition_rows, bool)
        or partition_rows <= 0
    ):
        raise ValueError("partition_rows must be a positive integer")
    packet_path = Path(packet_path).resolve()
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    row_count = int(packet["row_count"])
    group_dimension_count = int(packet["group_dimension_count"])
    predicate_dimension_count = int(packet["predicate_dimension_count"])
    column_count = int(packet["column_count"])
    data_path = Path(packet["data_path"])
    predicate_path = Path(packet["predicate_path"])
    expected_rows_path = Path(packet["expected_rows_path"])
    expected_size = row_count * column_count * np.dtype("<i4").itemsize
    if data_path.stat().st_size != expected_size:
        raise ValueError(
            f"packet size mismatch: expected {expected_size}, got {data_path.stat().st_size}"
        )
    data_sha256 = _packet._require_sha256(
        data_path, packet["data_sha256"], label="data packet"
    )
    predicate_sha256 = _packet._require_sha256(
        predicate_path, packet["predicate_sha256"], label="predicate"
    )
    expected_rows_sha256 = _packet._require_sha256(
        expected_rows_path,
        packet["expected_rows_sha256"],
        label="expected rows",
    )
    raw_predicates, scan_types = _packet._parse_predicate(
        predicate_path, predicate_dimension_count
    )
    if list(scan_types) != list(packet["scan_types"]):
        raise ValueError("predicate scan types differ from the packet manifest")

    registered_primary_start = time.perf_counter()
    trace = (
        ActionPhaseTrace(app="raydb", route="sf10_q11_partitioned_grouped_sum")
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="packet_columns_to_typed_arrays"):
        columns = np.memmap(
            data_path,
            dtype="<i4",
            mode="r",
            shape=(column_count, row_count),
        )
        aggregate_values = columns[0]
        group_columns = [
            columns[1 + index] for index in range(group_dimension_count)
        ]
        scan_offset = 1 + group_dimension_count
        scan_columns = [
            columns[scan_offset + index]
            for index in range(predicate_dimension_count)
        ]
        extra_multiplier = columns[-1] if packet["complex_aggregate"] else None
        group_encoding = exact_dense_row_ordinal_encode_integral(
            group_columns,
            ordinal_dtype=np.uint32,
        )
        unique_groups = group_encoding.unique_values
        group_ids = group_encoding.ordinals
        scan_unique_values = []
        scan_encodings = []
        merged_scan = None
        for scan_column in scan_columns:
            scan_encoding = exact_dense_ordinal_encode_integral(
                scan_column,
                ordinal_dtype=np.uint64,
            )
            unique_values = scan_encoding.unique_values
            ordinals = scan_encoding.ordinals
            merged_scan = (
                ordinals
                if merged_scan is None
                else merged_scan * len(unique_values) + ordinals
            )
            scan_unique_values.append(unique_values)
            scan_encodings.append(scan_encoding)
        if merged_scan is None:
            raise ValueError("at least one scan dimension is required")
        primitive_values = aggregate_values.astype(np.int64)
        if extra_multiplier is not None:
            primitive_values = _packet._multiply_packet_i32_columns_to_i64(
                aggregate_values,
                extra_multiplier,
            )
        group_tuples = tuple(
            tuple(int(item) for item in row.tolist()) for row in unique_groups
        )
        rays, ray_grid = _packet._build_rays(
            min_aggregate=int(aggregate_values.min()),
            max_aggregate=int(aggregate_values.max()),
            group_count=len(group_tuples),
            scan_unique_values=scan_unique_values,
            raw_predicates=raw_predicates,
            scan_types=scan_types,
            interval_x=int(packet["interval_x"]),
            interval_y=int(packet["interval_y"]),
        )

    def primitive_partitions():
        for start in range(0, row_count, partition_rows):
            stop = min(row_count, start + partition_rows)
            with action_phase(
                trace,
                "event_producer",
                label=f"pack_triangle_partition_{start}_{stop}",
            ):
                primitive_ids = np.arange(start, stop, dtype=np.uint32)
                triangles = pack_triangles_3d_from_arrays(
                    primitive_ids,
                    aggregate_values[start:stop],
                    group_ids[start:stop],
                    merged_scan[start:stop],
                    aggregate_values[start:stop].astype(np.int64)
                    + 2 * int(packet["interval_x"]),
                    group_ids[start:stop],
                    merged_scan[start:stop],
                    aggregate_values[start:stop],
                    group_ids[start:stop].astype(np.int64)
                    + 2 * int(packet["interval_y"]),
                    merged_scan[start:stop],
                )
            yield {
                "primitive_id_start": start,
                "triangles": triangles,
                "primitive_group_ids": group_ids[start:stop],
                "primitive_values": primitive_values[start:stop],
            }

    plan = _migration.prepare_partitioned_compiler_plan(
        group_tuples=group_tuples,
        rays=rays,
        phase_trace=trace,
    )
    try:
        execution = plan.execute_partitions(
            primitive_partitions(),
            expected_primitive_count=row_count,
        )
    finally:
        plan.close()
    plan_metadata = plan.to_metadata()
    registered_primary_elapsed_seconds = (
        time.perf_counter() - registered_primary_start
    )
    if trace is not None:
        trace.mark_not_applicable(
            "app_validation",
            reason=(
                "the complete grouped-row correctness comparator is mandatory "
                "but remains outside the registered performance endpoint"
            ),
        )
    phase_trace = trace.finish() if trace is not None else None
    expected_rows = json.loads(expected_rows_path.read_text(encoding="utf-8"))
    matched = execution["actual_rows"] == expected_rows
    return {
        "schema": "rtdl.research.v3.paper_app_driver.raydb_packet_partitioned.v1",
        "app": "raydb",
        "requested_execution_mode": "compiler",
        "selected_execution": "compiler_selected_action",
        "application_selected_backend": False,
        "packet_identity": {
            "path": str(packet_path),
            "packet_json_sha256": _packet.sha256_file(packet_path),
            "data_sha256": data_sha256,
            "predicate_sha256": predicate_sha256,
            "expected_rows_sha256": expected_rows_sha256,
            "row_count": row_count,
            "query_id": packet["query_id"],
            "scale_factor": int(packet.get("scale_factor", 1)),
        },
        "ray_grid": ray_grid,
        "input_encoding_certificates": {
            "group_rows": group_encoding.to_metadata(),
            "scan_columns": [
                encoding.to_metadata() for encoding in scan_encodings
            ],
            "application_identity_used": False,
            "mandatory_work_inside_registered_primary": True,
        },
        "output": execution["actual_rows"],
        "expected_output": expected_rows,
        "matched": matched,
        "partition_count": execution["partition_count"],
        "partition_rows": partition_rows,
        "compiler_plan_reused_across_partitions": execution[
            "compiler_plan_reused_across_partitions"
        ],
        "prepared_ray_batch_reused_across_partitions": execution[
            "prepared_ray_batch_reused_across_partitions"
        ],
        "prepared_ray_batch_execution_count": execution[
            "prepared_ray_batch_execution_count"
        ],
        "prepared_ray_batch_metadata": execution["prepared_ray_batch_metadata"],
        "prepared_partition_count": execution["prepared_partition_count"],
        "partition_ledger": execution["partition_ledger"],
        "partition_ledger_schema": "rtdl.raydb.v3.partition_ledger.v1",
        "compiler_lifecycle": plan_metadata,
        "registered_primary_timing": {
            "contract_id": "loaded_sf10_tables_to_canonical_group_rows__lower_prepare_twelve_partitions_project",
            "elapsed_seconds": registered_primary_elapsed_seconds,
            "starts_after_input_hash_verification": True,
            "ends_before_correctness_comparator": True,
            "includes_app_lowering": True,
            "includes_compiler_work": True,
            "includes_result_projection": True,
            "phase_trace_uses_same_registered_endpoint": phase_trace is not None,
            "correctness_comparator_outside_registered_endpoint": True,
        },
        "phase_trace": phase_trace,
        "real_input_frontdoor_supported": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


FlatRow = _app.FlatRow
ExactListPredicate = _app.ExactListPredicate


__all__ = (
    "ExactListPredicate",
    "FlatRow",
    "run_v3_app",
    "run_v3_packet_partitioned",
    "run_v3_rows",
)
