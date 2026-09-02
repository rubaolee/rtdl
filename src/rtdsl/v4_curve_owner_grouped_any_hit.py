"""Round-linear-curve physical adapter for owner-grouped any-hit."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    HIT,
    CallbackProgramSpec,
    CallbackRole,
    GeometryAdmission,
    ScalarKind,
    TypeKind,
    VerifiedCallbackProgram,
    _verify_callback_program_with_role_contract,
)
from .v4_curve_physical_schema import (
    BUILTIN_CURVE_CONTRACT,
    CurveTargetProfile,
)
from .v4_owner_grouped_any_hit import (
    VerifiedOwnerGroupedAnyHitContract,
    verify_owner_grouped_any_hit_schema,
)


CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_ID = (
    "https://rtdl.dev/schemas/"
    "v4-builtin-round-linear-curve-owner-grouped-any-hit-v1.json"
)
CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_VERSION = "v1"
CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE = (
    "builtin_round_linear_curve_owner_grouped_any_hit_bool_or_v1"
)
CURVE_OWNER_GROUPED_CANONICAL_FIELD_IDS = (
    "curve_control_points",
    "curve_widths",
    "curve_segment_indices",
    "owner_ids",
    "motion_segments",
    "owner_hit_bits",
    "query_completion_tokens",
    "device_status",
)


class CurveOwnerGroupedAnyHitError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 curve owner-grouped any-hit rejected: {code}@{path}: {message}"
        )


def _fail(code: str, path: str, message: str) -> None:
    raise CurveOwnerGroupedAnyHitError(code, path, message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BuiltinCurveOwnerGroupedAnyHitPhysicalSchema:
    callback_ir_sha256: str
    callback_effect_digest: str
    behavior_schema_sha256: str
    control_point_field_id: str = "curve_control_points"
    width_field_id: str = "curve_widths"
    segment_index_field_id: str = "curve_segment_indices"
    owner_field_id: str = "owner_ids"
    query_field_id: str = "motion_segments"
    owner_output_field_id: str = "owner_hit_bits"
    query_completion_field_id: str = "query_completion_tokens"
    status_field_id: str = "device_status"
    contract_name: str = BUILTIN_CURVE_CONTRACT
    template_id: str = CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE
    geometry_family: str = "builtin_round_linear_curve"
    curve_type: str = "round_linear"
    endcap_policy: str = "optix_curve_endcap_default_round_for_linear"
    width_policy: str = "equal_endpoint_width_per_segment"
    gas_update_policy: str = "static"
    graph_depth: int = 1
    sbt_record_count: int = 1
    motion_blur: bool = False
    primitive_index_offset: int = 0
    schema_id: str = CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_ID
    schema_version: str = CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "template_id": self.template_id,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_effect_digest": self.callback_effect_digest,
            "behavior_schema_sha256": self.behavior_schema_sha256,
            "geometry_contract": self.contract_name,
            "geometry_family": self.geometry_family,
            "curve_type": self.curve_type,
            "endcap_policy": self.endcap_policy,
            "width_policy": self.width_policy,
            "gas_update_policy": self.gas_update_policy,
            "graph_depth": self.graph_depth,
            "sbt_record_count": self.sbt_record_count,
            "motion_blur": self.motion_blur,
            "primitive_index_offset": self.primitive_index_offset,
            "field_ids": list(self.field_ids),
            "buffers": {
                "control_points": "vertex:vec3f32:read_only:vertex_count",
                "widths": "vertex:f32:read_only:vertex_count",
                "segment_indices": "primitive:u32:read_only:primitive_count",
                "owners": "primitive:u32:read_only:primitive_count",
                "queries": "query:motion_segment_f32x6:read_only:query_count",
                "owner_outputs": "owner:u32:zeroed_then_atomic_or:owner_count",
                "query_completion": "query:u32:write_only:query_count",
                "status": "status:status_record:internal:query_count",
            },
            "physical_any_hit": {
                "accepted_effect": "accept_continue",
                "reduction": "owner_hit_bits[owner_ids[primitive_id]] |= 1",
                "intersection_action": "ignore_and_continue",
                "closest_hit_disabled": True,
                "owner_bounds": "device_checked_fail_closed",
            },
            "application_identity_used": False,
        }

    @property
    def field_ids(self) -> tuple[str, ...]:
        return (
            self.control_point_field_id,
            self.width_field_id,
            self.segment_index_field_id,
            self.owner_field_id,
            self.query_field_id,
            self.owner_output_field_id,
            self.query_completion_field_id,
            self.status_field_id,
        )

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class CurveOwnerGroupedAnyHitPlan:
    behavior_schema_sha256: str
    physical_schema_sha256: str
    callback_ir_sha256: str
    callback_effect_digest: str
    target_sha256: str
    authority_nonce: str
    template_id: str = CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE
    executable: bool = False

    def semantic_dict(self) -> dict[str, object]:
        return {
            "behavior_schema_sha256": self.behavior_schema_sha256,
            "physical_schema_sha256": self.physical_schema_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_effect_digest": self.callback_effect_digest,
            "target_sha256": self.target_sha256,
            "authority_nonce": self.authority_nonce,
            "template_id": self.template_id,
            "role_topology": ["make_ray", "any_hit", "miss", "finalize"],
            "executable": self.executable,
        }

    @property
    def plan_sha256(self) -> str:
        return _digest(self.semantic_dict())


@dataclass(frozen=True)
class VerifiedCurveOwnerGroupedAnyHitAuthority:
    behavior: VerifiedOwnerGroupedAnyHitContract
    schema: BuiltinCurveOwnerGroupedAnyHitPhysicalSchema
    target: CurveTargetProfile
    canonical_plan: CurveOwnerGroupedAnyHitPlan

    @property
    def callback(self) -> VerifiedCallbackProgram:
        return self.behavior.callback

    @property
    def authority_nonce(self) -> str:
        return self.canonical_plan.authority_nonce


def verify_callback_program_for_curve_owner_grouped_any_hit(
    program: CallbackProgramSpec,
) -> VerifiedCallbackProgram:
    if program.schema_version != CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION:
        _fail("callback_schema", "program.schema_version", "typed physical v2 required")
    if program.manifest.geometry.contract_name != BUILTIN_CURVE_CONTRACT:
        _fail("curve_contract", "manifest.geometry.contract_name", BUILTIN_CURVE_CONTRACT)
    if program.manifest.attribute_types:
        _fail("curve_attributes", "manifest.attribute_types", "attributes are provider-owned")
    verified = _verify_callback_program_with_role_contract(
        program,
        required_roles=frozenset({
            CallbackRole.MAKE_RAY,
            CallbackRole.ANY_HIT,
            CallbackRole.MISS,
            CallbackRole.FINALIZE,
        }),
        forbidden_roles=frozenset({
            CallbackRole.BOUNDS,
            CallbackRole.INTERSECTION,
            CallbackRole.CLOSEST_HIT,
        }),
        hit_value_type=HIT,
        allow_hit_read_only_views=False,
        allowed_geometry_admissions=frozenset({
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
        }),
        expected_schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    for purpose, name in (
        ("payload", verified.program.manifest.payload_record),
        ("output", verified.program.manifest.output_record),
    ):
        record = verified.program.record(name)
        if len(record.fields) != 1 \
                or record.fields[0].name != "token" \
                or record.fields[0].value_type.kind is not TypeKind.SCALAR \
                or record.fields[0].value_type.scalar is not ScalarKind.U32:
            _fail(
                "record_shape", f"manifest.{purpose}_record",
                "exact token:u32 record required",
            )
    return verified


def verify_curve_owner_grouped_any_hit_physical_schema(
    behavior: VerifiedOwnerGroupedAnyHitContract,
    schema: BuiltinCurveOwnerGroupedAnyHitPhysicalSchema,
    *,
    target: CurveTargetProfile,
) -> VerifiedCurveOwnerGroupedAnyHitAuthority:
    if not isinstance(behavior, VerifiedOwnerGroupedAnyHitContract):
        _fail("behavior_type", "behavior", type(behavior).__name__)
    callback = verify_callback_program_for_curve_owner_grouped_any_hit(
        behavior.callback.program)
    if callback != behavior.callback:
        _fail("callback_reverification", "callback", "callback changed")
    fresh_behavior = verify_owner_grouped_any_hit_schema(
        callback, behavior.schema, behavior.proof)
    if fresh_behavior != behavior:
        _fail("behavior_reverification", "behavior", "behavior changed")
    if not isinstance(schema, BuiltinCurveOwnerGroupedAnyHitPhysicalSchema):
        _fail("schema_type", "schema", type(schema).__name__)
    if not isinstance(target, CurveTargetProfile):
        _fail("target_type", "target", type(target).__name__)
    fresh_target = CurveTargetProfile(
        target.provider,
        target.optix_sdk,
        target.compute_capability,
        target.native_sha256,
        target.supports_builtin_round_linear_curve,
        target.max_graph_depth,
    )
    if schema.schema_id != CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_ID \
            or schema.schema_version != CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_VERSION \
            or schema.template_id != CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE:
        _fail("schema_identity", "schema", "unsupported physical schema")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.callback_effect_digest != callback.effect_digest \
            or schema.behavior_schema_sha256 != behavior.schema.schema_sha256:
        _fail("authority_binding", "schema", "exact behavior/callback binding required")
    if schema.field_ids != CURVE_OWNER_GROUPED_CANONICAL_FIELD_IDS:
        _fail("field_identity", "schema.field_ids", repr(schema.field_ids))
    if schema.contract_name != BUILTIN_CURVE_CONTRACT \
            or schema.geometry_family != "builtin_round_linear_curve" \
            or schema.curve_type != "round_linear" \
            or schema.endcap_policy != "optix_curve_endcap_default_round_for_linear" \
            or schema.width_policy != "equal_endpoint_width_per_segment":
        _fail("geometry_identity", "schema", "exact round-linear curve contract required")
    if schema.gas_update_policy != "static" or schema.graph_depth != 1 \
            or schema.sbt_record_count != 1 or schema.motion_blur is not False \
            or schema.primitive_index_offset != 0:
        _fail("gas_contract", "schema", "static single-GAS contract required")
    nonce = _digest({
        "kind": "verified_curve_owner_grouped_any_hit_authority_v1",
        "behavior": behavior.authority_sha256,
        "physical": schema.schema_sha256,
        "target": fresh_target.target_sha256,
    })
    plan = CurveOwnerGroupedAnyHitPlan(
        behavior.schema.schema_sha256,
        schema.schema_sha256,
        callback.ir_sha256,
        callback.effect_digest,
        fresh_target.target_sha256,
        nonce,
    )
    return VerifiedCurveOwnerGroupedAnyHitAuthority(
        behavior, schema, fresh_target, plan)


__all__ = [
    "BuiltinCurveOwnerGroupedAnyHitPhysicalSchema",
    "CURVE_OWNER_GROUPED_CANONICAL_FIELD_IDS",
    "CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_ID",
    "CURVE_OWNER_GROUPED_PHYSICAL_SCHEMA_VERSION",
    "CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE",
    "CurveOwnerGroupedAnyHitError", "CurveOwnerGroupedAnyHitPlan",
    "VerifiedCurveOwnerGroupedAnyHitAuthority",
    "verify_callback_program_for_curve_owner_grouped_any_hit",
    "verify_curve_owner_grouped_any_hit_physical_schema",
]
