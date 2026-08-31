"""Closed app-neutral constructor for the V4 multi-round spatial family."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .v4_bounded_relation import (
    BoundedRelationEmissionSchema,
    RelationDuplicatePolicy,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from .v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from .v4_callback_ir import AnyHitDeliveryContract
from .v4_multiround_spatial import (
    MultiRoundSpatialSchema,
    verify_multiround_spatial_schema,
)
from .v4_typed_physical_schema import verify_typed_physical_schema
from .v4_spatial_candidate_callback import compile_callback, physical_schema


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def compile_standard_multiround_authority(
    target,
    *,
    capacity: int = 4096,
    maximum_rounds: int = 8,
):
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    relation_schema = BoundedRelationEmissionSchema(
        callback.ir_sha256,
        callback.effect_digest,
        physical.schema.schema_sha256,
        capacity,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
    )
    relation = verify_bounded_relation_schema(physical, relation_schema)
    proof = AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "v4_spatial_candidate_order_independence_v1",
            "callback": callback.ir_sha256,
            "standard_library": hashlib.sha256(
                Path(__file__).read_bytes()).hexdigest(),
            "raw_device_order_semantic": False,
            "canonical_order": "lexicographic_u32_pair",
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )
    abi = compile_callback_abi(
        callback,
        any_hit_proof_authority=proof,
        physical_schema_authority=physical,
    )
    relation_contract = compile_bounded_relation_contract(
        relation, abi_sha256=abi.abi_sha256)
    schema = MultiRoundSpatialSchema(
        relation_schema_sha256=relation.schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        maximum_rounds=maximum_rounds,
        maximum_event_capacity=capacity,
    )
    authority = verify_multiround_spatial_schema(
        relation,
        relation_contract,
        abi,
        schema,
        any_hit_proof_authority=proof,
    )
    return authority, proof


__all__ = ["compile_standard_multiround_authority"]
