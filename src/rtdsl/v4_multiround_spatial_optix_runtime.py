"""Prepared runtime and compiler-owned controllers for Goal5761 M3."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import threading
import time
from typing import Sequence

import numpy as np

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_bounded_relation import materialize_bounded_relation
from .v4_multiround_spatial import (
    MultiRoundSpatialError,
    MultiRoundTelemetry,
    RadiusGraphComponentsRequest,
    RankedDistanceWindowRequest,
    VerifiedMultiRoundSpatialAuthority,
    bounded_radius_schedule,
    radius_graph_components_partner,
    ranked_distance_window_partner,
    validate_multiround_telemetry,
    verify_multiround_spatial_schema,
)
from .v4_multiround_spatial_optix_compiler import (
    VerifiedMultiRoundSpatialExecutable,
    consume_verified_multiround_spatial_executable,
)


class _Status(ctypes.Structure):
    _fields_ = [
        ("first_error_claimed", ctypes.c_uint32),
        ("error_code", ctypes.c_uint32),
        ("stage", ctypes.c_uint32),
        ("role", ctypes.c_uint32),
        ("launch_index", ctypes.c_uint64),
        ("error_site", ctypes.c_uint32),
        ("effect_tag", ctypes.c_uint32),
        ("nonce_word", ctypes.c_uint32),
        ("invocation_mask", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class MultiRoundSpatialResult:
    partner_algebra: str
    value: object
    candidate_rows: tuple[tuple[int, int], ...]
    round_candidate_counts: tuple[int, ...]
    role_counters_by_round: tuple[tuple[int, ...], ...]
    status_by_round: tuple[tuple[dict[str, int], ...], ...]
    telemetry: MultiRoundTelemetry
    traversal_receipt: dict[str, object]
    output_sha256: str
    native_library_sha256: str
    composed_ptx_sha256: str


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _native_path(library: object, explicit: str | Path | None) -> Path:
    candidate = explicit or os.environ.get("RTDL_OPTIX_LIB") \
        or getattr(library, "_name", None)
    if not candidate:
        raise RuntimeError("exact native library path is required")
    path = Path(candidate).resolve()
    if not path.is_file():
        raise RuntimeError("exact native library bytes are unavailable")
    return path


def _configure(library: object):
    prepare = getattr(
        library, "rtdl_optix_v4_prepare_multiround_spatial_callback_v1", None)
    execute = getattr(
        library, "rtdl_optix_v4_execute_multiround_spatial_callback_v1", None)
    destroy = getattr(
        library, "rtdl_optix_v4_destroy_multiround_spatial_callback_v1", None)
    if prepare is None or execute is None or destroy is None:
        raise RuntimeError("native library lacks Goal5761 prepared spatial ABI")
    prepare.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t, ctypes.c_float, ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    prepare.restype = ctypes.c_int
    execute.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t, ctypes.c_float, ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    execute.restype = ctypes.c_int
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    destroy.restype = ctypes.c_int
    return prepare, execute, destroy


def _points(points: Sequence[Sequence[float]], label: str):
    values = np.asarray(points, dtype=np.float32)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[1] not in (2, 3):
        raise ValueError(f"{label} must be nonempty Nx2 or Nx3")
    if not np.isfinite(values).all():
        raise ValueError(f"{label} contains nonfinite coordinates")
    if values.shape[1] == 2:
        values = np.column_stack((values, np.zeros(values.shape[0], dtype=np.float32)))
    values = np.ascontiguousarray(values, dtype=np.float32)
    flat = (ctypes.c_float * values.size)(*map(float, values.reshape(-1)))
    ids = (ctypes.c_uint32 * len(values))(*range(len(values)))
    return values, flat, ids


class PreparedMultiRoundSpatialOwner:
    """Live, single-process/thread owner of one exact prepared V4 program.

    The owner is deliberately not a cache key or a serializable receipt.  Its
    native token is valid only in the creating process and thread.  Dynamic
    query batches remain inputs to each execution; only the verified program,
    exact search geometry and native resources cross the call boundary.
    """

    def __init__(
        self,
        *,
        token: int,
        authority: VerifiedMultiRoundSpatialAuthority,
        search_points: np.ndarray,
        library: object,
        native_path: Path,
        composed_ptx_sha256: str,
        initial_radius: float,
        prepare_seconds: float,
        native_sha256: str | None = None,
    ) -> None:
        self._token = int(token)
        self._authority = authority
        self._search_points = search_points
        self._library = library
        self._native_path = native_path
        self._native_sha256 = (
            hashlib.sha256(native_path.read_bytes()).hexdigest()
            if native_sha256 is None
            else native_sha256
        )
        if (
            len(self._native_sha256) != 64
            or any(char not in "0123456789abcdef" for char in self._native_sha256)
        ):
            raise ValueError("native_sha256 must be a lowercase SHA-256 digest")
        self._composed_ptx_sha256 = composed_ptx_sha256
        self._initial_radius = float(initial_radius)
        self._prepare_seconds = float(prepare_seconds)
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._nonce = secrets.token_hex(16)
        self._active = threading.Lock()
        self._closed = False
        self._poisoned = False
        self._rounds = 0
        self._execution_count = 0
        self._cumulative_refit_count = 0
        self._cumulative_launch_count = 0
        self._cumulative_mutation_epoch = 0
        self._physical_radius = float(initial_radius)
        self._session_identity = _digest({
            "schema": "rtdl.v4.prepared_multiround_spatial_owner.v2",
            "authority": authority.authority_nonce,
            "search_points": hashlib.sha256(search_points.tobytes()).hexdigest(),
            "composed_ptx": composed_ptx_sha256,
            "native": self._native_sha256,
            "initial_radius_f32": self._initial_radius,
            "pid": self._pid,
            "thread": self._thread,
            "nonce": self._nonce,
        })

    @property
    def token(self) -> int:
        self._check_owner()
        return self._token

    @property
    def search_points(self) -> np.ndarray:
        self._check_owner()
        return self._search_points.copy()

    @property
    def session_identity(self) -> str:
        self._check_owner()
        return self._session_identity

    @property
    def prepare_seconds(self) -> float:
        return self._prepare_seconds

    @property
    def execution_count(self) -> int:
        return self._execution_count

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        self._check_owner()
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "authority_nonce": self._authority.authority_nonce,
            "composed_ptx_sha256": self._composed_ptx_sha256,
            "native_library_sha256": self._native_sha256,
            "search_geometry_sha256": hashlib.sha256(
                self._search_points.tobytes()).hexdigest(),
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "prepare_seconds_reported_separately": True,
            "cold_result_replaced": False,
            "execution_count": self._execution_count,
        }

    def __getstate__(self):
        raise RuntimeError("prepared spatial owner cannot be serialized")

    def _check_owner(self) -> None:
        if self._closed:
            raise RuntimeError("prepared spatial owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared spatial owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared spatial owner crossed thread boundary")
        if self._poisoned:
            raise RuntimeError("prepared spatial owner is poisoned after failed execution")

    def _enter_execution(self) -> None:
        self._check_owner()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared spatial owner is already executing")

    def _leave_execution(self, *, completed: bool) -> None:
        if completed:
            self._execution_count += 1
        else:
            # A native failure may occur after a refit or launch.  Continuing
            # would make the Python-side cumulative state speculative.
            self._poisoned = True
        self._active.release()

    def close(self) -> None:
        if self._closed:
            raise RuntimeError("prepared spatial owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared spatial owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared spatial owner crossed thread boundary")
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared spatial owner during execution")
        _, _, destroy = _configure(self._library)
        error = ctypes.create_string_buffer(16384)
        try:
            status = int(destroy(self._token, error, len(error)))
            self._closed = True
            self._token = 0
        finally:
            self._active.release()
        if status:
            raise RuntimeError(error.value.decode(errors="replace")
                               or f"prepared spatial destroy status {status}")

    def __enter__(self):
        if self._closed:
            raise RuntimeError("prepared spatial owner is closed")
        return self

    def __exit__(self, exc_type, exc, tb):
        if not self._closed:
            self.close()


def prepare_multiround_spatial_callback(
    authority: VerifiedMultiRoundSpatialAuthority,
    executable: VerifiedMultiRoundSpatialExecutable,
    *,
    any_hit_proof_authority,
    search_points: Sequence[Sequence[float]],
    initial_radius: float,
    library: object | None = None,
    native_library_path: str | Path | None = None,
) -> PreparedMultiRoundSpatialOwner:
    prepare_started = time.perf_counter()
    fresh = verify_multiround_spatial_schema(
        authority.relation,
        authority.relation_contract,
        authority.abi,
        authority.schema,
        any_hit_proof_authority=any_hit_proof_authority,
    )
    if fresh != authority:
        raise RuntimeError("multi-round spatial authority drift")
    if not math.isfinite(initial_radius) or initial_radius <= 0.0:
        raise ValueError("initial_radius must be finite and positive")
    composed_ptx = consume_verified_multiround_spatial_executable(
        executable, fresh, any_hit_proof_authority=any_hit_proof_authority)
    search, search_native, search_ids = _points(search_points, "search_points")
    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    native_path = _native_path(library, native_library_path)
    native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
    if native_sha != fresh.relation.physical.target.native_sha256:
        raise RuntimeError("executed native bytes do not match target authority")
    prepare, _, _ = _configure(library)
    token = ctypes.c_uint64()
    error = ctypes.create_string_buffer(16384)
    status = int(prepare(
        composed_ptx.encode(), search_native, search_ids, len(search),
        float(np.float32(initial_radius)), ctypes.byref(token), error, len(error)))
    if status or not token.value:
        raise RuntimeError(error.value.decode(errors="replace")
                           or f"prepared spatial prepare status {status}")
    return PreparedMultiRoundSpatialOwner(
        token=int(token.value), authority=fresh, search_points=search,
        library=library, native_path=native_path,
        composed_ptx_sha256=hashlib.sha256(composed_ptx.encode()).hexdigest(),
        initial_radius=float(np.float32(initial_radius)),
        prepare_seconds=time.perf_counter() - prepare_started,
        native_sha256=native_sha,
    )


def _execute_round(
    owner: PreparedMultiRoundSpatialOwner,
    query_points: np.ndarray,
    *, radius: float,
):
    if owner._closed:
        raise RuntimeError("prepared spatial owner is closed")
    _, query_native, query_ids = _points(query_points, "query_points")
    capacity = owner._authority.schema.maximum_event_capacity
    rows = (ctypes.c_uint32 * (capacity * 2))()
    raw_count = ctypes.c_uint64()
    overflow = ctypes.c_uint32()
    statuses = (_Status * len(query_points))()
    counters = (ctypes.c_uint64 * 7)()
    telemetry = (ctypes.c_uint64 * 8)()
    _, execute, _ = _configure(owner._library)
    error = ctypes.create_string_buffer(16384)
    status = int(execute(
        owner._token, query_native, query_ids, len(query_points),
        float(np.float32(radius)), capacity,
        ctypes.byref(raw_count), ctypes.byref(overflow), rows,
        statuses, counters, telemetry, error, len(error)))
    if status:
        raise RuntimeError(error.value.decode(errors="replace")
                           or f"prepared spatial execute status {status}")
    status_rows = tuple(
        {name: int(getattr(item, name)) for name, _ in _Status._fields_}
        for item in statuses)
    if any(item["first_error_claimed"] or item["error_code"] for item in status_rows):
        raise RuntimeError("prepared spatial returned nonzero callback status")
    counter_row = tuple(int(item) for item in counters)
    if counter_row[1] != len(query_points) or counter_row[6] != len(query_points) \
            or counter_row[4] + counter_row[5] != len(query_points):
        raise RuntimeError(f"prepared spatial lifecycle incomplete: {counter_row!r}")
    stored = min(int(raw_count.value), capacity)
    raw_rows = tuple((int(rows[i * 2]), int(rows[i * 2 + 1]))
                     for i in range(stored))
    canonical = materialize_bounded_relation(
        raw_rows,
        capacity=capacity,
        duplicate_policy=owner._authority.relation.schema.duplicate_policy,
        observed_raw_count=int(raw_count.value),
        overflowed=bool(overflow.value),
    )
    owner._rounds += 1
    return canonical, counter_row, status_rows, tuple(int(item) for item in telemetry)


def _telemetry(
    owner: PreparedMultiRoundSpatialOwner,
    native_values: tuple[int, ...],
    radii: tuple[float, ...],
) -> MultiRoundTelemetry:
    if native_values[0] != 1:
        raise RuntimeError("prepared spatial cumulative GAS build count changed")
    if native_values[1] < owner._cumulative_refit_count \
            or native_values[2] < owner._cumulative_launch_count \
            or native_values[5] < owner._cumulative_mutation_epoch:
        raise RuntimeError("prepared spatial cumulative telemetry regressed")
    refit_delta = native_values[1] - owner._cumulative_refit_count
    launch_delta = native_values[2] - owner._cumulative_launch_count
    mutation_delta = native_values[5] - owner._cumulative_mutation_epoch
    physical_radius = owner._physical_radius
    expected_refits = 0
    for radius in radii:
        radius_f32 = float(np.float32(radius))
        if radius_f32 != physical_radius:
            expected_refits += 1
        physical_radius = radius_f32
    result = MultiRoundTelemetry(
        prepared_token=owner._token,
        gas_build_count=1,
        gas_refit_count=refit_delta,
        launch_count=launch_delta,
        traversable_handle_first=native_values[3],
        traversable_handle_last=native_values[4],
        radii=radii,
    )
    validate_multiround_telemetry(
        result, expected_rounds=len(radii), expected_refits=expected_refits)
    if mutation_delta != expected_refits:
        raise RuntimeError("prepared spatial mutation epoch does not match refits")
    owner._cumulative_refit_count = native_values[1]
    owner._cumulative_launch_count = native_values[2]
    owner._cumulative_mutation_epoch = native_values[5]
    owner._physical_radius = physical_radius
    return result


def _execute_ranked_distance_window_unlocked(
    owner: PreparedMultiRoundSpatialOwner,
    query_points: Sequence[Sequence[float]],
    request: RankedDistanceWindowRequest,
) -> MultiRoundSpatialResult:
    if request.maximum_rounds > owner._authority.schema.maximum_rounds:
        raise MultiRoundSpatialError(
            "round_bound", "request.maximum_rounds", "exceeds verified authority")
    queries, _, _ = _points(query_points, "query_points")
    radii = bounded_radius_schedule(
        initial_radius=request.initial_radius,
        maximum_radius=request.maximum_distance,
        maximum_rounds=request.maximum_rounds,
    )
    audit = OptixTraversalAuditSession.open(library=owner._library)
    candidate_counts = []
    counters_by_round = []
    statuses_by_round = []
    final_rows: tuple[tuple[int, int], ...] = ()
    used_radii = []
    native_telemetry: tuple[int, ...] = ()
    try:
        for radius in radii:
            final_rows, counters, statuses, native_telemetry = _execute_round(
                owner, queries, radius=radius)
            used_radii.append(radius)
            candidate_counts.append(len(final_rows))
            counters_by_round.append(counters)
            statuses_by_round.append(statuses)
            selected = ranked_distance_window_partner(
                owner._search_points, queries, final_rows,
                k=request.k,
                minimum_distance=request.minimum_distance,
                maximum_distance=request.maximum_distance,
                boundary_policy=request.boundary_policy,
            )
            counts = [0] * len(queries)
            for query_id, _, _, _ in selected:
                counts[query_id] += 1
            if all(count >= request.k for count in counts) or radius == radii[-1]:
                break
        value = ranked_distance_window_partner(
            owner._search_points, queries, final_rows,
            k=request.k,
            minimum_distance=request.minimum_distance,
            maximum_distance=request.maximum_distance,
            boundary_policy=request.boundary_policy,
        )
        output_sha = _digest(value)
        receipt = audit.finish(
            semantic_digest=_digest({
                "authority": owner._authority.authority_nonce,
                "algebra": "ranked_distance_window_f32_v1",
                "request": {
                    **request.__dict__,
                    "boundary_policy": request.boundary_policy.value,
                },
                "radii": used_radii,
                "native": owner._native_sha256,
                "ptx": owner._composed_ptx_sha256,
            }),
            output_digest=output_sha,
            route_identity="v4_callback_ir:prepared_multiround_spatial_v1",
            expected_program_bundles=(
                "v4_custom_aabb_prepared_multiround_spatial_composed",),
        )
    except Exception:
        audit.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("ranked spatial controller lacked bound OptiX traversal")
    resolved_telemetry = _telemetry(owner, native_telemetry, tuple(used_radii))
    return MultiRoundSpatialResult(
        partner_algebra="ranked_distance_window_f32_v1",
        value=value,
        candidate_rows=final_rows,
        round_candidate_counts=tuple(candidate_counts),
        role_counters_by_round=tuple(counters_by_round),
        status_by_round=tuple(statuses_by_round),
        telemetry=resolved_telemetry,
        traversal_receipt=receipt,
        output_sha256=output_sha,
        native_library_sha256=owner._native_sha256,
        composed_ptx_sha256=owner._composed_ptx_sha256,
    )


def _execute_radius_graph_components_unlocked(
    owner: PreparedMultiRoundSpatialOwner,
    request: RadiusGraphComponentsRequest,
) -> MultiRoundSpatialResult:
    if request.maximum_rounds != 1:
        raise MultiRoundSpatialError(
            "component_rounds", "request.maximum_rounds",
            "fixed-radius component algebra requires exactly one traversal round")
    points = owner._search_points
    audit = OptixTraversalAuditSession.open(library=owner._library)
    try:
        rows, counters, statuses, native_telemetry = _execute_round(
            owner, points, radius=request.epsilon)
        value = radius_graph_components_partner(
            points, rows, epsilon=request.epsilon, min_points=request.min_points)
        serializable = {
            key: value[key] for key in (
                "edge_count", "edge_rows", "neighbor_counts", "core_flags",
                "canonical_component_labels")
        }
        output_sha = _digest(serializable)
        receipt = audit.finish(
            semantic_digest=_digest({
                "authority": owner._authority.authority_nonce,
                "algebra": "radius_graph_components_f32_v1",
                "request": request.__dict__,
                "native": owner._native_sha256,
                "ptx": owner._composed_ptx_sha256,
            }),
            output_digest=output_sha,
            route_identity="v4_callback_ir:prepared_multiround_spatial_v1",
            expected_program_bundles=(
                "v4_custom_aabb_prepared_multiround_spatial_composed",),
        )
    except Exception:
        audit.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("component spatial controller lacked bound OptiX traversal")
    resolved_telemetry = _telemetry(owner, native_telemetry, (float(request.epsilon),))
    return MultiRoundSpatialResult(
        partner_algebra="radius_graph_components_f32_v1",
        value=value,
        candidate_rows=rows,
        round_candidate_counts=(len(rows),),
        role_counters_by_round=(counters,),
        status_by_round=(statuses,),
        telemetry=resolved_telemetry,
        traversal_receipt=receipt,
        output_sha256=output_sha,
        native_library_sha256=owner._native_sha256,
        composed_ptx_sha256=owner._composed_ptx_sha256,
    )


def execute_ranked_distance_window(
    owner: PreparedMultiRoundSpatialOwner,
    query_points: Sequence[Sequence[float]],
    request: RankedDistanceWindowRequest,
) -> MultiRoundSpatialResult:
    """Execute one dynamic query batch under the explicit owner guard."""

    owner._enter_execution()
    completed = False
    try:
        result = _execute_ranked_distance_window_unlocked(
            owner, query_points, request)
        completed = True
        return result
    finally:
        owner._leave_execution(completed=completed)


def execute_radius_graph_components(
    owner: PreparedMultiRoundSpatialOwner,
    request: RadiusGraphComponentsRequest,
) -> MultiRoundSpatialResult:
    """Execute one component request under the explicit owner guard."""

    owner._enter_execution()
    completed = False
    try:
        result = _execute_radius_graph_components_unlocked(owner, request)
        completed = True
        return result
    finally:
        owner._leave_execution(completed=completed)


__all__ = [
    "MultiRoundSpatialResult", "PreparedMultiRoundSpatialOwner",
    "execute_radius_graph_components", "execute_ranked_distance_window",
    "prepare_multiround_spatial_callback",
]
