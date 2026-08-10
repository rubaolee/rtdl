"""Private RTDL 3.0 end-to-end driver for the locked RayJoin workload."""

from pathlib import Path
from types import SimpleNamespace
import sys

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_rayjoin_migration", APP_DIR / "rtdl3_action_migration.py")
_pipeline = load_app_module(
    "rtdl_rayjoin_section57_overlay_columnar_binary",
    APP_DIR / "section57_overlay_columnar_binary.py",
)


def run_v3_app(*, execution_mode: str = "reference"):
    if execution_mode == "reference":
        pair = _migration.run_local_semantic_pair()
        selected = "action_cpu_reference"
    elif execution_mode == "compiler":
        pair = _migration.run_compiler_backend_pair()
        selected = "compiler_selected_action"
    else:
        raise ValueError("RayJoin execution_mode must be reference or compiler")
    return build_locked_workload_driver_result(
        app="rayjoin",
        workload="bounded_descriptor_carrier_downstream_consumer",
        requested_execution_mode=execution_mode,
        selected_execution=selected,
        stages=(
            {"kind": "input", "name": "locked_descriptor_carrier_columns", "owner": "app"},
            {"kind": "spatial_producer", "name": "preexisting_v2_carrier_producer", "owner": "app"},
            {"kind": "action_or_operator", "name": "typed_grouped_count_and_point_row_sum_action", "owner": "rtdl"},
            {"kind": "output", "name": "canonical_descriptor_pair_summary", "owner": "app"},
        ),
        output=pair["actual"],
        matched=bool(pair["matched"]),
        source_result=pair,
    )


def run_v3_real_input(
    args,
    *,
    execution_mode: str = "reference",
    collect_phase_trace: bool = False,
):
    """Run the existing complete overlay producer with the V3 Action consumer."""

    if execution_mode not in {"reference", "compiler"}:
        raise ValueError("RayJoin execution_mode must be reference or compiler")
    summary = _pipeline.run_pipeline(
        args,
        descriptor_consumer=_migration.descriptor_action_consumer(
            execution_mode=execution_mode,
            collect_phase_trace=collect_phase_trace,
        ),
    )
    consumer = summary["downstream_consumer"]
    return {
        "schema": "rtdl.research.v3.paper_app_driver.rayjoin_real_input.v1",
        "app": "rayjoin",
        "requested_execution_mode": execution_mode,
        "selected_execution": consumer["partner"],
        "application_selected_backend": False,
        "stages": (
            {"kind": "input", "name": "rayjoin_cdb_planar_maps", "owner": "app"},
            {"kind": "spatial_producer", "name": "complete_overlay_carrier_pipeline", "owner": "app+rtdl"},
            {"kind": "action_or_operator", "name": "typed_grouped_count_and_point_row_sum_action", "owner": "rtdl"},
            {"kind": "output", "name": "canonical_descriptor_pair_summary", "owner": "app"},
        ),
        "output": consumer["actual_action_summary"],
        "matched": bool(consumer["matched_v2_consumer"]),
        "source_result": summary,
        "real_input_frontdoor_supported": True,
        "full_overlay_producer_executed": True,
        "v3_action_consumer_executed": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def run_v3_prepared_six_batch(
    args,
    *,
    max_event_rows: int,
    collect_phase_trace: bool = True,
    validate_against_v2: bool = True,
):
    """Run the locked six-batch route with a compiler-selected prepared Action."""

    v2_summary = lambda carrier: _pipeline.descriptor_pair_count_projected_device(
        carrier
    )
    consumer = _migration.prepared_descriptor_action_consumer(
        max_event_rows=max_event_rows,
        validate_against_v2=validate_against_v2,
        collect_phase_trace=collect_phase_trace,
        v2_summary=v2_summary,
    )
    canonical_planar_bindings = {
        name: _migration.CANONICAL_ALGORITHM_BINDINGS[name]
        for name in (
            "directed_segment_point_location",
            "segment_pair_grouped_range_exact_count",
        )
    }
    sentinel = object()
    previous = getattr(args, "_rtdl_v3_canonical_planar_bindings", sentinel)
    setattr(args, "_rtdl_v3_canonical_planar_bindings", canonical_planar_bindings)
    try:
        try:
            protocol = _pipeline.run_pipeline_repeat_protocol(
                args,
                descriptor_consumer=consumer,
            )
            before_close = consumer.to_metadata()
        finally:
            consumer.close()
    finally:
        if previous is sentinel:
            delattr(args, "_rtdl_v3_canonical_planar_bindings")
        else:
            setattr(args, "_rtdl_v3_canonical_planar_bindings", previous)
    after_close = consumer.to_metadata()
    rows = tuple(protocol.get("measured_rows", ()))
    protocol["descriptor_consumer_specialization"] = (
        _descriptor_consumer_specialization_metadata(before_close)
    )
    protocol["consumer_specialization_scope"] = (
        "method_specific_consumer_setup_once_before_six_batch_primary"
    )
    return {
        "schema": "rtdl.research.v3.paper_app_driver.rayjoin_prepared_six_batch.v1",
        "app": "rayjoin",
        "requested_execution_mode": "compiler",
        "selected_execution": "compiler_selected_action",
        "application_selected_backend": False,
        "output": tuple(
            {
                "batch_index": index,
                "lsi_row_count": int(row["lsi_row_count"]),
                "descriptor_pair_count": int(row["descriptor_pair_count"]),
                "total_groups": int(row["descriptor_total_groups"]),
                "total_point_rows": int(row["descriptor_total_point_rows"]),
                "pair_rows_sha256": row.get("descriptor_pair_rows_sha256"),
                "matched_v2_consumer": row.get("descriptor_matched_v2_consumer"),
                "source_event_columns_device_resident": row.get(
                    "descriptor_source_event_columns_device_resident"
                ),
                "host_event_column_materialization_used": row.get(
                    "descriptor_host_event_column_materialization_used"
                ),
            }
            for index, row in enumerate(rows)
        ),
        "source_result": protocol,
        "prepared_consumer_metadata": before_close,
        "prepared_consumer_closed_metadata": after_close,
        "six_distinct_query_batches": len(rows) == 6,
        "device_resident_carrier_required": True,
        "python_event_rows_materialized": False,
        "real_input_frontdoor_supported": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def _descriptor_consumer_specialization_metadata(
    consumer_metadata: dict[str, object],
) -> dict[str, object]:
    """Normalize host/device compiler setup without assuming one placement."""

    prepared = consumer_metadata.get("prepared")
    if not isinstance(prepared, dict):
        raise RuntimeError("RayJoin prepared consumer metadata is missing")
    identity = prepared.get("identity")
    if not isinstance(identity, dict):
        raise RuntimeError("RayJoin prepared consumer identity is missing")
    backend = identity.get("selected_backend")
    template = identity.get("selected_template")
    plan_and_prepare = float(consumer_metadata.get("plan_and_prepare_seconds", 0.0))
    compile_seconds = float(consumer_metadata.get("compile_seconds", 0.0))

    if backend == "numba" and template == "grouped_i64x2_count_sum":
        raw = prepared.get("compiler_owned_eager_device_specialization")
        if not isinstance(raw, dict):
            raise RuntimeError(
                "RayJoin device plan lacks compiler-owned specialization metadata"
            )
        eager_seconds = float(raw.get("elapsed_seconds", 0.0))
        specialization_count = 1 if raw.get("complete_physical_route_executed") else 0
        physical_route = "compiler_selected_device_ordered_grouped_i64x2"
        complete_physical_route = bool(raw.get("complete_physical_route_executed"))
        backend_detail = dict(raw)
    elif backend == "host" and template == "sorted_host_i64x2_count_sum":
        timing = prepared.get("timing")
        lifecycle = prepared.get("backend_runtime_lifecycle")
        if not isinstance(timing, dict) or not isinstance(lifecycle, dict):
            raise RuntimeError(
                "RayJoin host plan lacks compiler-owned specialization metadata"
            )
        eager_seconds = float(timing.get("eager_specialization_seconds", 0.0))
        specialization_count = int(timing.get("eager_specialization_count", 0))
        physical_route = "compiler_selected_host_sorted_grouped_i64x2"
        # Host upload/download and sorting are input-dependent query work.  Its
        # only reusable setup is the checked scan specialization.
        complete_physical_route = False
        backend_detail = {
            "contract": "rtdl.rayjoin.host_checked_scan_specialization.v1",
            "checked_scan_specialization_count": specialization_count,
            "checked_scan_specialization_seconds": eager_seconds,
            "input_dependent_download_and_sort_executed_in_query": True,
            "complete_physical_route_executed_during_setup": False,
            "runtime_lifecycle": dict(lifecycle),
        }
    else:
        raise RuntimeError(
            "RayJoin compiler selected an unsupported grouped physical route: "
            f"{backend}:{template}"
        )

    compile_plan_prepare = compile_seconds + plan_and_prepare
    return {
        "contract": "rtdl.rayjoin.v3_descriptor_consumer_specialization.v1",
        "physical_route": physical_route,
        "selected_backend": backend,
        "selected_template": template,
        "elapsed_seconds": eager_seconds,
        "specialization_count": specialization_count,
        "complete_physical_route_executed": complete_physical_route,
        "registered_query_count": 0,
        "executed_once_before_primary": True,
        "excluded_from_writer_free_hot_primary": True,
        "plan_and_prepare_seconds": plan_and_prepare,
        "plan_and_prepare_seconds_includes_eager_specialization": True,
        "compile_plan_prepare_seconds": compile_plan_prepare,
        "compile_plan_prepare_seconds_includes_eager_specialization": True,
        "compile_plan_prepare_excluding_eager_seconds": max(
            0.0, compile_plan_prepare - eager_seconds
        ),
        "backend_specialization": backend_detail,
        "runtime_speedup_claimed": False,
    }


def run_v2_prepared_six_batch(args):
    """Run the locked Goal5039 six-batch V2 surface through a public app API."""

    specialization = _pipeline.eager_specialize_descriptor_pair_rows_projected_device()
    protocol = _pipeline.run_pipeline_repeat_protocol(
        args,
        descriptor_consumer=_pipeline.descriptor_pair_rows_projected_device,
    )
    protocol["descriptor_consumer_specialization"] = specialization
    protocol["consumer_specialization_scope"] = (
        "method_specific_consumer_setup_once_before_six_batch_primary"
    )
    return protocol


def real_input_args(
    left,
    right,
    *,
    pair_name: str = "v3_real_input",
    compiled_group: bool = True,
):
    """Build the bounded option envelope used by the private V3 driver."""

    return SimpleNamespace(
        left=str(Path(left)),
        right=str(Path(right)),
        pair_name=pair_name,
        author_overlay_compute_sec=None,
        swap_query_map_ids=False,
        bounded_exact_lsi_capacity=0,
        bounded_exact_lsi_repeat_diagnostic=0,
        device_columnar=False,
        native_lexsort=False,
        compiled_group=bool(compiled_group),
        validate_device_order=False,
        prepared_lsi_replay=False,
        exact_lsi_device_columns=False,
        bounded_exact_lsi_device_columns=False,
        point_location_device_face_columns=False,
        fast_scaled_point_pack=True,
        device_resident_carrier=False,
        device_carrier_concurrent_sides=False,
        compiled_group_side_order="0,1",
    )


def prepared_six_batch_args(
    left,
    right,
    *,
    lsi_capacity: int,
    pair_name: str = "v3_prepared_six_batch",
):
    """Build the compiler-mode envelope matching the Goal5039 hot route."""

    if not isinstance(lsi_capacity, int) or isinstance(lsi_capacity, bool) or lsi_capacity <= 0:
        raise ValueError("lsi_capacity must be a positive integer")
    return SimpleNamespace(
        left=str(Path(left)),
        right=str(Path(right)),
        pair_name=pair_name,
        author_overlay_compute_sec=None,
        cache_dir=None,
        swap_query_map_ids=False,
        no_numba_warmup=False,
        repeat=1,
        warmup_runs=0,
        prepared_operator_session=False,
        prepared_lsi_base_session=True,
        query_chain_batches=6,
        prepared_query_batch_right_vertex_points=True,
        prepared_query_batch_left_vertex_points=True,
        prepared_query_batch_segment_arrays=True,
        prepared_lsi_base_workspace_warmup=True,
        prepared_query_batch_lsi_query_workspaces=True,
        device_columnar=True,
        validate_device_order=False,
        native_lexsort=True,
        compiled_group=False,
        device_resident_carrier=True,
        device_carrier_concurrent_sides=True,
        compiled_group_side_order="0,1",
        prepared_lsi_replay=False,
        exact_lsi_device_columns=False,
        bounded_exact_lsi_device_columns=True,
        bounded_exact_lsi_capacity=lsi_capacity,
        bounded_exact_lsi_repeat_diagnostic=0,
        collect_complete_descriptor_pair_rows_for_validation=True,
        point_location_device_face_columns=True,
        fast_scaled_point_pack=False,
        generic_lsi_prewarm=False,
    )


__all__ = (
    "prepared_six_batch_args",
    "real_input_args",
    "run_v3_app",
    "run_v3_prepared_six_batch",
    "run_v3_real_input",
    "run_v2_prepared_six_batch",
)
