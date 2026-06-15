from __future__ import annotations

from collections.abc import Mapping, Sequence
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


V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION = (
    "rtdl.v3_0.hit_stream_full_window_transfer_audit.m14"
)
V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_STATUS = (
    "m14_hit_stream_full_window_transfer_audit_internal_claims_gated"
)
V3_M14_GRAPH_ID = "ray_triangle_hit_stream_full_window_transfer_audit"
V3_M14_CONTRACT_KEY = "ray_triangle_hit_stream_full_window_transfer_audit_contract_v1"
V3_M14_PARTNERS = ("cupy",)
V3_M14_GPU_RAY3D_HOST_BYTES = 32
V3_M14_ALLOWED_LAUNCH_PARAMETER_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)


def run_v3_m14_hit_stream_full_window_transfer_audit_case(
    *,
    transfer_counter_library: str | Path,
    ray_count: int = 8192,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
    capacity_multiplier: int = 2,
    deduplicate_primitives: bool = False,
) -> dict[str, object]:
    validate_v3_public_name(V3_M14_GRAPH_ID, label="M14 graph id")
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
                scene.ray_triangle_hit_stream_same_stream_row_reduction_summary(
                    rays,
                    buffers,
                    deduplicate_primitives=bool(deduplicate_primitives),
                )

            host_samples = []
            native_enqueue_samples = []
            consumer_samples = []
            snapshots = []
            audits = []
            result_summaries = []
            result_metadata = []
            for _ in range(repeats):
                start = time.perf_counter()
                result = scene.ray_triangle_hit_stream_same_stream_row_reduction_summary(
                    rays,
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
                audit = classify_v3_m14_full_window_transfer_snapshot(
                    snapshot,
                    ray_count=ray_count,
                    min_named_output_column_bytes=capacity * 8,
                    measured_window="native_producer_enqueue_to_same_stream_hit_stream_row_reduction_before_summary_materialization",
                    readiness_source="v3_m14_full_window_transfer_audit",
                )
                native_enqueue_samples.append(float(timings.get("native_async_launch_enqueue", 0.0)))
                consumer_samples.append(
                    float(timings.get("same_stream_partner_row_reduction_consumer_and_materialization", 0.0))
                )
                snapshots.append(snapshot)
                audits.append(audit)
                result_summaries.append(summary)
                result_metadata.append(metadata)
        finally:
            buffers.close()

    if not result_summaries:
        raise GraphValidationError("M14 hit-stream full-window audit produced no samples")
    signature = _hit_stream_signature(result_summaries[-1])
    if any(_hit_stream_signature(summary) != signature for summary in result_summaries):
        raise GraphValidationError("M14 hit-stream signatures changed across repeats")

    all_uploads_explained = all(bool(item["producer_input_upload_explained"]) for item in audits)
    all_no_forbidden_direction = all(bool(item["no_device_to_host_device_to_device_or_unknown_copy"]) for item in audits)
    all_handoff_ready = all(bool(item["handoff_no_hidden_output_copy_ready"]) for item in audits)
    all_full_zero_copy_ready = all(bool(item["full_window_true_zero_copy_ready"]) for item in audits)
    final_metadata = result_metadata[-1]
    full_window_evidence = {
        "evidence_source": "cuda_transfer_counter_full_producer_consumer_window",
        "event_pair_scope": "native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization",
        "producer_consumer_stream_ordering": final_metadata.get("producer_consumer_stream_ordering"),
        "stream_synchronization_proven": bool(final_metadata.get("stream_synchronization_proven")),
        "event_or_same_stream_ordering_proven": bool(final_metadata.get("event_or_same_stream_ordering_proven")),
        "native_symbol": final_metadata.get("native_symbol"),
        "release_symbol": final_metadata.get("release_symbol"),
        "transfer_counter_observed": True,
        "transfer_counter_snapshot": snapshots[-1],
        "transfer_counter_scope": final_metadata.get("transfer_counter_scope"),
        "transfer_counter_window": final_metadata.get("transfer_counter_window"),
        "validation_materialization_after_measured_window": True,
        "producer_input_upload_mode": final_metadata.get("producer_input_upload_mode"),
        "producer_input_upload_host_blocking_cuda_copy": bool(
            final_metadata.get("producer_input_upload_host_blocking_cuda_copy")
        ),
        "query_rays_still_packed_on_host": bool(final_metadata.get("query_rays_still_packed_on_host")),
        "expected_query_ray_upload_bytes": ray_count * V3_M14_GPU_RAY3D_HOST_BYTES,
        "allowed_launch_parameter_host_to_device_bytes": (
            V3_M14_ALLOWED_LAUNCH_PARAMETER_HOST_TO_DEVICE_BYTES
        ),
        "producer_input_upload_explained": all_uploads_explained,
        "handoff_no_hidden_output_copy_ready": all_handoff_ready,
        "full_window_true_zero_copy_ready": all_full_zero_copy_ready,
        "host_row_materialization_before_consumer": bool(
            final_metadata.get("host_row_materialization_before_consumer")
        ),
        "host_scalar_read_before_consumer": bool(final_metadata.get("host_scalar_read_before_consumer")),
        "cuda_stream_ptr_nonzero": bool(final_metadata.get("cuda_stream_ptr_nonzero")),
    }
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
        "metadata": {
            "full_window_transfer_evidence": full_window_evidence,
            "hit_stream_metadata": final_metadata,
        },
        "transfer_counter_samples": tuple(snapshots),
        "transfer_audits": tuple(audits),
        "transfer_audit": audits[-1],
        "transfer_audit_summary": summarize_v3_m14_full_window_transfer_audits(tuple(audits)),
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "producer_input_upload_observed": bool(audits[-1]["producer_input_upload_observed"]),
        "producer_input_upload_explained": all_uploads_explained,
        "no_device_to_host_device_to_device_or_unknown_copy": all_no_forbidden_direction,
        "handoff_no_hidden_output_copy_ready": all_handoff_ready,
        "full_window_true_zero_copy_ready": all_full_zero_copy_ready,
        "claim_readiness": {
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "producer_input_upload_explained": all_uploads_explained,
            "handoff_no_hidden_output_copy_ready": all_handoff_ready,
            "full_window_true_zero_copy_ready": all_full_zero_copy_ready,
            "public_claim_authorized": False,
        },
        "public_claim_authorized": False,
    }
    payload = {
        "version": V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION,
        "status": V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_STATUS,
        "graph_id": V3_M14_GRAPH_ID,
        "contract_key": V3_M14_CONTRACT_KEY,
        "parameters": {
            "ray_count": ray_count,
            "triangle_count": len(triangles),
            "capacity": capacity,
            "capacity_multiplier": capacity_multiplier,
            "deduplicate_primitives": bool(deduplicate_primitives),
            "warmups": warmups,
            "repeats": repeats,
            "gpu_ray3d_host_bytes": V3_M14_GPU_RAY3D_HOST_BYTES,
            "expected_query_ray_upload_bytes": ray_count * V3_M14_GPU_RAY3D_HOST_BYTES,
            "allowed_launch_parameter_host_to_device_bytes": (
                V3_M14_ALLOWED_LAUNCH_PARAMETER_HOST_TO_DEVICE_BYTES
            ),
            "transfer_counter_library": str(transfer_counter_library),
            "hardware": hardware,
        },
        "partner_rows": (row,),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": bool(row["same_stream_ready"]),
            "transfer_counter_observed": bool(row["transfer_counter_observed"]),
            "producer_input_upload_observed": bool(row["producer_input_upload_observed"]),
            "producer_input_upload_explained": bool(row["producer_input_upload_explained"]),
            "no_device_to_host_device_to_device_or_unknown_copy": bool(
                row["no_device_to_host_device_to_device_or_unknown_copy"]
            ),
            "handoff_no_hidden_output_copy_ready": bool(row["handoff_no_hidden_output_copy_ready"]),
            "full_window_true_zero_copy_ready": bool(row["full_window_true_zero_copy_ready"]),
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "reason": (
                "M14 intentionally expands the M13 measured window to include native producer enqueue. "
                "For the current host-packed ray API, the full window includes expected query-ray HtoD "
                "input upload plus small launch-parameter upload. Therefore the full window is not an "
                "end-to-end true-zero-copy claim; the useful claim is that no DtoH/DtoD/unknown transfer "
                "or unexplained HtoD transfer is observed before the same-stream partner summary."
            ),
        },
    }
    validate_v3_m14_hit_stream_full_window_transfer_audit_payload(payload)
    return payload


def classify_v3_m14_full_window_transfer_snapshot(
    snapshot: Mapping[str, object],
    *,
    ray_count: int,
    min_named_output_column_bytes: int,
    allowed_launch_parameter_host_to_device_bytes: int = (
        V3_M14_ALLOWED_LAUNCH_PARAMETER_HOST_TO_DEVICE_BYTES
    ),
    measured_window: str = "native_producer_enqueue_to_same_stream_partner_before_materialization",
    readiness_source: str = "v3_m14_full_window_transfer_audit",
) -> dict[str, object]:
    if not isinstance(snapshot, Mapping):
        raise GraphValidationError("transfer counter snapshot must be a mapping")
    ray_count = int(ray_count)
    min_named_output_column_bytes = int(min_named_output_column_bytes)
    allowed_launch_parameter_host_to_device_bytes = int(allowed_launch_parameter_host_to_device_bytes)
    if ray_count <= 0:
        raise GraphValidationError("ray_count must be positive")
    if min_named_output_column_bytes <= 0:
        raise GraphValidationError("min_named_output_column_bytes must be positive")
    if allowed_launch_parameter_host_to_device_bytes < 0:
        raise GraphValidationError("allowed_launch_parameter_host_to_device_bytes must be non-negative")

    observed_h2d = _snapshot_int(snapshot, "host_to_device_bytes")
    observed_dtoh_calls = _snapshot_int(snapshot, "device_to_host_calls")
    observed_dtod_calls = _snapshot_int(snapshot, "device_to_device_calls")
    observed_unknown_calls = _snapshot_int(snapshot, "unknown_calls")
    expected_query_ray_upload_bytes = ray_count * V3_M14_GPU_RAY3D_HOST_BYTES
    expected_upper_bound = expected_query_ray_upload_bytes + allowed_launch_parameter_host_to_device_bytes

    disallowed_reasons = []
    if observed_dtoh_calls:
        disallowed_reasons.append("device_to_host_copy_observed")
    if observed_dtod_calls:
        disallowed_reasons.append("device_to_device_copy_observed")
    if observed_unknown_calls:
        disallowed_reasons.append("unknown_direction_copy_observed")
    if observed_h2d < expected_query_ray_upload_bytes:
        disallowed_reasons.append("expected_query_ray_upload_not_observed")
    if observed_h2d > expected_upper_bound:
        disallowed_reasons.append("host_to_device_bytes_exceed_query_upload_plus_launch_parameter_scope")

    producer_input_upload_observed = observed_h2d >= expected_query_ray_upload_bytes
    producer_input_upload_explained = (
        producer_input_upload_observed and observed_h2d <= expected_upper_bound
    )
    no_forbidden_direction = (
        observed_dtoh_calls == 0 and observed_dtod_calls == 0 and observed_unknown_calls == 0
    )
    handoff_ready = no_forbidden_direction and producer_input_upload_explained
    full_zero_copy_ready = _snapshot_int(snapshot, "total_bytes") == 0 and no_forbidden_direction
    excess_host_to_device_bytes = max(0, observed_h2d - expected_query_ray_upload_bytes)
    return {
        "audit_version": V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION,
        "audit_status": V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_STATUS,
        "transfer_counter_observed": True,
        "readiness_source": readiness_source,
        "measured_window": str(measured_window),
        "allowed_transfer_scope": (
            "full producer+consumer window; host-to-device bytes may cover expected host-packed query "
            "ray upload plus small launch parameters, while device-to-host/device-to-device/unknown "
            "copies are disallowed before summary materialization"
        ),
        "ray_count": ray_count,
        "gpu_ray3d_host_bytes": V3_M14_GPU_RAY3D_HOST_BYTES,
        "expected_query_ray_upload_bytes": expected_query_ray_upload_bytes,
        "allowed_launch_parameter_host_to_device_bytes": (
            allowed_launch_parameter_host_to_device_bytes
        ),
        "expected_host_to_device_upper_bound_bytes": expected_upper_bound,
        "min_named_output_column_bytes": min_named_output_column_bytes,
        "observed_total_calls": _snapshot_int(snapshot, "total_calls"),
        "observed_total_bytes": _snapshot_int(snapshot, "total_bytes"),
        "observed_host_to_device_calls": _snapshot_int(snapshot, "host_to_device_calls"),
        "observed_host_to_device_bytes": observed_h2d,
        "observed_host_to_device_excess_after_expected_query_upload_bytes": (
            excess_host_to_device_bytes
        ),
        "observed_device_to_host_calls": observed_dtoh_calls,
        "observed_device_to_host_bytes": _snapshot_int(snapshot, "device_to_host_bytes"),
        "observed_device_to_device_calls": observed_dtod_calls,
        "observed_device_to_device_bytes": _snapshot_int(snapshot, "device_to_device_bytes"),
        "observed_unknown_calls": observed_unknown_calls,
        "observed_unknown_bytes": _snapshot_int(snapshot, "unknown_bytes"),
        "producer_input_upload_observed": producer_input_upload_observed,
        "producer_input_upload_explained": producer_input_upload_explained,
        "no_device_to_host_device_to_device_or_unknown_copy": no_forbidden_direction,
        "handoff_no_hidden_output_copy_ready": handoff_ready,
        "full_window_true_zero_copy_ready": full_zero_copy_ready,
        "unexpected_transfer_observed": bool(disallowed_reasons),
        "disallowed_reasons": tuple(disallowed_reasons),
    }


def summarize_v3_m14_full_window_transfer_audits(
    audits: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    rows = tuple(audits)
    if not rows:
        raise GraphValidationError("no M14 full-window transfer audits were provided")
    return {
        "audit_version": V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION,
        "sample_count": len(rows),
        "producer_input_upload_explained": all(
            bool(row.get("producer_input_upload_explained")) for row in rows
        ),
        "handoff_no_hidden_output_copy_ready": all(
            bool(row.get("handoff_no_hidden_output_copy_ready")) for row in rows
        ),
        "full_window_true_zero_copy_ready": all(
            bool(row.get("full_window_true_zero_copy_ready")) for row in rows
        ),
        "max_observed_host_to_device_bytes": max(
            int(row.get("observed_host_to_device_bytes", 0) or 0) for row in rows
        ),
        "max_observed_total_bytes": max(int(row.get("observed_total_bytes", 0) or 0) for row in rows),
        "max_host_to_device_excess_after_expected_query_upload_bytes": max(
            int(row.get("observed_host_to_device_excess_after_expected_query_upload_bytes", 0) or 0)
            for row in rows
        ),
        "any_device_to_host_copy_observed": any(
            int(row.get("observed_device_to_host_calls", 0) or 0) > 0 for row in rows
        ),
        "any_device_to_device_copy_observed": any(
            int(row.get("observed_device_to_device_calls", 0) or 0) > 0 for row in rows
        ),
        "any_unknown_direction_copy_observed": any(
            int(row.get("observed_unknown_calls", 0) or 0) > 0 for row in rows
        ),
        "disallowed_reasons": tuple(
            reason for row in rows for reason in tuple(row.get("disallowed_reasons", ()))
        ),
    }


def validate_v3_m14_hit_stream_full_window_transfer_audit_payload(
    payload: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("M14 full-window transfer audit payload must be a mapping")
    if payload.get("version") != V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION:
        raise GraphValidationError("unexpected M14 full-window transfer audit version")
    if payload.get("status") != V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_STATUS:
        raise GraphValidationError("unexpected M14 full-window transfer audit status")
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 1:
        raise GraphValidationError("M14 full-window transfer audit requires one CuPy partner row")
    row = rows[0]
    if not isinstance(row, Mapping):
        raise GraphValidationError("M14 full-window transfer audit row must be a mapping")
    if row.get("partner") != "cupy":
        raise GraphValidationError("M14 full-window transfer audit requires the CuPy partner")
    if int(row.get("ray_count", 0) or 0) <= 0:
        raise GraphValidationError("M14 full-window transfer audit row requires a positive ray_count")
    signature = tuple(row.get("validation_signature", ()))
    if len(signature) != 8:
        raise GraphValidationError("M14 hit-stream signature must include row and reduction fields")
    audit = row.get("transfer_audit", {})
    validate_v3_m14_full_window_transfer_audit(audit)
    if row.get("producer_input_upload_observed") is not True:
        raise GraphValidationError("M14 must observe current host-packed query input upload")
    if row.get("producer_input_upload_explained") is not True:
        raise GraphValidationError("M14 must explain producer input upload bytes")
    if row.get("handoff_no_hidden_output_copy_ready") is not True:
        raise GraphValidationError("M14 must preserve no-hidden-output-copy handoff readiness")
    if row.get("full_window_true_zero_copy_ready") is not False:
        raise GraphValidationError("M14 current host-packed path must not claim full-window true zero-copy")
    metadata = row.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise GraphValidationError("M14 full-window row requires metadata")
    evidence = metadata.get("full_window_transfer_evidence", {})
    if not isinstance(evidence, Mapping):
        raise GraphValidationError("M14 full-window row requires full-window evidence")
    if evidence.get("event_pair_scope") != "native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization":
        raise GraphValidationError("M14 measured window scope is wrong")
    if evidence.get("transfer_counter_scope") != "producer_consumer":
        raise GraphValidationError("M14 runtime transfer counter scope is wrong")
    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping):
        raise GraphValidationError("M14 full-window transfer audit requires comparison")
    for key in (
        "signature_match",
        "same_stream_ready",
        "transfer_counter_observed",
        "producer_input_upload_observed",
        "producer_input_upload_explained",
        "no_device_to_host_device_to_device_or_unknown_copy",
        "handoff_no_hidden_output_copy_ready",
    ):
        if comparison.get(key) is not True:
            raise GraphValidationError(f"M14 comparison must prove {key}=true")
    if comparison.get("full_window_true_zero_copy_ready") is not False:
        raise GraphValidationError("M14 comparison must not claim full-window true zero-copy")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M14 full-window transfer audit requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "same_stream_public_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
    ):
        if bool(boundary.get(str(key))):
            raise GraphValidationError(f"M14 full-window audit must not authorize {key}")
    return {
        "status": V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_STATUS,
        "partner_count": 1,
        "signature_match": True,
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "producer_input_upload_observed": True,
        "producer_input_upload_explained": True,
        "handoff_no_hidden_output_copy_ready": True,
        "full_window_true_zero_copy_ready": False,
        "public_claim_authorized": False,
    }


def validate_v3_m14_full_window_transfer_audit(audit: Mapping[str, object]) -> None:
    if not isinstance(audit, Mapping):
        raise GraphValidationError("M14 row requires transfer audit")
    if audit.get("transfer_counter_observed") is not True:
        raise GraphValidationError("M14 audit must observe a transfer counter")
    if audit.get("producer_input_upload_observed") is not True:
        raise GraphValidationError("M14 audit must observe query-ray input upload")
    if audit.get("producer_input_upload_explained") is not True:
        raise GraphValidationError("M14 audit must explain query-ray input upload")
    if audit.get("no_device_to_host_device_to_device_or_unknown_copy") is not True:
        raise GraphValidationError("M14 audit observed a forbidden transfer direction")
    if audit.get("handoff_no_hidden_output_copy_ready") is not True:
        raise GraphValidationError("M14 audit did not preserve handoff no-hidden-output-copy readiness")
    if audit.get("full_window_true_zero_copy_ready") is not False:
        raise GraphValidationError("M14 audit must not claim full-window true zero-copy")
    if tuple(audit.get("disallowed_reasons", ())) != ():
        raise GraphValidationError("M14 audit has disallowed transfer reasons")


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


def _snapshot_int(snapshot: Mapping[str, object], key: str) -> int:
    value = snapshot.get(key, 0)
    return int(value or 0)
