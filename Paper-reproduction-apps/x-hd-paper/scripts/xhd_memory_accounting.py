"""App-owned memory accounting helpers for X-HD paper reproduction.

The author Figure 11 log uses a memory schema with fields such as ``BVH``,
``Grid``, ``MBRs B``, ``WL``, and ``WL Heavy Peak``.  RTDL's X-HD paper app is
implemented as generic routes, so this module defines an explicit bridge from
the route metadata we currently expose to a conservative, reviewable memory
accounting schema.

The helpers intentionally return per-field status strings.  Estimated and
unavailable fields must not be treated as author memory parity.
"""

from __future__ import annotations

from typing import Any, Mapping


BYTES_PER_INT64 = 8
BYTES_PER_AUTHOR_UINT32 = 4
BYTES_PER_FLOAT64 = 8
CELL_MBR_AXIS_COUNT_3D = 3
FRONTIER_ROW_FIELD_COUNT = 8


def memory_field_json(*, status: str, bytes_value: int | None, method: str) -> dict[str, Any]:
    return {
        "status": status,
        "bytes": bytes_value,
        "mb": None if bytes_value is None else bytes_value / (1024.0 * 1024.0),
        "method": method,
    }


def _directed_a_to_b_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    try:
        return payload["RTDL"]["route"]["directed_a_to_b"]
    except Exception as exc:  # pragma: no cover - exercised by caller tests
        raise ValueError("expected RTDL hd_exec-compatible payload with directed_a_to_b route") from exc


def _rtdl_route_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    try:
        return payload["RTDL"]
    except Exception as exc:  # pragma: no cover
        raise ValueError("expected RTDL hd_exec-compatible payload") from exc


def estimate_cell_mbr_grid_bytes(route: Mapping[str, Any]) -> dict[str, int]:
    """Estimate generic grid-cell column bytes from route metadata.

    The estimate follows the public ``point_grid_cell_mbrs_*`` column contract:
    compact cell ids, original cell ids, begin offsets, counts, sorted point ids,
    sorted point row indices, grid shape/bounds, and optional dense lookup table.
    Cell MBR min/max arrays are reported separately as ``MBRs B`` to match the
    author's named memory component.
    """

    cell_count = int(route.get("grid_cell_count", 0))
    point_row_index_count = int(
        route.get("initial_native_phase_timings", {}).get(
            "point_row_index_count",
            route.get("point_count_b", 0),
        )
    )
    dense_count = int(route.get("initial_dense_lookup_cell_capacity", 0))

    grid_index_bytes = (
        # cell_ids, original_cell_ids, point_begin_offsets, point_counts
        (4 * cell_count * BYTES_PER_INT64)
        # point_ids and point_row_indices are target-point ordered arrays
        + (2 * point_row_index_count * BYTES_PER_INT64)
        # grid_shape plus lower/upper global grid bounds
        + (3 * BYTES_PER_INT64)
        + (2 * CELL_MBR_AXIS_COUNT_3D * BYTES_PER_FLOAT64)
        # dense encoded-cell -> compact-cell-position table used by native seed
        + (dense_count * BYTES_PER_INT64)
    )
    cell_mbr_bytes = (
        2 * CELL_MBR_AXIS_COUNT_3D * cell_count * BYTES_PER_FLOAT64
    )
    return {
        "grid_index_bytes": int(grid_index_bytes),
        "cell_mbr_bytes": int(cell_mbr_bytes),
    }


def estimate_frontier_worklist_bytes(route: Mapping[str, Any]) -> int:
    """Estimate allocated generic frontier row table bytes.

    The route reports ``frontier_row_capacity`` when the native frontier builder
    allocates a bounded row table.  A frontier row has eight 64-bit columns in
    the current app contract:

    frontier kind, query row id, query point id, cell id, point begin offset,
    point count, min distance, and max distance.
    """

    capacity = route.get("frontier_row_capacity")
    if capacity is None:
        capacity = 0
    return int(capacity) * FRONTIER_ROW_FIELD_COUNT * BYTES_PER_INT64


def estimate_input_column_bytes(point_count_a: int, point_count_b: int) -> int:
    """Estimate RTDL host-side point column matrix and id-array bytes."""

    per_point = CELL_MBR_AXIS_COUNT_3D * BYTES_PER_FLOAT64 + BYTES_PER_INT64
    return int(point_count_a + point_count_b) * per_point


def estimate_nearest_state_bytes(point_count_a: int) -> int:
    """Estimate route nearest-state arrays retained for max-nearest reduction."""

    # query id, nearest item id, nearest distance
    return int(point_count_a) * (2 * BYTES_PER_INT64 + BYTES_PER_FLOAT64)


def author_offload_mapping_from_native_telemetry(native_memory: Mapping[str, Any]) -> dict[str, Any]:
    """Map generic native offload telemetry to author-shaped X-HD fields.

    The mapping is intentionally status-bearing.  Author Figure 11 stores the
    heavy-worklist peak as ``offloading_size * 2 * sizeof(uint32_t)``.  RTDL's
    current generic telemetry measures a two-id queue shape with 64-bit ids, so
    the row-count shape can be mapped, but the measured byte denominator is not
    identical to the author's byte denominator.
    """

    if not isinstance(native_memory, Mapping):
        raise ValueError("native_memory must be a mapping")
    schema = str(native_memory.get("schema", ""))
    if not schema.endswith(".memory_telemetry.v2"):
        return {
            "schema": "rtdl.paper_reproduction.xhd.author_offload_field_mapping.v1",
            "status": "unavailable_native_memory_telemetry_v2_required",
            "source_telemetry_schema": schema or None,
            "author_shaped_fields": {
                "OffloadingSize": {
                    "status": "unavailable_native_v2_heavy_offload_rows_required",
                    "value": None,
                    "method": "Goal5282 requires native v2 heavy_offload_peak_rows telemetry.",
                },
                "WL": memory_field_json(
                    status="unavailable_native_v2_in_miss_queue_required",
                    bytes_value=None,
                    method="No native v2 queue telemetry was available.",
                ),
                "WL Heavy Peak": memory_field_json(
                    status="unavailable_native_v2_heavy_offload_peak_required",
                    bytes_value=None,
                    method="No native v2 heavy_offload_queue_peak telemetry was available.",
                ),
            },
            "rtdl_measured_fields": {},
            "denominator_alignment": {
                "offloading_size_row_count_shape_available": False,
                "same_byte_denominator_author_figure11": False,
                "same_denominator_author_figure11": False,
                "reason": "Native telemetry v2 was not available.",
            },
            "claim_boundary": {
                "figure11_reproduced": False,
                "author_memory_parity_claimed": False,
                "performance_ratio_claimed": False,
            },
        }

    heavy_rows = int(native_memory.get("heavy_offload_peak_rows", 0) or 0)
    rtdl_queue_peak_bytes = int(native_memory.get("heavy_offload_queue_peak_bytes", 0) or 0)
    rtdl_expected_pair_bytes = heavy_rows * 2 * BYTES_PER_INT64
    author_width_equivalent_bytes = heavy_rows * 2 * BYTES_PER_AUTHOR_UINT32
    in_queue_capacity = int(native_memory.get("in_queue_capacity", 0) or 0)
    miss_queue_capacity = int(native_memory.get("miss_queue_capacity", 0) or 0)
    return {
        "schema": "rtdl.paper_reproduction.xhd.author_offload_field_mapping.v1",
        "status": "bounded_author_offload_shape_mapped__figure11_byte_denominator_not_aligned",
        "source_telemetry_schema": schema,
        "author_shaped_fields": {
            "OffloadingSize": {
                "status": "mapped_from_generic_heavy_offload_peak_rows",
                "value": heavy_rows,
                "method": (
                    "Maps generic heavy_offload_peak_rows to the author's "
                    "OffloadingSize row-count concept. This is a bounded "
                    "shape mapping, not proof of paper Figure 11 parity."
                ),
            },
            "WL": memory_field_json(
                status="not_aligned_native_in_queue_capacity_is_not_author_in_plus_miss_queue",
                bytes_value=None,
                method=(
                    "Author WL is in_queue + miss_queue over source points. "
                    "Current RTDL native v2 telemetry reports in_queue_capacity="
                    f"{in_queue_capacity} attempted frontier hits and "
                    f"miss_queue_capacity={miss_queue_capacity}; this is not "
                    "the same author queue denominator."
                ),
            ),
            "WL Heavy Peak": memory_field_json(
                status="author_uint32_width_equivalent_from_generic_offload_rows",
                bytes_value=author_width_equivalent_bytes,
                method=(
                    "Author formula: OffloadingSize * 2 * sizeof(uint32_t). "
                    "The row-count shape comes from generic heavy_offload_peak_rows; "
                    "this is author-width equivalent accounting, not measured "
                    "RTDL queue allocation bytes."
                ),
            ),
        },
        "rtdl_measured_fields": {
            "generic_heavy_offload_queue_peak": memory_field_json(
                status="measured_native_rtdl_uint64_pair_queue_bytes",
                bytes_value=rtdl_queue_peak_bytes,
                method=(
                    "Native RTDL v2 telemetry reports heavy_offload_queue_peak_bytes "
                    "for a generic two-id offload row using RTDL's current 64-bit id "
                    "queue shape."
                ),
            ),
            "expected_rtdl_uint64_pair_queue_peak": memory_field_json(
                status="computed_from_generic_offload_rows_for_consistency_check",
                bytes_value=rtdl_expected_pair_bytes,
                method="heavy_offload_peak_rows * 2 * sizeof(uint64_t).",
            ),
        },
        "denominator_alignment": {
            "offloading_size_row_count_shape_available": True,
            "rtdl_queue_bytes_match_expected_uint64_pair_shape": bool(
                rtdl_queue_peak_bytes == rtdl_expected_pair_bytes
            ),
            "same_byte_denominator_author_figure11": bool(
                rtdl_queue_peak_bytes == author_width_equivalent_bytes
            ),
            "same_denominator_author_figure11": False,
            "reason": (
                "The offload row-count shape is now mappable, but measured RTDL "
                "queue bytes use 64-bit ids while author Figure 11 WL Heavy Peak "
                "uses uint32 ids. WL is also not aligned because RTDL in_queue "
                "capacity is attempted frontier hits rather than author "
                "in_queue + miss_queue over source points."
            ),
        },
        "claim_boundary": {
            "figure11_reproduced": False,
            "author_memory_parity_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def rtdl_memory_accounting_from_hd_exec_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    rtdl = _rtdl_route_from_payload(payload)
    route = _directed_a_to_b_from_payload(payload)
    point_count_a = int(rtdl.get("point_count_a", 0))
    point_count_b = int(rtdl.get("point_count_b", 0))
    grid = estimate_cell_mbr_grid_bytes(route)
    worklist_bytes = estimate_frontier_worklist_bytes(route)
    input_bytes = estimate_input_column_bytes(point_count_a, point_count_b)
    nearest_state_bytes = estimate_nearest_state_bytes(point_count_a)
    native_memory = route.get("frontier_native_memory_telemetry") or route.get("native_memory_telemetry")
    native_memory = native_memory if isinstance(native_memory, Mapping) else {}
    accel_output_bytes = int(native_memory.get("accel_output_bytes", 0) or 0)
    offload_mapping = author_offload_mapping_from_native_telemetry(native_memory)
    wl_heavy_mapping = offload_mapping["author_shaped_fields"]["WL Heavy Peak"]

    author_mapped_fields = {
        "BVH": (
            memory_field_json(
                status="measured_native_optix_accel_output_buffer",
                bytes_value=accel_output_bytes,
                method=(
                    "Native OptiX cell-MBR frontier telemetry: accel_output_bytes "
                    "from the GAS output buffer. This excludes transient build "
                    "workspace and is still not author Figure 11 parity."
                ),
            )
            if accel_output_bytes > 0
            else memory_field_json(
                status="unavailable_opaque_native_acceleration_memory_not_reported",
                bytes_value=None,
                method="RTDL current route metadata does not expose OptiX/acceleration-structure memory bytes.",
            )
        ),
        "Grid": memory_field_json(
            status="estimated_from_generic_grid_column_contract",
            bytes_value=grid["grid_index_bytes"],
            method="4 cell int64 columns + 2 target-point int64 columns + grid shape/bounds + dense lookup.",
        ),
        "MBRs B": memory_field_json(
            status="estimated_from_cell_mbr_columns",
            bytes_value=grid["cell_mbr_bytes"],
            method="6 float64 min/max cell-MBR columns over occupied grid cells.",
        ),
        "WL": memory_field_json(
            status="estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue",
            bytes_value=worklist_bytes,
            method=(
                "frontier_row_capacity * 8 generic 64-bit frontier row columns. "
                "This is RTDL route capacity accounting, not the author's Figure 11 "
                "WL denominator; author WL is in_queue + miss_queue, computed in "
                "hausdorff_distance_rt.h as 2 * n_points_a * sizeof(uint32_t)."
            ),
        ),
        "WL Heavy Peak": memory_field_json(
            status=str(wl_heavy_mapping["status"]),
            bytes_value=wl_heavy_mapping["bytes"],
            method=str(wl_heavy_mapping["method"]),
        )
        if offload_mapping["denominator_alignment"]["offloading_size_row_count_shape_available"]
        else memory_field_json(
            status="unavailable_no_author_heavy_offload_equivalent_in_current_rtdl_route",
            bytes_value=None,
            method="Current RTDL route does not expose an author-like heavy-cell offload worklist peak.",
        ),
    }

    rtdl_only_fields = {
        "native_accel_build_temp": memory_field_json(
            status=(
                "measured_native_optix_transient_accel_build_workspace"
                if int(native_memory.get("accel_temp_build_bytes", 0) or 0) > 0
                else "unavailable_or_not_applicable"
            ),
            bytes_value=(
                int(native_memory.get("accel_temp_build_bytes", 0))
                if int(native_memory.get("accel_temp_build_bytes", 0) or 0) > 0
                else None
            ),
            method="Transient OptiX GAS build workspace from native telemetry; not an author Figure 11 field.",
        ),
        "native_accel_aabb_input": memory_field_json(
            status=(
                "measured_native_optix_aabb_input_buffer"
                if int(native_memory.get("accel_aabb_input_bytes", 0) or 0) > 0
                else "unavailable_or_not_applicable"
            ),
            bytes_value=(
                int(native_memory.get("accel_aabb_input_bytes", 0))
                if int(native_memory.get("accel_aabb_input_bytes", 0) or 0) > 0
                else None
            ),
            method="Device AABB input buffer used to build the OptiX GAS; not an author Figure 11 field.",
        ),
        "native_route_device_buffers_excluding_accel": memory_field_json(
            status=(
                "measured_native_route_device_workspace"
                if int(native_memory.get("device_buffer_bytes_excluding_accel", 0) or 0) > 0
                else "unavailable_or_not_applicable"
            ),
            bytes_value=(
                int(native_memory.get("device_buffer_bytes_excluding_accel", 0))
                if int(native_memory.get("device_buffer_bytes_excluding_accel", 0) or 0) > 0
                else None
            ),
            method="Native cell-MBR frontier route device buffers excluding OptiX GAS output/temp/AABB.",
        ),
        "input_column_matrices_and_ids": memory_field_json(
            status="estimated_rtdl_host_column_memory_not_author_field",
            bytes_value=input_bytes,
            method="source/target float64 coordinate matrices plus int64 ids.",
        ),
        "nearest_state": memory_field_json(
            status="estimated_rtdl_route_state_not_author_field",
            bytes_value=nearest_state_bytes,
            method="query ids, nearest item ids, and nearest distances for max-nearest reduction.",
        ),
    }

    estimated_author_mapped_bytes = sum(
        int(field["bytes"])
        for field in author_mapped_fields.values()
        if isinstance(field.get("bytes"), int)
    )
    estimated_rtdl_only_bytes = sum(
        int(field["bytes"])
        for field in rtdl_only_fields.values()
        if isinstance(field.get("bytes"), int)
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.rtdl_memory_accounting.v1",
        "route_label": rtdl.get("route_label"),
        "route_contract": rtdl.get("route", {}).get("route_contract"),
        "point_count_a": point_count_a,
        "point_count_b": point_count_b,
        "grid_cell_count": int(route.get("grid_cell_count", 0)),
        "frontier_row_capacity": route.get("frontier_row_capacity"),
        "frontier_row_count": int(route.get("frontier_row_count", 0)),
        "author_mapped_fields": author_mapped_fields,
        "rtdl_only_fields": rtdl_only_fields,
        "estimated_author_mapped_bytes_excluding_unavailable": estimated_author_mapped_bytes,
        "estimated_author_mapped_mb_excluding_unavailable": estimated_author_mapped_bytes
        / (1024.0 * 1024.0),
        "estimated_total_accounted_bytes_excluding_unavailable": estimated_author_mapped_bytes
        + estimated_rtdl_only_bytes,
        "estimated_total_accounted_mb_excluding_unavailable": (
            estimated_author_mapped_bytes + estimated_rtdl_only_bytes
        )
        / (1024.0 * 1024.0),
        "claim_boundary": {
            "figure11_reproduced": False,
            "author_memory_parity_claimed": False,
            "exact_gpu_allocator_measurement_claimed": False,
            "performance_ratio_claimed": False,
        },
        "author_offload_field_mapping": offload_mapping,
    }
