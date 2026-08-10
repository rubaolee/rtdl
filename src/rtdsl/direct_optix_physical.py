"""Generic direct physical access to existing RTDL OptiX native families.

This module contains no compiler, planner, registry, application, or paper
selection logic.  It owns only the prepare/execute/close lifetime for an
already-selected native physical family.
"""

from __future__ import annotations

import ctypes
import hashlib
import hmac
import math
import secrets
import struct
import time

from .action_native_identity import (
    ACTION_POINT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS,
    METRIC_KNN_3D_REQUIRED_SYMBOLS,
    native_library_identity,
    validate_native_library_identity,
)
from .optix_runtime import (
    OptixRowView,
    _RtdlFixedRadiusNeighborRow,
    _check_status,
    _load_optix_library,
)
from .verified_packed_points import (
    VerifiedUniqueU32PackedPoints,
    consume_verified_unique_u32_packed_points,
    issue_verified_unique_u32_packed_points,
)


_DIRECT_POINT_NATIVE_OBJECT_SECRET = secrets.token_bytes(32)
_MAX_BOUNDED_SELECTION_K = 64


def _pack_points_3d(
    points,
    *,
    path: str,
) -> VerifiedUniqueU32PackedPoints:
    """Return one exact proof; ordinary inputs retain full validation."""

    if type(points) is VerifiedUniqueU32PackedPoints:
        points.validate()
        if points.dimension != 3:
            raise ValueError(f"{path} requires 3-D points")
        return points
    return issue_verified_unique_u32_packed_points(
        points,
        dimension=3,
        path=path,
    )


def _f32(name: str, value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    try:
        return struct.unpack(">f", struct.pack(">f", number))[0]
    except OverflowError as error:
        raise ValueError(f"{name} must fit float32") from error


def _boundary_mode(boundary: str) -> int:
    if boundary == "closed":
        return 0
    if boundary == "open":
        return 1
    raise ValueError("boundary must be 'open' or 'closed'")


def _configure_symbols(library) -> None:
    prepare = getattr(
        library, "rtdl_optix_prepare_action_point_candidates_3d", None
    )
    run = getattr(
        library, "rtdl_optix_run_prepared_action_bounded_selection_3d", None
    )
    destroy = getattr(
        library, "rtdl_optix_destroy_prepared_action_point_candidates_3d", None
    )
    if prepare is None or run is None or destroy is None:
        raise RuntimeError(
            "loaded OptiX backend lacks the existing generic bounded-selection ABI"
        )
    prepare.restype = ctypes.c_int
    run.restype = ctypes.c_int
    destroy.argtypes = [ctypes.c_void_p]
    destroy.restype = None


class PreparedDirectOptixBoundedSelection3D:
    """Move-only owner for one explicitly selected generic physical family."""

    physical_family = "action_bounded_selection_3d"

    def __init__(
        self,
        search_points,
        *,
        max_distance_bound: float,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
        _native_library_loader=None,
    ) -> None:
        bound = _f32("max_distance_bound", max_distance_bound)
        if bound <= 0.0:
            raise ValueError("max_distance_bound must be positive")
        if (expected_native_library_identity is None) != (
            expected_native_library_ref is None
        ):
            raise ValueError(
                "expected native library identity and object must be provided together"
            )
        verified_search = _pack_points_3d(
            search_points, path="direct bounded-selection search"
        )
        search_lease = consume_verified_unique_u32_packed_points(
            verified_search,
            dimension=3,
        )
        self._search_count = int(search_lease.count)
        self._search_validation_metadata = dict(search_lease.metadata)
        self._max_distance_bound = bound
        self._handle = ctypes.c_void_p()
        self._closed = False

        library_loader = _native_library_loader or _load_optix_library
        library = library_loader()
        if expected_native_library_identity is not None:
            if library is not expected_native_library_ref:
                raise RuntimeError(
                    "loaded native library object differs from the bound object"
                )
            validate_native_library_identity(
                library, expected_native_library_identity
            )
            resolved_identity = expected_native_library_identity
        else:
            resolved_identity = native_library_identity(
                library,
                required_symbols=ACTION_POINT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS,
            )
        self._native_library_ref = library
        self._native_library_identity = resolved_identity
        self._native_library_object_id = id(library)
        self._native_library_object_binding_seal = hmac.new(
            _DIRECT_POINT_NATIVE_OBJECT_SECRET,
            (
                "rtdl.direct_optix_point_native_object.v1\x00"
                f"{self._native_library_object_id}\x00"
                f"{type(library).__module__}.{type(library).__qualname__}\x00"
                f"{resolved_identity.identity_digest}"
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        _configure_symbols(library)
        error = ctypes.create_string_buffer(4096)
        status = library.rtdl_optix_prepare_action_point_candidates_3d(
            search_lease.native_pointer,
            ctypes.c_size_t(search_lease.count),
            ctypes.c_double(self._max_distance_bound),
            ctypes.byref(self._handle),
            error,
            ctypes.c_size_t(len(error)),
        )
        _check_status(status, error)

    def _library_for_call(self):
        expected_seal = hmac.new(
            _DIRECT_POINT_NATIVE_OBJECT_SECRET,
            (
                "rtdl.direct_optix_point_native_object.v1\x00"
                f"{self._native_library_object_id}\x00"
                f"{type(self._native_library_ref).__module__}."
                f"{type(self._native_library_ref).__qualname__}\x00"
                f"{self._native_library_identity.identity_digest}"
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if (
            not hmac.compare_digest(
                self._native_library_object_binding_seal, expected_seal
            )
            or id(self._native_library_ref) != self._native_library_object_id
        ):
            raise RuntimeError(
                "direct prepared native library object binding changed"
            )
        validate_native_library_identity(
            self._native_library_ref, self._native_library_identity
        )
        return self._native_library_ref

    @property
    def search_count(self) -> int:
        return self._search_count

    @property
    def native_library_identity(self):
        return self._native_library_identity

    def run(
        self,
        query_points,
        *,
        minimum_distance: float,
        maximum_distance: float,
        k: int,
        minimum_boundary: str = "open",
        maximum_boundary: str = "open",
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("direct prepared OptiX handle is closed")
        verified_query = _pack_points_3d(
            query_points, path="direct bounded-selection query"
        )
        query_lease = consume_verified_unique_u32_packed_points(
            verified_query,
            dimension=3,
        )
        minimum = _f32("minimum_distance", minimum_distance)
        maximum = _f32("maximum_distance", maximum_distance)
        if minimum < 0.0 or maximum < minimum:
            raise ValueError("distance window must satisfy 0 <= minimum <= maximum")
        if maximum > self._max_distance_bound:
            raise ValueError("maximum_distance exceeds the prepared bound")
        if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k <= 64:
            raise ValueError("k must be an integer in [0, 64]")
        capacity = int(query_lease.count) * int(k)
        if capacity == 0 or query_lease.count == 0 or self._search_count == 0:
            return {
                "rows": (),
                "metadata": {
                    "contract": "rtdl.direct_optix_bounded_selection_3d.v1",
                    "physical_family": self.physical_family,
                    "native_symbol": None,
                    "native_elapsed_sec": 0.0,
                    "search_count": self._search_count,
                    "query_count": int(query_lease.count),
                    "bounded_output_capacity_rows": capacity,
                    "empty_shortcut": True,
                    "optix_traversal_expected": False,
                    "compiler_or_planner_used": False,
                    "registry_selection_used": False,
                    "search_validation_capability": dict(
                        self._search_validation_metadata
                    ),
                    "query_validation_capability": dict(query_lease.metadata),
                },
            }

        library = self._library_for_call()
        _configure_symbols(library)
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        started = time.perf_counter()
        status = library.rtdl_optix_run_prepared_action_bounded_selection_3d(
            self._handle,
            query_lease.native_pointer,
            ctypes.c_size_t(query_lease.count),
            ctypes.c_double(minimum),
            ctypes.c_double(maximum),
            ctypes.c_size_t(k),
            ctypes.c_uint32(_boundary_mode(minimum_boundary)),
            ctypes.c_uint32(_boundary_mode(maximum_boundary)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            ctypes.c_size_t(len(error)),
        )
        _check_status(status, error)
        elapsed = time.perf_counter() - started
        if row_count.value > capacity:
            if bool(rows_ptr):
                library.rtdl_optix_free_rows(rows_ptr)
            raise RuntimeError("native bounded-selection output exceeded capacity")
        view = OptixRowView(
            library=library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusNeighborRow,
            field_names=("query_id", "neighbor_id", "distance"),
        )
        try:
            rows = tuple(
                (row["query_id"], row["neighbor_id"], row["distance"])
                for row in view.to_dict_rows()
            )
        finally:
            view.close()
        return {
            "rows": rows,
            "metadata": {
                "contract": "rtdl.direct_optix_bounded_selection_3d.v1",
                "physical_family": self.physical_family,
                "native_symbol": (
                    "rtdl_optix_run_prepared_action_bounded_selection_3d"
                ),
                "native_elapsed_sec": elapsed,
                "search_count": self._search_count,
                "query_count": int(query_lease.count),
                "bounded_output_capacity_rows": capacity,
                "emitted_row_count": len(rows),
                "empty_shortcut": False,
                "optix_traversal_expected": True,
                "prepared_search_resident": True,
                "unbounded_candidate_relation_materialized": False,
                "bounded_output_downloaded": True,
                "compiler_or_planner_used": False,
                "registry_selection_used": False,
                "application_identity_used_for_dispatch": False,
                "publication_identity_used_for_dispatch": False,
                "search_validation_capability": dict(
                    self._search_validation_metadata
                ),
                "query_validation_capability": dict(query_lease.metadata),
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        library = self._library_for_call() if self._handle.value else None
        if self._handle.value:
            assert library is not None
            _configure_symbols(library)
            library.rtdl_optix_destroy_prepared_action_point_candidates_3d(
                self._handle
            )
        self._handle = ctypes.c_void_p()
        self._closed = True

    def __enter__(self) -> "PreparedDirectOptixBoundedSelection3D":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_direct_optix_bounded_selection_3d(
    search_points,
    *,
    max_distance_bound: float,
    expected_native_library_identity=None,
    expected_native_library_ref=None,
    _native_library_loader=None,
) -> PreparedDirectOptixBoundedSelection3D:
    return PreparedDirectOptixBoundedSelection3D(
        search_points,
        max_distance_bound=max_distance_bound,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
        _native_library_loader=_native_library_loader,
    )


_METRIC_KNN_KIND_CODE = {
    "euclidean_filter_refine": 0,
    "l_infinity_filter_refine": 1,
    "cosine_monotone_transform": 2,
}


def _configure_metric_knn_symbols(library) -> None:
    prepare = getattr(library, "rtdl_optix_prepare_metric_knn_3d", None)
    execute = getattr(library, "rtdl_optix_execute_prepared_metric_knn_3d", None)
    destroy = getattr(library, "rtdl_optix_destroy_prepared_metric_knn_3d", None)
    if prepare is None or execute is None or destroy is None:
        raise RuntimeError("loaded OptiX backend lacks generic prepared metric-kNN ABI")
    prepare.restype = ctypes.c_int
    execute.restype = ctypes.c_int
    destroy.argtypes = [ctypes.c_void_p]
    destroy.restype = None


class PreparedDirectOptixMetricKnn3D:
    """Move-only direct owner for app-neutral prepared metric-kNN traversal."""

    physical_family = "prepared_metric_knn_3d_optix"

    def __init__(
        self,
        search_points,
        *,
        initial_geometric_radius: float,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
        _native_library_loader=None,
    ) -> None:
        radius = _f32("initial_geometric_radius", initial_geometric_radius)
        if radius <= 0.0:
            raise ValueError("initial_geometric_radius must be positive")
        if (expected_native_library_identity is None) != (
            expected_native_library_ref is None
        ):
            raise ValueError(
                "expected native library identity and object must be provided together"
            )
        verified_search = _pack_points_3d(
            search_points, path="direct metric-kNN search"
        )
        search_lease = consume_verified_unique_u32_packed_points(
            verified_search, dimension=3
        )
        if search_lease.count == 0:
            raise ValueError("metric-kNN search points must be nonempty")
        self._search_count = int(search_lease.count)
        self._search_validation_metadata = dict(search_lease.metadata)
        self._initial_radius = radius
        self._handle = ctypes.c_void_p()
        self._closed = False

        library_loader = _native_library_loader or _load_optix_library
        library = library_loader()
        if expected_native_library_identity is not None:
            if library is not expected_native_library_ref:
                raise RuntimeError("loaded native library object differs from the bound object")
            validate_native_library_identity(library, expected_native_library_identity)
            resolved_identity = expected_native_library_identity
        else:
            resolved_identity = native_library_identity(
                library, required_symbols=METRIC_KNN_3D_REQUIRED_SYMBOLS
            )
        self._native_library_ref = library
        self._native_library_identity = resolved_identity
        self._native_library_object_id = id(library)
        self._native_library_object_binding_seal = hmac.new(
            _DIRECT_POINT_NATIVE_OBJECT_SECRET,
            (
                "rtdl.direct_optix_metric_knn_native_object.v1\x00"
                f"{self._native_library_object_id}\x00"
                f"{type(library).__module__}.{type(library).__qualname__}\x00"
                f"{resolved_identity.identity_digest}"
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        _configure_metric_knn_symbols(library)
        error = ctypes.create_string_buffer(4096)
        status = library.rtdl_optix_prepare_metric_knn_3d(
            search_lease.native_pointer,
            ctypes.c_size_t(search_lease.count),
            ctypes.c_double(radius),
            ctypes.byref(self._handle),
            error,
            ctypes.c_size_t(len(error)),
        )
        _check_status(status, error)

    def _library_for_call(self):
        expected_seal = hmac.new(
            _DIRECT_POINT_NATIVE_OBJECT_SECRET,
            (
                "rtdl.direct_optix_metric_knn_native_object.v1\x00"
                f"{self._native_library_object_id}\x00"
                f"{type(self._native_library_ref).__module__}."
                f"{type(self._native_library_ref).__qualname__}\x00"
                f"{self._native_library_identity.identity_digest}"
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if (
            not hmac.compare_digest(
                self._native_library_object_binding_seal, expected_seal
            )
            or id(self._native_library_ref) != self._native_library_object_id
        ):
            raise RuntimeError("direct metric-kNN native object binding changed")
        validate_native_library_identity(
            self._native_library_ref, self._native_library_identity
        )
        return self._native_library_ref

    @property
    def native_library_identity(self):
        return self._native_library_identity

    def run(
        self,
        query_points,
        *,
        metric_kind: str,
        k: int,
        maximum_rounds: int,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("direct prepared metric-kNN handle is closed")
        try:
            metric_code = _METRIC_KNN_KIND_CODE[str(metric_kind)]
        except KeyError as exc:
            raise ValueError("unsupported generic metric-kNN metric kind") from exc
        if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 64:
            raise ValueError("k must be an integer in [1,64]")
        if k > self._search_count:
            raise ValueError("k exceeds prepared search count")
        if (
            not isinstance(maximum_rounds, int)
            or isinstance(maximum_rounds, bool)
            or not 1 <= maximum_rounds <= 64
        ):
            raise ValueError("maximum_rounds must be an integer in [1,64]")
        verified_query = _pack_points_3d(
            query_points, path="direct metric-kNN query"
        )
        query_lease = consume_verified_unique_u32_packed_points(
            verified_query, dimension=3
        )
        if query_lease.count == 0:
            raise ValueError("metric-kNN query points must be nonempty")
        capacity = int(query_lease.count) * k

        library = self._library_for_call()
        _configure_metric_knn_symbols(library)
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        completed_round_count = ctypes.c_size_t()
        final_radius = ctypes.c_double()
        refit_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        started = time.perf_counter()
        status = library.rtdl_optix_execute_prepared_metric_knn_3d(
            self._handle,
            query_lease.native_pointer,
            ctypes.c_size_t(query_lease.count),
            ctypes.c_uint32(metric_code),
            ctypes.c_size_t(k),
            ctypes.c_double(self._initial_radius),
            ctypes.c_size_t(maximum_rounds),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            ctypes.byref(completed_round_count),
            ctypes.byref(final_radius),
            ctypes.byref(refit_count),
            error,
            ctypes.c_size_t(len(error)),
        )
        _check_status(status, error)
        elapsed = time.perf_counter() - started
        if row_count.value != capacity:
            if bool(rows_ptr):
                library.rtdl_optix_free_rows(rows_ptr)
            raise RuntimeError("native metric-kNN output did not contain query_count*k rows")
        view = OptixRowView(
            library=library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusNeighborRow,
            field_names=("query_id", "neighbor_id", "distance"),
        )
        try:
            rows = tuple(
                (row["query_id"], row["neighbor_id"], row["distance"])
                for row in view.to_dict_rows()
            )
        finally:
            view.close()
        return {
            "rows": rows,
            "metadata": {
                "contract": "rtdl.direct_optix_metric_knn_3d.v1",
                "physical_family": self.physical_family,
                "native_symbol": "rtdl_optix_execute_prepared_metric_knn_3d",
                "native_elapsed_sec": elapsed,
                "metric_kind": str(metric_kind),
                "search_count": self._search_count,
                "query_count": int(query_lease.count),
                "k": k,
                "completed_round_count": int(completed_round_count.value),
                "final_geometric_radius": float(final_radius.value),
                "native_refit_count": int(refit_count.value),
                "prepared_search_resident": True,
                "persistent_gas": True,
                "device_metric_filter": True,
                "device_topk": True,
                "unbounded_candidate_relation_materialized": False,
                "compiler_or_planner_used": False,
                "registry_selection_used": False,
                "application_identity_used_for_dispatch": False,
                "publication_identity_used_for_dispatch": False,
                "search_validation_capability": dict(
                    self._search_validation_metadata
                ),
                "query_validation_capability": dict(query_lease.metadata),
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        library = self._library_for_call() if self._handle.value else None
        if self._handle.value:
            assert library is not None
            _configure_metric_knn_symbols(library)
            library.rtdl_optix_destroy_prepared_metric_knn_3d(self._handle)
        self._handle = ctypes.c_void_p()
        self._closed = True

    def __enter__(self) -> "PreparedDirectOptixMetricKnn3D":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_direct_optix_metric_knn_3d(
    search_points,
    *,
    initial_geometric_radius: float,
    expected_native_library_identity=None,
    expected_native_library_ref=None,
    _native_library_loader=None,
) -> PreparedDirectOptixMetricKnn3D:
    return PreparedDirectOptixMetricKnn3D(
        search_points,
        initial_geometric_radius=initial_geometric_radius,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
        _native_library_loader=_native_library_loader,
    )


__all__ = [
    "PreparedDirectOptixBoundedSelection3D",
    "PreparedDirectOptixMetricKnn3D",
    "prepare_direct_optix_bounded_selection_3d",
    "prepare_direct_optix_metric_knn_3d",
]
