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
V3_M19_RANKED_SUMMARY_BRIDGE_STATUS = (
    "m19_ranked_summary_prepared_graph_partner_bridge_internal_claims_gated"
)
V3_M19_GRAPH_ID = "prepared_ranked_summary_graph_partner_bridge"
V3_M19_CONTRACT_KEY = "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner_v1"
V3_M19_PARTNERS = ("cupy", "numba")
V3_M19_DISTRIBUTIONS = ("uniform", "clustered", "shell")
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
    if query_count > 65_536:
        raise GraphValidationError("query_count must be <= 65536 for the current prepared graph path")
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
