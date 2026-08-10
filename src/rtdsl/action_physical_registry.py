from __future__ import annotations

from dataclasses import dataclass, field, replace
import ctypes
import ctypes.util
import functools
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Mapping

from .action_api import (
    ActionProducerKind,
    ActionTargetProfile,
    BoundAction,
    LoweredAction,
    PlannedLoweredAction,
    _reseal_planned_lowered_action,
    lower_action,
)
from .action_ir import ExtentKind, verify_action_spec
from .action_native_identity import (
    ACTION_POINT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS,
    ACTION_NATIVE_LIBRARY_IDENTITY_VERSION,
    ACTION_NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION,
    ActionNativeLibraryIdentity,
    CANDIDATE_PRUNED_EXACT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS,
    PREPARED_RANKED_DISTANCE_WINDOW_3D_REQUIRED_SYMBOLS,
    native_library_identity as _shared_native_library_identity,
    probe_native_template_symbols as _shared_probe_native_template_symbols,
    validate_native_library_identity,
)
from .action_placement import (
    ActionBackendCapability,
    ActionBackendCostCalibration,
    ActionCalibrationMode,
    ActionCostFeatures,
    ActionPlacementKind,
    ActionStateStorage,
    ActionTransferAccounting,
    plan_action_placement,
)


ACTION_PHYSICAL_REGISTRY_VERSION = "rtdl.action_physical_registry.private_candidate.v5"
_CALIBRATION_VERSION = "rtdl.point_bounded_selection_exact_observed.v1"
_REPRESENTATION = "packed_point_records_and_bounded_rank_columns.v1"
_GRID_BACKEND = "ranked_window_qk"
_FUSED_BACKEND = "optix"
_PRUNED_BACKEND = "candidate_pruned_grid"
_CONSENSUS_POLICY_VERSION = (
    "rtdl.point_bounded_selection_sampled_route_direction_consensus.v3"
)
_NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION = (
    ACTION_NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION
)
_NATIVE_LIBRARY_IDENTITY_VERSION = ACTION_NATIVE_LIBRARY_IDENTITY_VERSION
_DEFAULT_FIXED_PRIORITY_LEGAL_ORDER = (_FUSED_BACKEND, _GRID_BACKEND)
_CANDIDATE_PRUNED_FIXED_PRIORITY_LEGAL_ORDER = (
    _PRUNED_BACKEND,
    _FUSED_BACKEND,
    _GRID_BACKEND,
)
_RUNTIME_DIRECTION_POLICY = {
    "minimum_distinct_hardware": 2,
    "minimum_controlled_modern_exact_observations": 1,
    "minimum_functional_direction_observations": 1,
    "minimum_loser_over_winner_ratio": 1.5,
}
_ROUTE_DIRECTION_CERTIFICATE_RELATIVE_PATH = (
    "history/internal_docs/"
    "point_bounded_selection_route_direction_certificate_2026-07-19.json"
)
_ROUTE_DIRECTION_CERTIFICATE_SHA256 = (
    "79efa447d2ec7c6acafc79c61b9716c7a0e273a8d5305e3562f8e1a91993f3cf"
)
_QK_REQUIRED_NATIVE_SYMBOLS = PREPARED_RANKED_DISTANCE_WINDOW_3D_REQUIRED_SYMBOLS
_FUSED_REQUIRED_NATIVE_SYMBOLS = ACTION_POINT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS
_PRUNED_REQUIRED_NATIVE_SYMBOLS = (
    CANDIDATE_PRUNED_EXACT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS
)
_FINGERPRINT_SAMPLE_LIMIT = 4_096
_NO_EVIDENCE_DIGEST = hashlib.sha256(
    b"rtdl.action_physical_registry.no_matching_calibration.v1"
).hexdigest()


@dataclass(frozen=True)
class _TrustedPointCalibration:
    hardware_key: str
    workload_fingerprint_digest: str
    source_exact_workload_identity_digest: str
    candidate_density: float
    fused_observed_total_seconds: float
    grid_observed_total_seconds: float
    source_evidence_digest: str
    source_evidence_path: str
    observation_id: str
    route_direction_certificate_digest: str
    controlled_modern_exact_observation: bool
    functional_only: bool
    direction_consensus_eligible: bool
    winner_backend: str
    clear_margin_threshold_met: bool
    limit: int
    minimum_distance_hex: str
    maximum_distance_hex: str
    minimum_boundary: str
    maximum_boundary: str
    expected_query_batches: int
    module_ready: bool
    index_ready: bool


@dataclass(frozen=True)
class _PointPhysicalIdentity:
    limit: int
    minimum_distance_hex: str
    maximum_distance_hex: str
    minimum_boundary: str
    maximum_boundary: str
    expected_query_batches: int = 1
    module_ready: bool = False
    index_ready: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "limit": self.limit,
            "minimum_distance_hex": self.minimum_distance_hex,
            "maximum_distance_hex": self.maximum_distance_hex,
            "minimum_boundary": self.minimum_boundary,
            "maximum_boundary": self.maximum_boundary,
            "expected_query_batches": self.expected_query_batches,
            "module_ready": self.module_ready,
            "index_ready": self.index_ready,
        }

    @property
    def digest(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("ascii")).hexdigest()


@dataclass(frozen=True)
class _NativeSymbolProbe:
    attempted: bool
    available: bool
    required_symbols: tuple[str, ...]
    missing_symbols: tuple[str, ...] = ()
    library_path: str | None = None
    library_identity: Mapping[str, object] | None = None
    error: str | None = None
    _library_identity_object: ActionNativeLibraryIdentity | None = field(
        default=None, repr=False, compare=False
    )
    _library_ref: object | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": _NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION,
            "attempted": self.attempted,
            "available": self.available,
            "required_symbols": list(self.required_symbols),
            "missing_symbols": list(self.missing_symbols),
            "library_path": self.library_path,
            "library_identity": (
                dict(self.library_identity)
                if self.library_identity is not None
                else None
            ),
            "error": self.error,
            "availability_derived_from_target_optix_flag_only": False,
        }


# Each point binds exact hardware, sampled and full packed identities, the full
# physical parameter identity, and one immutable evidence digest. Any mismatch
# deliberately makes the cost model fall back as a whole.
_TRUSTED_EXACT_POINT_CALIBRATIONS: tuple[_TrustedPointCalibration, ...] = (
    _TrustedPointCalibration(
        hardware_key="nvidia_geforce_gtx_1070__cc_6_1__optix_9_0_0",
        workload_fingerprint_digest=(
            "cb8f2bb3471acd58fb726a1157242449b8585e9768b13e77919b416e47c083a8"
        ),
        source_exact_workload_identity_digest=(
            "28d4cb1392c48328d7daf1f36f4205ad06875e57deecd8387a042e8b70d8b07e"
        ),
        candidate_density=646_391_723 / (12_000_000 * 4_096),
        fused_observed_total_seconds=12.296839078480843,
        grid_observed_total_seconds=7.146094559924677,
        source_evidence_digest=(
            "1ff254ba009389680f33690773f271ad24d4571ec8afcef18e9465852960e194"
        ),
        source_evidence_path=(
            "history/internal_docs/"
            "goal5624_current_source_bootstrap_calibration_home_linux.json"
        ),
        observation_id="functional_goal5624_bootstrap",
        route_direction_certificate_digest=_ROUTE_DIRECTION_CERTIFICATE_SHA256,
        controlled_modern_exact_observation=False,
        functional_only=True,
        direction_consensus_eligible=True,
        winner_backend=_GRID_BACKEND,
        clear_margin_threshold_met=True,
        limit=4,
        minimum_distance_hex=float(0.0).hex(),
        maximum_distance_hex=float(2.0).hex(),
        minimum_boundary="open",
        maximum_boundary="open",
        expected_query_batches=1,
        module_ready=False,
        index_ready=False,
    ),
    _TrustedPointCalibration(
        hardware_key="nvidia_rtx_4000_ada_generation__cc_8_9__optix_8_0_0",
        workload_fingerprint_digest=(
            "cb8f2bb3471acd58fb726a1157242449b8585e9768b13e77919b416e47c083a8"
        ),
        source_exact_workload_identity_digest=(
            "28d4cb1392c48328d7daf1f36f4205ad06875e57deecd8387a042e8b70d8b07e"
        ),
        candidate_density=646_391_723 / (12_000_000 * 4_096),
        fused_observed_total_seconds=5.011668618768454,
        grid_observed_total_seconds=2.3794553223997355,
        source_evidence_digest=(
            "f1ac5afb5fce1333524565c22b2f858b55d8bbbac24ad602b060a02cf894cd12"
        ),
        source_evidence_path=(
            "history/internal_docs/goal5615_current_source_modern_gpu_runtime_no_go.json"
        ),
        observation_id="controlled_modern_goal5615",
        route_direction_certificate_digest=_ROUTE_DIRECTION_CERTIFICATE_SHA256,
        controlled_modern_exact_observation=True,
        functional_only=False,
        direction_consensus_eligible=True,
        winner_backend=_GRID_BACKEND,
        clear_margin_threshold_met=True,
        limit=4,
        minimum_distance_hex=float(0.0).hex(),
        maximum_distance_hex=float(2.0).hex(),
        minimum_boundary="open",
        maximum_boundary="open",
        expected_query_batches=1,
        module_ready=False,
        index_ready=False,
    ),
)


def packed_point_workload_identity(search_points, query_points) -> str:
    """Bind one physical-plan decision to exact packed input bytes."""

    search_digest = _packed_point_identity(search_points)
    query_digest = _packed_point_identity(query_points)
    return _combine_packed_point_identities(search_digest, query_digest)


def _combine_packed_point_identities(search_digest: str, query_digest: str) -> str:
    digest = hashlib.sha256(b"rtdl.packed_point_workload_identity.v2\x00")
    digest.update(bytes.fromhex(search_digest))
    digest.update(bytes.fromhex(query_digest))
    return digest.hexdigest()


def packed_point_workload_fingerprint(search_points, query_points) -> str:
    """Compute a cheap compiler-owned cost fingerprint, never a semantic proof."""

    search_digest = _packed_point_sample_fingerprint(search_points)
    query_digest = _packed_point_sample_fingerprint(query_points)
    digest = hashlib.sha256(b"rtdl.packed_point_workload_fingerprint.v1\x00")
    digest.update(bytes.fromhex(search_digest))
    digest.update(bytes.fromhex(query_digest))
    return digest.hexdigest()


def _validated_packed_point_records(packed):
    """Return one exact native point layout after bounded structural checks."""

    from .embree_runtime import PackedPoints, _RtdlPoint, _RtdlPoint3D

    if type(packed) is not PackedPoints:
        raise TypeError("compiler physical planning requires PackedPoints")
    if not isinstance(packed.count, int) or isinstance(packed.count, bool):
        raise TypeError("packed point count must be an integer")
    if not isinstance(packed.dimension, int) or isinstance(packed.dimension, bool):
        raise TypeError("packed point dimension must be an integer")
    count = packed.count
    dimension = packed.dimension
    if count < 0:
        raise ValueError("packed point count must be nonnegative")
    if dimension not in {2, 3}:
        raise ValueError("packed point dimension must be 2 or 3")
    records = packed.records
    if not isinstance(records, ctypes.Array):
        raise TypeError("packed point records must be a ctypes array")
    if len(records) != count:
        raise ValueError("packed point record length differs from count")
    expected_record_type = _RtdlPoint3D if dimension == 3 else _RtdlPoint
    if getattr(type(records), "_type_", None) is not expected_record_type:
        raise TypeError("packed point record type differs from the native ABI")
    return records, count, dimension


def _packed_point_storage_binding(packed) -> dict[str, object]:
    """Bind the exact native storage object separately from sampled content."""

    records, count, dimension = _validated_packed_point_records(packed)
    record_type = type(records)._type_
    return {
        "contract": "rtdl.packed_point_storage_binding.v1",
        "packed_object_id": id(packed),
        "records_object_id": id(records),
        "records_address": ctypes.addressof(records),
        "records_type": f"{type(records).__module__}.{type(records).__qualname__}",
        "record_element_type": (
            f"{record_type.__module__}.{record_type.__qualname__}"
        ),
        "record_element_size": ctypes.sizeof(record_type),
        "records_byte_size": ctypes.sizeof(records),
        "count": count,
        "dimension": dimension,
    }


def _packed_point_identity(packed) -> str:
    import numpy as np

    packed_records, count, dimension = _validated_packed_point_records(packed)
    records = np.ctypeslib.as_array(packed_records)
    digest = hashlib.sha256(b"rtdl.packed_point_identity.v1\x00")
    digest.update(count.to_bytes(8, "little", signed=False))
    digest.update(dimension.to_bytes(4, "little", signed=False))
    for field_name in records.dtype.names or ():
        field = np.ascontiguousarray(records[field_name])
        digest.update(field_name.encode("ascii") + b"\x00")
        digest.update(field.dtype.str.encode("ascii") + b"\x00")
        digest.update(int(field.shape[0]).to_bytes(8, "little", signed=False))
        digest.update(field.tobytes(order="C"))
    return digest.hexdigest()


def _packed_point_sample_fingerprint(packed) -> str:
    import numpy as np

    packed_records, count, dimension = _validated_packed_point_records(packed)
    records = np.ctypeslib.as_array(packed_records)
    sample_count = min(count, _FINGERPRINT_SAMPLE_LIMIT)
    if sample_count == 0:
        indices = np.empty(0, dtype=np.uint64)
    elif sample_count == 1:
        indices = np.asarray([0], dtype=np.uint64)
    else:
        indices = (
            np.arange(sample_count, dtype=np.uint64) * np.uint64(count - 1)
        ) // np.uint64(sample_count - 1)
    digest = hashlib.sha256(b"rtdl.packed_point_sample_fingerprint.v1\x00")
    digest.update(count.to_bytes(8, "little", signed=False))
    digest.update(dimension.to_bytes(4, "little", signed=False))
    digest.update(sample_count.to_bytes(4, "little", signed=False))
    digest.update(indices.tobytes(order="C"))
    for field_name in records.dtype.names or ():
        field = np.ascontiguousarray(records[field_name][indices])
        digest.update(field_name.encode("ascii") + b"\x00")
        digest.update(field.dtype.str.encode("ascii") + b"\x00")
        digest.update(field.tobytes(order="C"))
    return digest.hexdigest()


@functools.lru_cache(maxsize=1)
def _cuda_driver_device_identity() -> tuple[str, int, int]:
    """Read device identity for offline evidence generation.

    CUDA driver initialization is required by this explicit offline utility.
    Runtime registered placement does not call it and does not query hardware
    identity, because its only performance hint is cross-hardware direction.
    """

    from .optix_runtime import _ensure_cuda_driver_initialized

    _ensure_cuda_driver_initialized()
    library_name = ctypes.util.find_library("cuda") or "libcuda.so.1"
    try:
        cuda = ctypes.CDLL(library_name)
    except OSError as exc:
        raise RuntimeError(
            "CUDA driver library is required for compiler target identity"
        ) from exc

    device = ctypes.c_int()
    cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceGet.restype = ctypes.c_int
    status = int(cuda.cuDeviceGet(ctypes.byref(device), 0))
    if status != 0:
        raise RuntimeError(
            f"CUDA device 0 lookup failed with cuDeviceGet status {status}"
        )

    name_buffer = ctypes.create_string_buffer(256)
    cuda.cuDeviceGetName.argtypes = [
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_int,
        ctypes.c_int,
    ]
    cuda.cuDeviceGetName.restype = ctypes.c_int
    status = int(cuda.cuDeviceGetName(name_buffer, len(name_buffer), device.value))
    if status != 0:
        raise RuntimeError(
            f"CUDA device-name query failed with cuDeviceGetName status {status}"
        )
    try:
        name = name_buffer.value.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RuntimeError("CUDA device name is not valid UTF-8") from exc
    if not name:
        raise RuntimeError("CUDA device name is empty")

    # Stable CUdevice_attribute enum values from the CUDA Driver API.
    compute_capability_major = 75
    compute_capability_minor = 76
    cuda.cuDeviceGetAttribute.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_int,
        ctypes.c_int,
    ]
    cuda.cuDeviceGetAttribute.restype = ctypes.c_int

    def attribute(attribute_id: int, label: str) -> int:
        value = ctypes.c_int()
        result = int(
            cuda.cuDeviceGetAttribute(
                ctypes.byref(value), attribute_id, device.value
            )
        )
        if result != 0 or value.value < 0:
            raise RuntimeError(
                f"CUDA {label} query failed with cuDeviceGetAttribute status "
                f"{result}"
            )
        return int(value.value)

    return (
        name,
        attribute(compute_capability_major, "compute-capability major"),
        attribute(compute_capability_minor, "compute-capability minor"),
    )


def compiler_hardware_calibration_key() -> str:
    """Derive an offline calibration key from compiler-probed device facts."""

    from .optix_runtime import optix_version

    name, major, minor = _cuda_driver_device_identity()
    normalized_name = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    version = "_".join(str(int(item)) for item in optix_version())
    return f"{normalized_name}__cc_{major}_{minor}__optix_{version}"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repository_evidence_path(relative_path: str) -> Path:
    root = Path(__file__).resolve().parents[2]
    candidate = (root / relative_path).resolve(strict=True)
    if root != candidate and root not in candidate.parents:
        raise RuntimeError("route certificate evidence path escapes repository")
    if not candidate.is_file() or candidate.is_symlink():
        raise RuntimeError("route certificate evidence path is not a regular file")
    return candidate


def _validated_route_direction_certificate(
    rows: tuple[_TrustedPointCalibration, ...] | None = None,
) -> dict[str, object]:
    """Recompute the closed successor certificate and all evidence hashes.

    The returned payload is trusted only for winner *direction*. Observed
    seconds remain exact observations on their recorded hardware and are never
    synthesized for a different target.
    """

    registered = _TRUSTED_EXACT_POINT_CALIBRATIONS if rows is None else rows
    certificate_path = _repository_evidence_path(
        _ROUTE_DIRECTION_CERTIFICATE_RELATIVE_PATH
    )
    certificate_digest = _sha256_file(certificate_path)
    if certificate_digest != _ROUTE_DIRECTION_CERTIFICATE_SHA256:
        raise RuntimeError("route direction certificate SHA-256 changed")
    payload = json.loads(certificate_path.read_text(encoding="utf-8"))
    if payload.get("schema") != (
        "rtdl.point_bounded_selection.route_direction_certificate.v1"
    ):
        raise RuntimeError("route direction certificate schema changed")
    policy = payload.get("policy")
    if not isinstance(policy, dict) or policy != {
        "actual_seconds_must_not_be_transferred_to_unknown_hardware": True,
        "all_eligible_observations_must_have_same_clear_winner": True,
        "default_when_ineligible": [_FUSED_BACKEND, _GRID_BACKEND],
        "minimum_controlled_modern_exact_observations": 1,
        "minimum_distinct_hardware": 2,
        "minimum_functional_direction_observations": 1,
        "minimum_loser_over_winner_ratio": 1.5,
        "only_winner_direction_may_change_fixed_priority": True,
    }:
        raise RuntimeError("route direction certificate policy changed")
    if payload.get("claim_boundary") != {
        "cross_hardware_seconds_extrapolation_authorized": False,
        "publication_performance_claimed": False,
        "placement_heuristic_only": True,
        "runtime_speedup_claimed": False,
    }:
        raise RuntimeError("route direction certificate claim boundary changed")

    evidence_digests: dict[str, str] = {}
    observations = payload.get("observations")
    if not isinstance(observations, list) or len(observations) != len(registered):
        raise RuntimeError("route direction certificate observation count changed")
    observations_by_id: dict[str, dict[str, object]] = {}
    for observation in observations:
        if not isinstance(observation, dict):
            raise RuntimeError("route direction certificate observation is invalid")
        observation_id = observation.get("observation_id")
        if not isinstance(observation_id, str) or observation_id in observations_by_id:
            raise RuntimeError("route direction certificate observation ID is invalid")
        observations_by_id[observation_id] = observation
        evidence = observation.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise RuntimeError("route direction certificate evidence is empty")
        for item in evidence:
            if not isinstance(item, dict):
                raise RuntimeError("route direction certificate evidence row is invalid")
            relative = item.get("path")
            expected = item.get("sha256")
            if not isinstance(relative, str) or not isinstance(expected, str):
                raise RuntimeError("route direction certificate evidence identity is invalid")
            actual = _sha256_file(_repository_evidence_path(relative))
            if actual != expected:
                raise RuntimeError(
                    f"route direction source evidence SHA-256 changed: {relative}"
                )
            evidence_digests[relative] = actual

    workload = payload.get("workload")
    physical = payload.get("physical_parameters")
    if not isinstance(workload, dict) or not isinstance(physical, dict):
        raise RuntimeError("route direction certificate workload identity is invalid")
    if physical != {
        "expected_query_batches": 1,
        "index_ready": False,
        "limit": 4,
        "maximum_boundary": "open",
        "maximum_distance_hex": float(2.0).hex(),
        "minimum_boundary": "open",
        "minimum_distance_hex": float(0.0).hex(),
        "module_ready": False,
    }:
        raise RuntimeError("route direction certificate physical identity changed")
    expected_workload = {
        "candidate_density": 646_391_723 / (12_000_000 * 4_096),
        "packed_workload_cost_fingerprint": (
            "cb8f2bb3471acd58fb726a1157242449b8585e9768b13e77919b416e47c083a8"
        ),
        "packed_workload_identity_digest": (
            "28d4cb1392c48328d7daf1f36f4205ad06875e57deecd8387a042e8b70d8b07e"
        ),
        "query_count": 4_096,
        "query_file_sha256": (
            "8b5d52ccb049a5604dbdc41b8ebefd2ba7ea2213e94e1e296ab3de2d55863f83"
        ),
        "search_count": 12_000_000,
        "search_file_sha256": (
            "f79916c2b4cb9548fe19b568256d2fd8f492ccac60eb5efefdfeafc66e1a830d"
        ),
    }
    if workload != expected_workload:
        raise RuntimeError("route direction certificate workload changed")

    modern = json.loads(
        _repository_evidence_path(
            "history/internal_docs/goal5615_current_source_modern_gpu_runtime_no_go.json"
        ).read_text(encoding="utf-8")
    )
    modern_timing = modern.get("prepared_first_query", {})
    modern_correctness = modern.get("correctness", {})
    modern_hardware = modern.get("hardware", {})
    if not (
        modern.get("schema") == "rtdl.research.v3.preserved_worker_runtime_no_go.v1"
        and modern_timing.get("action", {}).get("median") == 5.011668618768454
        and modern_timing.get("baseline", {}).get("median") == 2.3794553223997355
        and modern_hardware.get("gpu_name") == "NVIDIA RTX 4000 Ada Generation"
        and modern_hardware.get("compute_capability") == "8.9"
        and modern_hardware.get("optix_backend_version") == [8, 0, 0]
        and modern_correctness.get("row_count") == 16_382
        and modern_correctness.get("canonical_rows_sha256")
        == "57b0974a0d08ae72468a0ba88bdb3fcbaea48d6001b35f126db63ab22872ea0b"
        and modern_correctness.get("strict_canonical_rows_equal_in_every_pair") is True
    ):
        raise RuntimeError("controlled-modern route observation content changed")

    packet = json.loads(
        _repository_evidence_path(
            "history/internal_docs/goal5613_current_source_runtime_packet.json"
        ).read_text(encoding="utf-8")
    )
    packet_fixture = packet.get("fixture", {})
    packet_files = {
        item.get("name"): item.get("sha256")
        for item in packet_fixture.get("files", [])
        if isinstance(item, dict)
    }
    if not (
        packet_fixture.get("search_count") == expected_workload["search_count"]
        and packet_fixture.get("query_count") == expected_workload["query_count"]
        and packet_files.get("search.xyz") == expected_workload["search_file_sha256"]
        and packet_files.get("queries.xyz") == expected_workload["query_file_sha256"]
        and packet.get("hardware_gate", {}).get("controlled_modern_gpu_required")
        is True
        and packet.get("measurement", {}).get("pair_count") == 20
        and packet.get("measurement", {}).get("strict_output_equality_required")
        is True
    ):
        raise RuntimeError("controlled-modern workload protocol content changed")

    functional = json.loads(
        _repository_evidence_path(
            "history/internal_docs/goal5624_current_source_bootstrap_calibration_home_linux.json"
        ).read_text(encoding="utf-8")
    )
    functional_scope = functional.get("calibration_scope", {})
    functional_summaries = functional.get("measurement", {}).get("summaries", {})
    if not (
        functional_scope.get("exact_packed_workload_identity_digest")
        == expected_workload["packed_workload_identity_digest"]
        and functional_scope.get("candidate_density")
        == expected_workload["candidate_density"]
        and functional_summaries.get(
            "effect_typed_action_optix_bounded_selection_3d", {}
        ).get("prepare_plus_query_median_seconds")
        == 12.296839078480843
        and functional_summaries.get(
            "prepared_ranked_distance_window_neighbors_3d", {}
        ).get("prepare_plus_query_median_seconds")
        == 7.146094559924677
        and functional.get("claim_boundary", {}).get(
            "home_linux_functional_calibration_only"
        )
        is True
    ):
        raise RuntimeError("functional route observation content changed")

    identity = json.loads(
        _repository_evidence_path(
            "history/internal_docs/goal5624_locked_point_workload_identity_home_linux.json"
        ).read_text(encoding="utf-8")
    )
    if not all(
        identity.get(key) == expected_workload[expected_key]
        for key, expected_key in (
            ("packed_workload_cost_fingerprint", "packed_workload_cost_fingerprint"),
            ("packed_workload_identity_digest", "packed_workload_identity_digest"),
            ("query_count", "query_count"),
            ("query_file_sha256", "query_file_sha256"),
            ("search_count", "search_count"),
            ("search_file_sha256", "search_file_sha256"),
        )
    ):
        raise RuntimeError("functional workload identity content changed")

    minimum_ratio = float(policy["minimum_loser_over_winner_ratio"])
    clear_winners: set[str] = set()
    distinct_hardware: set[str] = set()
    controlled_count = 0
    functional_count = 0
    for row in registered:
        observation = observations_by_id.get(row.observation_id)
        if observation is None:
            raise RuntimeError("registered observation is absent from route certificate")
        hardware = observation.get("hardware")
        timing = observation.get("timing")
        eligibility = observation.get("eligibility")
        if not all(isinstance(value, dict) for value in (hardware, timing, eligibility)):
            raise RuntimeError("route direction certificate observation fields are invalid")
        assert isinstance(hardware, dict)
        assert isinstance(timing, dict)
        assert isinstance(eligibility, dict)
        fused = float(timing.get("fused_observed_total_seconds", math.nan))
        grid = float(timing.get("grid_observed_total_seconds", math.nan))
        if not (math.isfinite(fused) and math.isfinite(grid) and fused > 0 and grid > 0):
            raise RuntimeError("route direction certificate timing is invalid")
        winner = _GRID_BACKEND if grid < fused else _FUSED_BACKEND
        loser_over_winner = max(fused, grid) / min(fused, grid)
        if (
            hardware.get("hardware_key") != row.hardware_key
            or timing.get("winner_backend") != winner
            or not math.isclose(
                float(timing.get("loser_over_winner_ratio", math.nan)),
                loser_over_winner,
                rel_tol=0.0,
                abs_tol=1e-15,
            )
            or fused != row.fused_observed_total_seconds
            or grid != row.grid_observed_total_seconds
            or eligibility.get("controlled_modern_exact_observation")
            is not row.controlled_modern_exact_observation
            or eligibility.get("functional_only") is not row.functional_only
            or eligibility.get("eligible_for_direction_consensus")
            is not row.direction_consensus_eligible
            or eligibility.get("eligible_for_seconds_extrapolation") is not False
            or row.winner_backend != winner
            or row.clear_margin_threshold_met
            is not (loser_over_winner >= minimum_ratio)
            or row.route_direction_certificate_digest != certificate_digest
            or row.workload_fingerprint_digest
            != expected_workload["packed_workload_cost_fingerprint"]
            or row.source_exact_workload_identity_digest
            != expected_workload["packed_workload_identity_digest"]
            or row.limit != physical["limit"]
            or row.minimum_distance_hex != physical["minimum_distance_hex"]
            or row.maximum_distance_hex != physical["maximum_distance_hex"]
            or row.minimum_boundary != physical["minimum_boundary"]
            or row.maximum_boundary != physical["maximum_boundary"]
            or row.expected_query_batches != physical["expected_query_batches"]
            or row.module_ready is not physical["module_ready"]
            or row.index_ready is not physical["index_ready"]
        ):
            raise RuntimeError("registered observation differs from route certificate")
        evidence = observation["evidence"]
        assert isinstance(evidence, list)
        if not any(
            item.get("path") == row.source_evidence_path
            and item.get("sha256") == row.source_evidence_digest
            for item in evidence
            if isinstance(item, dict)
        ):
            raise RuntimeError("registered source evidence is absent from certificate")
        if row.candidate_density != float(workload.get("candidate_density", math.nan)):
            raise RuntimeError("registered candidate density differs from certificate")
        if row.direction_consensus_eligible:
            if loser_over_winner < minimum_ratio:
                raise RuntimeError("route direction margin is below certificate policy")
            clear_winners.add(winner)
            distinct_hardware.add(row.hardware_key)
            controlled_count += int(row.controlled_modern_exact_observation)
            functional_count += int(row.functional_only)

    if (
        clear_winners != {_GRID_BACKEND}
        or len(distinct_hardware) < int(policy["minimum_distinct_hardware"])
        or controlled_count
        < int(policy["minimum_controlled_modern_exact_observations"])
        or functional_count
        < int(policy["minimum_functional_direction_observations"])
    ):
        raise RuntimeError("route direction certificate consensus is ineligible")
    return payload | {
        "_certificate_path": _ROUTE_DIRECTION_CERTIFICATE_RELATIVE_PATH,
        "_certificate_sha256": certificate_digest,
        "_validated_source_sha256s": evidence_digests,
    }


def _runtime_route_direction_certificate(
    rows: tuple[_TrustedPointCalibration, ...] | None = None,
) -> dict[str, object]:
    """Expose only the source-frozen categorical direction to hot planning.

    The full certificate, raw timings, and evidence-file hashes are verified by
    ``_validated_route_direction_certificate`` during the offline freeze.  Hot
    planning consumes neither those files nor either observed-seconds field.
    """

    registered = _TRUSTED_EXACT_POINT_CALIBRATIONS if rows is None else rows
    for row in registered:
        if row.route_direction_certificate_digest != _ROUTE_DIRECTION_CERTIFICATE_SHA256:
            raise RuntimeError("runtime route direction certificate identity changed")
        if row.winner_backend not in {_FUSED_BACKEND, _GRID_BACKEND}:
            raise RuntimeError("runtime route direction winner is invalid")
        if not isinstance(row.clear_margin_threshold_met, bool):
            raise RuntimeError("runtime route direction margin certificate is invalid")
    return {
        "policy": dict(_RUNTIME_DIRECTION_POLICY),
        "_certificate_path": _ROUTE_DIRECTION_CERTIFICATE_RELATIVE_PATH,
        "_certificate_sha256": _ROUTE_DIRECTION_CERTIFICATE_SHA256,
        "_validation_stage": "offline_freeze__source_embedded_direction_only_at_runtime",
        "_runtime_source_evidence_rehashed": False,
        "_runtime_observed_seconds_read": False,
    }


def _native_library_identity(
    library,
    *,
    required_symbols: tuple[str, ...],
) -> dict[str, object]:
    """Compatibility metadata wrapper over the app-neutral identity helper."""

    return _shared_native_library_identity(
        library,
        required_symbols=required_symbols,
    ).to_metadata()


def _probe_native_template_symbols(
    required_symbols: tuple[str, ...],
) -> _NativeSymbolProbe:
    """Compatibility probe wrapper; identity and symbol logic stay shared."""

    probe = _shared_probe_native_template_symbols(required_symbols)
    identity = (
        probe.library_identity.to_metadata()
        if probe.library_identity is not None
        else None
    )
    return _NativeSymbolProbe(
        attempted=probe.attempted,
        available=probe.available,
        required_symbols=probe.required_symbols,
        missing_symbols=probe.missing_symbols,
        library_path=(
            probe.library_identity.resolved_path
            if probe.library_identity is not None
            else None
        ),
        library_identity=identity,
        error=probe.error,
        _library_identity_object=probe.library_identity,
        _library_ref=probe.library_ref,
    )


def _probe_ranked_window_qk_native_symbols() -> _NativeSymbolProbe:
    """Prove the native prepared-QK surface rather than trusting a broad flag."""

    return _probe_native_template_symbols(_QK_REQUIRED_NATIVE_SYMBOLS)


def _probe_fused_point_native_symbols() -> _NativeSymbolProbe:
    """Prove the fused point Action ABI independently from the QK ABI."""

    return _probe_native_template_symbols(_FUSED_REQUIRED_NATIVE_SYMBOLS)


def _probe_candidate_pruned_native_symbols() -> _NativeSymbolProbe:
    """Prove the complete prepared exact bounded-selection ABI."""

    return _probe_native_template_symbols(_PRUNED_REQUIRED_NATIVE_SYMBOLS)


def validate_registered_point_prepare_contract(
    planned: PlannedLoweredAction,
    *,
    parameters: Mapping[str, object],
    max_distance_bound: float | None,
) -> tuple[float | None, Mapping[str, object] | None]:
    """Revalidate the sealed point plan at the native owner-creation boundary."""

    lowered = planned.lowered
    if (
        lowered.producer_kind
        is not ActionProducerKind.PREPARED_POINT_CANDIDATES_3D
        or lowered.template_kind
        not in {
            "point_candidate_bounded_selection_3d",
            "prepared_ranked_distance_window_qk_3d",
            "candidate_pruned_exact_bounded_selection_3d",
        }
    ):
        return max_distance_bound, None
    trace = lowered.compiler_execution_trace
    registry = trace.get("physical_registry") if isinstance(trace, Mapping) else None
    if not isinstance(registry, Mapping) or registry.get("contract") != (
        ACTION_PHYSICAL_REGISTRY_VERSION
    ):
        raise RuntimeError("registered point plan has no sealed physical registry")
    expected_library = registry.get("runtime_native_library_identity")
    planned_identity = planned.compiler_native_library_identity
    planned_library = planned._compiler_native_library_ref
    if (
        not isinstance(expected_library, Mapping)
        or not isinstance(planned_identity, ActionNativeLibraryIdentity)
        or planned_library is None
        or planned._compiler_native_library_object_id != id(planned_library)
    ):
        raise RuntimeError("registered point plan has no native library identity")
    if lowered.backend == _GRID_BACKEND:
        current_probe = _probe_ranked_window_qk_native_symbols()
    elif lowered.backend == _FUSED_BACKEND:
        current_probe = _probe_fused_point_native_symbols()
    elif lowered.backend == _PRUNED_BACKEND:
        current_probe = _probe_candidate_pruned_native_symbols()
    else:
        raise RuntimeError("registered point backend changed")
    current_library = current_probe.library_identity
    if (
        not current_probe.available
        or current_probe._library_ref is not planned_library
        or not isinstance(current_library, Mapping)
        or dict(current_library) != dict(expected_library)
        or planned_identity.to_metadata() != dict(expected_library)
    ):
        raise RuntimeError("registered point native library identity changed")
    validate_native_library_identity(planned_library, planned_identity)

    program = lowered.program
    if lowered.backend == _GRID_BACKEND:
        from .action_ranked_window_lowering import (
            RankedDistanceWindowQkProgram3D,
            compile_ranked_distance_window_qk_3d,
        )

        if type(program) is not RankedDistanceWindowQkProgram3D:
            raise RuntimeError("registered point QK program type changed")
        expected_program = compile_ranked_distance_window_qk_3d(
            lowered.compiled.spec,
            discharged_delivery_proofs=frozenset(
                {program.delivery_proof_reference}
            ),
        )
    elif lowered.backend == _FUSED_BACKEND:
        from .action_optix_lowering import (
            OptixBoundedSelectionProgram3D,
            compile_optix_bounded_selection_3d,
        )

        if type(program) is not OptixBoundedSelectionProgram3D:
            raise RuntimeError("registered point fused program type changed")
        expected_program = compile_optix_bounded_selection_3d(
            lowered.compiled.spec,
            discharged_delivery_proofs=frozenset(
                {program.delivery_proof_reference}
            ),
        )
    elif lowered.backend == _PRUNED_BACKEND:
        from .action_candidate_pruned_lowering import (
            CandidatePrunedExactBoundedSelectionProgram3D,
            compile_candidate_pruned_exact_bounded_selection_3d,
        )

        if (
            type(program)
            is not CandidatePrunedExactBoundedSelectionProgram3D
        ):
            raise RuntimeError(
                "registered point candidate-pruned program type changed"
            )
        expected_program = (
            compile_candidate_pruned_exact_bounded_selection_3d(
                lowered.compiled.spec,
                discharged_delivery_proofs=frozenset(
                    {program.delivery_proof_reference}
                ),
            )
        )
    else:
        raise RuntimeError("registered point backend changed")
    if program != expected_program or program.to_metadata() != expected_program.to_metadata():
        raise RuntimeError("registered point executable program differs from verified IR")

    expected_physical = registry.get("physical_parameter_identity")
    current_physical = _point_physical_identity(
        {lowered.backend: lowered}, parameters
    ).to_dict()
    if not isinstance(expected_physical, Mapping) or (
        dict(expected_physical) != current_physical
    ):
        raise RuntimeError("registered point physical parameters changed")

    maximum_parameter = getattr(lowered.program, "maximum_parameter", None)
    if not isinstance(maximum_parameter, str) or maximum_parameter not in parameters:
        raise RuntimeError("registered point maximum parameter is missing")
    maximum = parameters[maximum_parameter]
    if isinstance(maximum, bool):
        raise RuntimeError("registered point maximum parameter is invalid")
    try:
        derived = float(maximum)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("registered point maximum parameter is invalid") from exc
    if not math.isfinite(derived) or derived <= 0.0:
        raise RuntimeError("registered point maximum parameter is invalid")
    expected_hex = registry.get("prepared_max_distance_bound_hex")
    if expected_hex != derived.hex():
        raise RuntimeError("registered point maximum parameter changed after planning")
    if max_distance_bound is not None:
        if isinstance(max_distance_bound, bool):
            raise RuntimeError("prepared max distance bound is invalid")
        try:
            supplied = float(max_distance_bound)
        except (TypeError, ValueError) as exc:
            raise RuntimeError("prepared max distance bound is invalid") from exc
        if not math.isfinite(supplied) or supplied.hex() != derived.hex():
            raise RuntimeError(
                "prepared max distance bound differs from verified maximum parameter"
            )
    return derived, planned_identity.to_metadata()


def _point_physical_identity(
    lowered_by_backend: Mapping[str, LoweredAction],
    parameters: Mapping[str, object],
) -> _PointPhysicalIdentity:
    programs = [
        lowered_by_backend[backend].program
        for backend in (_PRUNED_BACKEND, _FUSED_BACKEND, _GRID_BACKEND)
        if backend in lowered_by_backend
    ]
    if not programs:
        raise RuntimeError("no verified point bounded-selection template compiled")
    role_signatures = {
        (
            str(program.limit_parameter),
            str(program.minimum_parameter),
            str(program.maximum_parameter),
            str(program.minimum_boundary),
            str(program.maximum_boundary),
        )
        for program in programs
    }
    if len(role_signatures) != 1:
        raise RuntimeError("point physical templates disagree on parameter roles")
    (
        limit_parameter,
        minimum_parameter,
        maximum_parameter,
        minimum_boundary,
        maximum_boundary,
    ) = next(iter(role_signatures))
    expected_parameter_names = {
        limit_parameter,
        minimum_parameter,
        maximum_parameter,
    }
    if set(parameters) != expected_parameter_names:
        raise ValueError(
            "point bounded-selection parameters must contain exactly the verified "
            "limit and distance-window roles"
        )
    limit = parameters.get(limit_parameter)
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("bounded-selection limit must be a positive integer")
    minimum = parameters.get(minimum_parameter)
    maximum = parameters.get(maximum_parameter)
    if isinstance(minimum, bool) or isinstance(maximum, bool):
        raise ValueError("distance-window parameters must be finite numbers")
    try:
        minimum_value = float(minimum)
        maximum_value = float(maximum)
    except (TypeError, ValueError) as exc:
        raise ValueError("distance-window parameters must be finite numbers") from exc
    if not math.isfinite(minimum_value) or not math.isfinite(maximum_value):
        raise ValueError("distance-window parameters must be finite numbers")
    if minimum_value < 0.0 or maximum_value <= 0.0 or minimum_value > maximum_value:
        raise ValueError("distance-window parameters are outside the native domain")
    return _PointPhysicalIdentity(
        limit=limit,
        minimum_distance_hex=minimum_value.hex(),
        maximum_distance_hex=maximum_value.hex(),
        minimum_boundary=minimum_boundary,
        maximum_boundary=maximum_boundary,
    )


def _row_matches_exact_point(
    row: _TrustedPointCalibration,
    *,
    workload_fingerprint: str,
    workload_identity: str,
    physical_identity: _PointPhysicalIdentity,
) -> bool:
    return (
        row.workload_fingerprint_digest == workload_fingerprint
        and row.source_exact_workload_identity_digest == workload_identity
        and row.limit == physical_identity.limit
        and row.minimum_distance_hex == physical_identity.minimum_distance_hex
        and row.maximum_distance_hex == physical_identity.maximum_distance_hex
        and row.minimum_boundary == physical_identity.minimum_boundary
        and row.maximum_boundary == physical_identity.maximum_boundary
        and row.expected_query_batches == physical_identity.expected_query_batches
        and row.module_ready is physical_identity.module_ready
        and row.index_ready is physical_identity.index_ready
    )


def _row_matches_sample_and_physical_point(
    row: _TrustedPointCalibration,
    *,
    workload_fingerprint: str,
    physical_identity: _PointPhysicalIdentity,
) -> bool:
    """Match a bounded performance hint, never semantic legality or seconds.

    A sampled collision can at worst reorder two independently verified legal
    templates. Exact seconds and same-hardware calibration still require the
    full packed identity; neither is inferred from this predicate.
    """

    return (
        row.workload_fingerprint_digest == workload_fingerprint
        and row.limit == physical_identity.limit
        and row.minimum_distance_hex == physical_identity.minimum_distance_hex
        and row.maximum_distance_hex == physical_identity.maximum_distance_hex
        and row.minimum_boundary == physical_identity.minimum_boundary
        and row.maximum_boundary == physical_identity.maximum_boundary
        and row.expected_query_batches == physical_identity.expected_query_batches
        and row.module_ready is physical_identity.module_ready
        and row.index_ready is physical_identity.index_ready
    )


def _clear_observed_winner(
    row: _TrustedPointCalibration,
    *,
    minimum_loser_over_winner_ratio: float,
) -> str | None:
    if not math.isclose(
        minimum_loser_over_winner_ratio,
        float(_RUNTIME_DIRECTION_POLICY["minimum_loser_over_winner_ratio"]),
        rel_tol=0.0,
        abs_tol=0.0,
    ):
        return None
    if not row.clear_margin_threshold_met:
        return None
    return row.winner_backend


def _route_consensus(
    *,
    rows: tuple[_TrustedPointCalibration, ...],
    workload_fingerprint: str,
    workload_identity: str | None,
    physical_identity: _PointPhysicalIdentity,
    exact_hardware_calibration_matched: bool,
    certificate: Mapping[str, object] | None,
    certificate_error: str | None,
) -> tuple[tuple[str, str], dict[str, object]]:
    policy = certificate.get("policy") if certificate is not None else None
    minimum_ratio = (
        float(policy["minimum_loser_over_winner_ratio"])
        if isinstance(policy, dict)
        else math.inf
    )
    matching = tuple(
        row
        for row in rows
        if _row_matches_sample_and_physical_point(
            row,
            workload_fingerprint=workload_fingerprint,
            physical_identity=physical_identity,
        )
        and row.direction_consensus_eligible
        and certificate is not None
        and row.route_direction_certificate_digest
        == certificate.get("_certificate_sha256")
    )
    by_hardware: dict[str, set[str | None]] = {}
    for row in matching:
        by_hardware.setdefault(row.hardware_key, set()).add(
            _clear_observed_winner(
                row,
                minimum_loser_over_winner_ratio=minimum_ratio,
            )
        )
    hardware_winners = {
        hardware: next(iter(winners))
        for hardware, winners in by_hardware.items()
        if len(winners) == 1 and None not in winners
    }
    all_hardware_clear = len(hardware_winners) == len(by_hardware)
    winners = set(hardware_winners.values())
    controlled_count = sum(
        int(row.controlled_modern_exact_observation) for row in matching
    )
    functional_count = sum(int(row.functional_only) for row in matching)
    minimum_hardware = (
        int(policy["minimum_distinct_hardware"])
        if isinstance(policy, dict)
        else 2
    )
    minimum_controlled = (
        int(policy["minimum_controlled_modern_exact_observations"])
        if isinstance(policy, dict)
        else 1
    )
    minimum_functional = (
        int(policy["minimum_functional_direction_observations"])
        if isinstance(policy, dict)
        else 1
    )
    eligible = (
        certificate is not None
        and len(hardware_winners) >= minimum_hardware
        and all_hardware_clear
        and len(winners) == 1
        and controlled_count >= minimum_controlled
        and functional_count >= minimum_functional
    )
    winner = next(iter(winners)) if eligible else None
    if eligible:
        other = _GRID_BACKEND if winner == _FUSED_BACKEND else _FUSED_BACKEND
        consensus_order = (winner, other)
        reason = "clear_same_winner_on_multiple_distinct_trusted_hardware"
    else:
        consensus_order = _DEFAULT_FIXED_PRIORITY_LEGAL_ORDER
        if certificate is None:
            reason = "route_direction_certificate_invalid_or_unavailable"
        elif not matching:
            reason = "sampled_workload_or_physical_identity_not_registered"
        elif len(by_hardware) < minimum_hardware:
            reason = "fewer_than_two_distinct_route_direction_observations"
        elif controlled_count < minimum_controlled:
            reason = "controlled_modern_exact_direction_observation_missing"
        elif functional_count < minimum_functional:
            reason = "distinct_functional_direction_observation_missing"
        else:
            reason = "winner_not_clear_or_not_unanimous"
    override_applied = eligible and not exact_hardware_calibration_matched
    return consensus_order, {
        "contract": _CONSENSUS_POLICY_VERSION,
        "eligible": eligible,
        "reason": reason,
        "winner_backend": winner,
        "route_direction_certificate_path": (
            certificate.get("_certificate_path") if certificate is not None else None
        ),
        "route_direction_certificate_sha256": (
            certificate.get("_certificate_sha256") if certificate is not None else None
        ),
        "route_direction_certificate_valid": certificate is not None,
        "route_direction_certificate_error": certificate_error,
        "minimum_distinct_hardware_observations": minimum_hardware,
        "minimum_controlled_modern_exact_observations": minimum_controlled,
        "minimum_functional_direction_observations": minimum_functional,
        "minimum_loser_over_winner_ratio": minimum_ratio,
        "matching_observation_count": len(matching),
        "matching_distinct_hardware_count": len(by_hardware),
        "matching_controlled_modern_exact_observation_count": controlled_count,
        "matching_functional_direction_observation_count": functional_count,
        "matching_hardware_keys": sorted(by_hardware),
        "matching_source_evidence_digests": sorted(
            {row.source_evidence_digest for row in matching}
        ),
        "per_hardware_clear_winner": {
            key: hardware_winners.get(key) for key in sorted(by_hardware)
        },
        "priority_override_applied": override_applied,
        "priority_order": list(
            consensus_order
            if override_applied
            else _DEFAULT_FIXED_PRIORITY_LEGAL_ORDER
        ),
        "sampled_workload_fingerprint_used": True,
        "full_workload_identity_used": workload_identity is not None,
        "sampled_fingerprint_used_for_direction_only_not_seconds_or_legality": True,
        "fingerprint_collision_can_only_change_legal_template_priority": True,
        "semantic_legality_independent_of_fingerprint": True,
        "physical_parameter_identity_used": True,
        "distinct_hardware_identity_used": True,
        "trusted_evidence_identity_used": True,
        "runtime_seconds_used_only_for_observed_winner_direction": False,
        "observed_seconds_are_certificate_bound_offline_only": True,
        "categorical_winner_direction_used_at_runtime": bool(matching),
        "categorical_margin_certificate_used_at_runtime": bool(matching),
        "observed_seconds_read_during_runtime_placement": False,
        "runtime_seconds_inferred_for_current_hardware": False,
        "runtime_seconds_extrapolated_to_current_hardware": False,
        "folded_transfer_or_sync_components_calibrated": False,
        "action_name_used": False,
        "application_identity_used": False,
    }


def _plan_registered_point_bounded_selection_impl(
    bound: BoundAction,
    target_profile: ActionTargetProfile,
    *,
    prepared_search_points,
    query_points,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, object],
    functional_validation_candidate: str | None,
    semantic_statement_stable_id: str | None,
    backend_contract_id: str | None,
) -> PlannedLoweredAction:
    """Choose a trusted physical template without accepting app cost/backend input."""

    if bound.producer_kind is not ActionProducerKind.PREPARED_POINT_CANDIDATES_3D:
        raise ValueError("registered point planning requires the prepared point producer")
    if functional_validation_candidate is not None and (
        functional_validation_candidate
        not in {_PRUNED_BACKEND, _FUSED_BACKEND, _GRID_BACKEND}
    ):
        raise ValueError(
            "functional validation candidate is not compiler-registered"
        )
    query_count = _query_count(extents)
    search_count = int(prepared_search_points.count)
    if query_count != int(query_points.count):
        raise ValueError("query extent does not match packed query count")
    if int(prepared_search_points.dimension) != 3 or int(query_points.dimension) != 3:
        raise ValueError("registered point planning requires 3-D packed points")

    prepared_search_digest = _packed_point_sample_fingerprint(prepared_search_points)
    prepared_search_storage_binding = _packed_point_storage_binding(
        prepared_search_points
    )
    query_digest = _packed_point_sample_fingerprint(query_points)
    workload_hasher = hashlib.sha256(b"rtdl.packed_point_workload_fingerprint.v1\x00")
    workload_hasher.update(bytes.fromhex(prepared_search_digest))
    workload_hasher.update(bytes.fromhex(query_digest))
    workload_fingerprint = workload_hasher.hexdigest()
    # Runtime placement imports no same-hardware seconds calibration.  The
    # source-frozen hint requires agreement across distinct recorded hardware,
    # so probing current hardware here would add CUDA initialization cost and
    # cannot affect the legal or priority decision.
    hardware_key = None
    effects = frozenset(verify_action_spec(bound.compiled.spec).inferred_effects)
    lowered_by_backend: dict[str, LoweredAction] = {}
    rejections: list[tuple[str, str]] = []
    for backend in (_PRUNED_BACKEND, _FUSED_BACKEND, _GRID_BACKEND):
        try:
            lowered_by_backend[backend] = lower_action(bound, backend=backend)
        except Exception as exc:
            issue = getattr(exc, "issue", None)
            rejections.append(
                (backend, getattr(issue, "code", type(exc).__name__))
            )
    physical_identity = _point_physical_identity(lowered_by_backend, parameters)
    try:
        route_certificate = _runtime_route_direction_certificate(
            _TRUSTED_EXACT_POINT_CALIBRATIONS
        )
        route_certificate_error = None
        registered_rows = _TRUSTED_EXACT_POINT_CALIBRATIONS
    except Exception as exc:
        route_certificate = None
        route_certificate_error = f"{type(exc).__name__}:{exc}"
        registered_rows = ()
    same_hardware_direction_rows: tuple[_TrustedPointCalibration, ...] = ()
    # Full byte identity remains an offline evidence utility. Runtime placement
    # uses the cross-hardware winner direction only; it never imports exact
    # observed seconds or turns input bytes into a semantic/legality proof.
    # Therefore no O(N) packed-input scan belongs in the compiler hot path.
    search_full_identity: str | None = None
    query_full_identity: str | None = None
    workload_identity: str | None = None
    full_identity_scan_seconds: float | None = None
    exact_matches: tuple[_TrustedPointCalibration, ...] = ()
    trusted: _TrustedPointCalibration | None = None
    consensus_order, consensus_metadata = _route_consensus(
        rows=registered_rows,
        workload_fingerprint=workload_fingerprint,
        workload_identity=workload_identity,
        physical_identity=physical_identity,
        exact_hardware_calibration_matched=False,
        certificate=route_certificate,
        certificate_error=route_certificate_error,
    )
    production_default_plan: Mapping[str, object] | None = None
    production_default_binding: Mapping[str, object] | None = None
    canonical_resolution: Mapping[str, object] | None = None
    canonical_authority: Mapping[str, object] | None = None
    if (
        functional_validation_candidate is None
        and target_profile.production_selection_policy == "compiler_owned_default"
    ):
        from .production_default_integration import (
            ProductionDefaultIntegrationError,
            compile_production_default_plan,
            make_production_action_descriptor,
            make_production_target_descriptor,
        )

        if target_profile.profile_source != "runtime_capability_probe":
            raise RuntimeError(
                "production DEFAULT requires compiler-probed point target facts"
            )
        if target_profile.device_memory_limit_bytes is None:
            raise RuntimeError(
                "production DEFAULT requires an actual device-memory limit"
            )
        limit = int(parameters.get("k", parameters.get("limit", 1)))
        if limit <= 0:
            raise ValueError("bounded-selection limit must be positive")
        providers: set[str] = set()
        if target_profile.optix_available:
            providers.update(("cuda", "cupy", "optix"))
        if target_profile.numba_available:
            providers.add("numba")
        if target_profile.cpu_reference_available:
            providers.add("python")
        try:
            action_descriptor = make_production_action_descriptor(
                semantic_kind=bound.producer_kind.value,
                action_contract_class="bounded_selection_3d",
                action_semantic_digest=bound.compiled.spec.semantic_digest,
                output_contract={
                    "action_source_digest": bound.compiled.source_digest,
                    "producer_binding_digest": bound.binding_digest,
                    "bounded_selection_limit": limit,
                    "complete_query_output_required": True,
                },
                work_domain={
                    "search_count": search_count,
                    "query_count": query_count,
                    "parameters": dict(sorted(parameters.items())),
                    "prepared_search_storage_binding": (
                        prepared_search_storage_binding
                    ),
                },
                input_bytes=(search_count + query_count) * 16,
                output_bytes=query_count * limit * 32,
                prepared_bytes=search_count * 16,
                logical_cardinality_bound=max(search_count, query_count),
                pair_cardinality_bound=search_count * query_count,
                logical_item_bytes_bound=16,
                pair_item_bytes_bound=32,
            )
            target_descriptor = make_production_target_descriptor(
                target_identity={
                    "target_profile": target_profile.to_metadata(),
                    "producer_kind": bound.producer_kind.value,
                },
                available_providers=providers,
                memory_limit_bytes=target_profile.device_memory_limit_bytes,
                mandatory_nvidia_rt=True,
            )
            if (semantic_statement_stable_id is None) != (
                backend_contract_id is None
            ):
                raise ValueError(
                    "canonical semantic statement and backend contract are required together"
                )
            if semantic_statement_stable_id is not None:
                from .canonical_physical_resolution import (
                    CanonicalPhysicalResolutionError,
                    registered_backend_contract,
                    registered_semantic_statement,
                    resolve_canonical_provider,
                )

                statement = registered_semantic_statement(
                    semantic_statement_stable_id
                )
                backend_contract = registered_backend_contract(
                    backend_contract_id
                )
                canonical_resolution = resolve_canonical_provider(
                    statement_stable_id=statement.stable_id,
                    expected_statement_sha256=statement.digest,
                    backend_contract_id=backend_contract.stable_id,
                    expected_backend_contract_sha256=backend_contract.digest,
                    action=action_descriptor,
                    target=target_descriptor,
                )
                if canonical_resolution.get("status") != "RESOLVED":
                    raise CanonicalPhysicalResolutionError(
                        str(canonical_resolution.get("error_code", "FAIL_CLOSED")),
                        str(canonical_resolution.get("error_detail", "")),
                    )
            production_default_plan = compile_production_default_plan(
                action_descriptor,
                target_descriptor,
                mandatory_nvidia_rt=True,
                repository_root=Path(__file__).resolve().parents[2],
            )
        except ProductionDefaultIntegrationError as exc:
            raise RuntimeError(f"production DEFAULT failed closed: {exc}") from exc
        if not str(production_default_plan["selected_candidate_stable_id"]).endswith(
            "/optix/point_candidate_bounded_selection_3d"
        ):
            raise RuntimeError(
                "production DEFAULT selected an unexpected point candidate"
            )
        priority_order = (_FUSED_BACKEND, _PRUNED_BACKEND, _GRID_BACKEND)
    elif functional_validation_candidate is not None:
        priority_order = (functional_validation_candidate,) + tuple(
            backend
            for backend in _CANDIDATE_PRUNED_FIXED_PRIORITY_LEGAL_ORDER
            if backend != functional_validation_candidate
        )
    else:
        priority_order = (
            (_PRUNED_BACKEND,) + tuple(consensus_order)
            if bool(consensus_metadata["priority_override_applied"])
            else _CANDIDATE_PRUNED_FIXED_PRIORITY_LEGAL_ORDER
        )
    exact_route_identity_bound = False
    if target_profile.optix_available:
        pruned_symbol_probe = _probe_candidate_pruned_native_symbols()
        qk_symbol_probe = _probe_ranked_window_qk_native_symbols()
        fused_symbol_probe = _probe_fused_point_native_symbols()
    else:
        pruned_symbol_probe = _NativeSymbolProbe(
            attempted=False,
            available=False,
            required_symbols=_PRUNED_REQUIRED_NATIVE_SYMBOLS,
            error="target_profile_optix_unavailable",
        )
        qk_symbol_probe = _NativeSymbolProbe(
            attempted=False,
            available=False,
            required_symbols=_QK_REQUIRED_NATIVE_SYMBOLS,
            error="target_profile_optix_unavailable",
        )
        fused_symbol_probe = _NativeSymbolProbe(
            attempted=False,
            available=False,
            required_symbols=_FUSED_REQUIRED_NATIVE_SYMBOLS,
            error="target_profile_optix_unavailable",
        )
    if (
        target_profile.optix_available
        and _GRID_BACKEND in lowered_by_backend
        and not qk_symbol_probe.available
    ):
        rejections.append(
            (
                _GRID_BACKEND,
                "required_native_symbol_missing"
                if qk_symbol_probe.missing_symbols
                else "native_symbol_probe_failed",
            )
        )
    if (
        target_profile.optix_available
        and _FUSED_BACKEND in lowered_by_backend
        and not fused_symbol_probe.available
    ):
        rejections.append(
            (
                _FUSED_BACKEND,
                "required_native_symbol_missing"
                if fused_symbol_probe.missing_symbols
                else "native_symbol_probe_failed",
            )
        )
    capabilities = (
        ActionBackendCapability(
            backend=_PRUNED_BACKEND,
            placement=ActionPlacementKind.DEVICE_CONTINUATION,
            supported_effect_sets=(effects,),
            state_storage=ActionStateStorage.DEVICE_GLOBAL,
            max_state_bytes=target_profile.numba_max_device_state_bytes,
            max_output_bytes=target_profile.max_output_bytes,
            supports_proven_single=True,
            available=(
                target_profile.optix_available
                and pruned_symbol_probe.available
                and pruned_symbol_probe.library_identity is not None
                and _PRUNED_BACKEND in lowered_by_backend
            ),
            priority=priority_order.index(_PRUNED_BACKEND),
        ),
        ActionBackendCapability(
            backend=_FUSED_BACKEND,
            placement=ActionPlacementKind.TRAVERSAL_FUSED,
            supported_effect_sets=(effects,),
            state_storage=ActionStateStorage.INLINE_PER_SCOPE,
            max_state_bytes=target_profile.optix_max_inline_state_bytes,
            max_output_bytes=target_profile.max_output_bytes,
            supports_proven_single=True,
            available=(
                target_profile.optix_available
                and fused_symbol_probe.available
                and fused_symbol_probe.library_identity is not None
                and _FUSED_BACKEND in lowered_by_backend
            ),
            priority=priority_order.index(_FUSED_BACKEND),
        ),
        ActionBackendCapability(
            backend=_GRID_BACKEND,
            placement=ActionPlacementKind.DEVICE_CONTINUATION,
            supported_effect_sets=(effects,),
            state_storage=ActionStateStorage.DEVICE_GLOBAL,
            max_state_bytes=target_profile.numba_max_device_state_bytes,
            max_output_bytes=target_profile.max_output_bytes,
            supports_proven_single=True,
            available=(
                target_profile.optix_available
                and qk_symbol_probe.available
                and qk_symbol_probe.library_identity is not None
                and _GRID_BACKEND in lowered_by_backend
            ),
            priority=priority_order.index(_GRID_BACKEND),
        ),
    )
    effective = tuple(capabilities)

    features = ActionCostFeatures(
        producer_kind=bound.producer_kind.value,
        resident_representation=_REPRESENTATION,
        search_count=search_count,
        query_count=query_count,
        candidate_density_upper_bound=0.0,
        expected_query_batches=1,
        module_ready=False,
        index_ready=False,
        predicted_h2d_bytes=None,
        predicted_d2h_bytes=None,
        transfer_accounting=ActionTransferAccounting.FOLDED_INELIGIBLE,
        calibration_version=_CALIBRATION_VERSION,
        phase_evidence_digest=_NO_EVIDENCE_DIGEST,
        calibration_evidence_digest=_NO_EVIDENCE_DIGEST,
    )
    calibrations: tuple[ActionBackendCostCalibration, ...] = ()

    plan = plan_action_placement(
        bound.compiled.spec,
        effective,
        extents=extents,
        parameters={key: int(value) for key, value in parameters.items() if isinstance(value, int)},
        discharged_delivery_proofs=bound.delivery_proofs,
        discharged_termination_certificates=bound.termination_certificates,
        producer_kind=bound.producer_kind.value,
        cost_features=features,
        cost_calibrations=calibrations,
    )
    lowered = lowered_by_backend.get(plan.selected_backend)
    if lowered is None:
        raise RuntimeError("compiler selected a physical template that failed preflight")
    if plan.selected_backend == _PRUNED_BACKEND:
        selected_symbol_probe = pruned_symbol_probe
    elif plan.selected_backend == _GRID_BACKEND:
        selected_symbol_probe = qk_symbol_probe
    else:
        selected_symbol_probe = fused_symbol_probe
    if not selected_symbol_probe.available or selected_symbol_probe.library_identity is None:
        raise RuntimeError("compiler selected a native template without its exact ABI")
    if (
        selected_symbol_probe._library_identity_object is None
        or selected_symbol_probe._library_ref is None
    ):
        raise RuntimeError(
            "compiler selected a native template without a strong library binding"
        )
    if production_default_plan is not None:
        from .production_default_integration import (
            ProductionDefaultIntegrationError,
            bind_default_plan_to_lowering,
        )

        try:
            production_default_binding = bind_default_plan_to_lowering(
                production_default_plan,
                actual_backend=lowered.backend,
                actual_template=lowered.template_kind,
                repository_root=Path(__file__).resolve().parents[2],
            )
            if canonical_resolution is not None:
                from .canonical_physical_resolution import (
                    bind_canonical_provider_to_materialized_plan,
                )

                canonical_authority = bind_canonical_provider_to_materialized_plan(
                    canonical_resolution,
                    materialized_provider_stable_id=str(
                        production_default_plan["selected_candidate_stable_id"]
                    ),
                    materialized_plan_sha256=str(
                        production_default_plan["production_plan_sha256"]
                    ),
                    materialized_binding_sha256=str(
                        production_default_binding["binding_sha256"]
                    ),
                )
        except ProductionDefaultIntegrationError as exc:
            raise RuntimeError(
                f"production DEFAULT lowering binding failed: {exc}"
            ) from exc
    consensus_metadata = dict(consensus_metadata) | {
        "consensus_winner_native_and_template_legal": (
            consensus_metadata["winner_backend"] is not None
            and any(
                candidate.backend == consensus_metadata["winner_backend"]
                and candidate.legal
                for candidate in plan.candidates
            )
        ),
        "consensus_winner_selected": (
            bool(consensus_metadata["priority_override_applied"])
            and plan.selected_backend == consensus_metadata["winner_backend"]
        ),
    }
    registry_metadata = {
        "contract": ACTION_PHYSICAL_REGISTRY_VERSION,
        "hardware_calibration_key": hardware_key,
        "runtime_hardware_identity_queried": False,
        "runtime_hardware_identity_not_required_reason": (
            "cross_hardware_direction_only__no_same_hardware_seconds_calibration"
        ),
        "workload_fingerprint_digest": workload_fingerprint,
        "full_workload_identity_digest": workload_identity,
        "prepared_search_sample_fingerprint": prepared_search_digest,
        "prepared_search_storage_binding": prepared_search_storage_binding,
        "query_sample_fingerprint": query_digest,
        "fingerprint_sample_limit": _FINGERPRINT_SAMPLE_LIMIT,
        "fingerprint_is_exact_input_identity": (
            search_count <= _FINGERPRINT_SAMPLE_LIMIT
            and query_count <= _FINGERPRINT_SAMPLE_LIMIT
        ),
        "packed_input_fully_scanned_for_planning": workload_identity is not None,
        "full_identity_scan_candidate_count": 0,
        "full_identity_scan_gate": "disabled_for_runtime_placement",
        "sample_and_physical_gate_can_only_authorize_full_identity_scan": False,
        "same_hardware_match_required_to_authorize_full_identity_scan": False,
        "same_hardware_direction_observation_count": len(
            same_hardware_direction_rows
        ),
        "hot_exact_seconds_calibration_enabled": False,
        "exact_calibration_records_retained_offline_only": True,
        "full_identity_scan_seconds": full_identity_scan_seconds,
        "full_identity_scan_inside_compiler_plan_denominator": (
            workload_identity is not None
        ),
        "full_identity_scan_hidden_or_amortized": False,
        "route_direction_certificate_valid": route_certificate is not None,
        "route_direction_validation_stage": (
            "offline_freeze__source_embedded_direction_only_at_runtime"
        ),
        "runtime_source_evidence_rehashed": False,
        "observed_seconds_read_during_runtime_placement": False,
        "route_direction_certificate_error": route_certificate_error,
        "route_direction_certificate_path": (
            route_certificate.get("_certificate_path")
            if route_certificate is not None
            else _ROUTE_DIRECTION_CERTIFICATE_RELATIVE_PATH
        ),
        "route_direction_certificate_sha256": (
            route_certificate.get("_certificate_sha256")
            if route_certificate is not None
            else None
        ),
        "physical_parameter_identity": physical_identity.to_dict(),
        "physical_parameter_identity_digest": physical_identity.digest,
        "trusted_calibration_matched": trusted is not None,
        "trusted_calibration_exact_match_count": len(exact_matches),
        "trusted_calibration_ambiguous": len(exact_matches) > 1,
        "trusted_calibration_source_digest": (
            trusted.source_evidence_digest if trusted else None
        ),
        "calibration_source_exact_workload_identity_digest": (
            trusted.source_exact_workload_identity_digest if trusted else None
        ),
        "exact_calibration_match_requires": [
            "hardware_identity",
            "sampled_workload_fingerprint",
            "full_packed_workload_identity",
            "selection_limit",
            "minimum_distance",
            "maximum_distance",
            "verified_minimum_boundary",
            "verified_maximum_boundary",
            "expected_query_batches",
            "module_readiness",
            "index_readiness",
        ],
        "sampled_fingerprint_sufficient_for_calibration": False,
        "full_workload_identity_used_for_calibration": trusted is not None,
        "full_physical_parameter_identity_used_for_calibration": trusted is not None,
        "exact_route_runtime_content_binding": {
            "contract": "rtdl.exact_route_runtime_input_binding.v1",
            "enabled": exact_route_identity_bound,
            "reason": (
                "exact_same_hardware_cost_calibration"
                if trusted is not None
                else "route_did_not_depend_on_full_workload_identity"
            ),
            "prepared_search_object_and_full_content_revalidation_required_at_prepare": (
                exact_route_identity_bound
            ),
            "initial_query_object_and_full_content_revalidation_required_at_first_execute": (
                exact_route_identity_bound
            ),
            "runtime_revalidation_completed_during_planning": False,
            "repeated_query_batches_globally_content_bound": False,
            "generic_prepared_multi_batch_semantics_changed": False,
        },
        "sampled_direction_runtime_content_binding": {
            "enabled": bool(consensus_metadata["priority_override_applied"]),
            "full_content_identity_required": False,
            "reason": (
                "both_templates_independently_legal__sample_only_changes_priority"
                if consensus_metadata["priority_override_applied"]
                else "sampled_direction_override_not_applied"
            ),
            "sampled_fingerprint_is_semantic_identity": False,
            "sampled_fingerprint_is_seconds_calibration": False,
            "input_drift_can_change_correctness": False,
            "input_drift_can_change_realized_performance": True,
        },
        "candidate_backends": [
            _PRUNED_BACKEND,
            _FUSED_BACKEND,
            _GRID_BACKEND,
        ],
        "selected_backend": plan.selected_backend,
        "selected_template": lowered.template_kind,
        "cost_model_status": plan.cost_model_status.value,
        "cost_fallback_reason": plan.cost_fallback_reason,
        "default_fixed_priority_legal_order": list(
            _DEFAULT_FIXED_PRIORITY_LEGAL_ORDER
        ),
        "candidate_pruned_fixed_priority_legal_order": list(
            _CANDIDATE_PRUNED_FIXED_PRIORITY_LEGAL_ORDER
        ),
        "sampled_workload_route_consensus": consensus_metadata,
        "ranked_window_qk_native_symbol_probe": qk_symbol_probe.to_dict(),
        "candidate_pruned_native_symbol_probe": (
            pruned_symbol_probe.to_dict()
        ),
        "fused_point_native_symbol_probe": fused_symbol_probe.to_dict(),
        "runtime_native_library_identity": (
            dict(selected_symbol_probe.library_identity)
            if selected_symbol_probe.library_identity is not None
            else None
        ),
        "runtime_native_library_identity_selected_template_only": True,
        "prepared_max_distance_bound_hex": physical_identity.maximum_distance_hex,
        "prepared_max_distance_bound_derived_from_verified_maximum_parameter": True,
        "application_supplied_cost_or_backend": False,
        "functional_validation_only": (
            functional_validation_candidate is not None
        ),
        "functional_validation_candidate": functional_validation_candidate,
        "functional_validation_changes_production_priority": False,
        "production_default_plan": production_default_plan,
        "production_default_binding": production_default_binding,
        "canonical_resolution": canonical_resolution,
        "canonical_production_authority": canonical_authority,
        "action_name_used_for_dispatch": False,
        "raw_callback_accepted": False,
        "user_kernel_accepted": False,
        "arbitrary_ptx_accepted": False,
    }
    execution_trace = {
        "contract": "rtdl.action_compiler_execution_trace.private_candidate.v1",
        "semantic_digest": bound.compiled.spec.semantic_digest,
        "producer_kind": bound.producer_kind.value,
        "producer_binding_digest": bound.binding_digest,
        "target_profile": target_profile.to_metadata(),
        "plan": plan.to_dict(),
        "production_default": (
            {
                "plan": production_default_plan,
                "binding": production_default_binding,
                "behavioral_optix_claim_requires_post_execution_receipt": True,
                "partner_stage_can_satisfy_rt_claim": False,
                "canonical_resolution_is_selection_authority": (
                    canonical_authority is not None
                ),
                "legacy_default_is_compatibility_materializer_only": (
                    canonical_authority is not None
                ),
                "legacy_default_is_selection_authority": (
                    canonical_authority is None
                ),
                "canonical_resolution": canonical_resolution,
                "canonical_production_authority": canonical_authority,
            }
            if production_default_plan is not None
            else None
        ),
        "physical_registry": registry_metadata,
        "selected_backend": lowered.backend,
        "selected_placement": lowered.placement,
        "selected_template": lowered.template_kind,
        "template_preflight_rejections": [
            {"backend": backend, "reason": reason}
            for backend, reason in rejections
        ],
        "application_selected_backend": False,
        "raw_callback_accepted": False,
        "user_kernel_accepted": False,
        "arbitrary_ptx_accepted": False,
    }
    lowered = replace(lowered, compiler_execution_trace=execution_trace)
    planned = PlannedLoweredAction(
        plan=plan,
        lowered=lowered,
        target_profile=target_profile,
        template_preflight_rejections=tuple(rejections),
        compiler_native_library_identity=(
            selected_symbol_probe._library_identity_object
        ),
        _compiler_native_library_object_id=id(
            selected_symbol_probe._library_ref
        ),
        _compiler_native_library_ref=selected_symbol_probe._library_ref,
        compiler_prepared_input_digest=(
            search_full_identity
            if exact_route_identity_bound
            else prepared_search_digest
        ),
        compiler_prepared_input_digest_kind=(
            "packed_point_full_v1"
            if exact_route_identity_bound
            else "packed_point_sample_v1"
        ),
        _compiler_prepared_input_object_id=id(prepared_search_points),
        _compiler_prepared_input_ref=prepared_search_points,
        compiler_first_query_input_digest=(
            query_full_identity if exact_route_identity_bound else None
        ),
        compiler_first_query_input_digest_kind=(
            "packed_point_full_v1" if exact_route_identity_bound else None
        ),
        _compiler_first_query_input_object_id=(
            id(query_points) if exact_route_identity_bound else None
        ),
        _compiler_first_query_input_ref=(
            query_points if exact_route_identity_bound else None
        ),
    )
    return _reseal_planned_lowered_action(planned)


def plan_registered_point_bounded_selection(
    bound: BoundAction,
    target_profile: ActionTargetProfile,
    *,
    prepared_search_points,
    query_points,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, object],
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> PlannedLoweredAction:
    """Choose the production trusted physical template."""

    return _plan_registered_point_bounded_selection_impl(
        bound,
        target_profile,
        prepared_search_points=prepared_search_points,
        query_points=query_points,
        extents=extents,
        parameters=parameters,
        functional_validation_candidate=None,
        semantic_statement_stable_id=semantic_statement_stable_id,
        backend_contract_id=backend_contract_id,
    )


def plan_registered_point_bounded_selection_candidate_for_functional_validation(
    bound: BoundAction,
    target_profile: ActionTargetProfile,
    *,
    physical_candidate: str,
    prepared_search_points,
    query_points,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, object],
) -> PlannedLoweredAction:
    """Materialize one already registered candidate without changing priority."""

    planned = _plan_registered_point_bounded_selection_impl(
        bound,
        target_profile,
        prepared_search_points=prepared_search_points,
        query_points=query_points,
        extents=extents,
        parameters=parameters,
        functional_validation_candidate=physical_candidate,
        semantic_statement_stable_id=None,
        backend_contract_id=None,
    )
    if planned.lowered.backend != physical_candidate:
        raise RuntimeError(
            "compiler functional validation candidate was not selected"
        )
    return planned


def _query_count(extents: Mapping[ExtentKind | str, int]) -> int:
    for key, value in extents.items():
        name = key.value if isinstance(key, ExtentKind) else str(key)
        if name == ExtentKind.QUERY_COUNT.value:
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError("query_count must be a nonnegative integer")
            return value
    raise ValueError("query_count extent is required")


def _exact_calibration(
    backend: str,
    observed_seconds: float,
    row: _TrustedPointCalibration,
    *,
    search_count: int,
    query_count: int,
    state_bytes: int,
    output_bytes: int,
) -> ActionBackendCostCalibration:
    return ActionBackendCostCalibration(
        backend=backend,
        calibration_version=_CALIBRATION_VERSION,
        producer_kinds=(ActionProducerKind.PREPARED_POINT_CANDIDATES_3D.value,),
        resident_representations=(_REPRESENTATION,),
        min_search_count=search_count,
        max_search_count=search_count,
        min_query_count=query_count,
        max_query_count=query_count,
        max_expected_query_batches=row.expected_query_batches,
        min_candidate_density=row.candidate_density,
        max_candidate_density=row.candidate_density,
        max_state_bytes=state_bytes,
        max_output_bytes=output_bytes,
        max_h2d_bytes=0,
        max_d2h_bytes=0,
        fixed_prepare_seconds=0.0,
        module_prepare_seconds=0.0,
        index_prepare_seconds=0.0,
        per_search_prepare_seconds=0.0,
        fixed_query_seconds=0.0,
        per_query_seconds=0.0,
        per_candidate_seconds=0.0,
        per_state_byte_seconds=0.0,
        per_output_byte_seconds=0.0,
        per_h2d_byte_seconds=0.0,
        per_d2h_byte_seconds=0.0,
        uncertainty_fraction=0.05,
        uncertainty_seconds=0.0,
        source_evidence_digest=row.source_evidence_digest,
        transfer_calibration_eligible=False,
        mode=ActionCalibrationMode.EXACT_OBSERVED_TOTAL,
        observed_total_seconds=observed_seconds,
        exact_expected_query_batches=row.expected_query_batches,
        exact_module_ready=row.module_ready,
        exact_index_ready=row.index_ready,
        exact_state_bytes=state_bytes,
        exact_output_bytes=output_bytes,
    )


def trusted_registry_metadata() -> dict[str, object]:
    rows = [
        {
            "hardware_key": row.hardware_key,
            "workload_fingerprint_digest": row.workload_fingerprint_digest,
            "source_exact_workload_identity_digest": (
                row.source_exact_workload_identity_digest
            ),
            "source_evidence_digest": row.source_evidence_digest,
            "source_evidence_path": row.source_evidence_path,
            "observation_id": row.observation_id,
            "route_direction_certificate_digest": (
                row.route_direction_certificate_digest
            ),
            "controlled_modern_exact_observation": (
                row.controlled_modern_exact_observation
            ),
            "functional_only": row.functional_only,
            "direction_consensus_eligible": row.direction_consensus_eligible,
            "winner_backend": row.winner_backend,
            "clear_margin_threshold_met": row.clear_margin_threshold_met,
            "candidate_density": row.candidate_density,
            "fused_observed_total_seconds": row.fused_observed_total_seconds,
            "grid_observed_total_seconds": row.grid_observed_total_seconds,
            "physical_parameter_identity": {
                "limit": row.limit,
                "minimum_distance_hex": row.minimum_distance_hex,
                "maximum_distance_hex": row.maximum_distance_hex,
                "minimum_boundary": row.minimum_boundary,
                "maximum_boundary": row.maximum_boundary,
                "expected_query_batches": row.expected_query_batches,
                "module_ready": row.module_ready,
                "index_ready": row.index_ready,
            },
        }
        for row in _TRUSTED_EXACT_POINT_CALIBRATIONS
    ]
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    try:
        certificate = _validated_route_direction_certificate()
        certificate_valid = True
        certificate_error = None
        certificate_digest = certificate["_certificate_sha256"]
    except Exception as exc:
        certificate_valid = False
        certificate_error = f"{type(exc).__name__}:{exc}"
        certificate_digest = None
    return {
        "contract": ACTION_PHYSICAL_REGISTRY_VERSION,
        "registered_trusted_calibration_count": len(rows),
        "registry_digest": hashlib.sha256(payload.encode("ascii")).hexdigest(),
        "registry_digest_covers_every_entry_field": True,
        "route_direction_certificate_path": (
            _ROUTE_DIRECTION_CERTIFICATE_RELATIVE_PATH
        ),
        "route_direction_certificate_sha256": certificate_digest,
        "route_direction_certificate_valid": certificate_valid,
        "route_direction_certificate_error": certificate_error,
        "entries": rows,
        "application_mutable": False,
        "public_api": False,
    }


__all__ = (
    "ACTION_PHYSICAL_REGISTRY_VERSION",
    "compiler_hardware_calibration_key",
    "packed_point_workload_fingerprint",
    "packed_point_workload_identity",
    "plan_registered_point_bounded_selection",
    "plan_registered_point_bounded_selection_candidate_for_functional_validation",
    "trusted_registry_metadata",
    "validate_registered_point_prepare_contract",
)
