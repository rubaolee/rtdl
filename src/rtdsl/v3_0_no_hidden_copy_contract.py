from __future__ import annotations

from collections.abc import Mapping, Sequence
import ctypes
from pathlib import Path

from .v3_0_execution_graph import GraphValidationError


V3_NO_HIDDEN_COPY_CONTRACT_VERSION = "rtdl.v3_0.no_hidden_copy_contract.m12"
V3_NO_HIDDEN_COPY_CONTRACT_STATUS = "m12_app_agnostic_no_hidden_copy_contract_internal_claims_gated"
V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = 4096
V3_NO_HIDDEN_COPY_READINESS_SOURCE = "v3_m12_no_hidden_copy_transfer_counter_contract"
V3_NO_HIDDEN_COPY_FORBIDDEN_CLAIM_FLAGS = (
    "public_speedup_claim_authorized",
    "rt_core_speedup_claim_authorized",
    "same_stream_public_claim_authorized",
    "true_zero_copy_public_claim_authorized",
    "automatic_partner_selection_authorized",
)


class _TransferCounterSnapshot(ctypes.Structure):
    _fields_ = [
        ("enabled", ctypes.c_uint64),
        ("total_calls", ctypes.c_uint64),
        ("total_bytes", ctypes.c_uint64),
        ("host_to_device_calls", ctypes.c_uint64),
        ("host_to_device_bytes", ctypes.c_uint64),
        ("device_to_host_calls", ctypes.c_uint64),
        ("device_to_host_bytes", ctypes.c_uint64),
        ("device_to_device_calls", ctypes.c_uint64),
        ("device_to_device_bytes", ctypes.c_uint64),
        ("unknown_calls", ctypes.c_uint64),
        ("unknown_bytes", ctypes.c_uint64),
    ]


class CudaTransferCounter:
    """ctypes wrapper for the LD_PRELOAD CUDA transfer counter."""

    def __init__(self, library_path: str | Path):
        self.library_path = str(library_path)
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.rtdl_cuda_transfer_counter_reset.argtypes = []
        self._lib.rtdl_cuda_transfer_counter_reset.restype = None
        self._lib.rtdl_cuda_transfer_counter_set_enabled.argtypes = [ctypes.c_int]
        self._lib.rtdl_cuda_transfer_counter_set_enabled.restype = None
        self._lib.rtdl_cuda_transfer_counter_is_enabled.argtypes = []
        self._lib.rtdl_cuda_transfer_counter_is_enabled.restype = ctypes.c_uint64
        self._lib.rtdl_cuda_transfer_counter_snapshot.argtypes = [
            ctypes.POINTER(_TransferCounterSnapshot)
        ]
        self._lib.rtdl_cuda_transfer_counter_snapshot.restype = None
        self._lib.rtdl_cuda_transfer_counter_version.argtypes = []
        self._lib.rtdl_cuda_transfer_counter_version.restype = ctypes.c_char_p

    @property
    def version(self) -> str:
        value = self._lib.rtdl_cuda_transfer_counter_version()
        return value.decode("utf-8") if value else "unknown"

    def reset(self) -> None:
        self._lib.rtdl_cuda_transfer_counter_reset()

    def enable(self) -> None:
        self._lib.rtdl_cuda_transfer_counter_set_enabled(1)

    def disable_and_snapshot(self) -> dict[str, object]:
        self._lib.rtdl_cuda_transfer_counter_set_enabled(0)
        snapshot = _TransferCounterSnapshot()
        self._lib.rtdl_cuda_transfer_counter_snapshot(ctypes.byref(snapshot))
        return {
            "counter_version": self.version,
            "library_path": self.library_path,
            "enabled": int(snapshot.enabled),
            "total_calls": int(snapshot.total_calls),
            "total_bytes": int(snapshot.total_bytes),
            "host_to_device_calls": int(snapshot.host_to_device_calls),
            "host_to_device_bytes": int(snapshot.host_to_device_bytes),
            "device_to_host_calls": int(snapshot.device_to_host_calls),
            "device_to_host_bytes": int(snapshot.device_to_host_bytes),
            "device_to_device_calls": int(snapshot.device_to_device_calls),
            "device_to_device_bytes": int(snapshot.device_to_device_bytes),
            "unknown_calls": int(snapshot.unknown_calls),
            "unknown_bytes": int(snapshot.unknown_bytes),
        }


def min_named_column_bytes_from_descriptors(columns: Mapping[str, object] | Sequence[object]) -> int:
    """Return the smallest declared named-column byte size.

    Accepted descriptor shapes are intentionally small and app-agnostic:
    an integer byte count, a mapping with ``byte_count``/``bytes``/``nbytes``,
    or a mapping with ``row_count`` plus ``element_size``/``itemsize``.
    """

    descriptors = columns.values() if isinstance(columns, Mapping) else columns
    byte_counts = []
    for descriptor in descriptors:
        byte_count = _descriptor_byte_count(descriptor)
        if byte_count is not None:
            byte_counts.append(byte_count)
    if not byte_counts:
        raise GraphValidationError("no named column byte sizes were declared")
    return min(byte_counts)


def classify_no_hidden_copy_transfer_snapshot(
    snapshot: Mapping[str, object],
    *,
    min_named_column_bytes: int,
    allowed_non_column_host_to_device_bytes: int = (
        V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
    ),
    measured_window: str = "native_to_partner_continuation",
    readiness_source: str = V3_NO_HIDDEN_COPY_READINESS_SOURCE,
) -> dict[str, object]:
    if not isinstance(snapshot, Mapping):
        raise GraphValidationError("transfer counter snapshot must be a mapping")
    min_named_column_bytes = int(min_named_column_bytes)
    if min_named_column_bytes <= 0:
        raise GraphValidationError("min_named_column_bytes must be positive")
    allowed_h2d = int(allowed_non_column_host_to_device_bytes)
    if allowed_h2d < 0:
        raise GraphValidationError("allowed_non_column_host_to_device_bytes must be non-negative")

    host_to_device_bytes = _snapshot_int(snapshot, "host_to_device_bytes")
    device_to_host_calls = _snapshot_int(snapshot, "device_to_host_calls")
    device_to_device_calls = _snapshot_int(snapshot, "device_to_device_calls")
    unknown_calls = _snapshot_int(snapshot, "unknown_calls")
    disallowed_reasons = []
    if device_to_host_calls:
        disallowed_reasons.append("device_to_host_copy_observed")
    if device_to_device_calls:
        disallowed_reasons.append("device_to_device_copy_observed")
    if unknown_calls:
        disallowed_reasons.append("unknown_direction_copy_observed")
    if host_to_device_bytes > allowed_h2d:
        disallowed_reasons.append("host_to_device_bytes_exceed_allowed_launch_parameter_scope")
    if host_to_device_bytes >= min_named_column_bytes:
        disallowed_reasons.append("host_to_device_bytes_reach_named_column_size")
    hidden_copy_observed = bool(disallowed_reasons)
    return {
        "contract_version": V3_NO_HIDDEN_COPY_CONTRACT_VERSION,
        "contract_status": V3_NO_HIDDEN_COPY_CONTRACT_STATUS,
        "transfer_counter_observed": True,
        "readiness_source": readiness_source,
        "measured_window": str(measured_window),
        "allowed_non_column_host_to_device_bytes": allowed_h2d,
        "min_named_column_bytes": min_named_column_bytes,
        "observed_total_calls": _snapshot_int(snapshot, "total_calls"),
        "observed_total_bytes": _snapshot_int(snapshot, "total_bytes"),
        "observed_host_to_device_calls": _snapshot_int(snapshot, "host_to_device_calls"),
        "observed_host_to_device_bytes": host_to_device_bytes,
        "observed_device_to_host_calls": device_to_host_calls,
        "observed_device_to_host_bytes": _snapshot_int(snapshot, "device_to_host_bytes"),
        "observed_device_to_device_calls": device_to_device_calls,
        "observed_device_to_device_bytes": _snapshot_int(snapshot, "device_to_device_bytes"),
        "observed_unknown_calls": unknown_calls,
        "observed_unknown_bytes": _snapshot_int(snapshot, "unknown_bytes"),
        "allowed_transfer_scope": (
            "no device-to-host/device-to-device/unknown copies; host-to-device bytes may only cover "
            "small non-column setup such as native launch parameters, not named handoff or output columns"
        ),
        "hidden_copy_observed": hidden_copy_observed,
        "disallowed_reasons": tuple(disallowed_reasons),
        "no_hidden_column_copy_ready": not hidden_copy_observed,
        "true_zero_copy_ready": not hidden_copy_observed,
    }


def summarize_no_hidden_copy_classifications(
    classifications: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    rows = tuple(classifications)
    if not rows:
        raise GraphValidationError("no no-hidden-copy classifications were provided")
    ready = all(bool(row.get("no_hidden_column_copy_ready")) for row in rows)
    return {
        "contract_version": V3_NO_HIDDEN_COPY_CONTRACT_VERSION,
        "sample_count": len(rows),
        "no_hidden_column_copy_ready": ready,
        "true_zero_copy_ready": ready,
        "max_observed_host_to_device_bytes": max(
            int(row.get("observed_host_to_device_bytes", 0) or 0) for row in rows
        ),
        "max_observed_total_bytes": max(int(row.get("observed_total_bytes", 0) or 0) for row in rows),
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


def annotate_no_hidden_copy_metadata(
    metadata: Mapping[str, object],
    classification: Mapping[str, object],
    *,
    all_samples_ready: bool | None = None,
    readiness_source: str | None = None,
) -> dict[str, object]:
    annotated = dict(metadata)
    evidence = dict(annotated.get("same_stream_evidence") or {})
    ready = (
        bool(classification.get("no_hidden_column_copy_ready"))
        if all_samples_ready is None
        else bool(all_samples_ready)
    )
    evidence.update(
        {
            "no_hidden_column_copy_ready": ready,
            "true_zero_copy_ready": ready,
            "true_zero_copy_readiness_source": readiness_source
            or str(classification.get("readiness_source") or V3_NO_HIDDEN_COPY_READINESS_SOURCE),
            "allowed_non_column_host_to_device_bytes": int(
                classification.get("allowed_non_column_host_to_device_bytes", 0) or 0
            ),
            "min_named_column_bytes": int(classification.get("min_named_column_bytes", 0) or 0),
            "no_hidden_copy_contract_version": V3_NO_HIDDEN_COPY_CONTRACT_VERSION,
        }
    )
    annotated["same_stream_evidence"] = evidence
    return annotated


def validate_no_hidden_copy_row(
    row: Mapping[str, object],
    *,
    allowed_partners: Sequence[str] | None = None,
    row_label: str = "row",
) -> dict[str, object]:
    if not isinstance(row, Mapping):
        raise GraphValidationError(f"{row_label} must be a mapping")
    partner = str(row.get("partner", row_label))
    if allowed_partners is not None and partner not in set(str(item) for item in allowed_partners):
        raise GraphValidationError(f"{partner} row has unsupported partner")
    for key in (
        "same_stream_ready",
        "transfer_counter_observed",
        "no_hidden_column_copy_ready",
        "true_zero_copy_ready",
    ):
        if row.get(key) is not True:
            raise GraphValidationError(f"{partner} row must prove {key}=true")

    classification = row.get("transfer_counter_classification", {})
    validate_no_hidden_copy_classification(classification, row_label=partner)
    metadata = row.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise GraphValidationError(f"{partner} row requires metadata")
    evidence = metadata.get("same_stream_evidence", {})
    if not isinstance(evidence, Mapping):
        raise GraphValidationError(f"{partner} row requires same_stream_evidence")
    if evidence.get("transfer_counter_observed") is not True:
        raise GraphValidationError(f"{partner} same-stream evidence must include a transfer counter")
    if evidence.get("transfer_counter_snapshot") is None:
        raise GraphValidationError(f"{partner} row missing transfer counter snapshot")
    if evidence.get("true_zero_copy_ready") is not True:
        raise GraphValidationError(f"{partner} same-stream evidence must prove true_zero_copy_ready")

    instrumentation = row.get("instrumentation", {})
    if isinstance(instrumentation, Mapping):
        readiness = instrumentation.get("claim_readiness", {})
        if isinstance(readiness, Mapping):
            if readiness.get("same_stream_ready") is not True:
                raise GraphValidationError(f"{partner} instrumentation did not prove same_stream_ready")
            if readiness.get("true_zero_copy_ready") is not True:
                raise GraphValidationError(f"{partner} instrumentation did not prove true_zero_copy_ready")
    if bool(row.get("public_claim_authorized")):
        raise GraphValidationError(f"{partner} row must not authorize public claims")
    return {
        "partner": partner,
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "no_hidden_column_copy_ready": True,
        "true_zero_copy_ready": True,
        "public_claim_authorized": False,
    }


def validate_no_hidden_copy_payload(
    payload: Mapping[str, object],
    *,
    expected_version: str | None = None,
    expected_status: str | None = None,
    required_partners: Sequence[str] | None = None,
    require_signature_match: bool = True,
    forbidden_claim_flags: Sequence[str] = V3_NO_HIDDEN_COPY_FORBIDDEN_CLAIM_FLAGS,
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("no-hidden-copy payload must be a mapping")
    if expected_version is not None and payload.get("version") != expected_version:
        raise GraphValidationError("unexpected no-hidden-copy payload version")
    if expected_status is not None and payload.get("status") != expected_status:
        raise GraphValidationError("unexpected no-hidden-copy payload status")
    rows = tuple(payload.get("partner_rows", ()))
    if not rows:
        raise GraphValidationError("no-hidden-copy payload requires partner rows")
    partners = {str(row["partner"]) for row in rows if isinstance(row, Mapping)}
    if required_partners is not None and partners != set(str(item) for item in required_partners):
        raise GraphValidationError("no-hidden-copy payload partner set mismatch")
    if require_signature_match:
        signatures = {tuple(row["validation_signature"]) for row in rows if isinstance(row, Mapping)}
        if len(signatures) != 1:
            raise GraphValidationError("no-hidden-copy payload signatures must match")
    for row in rows:
        validate_no_hidden_copy_row(row, allowed_partners=required_partners)

    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping):
        raise GraphValidationError("no-hidden-copy payload requires comparison")
    for key in (
        "same_stream_ready",
        "transfer_counter_observed",
        "no_hidden_column_copy_ready",
        "true_zero_copy_ready",
    ):
        if comparison.get(key) is not True:
            raise GraphValidationError(f"no-hidden-copy comparison must prove {key}=true")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("no-hidden-copy payload requires claim boundary")
    for key in forbidden_claim_flags:
        if bool(boundary.get(str(key))):
            raise GraphValidationError(f"no-hidden-copy payload must not authorize {key}")
    return {
        "status": payload.get("status") or V3_NO_HIDDEN_COPY_CONTRACT_STATUS,
        "partner_count": len(rows),
        "signature_match": True,
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "no_hidden_column_copy_ready": True,
        "true_zero_copy_ready": True,
        "public_claim_authorized": False,
    }


def validate_no_hidden_copy_classification(
    classification: Mapping[str, object],
    *,
    row_label: str = "row",
) -> None:
    if not isinstance(classification, Mapping):
        raise GraphValidationError(f"{row_label} row requires transfer counter classification")
    if classification.get("hidden_copy_observed") is not False:
        raise GraphValidationError(f"{row_label} row observed a hidden copy")
    for key in (
        "transfer_counter_observed",
        "no_hidden_column_copy_ready",
        "true_zero_copy_ready",
    ):
        if classification.get(key) is not True:
            raise GraphValidationError(f"{row_label} classification must prove {key}=true")
    if int(classification.get("observed_device_to_host_calls", 0) or 0) != 0:
        raise GraphValidationError(f"{row_label} row observed device-to-host copies")
    if int(classification.get("observed_device_to_device_calls", 0) or 0) != 0:
        raise GraphValidationError(f"{row_label} row observed device-to-device copies")
    if int(classification.get("observed_unknown_calls", 0) or 0) != 0:
        raise GraphValidationError(f"{row_label} row observed unknown-direction copies")
    if int(classification.get("observed_host_to_device_bytes", 0) or 0) > int(
        classification.get("allowed_non_column_host_to_device_bytes", 0) or 0
    ):
        raise GraphValidationError(f"{row_label} row observed too many host-to-device bytes")
    if int(classification.get("observed_host_to_device_bytes", 0) or 0) >= int(
        classification.get("min_named_column_bytes", 0) or 0
    ):
        raise GraphValidationError(f"{row_label} row observed host-to-device bytes at named-column scale")


def _snapshot_int(snapshot: Mapping[str, object], key: str) -> int:
    value = snapshot.get(key, 0)
    return int(value or 0)


def _descriptor_byte_count(descriptor: object) -> int | None:
    if isinstance(descriptor, int):
        return int(descriptor)
    if isinstance(descriptor, Mapping):
        for key in ("byte_count", "bytes", "nbytes"):
            if key in descriptor and descriptor[key] is not None:
                return int(descriptor[key])
        if "row_count" in descriptor:
            element_size = descriptor.get("element_size", descriptor.get("itemsize"))
            if element_size is not None:
                return int(descriptor["row_count"]) * int(element_size)
    return None
