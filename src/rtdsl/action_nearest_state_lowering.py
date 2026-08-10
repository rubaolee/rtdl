from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import math
import secrets
import time
from typing import Mapping

import numpy as np

from .action_ir import ActionScalarKind, ActionScalarType, ActionSpec
from .action_composition import (
    UINT32_MAX,
    ActionConsumerCompositionKind,
    action_template_identity_digest,
    validate_certified_nearest_global_argmax_composition,
)
from .action_numba_continuation import (
    CERTIFIED_QUERY_MIN_ORDERING,
    compile_numba_certified_query_min_state,
)
from .action_value_validation import strict_u32_column


CERTIFIED_NEAREST_STATE_3D_TEMPLATE = "certified_nearest_state_3d"
CERTIFIED_NEAREST_STATE_3D_OPTIX_TRAVERSAL_TEMPLATE = (
    "certified_nearest_state_3d_optix_traversal"
)
CELL_MBR_EXACT_WITNESS_3D_BACKEND = "optix_cell_mbr_exact_witness"
CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE = (
    "cell_mbr_exact_witness_3d_optix_traversal"
)
INDEPENDENT_DISTANCE_MAX_ULPS = 1
_PREPARED_NEAREST_OWNER_SEAL_SECRET = secrets.token_bytes(32)
_POINT_COLUMN_DOMAIN_SEAL_SECRET = secrets.token_bytes(32)


class ImmutablePointColumnDomain3DCertificateError(ValueError):
    """Typed construction failure for an immutable point/ID column domain."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class ImmutablePointColumnDomain3DCertificate:
    """One-time proof for immutable F64x3 points and monotonic U32 IDs.

    The canonical columns are backed by immutable ``bytes`` objects.  Later
    compiler/backend/native layers can therefore validate their exact object
    and storage binding in O(1), instead of rescanning or sorting the same
    multi-million-row domain.  The supported public Python/NumPy API cannot
    replace sealed fields, make the arrays writeable, or issue a new seal.

    Arbitrary in-process TCB reflection (for example ``ctypes`` writes to a
    raw address, or ``object.__setattr__`` combined with calling private seal
    machinery from this internal module) can defeat Python-level immutability.
    Such code already has unrestricted process-memory authority and is outside
    this certificate's threat model; it must not be described as a supported
    application API or as hostile-process isolation.
    """

    __slots__ = (
        "_target_points",
        "_target_ids",
        "_point_storage",
        "_id_storage",
        "_point_object_id",
        "_id_object_id",
        "_point_storage_object_id",
        "_id_storage_object_id",
        "_target_count",
        "_id_ordering",
        "_lower_bounds",
        "_upper_bounds",
        "_target_content_digest",
        "_seal",
    )

    contract = "rtdl.immutable_point_column_domain_3d_certificate.v1"

    def __setattr__(self, name, value) -> None:
        raise AttributeError(
            "immutable point-column-domain certificate cannot be modified"
        )

    @property
    def target_points(self) -> np.ndarray:
        self.validate_exact(self._target_points, self._target_ids)
        return self._target_points

    @property
    def target_ids(self) -> np.ndarray:
        self.validate_exact(self._target_points, self._target_ids)
        return self._target_ids

    @property
    def target_count(self) -> int:
        self._validate_seal()
        return self._target_count

    @property
    def id_ordering(self) -> str:
        self._validate_seal()
        return self._id_ordering

    @property
    def dense_zero_based_ids(self) -> bool:
        self._validate_seal()
        return self._id_ordering == "dense_zero_based_monotonic_u32"

    @property
    def lower_bounds(self) -> tuple[float, float, float]:
        self._validate_seal()
        return self._lower_bounds

    @property
    def upper_bounds(self) -> tuple[float, float, float]:
        self._validate_seal()
        return self._upper_bounds

    @property
    def target_content_digest(self) -> str:
        self._validate_seal()
        return self._target_content_digest

    def identity_metadata(self) -> dict[str, object]:
        self.validate_exact(self._target_points, self._target_ids)
        return {
            "contract": self.contract,
            "target_count": self._target_count,
            "point_dtype": self._target_points.dtype.str,
            "point_shape": list(self._target_points.shape),
            "target_id_dtype": self._target_ids.dtype.str,
            "target_id_shape": list(self._target_ids.shape),
            "target_id_ordering": self._id_ordering,
            "target_content_digest": self._target_content_digest,
            "lower_bounds_f64_hex": [value.hex() for value in self._lower_bounds],
            "upper_bounds_f64_hex": [value.hex() for value in self._upper_bounds],
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            **self.identity_metadata(),
            "single_full_validation": True,
            "immutable_storage_kind": "python_bytes_backed_numpy_view",
            "subsequent_validation_kind": "sealed_exact_object_and_storage_binding_o1",
            "content_rescan_required_after_issue": False,
            "duplicate_id_scan_repeated_after_issue": False,
            "domain_validation_sort_repeated_after_issue": False,
        }

    def validate_exact(self, target_points, target_ids):
        self._validate_seal()
        if target_points is not self._target_points or target_ids is not self._target_ids:
            raise RuntimeError(
                "immutable point-column-domain certificate object binding changed"
            )
        if (
            id(self._target_points) != self._point_object_id
            or id(self._target_ids) != self._id_object_id
            or id(self._point_storage) != self._point_storage_object_id
            or id(self._id_storage) != self._id_storage_object_id
            or _immutable_array_storage_root(self._target_points)
            is not self._point_storage
            or _immutable_array_storage_root(self._target_ids) is not self._id_storage
            or self._target_points.dtype != np.dtype(np.float64)
            or self._target_ids.dtype != np.dtype(np.int64)
            or self._target_points.shape != (self._target_count, 3)
            or self._target_ids.shape != (self._target_count,)
            or not self._target_points.flags.c_contiguous
            or not self._target_ids.flags.c_contiguous
            or self._target_points.flags.writeable
            or self._target_ids.flags.writeable
        ):
            raise RuntimeError(
                "immutable point-column-domain certificate storage binding changed"
            )
        return self

    def _seal_payload(self) -> bytes:
        return (
            f"{self.contract}\x00{self._target_count}\x00{self._id_ordering}\x00"
            f"{self._target_content_digest}\x00{self._point_object_id}\x00"
            f"{self._id_object_id}\x00{self._point_storage_object_id}\x00"
            f"{self._id_storage_object_id}\x00"
            f"{','.join(value.hex() for value in self._lower_bounds)}\x00"
            f"{','.join(value.hex() for value in self._upper_bounds)}"
        ).encode("ascii")

    def _issue_seal(self) -> str:
        return hmac.new(
            _POINT_COLUMN_DOMAIN_SEAL_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_seal(self) -> None:
        try:
            expected = self._issue_seal()
            observed = self._seal
        except Exception as exc:
            raise RuntimeError(
                "immutable point-column-domain certificate fields are invalid"
            ) from exc
        if not hmac.compare_digest(observed, expected):
            raise RuntimeError(
                "immutable point-column-domain certificate seal changed"
            )


def _immutable_array_storage_root(array: np.ndarray):
    current = array
    seen: set[int] = set()
    while isinstance(current, np.ndarray):
        marker = id(current)
        if marker in seen:
            return None
        seen.add(marker)
        base = current.base
        if not isinstance(base, np.ndarray):
            return base
        current = base
    return None


def certify_immutable_point_column_domain_3d(
    target_points,
    target_ids=None,
) -> ImmutablePointColumnDomain3DCertificate:
    """Validate once, canonicalize, and seal an immutable point/ID domain."""

    try:
        points = np.array(target_points, dtype=np.float64, order="C", copy=True)
    except (TypeError, ValueError) as exc:
        raise ImmutablePointColumnDomain3DCertificateError(
            "target_matrix_required",
            "target points must be a finite nonempty F64[target_count][3] matrix",
        ) from exc
    if points.ndim != 2 or points.shape[1:] != (3,) or points.shape[0] == 0:
        raise ImmutablePointColumnDomain3DCertificateError(
            "target_matrix_required",
            f"target points must be a nonempty F64[target_count][3] matrix, got {points.shape}",
        )
    target_count = int(points.shape[0])
    if target_count > UINT32_MAX:
        raise ImmutablePointColumnDomain3DCertificateError(
            "target_count_u32_overflow",
            f"target_count {target_count} exceeds U32",
        )
    if not bool(np.all(np.isfinite(points))):
        raise ImmutablePointColumnDomain3DCertificateError(
            "target_finite_required",
            "target coordinates must be finite",
        )
    if target_ids is None:
        ids = np.arange(target_count, dtype=np.int64)
        ordering = "dense_zero_based_monotonic_u32"
    else:
        try:
            ids = strict_u32_column(
                target_ids,
                expected_length=target_count,
                require_unique=False,
            )
        except ValueError as exc:
            raise ImmutablePointColumnDomain3DCertificateError(
                "target_ids_invalid",
                f"target ids must be monotonic unique U32 values: {exc}",
            ) from exc
        if ids.size > 1 and bool(np.any(ids[1:] <= ids[:-1])):
            raise ImmutablePointColumnDomain3DCertificateError(
                "target_ids_invalid",
                "target ids must be strictly increasing (ordered and duplicate-free)",
            )
        ordering = (
            "dense_zero_based_monotonic_u32"
            if int(ids[0]) == 0 and int(ids[-1]) == target_count - 1
            else "strict_monotonic_u32"
        )

    lower_bounds = tuple(float(value) for value in np.min(points, axis=0))
    upper_bounds = tuple(float(value) for value in np.max(points, axis=0))
    point_storage = points.tobytes(order="C")
    id_storage = ids.tobytes(order="C")
    immutable_points = np.frombuffer(point_storage, dtype=np.float64).reshape(
        (target_count, 3)
    )
    immutable_ids = np.frombuffer(id_storage, dtype=np.int64)

    target_hasher = hashlib.sha256()
    target_hasher.update(b"rtdl.certified_nearest_target.v1\x00")
    target_hasher.update(immutable_points.dtype.str.encode("ascii"))
    target_hasher.update(str(tuple(immutable_points.shape)).encode("ascii"))
    target_hasher.update(point_storage)
    target_hasher.update(immutable_ids.dtype.str.encode("ascii"))
    target_hasher.update(id_storage)

    certificate = object.__new__(ImmutablePointColumnDomain3DCertificate)
    for name, value in (
        ("_target_points", immutable_points),
        ("_target_ids", immutable_ids),
        ("_point_storage", point_storage),
        ("_id_storage", id_storage),
        ("_point_object_id", id(immutable_points)),
        ("_id_object_id", id(immutable_ids)),
        ("_point_storage_object_id", id(point_storage)),
        ("_id_storage_object_id", id(id_storage)),
        ("_target_count", target_count),
        ("_id_ordering", ordering),
        ("_lower_bounds", lower_bounds),
        ("_upper_bounds", upper_bounds),
        ("_target_content_digest", target_hasher.hexdigest()),
    ):
        object.__setattr__(certificate, name, value)
    object.__setattr__(certificate, "_seal", certificate._issue_seal())
    certificate.validate_exact(immutable_points, immutable_ids)
    return certificate


def _f64_ulp_distance(left, right) -> np.ndarray:
    """Return elementwise IEEE-754 binary64 distance after zero normalization."""

    left_values = np.asarray(left, dtype=np.float64)
    right_values = np.asarray(right, dtype=np.float64)
    if left_values.shape != right_values.shape:
        raise ValueError("float64 ULP comparison requires equal shapes")
    if not np.all(np.isfinite(left_values)) or not np.all(np.isfinite(right_values)):
        raise ValueError("float64 ULP comparison requires finite values")

    def ordered(values: np.ndarray) -> np.ndarray:
        bits = values.view(np.uint64).copy()
        bits[values == 0.0] = np.uint64(0)
        sign = np.uint64(1) << np.uint64(63)
        return np.where(bits & sign, ~bits, bits | sign)

    left_ordered = ordered(left_values)
    right_ordered = ordered(right_values)
    return np.maximum(left_ordered, right_ordered) - np.minimum(
        left_ordered, right_ordered
    )


def _sampled_nearest_validation(
    observed_ids,
    observed_distances,
    expected_ids,
    expected_distances,
    *,
    max_distance_ulps: int = INDEPENDENT_DISTANCE_MAX_ULPS,
) -> dict[str, object]:
    """Compare exact witness identity with a bounded cross-device sqrt allowance."""

    if not isinstance(max_distance_ulps, int) or isinstance(max_distance_ulps, bool):
        raise ValueError("max_distance_ulps must be an integer")
    if max_distance_ulps < 0:
        raise ValueError("max_distance_ulps must be nonnegative")
    observed_id_values = np.asarray(observed_ids, dtype=np.int64)
    expected_id_values = np.asarray(expected_ids, dtype=np.int64)
    observed_distance_values = np.asarray(observed_distances, dtype=np.float64)
    expected_distance_values = np.asarray(expected_distances, dtype=np.float64)
    shapes = {
        observed_id_values.shape,
        expected_id_values.shape,
        observed_distance_values.shape,
        expected_distance_values.shape,
    }
    if len(shapes) != 1:
        raise ValueError("sampled nearest-state validation requires equal shapes")
    ulps = _f64_ulp_distance(observed_distance_values, expected_distance_values)
    id_mismatch = observed_id_values != expected_id_values
    distance_bit_mismatch = observed_distance_values != expected_distance_values
    distance_ulp_mismatch = ulps > np.uint64(max_distance_ulps)
    row_mismatch = id_mismatch | distance_ulp_mismatch
    return {
        "mismatch_count": int(np.count_nonzero(row_mismatch)),
        "candidate_id_mismatch_count": int(np.count_nonzero(id_mismatch)),
        "distance_bit_mismatch_count": int(np.count_nonzero(distance_bit_mismatch)),
        "distance_ulp_mismatch_count": int(np.count_nonzero(distance_ulp_mismatch)),
        "distance_max_ulp_error": int(np.max(ulps, initial=np.uint64(0))),
        "distance_max_ulp_tolerance": max_distance_ulps,
    }


@dataclass(frozen=True)
class CertifiedNearestStateProgram3D:
    """Verified per-query minimum semantics for an exact spatial producer."""

    spec: ActionSpec
    query_field: str
    candidate_field: str
    distance_field: str
    distance_state_name: str
    candidate_state_name: str
    termination_certificate: str

    def to_metadata(self) -> dict[str, object]:
        distance_spec = self.spec.event_type.field(self.distance_field)
        distance_kind = (
            distance_spec.value_type.kind.value
            if distance_spec is not None
            and isinstance(distance_spec.value_type, ActionScalarType)
            else "unknown"
        )
        return {
            "contract": "verified_action_certified_nearest_state_3d.v1",
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": CERTIFIED_NEAREST_STATE_3D_TEMPLATE,
            "effect_subset": ["per_query_state", "certified_termination"],
            "query_field": self.query_field,
            "candidate_field": self.candidate_field,
            "distance_field": self.distance_field,
            "distance_state_name": self.distance_state_name,
            "candidate_state_name": self.candidate_state_name,
            "termination_certificate": self.termination_certificate,
            "complete_cartesian_relation_materialized": False,
            "producer_state_bound": "O(query_count)",
            "distance_value_type": distance_kind,
            "physical_executor_kind": "compiler_selected_physical_candidate",
            "physical_placement": "compiler_selected_after_legality",
            "optix_traversal_used": None,
            "physical_candidate_bound_by_lowered_template": True,
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "raw_callback_accepted": False,
            "user_kernel_accepted": False,
            "arbitrary_ptx_accepted": False,
        }


def compile_certified_nearest_state_3d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
    discharged_termination_certificates: frozenset[str] = frozenset(),
) -> CertifiedNearestStateProgram3D:
    """Verify the closed query-min Action shape for an exact state producer.

    The shared query-min verifier is reused only for semantic shape checking.
    The physical producer returns final exact state columns and therefore does
    not materialize or expose the verifier's canonical event-row ordering.
    """

    verified = compile_numba_certified_query_min_state(
        spec,
        discharged_delivery_proofs=discharged_delivery_proofs,
        discharged_termination_certificates=discharged_termination_certificates,
        discharged_ordering_certificates=frozenset({CERTIFIED_QUERY_MIN_ORDERING}),
    )
    if verified.distance_state.value_type.kind is not ActionScalarKind.F64:
        raise ValueError(
            "certified native-CUDA nearest-state template requires an F64 distance contract"
        )
    return CertifiedNearestStateProgram3D(
        spec=spec,
        query_field=verified.query_field,
        candidate_field=verified.candidate_field,
        distance_field=verified.distance_field,
        distance_state_name=verified.distance_state.name,
        candidate_state_name=verified.candidate_state.name,
        termination_certificate=verified.termination_certificate,
    )


def _execute_certified_nearest_state_3d_host_projecting_legacy(
    planned_or_lowered,
    query_points,
    target_points,
    *,
    grid_shape=(32, 32, 32),
    independent_validation_sample_count: int = 64,
    query_domain_lower_bounds=None,
    query_domain_upper_bounds=None,
    optix_max_inline_points: int = 64,
    optix_max_heavy_point_evaluations: int = 1 << 30,
) -> dict[str, object]:
    """Execute a compiler-selected exact nearest-state physical template.

    The returned state is O(query_count); no source-target relation is built.
    The global max-witness stage reuses the established generic column reducer.
    """

    lowered = getattr(planned_or_lowered, "lowered", planned_or_lowered)
    backend = str(getattr(lowered, "backend", ""))
    template_kind = str(getattr(lowered, "template_kind", ""))
    if backend in {"optix", "cuda_grid", "optix_traversal"}:
        expected_template = (
            CERTIFIED_NEAREST_STATE_3D_OPTIX_TRAVERSAL_TEMPLATE
            if backend == "optix_traversal"
            else CERTIFIED_NEAREST_STATE_3D_TEMPLATE
        )
        if template_kind != expected_template:
            raise ValueError("native nearest-state execution requires the certified template")
        grid_executor = "native_cuda"
        nearest_executor = "native_cuda"
        physical_placement = (
            "traversal_device_continuation"
            if backend == "optix_traversal"
            else "device_continuation"
        )
        physical_executor = (
            "prepared_optix_cell_mbr_f64_nearest_with_bounded_device_continuation"
            if backend == "optix_traversal"
            else "native_cuda_grid_branch_bound"
        )
    elif backend == "cpu_reference":
        if template_kind != "cpu_reference_interpreter":
            raise ValueError("CPU nearest-state execution requires compiler reference fallback")
        grid_executor = "numpy"
        nearest_executor = "numba_parallel"
        physical_placement = "cpu_reference"
        physical_executor = "numpy_streaming_reference"
    else:
        raise ValueError("certified nearest-state execution requires compiler-selected OptiX or CPU reference")

    spec = lowered.compiled.spec
    distance_field = spec.event_type.field("distance")
    if (
        distance_field is None
        or not isinstance(distance_field.value_type, ActionScalarType)
        or distance_field.value_type.kind is not ActionScalarKind.F64
    ):
        raise ValueError("certified nearest-state physical route requires F64 distance semantics")
    query_matrix = _coordinate_matrix_3d(query_points, "query", dtype=np.float64)
    target_matrix = _coordinate_matrix_3d(target_points, "target", dtype=np.float64)
    if query_matrix.shape[0] == 0 or target_matrix.shape[0] == 0:
        raise ValueError("certified nearest-state execution requires non-empty point sets")
    shape = tuple(int(value) for value in grid_shape)
    if len(shape) != 3 or any(value <= 0 for value in shape):
        raise ValueError("grid_shape must contain three positive entries")

    query_columns = _point_columns(query_matrix)
    target_columns = _point_columns(target_matrix)
    grid_started = time.perf_counter()
    if grid_executor == "native_cuda":
        from .partner_continuations import point_grid_cell_mbrs_native_3d_cuda_columns

        grid = point_grid_cell_mbrs_native_3d_cuda_columns(
            target_columns,
            coordinate_fields=("x", "y", "z"),
            grid_shape=shape,
            cell_point_order="point-id",
            return_metadata=True,
        )
    else:
        grid = {
            "cell_columns": None,
            "metadata": {
                "contract": "cpu_streaming_exact_nearest_no_grid_required",
                "cell_count": 0,
            },
        }
    grid_seconds = time.perf_counter() - grid_started

    nearest_started = time.perf_counter()
    from .partner_continuations import (
        max_nearest_distance_witness_numpy_columns,
        seed_nearest_witness_from_grid_branch_bound_numpy_columns,
    )

    if nearest_executor == "native_cuda":
        nearest = seed_nearest_witness_from_grid_branch_bound_numpy_columns(
            query_columns,
            target_columns,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor=nearest_executor,
            return_metadata=True,
        )
    else:
        nearest = _streaming_exact_nearest_state(query_matrix, target_matrix)
    nearest_seconds = time.perf_counter() - nearest_started
    if nearest["metadata"].get("seed_quality") not in {
        "exact_nearest_witness_under_grid_cell_branch_bound",
        "exact_nearest_witness_streaming_reference",
    }:
        raise RuntimeError("nearest-state producer did not certify exact per-query witnesses")
    nearest_columns = nearest["columns"]
    source_ids = np.asarray(nearest_columns["source_ids"], dtype=np.int64)
    candidate_ids = np.asarray(nearest_columns["nearest_item_ids"], dtype=np.int64)
    distances = np.asarray(nearest_columns["nearest_distances"], dtype=np.float64)
    if source_ids.shape != candidate_ids.shape or source_ids.shape != distances.shape:
        raise RuntimeError("certified nearest-state columns have inconsistent shapes")
    if source_ids.shape != (query_matrix.shape[0],):
        raise RuntimeError("certified nearest-state row count does not match query count")
    if not np.array_equal(source_ids, np.arange(query_matrix.shape[0], dtype=np.int64)):
        raise RuntimeError("certified nearest-state source ids do not match query order")
    if np.any(candidate_ids < 0) or np.any(candidate_ids >= target_matrix.shape[0]):
        raise RuntimeError("certified nearest-state candidate ids are out of range")
    if not np.all(np.isfinite(distances)):
        raise RuntimeError("certified nearest-state distances must be finite")

    if not isinstance(independent_validation_sample_count, int) or isinstance(
        independent_validation_sample_count, bool
    ) or independent_validation_sample_count < 0:
        raise ValueError("independent_validation_sample_count must be nonnegative")
    if nearest_executor == "native_cuda" and independent_validation_sample_count:
        sample_count = min(independent_validation_sample_count, query_matrix.shape[0])
        sample_indices = np.unique(
            np.linspace(
                0,
                query_matrix.shape[0] - 1,
                num=sample_count,
                dtype=np.int64,
            )
        )
        sampled_reference = _streaming_exact_nearest_state(
            query_matrix[sample_indices], target_matrix
        )
        expected_ids = np.asarray(
            sampled_reference["columns"]["nearest_item_ids"], dtype=np.int64
        )
        expected_distances = np.asarray(
            sampled_reference["columns"]["nearest_distances"], dtype=np.float64
        )
        observed_ids = candidate_ids[sample_indices]
        observed_distances = distances[sample_indices]
        validation = _sampled_nearest_validation(
            observed_ids,
            observed_distances,
            expected_ids,
            expected_distances,
        )
        validation_mismatch_count = int(validation["mismatch_count"])
        if validation_mismatch_count:
            raise RuntimeError(
                "native nearest-state output failed independent sampled CPU parity"
            )
        validation_mode = "deterministic_cpu_streaming_sample__exact_id_f64_distance_1ulp"
        validated_source_count = int(sample_indices.size)
    elif nearest_executor == "native_cuda":
        validation_mode = "not_requested"
        validated_source_count = 0
        validation_mismatch_count = None
        validation = None
    else:
        validation_mode = "cpu_reference_is_physical_executor"
        validated_source_count = query_matrix.shape[0]
        validation_mismatch_count = 0
        validation = {
            "mismatch_count": 0,
            "candidate_id_mismatch_count": 0,
            "distance_bit_mismatch_count": 0,
            "distance_ulp_mismatch_count": 0,
            "distance_max_ulp_error": 0,
            "distance_max_ulp_tolerance": 0,
        }
    all_sources_independently_validated = (
        validated_source_count == query_matrix.shape[0]
        and validation_mismatch_count == 0
    )

    reduce_started = time.perf_counter()
    witness = max_nearest_distance_witness_numpy_columns(
        {
            "source_ids": source_ids,
            "nearest_item_ids": candidate_ids,
            "nearest_distances": distances,
        },
        return_metadata=True,
    )
    reduce_seconds = time.perf_counter() - reduce_started
    query_count = int(query_matrix.shape[0])
    target_count = int(target_matrix.shape[0])
    return {
        "actual": {
            "source_id": int(witness["source_id"]),
            "item_id": int(witness["item_id"]),
            "value": float(witness["value"]),
        },
        "metadata": {
            "contract": "rtdl.action.certified_nearest_state_3d_execution.v1",
            "selected_backend": backend,
            "selected_template": template_kind,
            "physical_executor_kind": physical_executor,
            "physical_placement": physical_placement,
            "optix_traversal_used": backend == "optix_traversal",
            "distance_value_type": "f64",
            "grid_executor": grid_executor,
            "nearest_executor": nearest["metadata"].get("executor"),
            "grid_contract": grid["metadata"].get("contract"),
            "nearest_contract": nearest["metadata"].get("contract"),
            "global_reducer_contract": witness["metadata"].get("contract"),
            "query_count": query_count,
            "target_count": target_count,
            "theoretical_cartesian_pair_count": query_count * target_count,
            "complete_cartesian_relation_materialized": False,
            "materialized_candidate_row_count": 0,
            "nearest_state_row_count": query_count,
            "nearest_state_bound": "O(query_count)",
            "nearest_state_output_space_bound": "O(query_count)",
            "runtime_work_worst_case_bound": "O(query_count * target_count)",
            "per_source_witness_exact_contract": True,
            "per_source_witness_exact": all_sources_independently_validated,
            "per_source_witness_independent_validation": validation_mode,
            "independently_validated_source_count": int(validated_source_count),
            "independent_validation_mismatch_count": validation_mismatch_count,
            "independent_validation_details": validation,
            "all_sources_independently_validated": all_sources_independently_validated,
            "global_witness_exact": all_sources_independently_validated,
            "global_witness_reducer_input_complete": True,
            "nearest_state_device_resident_through_global_reducer": False,
            "host_nearest_state_handoff_visible": True,
            "candidate_distance_evaluations": int(
                nearest["metadata"].get("candidate_distance_evaluations", 0)
            ),
            "grid_cell_probes": int(nearest["metadata"].get("grid_cell_probes", 0)),
            "scanned_cell_count": int(nearest["metadata"].get("scanned_cell_count", 0)),
            "phase_timings_sec": {
                "grid_cell_mbrs": grid_seconds,
                "exact_nearest_state": nearest_seconds,
                "global_max_witness": reduce_seconds,
            },
            "application_selected_backend": False,
            "app_semantics": "none",
            "runtime_speedup_claimed": False,
            "paper_performance_claimed": False,
        },
    }


class PreparedCertifiedNearestStateBackendOwner:
    """Compiler-created owner for one closed certified nearest-state template."""

    prepared_producer_kind = "certified_nearest_state_3d.v1"

    def __init__(
        self,
        lowered,
        target_points,
        *,
        consumer_composition,
        target_ids=None,
        column_domain_certificate=None,
        grid_shape=(32, 32, 32),
        independent_validation_sample_count: int = 64,
        query_domain_lower_bounds=None,
        query_domain_upper_bounds=None,
        optix_max_inline_points: int = 64,
        optix_max_heavy_point_evaluations: int = 1 << 30,
        cell_mbr_point_order: str = "point-id",
        prepared_target_domain: bool = False,
        physical_configuration_policy=None,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
    ) -> None:
        self._lowered = lowered
        self._backend = str(getattr(lowered, "backend", ""))
        template = str(getattr(lowered, "template_kind", ""))
        if self._backend in {"optix", "cuda_grid"}:
            if template != CERTIFIED_NEAREST_STATE_3D_TEMPLATE:
                raise ValueError(
                    "CUDA-grid nearest-state preparation requires the certified template"
                )
        elif self._backend == "optix_traversal":
            if template != CERTIFIED_NEAREST_STATE_3D_OPTIX_TRAVERSAL_TEMPLATE:
                raise ValueError(
                    "true-OptiX nearest-state preparation requires its certified traversal template"
                )
        elif self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND:
            if (
                template
                != CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE
            ):
                raise ValueError(
                    "cell-MBR exact-witness preparation requires its certified traversal template"
                )
        elif self._backend == "cpu_reference":
            if template != "cpu_reference_interpreter":
                raise ValueError(
                    "CPU nearest-state preparation requires compiler reference fallback"
                )
        else:
            raise ValueError(
                "certified nearest-state preparation requires a compiler-selected native route or CPU reference"
            )
        if consumer_composition is None:
            raise ValueError(
                "certified nearest-state backend owner requires an explicit consumer composition"
            )
        if (
            consumer_composition.kind
            is not ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
        ):
            raise ValueError("certified nearest-state backend owner received the wrong consumer")
        validate_certified_nearest_global_argmax_composition(
            consumer_composition,
            spec=lowered.compiled.spec,
            action_source_digest=lowered.compiled.source_digest,
            producer_kind=lowered.producer_kind.value,
            producer_binding_digest=lowered.producer_binding_digest,
            selected_backend=lowered.backend,
            selected_placement=lowered.placement,
            selected_template=lowered.template_kind,
            template_identity_digest=action_template_identity_digest(
                lowered.program.to_metadata()
                if hasattr(lowered.program, "to_metadata")
                else {"template": lowered.template_kind}
            ),
            query_count=consumer_composition.query_count,
        )
        self._consumer_composition = consumer_composition
        spec = lowered.compiled.spec
        distance_field = spec.event_type.field("distance")
        if (
            distance_field is None
            or not isinstance(distance_field.value_type, ActionScalarType)
            or distance_field.value_type.kind is not ActionScalarKind.F64
        ):
            raise ValueError(
                "certified nearest-state physical route requires F64 distance semantics"
            )
        if column_domain_certificate is not None:
            if not isinstance(
                column_domain_certificate,
                ImmutablePointColumnDomain3DCertificate,
            ):
                raise TypeError(
                    "column_domain_certificate must be compiler-issued for the exact point/ID objects"
                )
            column_domain_certificate.validate_exact(target_points, target_ids)
            target_matrix = column_domain_certificate.target_points
            target_id_values = column_domain_certificate.target_ids
            target_content_digest = (
                column_domain_certificate.target_content_digest
            )
            column_domain_certificate_reused = True
        else:
            # Compatibility/raw front door: preserve the complete independent
            # validation path.  Only compiler-issued immutable payloads may
            # bypass these scans.
            target_matrix = _coordinate_matrix_3d(
                target_points, "target", dtype=np.float64
            ).copy()
            if target_matrix.shape[0] == 0:
                raise ValueError("certified nearest-state target set must be nonempty")
            if int(target_matrix.shape[0]) > UINT32_MAX:
                raise ValueError("certified nearest-state target_count exceeds U32")
            if not np.all(np.isfinite(target_matrix)):
                raise ValueError("certified nearest-state target coordinates must be finite")
            if target_ids is None:
                target_id_values = np.arange(target_matrix.shape[0], dtype=np.int64)
            else:
                try:
                    target_id_values = strict_u32_column(
                        target_ids,
                        expected_length=int(target_matrix.shape[0]),
                        require_unique=True,
                    )
                except ValueError as exc:
                    raise ValueError(
                        "certified nearest-state target ids must be unique U32 values"
                    ) from exc
            if target_id_values.shape != (target_matrix.shape[0],):
                raise ValueError("target ids must match certified nearest-state targets")
            if (
                np.any(target_id_values < 0)
                or np.any(target_id_values > UINT32_MAX)
                or np.unique(target_id_values).size != target_id_values.size
            ):
                raise ValueError("certified nearest-state target ids must be unique U32 values")
            target_matrix.setflags(write=False)
            target_id_values.setflags(write=False)
            target_hasher = hashlib.sha256()
            target_hasher.update(b"rtdl.certified_nearest_target.v1\x00")
            target_hasher.update(target_matrix.dtype.str.encode("ascii"))
            target_hasher.update(str(tuple(target_matrix.shape)).encode("ascii"))
            target_hasher.update(target_matrix.tobytes(order="C"))
            target_hasher.update(target_id_values.dtype.str.encode("ascii"))
            target_hasher.update(target_id_values.tobytes(order="C"))
            target_content_digest = target_hasher.hexdigest()
            column_domain_certificate_reused = False
        shape = tuple(int(value) for value in grid_shape)
        if len(shape) != 3 or any(value <= 0 for value in shape):
            raise ValueError("grid_shape must contain three positive entries")
        if not isinstance(independent_validation_sample_count, int) or isinstance(
            independent_validation_sample_count, bool
        ) or independent_validation_sample_count < 0:
            raise ValueError("independent_validation_sample_count must be nonnegative")
        self._column_domain_certificate = column_domain_certificate
        self._column_domain_certificate_reused = column_domain_certificate_reused
        self._target_matrix = target_matrix
        self._target_ids = target_id_values
        if column_domain_certificate_reused:
            self._sorted_target_ids = target_id_values
        else:
            self._sorted_target_ids = np.sort(target_id_values).copy()
            self._sorted_target_ids.setflags(write=False)
        self._target_content_digest = target_content_digest
        self._grid_shape = shape
        self._validation_sample_count = independent_validation_sample_count
        self._native_owner = None
        if self._backend in {"optix", "cuda_grid"}:
            from .optix_runtime import (
                prepare_certified_nearest_global_witness_3d_cuda,
            )

            self._native_owner = prepare_certified_nearest_global_witness_3d_cuda(
                target_matrix,
                target_ids=target_id_values,
                column_domain_certificate=column_domain_certificate,
                grid_shape=shape,
                expected_native_library_identity=expected_native_library_identity,
                expected_native_library_ref=expected_native_library_ref,
            )
        elif self._backend == "optix_traversal":
            if (
                query_domain_lower_bounds is None
                or query_domain_upper_bounds is None
            ):
                raise ValueError(
                    "true-OptiX nearest-state preparation requires a certified query domain"
                )
            from .optix_runtime import (
                prepare_certified_nearest_global_witness_3d_optix,
            )

            self._native_owner = (
                prepare_certified_nearest_global_witness_3d_optix(
                    target_matrix,
                    target_ids=target_id_values,
                    column_domain_certificate=column_domain_certificate,
                    grid_shape=shape,
                    query_domain_lower_bounds=query_domain_lower_bounds,
                    query_domain_upper_bounds=query_domain_upper_bounds,
                    max_inline_points=optix_max_inline_points,
                    max_heavy_point_evaluations=(
                        optix_max_heavy_point_evaluations
                    ),
                    expected_native_library_identity=(
                        expected_native_library_identity
                    ),
                    expected_native_library_ref=expected_native_library_ref,
                )
            )
        elif self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND:
            from .action_cell_mbr_exact_witness_lowering import (
                prepare_cell_mbr_exact_witness_3d_optix,
            )

            self._native_owner = prepare_cell_mbr_exact_witness_3d_optix(
                target_matrix,
                target_ids=target_id_values,
                column_domain_certificate=column_domain_certificate,
                grid_shape=shape,
                max_inline_points=optix_max_inline_points,
                cell_point_order=cell_mbr_point_order,
                expected_native_library_identity=(
                    expected_native_library_identity
                ),
                expected_native_library_ref=expected_native_library_ref,
                prepared_target_domain=prepared_target_domain,
                physical_configuration_policy=physical_configuration_policy,
            )
        resolved_native_identity = (
            getattr(self._native_owner, "_native_library_identity", None)
            if self._native_owner is not None
            else None
        )
        resolved_native_library_ref = (
            getattr(self._native_owner, "_library", None)
            if self._native_owner is not None
            else None
        )
        if self._backend in {
            "optix",
            "cuda_grid",
            "optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_BACKEND,
        } and (
            resolved_native_identity is None
            or resolved_native_library_ref is None
            or (
                expected_native_library_identity is not None
                and resolved_native_identity != expected_native_library_identity
            )
            or (
                expected_native_library_ref is not None
                and resolved_native_library_ref is not expected_native_library_ref
            )
        ):
            raise RuntimeError(
                "prepared certified nearest native owner differs from the compiler binding"
            )
        self._native_library_identity = resolved_native_identity
        self._native_library_ref = resolved_native_library_ref
        self._native_prepare_symbol_name = (
            getattr(self._native_owner, "_prepare_symbol_name", None)
            if self._native_owner is not None
            else None
        )
        expected_prepare_symbol_name = (
            "rtdl_optix_prepare_certified_nearest_state_3d"
            if self._backend == "optix_traversal"
            else (
                "compiler_python_prepare_cell_mbr_exact_witness_3d_from_validated_columns"
                if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                else (
                    "rtdl_cuda_prepare_certified_nearest_grid_3d_from_validated_columns"
                    if column_domain_certificate_reused
                    else "rtdl_cuda_prepare_certified_nearest_grid_3d"
                )
            )
        )
        if self._backend in {
            "optix",
            "cuda_grid",
            "optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_BACKEND,
        } and (
            self._native_prepare_symbol_name != expected_prepare_symbol_name
        ):
            raise RuntimeError(
                "prepared certified nearest native prepare ABI differs from the column-domain contract"
            )
        self._native_owner_object_id = (
            id(self._native_owner) if self._native_owner is not None else None
        )
        self._native_library_object_id = (
            id(self._native_library_ref)
            if self._native_library_ref is not None
            else None
        )
        self._native_owner_binding_seal = self._issue_native_owner_binding_seal()
        self._closed = False
        self._execution_count = 0

    @property
    def closed(self) -> bool:
        return self._closed

    def _column_domain_reuse_metadata(self) -> dict[str, object]:
        certificate = self._column_domain_certificate
        certificate_metadata = (
            certificate.to_metadata() if certificate is not None else None
        )
        return {
            "target_column_domain_certificate_contract": (
                certificate_metadata.get("contract")
                if certificate_metadata is not None
                else None
            ),
            "target_column_domain_certificate_reused": (
                self._column_domain_certificate_reused
            ),
            "target_column_domain_certificate": certificate_metadata,
            "target_column_domain_single_full_validation": (
                certificate_metadata is not None
                and certificate_metadata.get("single_full_validation") is True
            ),
            "target_column_domain_validation_repeated": (
                not self._column_domain_certificate_reused
            ),
            "native_prepare_symbol": self._native_prepare_symbol_name,
        }

    def run(self, query_points) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared certified nearest-state owner is closed")
        self._validate_column_domain_binding()
        self._validate_native_owner_binding()
        query_matrix = _coordinate_matrix_3d(
            query_points, "query", dtype=np.float64
        ).copy()
        if query_matrix.shape[0] == 0:
            raise ValueError("certified nearest-state query set must be nonempty")
        if int(query_matrix.shape[0]) > UINT32_MAX:
            raise ValueError("certified nearest-state query_count exceeds U32")
        if int(query_matrix.shape[0]) != self._consumer_composition.query_count:
            raise ValueError(
                "certified nearest-state query_count violates the composition certificate"
            )
        if not np.all(np.isfinite(query_matrix)):
            raise ValueError("certified nearest-state query coordinates must be finite")
        sample_count = min(self._validation_sample_count, query_matrix.shape[0])
        sample_indices = (
            np.unique(
                np.linspace(
                    0,
                    query_matrix.shape[0] - 1,
                    num=sample_count,
                    dtype=np.int64,
                )
            )
            if sample_count
            else np.empty(0, dtype=np.int64)
        )
        if self._backend in {
            "optix",
            "cuda_grid",
            "optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_BACKEND,
        }:
            if self._native_owner is None:
                raise RuntimeError("prepared certified nearest native owner is unavailable")
            physical = self._native_owner.run(
                query_matrix,
                validation_sample_indices=sample_indices,
            )
            observed_ids = np.asarray(
                physical["validation_samples"]["nearest_item_ids"], dtype=np.int64
            )
            observed_distances = np.asarray(
                physical["validation_samples"]["nearest_distances"], dtype=np.float64
            )
            if sample_indices.size:
                sampled_reference = _streaming_exact_nearest_state(
                    query_matrix[sample_indices],
                    self._target_matrix,
                    target_ids=self._target_ids,
                )
                expected_ids = np.asarray(
                    sampled_reference["columns"]["nearest_item_ids"], dtype=np.int64
                )
                expected_distances = np.asarray(
                    sampled_reference["columns"]["nearest_distances"], dtype=np.float64
                )
                validation = _sampled_nearest_validation(
                    observed_ids,
                    observed_distances,
                    expected_ids,
                    expected_distances,
                )
            else:
                validation = None
            mismatch_count = (
                None if validation is None else int(validation["mismatch_count"])
            )
            if mismatch_count:
                raise RuntimeError(
                    "resident native nearest-state output failed independent sampled CPU parity"
                )
            validated_source_count = int(sample_indices.size)
            validation_mode = (
                "not_requested"
                if validation is None
                else "deterministic_cpu_streaming_sample__exact_id_f64_distance_1ulp"
            )
            actual = physical["actual"]
            native_metadata = physical["metadata"]
            column_domain_metadata = self._column_domain_reuse_metadata()
            for key, expected_value in column_domain_metadata.items():
                if key == "target_column_domain_certificate":
                    continue
                if native_metadata.get(key) != expected_value:
                    raise RuntimeError(
                        "prepared certified nearest native column-domain metadata differs"
                    )
            native_library_identity = native_metadata.get("native_library_identity")
            native_library_identity_digest = native_metadata.get(
                "native_library_identity_digest"
            )
            native_library_identity_revalidated = native_metadata.get(
                "native_library_identity_revalidated"
            )
            physical_executor = str(
                native_metadata.get(
                    "physical_executor_kind",
                    "native_cuda_prepared_grid_branch_bound_global_reducer",
                )
            )
            physical_placement = str(
                native_metadata.get(
                    "physical_placement",
                    "device_continuation",
                )
            )
            if self._backend == "optix_traversal":
                grid_executor = "prepared_optix_custom_primitive_gas"
                nearest_executor = (
                    "optix_anyhit_f64_plus_bounded_cuda_continuation"
                )
            elif self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND:
                grid_executor = "native_cuda_generic_point_grid_cell_mbrs"
                nearest_executor = (
                    "optix_cell_mbr_inline_nearest_plus_host_exact_continuation"
                )
            else:
                grid_executor = "native_cuda_prepared"
                nearest_executor = "native_cuda"
            candidate_evaluations = int(
                native_metadata["candidate_distance_evaluations"]
            )
            grid_probes = int(
                native_metadata.get(
                    "grid_cell_probes",
                    native_metadata.get("scanned_cell_count", 0),
                )
            )
            scanned_cells = int(native_metadata["scanned_cell_count"])
            phase_timings = dict(native_metadata["native_phase_timings_sec"])
            cell_count = int(native_metadata["cell_count"])
        else:
            state = _streaming_exact_nearest_state(
                query_matrix,
                self._target_matrix,
                target_ids=self._target_ids,
            )
            from .partner_continuations import (
                max_nearest_distance_witness_numpy_columns,
            )

            witness = max_nearest_distance_witness_numpy_columns(
                state["columns"], return_metadata=True
            )
            actual = {
                "source_id": int(witness["source_id"]),
                "item_id": int(witness["item_id"]),
                "value": float(witness["value"]),
            }
            # The CPU reference is itself the selected physical executor.  It is
            # exact, but it is not an *independent* comparator of its own result.
            validation = None
            mismatch_count = None
            validated_source_count = 0
            validation_mode = "not_applicable__cpu_reference_is_physical_executor"
            physical_executor = "numpy_streaming_reference"
            physical_placement = "cpu_reference"
            grid_executor = "numpy_no_grid"
            nearest_executor = "numpy_streaming_reference"
            candidate_evaluations = int(
                state["metadata"]["candidate_distance_evaluations"]
            )
            grid_probes = 0
            scanned_cells = 0
            phase_timings = {}
            cell_count = 0
            native_library_identity = None
            native_library_identity_digest = None
            native_library_identity_revalidated = False
            column_domain_metadata = self._column_domain_reuse_metadata()
        source_value = actual.get("source_id") if isinstance(actual, Mapping) else None
        item_value = actual.get("item_id") if isinstance(actual, Mapping) else None
        distance_value = actual.get("value") if isinstance(actual, Mapping) else None
        if (
            isinstance(source_value, (bool, np.bool_))
            or not isinstance(source_value, (int, np.integer))
            or isinstance(item_value, (bool, np.bool_))
            or not isinstance(item_value, (int, np.integer))
        ):
            raise RuntimeError(
                "certified nearest/global witness ids are not strict integers"
            )
        source_id = int(source_value)
        item_id = int(item_value)
        if (
            source_id < 0
            or source_id >= int(query_matrix.shape[0])
            or source_id > UINT32_MAX
            or item_id < 0
            or item_id > UINT32_MAX
        ):
            raise RuntimeError(
                "certified nearest/global witness escaped the query/U32 id contract"
            )
        target_position = int(np.searchsorted(self._sorted_target_ids, item_id))
        if (
            target_position >= int(self._sorted_target_ids.size)
            or int(self._sorted_target_ids[target_position]) != item_id
        ):
            raise RuntimeError(
                "certified nearest/global witness item is absent from the prepared target domain"
            )
        if (
            isinstance(distance_value, (bool, np.bool_))
            or not isinstance(distance_value, (int, float, np.integer, np.floating))
            or not math.isfinite(float(distance_value))
            or float(distance_value) < 0.0
        ):
            raise RuntimeError(
                "certified nearest/global witness distance must be finite and nonnegative"
            )
        actual = {
            "source_id": source_id,
            "item_id": item_id,
            "value": float(distance_value),
        }
        self._execution_count += 1
        query_count = int(query_matrix.shape[0])
        target_count = int(self._target_matrix.shape[0])
        all_sources_validated = (
            validated_source_count == query_count and mismatch_count == 0
        )
        if validated_source_count == 0:
            independent_validation_coverage = "none"
        elif all_sources_validated:
            independent_validation_coverage = "all_sources"
        else:
            independent_validation_coverage = "deterministic_sample"
        exactness_basis = (
            (
                (
                    "certified_complete_optix_cell_mbr_plus_bounded_heavy_continuation__complete_resident_global_reducer"
                    if self._backend == "optix_traversal"
                    else (
                        "certified_generic_cell_mbr_optix_frontier_plus_exact_host_continuation__complete_host_global_reducer"
                        if self._backend
                        == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                        else "certified_complete_grid_branch_bound__complete_resident_global_reducer"
                    )
                )
            )
            if self._backend
            in {
                "optix",
                "cuda_grid",
                "optix_traversal",
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
            }
            else "exact_cpu_streaming_reference__complete_host_global_reducer"
        )
        return {
            "actual": actual,
            "metadata": {
                "contract": "rtdl.action.certified_nearest_state_3d_execution.v3",
                "selected_backend": self._backend,
                "selected_template": self._lowered.template_kind,
                "physical_executor_kind": physical_executor,
                "physical_placement": physical_placement,
                "optix_traversal_used": (
                    self._backend
                    in {
                        "optix_traversal",
                        CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                    }
                ),
                "distance_value_type": "f64",
                "grid_executor": grid_executor,
                "nearest_executor": nearest_executor,
                "global_reducer_contract": "generic_max_nearest_distance_with_witness",
                "consumer_composition": self._consumer_composition.to_metadata(),
                "consumer_composition_digest": (
                    self._consumer_composition.composition_digest
                ),
                "consumer_composition_integrity_checked": True,
                "native_library_identity": native_library_identity,
                "native_library_identity_digest": native_library_identity_digest,
                "native_library_identity_revalidated": (
                    native_library_identity_revalidated
                ),
                "query_count": query_count,
                "target_count": target_count,
                "target_content_digest": self._target_content_digest,
                "target_input_copied_immutable": True,
                **column_domain_metadata,
                "cell_count": cell_count,
                "theoretical_cartesian_pair_count": query_count * target_count,
                "complete_cartesian_relation_materialized": False,
                "materialized_candidate_row_count": 0,
                "nearest_state_row_count": query_count,
                "nearest_state_bound": "O(query_count)",
                "nearest_state_output_space_bound": "O(query_count)",
                "runtime_work_worst_case_bound": "O(query_count * target_count)",
                "per_source_witness_exact_contract": True,
                # These two exactness fields describe the verified algorithm and
                # complete reducer contract.  Independent samples below are
                # empirical validation evidence, not the source of exactness.
                "per_source_witness_exact": True,
                "global_witness_exact": True,
                "algorithm_exactness_basis": exactness_basis,
                "independent_validation_is_algorithm_exactness_basis": False,
                "per_source_witness_independent_validation": validation_mode,
                "independently_validated_source_count": validated_source_count,
                "independent_validation_mismatch_count": mismatch_count,
                "independent_validation_details": validation,
                "all_sources_independently_validated": all_sources_validated,
                "independent_validation_coverage": independent_validation_coverage,
                "global_witness_reducer_input_complete": True,
                "target_and_grid_device_resident_for_prepared_lifetime": (
                    bool(
                        native_metadata.get(
                            "target_and_grid_device_resident_for_prepared_lifetime",
                            self._backend
                            in {"optix", "cuda_grid", "optix_traversal"},
                        )
                    )
                    if self._backend
                    in {
                        "optix",
                        "cuda_grid",
                        "optix_traversal",
                        CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                    }
                    else False
                ),
                "nearest_state_device_resident_through_global_reducer": (
                    bool(
                        native_metadata.get(
                            "nearest_state_device_resident_through_global_reducer",
                            self._backend
                            in {"optix", "cuda_grid", "optix_traversal"},
                        )
                    )
                    if self._backend
                    in {
                        "optix",
                        "cuda_grid",
                        "optix_traversal",
                        CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                    }
                    else False
                ),
                "host_nearest_state_handoff_visible": (
                    bool(
                        native_metadata.get(
                            "host_nearest_state_handoff_visible",
                            False,
                        )
                    )
                    if self._backend
                    == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else self._backend
                    not in {"optix", "cuda_grid", "optix_traversal"}
                ),
                "full_nearest_state_host_projection_used": (
                    bool(
                        native_metadata.get(
                            "full_nearest_state_host_projection_used",
                            False,
                        )
                    )
                    if self._backend
                    == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else self._backend
                    not in {"optix", "cuda_grid", "optix_traversal"}
                ),
                "bounded_witness_host_projection_rows": 1,
                "bounded_validation_sample_rows": validated_source_count,
                "candidate_distance_evaluations": candidate_evaluations,
                "grid_cell_probes": grid_probes,
                "scanned_cell_count": scanned_cells,
                "frontier_was_mandatory": (
                    bool(native_metadata.get("frontier_was_mandatory", False))
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "exact_seed_frontier_skipped": (
                    bool(native_metadata.get("exact_seed_frontier_skipped", True))
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "frontier_native_symbol": (
                    native_metadata.get("frontier_native_symbol")
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "frontier_row_count": (
                    int(native_metadata.get("frontier_row_count", 0))
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "frontier_row_capacity": (
                    int(native_metadata.get("frontier_row_capacity", 0))
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "frontier_capacity_policy": (
                    native_metadata.get("frontier_capacity_policy")
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                # Preserve the generic completion proof at the outer Action
                # boundary.  Without these fields a formal endpoint cannot
                # distinguish the verified zero-frontier passthrough from the
                # deliberately slower unverified all-row safety fallback.
                "completed_nearest_state_mode": (
                    native_metadata.get("completed_nearest_state_mode")
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "completed_nearest_state_capability_used": (
                    bool(
                        native_metadata.get(
                            "completed_nearest_state_capability_used",
                            False,
                        )
                    )
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else False
                ),
                "completed_nearest_state_producer_evidence": (
                    native_metadata.get(
                        "completed_nearest_state_producer_evidence"
                    )
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "verified_completed_nearest_state": (
                    native_metadata.get("verified_completed_nearest_state")
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                ),
                "unverified_zero_frontier_all_row_fallback_used": (
                    bool(
                        native_metadata.get(
                            "unverified_zero_frontier_all_row_fallback_used",
                            False,
                        )
                    )
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else False
                ),
                "ordinary_nonzero_frontier_continuation_unchanged": (
                    bool(
                        native_metadata.get(
                            "ordinary_nonzero_frontier_continuation_unchanged",
                            False,
                        )
                    )
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else False
                ),
                "missing_fallback_count": (
                    int(native_metadata.get("missing_fallback_count", 0))
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else 0
                ),
                "missing_fallback_distance_evaluations": (
                    int(
                        native_metadata.get(
                            "missing_fallback_distance_evaluations",
                            0,
                        )
                    )
                    if self._backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else 0
                ),
                "phase_timings_sec": phase_timings,
                "native_subphase_component_calibration_eligible": False,
                "native_subphase_component_calibration_ineligible_reason": (
                    "native buffer destruction and complete synchronization attribution "
                    "are outside the reported subphase intervals"
                    if self._backend
                    in {
                        "optix",
                        "cuda_grid",
                        "optix_traversal",
                        CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                    }
                    else "CPU reference subphases are not independently attributed"
                ),
                "prepared_execution_count": self._execution_count,
                "stream_ordering": "synchronous_default_stream.v1",
                "application_selected_backend": False,
                "app_semantics": "none",
                "runtime_speedup_claimed": False,
                "paper_performance_claimed": False,
            },
        }

    def to_metadata(self) -> dict[str, object]:
        if not self._closed:
            self._validate_column_domain_binding()
            self._validate_native_owner_binding()
        column_domain_metadata = self._column_domain_reuse_metadata()
        return {
            "contract": "rtdl.action.prepared_certified_nearest_state_backend_owner.v1",
            "producer_kind": self.prepared_producer_kind,
            "backend": self._backend,
            "target_count": int(self._target_matrix.shape[0]),
            "target_content_digest": self._target_content_digest,
            "target_input_copied_immutable": True,
            **column_domain_metadata,
            "grid_shape": self._grid_shape,
            "independent_validation_sample_count": self._validation_sample_count,
            "consumer_composition": self._consumer_composition.to_metadata(),
            "consumer_composition_digest": (
                self._consumer_composition.composition_digest
            ),
            "native_library_identity": (
                self._native_library_identity.to_metadata()
                if self._native_library_identity is not None
                else None
            ),
            "native_library_identity_digest": (
                self._native_library_identity.identity_digest
                if self._native_library_identity is not None
                else None
            ),
            "native_owner_object_bound": self._backend
            in {
                "optix",
                "cuda_grid",
                "optix_traversal",
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
            },
            "native_owner_runtime_revalidation_required": self._backend
            in {
                "optix",
                "cuda_grid",
                "optix_traversal",
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
            },
            "execution_count": self._execution_count,
            "closed": self._closed,
            "target_and_grid_device_resident_for_prepared_lifetime": (
                self._backend in {"optix", "cuda_grid", "optix_traversal"}
            ),
            "application_selected_backend": False,
        }

    def close(self) -> None:
        if self._closed:
            return
        self._validate_column_domain_binding()
        self._validate_native_owner_binding()
        native = self._native_owner
        if native is not None:
            native.close()
        self._native_owner = None
        self._closed = True

    def _native_owner_binding_payload(self) -> bytes:
        identity_digest = (
            self._native_library_identity.identity_digest
            if self._native_library_identity is not None
            else "none"
        )
        certificate = self._column_domain_certificate
        certificate_binding = (
            f"{id(certificate)}:{certificate.target_content_digest}"
            if certificate is not None
            else "none"
        )
        return (
            "rtdl.prepared_certified_nearest_owner_binding.v1\x00"
            f"{self._backend}\x00{self._native_owner_object_id}\x00"
            f"{self._native_library_object_id}\x00{identity_digest}\x00"
            f"{certificate_binding}\x00{self._native_prepare_symbol_name}"
        ).encode("ascii")

    def _issue_native_owner_binding_seal(self) -> str:
        return hmac.new(
            _PREPARED_NEAREST_OWNER_SEAL_SECRET,
            self._native_owner_binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_native_owner_binding(self) -> None:
        expected_seal = self._issue_native_owner_binding_seal()
        if not hmac.compare_digest(
            self._native_owner_binding_seal, expected_seal
        ):
            raise RuntimeError(
                "prepared certified nearest native owner binding seal changed"
            )
        if self._backend not in {
            "optix",
            "cuda_grid",
            "optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_BACKEND,
        }:
            if self._native_owner is not None or self._native_library_ref is not None:
                raise RuntimeError(
                    "CPU prepared certified nearest owner gained a native owner"
                )
            return
        native = self._native_owner
        if (
            native is None
            or id(native) != self._native_owner_object_id
            or getattr(native, "_library", None) is not self._native_library_ref
            or id(self._native_library_ref) != self._native_library_object_id
            or getattr(native, "_native_library_identity", None)
            != self._native_library_identity
        ):
            raise RuntimeError(
                "prepared certified nearest native owner object binding changed"
            )

    def _validate_column_domain_binding(self) -> None:
        certificate = self._column_domain_certificate
        if not self._column_domain_certificate_reused:
            if certificate is not None:
                raise RuntimeError(
                    "raw prepared certified nearest owner gained a column-domain certificate"
                )
            return
        if not isinstance(certificate, ImmutablePointColumnDomain3DCertificate):
            raise RuntimeError(
                "prepared certified nearest column-domain certificate changed"
            )
        certificate.validate_exact(self._target_matrix, self._target_ids)
        if (
            self._sorted_target_ids is not self._target_ids
            or certificate.target_content_digest != self._target_content_digest
        ):
            raise RuntimeError(
                "prepared certified nearest column-domain binding changed"
            )


def prepare_certified_nearest_state_backend_owner(
    lowered,
    target_points,
    *,
    consumer_composition,
    target_ids=None,
    column_domain_certificate=None,
    grid_shape=(32, 32, 32),
    independent_validation_sample_count: int = 64,
    query_domain_lower_bounds=None,
    query_domain_upper_bounds=None,
    optix_max_inline_points: int = 64,
    optix_max_heavy_point_evaluations: int = 1 << 30,
    cell_mbr_point_order: str = "point-id",
    prepared_target_domain: bool = False,
    physical_configuration_policy=None,
    expected_native_library_identity=None,
    expected_native_library_ref=None,
) -> PreparedCertifiedNearestStateBackendOwner:
    """Prepare the closed producer selected by the compiler plan."""

    return PreparedCertifiedNearestStateBackendOwner(
        lowered,
        target_points,
        consumer_composition=consumer_composition,
        target_ids=target_ids,
        column_domain_certificate=column_domain_certificate,
        grid_shape=grid_shape,
        independent_validation_sample_count=independent_validation_sample_count,
        query_domain_lower_bounds=query_domain_lower_bounds,
        query_domain_upper_bounds=query_domain_upper_bounds,
        optix_max_inline_points=optix_max_inline_points,
        optix_max_heavy_point_evaluations=(
            optix_max_heavy_point_evaluations
        ),
        cell_mbr_point_order=cell_mbr_point_order,
        prepared_target_domain=prepared_target_domain,
        physical_configuration_policy=physical_configuration_policy,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
    )


def execute_certified_nearest_state_3d(
    planned_or_lowered,
    query_points,
    target_points,
    *,
    grid_shape=(32, 32, 32),
    independent_validation_sample_count: int = 64,
) -> dict[str, object]:
    """One-shot compatibility front door backed by the prepared native owner."""

    lowered = getattr(planned_or_lowered, "lowered", planned_or_lowered)
    consumer_composition = getattr(
        planned_or_lowered, "consumer_composition", None
    )
    expected_native_library_identity = getattr(
        planned_or_lowered, "compiler_native_library_identity", None
    )
    expected_native_library_ref = getattr(
        planned_or_lowered, "_compiler_native_library_ref", None
    )
    owner = prepare_certified_nearest_state_backend_owner(
        lowered,
        target_points,
        consumer_composition=consumer_composition,
        grid_shape=grid_shape,
        independent_validation_sample_count=independent_validation_sample_count,
        query_domain_lower_bounds=(
            np.min(
                _coordinate_matrix_3d(
                    query_points, "query", dtype=np.float64
                ),
                axis=0,
            )
            if str(getattr(lowered, "backend", ""))
            == "optix_traversal"
            else None
        ),
        query_domain_upper_bounds=(
            np.max(
                _coordinate_matrix_3d(
                    query_points, "query", dtype=np.float64
                ),
                axis=0,
            )
            if str(getattr(lowered, "backend", ""))
            == "optix_traversal"
            else None
        ),
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
    )
    try:
        return owner.run(query_points)
    finally:
        owner.close()


def _coordinate_matrix_3d(points, label: str, *, dtype) -> np.ndarray:
    matrix = np.asarray(points, dtype=dtype)
    if matrix.ndim != 2 or matrix.shape[1] != 3:
        raise ValueError(f"{label} points must be an Nx3 numeric matrix")
    return np.ascontiguousarray(matrix)


def _point_columns(matrix: np.ndarray) -> Mapping[str, object]:
    return {
        "ids": np.arange(matrix.shape[0], dtype=np.int64),
        "x": matrix[:, 0],
        "y": matrix[:, 1],
        "z": matrix[:, 2],
        "coordinate_matrix": matrix,
        "coordinate_matrix_fields": ("x", "y", "z"),
    }


def _streaming_exact_nearest_state(
    query_matrix: np.ndarray,
    target_matrix: np.ndarray,
    *,
    target_ids=None,
) -> dict[str, object]:
    best_ids = np.empty(query_matrix.shape[0], dtype=np.int64)
    best_distances = np.empty(query_matrix.shape[0], dtype=np.float64)
    if target_ids is None:
        target_id_values = np.arange(target_matrix.shape[0], dtype=np.int64)
    else:
        target_id_values = np.ascontiguousarray(target_ids, dtype=np.int64)
        if target_id_values.shape != (target_matrix.shape[0],):
            raise ValueError("streaming nearest target_ids must match target rows")
    evaluations = 0
    for query_index, query in enumerate(query_matrix):
        deltas = target_matrix - query
        distances_sq = np.einsum("ij,ij->i", deltas, deltas)
        best_sq = float(np.min(distances_sq))
        tied = target_id_values[distances_sq == best_sq]
        best_ids[query_index] = int(np.min(tied))
        best_distances[query_index] = float(np.sqrt(best_sq))
        evaluations += int(target_matrix.shape[0])
    return {
        "columns": {
            "source_ids": np.arange(query_matrix.shape[0], dtype=np.int64),
            "nearest_item_ids": best_ids,
            "nearest_distances": best_distances,
            "seed_cell_ids": np.full(query_matrix.shape[0], -1, dtype=np.int64),
        },
        "metadata": {
            "contract": "generic_streaming_exact_nearest_state_reference",
            "executor": "numpy_streaming_reference",
            "seed_quality": "exact_nearest_witness_streaming_reference",
            "candidate_distance_evaluations": evaluations,
            "grid_cell_probes": 0,
            "scanned_cell_count": 0,
            "complete_cartesian_relation_materialized": False,
            "app_semantics": "none",
        },
    }


__all__ = (
    "CERTIFIED_NEAREST_STATE_3D_TEMPLATE",
    "CertifiedNearestStateProgram3D",
    "PreparedCertifiedNearestStateBackendOwner",
    "compile_certified_nearest_state_3d",
    "execute_certified_nearest_state_3d",
    "prepare_certified_nearest_state_backend_owner",
)
