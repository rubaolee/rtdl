"""App-neutral owner-grouped reduction over accepted RT any-hit events.

The behavior contract is independent of geometry and applications.  A
verified callback decides whether an intersection is an accepted event.  The
physical provider projects each accepted primitive through one read-only
``owner_id`` column and reduces the constant bit ``1`` with Boolean OR.

The public contract deliberately does not expose writable pointers or raw
atomics to restricted Python.  Backends may implement the closed reduction
with an atomic OR, but must fail closed before returning a partial result when
an owner index or another protocol obligation is invalid.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Iterable, Sequence

from . import v4_callback_abi as _abi
from .v4_callback_abi import AnyHitProofAuthority, CompiledCallbackAbi
from .v4_callback_ir import (
    AnyHitDeliveryContract,
    CallbackEffect,
    CallbackRole,
    EffectKind,
    IfStatement,
    ReturnEffectStatement,
    StaticForStatement,
    VerifiedCallbackProgram,
)


OWNER_GROUPED_ANY_HIT_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-owner-grouped-any-hit-v1.json"
)
OWNER_GROUPED_ANY_HIT_SCHEMA_VERSION = "v1"
OWNER_GROUPED_ANY_HIT_TEMPLATE = "owner_grouped_any_hit_bool_or_v1"
OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA = (
    "rtdl.v4.owner_grouped_any_hit_bits.v1"
)
U32_MAX = (1 << 32) - 1


class OwnerGroupedAnyHitError(ValueError):
    """Stable fail-closed error for the grouped behavior contract."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 owner-grouped any-hit rejected: {code}@{path}: {message}"
        )


def _fail(code: str, path: str, message: str) -> None:
    raise OwnerGroupedAnyHitError(code, path, message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _u32(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) \
            or not 0 <= value <= U32_MAX:
        _fail("u32_domain", path, repr(value))
    return value


class OwnerGroupedReduction(str, Enum):
    BOOL_OR = "bool_or"


class HitOwnerDomain(str, Enum):
    PRIMITIVE = "primitive"


@dataclass(frozen=True)
class OwnerGroupedAnyHitSchema:
    callback_ir_sha256: str
    callback_effect_digest: str
    owner_semantic_id: str = "primitive.owner_id"
    owner_field_id: str = "owner_ids"
    output_field_id: str = "owner_hit_bits"
    owner_domain: HitOwnerDomain = HitOwnerDomain.PRIMITIVE
    reduction: OwnerGroupedReduction = OwnerGroupedReduction.BOOL_OR
    maximum_owner_count: int = U32_MAX
    schema_id: str = OWNER_GROUPED_ANY_HIT_SCHEMA_ID
    schema_version: str = OWNER_GROUPED_ANY_HIT_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "template_id": OWNER_GROUPED_ANY_HIT_TEMPLATE,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_effect_digest": self.callback_effect_digest,
            "owner_semantic_id": self.owner_semantic_id,
            "owner_field_id": self.owner_field_id,
            "output_field_id": self.output_field_id,
            "owner_domain": self.owner_domain.value,
            "reduction": self.reduction.value,
            "event_value": 1,
            "delivery": "accepted_any_hit_events",
            "duplicate_policy": "idempotent",
            "device_operation": "atomic_or_u32",
            "owner_bounds_policy": "fail_closed_before_output_consumption",
            "raw_event_order_is_semantic": False,
            "application_identity_used": False,
            "maximum_owner_count": self.maximum_owner_count,
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class VerifiedOwnerGroupedAnyHitContract:
    callback: VerifiedCallbackProgram
    schema: OwnerGroupedAnyHitSchema
    proof: AnyHitProofAuthority
    authority_sha256: str


@dataclass(frozen=True)
class OwnerGroupedAnyHitReferenceResult:
    owner_hit_bits: tuple[int, ...]
    accepted_event_count: int
    hit_owner_count: int
    output_sha256: str


def owner_grouped_any_hit_output_sha256(owner_hit_bits) -> str:
    try:
        bits = tuple(owner_hit_bits)
    except TypeError:
        _fail("output_shape", "owner_hit_bits", "iterable bits required")
    if not bits or any(type(value) is not int or value not in (0, 1)
                       for value in bits):
        _fail("output_shape", "owner_hit_bits", "nonempty Boolean U32 row required")
    return _digest({
        "schema": OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA,
        "owner_hit_bits": bits,
    })


def _effects(statements) -> tuple[CallbackEffect, ...]:
    result: list[CallbackEffect] = []
    for statement in statements:
        if isinstance(statement, ReturnEffectStatement):
            result.append(statement.effect)
        elif isinstance(statement, IfStatement):
            result.extend(_effects(statement.then_body))
            result.extend(_effects(statement.else_body))
        elif isinstance(statement, StaticForStatement):
            result.extend(_effects(statement.body))
    return tuple(result)


def _is_passthrough_accept(effect: CallbackEffect, payload_name: str) -> bool:
    if effect.kind is not EffectKind.ACCEPT_CONTINUE \
            or tuple(name for name, _ in effect.fields) != ("payload",):
        return False
    payload = effect.field("payload")
    return payload is not None and payload.opcode == "local" \
        and payload.attribute("name") == payload_name and not payload.operands


def derive_owner_grouped_any_hit_proof(
    callback: VerifiedCallbackProgram,
) -> AnyHitProofAuthority:
    """Recognize the closed pass-through any-hit normal form.

    Confluence of the complete operation comes from two independently checked
    facts: the callback accepts without order-dependent payload mutation, and
    the physical schema reduces a constant bit with idempotent Boolean OR.
    """

    if not isinstance(callback, VerifiedCallbackProgram):
        _fail("verified_callback_required", "callback", type(callback).__name__)
    if callback.program.manifest.any_hit_delivery \
            is not AnyHitDeliveryContract.IDEMPOTENT_MONOTONE:
        _fail(
            "delivery_contract", "callback.manifest.any_hit_delivery",
            "idempotent_monotone required",
        )
    try:
        function = callback.program.function_for_role(CallbackRole.ANY_HIT)
    except Exception as exc:
        _fail("any_hit_role", "callback.functions", str(exc))
    if len(function.arguments) < 2:
        _fail("any_hit_signature", "callback.any_hit", "hit and payload required")
    payload_name = function.arguments[1].name
    effects = _effects(function.body)
    if not effects or any(
            not _is_passthrough_accept(effect, payload_name)
            for effect in effects):
        _fail(
            "any_hit_normal_form", "callback.any_hit",
            "all paths must return accept_continue with the unchanged payload",
        )
    proof_payload = {
        "schema": "rtdl.v4.owner_grouped_any_hit_proof.v1",
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "delivery_contract": AnyHitDeliveryContract.IDEMPOTENT_MONOTONE.value,
        "callback_normal_form": "accept_continue_unchanged_payload",
        "physical_algebra": "constant_one_bool_or",
        "algebra_properties": ["associative", "commutative", "idempotent", "monotone"],
    }
    return AnyHitProofAuthority(
        callback.ir_sha256,
        callback.effect_digest,
        AnyHitDeliveryContract.IDEMPOTENT_MONOTONE,
        _digest(proof_payload),
        "compiler_recognized_commutative_idempotent_reduction_v1",
    )


def verify_owner_grouped_any_hit_schema(
    callback: VerifiedCallbackProgram,
    schema: OwnerGroupedAnyHitSchema,
    proof: AnyHitProofAuthority,
) -> VerifiedOwnerGroupedAnyHitContract:
    if not isinstance(callback, VerifiedCallbackProgram):
        _fail("verified_callback_required", "callback", type(callback).__name__)
    if not isinstance(schema, OwnerGroupedAnyHitSchema):
        _fail("schema_type", "schema", type(schema).__name__)
    if schema.schema_id != OWNER_GROUPED_ANY_HIT_SCHEMA_ID \
            or schema.schema_version != OWNER_GROUPED_ANY_HIT_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported schema")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.callback_effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "exact callback identity required")
    if schema.owner_domain is not HitOwnerDomain.PRIMITIVE \
            or schema.reduction is not OwnerGroupedReduction.BOOL_OR:
        _fail("closed_algebra", "schema", "primitive owner Boolean OR required")
    if schema.owner_semantic_id != "primitive.owner_id" \
            or schema.owner_field_id != "owner_ids" \
            or schema.output_field_id != "owner_hit_bits":
        _fail("field_identity", "schema", "canonical owner/output fields required")
    if not isinstance(schema.maximum_owner_count, int) \
            or isinstance(schema.maximum_owner_count, bool) \
            or not 1 <= schema.maximum_owner_count <= U32_MAX:
        _fail("owner_capacity", "schema.maximum_owner_count", repr(schema.maximum_owner_count))
    expected_proof = derive_owner_grouped_any_hit_proof(callback)
    if proof != expected_proof:
        _fail("proof_binding", "proof", "proof does not rederive exactly")
    authority = _digest({
        "kind": "verified_owner_grouped_any_hit_contract_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "schema": schema.schema_sha256,
        "proof": proof.proof_sha256,
    })
    return VerifiedOwnerGroupedAnyHitContract(callback, schema, proof, authority)


def compile_owner_grouped_any_hit_abi(
    contract: VerifiedOwnerGroupedAnyHitContract,
) -> CompiledCallbackAbi:
    """Compile the existing Callback ABI after successor-contract checks."""

    fresh = verify_owner_grouped_any_hit_schema(
        contract.callback, contract.schema, contract.proof)
    if fresh != contract:
        _fail("authority_reverification", "contract", "contract changed")
    verified = fresh.callback
    records = {item.name: item for item in verified.program.records}
    role_functions = {
        item.role: item for item in verified.program.functions
        if item.role is not None
    }
    roles = []
    for role in CallbackRole:
        function = role_functions.get(role)
        if function is None:
            continue
        inputs = [
            _abi.AbiField(
                "in.context.launch_index", "u64", "in", "launch_index", True),
        ]
        for argument in function.arguments:
            inputs.extend(_abi._flatten_type(
                argument.value_type, f"in.{argument.name}", direction="in",
                records=records, seen=set()))
        nonce = int(hashlib.sha256(
            f"{verified.ir_sha256}:{verified.effect_digest}:{role.value}".encode(
                "ascii")
        ).hexdigest()[:8], 16)
        roles.append(_abi.RoleAbi(
            role=role,
            role_tag=_abi._ROLE_TAGS[role],
            stage_tag=_abi._STAGE_TAGS[_abi.ROLE_STAGE[role]],
            symbol=f"rtdl_v4_{role.value}_{verified.ir_sha256[:16]}",
            inputs=tuple(inputs),
            status=_abi._STATUS_FIELDS,
            effects=_abi._effect_variants(function, records),
            first_error_policy=_abi._FIRST_ERROR_POLICY,
            nonce_word=nonce,
        ))
    base = CompiledCallbackAbi(
        schema_id=_abi.CALLBACK_ABI_SCHEMA_ID,
        schema_version=_abi.CALLBACK_ABI_SCHEMA_VERSION,
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        any_hit_proof_sha256=fresh.proof.proof_sha256,
        any_hit_proof_kind=fresh.proof.proof_kind,
        any_hit_delivery_contract=fresh.proof.delivery_contract.value,
        runtime_status_codes=_abi._RUNTIME_STATUS_CODES,
        roles=tuple(roles),
        abi_sha256="",
    )
    digest = _digest(base.payload_without_digest())
    return CompiledCallbackAbi(**{**base.__dict__, "abi_sha256": digest})


def verify_owner_grouped_any_hit_abi(
    artifact: CompiledCallbackAbi,
    contract: VerifiedOwnerGroupedAnyHitContract,
) -> CompiledCallbackAbi:
    """Recompile the successor ABI instead of widening the frozen decoder."""

    if type(artifact) is not CompiledCallbackAbi:
        _fail("abi_type", "abi", "CompiledCallbackAbi required")
    expected = compile_owner_grouped_any_hit_abi(contract)
    if artifact.to_dict() != expected.to_dict():
        _fail("abi_recompile_mismatch", "abi", "ABI differs from exact recompilation")
    return artifact


def execute_owner_grouped_any_hit_reference(
    owner_ids: Sequence[object],
    owner_count: int,
    accepted_events: Iterable[Sequence[object]],
    *,
    maximum_owner_count: int = U32_MAX,
) -> OwnerGroupedAnyHitReferenceResult:
    """Execute exact canonical CPU semantics for ``(query, primitive)`` rows."""

    if not isinstance(owner_count, int) or isinstance(owner_count, bool) \
            or not 1 <= owner_count <= maximum_owner_count <= U32_MAX:
        _fail("owner_count", "owner_count", repr(owner_count))
    owners = tuple(_u32(value, f"owner_ids[{index}]")
                   for index, value in enumerate(owner_ids))
    if not owners:
        _fail("owner_ids", "owner_ids", "at least one primitive owner required")
    for index, owner in enumerate(owners):
        if owner >= owner_count:
            _fail(
                "owner_out_of_bounds", f"owner_ids[{index}]",
                f"owner={owner}, owner_count={owner_count}",
            )
    bits = [0] * owner_count
    event_count = 0
    for index, row in enumerate(accepted_events):
        try:
            values = tuple(row)
        except TypeError:
            _fail("event_shape", f"accepted_events[{index}]", "pair required")
        if len(values) != 2:
            _fail("event_shape", f"accepted_events[{index}]", "pair required")
        _u32(values[0], f"accepted_events[{index}].query_id")
        primitive = _u32(
            values[1], f"accepted_events[{index}].primitive_id")
        if primitive >= len(owners):
            _fail(
                "primitive_out_of_bounds",
                f"accepted_events[{index}].primitive_id",
                f"primitive={primitive}, primitive_count={len(owners)}",
            )
        bits[owners[primitive]] = 1
        event_count += 1
    frozen = tuple(bits)
    return OwnerGroupedAnyHitReferenceResult(
        frozen,
        event_count,
        sum(frozen),
        owner_grouped_any_hit_output_sha256(frozen),
    )


__all__ = [
    "HitOwnerDomain", "OWNER_GROUPED_ANY_HIT_SCHEMA_ID",
    "OWNER_GROUPED_ANY_HIT_SCHEMA_VERSION", "OWNER_GROUPED_ANY_HIT_TEMPLATE",
    "OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA",
    "OwnerGroupedAnyHitError", "OwnerGroupedAnyHitReferenceResult",
    "OwnerGroupedAnyHitSchema", "OwnerGroupedReduction",
    "VerifiedOwnerGroupedAnyHitContract", "compile_owner_grouped_any_hit_abi",
    "derive_owner_grouped_any_hit_proof",
    "execute_owner_grouped_any_hit_reference",
    "owner_grouped_any_hit_output_sha256",
    "verify_owner_grouped_any_hit_abi", "verify_owner_grouped_any_hit_schema",
]
