"""Verified bounded-output lowering for V4 global nearest witnesses.

The general V4 spatial-callback runtime exposes relation rows.  That is the
right generic ABI, but it is not a legal large-scale implementation of a
``global_max_nearest_witness`` algebra: materialising one Python row per query
throws away the existing device-side global reducer.  This module proves the
canonical spatial callback plus the closed global-witness algebra, consumes
the verified executable once, and reuses the existing prepared true-OptiX
global-witness physical family.  Only one bounded witness crosses the ABI.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import threading

import numpy as np

from .optix_runtime import (
    _load_optix_library,
    prepare_certified_nearest_global_witness_3d_optix,
)
from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_exact_predicate_witness import (
    CandidateProducerKind,
    ExactPartnerAlgebra,
    VerifiedExactPredicateWitnessAuthority,
)
from .v4_multiround_spatial import VerifiedMultiRoundSpatialAuthority
from .v4_multiround_spatial_optix_compiler import (
    VerifiedMultiRoundSpatialExecutable,
    consume_verified_multiround_spatial_executable,
)
from .v4_spatial_candidate_callback import compile_callback as compile_canonical_callback


EXPECTED_PROGRAM_BUNDLE = "certified_nearest_state_f64_cell_mbr_3d.v1"


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
class OptimizedGlobalNearestWitnessResult:
    witness: dict[str, object]
    traversal_receipt: dict[str, object]
    physical_metadata: dict[str, object]
    native_library_sha256: str
    callback_ptx_sha256: str
    physical_lowering: str = (
        "canonical_v4_spatial_emit_to_device_global_nearest_witness_v1")


class PreparedVerifiedGlobalNearestWitnessV4:
    """Process/thread-bound owner of the bounded device witness route."""

    def __init__(
        self,
        authority: VerifiedMultiRoundSpatialAuthority,
        executable: VerifiedMultiRoundSpatialExecutable,
        *,
        exact_authority: VerifiedExactPredicateWitnessAuthority,
        any_hit_proof_authority,
        target_points: np.ndarray,
        query_domain_lower_bounds: np.ndarray,
        query_domain_upper_bounds: np.ndarray,
        native_library_path: str | Path,
        grid_shape: tuple[int, int, int] = (32, 32, 32),
        max_inline_points: int = 64,
        maximum_query_count: int,
    ) -> None:
        if not isinstance(authority, VerifiedMultiRoundSpatialAuthority):
            raise TypeError("verified multi-round authority is required")
        if not isinstance(executable, VerifiedMultiRoundSpatialExecutable):
            raise TypeError("live verified multi-round executable is required")
        if not isinstance(exact_authority, VerifiedExactPredicateWitnessAuthority):
            raise TypeError("verified exact-witness authority is required")
        canonical = compile_canonical_callback()
        callback = authority.relation.physical.callback
        if callback.ir_sha256 != canonical.ir_sha256 \
                or callback.effect_digest != canonical.effect_digest:
            raise RuntimeError(
                "global-witness lowering accepts only the canonical spatial callback")
        schema = exact_authority.schema
        if (
            schema.callback_ir_sha256 != callback.ir_sha256
            or schema.effect_digest != callback.effect_digest
            or schema.physical_schema_sha256
            != authority.relation.physical.schema.schema_sha256
            or schema.source_authority_nonce != authority.authority_nonce
            or schema.producer_kind is not CandidateProducerKind.SPHERE_NEAREST
            or schema.partner_algebras != (
                ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,)
        ):
            raise RuntimeError("exact-witness authority is not bound to this producer")

        targets = np.ascontiguousarray(target_points, dtype=np.float64)
        lower = np.ascontiguousarray(query_domain_lower_bounds, dtype=np.float64)
        upper = np.ascontiguousarray(query_domain_upper_bounds, dtype=np.float64)
        if targets.ndim != 2 or targets.shape[1] != 3 or not len(targets) \
                or not np.isfinite(targets).all():
            raise ValueError("finite non-empty float64 [N,3] targets required")
        if lower.shape != (3,) or upper.shape != (3,) \
                or not np.isfinite(lower).all() or not np.isfinite(upper).all() \
                or np.any(upper < lower):
            raise ValueError("finite ordered 3-D query domain required")
        if not isinstance(maximum_query_count, int) \
                or isinstance(maximum_query_count, bool) \
                or maximum_query_count <= 0:
            raise ValueError("positive maximum_query_count required")
        maximum_heavy = maximum_query_count * int(targets.shape[0])
        if maximum_heavy > (1 << 64) - 1:
            raise ValueError("query-target heavy-evaluation bound exceeds uint64")

        native_path = Path(native_library_path).resolve()
        if not native_path.is_file():
            raise FileNotFoundError(native_path)
        composed = consume_verified_multiround_spatial_executable(
            executable, authority,
            any_hit_proof_authority=any_hit_proof_authority)
        self._callback_ptx_sha256 = hashlib.sha256(composed.encode()).hexdigest()
        self._authority = authority
        self._exact_authority = exact_authority
        self._native_path = native_path
        self._native_sha256 = _file_sha256(native_path)
        self._query_lower = lower
        self._query_upper = upper
        self._maximum_query_count = maximum_query_count
        os.environ["RTDL_OPTIX_LIB"] = str(native_path)
        os.environ["RTDL_OPTIX_LIBRARY"] = str(native_path)
        self._library = _load_optix_library()
        self._prepared = prepare_certified_nearest_global_witness_3d_optix(
            targets,
            target_ids=np.arange(len(targets), dtype=np.int64),
            grid_shape=grid_shape,
            query_domain_lower_bounds=lower,
            query_domain_upper_bounds=upper,
            max_inline_points=max_inline_points,
            max_heavy_point_evaluations=maximum_heavy,
            application_selected_backend=False,
        )
        self._closed = False
        self._owner_pid = os.getpid()
        self._owner_thread = threading.get_ident()
        self._execution_count = 0
        self._session_identity = _digest({
            "authority": authority.authority_nonce,
            "exact_authority": exact_authority.authority_nonce,
            "callback_ptx": self._callback_ptx_sha256,
            "native": self._native_sha256,
            "targets": hashlib.sha256(targets.tobytes()).hexdigest(),
            "query_domain_lower": lower.tolist(),
            "query_domain_upper": upper.tolist(),
            "maximum_query_count": maximum_query_count,
            "physical_lowering": (
                "canonical_v4_spatial_emit_to_device_global_nearest_witness_v1"),
        })

    def _guard(self) -> None:
        if self._closed:
            raise RuntimeError("prepared global-witness V4 owner is closed")
        if os.getpid() != self._owner_pid:
            raise RuntimeError("prepared global-witness V4 owner crossed process boundary")
        if threading.get_ident() != self._owner_thread:
            raise RuntimeError("prepared global-witness V4 owner crossed thread boundary")

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "authority_nonce": self._authority.authority_nonce,
            "exact_authority_nonce": self._exact_authority.authority_nonce,
            "callback_ptx_sha256": self._callback_ptx_sha256,
            "native_library_sha256": self._native_sha256,
            "physical_lowering": (
                "canonical_v4_spatial_emit_to_device_global_nearest_witness_v1"),
            "execution_count": self._execution_count,
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "prepare_seconds_reported_separately": True,
        }

    def execute_global_witness(
        self, query_points: np.ndarray,
    ) -> OptimizedGlobalNearestWitnessResult:
        self._guard()
        queries = np.ascontiguousarray(query_points, dtype=np.float64)
        if queries.ndim != 2 or queries.shape[1] != 3 or not len(queries) \
                or not np.isfinite(queries).all():
            raise ValueError("finite non-empty float64 [Q,3] queries required")
        if len(queries) > self._maximum_query_count:
            raise ValueError("query count exceeds prepared certified bound")
        if np.any(queries < self._query_lower) or np.any(queries > self._query_upper):
            raise ValueError("queries escaped the certified prepared domain")
        audit = OptixTraversalAuditSession.open(
            library=self._library, library_path=self._native_path)
        try:
            physical = self._prepared.run(queries)
            actual = dict(physical["actual"])
            witness = {
                "source_id": int(actual["source_id"]),
                "item_id": int(actual["item_id"]),
                "value": float(actual["value"]),
            }
            receipt = audit.finish(
                semantic_digest=_digest({
                    "authority": self._authority.authority_nonce,
                    "exact_authority": self._exact_authority.authority_nonce,
                    "algebra": ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32.value,
                    "query_sha256": hashlib.sha256(queries.tobytes()).hexdigest(),
                    "native": self._native_sha256,
                    "callback_ptx": self._callback_ptx_sha256,
                }),
                output_digest=_digest(witness),
                route_identity=(
                    "v4_callback_ir:canonical_spatial_emit:device_global_witness_v1"),
                expected_program_bundles=(EXPECTED_PROGRAM_BUNDLE,),
            )
        except Exception:
            audit.abort()
            raise
        if receipt["physical_executor_classification"] != "optix_traversal_observed":
            raise RuntimeError("global-witness lowering lacked OptiX traversal")
        metadata = dict(physical["metadata"])
        if metadata.get("full_nearest_state_host_projection_used") is not False \
                or int(metadata.get("bounded_witness_host_projection_rows", 0)) != 1:
            raise RuntimeError("global-witness physical route lost bounded device reduction")
        self._execution_count += 1
        return OptimizedGlobalNearestWitnessResult(
            witness=witness,
            traversal_receipt=receipt,
            physical_metadata=metadata,
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
        raise RuntimeError("prepared global-witness V4 owner cannot be serialized")


def prepare_verified_global_nearest_witness_v4(
    authority: VerifiedMultiRoundSpatialAuthority,
    executable: VerifiedMultiRoundSpatialExecutable,
    *, exact_authority: VerifiedExactPredicateWitnessAuthority,
    any_hit_proof_authority, target_points: np.ndarray,
    query_domain_lower_bounds: np.ndarray,
    query_domain_upper_bounds: np.ndarray,
    native_library_path: str | Path,
    maximum_query_count: int,
) -> PreparedVerifiedGlobalNearestWitnessV4:
    return PreparedVerifiedGlobalNearestWitnessV4(
        authority, executable,
        exact_authority=exact_authority,
        any_hit_proof_authority=any_hit_proof_authority,
        target_points=target_points,
        query_domain_lower_bounds=query_domain_lower_bounds,
        query_domain_upper_bounds=query_domain_upper_bounds,
        native_library_path=native_library_path,
        maximum_query_count=maximum_query_count,
    )


__all__ = [
    "OptimizedGlobalNearestWitnessResult",
    "PreparedVerifiedGlobalNearestWitnessV4",
    "prepare_verified_global_nearest_witness_v4",
]
