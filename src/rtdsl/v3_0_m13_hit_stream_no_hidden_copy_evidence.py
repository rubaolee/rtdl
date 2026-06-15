from __future__ import annotations

from collections.abc import Mapping
import statistics
import time
from pathlib import Path

from .optix_runtime import prepare_optix_static_triangle_scene_3d
from .reference import Ray3D
from .reference import Triangle3D
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import annotate_no_hidden_copy_metadata
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import summarize_no_hidden_copy_classifications
from .v3_0_no_hidden_copy_contract import validate_no_hidden_copy_payload


V3_M13_HIT_STREAM_NO_HIDDEN_COPY_VERSION = "rtdl.v3_0.hit_stream_no_hidden_copy_evidence.m13"
V3_M13_HIT_STREAM_NO_HIDDEN_COPY_STATUS = (
    "m13_hit_stream_row_reduction_second_workload_no_hidden_copy_internal_claims_gated"
)
V3_M13_GRAPH_ID = "ray_triangle_hit_stream_row_reduction_no_hidden_copy_pilot"
V3_M13_CONTRACT_KEY = "ray_triangle_hit_stream_row_reduction_no_hidden_copy_contract_v1"
V3_M13_PARTNERS = ("cupy",)
V3_M13_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)


def run_v3_m13_hit_stream_no_hidden_copy_evidence_case(
    *,
    transfer_counter_library: str | Path,
    ray_count: int = 8192,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
    capacity_multiplier: int = 2,
) -> dict[str, object]:
    validate_v3_public_name(V3_M13_GRAPH_ID, label="M13 graph id")
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
        prepare_seconds = time.perf_counter() - prepare_start
        buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(capacity)
        try:
            for _ in range(warmups):
                scene.ray_triangle_hit_stream_same_stream_row_reduction_summary(rays, buffers)

            host_samples = []
            native_enqueue_samples = []
            consumer_samples = []
            snapshots = []
            classifications = []
            result_summaries = []
            result_metadata = []
            for _ in range(repeats):
                start = time.perf_counter()
                result = scene.ray_triangle_hit_stream_same_stream_row_reduction_summary(
                    rays,
                    buffers,
                    transfer_counter=transfer_counter,
                )
                host_samples.append(time.perf_counter() - start)
                summary = dict(result["summary"])
                metadata = dict(result["metadata"])
                timings = dict(metadata.get("phase_timing_seconds") or {})
                snapshot = dict(metadata["transfer_counter_snapshot"])
                classification = classify_no_hidden_copy_transfer_snapshot(
                    snapshot,
                    min_named_column_bytes=capacity * 8,
                    allowed_non_column_host_to_device_bytes=V3_M13_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
                    measured_window="post_native_enqueue_same_stream_hit_stream_row_reduction_before_summary_materialization",
                    readiness_source="v3_m13_hit_stream_transfer_counter_classification",
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

    if not result_summaries:
        raise GraphValidationError("M13 hit-stream run produced no samples")
    signature = _hit_stream_signature(result_summaries[-1])
    if any(_hit_stream_signature(summary) != signature for summary in result_summaries):
        raise GraphValidationError("M13 hit-stream signatures changed across repeats")
    all_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in classifications)
    final_metadata = result_metadata[-1]
    same_stream_evidence = {
        "evidence_source": "cupy_rawkernel_same_stream_hit_stream_row_reduction",
        "event_pair_scope": "post_native_enqueue_to_cupy_row_reduction_before_summary_materialization",
        "producer_consumer_stream_ordering": final_metadata.get("producer_consumer_stream_ordering"),
        "stream_synchronization_proven": bool(final_metadata.get("stream_synchronization_proven")),
        "event_or_same_stream_ordering_proven": bool(final_metadata.get("event_or_same_stream_ordering_proven")),
        "native_symbol": final_metadata.get("native_symbol"),
        "release_symbol": final_metadata.get("release_symbol"),
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
        readiness_source="v3_m13_hit_stream_transfer_counter_classification",
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
        "no_hidden_column_copy_ready": all_ready,
        "true_zero_copy_ready": all_ready,
        "claim_readiness": {
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "no_hidden_column_copy_ready": all_ready,
            "true_zero_copy_ready": all_ready,
            "public_claim_authorized": False,
        },
        "public_claim_authorized": False,
    }
    payload = {
        "version": V3_M13_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        "status": V3_M13_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        "graph_id": V3_M13_GRAPH_ID,
        "contract_key": V3_M13_CONTRACT_KEY,
        "parameters": {
            "ray_count": ray_count,
            "triangle_count": len(triangles),
            "capacity": capacity,
            "capacity_multiplier": capacity_multiplier,
            "warmups": warmups,
            "repeats": repeats,
            "allowed_non_column_host_to_device_bytes": V3_M13_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            "transfer_counter_library": str(transfer_counter_library),
        },
        "partner_rows": (row,),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": bool(row["same_stream_ready"]),
            "transfer_counter_observed": bool(row["transfer_counter_observed"]),
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
                "M13 applies the M12 no-hidden-copy contract to a second workload: "
                "OptiX ray-triangle hit-stream producer plus CuPy same-stream row-reduction consumer. "
                "The measured window starts after native producer enqueue and ends before final summary "
                "materialization, so it proves the producer-to-partner handoff window only."
            ),
        },
    }
    validate_v3_m13_hit_stream_no_hidden_copy_payload(payload)
    return payload


def validate_v3_m13_hit_stream_no_hidden_copy_payload(payload: Mapping[str, object]) -> dict[str, object]:
    validation = validate_no_hidden_copy_payload(
        payload,
        expected_version=V3_M13_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        expected_status=V3_M13_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        required_partners=V3_M13_PARTNERS,
        require_signature_match=True,
    )
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 1:
        raise GraphValidationError("M13 hit-stream payload requires one CuPy partner row")
    row = rows[0]
    if int(row.get("ray_count", 0) or 0) <= 0:
        raise GraphValidationError("M13 hit-stream row requires a positive ray_count")
    signature = tuple(row.get("validation_signature", ()))
    if len(signature) != 8:
        raise GraphValidationError("M13 hit-stream signature must include row and reduction fields")
    metadata = row.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise GraphValidationError("M13 hit-stream row requires metadata")
    same_stream = metadata.get("same_stream_evidence", {})
    if not isinstance(same_stream, Mapping):
        raise GraphValidationError("M13 hit-stream row requires same-stream evidence")
    if same_stream.get("event_pair_scope") != "post_native_enqueue_to_cupy_row_reduction_before_summary_materialization":
        raise GraphValidationError("M13 measured window scope is wrong")
    if same_stream.get("host_row_materialization_before_consumer") is not False:
        raise GraphValidationError("M13 must not materialize hit rows before the partner consumer")
    validation["status"] = V3_M13_HIT_STREAM_NO_HIDDEN_COPY_STATUS
    return validation


def make_v3_m13_two_plane_triangles() -> tuple[Triangle3D, Triangle3D]:
    return (
        Triangle3D(
            id=0,
            x0=0.0,
            y0=0.0,
            z0=0.0,
            x1=1.0,
            y1=0.0,
            z1=0.0,
            x2=0.0,
            y2=1.0,
            z2=0.0,
        ),
        Triangle3D(
            id=1,
            x0=0.0,
            y0=0.0,
            z0=1.0,
            x1=1.0,
            y1=0.0,
            z1=1.0,
            x2=0.0,
            y2=1.0,
            z2=1.0,
        ),
    )


def make_v3_m13_hit_stream_rays(ray_count: int) -> tuple[Ray3D, ...]:
    count = int(ray_count)
    if count <= 0:
        raise GraphValidationError("ray_count must be positive")
    return tuple(
        Ray3D(
            id=index,
            ox=0.25 + float(index % 7) * 0.01,
            oy=0.25 + float((index // 7) % 7) * 0.01,
            oz=-1.0,
            dx=0.0,
            dy=0.0,
            dz=1.0,
            tmax=4.0,
        )
        for index in range(count)
    )


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
