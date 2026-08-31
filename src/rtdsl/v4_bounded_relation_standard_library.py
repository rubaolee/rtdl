"""Closed app-neutral constructor for the V4 bounded AABB relation family."""

from __future__ import annotations

from .v4_bounded_relation import (
    BoundedRelationEmissionSchema,
    RelationDuplicatePolicy,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from .v4_callback_abi import compile_callback_abi
from .v4_typed_physical_schema import verify_typed_physical_schema
from .v4_box_relation_callback import compile_callback, physical_schema


def compile_standard_bounded_relation_authority(
    target,
    proof,
    *,
    capacity: int,
    minimum_overlap_f32: float = 0.0,
):
    callback = compile_callback()
    if proof.callback_ir_sha256 != callback.ir_sha256 \
            or proof.effect_digest != callback.effect_digest:
        raise ValueError("proof does not bind the standard AABB callback")
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256,
        callback.effect_digest,
        physical.schema.schema_sha256,
        capacity,
        minimum_overlap_f32=minimum_overlap_f32,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
    )
    authority = verify_bounded_relation_schema(physical, schema)
    abi = compile_callback_abi(
        callback,
        any_hit_proof_authority=proof,
        physical_schema_authority=physical,
    )
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    return authority, contract, abi


__all__ = ["compile_standard_bounded_relation_authority"]
