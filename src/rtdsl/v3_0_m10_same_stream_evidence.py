from __future__ import annotations

from collections.abc import Mapping, Sequence
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


V3_M10_SAME_STREAM_VERSION = "rtdl.v3_0.same_stream_evidence.m10"
V3_M10_SAME_STREAM_STATUS = "m10_same_stream_event_evidence_internal_claims_gated"
V3_M10_GRAPH_ID = "fixed_radius_component_same_stream_evidence_pilot"
V3_M10_CONTRACT_KEY = "fixed_radius_component_same_stream_contract_v1"
V3_M10_PARTNERS = V3_M9_PARTNERS


def run_v3_m10_same_stream_evidence_case(
    *,
    point_count: int = 8192,
    radius: float = 1.01,
    component_threshold: int = 7,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
    partners: Sequence[str] = V3_M10_PARTNERS,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, object]:
    compat = _apply_numba_cuda_compat_env()
    validate_v3_public_name(V3_M10_GRAPH_ID, label="M10 graph id")
    if int(warmups) < 0 or int(repeats) <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    if float(radius) <= 0.0:
        raise GraphValidationError("radius must be positive")
    if int(component_threshold) < 1:
        raise GraphValidationError("component_threshold must be at least 1")
    partner_tuple = tuple(str(partner) for partner in partners)
    if partner_tuple != V3_M10_PARTNERS:
        raise GraphValidationError("M10 same-stream case requires cupy and numba rows")

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
        )
        rows.append(row)
        signatures[partner] = tuple(row["validation_signature"])

    signatures_match = len(set(signatures.values())) == 1
    if not signatures_match:
        raise GraphValidationError("M10 same-stream CuPy and Numba signatures differ")

    cupy_row = next(row for row in rows if row["partner"] == "cupy")
    numba_row = next(row for row in rows if row["partner"] == "numba")
    cupy_total = float(cupy_row["total_event_seconds_median"])
    numba_total = float(numba_row["total_event_seconds_median"])
    event_accounting_warnings = tuple(
        {
            "partner": str(row["partner"]),
            "warning": row["event_accounting"]["warning"],
            "median_total_event_seconds": row["event_accounting"]["median_total_event_seconds"],
            "median_native_plus_partner_seconds": row["event_accounting"][
                "median_native_plus_partner_seconds"
            ],
        }
        for row in rows
        if isinstance(row.get("event_accounting"), Mapping) and row["event_accounting"].get("warning")
    )
    payload = {
        "version": V3_M10_SAME_STREAM_VERSION,
        "status": V3_M10_SAME_STREAM_STATUS,
        "graph_id": V3_M10_GRAPH_ID,
        "contract_key": V3_M10_CONTRACT_KEY,
        "parameters": {
            "point_count": int(point_count),
            "radius": float(radius),
            "component_threshold": int(component_threshold),
            "warmups": int(warmups),
            "repeats": int(repeats),
            "grouped_union_query_block_size": None,
            "grouped_union_direct_side_effect": bool(grouped_union_direct_side_effect),
        },
        "partner_rows": tuple(rows),
        "comparison": {
            "cupy_total_event_seconds_median": cupy_total,
            "numba_total_event_seconds_median": numba_total,
            "cupy_over_numba_event_ratio": cupy_total / numba_total if numba_total > 0 else None,
            "winner": "cupy" if cupy_total < numba_total else "numba",
            "signature_match": True,
            "same_stream_ready": all(bool(row["same_stream_ready"]) for row in rows),
            "true_zero_copy_ready": all(bool(row["true_zero_copy_ready"]) for row in rows),
            "event_accounting_status": (
                "succeeded_with_independent_median_accounting_warning"
                if event_accounting_warnings
                else "clean"
            ),
            "event_accounting_warning_count": len(event_accounting_warnings),
            "event_accounting_warnings": event_accounting_warnings,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "reason": (
                "This gate proves same-stream native-to-partner ordering for the named grouped-union "
                "handoff using CUDA events, but it does not include transfer-counter evidence; "
                "true-zero-copy and public speedup wording remain unauthorized."
            ),
        },
    }
    validate_v3_m10_same_stream_payload(payload)
    return payload


def build_v3_m10_same_stream_instrumentation(
    *,
    partner: str,
    hardware: str,
    prepare_seconds: float,
    host_run_seconds: float,
    native_event_seconds: float,
    partner_event_seconds: float,
    total_event_seconds: float,
    validation_seconds: float,
    data_ptrs: Mapping[str, int],
    metadata: Mapping[str, object],
    same_stream_evidence: Mapping[str, object],
) -> InstrumentationPacket:
    partner = str(partner)
    if partner not in V3_M10_PARTNERS:
        raise GraphValidationError("M10 instrumentation partner must be cupy or numba")
    event_id = f"{partner}_native_partner_cuda_event_pair"
    pointer_id = f"{partner}_device_pointer_record"
    native_id = f"{partner}_optix_native_handle_record"
    no_materialization_id = f"{partner}_no_materialization_during_event_window"
    host_timer_id = f"{partner}_host_timer_record"
    validation_id = f"{partner}_validation_timer_record"
    event_details = dict(same_stream_evidence)
    native_partner_sum_seconds = float(native_event_seconds) + float(partner_event_seconds)
    median_total_seconds = float(total_event_seconds)
    event_details["median_native_event_seconds"] = float(native_event_seconds)
    event_details["median_partner_event_seconds"] = float(partner_event_seconds)
    event_details["median_total_event_seconds"] = median_total_seconds
    event_details["median_native_plus_partner_seconds"] = native_partner_sum_seconds
    if median_total_seconds + 1.0e-9 < native_partner_sum_seconds:
        event_details["independent_median_accounting_warning"] = (
            "median(total_event) is smaller than median(native_event)+median(partner_event); "
            "these medians are computed independently and may come from different repeats"
        )
    evidence = (
        EvidenceRecord(
            evidence_id=event_id,
            kind="cuda_event_pair",
            backend="optix",
            phase="stream_handoff",
            source=str(event_details.get("evidence_source", "cuda_event_pair")),
            hardware=hardware,
            details=event_details,
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
            evidence_id=native_id,
            kind="backend_native_handle",
            backend="optix",
            phase="rt_traversal",
            source="prepared_optix_grouped_union_on_stream_metadata",
            hardware=hardware,
            details={
                "native_execution_path": metadata.get("native_execution_path"),
                "native_engine_row_contract": metadata.get("native_engine_row_contract"),
                "native_symbol": event_details.get("native_symbol"),
                "cuda_stream_ptr": event_details.get("cuda_stream_ptr"),
                "native_synchronized_before_return": event_details.get("native_synchronized_before_return"),
            },
        ),
        EvidenceRecord(
            evidence_id=no_materialization_id,
            kind="no_host_materialization",
            backend="optix",
            phase="continuation_or_reduction",
            source="adapter_event_window_contract",
            hardware=hardware,
            details={
                "validation_materialization_after_measured_window": bool(
                    event_details.get("validation_materialization_after_measured_window")
                ),
                "transfer_counter_observed": bool(event_details.get("transfer_counter_observed")),
                "true_zero_copy_ready": bool(event_details.get("true_zero_copy_ready")),
            },
        ),
        EvidenceRecord(
            evidence_id=host_timer_id,
            kind="host_timer",
            backend="optix",
            phase="host_wrapper",
            source="python_perf_counter_wrapper",
            hardware=hardware,
            details={"host_run_seconds_median": float(host_run_seconds)},
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
        "rt_traversal": (event_id, native_id),
        "stream_handoff": (event_id, pointer_id),
        "continuation_or_reduction": (event_id, no_materialization_id),
        "host_wrapper": (host_timer_id,),
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
            transfer_counter_observed=False,
            host_materialized=False,
            hidden_copy_observed=False,
            evidence_ids=(event_id, pointer_id, native_id, no_materialization_id),
        ),
    )
    packet = InstrumentationPacket(
        graph_id=V3_M10_GRAPH_ID,
        backend="optix",
        hardware=hardware,
        phase_timings=timings,
        evidence_records=evidence,
        residency_evidence=residency,
    )
    if float(total_event_seconds) + 1.0e-9 < max(float(native_event_seconds), float(partner_event_seconds)):
        raise GraphValidationError("total event time is smaller than an event component")
    return packet


def validate_v3_m10_same_stream_payload(payload: Mapping[str, object]) -> dict[str, object]:
    if payload.get("version") != V3_M10_SAME_STREAM_VERSION:
        raise GraphValidationError("unexpected M10 same-stream version")
    if payload.get("status") != V3_M10_SAME_STREAM_STATUS:
        raise GraphValidationError("unexpected M10 same-stream status")
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 2:
        raise GraphValidationError("M10 same-stream payload requires two partner rows")
    partners = {str(row["partner"]) for row in rows if isinstance(row, Mapping)}
    if partners != set(V3_M10_PARTNERS):
        raise GraphValidationError("M10 same-stream payload must include cupy and numba")
    for row in rows:
        if not isinstance(row, Mapping):
            raise GraphValidationError("M10 same-stream row must be a mapping")
        _validate_partner_row(row)
    signatures = {tuple(row["validation_signature"]) for row in rows}
    if len(signatures) != 1:
        raise GraphValidationError("M10 same-stream signatures must match")
    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping) or comparison.get("signature_match") is not True:
        raise GraphValidationError("M10 same-stream comparison must record signature_match=true")
    if comparison.get("same_stream_ready") is not True:
        raise GraphValidationError("M10 same-stream comparison must prove same_stream_ready=true")
    if comparison.get("true_zero_copy_ready") is not False:
        raise GraphValidationError("M10 same-stream must fail closed on true_zero_copy_ready without transfer counters")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M10 same-stream payload requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "same_stream_public_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
    ):
        if bool(boundary.get(key)):
            raise GraphValidationError(f"M10 same-stream payload must not authorize {key}")
    return {
        "status": V3_M10_SAME_STREAM_STATUS,
        "partner_count": len(rows),
        "signature_match": True,
        "same_stream_ready": True,
        "true_zero_copy_ready": False,
        "public_claim_authorized": False,
    }


def _validate_partner_row(row: Mapping[str, object]) -> None:
    partner = str(row.get("partner"))
    if partner not in V3_M10_PARTNERS:
        raise GraphValidationError("M10 same-stream row has unsupported partner")
    if bool(row.get("same_stream_ready")) is not True:
        raise GraphValidationError(f"{partner} row did not prove same_stream_ready")
    if bool(row.get("true_zero_copy_ready")) is not False:
        raise GraphValidationError(f"{partner} row must not claim true_zero_copy_ready")
    metadata = row.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise GraphValidationError(f"{partner} row requires metadata")
    evidence = metadata.get("same_stream_evidence", {})
    if not isinstance(evidence, Mapping):
        raise GraphValidationError(f"{partner} row requires same_stream_evidence")
    if evidence.get("evidence_source") not in {"cupy_cuda_event_pair", "numba_cuda_event_pair"}:
        raise GraphValidationError(f"{partner} same-stream evidence must be a CUDA event pair")
    if "native_optix_launch_to" not in str(evidence.get("event_pair_scope", "")):
        raise GraphValidationError(f"{partner} event pair does not name the native-to-partner handoff")
    stream_ptr = int(evidence.get("cuda_stream_ptr", 0) or 0)
    native_stream_ptr = int(evidence.get("native_metadata_cuda_stream_ptr", 0) or 0)
    if stream_ptr <= 0 or native_stream_ptr != stream_ptr:
        raise GraphValidationError(f"{partner} event stream pointer does not match native metadata")
    if bool(evidence.get("native_synchronized_before_return", True)):
        raise GraphValidationError(f"{partner} native wrapper synchronized before returning")
    if bool(evidence.get("validation_materialization_after_measured_window")) is not True:
        raise GraphValidationError(f"{partner} validation materialization boundary is missing")
    if float(evidence.get("native_event_ms", -1.0)) < 0.0:
        raise GraphValidationError(f"{partner} native event time must be non-negative")
    if float(evidence.get("partner_event_ms", -1.0)) < 0.0:
        raise GraphValidationError(f"{partner} partner event time must be non-negative")
    if float(evidence.get("total_event_ms", -1.0)) < float(evidence.get("native_event_ms", 0.0)):
        raise GraphValidationError(f"{partner} total event time is smaller than native event time")
    for sample in tuple(row.get("event_samples", ())):
        if not isinstance(sample, Mapping):
            raise GraphValidationError(f"{partner} event sample must be a mapping")
        native_seconds = float(sample.get("native_event_seconds", -1.0))
        partner_seconds = float(sample.get("partner_event_seconds", -1.0))
        total_seconds = float(sample.get("total_event_seconds", -1.0))
        if native_seconds < 0.0 or partner_seconds < 0.0 or total_seconds < 0.0:
            raise GraphValidationError(f"{partner} event sample has negative timing")
        if total_seconds + 1.0e-9 < max(native_seconds, partner_seconds):
            raise GraphValidationError(f"{partner} event sample total is smaller than a component")
        if sample.get("same_stream_ready") is not True:
            raise GraphValidationError(f"{partner} event sample did not prove same_stream_ready")
    if bool(evidence.get("transfer_counter_observed")):
        raise GraphValidationError(f"{partner} transfer counters are not part of M10 evidence")
    instrumentation = row.get("instrumentation", {})
    if isinstance(instrumentation, Mapping):
        readiness = instrumentation.get("claim_readiness", {})
        if isinstance(readiness, Mapping):
            if readiness.get("same_stream_ready") is not True:
                raise GraphValidationError(f"{partner} instrumentation did not prove same_stream_ready")
            if readiness.get("true_zero_copy_ready") is not False:
                raise GraphValidationError(f"{partner} instrumentation must not prove true_zero_copy_ready")
    if bool(row.get("public_claim_authorized")):
        raise GraphValidationError(f"{partner} row must not authorize public claims")


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
        raise GraphValidationError("unsupported M10 partner")
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
        event_samples = []
        last_result = None
        for _ in range(repeats):
            start = time.perf_counter()
            result = prepared.run_same_stream_evidence(
                min_neighbors=component_threshold,
                return_metadata=True,
            )
            host_elapsed = time.perf_counter() - start
            metadata = dict(result["metadata"])
            evidence = dict(metadata["same_stream_evidence"])
            host_samples.append(host_elapsed)
            native_event_samples.append(float(evidence["native_event_ms"]) / 1000.0)
            partner_event_samples.append(float(evidence["partner_event_ms"]) / 1000.0)
            total_event_samples.append(float(evidence["total_event_ms"]) / 1000.0)
            event_samples.append(
                {
                    "native_event_seconds": native_event_samples[-1],
                    "partner_event_seconds": partner_event_samples[-1],
                    "total_event_seconds": total_event_samples[-1],
                    "same_stream_ready": bool(evidence["same_stream_ready"]),
                }
            )
            last_result = result
        if last_result is None:
            raise GraphValidationError("M10 same-stream partner run produced no samples")

        validation_start = time.perf_counter()
        signature = _component_signature_from_columns(last_result["columns"])
        validation_seconds = time.perf_counter() - validation_start
        data_ptrs = _column_data_ptrs(last_result["columns"])
        metadata = dict(last_result["metadata"])
        same_stream_evidence = dict(metadata["same_stream_evidence"])
        instrumentation = build_v3_m10_same_stream_instrumentation(
            partner=partner,
            hardware=hardware,
            prepare_seconds=prepare_seconds,
            host_run_seconds=statistics.median(host_samples),
            native_event_seconds=statistics.median(native_event_samples),
            partner_event_seconds=statistics.median(partner_event_samples),
            total_event_seconds=statistics.median(total_event_samples),
            validation_seconds=validation_seconds,
            data_ptrs=data_ptrs,
            metadata=metadata,
            same_stream_evidence=same_stream_evidence,
        )
        event_accounting = _event_accounting_summary(
            instrumentation=instrumentation,
            native_event_seconds=statistics.median(native_event_samples),
            partner_event_seconds=statistics.median(partner_event_samples),
            total_event_seconds=statistics.median(total_event_samples),
        )
        return {
            "partner": partner,
            "backend": "optix",
            "host_samples_seconds": tuple(host_samples),
            "event_samples": tuple(event_samples),
            "host_median_seconds": statistics.median(host_samples),
            "host_min_seconds": min(host_samples),
            "host_max_seconds": max(host_samples),
            "native_event_seconds_median": statistics.median(native_event_samples),
            "partner_event_seconds_median": statistics.median(partner_event_samples),
            "total_event_seconds_median": statistics.median(total_event_samples),
            "prepare_seconds": prepare_seconds,
            "validation_seconds": validation_seconds,
            "validation_signature": signature,
            "device_data_ptrs": data_ptrs,
            "metadata": metadata,
            "same_stream_ready": bool(same_stream_evidence.get("same_stream_ready")),
            "true_zero_copy_ready": bool(same_stream_evidence.get("true_zero_copy_ready")),
            "event_accounting": event_accounting,
            "numba_cuda_compat_env": dict(compat_env) if partner == "numba" else None,
            "instrumentation": instrumentation.to_metadata(),
            "claim_readiness": instrumentation.claim_readiness,
            "public_claim_authorized": False,
        }
    finally:
        close = getattr(prepared, "close", None)
        if close is not None:
            close()


def _event_accounting_summary(
    *,
    instrumentation: InstrumentationPacket,
    native_event_seconds: float,
    partner_event_seconds: float,
    total_event_seconds: float,
) -> dict[str, object]:
    warning = ""
    for record in instrumentation.to_metadata()["evidence_records"]:
        if record["kind"] != "cuda_event_pair":
            continue
        details = record["details"]
        warning = str(details.get("independent_median_accounting_warning", ""))
        break
    return {
        "median_native_event_seconds": float(native_event_seconds),
        "median_partner_event_seconds": float(partner_event_seconds),
        "median_total_event_seconds": float(total_event_seconds),
        "median_native_plus_partner_seconds": float(native_event_seconds) + float(partner_event_seconds),
        "warning": warning,
        "status": "warning" if warning else "clean",
    }
