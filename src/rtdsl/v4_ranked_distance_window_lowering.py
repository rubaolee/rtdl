"""Verified optimized lowering for the canonical V4 ranked-distance window.

The canonical spatial callback plus exact open-boundary top-K partner has a
closed implementation in the generic ``action_bounded_selection_3d`` OptiX
family.  This module consumes the verified callback executable, proves that
exact canonical shape, and uses the bounded native result directly instead of
materializing an unbounded broad-phase relation in Python.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import threading

import numpy as np

from .direct_optix_physical import prepare_direct_optix_bounded_selection_3d
from .optix_runtime import _load_optix_library, pack_points
from .physical_execution_provenance import OptixTraversalAuditSession
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
class OptimizedRankedDistanceWindowResult:
    rows: tuple[tuple[int, int, float], ...]
    traversal_receipt: dict[str, object]
    native_library_sha256: str
    callback_ptx_sha256: str
    physical_lowering: str = (
        "canonical_v4_spatial_emit_to_action_bounded_selection_3d_v1")


class PreparedVerifiedRankedDistanceWindowV4:
    def __init__(
        self,
        authority: VerifiedMultiRoundSpatialAuthority,
        executable: VerifiedMultiRoundSpatialExecutable,
        *, any_hit_proof_authority,
        search_points: np.ndarray,
        maximum_distance_bound: float,
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
                "ranked-window lowering accepts only the canonical spatial emit callback")
        search = np.ascontiguousarray(search_points, dtype=np.float32)
        if search.ndim != 2 or search.shape[1] != 3 or not len(search) \
                or not np.isfinite(search).all():
            raise ValueError("finite non-empty float32 [N,3] search points required")
        maximum_distance_bound = float(np.float32(maximum_distance_bound))
        if not np.isfinite(maximum_distance_bound) or maximum_distance_bound <= 0:
            raise ValueError("positive finite maximum distance bound required")
        native_path = Path(native_library_path).resolve()
        if not native_path.is_file():
            raise FileNotFoundError(native_path)
        composed = consume_verified_multiround_spatial_executable(
            executable, authority,
            any_hit_proof_authority=any_hit_proof_authority)
        self._callback_ptx_sha256 = hashlib.sha256(composed.encode()).hexdigest()
        self._authority = authority
        self._native_path = native_path
        self._native_sha256 = _file_sha256(native_path)
        self._maximum_distance_bound = maximum_distance_bound
        packed_search = pack_points(
            ids=np.arange(len(search), dtype=np.uint32),
            x=search[:, 0], y=search[:, 1], z=search[:, 2], dimension=3)
        os.environ["RTDL_OPTIX_LIB"] = str(native_path)
        os.environ["RTDL_OPTIX_LIBRARY"] = str(native_path)
        self._library = _load_optix_library()
        self._prepared = prepare_direct_optix_bounded_selection_3d(
            packed_search, max_distance_bound=maximum_distance_bound)
        self._closed = False
        self._owner_pid = os.getpid()
        self._owner_thread = threading.get_ident()
        self._execution_count = 0
        self._session_identity = _digest({
            "authority": authority.authority_nonce,
            "callback_ptx": self._callback_ptx_sha256,
            "native": self._native_sha256,
            "search": hashlib.sha256(search.tobytes()).hexdigest(),
            "maximum_distance_bound_f32": maximum_distance_bound,
            "physical_lowering": (
                "canonical_v4_spatial_emit_to_action_bounded_selection_3d_v1"),
        })

    def _guard(self) -> None:
        if self._closed:
            raise RuntimeError("prepared ranked-window V4 owner is closed")
        if os.getpid() != self._owner_pid:
            raise RuntimeError("prepared ranked-window V4 owner crossed process boundary")
        if threading.get_ident() != self._owner_thread:
            raise RuntimeError("prepared ranked-window V4 owner crossed thread boundary")

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "authority_nonce": self._authority.authority_nonce,
            "callback_ptx_sha256": self._callback_ptx_sha256,
            "native_library_sha256": self._native_sha256,
            "physical_lowering": (
                "canonical_v4_spatial_emit_to_action_bounded_selection_3d_v1"),
            "execution_count": self._execution_count,
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "prepare_seconds_reported_separately": True,
        }

    def execute_ranked(
        self, queries: np.ndarray, *, k: int, minimum_distance: float,
        maximum_distance: float, initial_radius: float,
        maximum_rounds: int,
    ) -> OptimizedRankedDistanceWindowResult:
        self._guard()
        query_values = np.ascontiguousarray(queries, dtype=np.float32)
        if query_values.ndim != 2 or query_values.shape[1] != 3 \
                or not np.isfinite(query_values).all():
            raise ValueError("finite float32 [Q,3] query points required")
        k = int(k)
        minimum = float(np.float32(minimum_distance))
        maximum = float(np.float32(maximum_distance))
        initial = float(np.float32(initial_radius))
        rounds = int(maximum_rounds)
        if not 0 <= minimum <= maximum <= self._maximum_distance_bound:
            raise ValueError("ranked distance window exceeds prepared bound")
        if initial <= 0 or rounds < 1 \
                or initial * (2 ** (rounds - 1)) < maximum:
            raise ValueError("multi-round schedule cannot reach maximum distance")
        packed_queries = pack_points(
            ids=np.arange(len(query_values), dtype=np.uint32),
            x=query_values[:, 0], y=query_values[:, 1], z=query_values[:, 2],
            dimension=3)
        audit = OptixTraversalAuditSession.open(
            library=self._library, library_path=self._native_path)
        try:
            physical = self._prepared.run(
                packed_queries, minimum_distance=minimum,
                maximum_distance=maximum, k=k,
                minimum_boundary="open", maximum_boundary="open")
            result_rows = tuple(
                (int(query_id), int(item_id), float(distance))
                for query_id, item_id, distance in physical["rows"])
            receipt = audit.finish(
                semantic_digest=_digest({
                    "authority": self._authority.authority_nonce,
                    "algebra": "ranked_distance_window_f32_v1",
                    "k": k, "minimum_f32": minimum, "maximum_f32": maximum,
                    "initial_radius_f32": initial, "maximum_rounds": rounds,
                    "native": self._native_sha256,
                    "callback_ptx": self._callback_ptx_sha256,
                    "physical_lowering": (
                        "canonical_v4_spatial_emit_to_action_bounded_selection_3d_v1"),
                }),
                output_digest=_digest(result_rows),
                route_identity=(
                    "v4_callback_ir:canonical_spatial_emit:bounded_selection_v1"),
                expected_program_bundles=("action_bounded_selection_3d",),
            )
        except Exception:
            audit.abort()
            raise
        if receipt["physical_executor_classification"] != "optix_traversal_observed":
            raise RuntimeError("optimized ranked-window lowering lacked OptiX traversal")
        self._execution_count += 1
        return OptimizedRankedDistanceWindowResult(
            rows=result_rows,
            traversal_receipt=receipt,
            native_library_sha256=self._native_sha256,
            callback_ptx_sha256=self._callback_ptx_sha256,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._guard()
        self._prepared.close()
        self._closed = True

    def __getstate__(self):
        raise RuntimeError("prepared ranked-window V4 owner cannot be serialized")


def prepare_verified_ranked_distance_window_v4(
    authority: VerifiedMultiRoundSpatialAuthority,
    executable: VerifiedMultiRoundSpatialExecutable,
    *, any_hit_proof_authority, search_points: np.ndarray,
    maximum_distance_bound: float, native_library_path: str | Path,
) -> PreparedVerifiedRankedDistanceWindowV4:
    return PreparedVerifiedRankedDistanceWindowV4(
        authority, executable,
        any_hit_proof_authority=any_hit_proof_authority,
        search_points=search_points,
        maximum_distance_bound=maximum_distance_bound,
        native_library_path=native_library_path)


__all__ = [
    "OptimizedRankedDistanceWindowResult",
    "PreparedVerifiedRankedDistanceWindowV4",
    "prepare_verified_ranked_distance_window_v4",
]
