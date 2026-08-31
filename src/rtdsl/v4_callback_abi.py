"""Canonical V4 callback ABI/layout compilation.

This module is the first production tranche of Goal5751.  It consumes only a
``VerifiedCallbackProgram`` and emits a backend-neutral, deterministic ABI
description.  It never accepts the original Python callable or source text.

The ABI description deliberately separates three things that the Goal5749 PoC
had combined:

* flattened, typed callback inputs;
* a tagged union of the role's verified effects; and
* an RTDL-owned per-launch status record used as the only device fault channel.

The status record is specified as a first-error-wins atomic claim.  A backend
that cannot implement that policy race-free is not conforming and must fail
closed before launch.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Mapping, Sequence

from .v4_callback_ir import (
    AABB3F,
    HIT,
    TRIANGLE_HIT,
    RAY3F,
    AnyHitDeliveryContract,
    CallbackEffect,
    CallbackFunction,
    CallbackRole,
    CallbackStage,
    CallbackStatement,
    CallbackType,
    CallbackVerificationError,
    EffectKind,
    GeometryProofAuthority,
    IfStatement,
    LetStatement,
    ReturnEffectStatement,
    ScalarKind,
    StaticForStatement,
    TypeKind,
    VerifiedCallbackProgram,
    RuntimeStatus,
    ROLE_STAGE,
    verify_callback_program,
)


CALLBACK_ABI_SCHEMA_ID = "https://rtdl.dev/schemas/v4-callback-abi-v1.json"
CALLBACK_ABI_SCHEMA_VERSION = "v1"
_SHA256 = re.compile(r"[0-9a-f]{64}")


class CallbackAbiError(ValueError):
    """Fail-closed ABI compilation error with a stable code and path."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 Callback ABI compilation failed: {code}@{path}: {message}")


@dataclass(frozen=True)
class AnyHitProofAuthority:
    """Out-of-program authority for a verified any-hit delivery proof.

    Merely declaring ``manifest.any_hit_delivery`` is not enough for device
    code generation.  The compiler caller must supply an independently bound
    proof covering the exact verified IR and exact effect set.
    """

    callback_ir_sha256: str
    effect_digest: str
    delivery_contract: AnyHitDeliveryContract
    proof_sha256: str
    proof_kind: str

    def to_dict(self) -> dict[str, str]:
        return {
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "delivery_contract": self.delivery_contract.value,
            "proof_sha256": self.proof_sha256,
            "proof_kind": self.proof_kind,
        }


@dataclass(frozen=True)
class AbiField:
    path: str
    scalar: str
    direction: str
    semantic_type: str
    readonly: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "scalar": self.scalar,
            "direction": self.direction,
            "semantic_type": self.semantic_type,
            "readonly": self.readonly,
        }


@dataclass(frozen=True)
class EffectVariantAbi:
    tag: int
    kind: EffectKind
    fields: tuple[AbiField, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "tag": self.tag,
            "kind": self.kind.value,
            "fields": [item.to_dict() for item in self.fields],
        }


@dataclass(frozen=True)
class RoleAbi:
    role: CallbackRole
    role_tag: int
    stage_tag: int
    symbol: str
    inputs: tuple[AbiField, ...]
    status: tuple[AbiField, ...]
    effects: tuple[EffectVariantAbi, ...]
    first_error_policy: str
    nonce_word: int

    @property
    def parameter_order(self) -> tuple[str, ...]:
        effect_fields = sorted(
            {field.path for variant in self.effects for field in variant.fields}
        )
        return tuple(
            [item.path for item in self.inputs]
            + [item.path for item in self.status]
            + ["out.effect_tag"]
            + effect_fields
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "role_tag": self.role_tag,
            "stage_tag": self.stage_tag,
            "symbol": self.symbol,
            "inputs": [item.to_dict() for item in self.inputs],
            "status": [item.to_dict() for item in self.status],
            "effects": [item.to_dict() for item in self.effects],
            "first_error_policy": self.first_error_policy,
            "nonce_word": self.nonce_word,
            "parameter_order": list(self.parameter_order),
        }


@dataclass(frozen=True)
class CompiledCallbackAbi:
    schema_id: str
    schema_version: str
    callback_ir_sha256: str
    callback_effect_digest: str
    any_hit_proof_sha256: str | None
    any_hit_proof_kind: str | None
    any_hit_delivery_contract: str | None
    runtime_status_codes: tuple[tuple[str, int], ...]
    roles: tuple[RoleAbi, ...]
    abi_sha256: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_effect_digest": self.callback_effect_digest,
            "any_hit_proof_sha256": self.any_hit_proof_sha256,
            "any_hit_proof_kind": self.any_hit_proof_kind,
            "any_hit_delivery_contract": self.any_hit_delivery_contract,
            "runtime_status_codes": {key: value for key, value in self.runtime_status_codes},
            "roles": [item.to_dict() for item in self.roles],
        }

    def to_dict(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "abi_sha256": self.abi_sha256}


_STATUS_FIELDS = (
    AbiField("status.ok", "u32", "out", "status_ok"),
    AbiField("status.error_code", "u32", "out", "runtime_status"),
    AbiField("status.stage", "u32", "out", "callback_stage"),
    AbiField("status.role", "u32", "out", "callback_role"),
    AbiField("status.launch_index", "u64", "out", "launch_index"),
    AbiField("status.error_site", "u32", "out", "verified_ir_site"),
    AbiField("status.effect_tag", "u32", "out", "effect_tag"),
    AbiField("status.nonce_word", "u32", "out", "module_nonce"),
    AbiField("status.invocation_mask", "u32", "out", "role_invocation_mask"),
    AbiField("status.first_error_claimed", "u32", "out", "atomic_first_error_claim"),
)

_FIRST_ERROR_POLICY = (
    "per_launch_index_atomic_compare_exchange_from_zero;"
    "first_successful_error_claim_wins;never_clear_on_device"
)

_EFFECT_TAGS: Mapping[EffectKind, int] = {
    kind: index + 1 for index, kind in enumerate(EffectKind)
}

_ROLE_TAGS: Mapping[CallbackRole, int] = {
    role: index + 1 for index, role in enumerate(CallbackRole)
}

_STAGE_TAGS: Mapping[CallbackStage, int] = {
    stage: index + 1 for index, stage in enumerate(CallbackStage)
}

_RUNTIME_STATUS_CODES: tuple[tuple[str, int], ...] = tuple(
    (status.value, index) for index, status in enumerate(RuntimeStatus)
)

_ROLE_EFFECTS: Mapping[CallbackRole, frozenset[EffectKind]] = {
    CallbackRole.BOUNDS: frozenset({EffectKind.AABB}),
    CallbackRole.MAKE_RAY: frozenset({EffectKind.TRACE_REQUEST}),
    CallbackRole.INTERSECTION: frozenset({EffectKind.HIT, EffectKind.NO_HIT}),
    CallbackRole.ANY_HIT: frozenset({
        EffectKind.ACCEPT_CONTINUE, EffectKind.IGNORE, EffectKind.TERMINATE,
    }),
    CallbackRole.CLOSEST_HIT: frozenset({EffectKind.PAYLOAD}),
    CallbackRole.MISS: frozenset({EffectKind.PAYLOAD}),
    CallbackRole.FINALIZE: frozenset({EffectKind.OUTPUT}),
}

_ANY_HIT_PROOF_KINDS: Mapping[AnyHitDeliveryContract, frozenset[str]] = {
    AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL: frozenset({
        "external_machine_checked_order_independence_v1",
        "compiler_recognized_commutative_idempotent_reduction_v1",
    }),
    AnyHitDeliveryContract.IDEMPOTENT_MONOTONE: frozenset({
        "external_machine_checked_order_independence_v1",
        "compiler_recognized_commutative_idempotent_reduction_v1",
    }),
    AnyHitDeliveryContract.ABSORBING_TERMINATION: frozenset({
        "external_machine_checked_order_independence_v1",
        "compiler_recognized_absorbing_termination_v1",
    }),
}


def _scalar(kind: ScalarKind) -> CallbackType:
    return CallbackType(TypeKind.SCALAR, scalar=kind)


def _vector(kind: ScalarKind, lanes: int) -> CallbackType:
    return CallbackType(TypeKind.VECTOR, scalar=kind, lanes=lanes)


_BUILTIN_FIELDS: Mapping[str, tuple[tuple[str, CallbackType], ...]] = {
    "Ray3f": (
        ("origin", _vector(ScalarKind.F32, 3)),
        ("direction", _vector(ScalarKind.F32, 3)),
        ("tmin", _scalar(ScalarKind.F32)),
        ("tmax", _scalar(ScalarKind.F32)),
    ),
    "Hit": (
        ("t", _scalar(ScalarKind.F32)),
        ("hit_kind", _scalar(ScalarKind.U32)),
    ),
    "TriangleHit": (
        ("t", _scalar(ScalarKind.F32)),
        ("primitive_index", _scalar(ScalarKind.U32)),
        ("hit_kind", _scalar(ScalarKind.U32)),
        ("barycentrics", _vector(ScalarKind.F32, 2)),
    ),
    "Aabb3f": (
        ("lower", _vector(ScalarKind.F32, 3)),
        ("upper", _vector(ScalarKind.F32, 3)),
    ),
}


def _reverify_physical_schema_authority(
    verified: VerifiedCallbackProgram,
    authority: object,
) -> VerifiedCallbackProgram:
    """Re-derive a live typed-physical authority before ABI compilation.

    Serialized schema bytes, a target name, or a callback digest are not
    sufficient.  The bridge accepts only the non-serializable authority
    returned by ``verify_typed_physical_schema`` and independently reruns that
    admission, including its externally supplied triangle-orientation proof.
    """

    from .v4_typed_physical_schema import (
        GeometryFamily,
        VerifiedPhysicalSchemaAuthority,
        verify_typed_physical_schema,
    )

    if not isinstance(authority, VerifiedPhysicalSchemaAuthority):
        _fail(
            "physical_schema_authority_required", "physical_schema_authority",
            "expected live VerifiedPhysicalSchemaAuthority",
        )
    if authority.callback != verified:
        _fail(
            "physical_schema_callback_binding", "physical_schema_authority.callback",
            "authority does not bind the exact verified callback",
        )
    orientation = authority.triangle_orientation_authority
    orientation_map = (
        {} if orientation is None else {orientation.authority_sha256: orientation}
    )
    fresh = verify_typed_physical_schema(
        verified,
        authority.schema,
        target=authority.target,
        orientation_authorities=orientation_map,
    )
    if fresh != authority:
        _fail(
            "physical_schema_authority_reverification",
            "physical_schema_authority",
            "live typed authority does not rederive exactly",
        )
    if authority.schema.geometry_family is GeometryFamily.BUILTIN_TRIANGLE:
        closest = verified.program.function_for_role(CallbackRole.CLOSEST_HIT)
        if not closest.arguments or closest.arguments[0].value_type != TRIANGLE_HIT:
            _fail(
                "triangle_hit_abi", "closest_hit.arguments[0]",
                "built-in triangle lowering requires TriangleHit",
            )
    return fresh.callback


def compile_callback_abi(
    verified: VerifiedCallbackProgram,
    *,
    any_hit_proof_authority: AnyHitProofAuthority | None = None,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
    physical_schema_authority: object | None = None,
) -> CompiledCallbackAbi:
    """Compile a verified program into one deterministic ABI description."""

    if not isinstance(verified, VerifiedCallbackProgram):
        _fail("verified_program_required", "program", "unverified Callback IR is not accepted")
    # Re-verify instead of trusting a forged dataclass instance.
    try:
        if physical_schema_authority is None:
            fresh = verify_callback_program(
                verified.program,
                geometry_proof_authorities=geometry_proof_authorities,
            )
        else:
            fresh = _reverify_physical_schema_authority(
                verified, physical_schema_authority)
    except CallbackVerificationError as exc:
        raise CallbackAbiError(
            "callback_ir_reverification",
            exc.path,
            f"{exc.code}: {exc.message}",
        ) from exc
    if fresh.ir_sha256 != verified.ir_sha256 or fresh.effect_digest != verified.effect_digest:
        _fail("verified_identity_mismatch", "program", "verified program identities do not rederive")

    role_functions = {
        item.role: item for item in verified.program.functions if item.role is not None
    }
    proof_sha: str | None = None
    if CallbackRole.ANY_HIT in role_functions:
        proof_sha = _verify_any_hit_authority(verified, any_hit_proof_authority)
    elif any_hit_proof_authority is not None:
        _fail("unused_any_hit_proof", "any_hit_proof", "program has no any-hit role")

    records = {item.name: item for item in verified.program.records}
    roles: list[RoleAbi] = []
    for role in CallbackRole:
        function = role_functions.get(role)
        if function is None:
            continue
        inputs: list[AbiField] = [
            AbiField("in.context.launch_index", "u64", "in", "launch_index", True),
        ]
        for argument in function.arguments:
            inputs.extend(_flatten_type(
                argument.value_type,
                f"in.{argument.name}",
                direction="in",
                records=records,
                seen=set(),
            ))
        variants = _effect_variants(function, records)
        nonce = int(hashlib.sha256(
            f"{verified.ir_sha256}:{verified.effect_digest}:{role.value}".encode("ascii")
        ).hexdigest()[:8], 16)
        roles.append(RoleAbi(
            role=role,
            role_tag=_ROLE_TAGS[role],
            stage_tag=_STAGE_TAGS[ROLE_STAGE[role]],
            symbol=f"rtdl_v4_{role.value}_{verified.ir_sha256[:16]}",
            inputs=tuple(inputs),
            status=_STATUS_FIELDS,
            effects=variants,
            first_error_policy=_FIRST_ERROR_POLICY,
            nonce_word=nonce,
        ))

    base = CompiledCallbackAbi(
        schema_id=CALLBACK_ABI_SCHEMA_ID,
        schema_version=CALLBACK_ABI_SCHEMA_VERSION,
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        any_hit_proof_sha256=proof_sha,
        any_hit_proof_kind=(
            None if any_hit_proof_authority is None else any_hit_proof_authority.proof_kind
        ),
        any_hit_delivery_contract=(
            None
            if any_hit_proof_authority is None
            else any_hit_proof_authority.delivery_contract.value
        ),
        runtime_status_codes=_RUNTIME_STATUS_CODES,
        roles=tuple(roles),
        abi_sha256="",
    )
    digest = hashlib.sha256(_canonical_json(base.payload_without_digest())).hexdigest()
    return CompiledCallbackAbi(**{**base.__dict__, "abi_sha256": digest})


def callback_abi_from_dict(payload: Mapping[str, object]) -> CompiledCallbackAbi:
    """Strictly decode and revalidate a serialized ABI artifact."""

    try:
        expected_keys = {
            "schema_id", "schema_version", "callback_ir_sha256",
            "callback_effect_digest", "any_hit_proof_sha256",
            "any_hit_proof_kind", "any_hit_delivery_contract", "runtime_status_codes",
            "roles", "abi_sha256",
        }
        if set(payload) != expected_keys:
            _fail("artifact_keys", "abi", repr(sorted(set(payload) ^ expected_keys)))
        schema_id = _required_string(payload["schema_id"], "abi.schema_id")
        schema_version = _required_string(payload["schema_version"], "abi.schema_version")
        if schema_id != CALLBACK_ABI_SCHEMA_ID or schema_version != CALLBACK_ABI_SCHEMA_VERSION:
            _fail("artifact_schema", "abi", f"{schema_id} {schema_version}")
        ir_sha = _digest(payload["callback_ir_sha256"], "abi.callback_ir_sha256")
        effect_digest = _digest(payload["callback_effect_digest"], "abi.callback_effect_digest")
        proof_sha = _optional_digest(payload["any_hit_proof_sha256"], "abi.any_hit_proof_sha256")
        proof_kind = _optional_string(payload["any_hit_proof_kind"], "abi.any_hit_proof_kind")
        delivery = _optional_string(
            payload["any_hit_delivery_contract"], "abi.any_hit_delivery_contract"
        )
        if (proof_sha is None) != (proof_kind is None) or (proof_sha is None) != (delivery is None):
            _fail("artifact_any_hit_proof_shape", "abi", "proof fields must be all null or all present")
        if delivery is not None:
            contract = AnyHitDeliveryContract(delivery)
            if proof_kind not in _ANY_HIT_PROOF_KINDS[contract]:
                _fail("artifact_any_hit_proof_kind", "abi.any_hit_proof_kind", str(proof_kind))
        raw_status_codes = payload["runtime_status_codes"]
        if (
            not isinstance(raw_status_codes, Mapping)
            or dict(raw_status_codes) != dict(_RUNTIME_STATUS_CODES)
        ):
            _fail("artifact_runtime_status_codes", "abi.runtime_status_codes", "status code drift")
        raw_roles = payload["roles"]
        if not isinstance(raw_roles, list):
            _fail("artifact_roles", "abi.roles", "expected list")
        roles = tuple(
            _role_from_dict(item, ir_sha, effect_digest, index)
            for index, item in enumerate(raw_roles)
        )
        if len({item.role for item in roles}) != len(roles):
            _fail("artifact_duplicate_role", "abi.roles", "duplicate callback role")
        if tuple(sorted(roles, key=lambda item: list(CallbackRole).index(item.role))) != roles:
            _fail("artifact_role_order", "abi.roles", "roles are not in canonical order")
        role_set = {item.role for item in roles}
        legacy_required = {
            CallbackRole.BOUNDS, CallbackRole.MAKE_RAY, CallbackRole.INTERSECTION,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        }
        triangle_required = {
            CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        }
        legacy_shape = legacy_required <= role_set and bool(
            {CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT} & role_set)
        triangle_shape = role_set == triangle_required
        if not (legacy_shape or triangle_shape):
            _fail(
                "artifact_role_cardinality", "abi.roles",
                "neither the legacy custom-AABB nor built-in-triangle role topology is complete",
            )
        if (CallbackRole.ANY_HIT in role_set) != (proof_sha is not None):
            _fail("artifact_any_hit_proof_role", "abi", "proof presence must match any-hit role")
        artifact = CompiledCallbackAbi(
            schema_id=schema_id,
            schema_version=schema_version,
            callback_ir_sha256=ir_sha,
            callback_effect_digest=effect_digest,
            any_hit_proof_sha256=proof_sha,
            any_hit_proof_kind=proof_kind,
            any_hit_delivery_contract=delivery,
            runtime_status_codes=_RUNTIME_STATUS_CODES,
            roles=roles,
            abi_sha256=_digest(payload["abi_sha256"], "abi.abi_sha256"),
        )
        expected = hashlib.sha256(_canonical_json(artifact.payload_without_digest())).hexdigest()
        if artifact.abi_sha256 != expected:
            _fail("artifact_digest", "abi.abi_sha256", "ABI digest does not rederive")
        return artifact
    except CallbackAbiError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise CallbackAbiError(
            "artifact_decode_error", "abi", f"{type(exc).__name__}: {exc}"
        ) from exc


def verify_compiled_callback_abi(
    artifact: CompiledCallbackAbi | Mapping[str, object],
    verified: VerifiedCallbackProgram,
    *,
    any_hit_proof_authority: AnyHitProofAuthority | None = None,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
    physical_schema_authority: object | None = None,
) -> CompiledCallbackAbi:
    """Recompile the exact IR and require byte-semantic ABI equality.

    A self-consistent serialized ABI is not authority for the Callback IR it
    names.  Consumers must call this function with the exact verified program;
    it prevents a hostile artifact from inventing a different scalar layout
    while retaining a valid-looking IR digest.
    """

    decoded = artifact if isinstance(artifact, CompiledCallbackAbi) else callback_abi_from_dict(artifact)
    expected = compile_callback_abi(
        verified,
        any_hit_proof_authority=any_hit_proof_authority,
        geometry_proof_authorities=geometry_proof_authorities,
        physical_schema_authority=physical_schema_authority,
    )
    if decoded != expected:
        _fail("artifact_ir_recompile_mismatch", "abi", "serialized ABI differs from exact IR recompilation")
    return decoded


def _role_from_dict(payload: object, ir_sha: str, effect_digest: str, index: int) -> RoleAbi:
    path = f"abi.roles[{index}]"
    if not isinstance(payload, Mapping):
        _fail("artifact_role", path, "expected object")
    keys = {
        "role", "symbol", "inputs", "status", "effects",
        "role_tag", "stage_tag", "first_error_policy", "nonce_word", "parameter_order",
    }
    if set(payload) != keys:
        _fail("artifact_role_keys", path, repr(sorted(set(payload) ^ keys)))
    role = CallbackRole(_required_string(payload["role"], f"{path}.role"))
    role_tag = _required_int(payload["role_tag"], f"{path}.role_tag")
    stage_tag = _required_int(payload["stage_tag"], f"{path}.stage_tag")
    if role_tag != _ROLE_TAGS[role] or stage_tag != _STAGE_TAGS[ROLE_STAGE[role]]:
        _fail("artifact_role_stage_tag", path, f"{role_tag}/{stage_tag}")
    symbol = _required_string(payload["symbol"], f"{path}.symbol")
    if symbol != f"rtdl_v4_{role.value}_{ir_sha[:16]}":
        _fail("artifact_symbol", f"{path}.symbol", symbol)
    inputs = _fields_from_list(payload["inputs"], f"{path}.inputs")
    if any(item.direction != "in" or not item.path.startswith("in.") for item in inputs):
        _fail("artifact_input_layout", f"{path}.inputs", "input direction/path mismatch")
    status = _fields_from_list(payload["status"], f"{path}.status")
    if status != _STATUS_FIELDS:
        _fail("artifact_status_layout", f"{path}.status", "status layout drift")
    raw_effects = payload["effects"]
    if not isinstance(raw_effects, list):
        _fail("artifact_effects", f"{path}.effects", "expected list")
    effects: list[EffectVariantAbi] = []
    for effect_index, raw_effect in enumerate(raw_effects):
        effect_path = f"{path}.effects[{effect_index}]"
        if not isinstance(raw_effect, Mapping) or set(raw_effect) != {"tag", "kind", "fields"}:
            _fail("artifact_effect", effect_path, "invalid effect object")
        kind = EffectKind(_required_string(raw_effect["kind"], f"{effect_path}.kind"))
        tag = _required_int(raw_effect["tag"], f"{effect_path}.tag")
        if tag != _EFFECT_TAGS[kind]:
            _fail("artifact_effect_tag", f"{effect_path}.tag", str(tag))
        effects.append(EffectVariantAbi(
            tag=tag,
            kind=kind,
            fields=_fields_from_list(raw_effect["fields"], f"{effect_path}.fields"),
        ))
        if any(
            item.direction != "out" or not item.path.startswith("out.")
            for item in effects[-1].fields
        ):
            _fail("artifact_output_layout", f"{effect_path}.fields", "output direction/path mismatch")
    if not effects or len({item.tag for item in effects}) != len(effects):
        _fail("artifact_effect_set", f"{path}.effects", "empty or duplicate effect variants")
    if not {item.kind for item in effects} <= _ROLE_EFFECTS[role]:
        _fail("artifact_role_effect", f"{path}.effects", "effect is illegal for role")
    if tuple(sorted(effects, key=lambda item: (item.tag, tuple(f.path for f in item.fields)))) != tuple(effects):
        _fail("artifact_effect_order", f"{path}.effects", "effects are not canonical")
    nonce = _required_int(payload["nonce_word"], f"{path}.nonce_word")
    policy = _required_string(payload["first_error_policy"], f"{path}.first_error_policy")
    if policy != _FIRST_ERROR_POLICY:
        _fail("artifact_first_error_policy", f"{path}.first_error_policy", policy)
    role_abi = RoleAbi(role, role_tag, stage_tag, symbol, inputs, status, tuple(effects), policy, nonce)
    expected_nonce = int(hashlib.sha256(
        f"{ir_sha}:{effect_digest}:{role.value}".encode("ascii")
    ).hexdigest()[:8], 16)
    if nonce != expected_nonce:
        _fail("artifact_nonce", f"{path}.nonce_word", str(nonce))
    raw_order = payload["parameter_order"]
    if not isinstance(raw_order, list) or not all(isinstance(item, str) for item in raw_order):
        _fail("artifact_parameter_order", f"{path}.parameter_order", "expected string list")
    if tuple(raw_order) != role_abi.parameter_order:
        _fail("artifact_parameter_order", f"{path}.parameter_order", "order does not rederive")
    return role_abi


def _fields_from_list(payload: object, path: str) -> tuple[AbiField, ...]:
    if not isinstance(payload, list):
        _fail("artifact_fields", path, "expected list")
    fields: list[AbiField] = []
    for index, raw in enumerate(payload):
        field_path = f"{path}[{index}]"
        if not isinstance(raw, Mapping) or set(raw) != {
            "path", "scalar", "direction", "semantic_type", "readonly"
        }:
            _fail("artifact_field", field_path, "invalid field object")
        readonly = raw["readonly"]
        if type(readonly) is not bool:
            _fail("artifact_field_readonly", f"{field_path}.readonly", repr(readonly))
        fields.append(AbiField(
            path=_required_string(raw["path"], f"{field_path}.path"),
            scalar=_required_string(raw["scalar"], f"{field_path}.scalar"),
            direction=_required_string(raw["direction"], f"{field_path}.direction"),
            semantic_type=_required_string(raw["semantic_type"], f"{field_path}.semantic_type"),
            readonly=readonly,
        ))
    if len({item.path for item in fields}) != len(fields):
        _fail("artifact_duplicate_field", path, "duplicate field path")
    return tuple(fields)


def _required_string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("artifact_string", path, repr(value))
    return value


def _optional_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, path)


def _required_int(value: object, path: str) -> int:
    if type(value) is not int:
        _fail("artifact_integer", path, repr(value))
    return value


def _digest(value: object, path: str) -> str:
    result = _required_string(value, path)
    if _SHA256.fullmatch(result) is None:
        _fail("artifact_digest_shape", path, result)
    return result


def _optional_digest(value: object, path: str) -> str | None:
    return None if value is None else _digest(value, path)


def _verify_any_hit_authority(
    verified: VerifiedCallbackProgram,
    authority: AnyHitProofAuthority | None,
) -> str:
    if authority is None:
        _fail(
            "any_hit_proof_required",
            "any_hit_proof",
            "a manifest declaration does not prove delivery confluence",
        )
    assert authority is not None
    for path, value in (
        ("callback_ir_sha256", authority.callback_ir_sha256),
        ("effect_digest", authority.effect_digest),
        ("proof_sha256", authority.proof_sha256),
    ):
        if _SHA256.fullmatch(value) is None:
            _fail("any_hit_proof_identity", f"any_hit_proof.{path}", value)
    expected_contract = verified.program.manifest.any_hit_delivery
    if (
        authority.callback_ir_sha256 != verified.ir_sha256
        or authority.effect_digest != verified.effect_digest
        or authority.delivery_contract is not expected_contract
    ):
        _fail("any_hit_proof_mismatch", "any_hit_proof", "proof does not bind the exact verified program")
    allowed = _ANY_HIT_PROOF_KINDS[authority.delivery_contract]
    if authority.proof_kind not in allowed:
        _fail(
            "any_hit_proof_kind",
            "any_hit_proof.proof_kind",
            f"{authority.proof_kind!r} is not recognized for {authority.delivery_contract.value}",
        )
    if authority.proof_kind == "compiler_recognized_commutative_idempotent_reduction_v1":
        expected = derive_compiler_recognized_any_hit_proof(verified)
        if authority != expected:
            _fail(
                "any_hit_compiler_proof_mismatch", "any_hit_proof",
                "authority is not the proof rederived from the verified IR",
            )
    return authority.proof_sha256


def _local(expression, name: str) -> bool:
    return (expression.opcode == "local" and
            expression.attribute("name") == name and not expression.operands)


def _field(expression, base: str, name: str) -> bool:
    return (expression.opcode == "field" and
            expression.attribute("name") == name and
            len(expression.operands) == 1 and _local(expression.operands[0], base))


def _binary(expression, opcode: str, left, right) -> bool:
    return (expression.opcode == opcode and len(expression.operands) == 2 and
            left(expression.operands[0]) and right(expression.operands[1]))


def _returned_payload(statement, local_name: str) -> bool:
    if not isinstance(statement, ReturnEffectStatement):
        return False
    payload = statement.effect.field("payload")
    return (statement.effect.kind is EffectKind.ACCEPT_CONTINUE and
            payload is not None and _local(payload, local_name))


def _recognizes_lexicographic_min_any_hit(verified: VerifiedCallbackProgram) -> bool:
    """Recognize the closed `(f32 distance, u32 id)` minimum reduction."""

    function = verified.program.function_for_role(CallbackRole.ANY_HIT)
    if ([item.name for item in function.arguments] != ["hit", "payload"] or
            len(function.body) != 1 or not isinstance(function.body[0], IfStatement)):
        return False
    branch = function.body[0]
    hit_t = lambda item: _field(item, "hit", "t")
    best_t = lambda item: _field(item, "payload", "best_t")
    hit_id = lambda item: _field(item, "hit", "hit_kind")
    best_id = lambda item: _field(item, "payload", "best_id")
    condition_ok = _binary(
        branch.condition, "or",
        lambda item: _binary(item, "lt", hit_t, best_t),
        lambda item: _binary(
            item, "and",
            lambda part: _binary(part, "eq", hit_t, best_t),
            lambda part: _binary(part, "lt", hit_id, best_id),
        ),
    )
    if not condition_ok or len(branch.then_body) != 2 or len(branch.else_body) != 1:
        return False
    binding = branch.then_body[0]
    if not isinstance(binding, LetStatement) or binding.name != "updated":
        return False
    constructed = binding.value
    if (constructed.opcode != "construct" or
            tuple(constructed.attribute("field_names") or ()) != ("best_t", "best_id") or
            len(constructed.operands) != 2 or
            not hit_t(constructed.operands[0]) or not hit_id(constructed.operands[1])):
        return False
    return (_returned_payload(branch.then_body[1], "updated") and
            _returned_payload(branch.else_body[0], "payload"))


def derive_compiler_recognized_any_hit_proof(
    verified: VerifiedCallbackProgram,
) -> AnyHitProofAuthority:
    """Derive, rather than trust, the first compiler-recognized confluence proof."""

    verified = verify_callback_program(verified.program)
    delivery = verified.program.manifest.any_hit_delivery
    if delivery is not AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL:
        _fail("any_hit_compiler_proof_contract", "any_hit", str(delivery))
    if not _recognizes_lexicographic_min_any_hit(verified):
        _fail(
            "any_hit_compiler_proof_shape", "any_hit",
            "callback is not the admitted lexicographic-minimum normal form",
        )
    payload = {
        "schema": "rtdl.v4.compiler_any_hit_proof.v1",
        "callback_ir_sha256": verified.ir_sha256,
        "effect_digest": verified.effect_digest,
        "delivery_contract": delivery.value,
        "normal_form": "lexicographic_min_f32_distance_then_u32_id",
        "algebra": "associative_commutative_idempotent_minimum",
        "strict_nonfinite_policy": verified.program.manifest.numeric.nonfinite_input,
    }
    proof_sha = hashlib.sha256(_canonical_json(payload)).hexdigest()
    return AnyHitProofAuthority(
        callback_ir_sha256=verified.ir_sha256,
        effect_digest=verified.effect_digest,
        delivery_contract=delivery,
        proof_sha256=proof_sha,
        proof_kind="compiler_recognized_commutative_idempotent_reduction_v1",
    )


def _effect_variants(
    function: CallbackFunction,
    records: Mapping[str, object],
) -> tuple[EffectVariantAbi, ...]:
    effects: list[CallbackEffect] = []
    _collect_effects(function.body, effects)
    variants: dict[str, EffectVariantAbi] = {}
    for effect in effects:
        fields: list[AbiField] = []
        for name, expression in effect.fields:
            fields.extend(_flatten_type(
                expression.value_type,
                f"out.{effect.kind.value}.{name}",
                direction="out",
                records=records,
                seen=set(),
            ))
        variant = EffectVariantAbi(_EFFECT_TAGS[effect.kind], effect.kind, tuple(fields))
        key = json.dumps(variant.to_dict(), sort_keys=True, separators=(",", ":"))
        variants[key] = variant
    return tuple(sorted(variants.values(), key=lambda item: (item.tag, tuple(f.path for f in item.fields))))


def _collect_effects(statements: Sequence[CallbackStatement], output: list[CallbackEffect]) -> None:
    for statement in statements:
        if isinstance(statement, ReturnEffectStatement):
            output.append(statement.effect)
        elif isinstance(statement, IfStatement):
            _collect_effects(statement.then_body, output)
            _collect_effects(statement.else_body, output)
        elif isinstance(statement, StaticForStatement):
            _collect_effects(statement.body, output)


def _flatten_type(
    value_type: CallbackType,
    path: str,
    *,
    direction: str,
    records: Mapping[str, object],
    seen: set[str],
) -> list[AbiField]:
    semantic = _type_text(value_type)
    if value_type.kind is TypeKind.SCALAR:
        assert value_type.scalar is not None
        return [AbiField(path, value_type.scalar.value, direction, semantic, direction == "in")]
    if value_type.kind is TypeKind.VECTOR:
        assert value_type.scalar is not None
        return [
            AbiField(f"{path}.{lane}", value_type.scalar.value, direction, semantic, direction == "in")
            for lane in "xyzw"[:value_type.lanes]
        ]
    if value_type.kind is TypeKind.TUPLE:
        result: list[AbiField] = []
        for index, item in enumerate(value_type.items):
            result.extend(_flatten_type(
                item, f"{path}.{index}", direction=direction, records=records, seen=seen,
            ))
        return result
    if value_type.kind is TypeKind.READ_ONLY_VIEW:
        # Views lower to deterministic structure-of-arrays columns.  A single
        # opaque pointer would force generated Numba code to reinterpret an
        # unverified C struct layout.  One typed pointer per scalar leaf keeps
        # both the wrapper ABI and device dereference semantics explicit.
        element = _flatten_type(
            value_type.items[0],
            f"{path}.element",
            direction=direction,
            records=records,
            seen=seen,
        )
        columns = [
            AbiField(
                item.path.replace(f"{path}.element", f"{path}.columns", 1),
                f"device_ptr<{item.scalar}>",
                direction,
                f"readonly_column<{item.semantic_type}>",
                True,
            )
            for item in element
        ]
        columns.append(AbiField(f"{path}.length", "u64", direction, "element_count", True))
        return columns
    if value_type.kind is TypeKind.BUILTIN:
        members = _BUILTIN_FIELDS.get(value_type.name or "")
        if members is None:
            _fail("builtin_layout", path, str(value_type.name))
        result = []
        for name, item in members:
            result.extend(_flatten_type(
                item, f"{path}.{name}", direction=direction, records=records, seen=seen,
            ))
        return result
    if value_type.kind is TypeKind.RECORD:
        name = value_type.name or ""
        if name in seen:
            _fail("recursive_record_layout", path, name)
        record = records.get(name)
        if record is None or not hasattr(record, "fields"):
            _fail("record_layout", path, name)
        result = []
        for field in record.fields:
            result.extend(_flatten_type(
                field.value_type,
                f"{path}.{field.name}",
                direction=direction,
                records=records,
                seen=seen | {name},
            ))
        return result
    _fail("type_layout", path, value_type.kind.value)
    raise AssertionError


def _type_text(value_type: CallbackType) -> str:
    return json.dumps(value_type.to_dict(), sort_keys=True, separators=(",", ":"))


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _fail(code: str, path: str, message: str) -> None:
    raise CallbackAbiError(code, path, message)


__all__ = [
    "CALLBACK_ABI_SCHEMA_ID",
    "CALLBACK_ABI_SCHEMA_VERSION",
    "AbiField",
    "AnyHitProofAuthority",
    "CallbackAbiError",
    "CompiledCallbackAbi",
    "EffectVariantAbi",
    "RoleAbi",
    "callback_abi_from_dict",
    "compile_callback_abi",
    "derive_compiler_recognized_any_hit_proof",
    "verify_compiled_callback_abi",
]
