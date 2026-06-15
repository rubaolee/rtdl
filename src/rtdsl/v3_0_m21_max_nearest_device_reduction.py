from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import statistics
import time

from .optix_runtime import prepare_optix_point_group_nearest_witness_2d
from .partner_adapters import global_argmax_u32_f64_partner_columns
from .reference import Point
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import summarize_no_hidden_copy_classifications


V3_M21_MAX_NEAREST_DEVICE_REDUCTION_VERSION = "rtdl.v3_0.max_nearest_device_reduction.m21"
V3_M21_MAX_NEAREST_DEVICE_REDUCTION_STATUS = (
    "m21_point_group_nearest_device_query_partner_reduction_internal_claims_gated"
)
V3_M21_GRAPH_ID = "prepared_point_group_nearest_device_query_partner_reduction"
V3_M21_CONTRACT_KEY = "prepared_point_group_nearest_device_query_columns_global_max_partner_v1"
V3_M21_PARTNERS = ("cupy", "numba")
V3_M21_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)
V3_M21_INVALID_U32 = 0xFFFFFFFF


def run_v3_m21_max_nearest_device_reduction_case(
    *,
    transfer_counter_library: str | Path,
    point_count: int = 65_536,
    group_axis: int = 64,
    radius: float = 0.025,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
) -> dict[str, object]:
    validate_v3_public_name(V3_M21_GRAPH_ID, label="M21 graph id")
    point_count = int(point_count)
    group_axis = int(group_axis)
    radius = float(radius)
    warmups = int(warmups)
    repeats = int(repeats)
    if point_count <= 0:
        raise GraphValidationError("point_count must be positive")
    if group_axis <= 0:
        raise GraphValidationError("group_axis must be positive")
    if radius <= 0.0:
        raise GraphValidationError("radius must be positive")
    if warmups < 0 or repeats <= 0:
        raise GraphValidationError("warmups/repeats are invalid")

    try:
        import cupy as cp
    except Exception as exc:
        raise RuntimeError("M21 max-nearest device reduction requires CuPy") from exc

    transfer_counter = CudaTransferCounter(transfer_counter_library)
    search_points, groups, query_points = make_v3_m21_max_nearest_points(
        point_count,
        group_axis=group_axis,
        radius=radius,
    )

    transfer_counter.reset()
    transfer_counter.enable()
    prepare_start = time.perf_counter()
    try:
        scene = prepare_optix_point_group_nearest_witness_2d(
            search_points,
            groups,
            max_radius=radius,
        )
        query_columns = _make_cupy_query_columns(cp, query_points)
        output_columns = {
            partner: {
                "query_ids": cp.empty((point_count,), dtype=cp.uint32),
                "neighbor_ids": cp.empty((point_count,), dtype=cp.uint32),
                "distances": cp.empty((point_count,), dtype=cp.float64),
            }
            for partner in V3_M21_PARTNERS
        }
        cp.cuda.runtime.deviceSynchronize()
        prepare_seconds = time.perf_counter() - prepare_start
        prepare_snapshot = transfer_counter.disable_and_snapshot()
    except Exception:
        transfer_counter.disable_and_snapshot()
        raise

    try:
        rows = []
        for partner in V3_M21_PARTNERS:
            rows.append(
                _run_partner_row(
                    scene=scene,
                    query_columns=query_columns,
                    output_columns=output_columns[partner],
                    partner=partner,
                    radius=radius,
                    transfer_counter=transfer_counter,
                    warmups=warmups,
                    repeats=repeats,
                )
            )
    finally:
        scene.close()

    signatures = {tuple(row["validation_signature"]) for row in rows}
    payload = {
        "version": V3_M21_MAX_NEAREST_DEVICE_REDUCTION_VERSION,
        "status": V3_M21_MAX_NEAREST_DEVICE_REDUCTION_STATUS,
        "graph_id": V3_M21_GRAPH_ID,
        "contract_key": V3_M21_CONTRACT_KEY,
        "parameters": {
            "point_count": point_count,
            "query_count": point_count,
            "group_count": len(groups),
            "group_axis": group_axis,
            "radius": radius,
            "warmups": warmups,
            "repeats": repeats,
            "partners": V3_M21_PARTNERS,
            "allowed_non_column_host_to_device_bytes": V3_M21_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            "transfer_counter_library": str(transfer_counter_library),
            "hardware": hardware,
        },
        "preparation": {
            "prepared_scene_used": True,
            "prepared_query_columns_used": True,
            "prepared_output_columns_used": True,
            "initial_host_to_device_upload_expected": True,
            "prepare_seconds": prepare_seconds,
            "prepare_transfer_counter_snapshot": prepare_snapshot,
            "prepare_window_claim_boundary": (
                "The M21 prepare window intentionally includes initial search-point scene build "
                "and query-column upload. The hot window starts after query/output columns are "
                "device-resident."
            ),
        },
        "partner_rows": tuple(rows),
        "comparison": {
            "signature_match": len(signatures) == 1,
            "partners": V3_M21_PARTNERS,
            "device_query_columns_used": True,
            "device_output_columns_used": True,
            "hot_no_hidden_column_copy_ready": all(bool(row["hot_no_hidden_column_copy_ready"]) for row in rows),
            "device_result_materialization_after_hot_window": all(
                bool(row["device_result_materialization_after_hot_window"]) for row in rows
            ),
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "paper_or_author_parity_claim_authorized": False,
            "reason": (
                "M21 validates a generic prepared point-group nearest-witness device-query "
                "producer feeding CuPy and Numba device-side global-max reductions before "
                "materialization. It is bridge evidence, not a public speedup or whole-app claim."
            ),
        },
        "measurement_methodology_limits": {
            "transfer_counter_scope": (
                "LD_PRELOAD CUDA transfer counter observes CUDA copy calls made in this process "
                "during measured windows. It does not prove absence of copies through unobserved "
                "internal library paths, child processes, or non-CUDA DMA."
            ),
            "query_residency_scope": (
                "Query columns are CuPy CUDA arrays prepared before the hot window. Search scene "
                "construction is still native-owned and belongs to the prepare phase."
            ),
        },
    }
    validate_v3_m21_max_nearest_device_reduction_payload(payload)
    return payload


def make_v3_m21_max_nearest_points(
    point_count: int,
    *,
    group_axis: int = 64,
    radius: float = 0.025,
) -> tuple[tuple[Point, ...], tuple[dict[str, object], ...], tuple[Point, ...]]:
    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("M21 point generation requires numpy") from exc
    count = int(point_count)
    axis = int(group_axis)
    radius = float(radius)
    if count <= 0:
        raise GraphValidationError("point_count must be positive")
    if axis <= 0:
        raise GraphValidationError("group_axis must be positive")
    if radius <= 0.0:
        raise GraphValidationError("radius must be positive")

    rng = np.random.default_rng(4421)
    coords = rng.random((count, 2), dtype=np.float64)
    jitter_angle = rng.random(count, dtype=np.float64) * (2.0 * np.pi)
    jitter_radius = rng.random(count, dtype=np.float64) * (0.35 * radius)
    query_coords = np.clip(
        coords
        + np.stack((np.cos(jitter_angle), np.sin(jitter_angle)), axis=1) * jitter_radius[:, None],
        0.0,
        1.0,
    )

    cell_x = np.minimum((coords[:, 0] * axis).astype(np.int64), axis - 1)
    cell_y = np.minimum((coords[:, 1] * axis).astype(np.int64), axis - 1)
    cell_id = cell_y * axis + cell_x
    order = np.argsort(cell_id, kind="stable")
    sorted_coords = coords[order]
    sorted_cells = cell_id[order]
    sorted_ids = order.astype(np.uint32)

    search_points = tuple(
        Point(int(sorted_ids[index]), float(sorted_coords[index, 0]), float(sorted_coords[index, 1]))
        for index in range(count)
    )
    groups = []
    start = 0
    group_id = 0
    while start < count:
        end = start + 1
        while end < count and sorted_cells[end] == sorted_cells[start]:
            end += 1
        group_coords = sorted_coords[start:end]
        groups.append(
            {
                "id": group_id,
                "point_offset": start,
                "point_count": end - start,
                "min_x": float(group_coords[:, 0].min()),
                "min_y": float(group_coords[:, 1].min()),
                "max_x": float(group_coords[:, 0].max()),
                "max_y": float(group_coords[:, 1].max()),
            }
        )
        start = end
        group_id += 1

    query_points = tuple(
        Point(int(index), float(query_coords[index, 0]), float(query_coords[index, 1]))
        for index in range(count)
    )
    return search_points, tuple(groups), query_points


def validate_v3_m21_max_nearest_device_reduction_payload(payload: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("M21 payload must be a mapping")
    if payload.get("version") != V3_M21_MAX_NEAREST_DEVICE_REDUCTION_VERSION:
        raise GraphValidationError("unexpected M21 payload version")
    if payload.get("status") != V3_M21_MAX_NEAREST_DEVICE_REDUCTION_STATUS:
        raise GraphValidationError("unexpected M21 payload status")
    validate_v3_public_name(str(payload.get("graph_id", "")), label="M21 graph id")
    preparation = payload.get("preparation", {})
    if not isinstance(preparation, Mapping):
        raise GraphValidationError("M21 payload requires preparation metadata")
    for key in ("prepared_scene_used", "prepared_query_columns_used", "prepared_output_columns_used"):
        if preparation.get(key) is not True:
            raise GraphValidationError(f"M21 preparation must prove {key}=true")
    if preparation.get("initial_host_to_device_upload_expected") is not True:
        raise GraphValidationError("M21 prepare window must explicitly mark initial upload as expected")

    rows = tuple(payload.get("partner_rows", ()))
    if {str(row.get("partner")) for row in rows if isinstance(row, Mapping)} != set(V3_M21_PARTNERS):
        raise GraphValidationError("M21 payload requires CuPy and Numba partner rows")
    signatures = {tuple(row.get("validation_signature", ())) for row in rows if isinstance(row, Mapping)}
    if len(signatures) != 1:
        raise GraphValidationError("M21 CuPy and Numba signatures must match")
    for row in rows:
        if not isinstance(row, Mapping):
            raise GraphValidationError("M21 partner row must be a mapping")
        partner = str(row.get("partner"))
        for key in (
            "prepared_scene_used",
            "prepared_query_columns_used",
            "prepared_output_columns_used",
            "device_query_columns_used",
            "device_output_columns_used",
            "same_stream_or_default_stream_ordering_used",
            "device_result_materialization_after_hot_window",
            "hot_transfer_counter_observed",
            "hot_no_hidden_column_copy_ready",
        ):
            if row.get(key) is not True:
                raise GraphValidationError(f"{partner} row must prove {key}=true")
        for key in (
            "host_query_upload_in_hot_window",
            "host_row_materialization_before_consumer",
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
        raise GraphValidationError("M21 payload requires comparison")
    for key in (
        "signature_match",
        "device_query_columns_used",
        "device_output_columns_used",
        "hot_no_hidden_column_copy_ready",
        "device_result_materialization_after_hot_window",
    ):
        if comparison.get(key) is not True:
            raise GraphValidationError(f"M21 comparison must prove {key}=true")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M21 payload requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
        "paper_or_author_parity_claim_authorized",
    ):
        if bool(boundary.get(key)):
            raise GraphValidationError(f"M21 must not authorize {key}")
    return {
        "status": V3_M21_MAX_NEAREST_DEVICE_REDUCTION_STATUS,
        "partner_count": len(rows),
        "signature_match": True,
        "hot_no_hidden_column_copy_ready": True,
        "public_claim_authorized": False,
    }


def _make_cupy_query_columns(cp, query_points: tuple[Point, ...]) -> dict[str, object]:
    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("M21 query column preparation requires numpy") from exc
    ids = np.asarray([int(point.id) for point in query_points], dtype=np.uint32)
    xs = np.asarray([float(point.x) for point in query_points], dtype=np.float64)
    ys = np.asarray([float(point.y) for point in query_points], dtype=np.float64)
    return {
        "ids": cp.asarray(ids, dtype=cp.uint32),
        "x": cp.asarray(xs, dtype=cp.float64),
        "y": cp.asarray(ys, dtype=cp.float64),
    }


def _run_partner_row(
    *,
    scene,
    query_columns: dict[str, object],
    output_columns: dict[str, object],
    partner: str,
    radius: float,
    transfer_counter: CudaTransferCounter,
    warmups: int,
    repeats: int,
) -> dict[str, object]:
    if partner not in V3_M21_PARTNERS:
        raise GraphValidationError(f"unsupported M21 partner: {partner}")
    for _ in range(warmups):
        device_result = _run_partner_device_result(
            scene=scene,
            query_columns=query_columns,
            output_columns=output_columns,
            partner=partner,
            radius=radius,
        )
        device_result.materialize()

    hot_samples = []
    materialize_samples = []
    hot_snapshots = []
    hot_classifications = []
    signatures = []
    metadata_rows = []
    materialize_rows = []
    for _ in range(repeats):
        transfer_counter.reset()
        transfer_counter.enable()
        hot_start = time.perf_counter()
        try:
            device_result = _run_partner_device_result(
                scene=scene,
                query_columns=query_columns,
                output_columns=output_columns,
                partner=partner,
                radius=radius,
            )
            hot_samples.append(time.perf_counter() - hot_start)
            hot_snapshot = transfer_counter.disable_and_snapshot()
        except Exception:
            transfer_counter.disable_and_snapshot()
            raise

        materialize_start = time.perf_counter()
        materialized = device_result.materialize()
        materialize_samples.append(time.perf_counter() - materialize_start)
        metadata = dict(device_result.metadata)
        classification = classify_no_hidden_copy_transfer_snapshot(
            hot_snapshot,
            min_named_column_bytes=_m21_min_named_column_bytes(metadata),
            allowed_non_column_host_to_device_bytes=V3_M21_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            measured_window=(
                "prepared_point_group_nearest_device_query_columns_to_partner_global_max_before_materialization"
            ),
            readiness_source="v3_m21_max_nearest_hot_transfer_counter_classification",
        )
        signature = _m21_signature(materialized)
        signatures.append(signature)
        hot_snapshots.append(hot_snapshot)
        hot_classifications.append(classification)
        metadata_rows.append(metadata)
        materialize_rows.append(dict(materialized["metadata"]))

    if any(signature != signatures[-1] for signature in signatures):
        raise GraphValidationError(f"M21 {partner} signatures changed across repeats")
    hot_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in hot_classifications)
    final_metadata = metadata_rows[-1]
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_point_group_nearest_device_query_columns_partner_global_max",
        "prepared_scene_used": True,
        "prepared_query_columns_used": True,
        "prepared_output_columns_used": True,
        "device_query_columns_used": True,
        "device_output_columns_used": True,
        "same_stream_or_default_stream_ordering_used": True,
        "host_query_upload_in_hot_window": False,
        "host_row_materialization_before_consumer": False,
        "device_result_materialized_in_hot_window": False,
        "device_result_materialization_after_hot_window": True,
        "consumer_host_valid_count_check_used": bool(final_metadata.get("consumer_host_valid_count_check_used")),
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
            "materialization_metadata": materialize_rows[-1],
        },
        "public_claim_authorized": False,
        "claim_readiness": {
            "prepared_scene_query_and_output_columns_before_hot_window": True,
            "no_host_query_upload_in_hot_window": True,
            "no_host_row_materialization_before_partner": True,
            "no_hidden_column_copy_ready": hot_ready,
            "measured_window_scope_only": True,
            "public_claim_authorized": False,
        },
    }


def _run_partner_device_result(
    *,
    scene,
    query_columns: dict[str, object],
    output_columns: dict[str, object],
    partner: str,
    radius: float,
) -> "_V3M21DeviceResult":
    try:
        import cupy as cp
    except Exception as exc:
        raise RuntimeError("M21 partner device result requires CuPy") from exc
    producer = scene.write_device_nearest_witness_columns_from_device_query_columns(
        query_columns,
        radius=radius,
        query_ids_out=output_columns["query_ids"],
        neighbor_ids_out=output_columns["neighbor_ids"],
        distances_out=output_columns["distances"],
    )
    consumer_item_ids = cp.where(
        output_columns["neighbor_ids"] != cp.uint32(V3_M21_INVALID_U32),
        output_columns["query_ids"],
        cp.uint32(V3_M21_INVALID_U32),
    ).astype(cp.uint32, copy=False)
    if partner == "cupy":
        consumer = _run_cupy_global_argmax_device(
            cp,
            consumer_item_ids,
            output_columns["neighbor_ids"],
            output_columns["distances"],
        )
    elif partner == "numba":
        consumer = global_argmax_u32_f64_partner_columns(
            {"item_ids": consumer_item_ids, "scores": output_columns["distances"]},
            partner="numba",
            validate_non_empty_on_host=False,
            return_metadata=True,
        )
    else:
        raise GraphValidationError(f"unsupported M21 partner: {partner}")
    cp.cuda.runtime.deviceSynchronize()
    return _V3M21DeviceResult(
        partner=partner,
        query_ids=output_columns["query_ids"],
        neighbor_ids=output_columns["neighbor_ids"],
        distances=output_columns["distances"],
        consumer=consumer,
        metadata={
            "producer_metadata": dict(producer["metadata"]),
            "consumer_metadata": dict(consumer["metadata"]),
            "consumer_host_valid_count_check_used": bool(
                consumer["metadata"].get("host_valid_count_check_used")
            ),
            "device_query_columns_used": True,
            "device_output_columns_used": True,
            "host_query_upload_in_hot_window": False,
            "host_row_materialization_before_consumer": False,
            "device_result_materialized_in_hot_window": False,
            "hot_device_synchronized_before_timer_stop": True,
        },
    )


def _run_cupy_global_argmax_device(cp, item_ids, neighbor_ids, scores) -> dict[str, object]:
    valid = (item_ids != cp.uint32(V3_M21_INVALID_U32)) & cp.isfinite(scores)
    safe_scores = cp.where(valid, scores, cp.asarray(-float("inf"), dtype=cp.float64))
    best_score = cp.max(safe_scores)
    candidate = valid & (scores == best_score)
    item_ids_u64 = item_ids.astype(cp.uint64, copy=False)
    max_u64 = cp.asarray(0xFFFFFFFFFFFFFFFF, dtype=cp.uint64)
    best_item = cp.min(cp.where(candidate, item_ids_u64, max_u64))
    row_indices = cp.arange(item_ids.shape[0], dtype=cp.int64)
    max_i64 = cp.asarray(0x7FFFFFFFFFFFFFFF, dtype=cp.int64)
    best_row = cp.min(cp.where(candidate & (item_ids_u64 == best_item), row_indices, max_i64))
    selected_neighbor = neighbor_ids[best_row].reshape((1,))
    return {
        "columns": {
            "item_ids": best_item.astype(cp.uint32, copy=False).reshape((1,)),
            "scores": best_score.reshape((1,)),
            "row_indices": best_row.reshape((1,)),
            "neighbor_ids": selected_neighbor,
            "valid_count": cp.sum(valid).astype(cp.int64, copy=False).reshape((1,)),
        },
        "metadata": {
            "adapter": "v3_m21_cupy_global_argmax_device",
            "partner": "cupy",
            "operation": "global_argmax_u32_f64",
            "contract": "generic_global_argmax_u32_f64",
            "tie_break": "highest_score_then_lowest_item_id_then_lowest_row_index",
            "reduction_strategy": "cupy_vectorized_device_reduction",
            "host_valid_count_check_used": False,
            "host_row_materialization_used": False,
            "direct_device_handoff_authorized": True,
            "true_zero_copy_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
    }


class _V3M21DeviceResult:
    def __init__(
        self,
        *,
        partner: str,
        query_ids,
        neighbor_ids,
        distances,
        consumer: Mapping[str, object],
        metadata: Mapping[str, object],
    ):
        self.partner = str(partner)
        self.query_ids = query_ids
        self.neighbor_ids = neighbor_ids
        self.distances = distances
        self.consumer = dict(consumer)
        self.metadata = dict(metadata)

    def materialize(self) -> dict[str, object]:
        started = time.perf_counter()
        columns = self.consumer["columns"]
        if self.partner == "cupy":
            try:
                import cupy as cp
            except Exception as exc:
                raise RuntimeError("CuPy materialization requires cupy") from exc
            query_id = int(cp.asnumpy(columns["item_ids"])[0])
            row_index = int(cp.asnumpy(columns["row_indices"])[0])
            distance = float(cp.asnumpy(columns["scores"])[0])
            neighbor_id = int(cp.asnumpy(columns["neighbor_ids"])[0])
            valid_count = int(cp.asnumpy(columns["valid_count"])[0])
        elif self.partner == "numba":
            try:
                import cupy as cp
            except Exception as exc:
                raise RuntimeError("Numba M21 materialization requires CuPy for producer columns") from exc
            query_id = int(columns["item_ids"].copy_to_host()[0])
            row_index = int(columns["row_indices"].copy_to_host()[0])
            distance = float(columns["scores"].copy_to_host()[0])
            valid_count = int(columns["valid_count"].copy_to_host()[0])
            neighbor_id = int(cp.asnumpy(self.neighbor_ids[row_index : row_index + 1])[0])
        else:
            raise RuntimeError(f"unsupported M21 materialization partner: {self.partner}")
        materialize_seconds = time.perf_counter() - started
        metadata = dict(self.metadata)
        metadata.update(
            {
                "result_materialized": True,
                "result_materialization_after_device_window": True,
                "result_materialization_seconds": materialize_seconds,
            }
        )
        return {
            "result": {
                "query_id": query_id,
                "neighbor_id": neighbor_id,
                "row_index": row_index,
                "distance": distance,
                "valid_count": valid_count,
            },
            "metadata": metadata,
        }


def _m21_signature(materialized: Mapping[str, object]) -> tuple[int, int, int, int, int]:
    row = materialized["result"]
    return (
        int(row["query_id"]),
        int(row["neighbor_id"]),
        int(row["row_index"]),
        int(round(float(row["distance"]) * 1_000_000_000.0)),
        int(row["valid_count"]),
    )


def _m21_min_named_column_bytes(metadata: Mapping[str, object]) -> int:
    producer = metadata.get("producer_metadata", {})
    query_count = int(producer.get("query_count", 0) if isinstance(producer, Mapping) else 0)
    return max(query_count * (4 + 4 + 8), 1)
