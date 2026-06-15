from __future__ import annotations

from collections.abc import Mapping
import statistics
import time
from pathlib import Path

from .optix_runtime import prepare_optix_static_triangle_scene_3d
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_m13_hit_stream_no_hidden_copy_evidence import make_v3_m13_hit_stream_rays
from .v3_0_m13_hit_stream_no_hidden_copy_evidence import make_v3_m13_two_plane_triangles
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import annotate_no_hidden_copy_metadata
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import summarize_no_hidden_copy_classifications
from .v3_0_no_hidden_copy_contract import validate_no_hidden_copy_payload


V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_VERSION = (
    "rtdl.v3_0.prepared_hit_stream_no_hidden_copy_evidence.m15"
)
V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_STATUS = (
    "m15_prepared_ray_batch_hit_stream_full_window_no_hidden_copy_internal_claims_gated"
)
V3_M15_GRAPH_ID = "prepared_ray_batch_hit_stream_full_window_no_hidden_copy_pilot"
V3_M15_CONTRACT_KEY = "prepared_ray_batch_hit_stream_no_hidden_copy_contract_v1"
V3_M15_PARTNERS = ("cupy",)
V3_M15_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)


def run_v3_m15_prepared_hit_stream_no_hidden_copy_evidence_case(
    *,
    transfer_counter_library: str | Path,
    ray_count: int = 8192,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
    capacity_multiplier: int = 2,
    deduplicate_primitives: bool = False,
) -> dict[str, object]:
    validate_v3_public_name(V3_M15_GRAPH_ID, label="M15 graph id")
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
    rays = make_v3_m13_hit_stream_rays(ray_count)
    capacity = ray_count * capacity_multiplier
    prepare_start = time.perf_counter()
    with prepare_optix_static_triangle_scene_3d(triangles) as scene:
        scene_prepare_seconds = time.perf_counter() - prepare_start
        ray_batch = scene.prepare_ray_batch(rays)
        buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(capacity)
        try:
            for _ in range(warmups):
                scene.ray_batch_triangle_hit_stream_same_stream_row_reduction_summary(
                    ray_batch,
                    buffers,
                    deduplicate_primitives=bool(deduplicate_primitives),
                )

            host_samples = []
            native_enqueue_samples = []
            consumer_samples = []
            snapshots = []
            classifications = []
            result_summaries = []
            result_metadata = []
            for _ in range(repeats):
                start = time.perf_counter()
                result = scene.ray_batch_triangle_hit_stream_same_stream_row_reduction_summary(
                    ray_batch,
                    buffers,
                    deduplicate_primitives=bool(deduplicate_primitives),
                    transfer_counter=transfer_counter,
                    transfer_counter_scope="producer_consumer",
                )
                host_samples.append(time.perf_counter() - start)
                summary = dict(result["summary"])
                metadata = dict(result["metadata"])
                timings = dict(metadata.get("phase_timing_seconds") or {})
                snapshot = dict(metadata["transfer_counter_snapshot"])
                classification = classify_no_hidden_copy_transfer_snapshot(
                    snapshot,
                    min_named_column_bytes=capacity * 8,
                    allowed_non_column_host_to_device_bytes=(
                        V3_M15_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
                    ),
                    measured_window=(
                        "prepared_ray_batch_native_producer_enqueue_to_same_stream_"
                        "hit_stream_row_reduction_before_summary_materialization"
                    ),
                    readiness_source="v3_m15_prepared_hit_stream_transfer_counter_classification",
                )
                native_enqueue_samples.append(float(timings.get("native_async_launch_enqueue", 0.0)))
                consumer_samples.append(
                    float(timings.get("same_stream_partner_row_reduction_consumer_and_materialization", 0.0))
                )
                snapshots.append(snapshot)
                classifications.append(classification)
                result_summaries.append(summary)
                result_metadata.append(metadata)
        finally:
            buffers.close()
            ray_batch.close()

    if not result_summaries:
        raise GraphValidationError("M15 prepared hit-stream run produced no samples")
    signature = _hit_stream_signature(result_summaries[-1])
    if any(_hit_stream_signature(summary) != signature for summary in result_summaries):
        raise GraphValidationError("M15 prepared hit-stream signatures changed across repeats")
    all_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in classifications)
    final_metadata = result_metadata[-1]
    same_stream_evidence = {
        "evidence_source": "prepared_ray_batch_cupy_rawkernel_same_stream_hit_stream_row_reduction",
        "event_pair_scope": (
            "prepared_ray_batch_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization"
        ),
        "producer_consumer_stream_ordering": final_metadata.get("producer_consumer_stream_ordering"),
        "stream_synchronization_proven": bool(final_metadata.get("stream_synchronization_proven")),
        "event_or_same_stream_ordering_proven": bool(final_metadata.get("event_or_same_stream_ordering_proven")),
        "native_symbol": final_metadata.get("native_symbol"),
        "release_symbol": final_metadata.get("release_symbol"),
        "prepared_ray_batch_used": bool(final_metadata.get("prepared_ray_batch_used")),
        "prepared_ray_batch_seconds": float(final_metadata.get("prepared_ray_batch_seconds", 0.0) or 0.0),
        "prepared_ray_batch_transfer_metadata": final_metadata.get("prepared_ray_batch_transfer_metadata"),
        "query_rays_uploaded_each_run": bool(final_metadata.get("query_rays_uploaded_each_run")),
        "prepared_rays_resident_on_device": bool(final_metadata.get("prepared_rays_resident_on_device")),
        "producer_input_upload_mode": final_metadata.get("producer_input_upload_mode"),
        "transfer_counter_observed": True,
        "transfer_counter_snapshot": snapshots[-1],
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
        {"same_stream_evidence": same_stream_evidence, "hit_stream_metadata": final_metadata},
        classifications[-1],
        all_samples_ready=all_ready,
        readiness_source="v3_m15_prepared_hit_stream_transfer_counter_classification",
    )
    row = {
        "partner": "cupy",
        "backend": "optix",
        "host_samples_seconds": tuple(host_samples),
        "native_enqueue_seconds_median": statistics.median(native_enqueue_samples),
        "consumer_and_summary_seconds_median": statistics.median(consumer_samples),
        "total_host_seconds_median": statistics.median(host_samples),
        "validation_signature": signature,
        "ray_count": ray_count,
        "triangle_count": len(triangles),
        "capacity": capacity,
        "metadata": metadata,
        "transfer_counter_samples": tuple(snapshots),
        "transfer_counter_classifications": tuple(classifications),
        "transfer_counter_classification": classifications[-1],
        "transfer_counter_summary": summarize_no_hidden_copy_classifications(tuple(classifications)),
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "prepared_ray_batch_used": True,
        "query_rays_uploaded_each_run": False,
        "no_hidden_column_copy_ready": all_ready,
        "true_zero_copy_ready": all_ready,
        "claim_readiness": {
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "prepared_ray_batch_used": True,
            "query_rays_uploaded_each_run": False,
            "no_hidden_column_copy_ready": all_ready,
            "true_zero_copy_ready": all_ready,
            "public_claim_authorized": False,
        },
        "public_claim_authorized": False,
    }
    payload = {
        "version": V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        "status": V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        "graph_id": V3_M15_GRAPH_ID,
        "contract_key": V3_M15_CONTRACT_KEY,
        "parameters": {
            "ray_count": ray_count,
            "triangle_count": len(triangles),
            "capacity": capacity,
            "capacity_multiplier": capacity_multiplier,
            "deduplicate_primitives": bool(deduplicate_primitives),
            "warmups": warmups,
            "repeats": repeats,
            "allowed_non_column_host_to_device_bytes": (
                V3_M15_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
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
            "prepared_ray_batch_used": bool(row["prepared_ray_batch_used"]),
            "query_rays_uploaded_each_run": bool(row["query_rays_uploaded_each_run"]),
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
                "M15 uses a prepared device-resident ray batch so query rays are not uploaded "
                "inside the measured producer+partner window. The M12 classifier therefore "
                "applies to the full prepared-ray producer enqueue through same-stream CuPy "
                "row-reduction window, excluding final scalar summary materialization."
            ),
        },
    }
    validate_v3_m15_prepared_hit_stream_no_hidden_copy_payload(payload)
    return payload


def validate_v3_m15_prepared_hit_stream_no_hidden_copy_payload(
    payload: Mapping[str, object],
) -> dict[str, object]:
    validation = validate_no_hidden_copy_payload(
        payload,
        expected_version=V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        expected_status=V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        required_partners=V3_M15_PARTNERS,
        require_signature_match=True,
    )
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 1:
        raise GraphValidationError("M15 prepared hit-stream payload requires one CuPy partner row")
    row = rows[0]
    if int(row.get("ray_count", 0) or 0) <= 0:
        raise GraphValidationError("M15 prepared hit-stream row requires a positive ray_count")
    if row.get("prepared_ray_batch_used") is not True:
        raise GraphValidationError("M15 row must use a prepared ray batch")
    if row.get("query_rays_uploaded_each_run") is not False:
        raise GraphValidationError("M15 row must not upload query rays each run")
    signature = tuple(row.get("validation_signature", ()))
    if len(signature) != 8:
        raise GraphValidationError("M15 prepared hit-stream signature must include row and reduction fields")
    metadata = row.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise GraphValidationError("M15 prepared hit-stream row requires metadata")
    same_stream = metadata.get("same_stream_evidence", {})
    if not isinstance(same_stream, Mapping):
        raise GraphValidationError("M15 prepared hit-stream row requires same-stream evidence")
    if same_stream.get("event_pair_scope") != (
        "prepared_ray_batch_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization"
    ):
        raise GraphValidationError("M15 measured window scope is wrong")
    if same_stream.get("query_rays_uploaded_each_run") is not False:
        raise GraphValidationError("M15 evidence must show no per-run query-ray upload")
    if same_stream.get("prepared_rays_resident_on_device") is not True:
        raise GraphValidationError("M15 evidence must show prepared rays are device-resident")
    validation["status"] = V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_STATUS
    validation["prepared_ray_batch_used"] = True
    validation["query_rays_uploaded_each_run"] = False
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
