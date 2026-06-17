from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import statistics
import time

from .optix_runtime import prepare_optix_fixed_radius_neighbors_3d
from .reference import Point3D
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import summarize_no_hidden_copy_classifications


V3_M19_RANKED_SUMMARY_BRIDGE_VERSION = "rtdl.v3_0.ranked_summary_bridge.m19"
V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_VERSION = (
    "rtdl.v3_0.ranked_summary_bridge.m19.chunked.v1"
)
V3_M19_RANKED_SUMMARY_BRIDGE_STATUS = (
    "m19_ranked_summary_prepared_graph_partner_bridge_internal_claims_gated"
)
V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_STATUS = (
    "m19_chunked_ranked_summary_partner_bridge_internal_claims_gated"
)
V3_M19_GRAPH_ID = "prepared_ranked_summary_graph_partner_bridge"
V3_M19_CONTRACT_KEY = "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner_v1"
V3_M19_PARTNERS = ("cupy", "numba")
V3_M19_DISTRIBUTIONS = ("uniform", "clustered", "shell")
V3_M19_GRAPH_QUERY_COUNT_CAP = 65_536
V3_M19_CHUNK_PLAN_VERSION = "rtdl.v3_0.m19.ranked_summary_bridge_chunk_plan.v1"
V3_M19_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)
V3_M19_DEFAULT_REQUESTS = (
    {"radius": 0.015, "k_max": 50},
    {"radius": 0.020, "k_max": 50},
    {"radius": 0.025, "k_max": 50},
)


def run_v3_m19_ranked_summary_bridge_case(
    *,
    transfer_counter_library: str | Path,
    point_count: int = 65_536,
    query_count: int | None = None,
    distribution: str = "uniform",
    requests: tuple[Mapping[str, object], ...] = V3_M19_DEFAULT_REQUESTS,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
) -> dict[str, object]:
    validate_v3_public_name(V3_M19_GRAPH_ID, label="M19 graph id")
    point_count = int(point_count)
    query_count = point_count if query_count is None else int(query_count)
    warmups = int(warmups)
    repeats = int(repeats)
    if point_count <= 0:
        raise GraphValidationError("point_count must be positive")
    if query_count <= 0:
        raise GraphValidationError("query_count must be positive")
    if query_count > point_count:
        raise GraphValidationError("query_count must not exceed point_count")
    execution_path_plan = plan_v3_m19_ranked_summary_bridge_chunks(
        point_count=point_count,
        query_count=query_count,
        distribution=distribution,
    )
    if query_count > V3_M19_GRAPH_QUERY_COUNT_CAP:
        raise GraphValidationError(
            "query_count must be <= 65536 for the current prepared graph path; "
            "use plan_v3_m19_ranked_summary_bridge_chunks for the explicit large-query chunk plan"
        )
    if warmups < 0 or repeats <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    normalized_requests = _normalize_requests(requests)
    max_radius = max(float(request["radius"]) for request in normalized_requests)

    transfer_counter = CudaTransferCounter(transfer_counter_library)
    points = make_v3_m19_ranked_summary_points(point_count, distribution=distribution)

    transfer_counter.reset()
    transfer_counter.enable()
    prepare_start = time.perf_counter()
    try:
        scene = prepare_optix_fixed_radius_neighbors_3d(points, max_radius=max_radius)
        queries = scene.prepare_query_points(points[:query_count])
        graph = scene.prepare_ranked_summary_prepared_queries_batch_graph(
            queries,
            normalized_requests,
            precision="float32",
        )
        prepare_seconds = time.perf_counter() - prepare_start
        prepare_snapshot = transfer_counter.disable_and_snapshot()
    except Exception:
        transfer_counter.disable_and_snapshot()
        raise

    try:
        rows = []
        for partner in V3_M19_PARTNERS:
            rows.append(
                _run_partner_row(
                    graph=graph,
                    partner=partner,
                    transfer_counter=transfer_counter,
                    warmups=warmups,
                    repeats=repeats,
                )
            )
    finally:
        graph.close()
        queries.close()
        scene.close()

    signatures = {tuple(row["validation_signature"]) for row in rows}
    payload = {
        "version": V3_M19_RANKED_SUMMARY_BRIDGE_VERSION,
        "status": V3_M19_RANKED_SUMMARY_BRIDGE_STATUS,
        "graph_id": V3_M19_GRAPH_ID,
        "contract_key": V3_M19_CONTRACT_KEY,
        "parameters": {
            "point_count": point_count,
            "query_count": query_count,
            "distribution": distribution,
            "requests": tuple(dict(request) for request in normalized_requests),
            "request_count": len(normalized_requests),
            "warmups": warmups,
            "repeats": repeats,
            "allowed_non_column_host_to_device_bytes": V3_M19_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            "transfer_counter_library": str(transfer_counter_library),
            "hardware": hardware,
        },
        "execution_path_plan": execution_path_plan,
        "preparation": {
            "prepared_scene_used": True,
            "prepared_query_points_used": True,
            "cuda_graph_prepared": True,
            "prepared_scene_and_query_resident_before_hot_window": True,
            "initial_host_to_device_upload_expected": True,
            "prepare_seconds": prepare_seconds,
            "prepare_transfer_counter_snapshot": prepare_snapshot,
            "prepare_window_claim_boundary": (
                "The M19 prepare window intentionally includes initial host point upload and graph "
                "construction. It is recorded, not claimed as a no-hidden-copy hot path."
            ),
        },
        "partner_rows": tuple(rows),
        "comparison": {
            "signature_match": len(signatures) == 1,
            "partners": V3_M19_PARTNERS,
            "hot_no_hidden_column_copy_ready": all(bool(row["hot_no_hidden_column_copy_ready"]) for row in rows),
            "device_result_materialization_after_hot_window": all(
                bool(row["device_result_materialization_after_hot_window"]) for row in rows
            ),
            "prepared_graph_reused_for_both_partners": True,
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "reason": (
                "M19 validates the current ranked-summary route as a prepared OptiX graph "
                "that can hand device-resident partial aggregate rows to bounded CuPy and Numba "
                "same-stream partner reductions before result materialization. It does not claim "
                "paper parity, public performance, whole-app speedup, or end-to-end zero copy."
            ),
        },
        "measurement_methodology_limits": {
            "transfer_counter_scope": (
                "LD_PRELOAD CUDA transfer counter observes CUDA copy calls made in this process "
                "during the measured windows. It does not prove absence of copies through "
                "unobserved internal library paths, child processes, or non-CUDA DMA."
            ),
            "hot_window_scope": (
                "The hot window starts after prepared scene/query/graph residency and ends after "
                "same-stream partner device reduction. Aggregate materialization happens after "
                "the hot transfer counter is disabled."
            ),
        },
    }
    validate_v3_m19_ranked_summary_bridge_payload(payload)
    return payload


def run_v3_m19_ranked_summary_bridge_chunked_case(
    *,
    transfer_counter_library: str | Path,
    point_count: int = 131_072,
    query_count: int | None = None,
    max_query_count: int = V3_M19_GRAPH_QUERY_COUNT_CAP,
    distribution: str = "uniform",
    requests: tuple[Mapping[str, object], ...] = V3_M19_DEFAULT_REQUESTS,
    warmups: int = 1,
    repeats: int = 3,
    hardware: str = "pod_rtx_4000_ada",
) -> dict[str, object]:
    validate_v3_public_name(V3_M19_GRAPH_ID, label="M19 graph id")
    point_count = int(point_count)
    query_count = point_count if query_count is None else int(query_count)
    max_query_count = int(max_query_count)
    warmups = int(warmups)
    repeats = int(repeats)
    if point_count <= 0:
        raise GraphValidationError("point_count must be positive")
    if query_count <= 0:
        raise GraphValidationError("query_count must be positive")
    if query_count > point_count:
        raise GraphValidationError("query_count must not exceed point_count")
    if max_query_count <= 0 or max_query_count > V3_M19_GRAPH_QUERY_COUNT_CAP:
        raise GraphValidationError("max_query_count must be in [1, 65536]")
    if warmups < 0 or repeats <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    execution_path_plan = plan_v3_m19_ranked_summary_bridge_chunks(
        point_count=point_count,
        query_count=query_count,
        max_query_count=max_query_count,
        distribution=distribution,
    )
    normalized_requests = _normalize_requests(requests)
    max_radius = max(float(request["radius"]) for request in normalized_requests)

    transfer_counter = CudaTransferCounter(transfer_counter_library)
    points = make_v3_m19_ranked_summary_points(point_count, distribution=distribution)

    transfer_counter.reset()
    transfer_counter.enable()
    scene_prepare_start = time.perf_counter()
    try:
        scene = prepare_optix_fixed_radius_neighbors_3d(points, max_radius=max_radius)
        scene_prepare_seconds = time.perf_counter() - scene_prepare_start
        scene_prepare_snapshot = transfer_counter.disable_and_snapshot()
    except Exception:
        transfer_counter.disable_and_snapshot()
        raise

    partner_chunk_rows: dict[str, list[dict[str, object]]] = {
        partner: [] for partner in V3_M19_PARTNERS
    }
    chunk_preparation_rows: list[dict[str, object]] = []
    try:
        for chunk in execution_path_plan["chunks"]:
            chunk_index = int(chunk["chunk_index"])
            start = int(chunk["query_start_inclusive"])
            end = int(chunk["query_end_exclusive"])
            transfer_counter.reset()
            transfer_counter.enable()
            chunk_prepare_start = time.perf_counter()
            try:
                queries = scene.prepare_query_points(points[start:end])
                graph = scene.prepare_ranked_summary_prepared_queries_batch_graph(
                    queries,
                    normalized_requests,
                    precision="float32",
                )
                chunk_prepare_seconds = time.perf_counter() - chunk_prepare_start
                chunk_prepare_snapshot = transfer_counter.disable_and_snapshot()
            except Exception:
                transfer_counter.disable_and_snapshot()
                raise

            try:
                chunk_preparation_rows.append(
                    {
                        **dict(chunk),
                        "prepared_query_points_used": True,
                        "cuda_graph_prepared": True,
                        "chunk_prepare_seconds": float(chunk_prepare_seconds),
                        "chunk_prepare_transfer_counter_snapshot": chunk_prepare_snapshot,
                    }
                )
                for partner in V3_M19_PARTNERS:
                    row = _run_partner_row(
                        graph=graph,
                        partner=partner,
                        transfer_counter=transfer_counter,
                        warmups=warmups,
                        repeats=repeats,
                    )
                    partner_chunk_rows[partner].append(
                        {
                            **row,
                            "chunk_index": chunk_index,
                            "query_start_inclusive": start,
                            "query_end_exclusive": end,
                        }
                    )
            finally:
                graph.close()
                queries.close()
    finally:
        scene.close()

    partner_rows = tuple(
        _combine_chunked_partner_rows(partner, tuple(rows))
        for partner, rows in sorted(partner_chunk_rows.items())
    )
    signatures = {tuple(row["combined_validation_signature"]) for row in partner_rows}
    payload = {
        "version": V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_VERSION,
        "status": V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_STATUS,
        "graph_id": V3_M19_GRAPH_ID,
        "contract_key": V3_M19_CONTRACT_KEY,
        "parameters": {
            "point_count": point_count,
            "query_count": query_count,
            "distribution": distribution,
            "requests": tuple(dict(request) for request in normalized_requests),
            "request_count": len(normalized_requests),
            "max_query_count": max_query_count,
            "chunk_count": int(execution_path_plan["chunk_count"]),
            "warmups": warmups,
            "repeats": repeats,
            "allowed_non_column_host_to_device_bytes": V3_M19_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            "transfer_counter_library": str(transfer_counter_library),
            "hardware": hardware,
        },
        "execution_path_plan": execution_path_plan,
        "preparation": {
            "prepared_scene_used": True,
            "prepared_scene_reused_across_chunks": True,
            "prepared_query_points_per_chunk": True,
            "cuda_graph_per_chunk": True,
            "initial_host_to_device_upload_expected": True,
            "scene_prepare_seconds": scene_prepare_seconds,
            "scene_prepare_transfer_counter_snapshot": scene_prepare_snapshot,
            "chunk_preparation_rows": tuple(chunk_preparation_rows),
            "prepare_window_claim_boundary": (
                "The chunked prepare windows include scene upload, per-chunk query preparation, "
                "and per-chunk graph construction. They are recorded, not claimed as no-hidden-copy hot paths."
            ),
        },
        "partner_rows": partner_rows,
        "comparison": {
            "signature_match": len(signatures) == 1,
            "partners": V3_M19_PARTNERS,
            "chunk_count": int(execution_path_plan["chunk_count"]),
            "chunked_runtime_executed": True,
            "hot_no_hidden_column_copy_ready": all(bool(row["hot_no_hidden_column_copy_ready"]) for row in partner_rows),
            "device_result_materialization_after_hot_window": all(
                bool(row["device_result_materialization_after_hot_window"]) for row in partner_rows
            ),
            "prepared_scene_reused_across_chunks": True,
            "cuda_graph_per_chunk": True,
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "large_chunked_runtime_evidence": True,
            "reason": (
                "M19 chunked runtime evidence executes the explicit partner-continuation chunk plan "
                "with prepared scene reuse and per-chunk query/graph preparation. It does not claim "
                "paper parity, public performance, whole-app speedup, or end-to-end zero copy."
            ),
        },
    }
    validate_v3_m19_ranked_summary_bridge_chunked_payload(payload)
    return payload


def plan_v3_m19_ranked_summary_bridge_chunks(
    *,
    point_count: int,
    query_count: int | None = None,
    max_query_count: int = V3_M19_GRAPH_QUERY_COUNT_CAP,
    distribution: str = "unspecified",
    requires_partner_continuation: bool = True,
) -> dict[str, object]:
    """Plan explicit query chunks for the M19 same-stream partner route.

    The M19 runtime graph captures one prepared query batch with a bounded
    query-count cap. For aggregate-only large work, Goal4502 prefers the
    full-batch direct aggregate route. For partner continuation, however, the
    app needs device partial rows, so large work must be chunked instead of
    silently switching to the aggregate-only route.
    """

    normalized_point_count = int(point_count)
    normalized_query_count = (
        normalized_point_count if query_count is None else int(query_count)
    )
    normalized_max_query_count = int(max_query_count)
    continuation_required = bool(requires_partner_continuation)
    if normalized_point_count <= 0:
        raise GraphValidationError("point_count must be positive")
    if normalized_query_count <= 0:
        raise GraphValidationError("query_count must be positive")
    if normalized_query_count > normalized_point_count:
        raise GraphValidationError("query_count must not exceed point_count")
    if normalized_max_query_count <= 0:
        raise GraphValidationError("max_query_count must be positive")
    if not continuation_required:
        raise GraphValidationError("M19 chunk planning is only for partner continuation")

    chunks = []
    query_offset = 0
    while query_offset < normalized_query_count:
        chunk_query_count = min(
            normalized_max_query_count,
            normalized_query_count - query_offset,
        )
        chunks.append(
            {
                "chunk_index": len(chunks),
                "query_offset": query_offset,
                "query_start_inclusive": query_offset,
                "query_end_exclusive": query_offset + chunk_query_count,
                "query_count": chunk_query_count,
                "prepared_scene_reused": True,
                "prepared_query_points_per_chunk": True,
                "cuda_graph_per_chunk": True,
                "same_stream_partner_device_reduction_per_chunk": True,
                "host_materialization_before_partner": False,
            }
        )
        query_offset += chunk_query_count

    single_graph_cap_exceeded = normalized_query_count > normalized_max_query_count
    return {
        "version": V3_M19_CHUNK_PLAN_VERSION,
        "graph_id": V3_M19_GRAPH_ID,
        "contract_key": V3_M19_CONTRACT_KEY,
        "operation": "fixed_radius_ranked_summary_graph_partials_same_stream_partner",
        "distribution": str(distribution),
        "point_count": normalized_point_count,
        "query_count": normalized_query_count,
        "max_query_count": normalized_max_query_count,
        "graph_query_count_cap": V3_M19_GRAPH_QUERY_COUNT_CAP,
        "chunk_count": len(chunks),
        "chunks": tuple(chunks),
        "single_graph_cap_exceeded": single_graph_cap_exceeded,
        "plan_status": (
            "chunked_partner_continuation_required"
            if single_graph_cap_exceeded
            else "single_graph_partner_continuation"
        ),
        "requires_partner_continuation": True,
        "same_stream_partner_device_reduction_required": True,
        "prepared_scene_reuse_required": True,
        "prepared_query_points_per_chunk_required": True,
        "cuda_graph_per_chunk_required": True,
        "aggregate_only_full_batch_direct_substitute_allowed": False,
        "aggregate_only_policy_reference": "Goal4504",
        "large_chunk_runtime_evidence_required": single_graph_cap_exceeded,
        "runtime_executed": False,
        "hidden_auto_dispatch_allowed": False,
        "automatic_partner_selection_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "This is an explicit partner-continuation chunk plan. It does not execute "
            "the chunks, authorize automatic dispatch, or authorize public speedup "
            "wording. Aggregate-only full-batch direct mode is not a substitute when "
            "the app requires same-stream device partial rows for a partner."
        ),
    }


def make_v3_m19_ranked_summary_points(point_count: int, *, distribution: str = "uniform") -> tuple[Point3D, ...]:
    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("M19 ranked-summary point generation requires numpy") from exc
    count = int(point_count)
    if count <= 0:
        raise GraphValidationError("point_count must be positive")
    if distribution == "uniform":
        rng = np.random.default_rng(4419)
        coords = rng.random((count, 3), dtype=np.float64)
    elif distribution == "clustered":
        rng = np.random.default_rng(4420)
        center_count = max(4, min(64, count // 1024))
        centers = rng.random((center_count, 3), dtype=np.float64)
        assignments = rng.integers(0, center_count, size=count)
        coords = centers[assignments] + rng.normal(0.0, 0.018, size=(count, 3))
        coords = np.clip(coords, 0.0, 1.0)
    elif distribution == "shell":
        rng = np.random.default_rng(4421)
        theta = rng.random(count, dtype=np.float64) * (2.0 * np.pi)
        shell_z = rng.uniform(-1.0, 1.0, size=count)
        radial = np.sqrt(np.maximum(0.0, 1.0 - shell_z * shell_z))
        radius = np.clip(rng.normal(0.34, 0.025, size=count), 0.0, 0.49)
        coords = np.empty((count, 3), dtype=np.float64)
        coords[:, 0] = 0.5 + radius * radial * np.cos(theta)
        coords[:, 1] = 0.5 + radius * radial * np.sin(theta)
        coords[:, 2] = 0.5 + radius * shell_z
        coords = np.clip(coords, 0.0, 1.0)
    else:
        raise GraphValidationError(f"unsupported M19 ranked-summary distribution: {distribution}")
    return tuple(
        Point3D(int(index), float(coords[index, 0]), float(coords[index, 1]), float(coords[index, 2]))
        for index in range(count)
    )


def _run_partner_row(
    *,
    graph,
    partner: str,
    transfer_counter: CudaTransferCounter,
    warmups: int,
    repeats: int,
) -> dict[str, object]:
    if partner not in V3_M19_PARTNERS:
        raise GraphValidationError(f"unsupported M19 partner: {partner}")
    for _ in range(warmups):
        device_result = _run_partner_device_result(graph, partner)
        device_result.materialize()

    hot_samples = []
    materialize_samples = []
    hot_snapshots = []
    hot_classifications = []
    signatures = []
    device_metadata_rows = []
    materialize_metadata_rows = []
    for _ in range(repeats):
        transfer_counter.reset()
        transfer_counter.enable()
        hot_start = time.perf_counter()
        try:
            device_result = _run_partner_device_result(graph, partner)
            hot_samples.append(time.perf_counter() - hot_start)
            hot_snapshot = transfer_counter.disable_and_snapshot()
        except Exception:
            transfer_counter.disable_and_snapshot()
            raise

        materialize_start = time.perf_counter()
        materialized = device_result.materialize()
        materialize_samples.append(time.perf_counter() - materialize_start)
        metadata = dict(device_result.metadata)
        materialize_metadata = dict(materialized["metadata"])
        classification = classify_no_hidden_copy_transfer_snapshot(
            hot_snapshot,
            min_named_column_bytes=_m19_min_named_column_bytes(metadata),
            allowed_non_column_host_to_device_bytes=V3_M19_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            measured_window=(
                "prepared_ranked_summary_graph_device_partials_to_partner_device_"
                "aggregate_before_materialization"
            ),
            readiness_source="v3_m19_ranked_summary_hot_transfer_counter_classification",
        )
        signatures.append(_aggregate_signature(materialized["aggregates"]))
        hot_snapshots.append(hot_snapshot)
        hot_classifications.append(classification)
        device_metadata_rows.append(metadata)
        materialize_metadata_rows.append(materialize_metadata)

    if any(signature != signatures[-1] for signature in signatures):
        raise GraphValidationError(f"M19 {partner} signatures changed across repeats")
    hot_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in hot_classifications)
    final_metadata = device_metadata_rows[-1]
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner",
        "prepared_scene_used": True,
        "prepared_query_points_used": True,
        "cuda_graph_replay_used": True,
        "same_stream_partner_device_reduction_used": True,
        "device_resident_partial_rows_for_partner": bool(
            final_metadata.get("device_resident_partial_rows_for_partner")
        ),
        "host_scalar_read_before_consumer": bool(final_metadata.get("host_scalar_read_before_consumer")),
        "host_partial_materialization_before_consumer": bool(
            final_metadata.get("host_partial_materialization_before_consumer")
        ),
        "device_result_materialized_in_hot_window": False,
        "device_result_materialization_after_hot_window": True,
        "validation_signature": signatures[-1],
        "hot_device_run_samples_seconds": tuple(hot_samples),
        "materialize_samples_seconds": tuple(materialize_samples),
        "hot_device_run_seconds_median": statistics.median(hot_samples),
        "materialize_seconds_median": statistics.median(materialize_samples),
        "transfer_counter_samples": tuple(hot_snapshots),
        "transfer_counter_classifications": tuple(hot_classifications),
        "transfer_counter_classification": hot_classifications[-1],
        "transfer_counter_summary": summarize_no_hidden_copy_classifications(tuple(hot_classifications)),
        "hot_transfer_counter_observed": True,
        "hot_no_hidden_column_copy_ready": hot_ready,
        "metadata": {
            "device_execution_metadata": final_metadata,
            "materialization_metadata": materialize_metadata_rows[-1],
        },
        "public_claim_authorized": False,
        "claim_readiness": {
            "prepared_scene_and_query_resident_before_hot_window": True,
            "cuda_graph_replay_used": True,
            "same_stream_partner_device_reduction_used": True,
            "no_hidden_column_copy_ready": hot_ready,
            "measured_window_scope_only": True,
            "public_claim_authorized": False,
        },
    }


def _run_partner_device_result(graph, partner: str):
    if partner == "cupy":
        return graph.replay_same_stream_device_partials_summary_cupy_device()
    if partner == "numba":
        return graph.replay_same_stream_device_partials_summary_numba_device()
    raise GraphValidationError(f"unsupported M19 partner: {partner}")


def _aggregate_signature(aggregates: object) -> tuple[tuple[int, int, int, int, int], ...]:
    rows = tuple(aggregates)
    return tuple(
        (
            int(row["query_count"]),
            int(row["bounded_neighbor_count"]),
            int(row["nearest_id_checksum"]),
            int(row["kth_id_checksum"]),
            int(round(float(row["sum_distance"]) * 1_000_000.0)),
        )
        for row in rows
        if isinstance(row, Mapping)
    )


def _combine_chunked_partner_rows(
    partner: str,
    chunk_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    if not chunk_rows:
        raise GraphValidationError(f"M19 chunked {partner} row has no chunks")
    combined_signature = _combine_chunk_signatures(
        tuple(tuple(tuple(item) for item in row["validation_signature"]) for row in chunk_rows)
    )
    hot_median_sum = sum(float(row["hot_device_run_seconds_median"]) for row in chunk_rows)
    materialize_median_sum = sum(float(row["materialize_seconds_median"]) for row in chunk_rows)
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner_chunked",
        "chunk_count": len(chunk_rows),
        "chunk_rows": chunk_rows,
        "prepared_scene_reused_across_chunks": True,
        "prepared_query_points_per_chunk": all(bool(row["prepared_query_points_used"]) for row in chunk_rows),
        "cuda_graph_per_chunk": all(bool(row["cuda_graph_replay_used"]) for row in chunk_rows),
        "same_stream_partner_device_reduction_per_chunk": all(
            bool(row["same_stream_partner_device_reduction_used"]) for row in chunk_rows
        ),
        "device_resident_partial_rows_for_partner": all(
            bool(row["device_resident_partial_rows_for_partner"]) for row in chunk_rows
        ),
        "host_scalar_read_before_consumer": any(
            bool(row["host_scalar_read_before_consumer"]) for row in chunk_rows
        ),
        "host_partial_materialization_before_consumer": any(
            bool(row["host_partial_materialization_before_consumer"]) for row in chunk_rows
        ),
        "device_result_materialized_in_hot_window": any(
            bool(row["device_result_materialized_in_hot_window"]) for row in chunk_rows
        ),
        "device_result_materialization_after_hot_window": all(
            bool(row["device_result_materialization_after_hot_window"]) for row in chunk_rows
        ),
        "combined_validation_signature": combined_signature,
        "chunk_hot_device_run_seconds_medians": tuple(
            float(row["hot_device_run_seconds_median"]) for row in chunk_rows
        ),
        "chunk_materialize_seconds_medians": tuple(
            float(row["materialize_seconds_median"]) for row in chunk_rows
        ),
        "hot_device_run_seconds_median_sum": float(hot_median_sum),
        "materialize_seconds_median_sum": float(materialize_median_sum),
        "hot_no_hidden_column_copy_ready": all(
            bool(row["hot_no_hidden_column_copy_ready"]) for row in chunk_rows
        ),
        "public_claim_authorized": False,
    }


def _combine_chunk_signatures(
    chunk_signatures: tuple[tuple[tuple[int, int, int, int, int], ...], ...],
) -> tuple[tuple[int, int, int, int, int], ...]:
    if not chunk_signatures:
        raise GraphValidationError("M19 chunked signature requires at least one chunk")
    request_count = len(chunk_signatures[0])
    totals = [[0, 0, 0, 0, 0] for _ in range(request_count)]
    for signature in chunk_signatures:
        if len(signature) != request_count:
            raise GraphValidationError("M19 chunked signatures have inconsistent request counts")
        for request_index, row in enumerate(signature):
            if len(row) != 5:
                raise GraphValidationError("M19 chunked signature row must have five fields")
            for value_index, value in enumerate(row):
                totals[request_index][value_index] += int(value)
    return tuple(tuple(row) for row in totals)


def _m19_min_named_column_bytes(metadata: Mapping[str, object]) -> int:
    partial_count = int(metadata.get("partial_count", 0) or 0)
    request_count = int(metadata.get("request_count", 0) or 0)
    partial_row_bytes = int(metadata.get("partial_row_size_bytes", 40) or 40)
    partial_bytes = partial_count * partial_row_bytes
    aggregate_bytes = request_count * partial_row_bytes
    return max(partial_bytes, aggregate_bytes, 1)


def _normalize_requests(requests: tuple[Mapping[str, object], ...] | object) -> tuple[dict[str, object], ...]:
    normalized = tuple(dict(request) for request in requests)
    if not normalized:
        raise GraphValidationError("M19 requires at least one ranked-summary request")
    for request in normalized:
        radius = float(request.get("radius", 0.0))
        k_max = int(request.get("k_max", 0))
        if radius <= 0.0:
            raise GraphValidationError("M19 request radius must be positive")
        if k_max <= 0 or k_max > 64:
            raise GraphValidationError("M19 request k_max must be in [1, 64]")
        request["radius"] = radius
        request["k_max"] = k_max
    return normalized


def validate_v3_m19_ranked_summary_bridge_payload(payload: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("M19 payload must be a mapping")
    if payload.get("version") != V3_M19_RANKED_SUMMARY_BRIDGE_VERSION:
        raise GraphValidationError("unexpected M19 payload version")
    if payload.get("status") != V3_M19_RANKED_SUMMARY_BRIDGE_STATUS:
        raise GraphValidationError("unexpected M19 payload status")
    preparation = payload.get("preparation", {})
    if not isinstance(preparation, Mapping):
        raise GraphValidationError("M19 payload requires preparation metadata")
    if preparation.get("prepared_scene_and_query_resident_before_hot_window") is not True:
        raise GraphValidationError("M19 requires prepared scene/query residency before hot window")
    if preparation.get("initial_host_to_device_upload_expected") is not True:
        raise GraphValidationError("M19 prepare window must explicitly mark initial upload as expected")
    execution_path_plan = payload.get("execution_path_plan")
    if execution_path_plan is not None:
        validate_v3_m19_ranked_summary_bridge_chunk_plan(execution_path_plan)

    rows = tuple(payload.get("partner_rows", ()))
    if {str(row.get("partner")) for row in rows if isinstance(row, Mapping)} != set(V3_M19_PARTNERS):
        raise GraphValidationError("M19 payload requires CuPy and Numba partner rows")
    signatures = {tuple(tuple(item) for item in row.get("validation_signature", ())) for row in rows}
    if len(signatures) != 1:
        raise GraphValidationError("M19 CuPy and Numba aggregate signatures must match")
    for row in rows:
        if not isinstance(row, Mapping):
            raise GraphValidationError("M19 partner row must be a mapping")
        partner = str(row.get("partner"))
        for key in (
            "prepared_scene_used",
            "prepared_query_points_used",
            "cuda_graph_replay_used",
            "same_stream_partner_device_reduction_used",
            "device_resident_partial_rows_for_partner",
            "device_result_materialization_after_hot_window",
            "hot_transfer_counter_observed",
            "hot_no_hidden_column_copy_ready",
        ):
            if row.get(key) is not True:
                raise GraphValidationError(f"{partner} row must prove {key}=true")
        for key in (
            "host_scalar_read_before_consumer",
            "host_partial_materialization_before_consumer",
            "device_result_materialized_in_hot_window",
            "public_claim_authorized",
        ):
            if row.get(key) is not False:
                raise GraphValidationError(f"{partner} row must prove {key}=false")
        classification = row.get("transfer_counter_classification", {})
        if not isinstance(classification, Mapping):
            raise GraphValidationError(f"{partner} row requires transfer counter classification")
        if classification.get("hidden_copy_observed") is not False:
            raise GraphValidationError(f"{partner} hot window observed hidden copy")
        if classification.get("no_hidden_column_copy_ready") is not True:
            raise GraphValidationError(f"{partner} hot window no-hidden-copy readiness failed")

    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping):
        raise GraphValidationError("M19 payload requires comparison")
    for key in (
        "signature_match",
        "hot_no_hidden_column_copy_ready",
        "device_result_materialization_after_hot_window",
        "prepared_graph_reused_for_both_partners",
    ):
        if comparison.get(key) is not True:
            raise GraphValidationError(f"M19 comparison must prove {key}=true")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M19 payload requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
    ):
        if bool(boundary.get(key)):
            raise GraphValidationError(f"M19 must not authorize {key}")
    return {
        "status": V3_M19_RANKED_SUMMARY_BRIDGE_STATUS,
        "partner_count": len(rows),
        "signature_match": True,
        "hot_no_hidden_column_copy_ready": True,
        "public_claim_authorized": False,
    }


def validate_v3_m19_ranked_summary_bridge_chunk_plan(
    plan: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(plan, Mapping):
        raise GraphValidationError("M19 chunk plan must be a mapping")
    if plan.get("version") != V3_M19_CHUNK_PLAN_VERSION:
        raise GraphValidationError("unexpected M19 chunk plan version")
    query_count = int(plan.get("query_count", 0) or 0)
    max_query_count = int(plan.get("max_query_count", 0) or 0)
    chunks = tuple(plan.get("chunks", ()))
    if query_count <= 0:
        raise GraphValidationError("M19 chunk plan query_count must be positive")
    if max_query_count <= 0:
        raise GraphValidationError("M19 chunk plan max_query_count must be positive")
    if int(plan.get("chunk_count", -1)) != len(chunks):
        raise GraphValidationError("M19 chunk plan chunk_count does not match chunks")
    if bool(plan.get("aggregate_only_full_batch_direct_substitute_allowed")):
        raise GraphValidationError("M19 chunk plan must not allow aggregate-only substitute")
    if bool(plan.get("hidden_auto_dispatch_allowed")):
        raise GraphValidationError("M19 chunk plan must not allow hidden dispatch")
    if bool(plan.get("automatic_partner_selection_authorized")):
        raise GraphValidationError("M19 chunk plan must not authorize automatic partner selection")
    if bool(plan.get("public_speedup_claim_authorized")):
        raise GraphValidationError("M19 chunk plan must not authorize public speedup claims")

    expected_offset = 0
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, Mapping):
            raise GraphValidationError("M19 chunk plan chunk must be a mapping")
        chunk_count = int(chunk.get("query_count", 0))
        start = int(chunk.get("query_start_inclusive", -1))
        end = int(chunk.get("query_end_exclusive", -1))
        if int(chunk.get("chunk_index", -1)) != index:
            raise GraphValidationError("M19 chunk plan chunk_index mismatch")
        if start != expected_offset or int(chunk.get("query_offset", -1)) != expected_offset:
            raise GraphValidationError("M19 chunk plan query offsets are not contiguous")
        if chunk_count <= 0 or chunk_count > max_query_count:
            raise GraphValidationError("M19 chunk plan chunk query_count is invalid")
        if end - start != chunk_count:
            raise GraphValidationError("M19 chunk plan chunk end/start does not match query_count")
        for key in (
            "prepared_scene_reused",
            "prepared_query_points_per_chunk",
            "cuda_graph_per_chunk",
            "same_stream_partner_device_reduction_per_chunk",
        ):
            if chunk.get(key) is not True:
                raise GraphValidationError(f"M19 chunk plan must prove {key}=true")
        if chunk.get("host_materialization_before_partner") is not False:
            raise GraphValidationError("M19 chunk plan must block host materialization before partner")
        expected_offset = end
    if expected_offset != query_count:
        raise GraphValidationError("M19 chunk plan chunks do not cover query_count")
    return {
        "status": "accept",
        "version": plan.get("version"),
        "query_count": query_count,
        "chunk_count": len(chunks),
        "single_graph_cap_exceeded": bool(plan.get("single_graph_cap_exceeded")),
        "runtime_executed": bool(plan.get("runtime_executed")),
        "public_claim_authorized": False,
    }


def validate_v3_m19_ranked_summary_bridge_chunked_payload(
    payload: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("M19 chunked payload must be a mapping")
    if payload.get("version") != V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_VERSION:
        raise GraphValidationError("unexpected M19 chunked payload version")
    if payload.get("status") != V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_STATUS:
        raise GraphValidationError("unexpected M19 chunked payload status")
    plan = payload.get("execution_path_plan", {})
    plan_validation = validate_v3_m19_ranked_summary_bridge_chunk_plan(plan)
    if plan_validation["chunk_count"] <= 1:
        raise GraphValidationError("M19 chunked payload must contain more than one chunk")
    preparation = payload.get("preparation", {})
    if not isinstance(preparation, Mapping):
        raise GraphValidationError("M19 chunked payload requires preparation metadata")
    for key in (
        "prepared_scene_used",
        "prepared_scene_reused_across_chunks",
        "prepared_query_points_per_chunk",
        "cuda_graph_per_chunk",
        "initial_host_to_device_upload_expected",
    ):
        if preparation.get(key) is not True:
            raise GraphValidationError(f"M19 chunked preparation must prove {key}=true")

    rows = tuple(payload.get("partner_rows", ()))
    if {str(row.get("partner")) for row in rows if isinstance(row, Mapping)} != set(V3_M19_PARTNERS):
        raise GraphValidationError("M19 chunked payload requires CuPy and Numba partner rows")
    signatures = {tuple(tuple(item) for item in row.get("combined_validation_signature", ())) for row in rows}
    if len(signatures) != 1:
        raise GraphValidationError("M19 chunked CuPy and Numba combined signatures must match")
    for row in rows:
        if not isinstance(row, Mapping):
            raise GraphValidationError("M19 chunked partner row must be a mapping")
        partner = str(row.get("partner"))
        if int(row.get("chunk_count", 0) or 0) != int(plan_validation["chunk_count"]):
            raise GraphValidationError(f"{partner} chunked row chunk_count mismatch")
        for key in (
            "prepared_scene_reused_across_chunks",
            "prepared_query_points_per_chunk",
            "cuda_graph_per_chunk",
            "same_stream_partner_device_reduction_per_chunk",
            "device_resident_partial_rows_for_partner",
            "device_result_materialization_after_hot_window",
            "hot_no_hidden_column_copy_ready",
        ):
            if row.get(key) is not True:
                raise GraphValidationError(f"{partner} chunked row must prove {key}=true")
        for key in (
            "host_scalar_read_before_consumer",
            "host_partial_materialization_before_consumer",
            "device_result_materialized_in_hot_window",
            "public_claim_authorized",
        ):
            if row.get(key) is not False:
                raise GraphValidationError(f"{partner} chunked row must prove {key}=false")

    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping):
        raise GraphValidationError("M19 chunked payload requires comparison")
    for key in (
        "signature_match",
        "chunked_runtime_executed",
        "hot_no_hidden_column_copy_ready",
        "device_result_materialization_after_hot_window",
        "prepared_scene_reused_across_chunks",
        "cuda_graph_per_chunk",
    ):
        if comparison.get(key) is not True:
            raise GraphValidationError(f"M19 chunked comparison must prove {key}=true")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M19 chunked payload requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
    ):
        if bool(boundary.get(key)):
            raise GraphValidationError(f"M19 chunked must not authorize {key}")
    return {
        "status": V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_STATUS,
        "partner_count": len(rows),
        "chunk_count": int(plan_validation["chunk_count"]),
        "signature_match": True,
        "hot_no_hidden_column_copy_ready": True,
        "public_claim_authorized": False,
    }
