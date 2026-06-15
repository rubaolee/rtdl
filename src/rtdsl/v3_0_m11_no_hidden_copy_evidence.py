from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
import statistics
import time

from .partner_adapters import prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d
from .partner_adapters import prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import REQUIRED_PHASE_NAMES
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_instrumentation import EvidenceRecord
from .v3_0_instrumentation import InstrumentationPacket
from .v3_0_instrumentation import PhaseTimingRecord
from .v3_0_instrumentation import ResidencyEvidence
from .v3_0_m9_grouped_stream_partner import V3_M9_PARTNERS
from .v3_0_m9_grouped_stream_partner import _apply_numba_cuda_compat_env
from .v3_0_m9_grouped_stream_partner import _column_data_ptrs
from .v3_0_m9_grouped_stream_partner import _component_signature_from_columns
from .v3_0_m9_grouped_stream_partner import make_v3_m9_point_grid_3d
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import annotate_no_hidden_copy_metadata
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import validate_no_hidden_copy_payload


V3_M11_NO_HIDDEN_COPY_VERSION = "rtdl.v3_0.no_hidden_copy_evidence.m11"
V3_M11_NO_HIDDEN_COPY_STATUS = "m11_transfer_counter_no_hidden_column_copy_internal_claims_gated"
V3_M11_GRAPH_ID = "fixed_radius_component_no_hidden_copy_evidence_pilot"
V3_M11_CONTRACT_KEY = "fixed_radius_component_no_hidden_copy_contract_v1"
V3_M11_PARTNERS = V3_M9_PARTNERS
V3_M11_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)


def run_v3_m11_no_hidden_copy_evidence_case(
    *,
    transfer_counter_library: str | Path,
    point_count: int = 65536,
    radius: float = 1.01,
    component_threshold: int = 7,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
    partners: Sequence[str] = V3_M11_PARTNERS,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, object]:
    compat = _apply_numba_cuda_compat_env()
    validate_v3_public_name(V3_M11_GRAPH_ID, label="M11 graph id")
    if int(warmups) < 0 or int(repeats) <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    if float(radius) <= 0.0:
        raise GraphValidationError("radius must be positive")
    if int(component_threshold) < 1:
        raise GraphValidationError("component_threshold must be at least 1")
    partner_tuple = tuple(str(partner) for partner in partners)
    if partner_tuple != V3_M11_PARTNERS:
        raise GraphValidationError("M11 no-hidden-copy case requires cupy and numba rows")

    counter = CudaTransferCounter(transfer_counter_library)
    points = make_v3_m9_point_grid_3d(int(point_count))
    rows = []
    signatures = {}
    for partner in partner_tuple:
        row = _run_partner_row(
            partner=partner,
            points=points,
            radius=float(radius),
            component_threshold=int(component_threshold),
            warmups=int(warmups),
            repeats=int(repeats),
            hardware=hardware,
            grouped_union_direct_side_effect=bool(grouped_union_direct_side_effect),
            compat_env=compat,
            transfer_counter=counter,
        )
        rows.append(row)
        signatures[partner] = tuple(row["validation_signature"])

    if len(set(signatures.values())) != 1:
        raise GraphValidationError("M11 no-hidden-copy CuPy and Numba signatures differ")

    payload = {
        "version": V3_M11_NO_HIDDEN_COPY_VERSION,
        "status": V3_M11_NO_HIDDEN_COPY_STATUS,
        "graph_id": V3_M11_GRAPH_ID,
        "contract_key": V3_M11_CONTRACT_KEY,
        "parameters": {
            "point_count": int(point_count),
            "radius": float(radius),
            "component_threshold": int(component_threshold),
            "warmups": int(warmups),
            "repeats": int(repeats),
            "grouped_union_query_block_size": None,
            "grouped_union_direct_side_effect": bool(grouped_union_direct_side_effect),
            "allowed_non_column_host_to_device_bytes": V3_M11_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            "transfer_counter_library": str(transfer_counter_library),
        },
        "partner_rows": tuple(rows),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": all(bool(row["same_stream_ready"]) for row in rows),
            "transfer_counter_observed": all(bool(row["transfer_counter_observed"]) for row in rows),
            "no_hidden_column_copy_ready": all(bool(row["no_hidden_column_copy_ready"]) for row in rows),
            "true_zero_copy_ready": all(bool(row["true_zero_copy_ready"]) for row in rows),
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "reason": (
                "This gate attaches an LD_PRELOAD CUDA transfer counter to the same M10 "
                "native-to-partner event window. It promotes internal named-column true-zero-copy "
                "readiness only when observed transfers are absent or limited to small launch-parameter "
                "host-to-device copies, with no device-to-host, device-to-device, or unknown copies."
            ),
        },
    }
    validate_v3_m11_no_hidden_copy_payload(payload)
    return payload


def classify_transfer_counter_snapshot(
    snapshot: Mapping[str, object],
    *,
    point_count: int,
    allowed_non_column_host_to_device_bytes: int = V3_M11_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
) -> dict[str, object]:
    point_count = int(point_count)
    min_named_column_bytes = min(point_count * 4, point_count * 8)
    return classify_no_hidden_copy_transfer_snapshot(
        snapshot,
        min_named_column_bytes=min_named_column_bytes,
        allowed_non_column_host_to_device_bytes=allowed_non_column_host_to_device_bytes,
        measured_window="m11_native_optix_to_python_partner_continuation",
        readiness_source="v3_m11_transfer_counter_classification",
    )


def build_v3_m11_no_hidden_copy_instrumentation(
    *,
    partner: str,
    hardware: str,
    prepare_seconds: float,
    host_run_seconds: float,
    native_event_seconds: float,
    partner_event_seconds: float,
    validation_seconds: float,
    data_ptrs: Mapping[str, int],
    metadata: Mapping[str, object],
    transfer_classification: Mapping[str, object],
) -> InstrumentationPacket:
    partner = str(partner)
    if partner not in V3_M11_PARTNERS:
        raise GraphValidationError("M11 instrumentation partner must be cupy or numba")
    event_id = f"{partner}_native_partner_cuda_event_pair"
    transfer_id = f"{partner}_cuda_transfer_counter_window"
    pointer_id = f"{partner}_device_pointer_record"
    validation_id = f"{partner}_validation_timer_record"
    same_stream_evidence = dict(metadata.get("same_stream_evidence") or {})
    evidence = (
        EvidenceRecord(
            evidence_id=event_id,
            kind="cuda_event_pair",
            backend="optix",
            phase="stream_handoff",
            source=str(same_stream_evidence.get("evidence_source", "cuda_event_pair")),
            hardware=hardware,
            details=same_stream_evidence,
        ),
        EvidenceRecord(
            evidence_id=transfer_id,
            kind="transfer_counter",
            backend="optix",
            phase="stream_handoff",
            source="ld_preload_cuda_memcpy_counter",
            hardware=hardware,
            details=dict(transfer_classification),
        ),
        EvidenceRecord(
            evidence_id=pointer_id,
            kind="pointer_identity",
            backend="optix",
            phase="stream_handoff",
            source=f"{partner}_device_array_pointer_probe",
            hardware=hardware,
            details={key: int(value) for key, value in data_ptrs.items()},
        ),
        EvidenceRecord(
            evidence_id=validation_id,
            kind="host_timer",
            backend="optix",
            phase="validation",
            source="post_measurement_signature_materialization",
            hardware=hardware,
            details={"validation_seconds": float(validation_seconds)},
        ),
    )
    phase_seconds = {
        "prepare": float(prepare_seconds),
        "build": 0.0,
        "upload": 0.0,
        "query_prepare": 0.0,
        "rt_traversal": float(native_event_seconds),
        "stream_handoff": 0.0,
        "continuation_or_reduction": float(partner_event_seconds),
        "download_or_materialization": 0.0,
        "validation": float(validation_seconds),
        "host_wrapper": float(host_run_seconds),
    }
    phase_sources = {
        "rt_traversal": "cuda_event",
        "stream_handoff": "cuda_event",
        "continuation_or_reduction": "cuda_event",
        "host_wrapper": "host_timer",
        "validation": "host_timer",
    }
    phase_evidence_ids = {
        "rt_traversal": (event_id,),
        "stream_handoff": (event_id, transfer_id, pointer_id),
        "continuation_or_reduction": (event_id, transfer_id),
        "validation": (validation_id,),
    }
    timings = tuple(
        PhaseTimingRecord(
            phase=phase,
            seconds=phase_seconds[phase],
            backend="optix",
            timing_source=phase_sources.get(phase, "metadata_only"),
            evidence_ids=phase_evidence_ids.get(phase, ()),
            steady_state_candidate=phase in {"rt_traversal", "stream_handoff", "continuation_or_reduction"},
            setup_candidate=phase in {"prepare", "build", "upload", "query_prepare"},
            materialization_candidate=phase == "download_or_materialization",
        )
        for phase in REQUIRED_PHASE_NAMES
    )
    residency = (
        ResidencyEvidence(
            value_name="component_labels",
            storage="cuda",
            residency="device_resident",
            lifetime="partner_owned",
            stream_ordering="same_stream",
            data_ptr_observed=bool(data_ptrs.get("component_labels")),
            backend_handle_observed=True,
            transfer_counter_observed=True,
            host_materialized=False,
            hidden_copy_observed=bool(transfer_classification.get("hidden_copy_observed")),
            evidence_ids=(event_id, transfer_id, pointer_id),
        ),
    )
    return InstrumentationPacket(
        graph_id=V3_M11_GRAPH_ID,
        backend="optix",
        hardware=hardware,
        phase_timings=timings,
        evidence_records=evidence,
        residency_evidence=residency,
    )


def validate_v3_m11_no_hidden_copy_payload(payload: Mapping[str, object]) -> dict[str, object]:
    validation = validate_no_hidden_copy_payload(
        payload,
        expected_version=V3_M11_NO_HIDDEN_COPY_VERSION,
        expected_status=V3_M11_NO_HIDDEN_COPY_STATUS,
        required_partners=V3_M11_PARTNERS,
        require_signature_match=True,
    )
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 2:
        raise GraphValidationError("M11 no-hidden-copy payload requires two partner rows")
    validation["status"] = V3_M11_NO_HIDDEN_COPY_STATUS
    return validation


def _run_partner_row(
    *,
    partner: str,
    points: Sequence[object],
    radius: float,
    component_threshold: int,
    warmups: int,
    repeats: int,
    hardware: str,
    grouped_union_direct_side_effect: bool,
    compat_env: Mapping[str, object],
    transfer_counter: CudaTransferCounter,
) -> dict[str, object]:
    prepare_start = time.perf_counter()
    if partner == "cupy":
        prepared = prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
            points,
            radius=radius,
            grouped_union_query_block_size=None,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
        )
    elif partner == "numba":
        prepared = prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
            points,
            radius=radius,
            grouped_union_query_block_size=None,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
            boundary_assignment_policy="single_pass_candidate_root_rebased",
        )
    else:
        raise GraphValidationError("unsupported M11 partner")
    prepare_seconds = time.perf_counter() - prepare_start
    try:
        for _ in range(warmups):
            prepared.run_same_stream_evidence(
                min_neighbors=component_threshold,
                return_metadata=True,
            )

        host_samples = []
        native_event_samples = []
        partner_event_samples = []
        total_event_samples = []
        transfer_samples = []
        classifications = []
        last_result = None
        for _ in range(repeats):
            start = time.perf_counter()
            result = prepared.run_same_stream_evidence(
                min_neighbors=component_threshold,
                return_metadata=True,
                transfer_counter=transfer_counter,
            )
            host_elapsed = time.perf_counter() - start
            metadata = dict(result["metadata"])
            evidence = dict(metadata["same_stream_evidence"])
            snapshot = dict(evidence["transfer_counter_snapshot"])
            classification = classify_transfer_counter_snapshot(
                snapshot,
                point_count=len(points),
            )
            host_samples.append(host_elapsed)
            native_event_samples.append(float(evidence["native_event_ms"]) / 1000.0)
            partner_event_samples.append(float(evidence["partner_event_ms"]) / 1000.0)
            total_event_samples.append(float(evidence["total_event_ms"]) / 1000.0)
            transfer_samples.append(snapshot)
            classifications.append(classification)
            last_result = result
        if last_result is None:
            raise GraphValidationError("M11 no-hidden-copy partner run produced no samples")

        validation_start = time.perf_counter()
        signature = _component_signature_from_columns(last_result["columns"])
        validation_seconds = time.perf_counter() - validation_start
        data_ptrs = _column_data_ptrs(last_result["columns"])
        metadata = dict(last_result["metadata"])
        final_classification = classifications[-1]
        all_samples_no_hidden_copy = all(
            bool(item["no_hidden_column_copy_ready"]) for item in classifications
        )
        metadata = annotate_no_hidden_copy_metadata(
            metadata,
            final_classification,
            all_samples_ready=all_samples_no_hidden_copy,
            readiness_source="v3_m11_transfer_counter_classification",
        )
        instrumentation = build_v3_m11_no_hidden_copy_instrumentation(
            partner=partner,
            hardware=hardware,
            prepare_seconds=prepare_seconds,
            host_run_seconds=statistics.median(host_samples),
            native_event_seconds=statistics.median(native_event_samples),
            partner_event_seconds=statistics.median(partner_event_samples),
            validation_seconds=validation_seconds,
            data_ptrs=data_ptrs,
            metadata=metadata,
            transfer_classification=final_classification,
        )
        return {
            "partner": partner,
            "backend": "optix",
            "host_samples_seconds": tuple(host_samples),
            "native_event_seconds_median": statistics.median(native_event_samples),
            "partner_event_seconds_median": statistics.median(partner_event_samples),
            "total_event_seconds_median": statistics.median(total_event_samples),
            "prepare_seconds": prepare_seconds,
            "validation_seconds": validation_seconds,
            "validation_signature": signature,
            "device_data_ptrs": data_ptrs,
            "metadata": metadata,
            "transfer_counter_samples": tuple(transfer_samples),
            "transfer_counter_classifications": tuple(classifications),
            "transfer_counter_classification": final_classification,
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "no_hidden_column_copy_ready": all_samples_no_hidden_copy,
            "true_zero_copy_ready": all_samples_no_hidden_copy,
            "numba_cuda_compat_env": dict(compat_env) if partner == "numba" else None,
            "instrumentation": instrumentation.to_metadata(),
            "claim_readiness": instrumentation.claim_readiness,
            "public_claim_authorized": False,
        }
    finally:
        close = getattr(prepared, "close", None)
        if close is not None:
            close()
