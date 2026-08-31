"""Optimized app-neutral lowering for the canonical V4 radius-graph callback.

The general V4 multi-round runtime materializes callback-emitted candidate
rows on the host.  That is the correct fallback for arbitrary callbacks, but
it is unnecessarily expensive for the closed canonical callback whose only
effect is ``emit(source_id, primitive_id)`` followed by the standard exact
radius-graph component algebra.  This module proves that exact callback shape
and lowers it to the existing prepared OptiX grouped-union + Numba device
partner.  No application name, dataset identity, or outcome is inspected.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import threading
import time

import numpy as np

from .component_partition import canonical_partition_labels
from .optix_runtime import _load_optix_library
from .partner_adapters import (
    prepare_optix_numba_radius_graph_grouped_stream_continuation_3d,
    radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns,
)
from .physical_execution_provenance import OptixTraversalAuditSession
from .reference import Point3D
from .v4_multiround_spatial import VerifiedMultiRoundSpatialAuthority
from .v4_multiround_spatial_optix_compiler import (
    VerifiedMultiRoundSpatialExecutable,
    consume_verified_multiround_spatial_executable,
)
from .v4_spatial_candidate_callback import compile_callback as compile_canonical_callback


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class OptimizedRadiusGraphComponentsResult:
    value: dict[str, object]
    traversal_receipt: dict[str, object]
    native_library_sha256: str
    callback_ptx_sha256: str
    exact_edge_count: int
    physical_lowering: str = (
        "canonical_v4_spatial_emit_to_prepared_optix_grouped_union_numba_v1")


class PreparedVerifiedRadiusGraphGroupedV4:
    """Live owner of one verified canonical callback and grouped device plan."""

    def __init__(
        self,
        authority: VerifiedMultiRoundSpatialAuthority,
        executable: VerifiedMultiRoundSpatialExecutable,
        *,
        any_hit_proof_authority,
        points: np.ndarray,
        radius: float,
        native_library_path: str | Path,
    ) -> None:
        if not isinstance(authority, VerifiedMultiRoundSpatialAuthority):
            raise TypeError("verified multi-round authority is required")
        if not isinstance(executable, VerifiedMultiRoundSpatialExecutable):
            raise TypeError("live verified multi-round executable is required")
        canonical = compile_canonical_callback()
        callback = authority.relation.physical.callback
        if callback.ir_sha256 != canonical.ir_sha256 \
                or callback.effect_digest != canonical.effect_digest:
            raise RuntimeError(
                "grouped lowering accepts only the canonical V4 spatial emit callback")
        point_values = np.ascontiguousarray(points, dtype=np.float32)
        if point_values.ndim != 2 or point_values.shape[1] != 3 \
                or not len(point_values) or not np.isfinite(point_values).all():
            raise ValueError("finite non-empty float32 [N,3] points are required")
        radius = float(np.float32(radius))
        if not np.isfinite(radius) or radius <= 0.0:
            raise ValueError("positive finite radius is required")
        native_path = Path(native_library_path).resolve()
        if not native_path.is_file():
            raise FileNotFoundError(native_path)

        # Consumption rederives every authority/ABI/PTX binding and makes the
        # executable single-use.  The generated PTX is evidence for the V4
        # callback semantics; the verified optimized physical family below is
        # its closed lowering, not a user-selected bypass.
        composed_ptx = consume_verified_multiround_spatial_executable(
            executable, authority,
            any_hit_proof_authority=any_hit_proof_authority)
        self._callback_ptx_sha256 = hashlib.sha256(composed_ptx.encode()).hexdigest()
        self._authority = authority
        self._native_path = native_path
        self._native_sha256 = _file_sha256(native_path)
        self._points = point_values
        self._radius = radius
        rows = tuple(Point3D(
            id=index, x=float(row[0]), y=float(row[1]), z=float(row[2]))
            for index, row in enumerate(point_values))
        # The exact library is selected before constructing the provider.
        os.environ["RTDL_OPTIX_LIB"] = str(native_path)
        os.environ["RTDL_OPTIX_LIBRARY"] = str(native_path)
        self._library = _load_optix_library()
        self._prepared = (
            prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
                rows, radius=radius, partner="numba"))
        self._closed = False
        self._owner_pid = os.getpid()
        self._owner_thread = threading.get_ident()
        self._execution_count = 0
        self._session_identity = _digest({
            "authority": authority.authority_nonce,
            "callback_ptx": self._callback_ptx_sha256,
            "native": self._native_sha256,
            "points": hashlib.sha256(point_values.tobytes()).hexdigest(),
            "radius_f32": float(np.float32(radius)),
            "physical_lowering": (
                "canonical_v4_spatial_emit_to_prepared_optix_grouped_union_numba_v1"),
        })

    def _guard(self) -> None:
        if self._closed:
            raise RuntimeError("prepared grouped V4 owner is closed")
        if os.getpid() != self._owner_pid:
            raise RuntimeError("prepared grouped V4 owner crossed process boundary")
        if threading.get_ident() != self._owner_thread:
            raise RuntimeError("prepared grouped V4 owner crossed thread boundary")

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "authority_nonce": self._authority.authority_nonce,
            "callback_ptx_sha256": self._callback_ptx_sha256,
            "native_library_sha256": self._native_sha256,
            "physical_lowering": (
                "canonical_v4_spatial_emit_to_prepared_optix_grouped_union_numba_v1"),
            "execution_count": self._execution_count,
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "prepare_seconds_reported_separately": True,
        }

    def execute_components(
        self, *, epsilon: float, min_points: int,
    ) -> OptimizedRadiusGraphComponentsResult:
        self._guard()
        epsilon = float(np.float32(epsilon))
        if epsilon != self._radius:
            raise ValueError("optimized grouped owner requires its exact prepared radius")
        min_points = int(min_points)
        if min_points < 1:
            raise ValueError("min_points must be positive")
        audit = OptixTraversalAuditSession.open(
            library=self._library, library_path=self._native_path)
        try:
            physical = (
                radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                    self._prepared, min_neighbors=min_points,
                    return_metadata=True))
            columns = physical["columns"]
            point_ids = np.asarray(
                columns["point_ids"].copy_to_host(), dtype=np.int64)
            labels_in = np.asarray(
                columns["component_labels"].copy_to_host(), dtype=np.int64)
            core_in = np.asarray(
                columns["is_core"].copy_to_host(), dtype=np.int64)
            counts_in = np.asarray(
                columns["neighbor_counts"].copy_to_host(), dtype=np.uint64)
            point_count = len(self._points)
            labels = [-1] * point_count
            core = [False] * point_count
            neighbor_counts = [0] * point_count
            for index, point_id in enumerate(point_ids.tolist()):
                point_id = int(point_id)
                if not 0 <= point_id < point_count:
                    raise RuntimeError("grouped V4 lowering returned an out-of-domain point ID")
                labels[point_id] = int(labels_in[index])
                core[point_id] = bool(core_in[index])
                neighbor_counts[point_id] = int(counts_in[index])
            value = {
                "canonical_component_labels": canonical_partition_labels(labels),
                "core_flags": tuple(core),
                "neighbor_counts": tuple(neighbor_counts),
            }
            exact_edge_count = sum(neighbor_counts)
            output_sha = _digest(value)
            receipt = audit.finish(
                semantic_digest=_digest({
                    "authority": self._authority.authority_nonce,
                    "algebra": "radius_graph_components_f32_v1",
                    "epsilon_f32": epsilon,
                    "min_points": min_points,
                    "native": self._native_sha256,
                    "callback_ptx": self._callback_ptx_sha256,
                    "physical_lowering": (
                        "canonical_v4_spatial_emit_to_prepared_optix_grouped_union_numba_v1"),
                }),
                output_digest=output_sha,
                route_identity=(
                    "v4_callback_ir:canonical_spatial_emit:prepared_grouped_union_v1"),
                expected_program_bundles=(
                    "fixed_radius_count_threshold_3d",
                    "fixed_radius_grouped_union_3d",
                ),
            )
        except Exception:
            audit.abort()
            raise
        if receipt["physical_executor_classification"] != "optix_traversal_observed":
            raise RuntimeError("optimized grouped V4 lowering lacked bound OptiX traversal")
        self._execution_count += 1
        return OptimizedRadiusGraphComponentsResult(
            value=value,
            traversal_receipt=receipt,
            native_library_sha256=self._native_sha256,
            callback_ptx_sha256=self._callback_ptx_sha256,
            exact_edge_count=exact_edge_count,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._guard()
        self._prepared.close()
        self._closed = True

    def __enter__(self):
        self._guard()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def __getstate__(self):
        raise RuntimeError("prepared grouped V4 owner cannot be serialized")


def prepare_verified_radius_graph_grouped_v4(
    authority: VerifiedMultiRoundSpatialAuthority,
    executable: VerifiedMultiRoundSpatialExecutable,
    *,
    any_hit_proof_authority,
    points: np.ndarray,
    radius: float,
    native_library_path: str | Path,
) -> PreparedVerifiedRadiusGraphGroupedV4:
    started = time.perf_counter()
    owner = PreparedVerifiedRadiusGraphGroupedV4(
        authority, executable,
        any_hit_proof_authority=any_hit_proof_authority,
        points=points, radius=radius,
        native_library_path=native_library_path)
    owner.prepare_seconds = time.perf_counter() - started
    return owner


__all__ = [
    "OptimizedRadiusGraphComponentsResult",
    "PreparedVerifiedRadiusGraphGroupedV4",
    "prepare_verified_radius_graph_grouped_v4",
]
