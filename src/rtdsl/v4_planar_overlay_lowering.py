"""Canonical V4 lowering for exact planar-overlay producer pipelines.

The unrestricted V4 AABB callback runtime returns bounded host rows.  A real
planar overlay can contain millions of segments and must keep its producer and
grouped continuation on the device.  This lowering accepts only the canonical
closed-AABB callback plus the two compiler-verified exact planar partner
algebras, consumes the verified callback executable, and then invokes an
existing prepared planar-overlay physical family supplied by the application
adapter.  It never selects an application algorithm and never materializes
callback rows in Python.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Callable

from .optix_runtime import _load_optix_library
from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_bounded_relation_optix_compiler import (
    consume_verified_bounded_relation_executable,
)
from .v4_box_relation_callback import compile_callback as compile_box_callback
from .v4_exact_predicate_witness import (
    CandidateProducerKind,
    ExactPartnerAlgebra,
    VerifiedExactPredicateWitnessAuthority,
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class VerifiedPlanarOverlayResult:
    physical_result: dict[str, object]
    traversal_receipt: dict[str, object]
    callback_ptx_sha256: str
    physical_lowering: str = (
        "canonical_v4_closed_aabb_to_prepared_planar_overlay_device_pipeline_v1")


def execute_verified_planar_overlay_v4(
    relation,
    contract,
    abi,
    executable,
    *,
    any_hit_proof_authority,
    exact_authority: VerifiedExactPredicateWitnessAuthority,
    physical_runner: Callable[[], tuple[dict[str, object], object]],
    native_library_path: str | Path,
) -> VerifiedPlanarOverlayResult:
    """Consume V4 authority and execute one app-owned exact overlay protocol."""

    canonical = compile_box_callback()
    callback = relation.physical.callback
    exact_schema = exact_authority.schema
    if (
        callback.ir_sha256 != canonical.ir_sha256
        or callback.effect_digest != canonical.effect_digest
        or exact_schema.callback_ir_sha256 != canonical.ir_sha256
        or exact_schema.effect_digest != canonical.effect_digest
        or exact_schema.physical_schema_sha256
        != relation.physical.schema.schema_sha256
        or exact_schema.source_authority_nonce != relation.authority_nonce
        or exact_schema.producer_kind
        is not CandidateProducerKind.CLOSED_AABB_RELATION
        or frozenset(exact_schema.partner_algebras)
        != frozenset({
            ExactPartnerAlgebra.DIRECTED_POINT_LOCATION_SOS_I46,
            ExactPartnerAlgebra.SEGMENT_PAIR_GROUPED_COUNT_SOS_I46,
        })
    ):
        raise RuntimeError(
            "planar-overlay lowering requires the canonical callback and both exact algebras")
    composed = consume_verified_bounded_relation_executable(
        executable, relation, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)
    callback_ptx_sha256 = hashlib.sha256(composed.encode()).hexdigest()
    native_path = Path(native_library_path).resolve()
    library = _load_optix_library()
    audit = OptixTraversalAuditSession.open(
        library=library, library_path=native_path)
    try:
        physical_result, canonical_output = physical_runner()
        receipt = audit.finish(
            semantic_digest=_digest({
                "callback_ir": canonical.ir_sha256,
                "effect": canonical.effect_digest,
                "physical_schema": relation.physical.schema.schema_sha256,
                "exact_authority": exact_authority.authority_nonce,
                "callback_ptx": callback_ptx_sha256,
                "physical_lowering": (
                    "canonical_v4_closed_aabb_to_prepared_planar_overlay_device_pipeline_v1"),
            }),
            output_digest=_digest(canonical_output),
            route_identity=(
                "v4_callback_ir:closed_aabb:prepared_planar_overlay_device_pipeline_v1"),
        )
    except Exception:
        audit.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("planar-overlay lowering lacked complete bound OptiX traversal")
    return VerifiedPlanarOverlayResult(
        physical_result=physical_result,
        traversal_receipt=receipt,
        callback_ptx_sha256=callback_ptx_sha256,
    )


__all__ = ["VerifiedPlanarOverlayResult", "execute_verified_planar_overlay_v4"]
