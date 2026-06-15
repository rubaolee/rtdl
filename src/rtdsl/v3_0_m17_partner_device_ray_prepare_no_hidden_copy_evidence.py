from __future__ import annotations

from collections.abc import Mapping
import statistics
import time
from pathlib import Path

from .optix_runtime import prepare_optix_static_triangle_scene_3d
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_m13_hit_stream_no_hidden_copy_evidence import make_v3_m13_two_plane_triangles
from .v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence import make_v3_m16_cupy_ray_columns
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import annotate_no_hidden_copy_metadata
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import summarize_no_hidden_copy_classifications
from .v3_0_no_hidden_copy_contract import validate_no_hidden_copy_payload


V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_VERSION = (
    "rtdl.v3_0.partner_device_ray_prepare_no_hidden_copy_evidence.m17"
)
V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_STATUS = (
    "m17_partner_device_ray_prepare_and_hot_path_no_hidden_copy_internal_claims_gated"
)
V3_M17_GRAPH_ID = "partner_device_ray_prepare_and_hit_stream_no_hidden_copy_pilot"
V3_M17_CONTRACT_KEY = "partner_device_ray_prepare_no_hidden_copy_contract_v1"
V3_M17_PARTNERS = ("cupy",)
V3_M17_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)


def run_v3_m17_partner_device_ray_prepare_no_hidden_copy_evidence_case(
    *,
    transfer_counter_library: str | Path,
    ray_count: int = 8192,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
    capacity_multiplier: int = 2,
    deduplicate_primitives: bool = False,
) -> dict[str, object]:
    validate_v3_public_name(V3_M17_GRAPH_ID, label="M17 graph id")
    ray_count = int(ray_count)
    warmups = int(warmups)
    repeats = int(repeats)
    capacity_multiplier = int(capacity_multiplier)
    if ray_count <= 0:
        raise GraphValidationError("ray_count must be positive")
    if warmups < 0 or repeats <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    if capacity_multiplier < 2:
        raise GraphValidationError("capacity_multiplier must leave room for two hits per ray")

    transfer_counter = CudaTransferCounter(transfer_counter_library)
    triangles = make_v3_m13_two_plane_triangles()
    ray_columns = make_v3_m16_cupy_ray_columns(ray_count)
    capacity = ray_count * capacity_multiplier
    scene_prepare_start = time.perf_counter()
    with prepare_optix_static_triangle_scene_3d(triangles) as scene:
        scene_prepare_seconds = time.perf_counter() - scene_prepare_start
        buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(capacity)
        try:
            for _ in range(warmups):
                ray_batch = scene.prepare_ray_batch_device_columns(ray_columns)
                try:
                    scene.ray_batch_triangle_hit_stream_same_stream_row_reduction_summary(
                        ray_batch,
                        buffers,
                        deduplicate_primitives=bool(deduplicate_primitives),
                    )
                finally:
                    ray_batch.close()

            prepare_samples = []
            prepare_snapshots = []
            prepare_classifications = []
            hot_host_samples = []
            native_enqueue_samples = []
            consumer_samples = []
            hot_snapshots = []
            hot_classifications = []
            result_summaries = []
            result_metadata = []
            for _ in range(repeats):
                transfer_counter.reset()
                transfer_counter.enable()
                prepare_start = time.perf_counter()
                ray_batch = scene.prepare_ray_batch_device_columns(ray_columns)
                prepare_samples.append(time.perf_counter() - prepare_start)
                prepare_snapshot = transfer_counter.disable_and_snapshot()
                prepare_classification = classify_no_hidden_copy_transfer_snapshot(
                    prepare_snapshot,
                    min_named_column_bytes=ray_count * 4,
                    allowed_non_column_host_to_device_bytes=(
                        V3_M17_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
                    ),
                    measured_window=(
                        "partner_device_ray_batch_prepare_from_device_columns_before_hot_path"
                    ),
                    readiness_source="v3_m17_partner_device_ray_prepare_transfer_counter_classification",
                )
                prepare_snapshots.append(prepare_snapshot)
                prepare_classifications.append(prepare_classification)
                try:
                    hot_start = time.perf_counter()
                    result = scene.ray_batch_triangle_hit_stream_same_stream_row_reduction_summary(
                        ray_batch,
                        buffers,
                        deduplicate_primitives=bool(deduplicate_primitives),
                        transfer_counter=transfer_counter,
                        transfer_counter_scope="producer_consumer",
                    )
                    hot_host_samples.append(time.perf_counter() - hot_start)
                finally:
                    ray_batch.close()
                summary = dict(result["summary"])
                metadata = dict(result["metadata"])
                timings = dict(metadata.get("phase_timing_seconds") or {})
                hot_snapshot = dict(metadata["transfer_counter_snapshot"])
                hot_classification = classify_no_hidden_copy_transfer_snapshot(
                    hot_snapshot,
                    min_named_column_bytes=capacity * 8,
                    allowed_non_column_host_to_device_bytes=(
                        V3_M17_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
                    ),
                    measured_window=(
                        "partner_device_ray_prepare_native_producer_enqueue_to_same_stream_"
                        "hit_stream_row_reduction_before_summary_materialization"
                    ),
                    readiness_source="v3_m17_partner_device_ray_hot_path_transfer_counter_classification",
                )
                native_enqueue_samples.append(float(timings.get("native_async_launch_enqueue", 0.0)))
                consumer_samples.append(
                    float(timings.get("same_stream_partner_row_reduction_consumer_and_materialization", 0.0))
                )
                hot_snapshots.append(hot_snapshot)
                hot_classifications.append(hot_classification)
                result_summaries.append(summary)
                result_metadata.append(metadata)
        finally:
            buffers.close()

    if not result_summaries:
        raise GraphValidationError("M17 partner-device-ray prepare run produced no samples")
    signature = _hit_stream_signature(result_summaries[-1])
    if any(_hit_stream_signature(summary) != signature for summary in result_summaries):
        raise GraphValidationError("M17 partner-device-ray signatures changed across repeats")
    prepare_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in prepare_classifications)
    hot_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in hot_classifications)
    all_ready = prepare_ready and hot_ready
    final_metadata = result_metadata[-1]
    prepared_transfer_metadata = dict(final_metadata.get("prepared_ray_batch_transfer_metadata") or {})
    prepare_evidence = {
        "evidence_source": "partner_owned_cupy_device_ray_columns_to_rtdl_prepared_device_ray_batch",
        "event_pair_scope": "partner_device_ray_batch_prepare_from_device_columns_before_hot_path",
        "ray_columns_partner_owned": bool(prepared_transfer_metadata.get("ray_columns_partner_owned")),
        "ray_batch_created_from": prepared_transfer_metadata.get("ray_batch_created_from"),
        "source_protocols": tuple(prepared_transfer_metadata.get("source_protocols", ())),
        "source_devices": tuple(prepared_transfer_metadata.get("source_devices", ())),
        "ray_id_host_bookkeeping_downloaded": bool(
            prepared_transfer_metadata.get("ray_id_host_bookkeeping_downloaded")
        ),
        "host_ray_ids_available": bool(prepared_transfer_metadata.get("host_ray_ids_available")),
        "grouped_host_ray_id_contract_available": bool(
            prepared_transfer_metadata.get("grouped_host_ray_id_contract_available")
        ),
        "prepared_rays_resident_on_device": bool(final_metadata.get("prepared_rays_resident_on_device")),
        "transfer_counter_observed": True,
        "transfer_counter_snapshot": prepare_snapshots[-1],
        "no_hidden_column_copy_ready": prepare_ready,
        "true_zero_copy_ready": prepare_ready,
    }
    same_stream_evidence = {
        "evidence_source": "partner_device_ray_columns_to_prepared_ray_batch_cupy_same_stream_hit_stream_row_reduction",
        "event_pair_scope": (
            "partner_device_ray_prepare_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization"
        ),
        "producer_consumer_stream_ordering": final_metadata.get("producer_consumer_stream_ordering"),
        "stream_synchronization_proven": bool(final_metadata.get("stream_synchronization_proven")),
        "event_or_same_stream_ordering_proven": bool(final_metadata.get("event_or_same_stream_ordering_proven")),
        "native_symbol": final_metadata.get("native_symbol"),
        "release_symbol": final_metadata.get("release_symbol"),
        "prepared_ray_batch_used": bool(final_metadata.get("prepared_ray_batch_used")),
        "prepared_ray_batch_seconds": float(final_metadata.get("prepared_ray_batch_seconds", 0.0) or 0.0),
        "prepared_ray_batch_transfer_metadata": prepared_transfer_metadata,
        "ray_columns_partner_owned": bool(prepared_transfer_metadata.get("ray_columns_partner_owned")),
        "ray_batch_created_from": prepared_transfer_metadata.get("ray_batch_created_from"),
        "source_protocols": tuple(prepared_transfer_metadata.get("source_protocols", ())),
        "source_devices": tuple(prepared_transfer_metadata.get("source_devices", ())),
        "query_rays_uploaded_each_run": bool(final_metadata.get("query_rays_uploaded_each_run")),
        "prepared_rays_resident_on_device": bool(final_metadata.get("prepared_rays_resident_on_device")),
        "producer_input_upload_mode": final_metadata.get("producer_input_upload_mode"),
        "transfer_counter_observed": True,
        "transfer_counter_snapshot": hot_snapshots[-1],
        "validation_materialization_after_measured_window": True,
        "same_stream_ready": bool(final_metadata.get("event_or_same_stream_ordering_proven")),
        "native_synchronized_before_return": bool(final_metadata.get("producer_host_synchronization_used")),
        "host_row_materialization_before_consumer": bool(
            final_metadata.get("host_row_materialization_before_consumer")
        ),
        "host_scalar_read_before_consumer": bool(final_metadata.get("host_scalar_read_before_consumer")),
        "cuda_stream_ptr_nonzero": bool(final_metadata.get("cuda_stream_ptr_nonzero")),
    }
    metadata = annotate_no_hidden_copy_metadata(
        {
            "prepare_evidence": prepare_evidence,
            "same_stream_evidence": same_stream_evidence,
            "hit_stream_metadata": final_metadata,
        },
        hot_classifications[-1],
        all_samples_ready=all_ready,
        readiness_source="v3_m17_partner_device_ray_prepare_and_hot_path_transfer_counter_classification",
    )
    row = {
        "partner": "cupy",
        "backend": "optix",
        "prepare_samples_seconds": tuple(prepare_samples),
        "prepare_seconds_median": statistics.median(prepare_samples),
        "hot_host_samples_seconds": tuple(hot_host_samples),
        "native_enqueue_seconds_median": statistics.median(native_enqueue_samples),
        "consumer_and_summary_seconds_median": statistics.median(consumer_samples),
        "total_hot_host_seconds_median": statistics.median(hot_host_samples),
        "validation_signature": signature,
        "ray_count": ray_count,
        "triangle_count": len(triangles),
        "capacity": capacity,
        "metadata": metadata,
        "prepare_transfer_counter_samples": tuple(prepare_snapshots),
        "prepare_transfer_counter_classifications": tuple(prepare_classifications),
        "prepare_transfer_counter_classification": prepare_classifications[-1],
        "prepare_transfer_counter_summary": summarize_no_hidden_copy_classifications(tuple(prepare_classifications)),
        "transfer_counter_samples": tuple(hot_snapshots),
        "transfer_counter_classifications": tuple(hot_classifications),
        "transfer_counter_classification": hot_classifications[-1],
        "transfer_counter_summary": summarize_no_hidden_copy_classifications(tuple(hot_classifications)),
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "prepare_transfer_counter_observed": True,
        "prepared_ray_batch_used": True,
        "ray_columns_partner_owned": True,
        "ray_batch_created_from": "partner_device_columns",
        "ray_id_host_bookkeeping_downloaded": False,
        "host_ray_ids_available": False,
        "query_rays_uploaded_each_run": False,
        "prepare_no_hidden_column_copy_ready": prepare_ready,
        "hot_no_hidden_column_copy_ready": hot_ready,
        "no_hidden_column_copy_ready": all_ready,
        "true_zero_copy_ready": all_ready,
        "claim_readiness": {
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "prepare_transfer_counter_observed": True,
            "prepared_ray_batch_used": True,
            "ray_columns_partner_owned": True,
            "ray_id_host_bookkeeping_downloaded": False,
            "query_rays_uploaded_each_run": False,
            "no_hidden_column_copy_ready": all_ready,
            "true_zero_copy_ready": all_ready,
            "public_claim_authorized": False,
        },
        "public_claim_authorized": False,
    }
    payload = {
        "version": V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_VERSION,
        "status": V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_STATUS,
        "graph_id": V3_M17_GRAPH_ID,
        "contract_key": V3_M17_CONTRACT_KEY,
        "parameters": {
            "ray_count": ray_count,
            "triangle_count": len(triangles),
            "capacity": capacity,
            "capacity_multiplier": capacity_multiplier,
            "deduplicate_primitives": bool(deduplicate_primitives),
            "warmups": warmups,
            "repeats": repeats,
            "allowed_non_column_host_to_device_bytes": (
                V3_M17_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
            ),
            "transfer_counter_library": str(transfer_counter_library),
            "hardware": hardware,
            "scene_prepare_seconds": scene_prepare_seconds,
        },
        "partner_rows": (row,),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": bool(row["same_stream_ready"]),
            "transfer_counter_observed": bool(row["transfer_counter_observed"]),
            "prepare_transfer_counter_observed": bool(row["prepare_transfer_counter_observed"]),
            "prepared_ray_batch_used": bool(row["prepared_ray_batch_used"]),
            "ray_columns_partner_owned": bool(row["ray_columns_partner_owned"]),
            "ray_id_host_bookkeeping_downloaded": bool(row["ray_id_host_bookkeeping_downloaded"]),
            "query_rays_uploaded_each_run": bool(row["query_rays_uploaded_each_run"]),
            "prepare_no_hidden_column_copy_ready": bool(row["prepare_no_hidden_column_copy_ready"]),
            "hot_no_hidden_column_copy_ready": bool(row["hot_no_hidden_column_copy_ready"]),
            "no_hidden_column_copy_ready": bool(row["no_hidden_column_copy_ready"]),
            "true_zero_copy_ready": bool(row["true_zero_copy_ready"]),
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "reason": (
                "M17 removes the one-time device-to-host ray-id bookkeeping download from "
                "partner-device-ray preparation for the hit-stream-safe prepared ray batch "
                "contract, then revalidates the prepared hot path. The final scalar summary "
                "materialization remains outside the measured hot-path window."
            ),
        },
    }
    validate_v3_m17_partner_device_ray_prepare_no_hidden_copy_payload(payload)
    return payload


def validate_v3_m17_partner_device_ray_prepare_no_hidden_copy_payload(
    payload: Mapping[str, object],
) -> dict[str, object]:
    validation = validate_no_hidden_copy_payload(
        payload,
        expected_version=V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_VERSION,
        expected_status=V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_STATUS,
        required_partners=V3_M17_PARTNERS,
        require_signature_match=True,
    )
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 1:
        raise GraphValidationError("M17 partner-device-ray prepare payload requires one CuPy partner row")
    row = rows[0]
    if row.get("prepared_ray_batch_used") is not True:
        raise GraphValidationError("M17 row must use a prepared ray batch")
    if row.get("ray_columns_partner_owned") is not True:
        raise GraphValidationError("M17 row must start from partner-owned ray columns")
    if row.get("ray_batch_created_from") != "partner_device_columns":
        raise GraphValidationError("M17 row must create the ray batch from partner device columns")
    if row.get("ray_id_host_bookkeeping_downloaded") is not False:
        raise GraphValidationError("M17 row must not download ray IDs for host bookkeeping")
    if row.get("host_ray_ids_available") is not False:
        raise GraphValidationError("M17 row must use the device-only hit-stream ray batch contract")
    if row.get("query_rays_uploaded_each_run") is not False:
        raise GraphValidationError("M17 row must not upload query rays each run")
    if row.get("prepare_no_hidden_column_copy_ready") is not True:
        raise GraphValidationError("M17 prepare window must pass no-hidden-copy")
    if row.get("hot_no_hidden_column_copy_ready") is not True:
        raise GraphValidationError("M17 hot window must pass no-hidden-copy")
    prepare_classification = row.get("prepare_transfer_counter_classification", {})
    if not isinstance(prepare_classification, Mapping):
        raise GraphValidationError("M17 row requires prepare transfer-counter classification")
    if prepare_classification.get("measured_window") != (
        "partner_device_ray_batch_prepare_from_device_columns_before_hot_path"
    ):
        raise GraphValidationError("M17 prepare measured window scope is wrong")
    for key in (
        "observed_device_to_host_calls",
        "observed_device_to_device_calls",
        "observed_unknown_calls",
    ):
        if int(prepare_classification.get(key, 0) or 0) != 0:
            raise GraphValidationError(f"M17 prepare window observed disallowed transfer: {key}")
    metadata = row.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise GraphValidationError("M17 row requires metadata")
    prepare_evidence = metadata.get("prepare_evidence", {})
    if not isinstance(prepare_evidence, Mapping):
        raise GraphValidationError("M17 row requires prepare evidence")
    if prepare_evidence.get("ray_id_host_bookkeeping_downloaded") is not False:
        raise GraphValidationError("M17 prepare evidence must show no ray-id host bookkeeping download")
    same_stream = metadata.get("same_stream_evidence", {})
    if not isinstance(same_stream, Mapping):
        raise GraphValidationError("M17 row requires same-stream evidence")
    if same_stream.get("event_pair_scope") != (
        "partner_device_ray_prepare_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization"
    ):
        raise GraphValidationError("M17 hot measured window scope is wrong")
    if same_stream.get("query_rays_uploaded_each_run") is not False:
        raise GraphValidationError("M17 hot evidence must show no per-run query-ray upload")
    validation["status"] = V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_STATUS
    validation["prepared_ray_batch_used"] = True
    validation["ray_columns_partner_owned"] = True
    validation["ray_id_host_bookkeeping_downloaded"] = False
    validation["query_rays_uploaded_each_run"] = False
    validation["prepare_no_hidden_column_copy_ready"] = True
    validation["hot_no_hidden_column_copy_ready"] = True
    return validation


def _hit_stream_signature(summary: Mapping[str, object]) -> tuple[int, ...]:
    return (
        int(summary["row_count"]),
        int(summary["hit_event_count"]),
        int(summary["stored_row_count"]),
        int(summary["ray_id_sum_mod_u64"]),
        int(summary["primitive_id_sum_mod_u64"]),
        int(summary["ray_id_xor"]),
        -1 if summary["min_primitive_id"] is None else int(summary["min_primitive_id"]),
        -1 if summary["max_primitive_id"] is None else int(summary["max_primitive_id"]),
    )
