"""Physical authority for the bounded OptiX round-linear curve route.

Goal5834 covers static, constant-radius round-linear curve segments.  Each
primitive is a capsule: two indexed float32 control points and equal positive
float32 widths.  OptiX owns intersection; RTDL owns the whole callback
protocol, application-ID ordering, lifecycle, and status-before-output rule.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
import struct
from typing import Sequence

from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    HIT,
    CallbackProgramSpec,
    CallbackRole,
    GeometryAdmission,
    TypeKind,
    VerifiedCallbackProgram,
    _verify_callback_program_with_role_contract,
)


CURVE_PHYSICAL_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-builtin-round-linear-curve-physical-v1.json"
)
CURVE_PHYSICAL_SCHEMA_VERSION = "v1"
BUILTIN_CURVE_CONTRACT = "optix_builtin_round_linear_curve_v1"
BUILTIN_CURVE_TEMPLATE = "builtin_round_linear_curve_first_contact_u32x3_v1"
BUILTIN_CURVE_BOOLEAN_TEMPLATE = (
    "builtin_round_linear_curve_provider_any_contact_u32_v1")
CURVE_CANONICAL_FIELD_IDS = (
    "curve_control_points", "curve_widths", "curve_segment_indices",
    "application_ids", "motion_segments", "first_contacts", "device_status",
)
CURVE_BOOLEAN_CANONICAL_FIELD_IDS = (
    "curve_control_points", "curve_widths", "curve_segment_indices",
    "application_ids", "motion_segments", "any_contact_bits", "device_status",
)
CURVE_CONTACT_SEPARATION_MIN_EXPONENT2 = -12
CURVE_DIRECTION_CROSS_RATIO_MIN_EXPONENT2 = -12
CURVE_FRONT_ENTRY_ENDPOINT_MARGIN_EXPONENT2 = -12
CURVE_CONTACT_SEPARATION_MIN = 2.0 ** CURVE_CONTACT_SEPARATION_MIN_EXPONENT2
CURVE_DIRECTION_CROSS_RATIO_MIN = (
    2.0 ** CURVE_DIRECTION_CROSS_RATIO_MIN_EXPONENT2)
CURVE_FRONT_ENTRY_ENDPOINT_MARGIN = (
    2.0 ** CURVE_FRONT_ENTRY_ENDPOINT_MARGIN_EXPONENT2)
CURVE_NUMERIC_POLICY_ID = "rtdl.v4.curve_numeric_admission.v2"
CURVE_PROVIDER_T_SEMANTICS = (
    "optix_provider_reported_float32__no_cpu_toi_accuracy_bound_v1")
CURVE_NUMERIC_POLICY = (
    "binary32_projection__constant_radius_per_segment__"
    "query_axis_cross_ratio_ge_2^-12__"
    "segment_distance_ratio_ge_2^-12__front_entry_endpoint_margin_2^-12__"
    "provider_reported_float32_t__no_cpu_toi_accuracy_bound_v2"
)
CURVE_BOOLEAN_PHYSICAL_SCHEMA_ID = (
    "https://rtdl.dev/schemas/"
    "v4-builtin-round-linear-curve-provider-any-contact-v1.json")
CURVE_BOOLEAN_PHYSICAL_SCHEMA_VERSION = "v1"
CURVE_BOOLEAN_NUMERIC_POLICY_ID = (
    "rtdl.v4.curve_boolean_structural_admission.v1")
CURVE_BOOLEAN_PROVIDER_SEMANTICS = (
    "optix_provider_any_contact_bit__"
    "registered_fixture_evaluation_only_v1")
CURVE_BOOLEAN_NUMERIC_POLICY = (
    "binary32_projection__shape_type_only__nonzero_query__"
    "provider_any_contact_bit__registered_fixture_evaluation_only_v1")


class CurvePhysicalSchemaError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 curve physical schema rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise CurvePhysicalSchemaError(code, path, message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(
        r"[0-9a-f]{64}", value) is not None


def _strict_decimal_version(
    value: object, components: int, path: str,
) -> tuple[int, ...]:
    if not isinstance(value, str) or re.fullmatch(
            rf"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){{{components - 1}}}",
            value) is None:
        _fail("target_version", path, "strict decimal version required")
    result = tuple(int(item) for item in value.split("."))
    if result[0] == 0 or any(item >= 100 for item in result[1:]):
        _fail("target_version", path, "unsupported version form")
    return result


@dataclass(frozen=True)
class CurveTargetProfile:
    provider: str
    optix_sdk: str
    compute_capability: str
    native_sha256: str
    supports_builtin_round_linear_curve: bool = True
    max_graph_depth: int = 1

    def __post_init__(self) -> None:
        if type(self.provider) is not str or self.provider != "optix" \
                or not _is_sha(self.native_sha256):
            _fail("target_identity", "target", "exact OptiX/native identity required")
        _strict_decimal_version(self.optix_sdk, 3, "target.optix_sdk")
        _strict_decimal_version(
            self.compute_capability, 2, "target.compute_capability")
        if type(self.supports_builtin_round_linear_curve) is not bool \
                or self.supports_builtin_round_linear_curve is not True \
                or type(self.max_graph_depth) is not int \
                or self.max_graph_depth != 1:
            _fail(
                "target_capability", "target",
                "static built-in round-linear curve single-GAS support required",
            )

    @property
    def target_sha256(self) -> str:
        return _sha({
            "provider": self.provider,
            "optix_sdk": self.optix_sdk,
            "compute_capability": self.compute_capability,
            "native_sha256": self.native_sha256,
            "supports_builtin_round_linear_curve":
                self.supports_builtin_round_linear_curve,
            "max_graph_depth": self.max_graph_depth,
        })


@dataclass(frozen=True)
class BuiltinCurvePhysicalSchema:
    callback_ir_sha256: str
    effect_digest: str
    control_point_field_id: str
    width_field_id: str
    segment_index_field_id: str
    application_id_field_id: str
    query_field_id: str
    output_field_id: str
    status_field_id: str
    contract_name: str = BUILTIN_CURVE_CONTRACT
    template_id: str = BUILTIN_CURVE_TEMPLATE
    geometry_family: str = "builtin_round_linear_curve"
    curve_type: str = "round_linear"
    endcap_policy: str = "optix_curve_endcap_default_round_for_linear"
    width_policy: str = "equal_endpoint_width_per_segment"
    gas_update_policy: str = "static"
    graph_depth: int = 1
    sbt_record_count: int = 1
    motion_blur: bool = False
    primitive_index_offset: int = 0
    stable_order: tuple[str, ...] = (
        "ordered_float32_t", "application_id")
    numeric_policy_id: str = CURVE_NUMERIC_POLICY_ID
    direction_cross_ratio_min_exponent2: int = (
        CURVE_DIRECTION_CROSS_RATIO_MIN_EXPONENT2)
    contact_separation_min_exponent2: int = (
        CURVE_CONTACT_SEPARATION_MIN_EXPONENT2)
    front_entry_endpoint_margin_exponent2: int = (
        CURVE_FRONT_ENTRY_ENDPOINT_MARGIN_EXPONENT2)
    provider_t_semantics: str = CURVE_PROVIDER_T_SEMANTICS
    control_points_buffer_contract: str = (
        "vertex:vec3f32:read_only:vertex_count")
    widths_buffer_contract: str = "vertex:f32:read_only:vertex_count"
    segment_indices_buffer_contract: str = (
        "primitive:u32:read_only:primitive_count")
    application_ids_buffer_contract: str = (
        "primitive:u32:read_only:primitive_count")
    queries_buffer_contract: str = (
        "query:motion_segment_f32x6:read_only:query_count")
    outputs_buffer_contract: str = "output:u32x3:write_only:query_count"
    status_buffer_contract: str = (
        "status:status_record:internal:query_count")
    t_hit_channel_contract: str = "optix_builtin:f32"
    hit_kind_channel_contract: str = "optix_builtin:u32"
    primitive_index_hit_channel_contract: str = "optix_builtin:u32"
    application_id_hit_channel_contract: str = (
        "compiler_metadata_lookup:u32")
    schema_id: str = CURVE_PHYSICAL_SCHEMA_ID
    schema_version: str = CURVE_PHYSICAL_SCHEMA_VERSION

    def numeric_admission_dict(self) -> dict[str, object]:
        return {
            "policy_id": self.numeric_policy_id,
            "query_axis_cross_ratio_min_exponent2":
                self.direction_cross_ratio_min_exponent2,
            "segment_distance_ratio_min_exponent2":
                self.contact_separation_min_exponent2,
            "front_entry_endpoint_margin_exponent2":
                self.front_entry_endpoint_margin_exponent2,
            "provider_t_semantics": self.provider_t_semantics,
        }

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "control_point_field_id": self.control_point_field_id,
            "width_field_id": self.width_field_id,
            "segment_index_field_id": self.segment_index_field_id,
            "application_id_field_id": self.application_id_field_id,
            "query_field_id": self.query_field_id,
            "output_field_id": self.output_field_id,
            "status_field_id": self.status_field_id,
            "contract_name": self.contract_name,
            "template_id": self.template_id,
            "geometry_family": self.geometry_family,
            "curve_type": self.curve_type,
            "endcap_policy": self.endcap_policy,
            "width_policy": self.width_policy,
            "gas_update_policy": self.gas_update_policy,
            "graph_depth": self.graph_depth,
            "sbt_record_count": self.sbt_record_count,
            "motion_blur": self.motion_blur,
            "primitive_index_offset": self.primitive_index_offset,
            "stable_order": list(self.stable_order),
            "numeric_admission": self.numeric_admission_dict(),
            "buffers": {
                "control_points": self.control_points_buffer_contract,
                "widths": self.widths_buffer_contract,
                "segment_indices": self.segment_indices_buffer_contract,
                "application_ids": self.application_ids_buffer_contract,
                "queries": self.queries_buffer_contract,
                "outputs": self.outputs_buffer_contract,
                "status": self.status_buffer_contract,
            },
            "hit_channels": {
                "t": self.t_hit_channel_contract,
                "hit_kind": self.hit_kind_channel_contract,
                "primitive_index": self.primitive_index_hit_channel_contract,
                "application_id": self.application_id_hit_channel_contract,
            },
        }

    @property
    def schema_sha256(self) -> str:
        return _sha(self.semantic_dict())


@dataclass(frozen=True)
class BuiltinCurveBooleanPhysicalSchema:
    """Fixed provider-any-contact schema with one semantic u32 output.

    The native transport remains u32x3 for compatibility, but lanes 1 and 2
    are compiler-owned deterministic zero padding.  This schema deliberately
    contains no pairwise capsule/query numeric admission contract.
    """

    callback_ir_sha256: str
    effect_digest: str
    control_point_field_id: str
    width_field_id: str
    segment_index_field_id: str
    application_id_field_id: str
    query_field_id: str
    output_field_id: str
    status_field_id: str
    contract_name: str = BUILTIN_CURVE_CONTRACT
    template_id: str = BUILTIN_CURVE_BOOLEAN_TEMPLATE
    geometry_family: str = "builtin_round_linear_curve"
    curve_type: str = "round_linear"
    endcap_policy: str = "optix_curve_endcap_default_round_for_linear"
    width_policy: str = "equal_endpoint_width_per_segment"
    gas_update_policy: str = "static"
    graph_depth: int = 1
    sbt_record_count: int = 1
    motion_blur: bool = False
    primitive_index_offset: int = 0
    stable_order: tuple[str, ...] = (
        "provider_internal_t_then_application_id__not_application_semantic",)
    numeric_policy_id: str = CURVE_BOOLEAN_NUMERIC_POLICY_ID
    admission_mode: str = "shape_type_only_f32_nonzero_query_v1"
    provider_semantics: str = CURVE_BOOLEAN_PROVIDER_SEMANTICS
    control_points_buffer_contract: str = (
        "vertex:vec3f32:read_only:vertex_count")
    widths_buffer_contract: str = "vertex:f32:read_only:vertex_count"
    segment_indices_buffer_contract: str = (
        "primitive:u32:read_only:primitive_count")
    application_ids_buffer_contract: str = (
        "primitive:u32:read_only:primitive_count")
    queries_buffer_contract: str = (
        "query:motion_segment_f32x6:read_only:query_count")
    outputs_buffer_contract: str = "output:u32x3:write_only:query_count"
    semantic_output_contract: str = (
        "output:u32:provider_any_contact_bit:query_count")
    status_buffer_contract: str = (
        "status:status_record:internal:query_count")
    hidden_hit_channel_contract: str = (
        "compiler_owned:optix_t_application_id_primitive_hit_kind")
    schema_id: str = CURVE_BOOLEAN_PHYSICAL_SCHEMA_ID
    schema_version: str = CURVE_BOOLEAN_PHYSICAL_SCHEMA_VERSION

    def numeric_admission_dict(self) -> dict[str, object]:
        return {
            "policy_id": self.numeric_policy_id,
            "admission_mode": self.admission_mode,
            "provider_semantics": self.provider_semantics,
        }

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "control_point_field_id": self.control_point_field_id,
            "width_field_id": self.width_field_id,
            "segment_index_field_id": self.segment_index_field_id,
            "application_id_field_id": self.application_id_field_id,
            "query_field_id": self.query_field_id,
            "output_field_id": self.output_field_id,
            "status_field_id": self.status_field_id,
            "contract_name": self.contract_name,
            "template_id": self.template_id,
            "geometry_family": self.geometry_family,
            "curve_type": self.curve_type,
            "endcap_policy": self.endcap_policy,
            "width_policy": self.width_policy,
            "gas_update_policy": self.gas_update_policy,
            "graph_depth": self.graph_depth,
            "sbt_record_count": self.sbt_record_count,
            "motion_blur": self.motion_blur,
            "primitive_index_offset": self.primitive_index_offset,
            "stable_order": list(self.stable_order),
            "numeric_admission": self.numeric_admission_dict(),
            "buffers": {
                "control_points": self.control_points_buffer_contract,
                "widths": self.widths_buffer_contract,
                "segment_indices": self.segment_indices_buffer_contract,
                "application_ids": self.application_ids_buffer_contract,
                "queries": self.queries_buffer_contract,
                "physical_outputs": self.outputs_buffer_contract,
                "semantic_output": self.semantic_output_contract,
                "status": self.status_buffer_contract,
            },
            "hidden_hit_channels": self.hidden_hit_channel_contract,
        }

    @property
    def schema_sha256(self) -> str:
        return _sha(self.semantic_dict())


@dataclass(frozen=True, eq=False)
class CurveCanonicalPlan:
    schema_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    target_sha256: str
    authority_nonce: str
    template_id: str = BUILTIN_CURVE_TEMPLATE
    executable: bool = False

    def semantic_dict(self) -> dict[str, object]:
        return {
            "template_id": self.template_id,
            "schema_sha256": self.schema_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "target_sha256": self.target_sha256,
            "authority_nonce": self.authority_nonce,
            "executable": self.executable,
        }

    @property
    def plan_sha256(self) -> str:
        return _sha(self.semantic_dict())

    def __eq__(self, other: object) -> bool:
        return type(other) is CurveCanonicalPlan and _canonical(
            self.semantic_dict()) == _canonical(other.semantic_dict())

    def __hash__(self) -> int:
        return hash(self.plan_sha256)


@dataclass(frozen=True)
class VerifiedCurvePhysicalAuthority:
    callback: VerifiedCallbackProgram
    schema: BuiltinCurvePhysicalSchema | BuiltinCurveBooleanPhysicalSchema
    target: CurveTargetProfile
    canonical_plan: CurveCanonicalPlan

    @property
    def authority_nonce(self) -> str:
        return self.canonical_plan.authority_nonce


def verify_callback_program_for_builtin_curve(
    program: CallbackProgramSpec,
) -> VerifiedCallbackProgram:
    if program.schema_version != CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION:
        _fail("callback_schema", "program.schema_version", "typed physical v1 required")
    if program.manifest.geometry.contract_name != BUILTIN_CURVE_CONTRACT:
        _fail("curve_contract", "manifest.geometry.contract_name", BUILTIN_CURVE_CONTRACT)
    if program.manifest.attribute_types:
        _fail("curve_attributes", "manifest.attribute_types", "attributes are compiler-owned")
    verified = _verify_callback_program_with_role_contract(
        program,
        required_roles=frozenset({
            CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        }),
        forbidden_roles=frozenset({
            CallbackRole.BOUNDS, CallbackRole.INTERSECTION, CallbackRole.ANY_HIT,
        }),
        hit_value_type=HIT,
        allow_hit_read_only_views=True,
        allowed_geometry_admissions=frozenset({
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS}),
        expected_schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    closest = verified.program.function_for_role(CallbackRole.CLOSEST_HIT)
    if len(closest.arguments) != 3 or closest.arguments[0].value_type != HIT \
            or closest.arguments[1].value_type.kind is not TypeKind.RECORD \
            or closest.arguments[1].value_type.name \
                != verified.program.manifest.payload_record:
        _fail(
            "closest_hit_signature", "closest_hit",
            "Hit, payload, and one application-ID view required",
        )
    view = closest.arguments[2].value_type
    if view.kind is not TypeKind.READ_ONLY_VIEW \
            or view.items[0].to_dict() != {"kind": "scalar", "scalar": "u32"}:
        _fail(
            "closest_hit_metadata", "closest_hit.arguments[2]",
            "ReadOnlyView[u32] required",
        )
    return verified


def _verify_builtin_curve_boolean_physical_schema(
    callback: VerifiedCallbackProgram,
    schema: BuiltinCurveBooleanPhysicalSchema,
    *,
    target: CurveTargetProfile,
) -> VerifiedCurvePhysicalAuthority:
    if type(target) is not CurveTargetProfile:
        _fail("target_type", "target", type(target).__name__)
    fresh_target = CurveTargetProfile(
        target.provider, target.optix_sdk, target.compute_capability,
        target.native_sha256, target.supports_builtin_round_linear_curve,
        target.max_graph_depth,
    )
    fresh = verify_callback_program_for_builtin_curve(callback.program)
    if fresh != callback:
        _fail("callback_reverification", "callback", "Callback IR does not rederive")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "exact callback/effect identity required")
    records = {item.name: item for item in callback.program.records}
    for path, name in (
            ("manifest.payload_record", callback.program.manifest.payload_record),
            ("manifest.output_record", callback.program.manifest.output_record)):
        record = records.get(name)
        if record is None or len(record.fields) != 1 \
                or record.fields[0].name != "hit" \
                or record.fields[0].value_type.kind is not TypeKind.SCALAR \
                or record.fields[0].value_type.scalar.value != "u32":
            _fail(
                "boolean_record_shape", path,
                "exact one-field hit:u32 record required",
            )
    if schema.schema_id != CURVE_BOOLEAN_PHYSICAL_SCHEMA_ID \
            or schema.schema_version != CURVE_BOOLEAN_PHYSICAL_SCHEMA_VERSION \
            or schema.contract_name != BUILTIN_CURVE_CONTRACT \
            or schema.template_id != BUILTIN_CURVE_BOOLEAN_TEMPLATE \
            or schema.geometry_family != "builtin_round_linear_curve" \
            or schema.curve_type != "round_linear" \
            or schema.endcap_policy \
                != "optix_curve_endcap_default_round_for_linear" \
            or schema.width_policy != "equal_endpoint_width_per_segment":
        _fail(
            "schema_identity", "schema",
            "unsupported round-linear Boolean schema",
        )
    identifiers = (
        schema.control_point_field_id, schema.width_field_id,
        schema.segment_index_field_id, schema.application_id_field_id,
        schema.query_field_id, schema.output_field_id, schema.status_field_id,
    )
    if identifiers != CURVE_BOOLEAN_CANONICAL_FIELD_IDS:
        _fail(
            "field_identity", "schema",
            "exact canonical Boolean seven-field tuple required",
        )
    if schema.gas_update_policy != "static" \
            or type(schema.graph_depth) is not int or schema.graph_depth != 1 \
            or type(schema.sbt_record_count) is not int \
            or schema.sbt_record_count != 1 \
            or type(schema.motion_blur) is not bool or schema.motion_blur is not False \
            or type(schema.primitive_index_offset) is not int \
            or schema.primitive_index_offset != 0:
        _fail("gas_contract", "schema", "static single-GAS curve contract required")
    if type(schema.stable_order) is not tuple or schema.stable_order != (
            "provider_internal_t_then_application_id__not_application_semantic",):
        _fail("stable_order", "schema", repr(schema.stable_order))
    if schema.numeric_policy_id != CURVE_BOOLEAN_NUMERIC_POLICY_ID \
            or schema.admission_mode != "shape_type_only_f32_nonzero_query_v1" \
            or schema.provider_semantics != CURVE_BOOLEAN_PROVIDER_SEMANTICS:
        _fail(
            "numeric_admission", "schema.numeric_admission",
            "exact structural-only Boolean policy required",
        )
    if (
        schema.control_points_buffer_contract,
        schema.widths_buffer_contract,
        schema.segment_indices_buffer_contract,
        schema.application_ids_buffer_contract,
        schema.queries_buffer_contract,
        schema.outputs_buffer_contract,
        schema.semantic_output_contract,
        schema.status_buffer_contract,
        schema.hidden_hit_channel_contract,
    ) != (
        "vertex:vec3f32:read_only:vertex_count",
        "vertex:f32:read_only:vertex_count",
        "primitive:u32:read_only:primitive_count",
        "primitive:u32:read_only:primitive_count",
        "query:motion_segment_f32x6:read_only:query_count",
        "output:u32x3:write_only:query_count",
        "output:u32:provider_any_contact_bit:query_count",
        "status:status_record:internal:query_count",
        "compiler_owned:optix_t_application_id_primitive_hit_kind",
    ):
        _fail(
            "buffer_contract", "schema.buffers",
            "exact Boolean semantic/native projection required",
        )
    nonce = _sha({
        "kind": "builtin_round_linear_curve_boolean_physical_authority_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "schema": schema.schema_sha256,
        "target": fresh_target.target_sha256,
    })
    plan = CurveCanonicalPlan(
        schema.schema_sha256, callback.ir_sha256, callback.effect_digest,
        fresh_target.target_sha256, nonce,
        template_id=BUILTIN_CURVE_BOOLEAN_TEMPLATE,
    )
    return VerifiedCurvePhysicalAuthority(callback, schema, fresh_target, plan)


def verify_builtin_curve_physical_schema(
    callback: VerifiedCallbackProgram,
    schema: BuiltinCurvePhysicalSchema | BuiltinCurveBooleanPhysicalSchema,
    *,
    target: CurveTargetProfile,
) -> VerifiedCurvePhysicalAuthority:
    if type(schema) is BuiltinCurveBooleanPhysicalSchema:
        return _verify_builtin_curve_boolean_physical_schema(
            callback, schema, target=target)
    if type(schema) is not BuiltinCurvePhysicalSchema:
        _fail("schema_type", "schema", type(schema).__name__)
    if type(target) is not CurveTargetProfile:
        _fail("target_type", "target", type(target).__name__)
    fresh_target = CurveTargetProfile(
        target.provider, target.optix_sdk, target.compute_capability,
        target.native_sha256, target.supports_builtin_round_linear_curve,
        target.max_graph_depth,
    )
    fresh = verify_callback_program_for_builtin_curve(callback.program)
    if fresh != callback:
        _fail("callback_reverification", "callback", "Callback IR does not rederive")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "exact callback/effect identity required")
    if schema.schema_id != CURVE_PHYSICAL_SCHEMA_ID \
            or schema.schema_version != CURVE_PHYSICAL_SCHEMA_VERSION \
            or schema.contract_name != BUILTIN_CURVE_CONTRACT \
            or schema.template_id != BUILTIN_CURVE_TEMPLATE \
            or schema.geometry_family != "builtin_round_linear_curve" \
            or schema.curve_type != "round_linear" \
            or schema.endcap_policy \
                != "optix_curve_endcap_default_round_for_linear" \
            or schema.width_policy != "equal_endpoint_width_per_segment":
        _fail("schema_identity", "schema", "unsupported round-linear curve schema")
    identifiers = (
        schema.control_point_field_id, schema.width_field_id,
        schema.segment_index_field_id, schema.application_id_field_id,
        schema.query_field_id, schema.output_field_id, schema.status_field_id,
    )
    if identifiers != CURVE_CANONICAL_FIELD_IDS:
        _fail("field_identity", "schema", "exact canonical seven-field tuple required")
    if schema.gas_update_policy != "static" \
            or type(schema.graph_depth) is not int or schema.graph_depth != 1 \
            or type(schema.sbt_record_count) is not int \
            or schema.sbt_record_count != 1 \
            or type(schema.motion_blur) is not bool or schema.motion_blur is not False \
            or type(schema.primitive_index_offset) is not int \
            or schema.primitive_index_offset != 0:
        _fail("gas_contract", "schema", "static single-GAS curve contract required")
    if type(schema.stable_order) is not tuple or schema.stable_order != (
            "ordered_float32_t", "application_id"):
        _fail("stable_order", "schema", repr(schema.stable_order))
    if schema.numeric_policy_id != CURVE_NUMERIC_POLICY_ID \
            or type(schema.direction_cross_ratio_min_exponent2) is not int \
            or schema.direction_cross_ratio_min_exponent2 \
                != CURVE_DIRECTION_CROSS_RATIO_MIN_EXPONENT2 \
            or type(schema.contact_separation_min_exponent2) is not int \
            or schema.contact_separation_min_exponent2 \
                != CURVE_CONTACT_SEPARATION_MIN_EXPONENT2 \
            or type(schema.front_entry_endpoint_margin_exponent2) is not int \
            or schema.front_entry_endpoint_margin_exponent2 \
                != CURVE_FRONT_ENTRY_ENDPOINT_MARGIN_EXPONENT2 \
            or schema.provider_t_semantics != CURVE_PROVIDER_T_SEMANTICS:
        _fail(
            "numeric_admission", "schema.numeric_admission",
            "exact structured curve numeric policy required",
        )
    if (
        schema.control_points_buffer_contract,
        schema.widths_buffer_contract,
        schema.segment_indices_buffer_contract,
        schema.application_ids_buffer_contract,
        schema.queries_buffer_contract,
        schema.outputs_buffer_contract,
        schema.status_buffer_contract,
    ) != (
        "vertex:vec3f32:read_only:vertex_count",
        "vertex:f32:read_only:vertex_count",
        "primitive:u32:read_only:primitive_count",
        "primitive:u32:read_only:primitive_count",
        "query:motion_segment_f32x6:read_only:query_count",
        "output:u32x3:write_only:query_count",
        "status:status_record:internal:query_count",
    ):
        _fail(
            "buffer_contract", "schema.buffers",
            "exact compiler/native buffer projection required",
        )
    if (
        schema.t_hit_channel_contract,
        schema.hit_kind_channel_contract,
        schema.primitive_index_hit_channel_contract,
        schema.application_id_hit_channel_contract,
    ) != (
        "optix_builtin:f32", "optix_builtin:u32", "optix_builtin:u32",
        "compiler_metadata_lookup:u32",
    ):
        _fail(
            "hit_channel_contract", "schema.hit_channels",
            "exact provider/compiler hit-channel projection required",
        )
    nonce = _sha({
        "kind": "builtin_round_linear_curve_physical_authority_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "schema": schema.schema_sha256,
        "target": fresh_target.target_sha256,
    })
    plan = CurveCanonicalPlan(
        schema.schema_sha256, callback.ir_sha256, callback.effect_digest,
        fresh_target.target_sha256, nonce,
    )
    return VerifiedCurvePhysicalAuthority(callback, schema, fresh_target, plan)


def _f32(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) \
            or not math.isfinite(float(value)):
        _fail("nonfinite_f32", path, repr(value))
    result = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    if not math.isfinite(result):
        _fail("nonfinite_f32", path, repr(value))
    return result


def verify_reference_curve_contents(
    control_points: Sequence[Sequence[float]],
    widths: Sequence[float],
    segment_indices: Sequence[int],
    application_ids: Sequence[int],
) -> tuple[
    tuple[tuple[float, float, float], ...], tuple[float, ...],
    tuple[int, ...], tuple[int, ...],
]:
    if len(control_points) < 2 or len(control_points) != len(widths):
        _fail(
            "curve_vertex_cardinality", "static_input",
            "at least two control points and one width per point required",
        )
    if not segment_indices or len(segment_indices) != len(application_ids):
        _fail(
            "curve_primitive_cardinality", "static_input",
            "equal nonzero segment-index/application-ID columns required",
        )
    points = []
    normalized_widths = []
    for index, point in enumerate(control_points):
        if len(point) != 3:
            _fail("curve_control_point", f"control_points[{index}]", "vec3 required")
        points.append(tuple(
            _f32(value, f"control_points[{index}]") for value in point))
        width = _f32(widths[index], f"widths[{index}]")
        if width <= 0.0:
            _fail("curve_width", f"widths[{index}]", "positive f32 radius required")
        normalized_widths.append(width)
    indices = []
    identities = []
    for primitive, (start, identity) in enumerate(
            zip(segment_indices, application_ids)):
        if not isinstance(start, int) or isinstance(start, bool) \
                or not 0 <= start < len(points) - 1:
            _fail(
                "curve_segment_index", f"segment_indices[{primitive}]",
                "u32 start with start+1 inside control-point buffer required",
            )
        if points[start] == points[start + 1]:
            _fail(
                "zero_length_curve_segment", f"segment_indices[{primitive}]",
                "nonzero centerline segment required",
            )
        if normalized_widths[start] != normalized_widths[start + 1]:
            _fail(
                "tapered_curve_unsupported", f"segment_indices[{primitive}]",
                "Goal5834 supports equal endpoint radii per segment",
            )
        if not isinstance(identity, int) or isinstance(identity, bool) \
                or not 0 <= identity <= 0xFFFFFFFF:
            _fail("application_id", f"application_ids[{primitive}]", "u32 required")
        indices.append(start)
        identities.append(identity)
    if len(set(indices)) != len(indices):
        _fail("duplicate_segment_index", "segment_indices", "segment starts must be unique")
    if len(set(identities)) != len(identities):
        _fail("duplicate_application_id", "application_ids", "IDs must be unique")
    return tuple(points), tuple(normalized_widths), tuple(indices), tuple(identities)


def _dot(a, b) -> float:
    return sum(x * y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _add_scaled(a, b, scale: float):
    return tuple(x + scale * y for x, y in zip(a, b))


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


def _segment_segment_distance2(p1, q1, p2, q2) -> float:
    d1 = _sub(q1, p1)
    d2 = _sub(q2, p2)
    r = _sub(p1, p2)
    a = _dot(d1, d1)
    e = _dot(d2, d2)
    b = _dot(d1, d2)
    c = _dot(d1, r)
    f = _dot(d2, r)
    denominator = a * e - b * b
    s = _clamp((b * f - c * e) / denominator) if denominator > 0.0 else 0.0
    t = (b * s + f) / e
    if t < 0.0:
        t = 0.0
        s = _clamp(-c / a)
    elif t > 1.0:
        t = 1.0
        s = _clamp((b - c) / a)
    delta = _sub(_add_scaled(p1, d1, s), _add_scaled(p2, d2, t))
    return _dot(delta, delta)


def _point_segment_distance2(point, a, b) -> float:
    axis = _sub(b, a)
    t = _clamp(_dot(_sub(point, a), axis) / _dot(axis, axis))
    delta = _sub(point, _add_scaled(a, axis, t))
    return _dot(delta, delta)


def _sphere_roots(origin, direction, center, radius: float):
    offset = _sub(origin, center)
    qa = _dot(direction, direction)
    qb = _dot(offset, direction)
    qc = _dot(offset, offset) - radius * radius
    disc = qb * qb - qa * qc
    if disc < 0.0:
        return ()
    root = math.sqrt(max(0.0, disc))
    return ((-qb - root) / qa, (-qb + root) / qa)


def _capsule_entry(origin, end, a, b, radius: float) -> float | None:
    direction = _sub(end, origin)
    axis = _sub(b, a)
    oa = _sub(origin, a)
    baba = _dot(axis, axis)
    bard = _dot(axis, direction)
    baoa = _dot(axis, oa)
    rdoa = _dot(direction, oa)
    oaoa = _dot(oa, oa)
    dd = _dot(direction, direction)
    side_a = baba * dd - bard * bard
    side_b = baba * rdoa - baoa * bard
    side_c = baba * oaoa - baoa * baoa - radius * radius * baba
    candidates: list[float] = []
    side_disc = side_b * side_b - side_a * side_c
    if side_a > 0.0 and side_disc >= 0.0:
        root = math.sqrt(max(0.0, side_disc))
        for value in ((-side_b - root) / side_a,
                      (-side_b + root) / side_a):
            y = baoa + value * bard
            if 0.0 < y < baba:
                candidates.append(value)
    for center, first_cap in ((a, True), (b, False)):
        for value in _sphere_roots(origin, direction, center, radius):
            point = _add_scaled(origin, direction, value)
            projection = _dot(_sub(point, center), axis)
            if (first_cap and projection <= 0.0) \
                    or (not first_cap and projection >= 0.0):
                candidates.append(value)
    legal = [value for value in candidates if 0.0 <= value <= 1.0]
    return min(legal) if legal else None


def verify_curve_motion_segments(
    starts: Sequence[Sequence[float]],
    ends: Sequence[Sequence[float]],
    *,
    control_points: Sequence[Sequence[float]],
    widths: Sequence[float],
    segment_indices: Sequence[int],
) -> tuple[tuple[float, float, float, float, float, float], ...]:
    if not starts or len(starts) != len(ends):
        _fail("query_cardinality", "queries", "equal nonzero start/end columns required")
    result = []
    for query_index, (start, end) in enumerate(zip(starts, ends)):
        if len(start) != 3 or len(end) != 3:
            _fail("query_shape", f"queries[{query_index}]", "two vec3 values required")
        s = tuple(_f32(value, f"starts[{query_index}]") for value in start)
        e = tuple(_f32(value, f"ends[{query_index}]") for value in end)
        if s == e:
            _fail("zero_direction", f"queries[{query_index}]", "nonzero segment required")
        for primitive, segment_start in enumerate(segment_indices):
            a = control_points[segment_start]
            b = control_points[segment_start + 1]
            radius = widths[segment_start]
            radius2 = radius * radius
            direction = _sub(e, s)
            axis = _sub(b, a)
            direction2 = _dot(direction, direction)
            axis2 = _dot(axis, axis)
            alignment = _dot(direction, axis)
            cross2 = max(
                0.0, direction2 * axis2 - alignment * alignment)
            cross_ratio = cross2 / (direction2 * axis2)
            if _point_segment_distance2(s, a, b) <= radius2:
                _fail(
                    "start_not_strictly_outside", f"queries[{query_index}]",
                    f"curve primitive {primitive}",
                )
            distance2 = _segment_segment_distance2(s, e, a, b)
            if cross_ratio < CURVE_DIRECTION_CROSS_RATIO_MIN \
                    and distance2 <= radius2:
                _fail(
                    "near_parallel_curve_query",
                    f"queries[{query_index}].curves[{primitive}]",
                    "potential query/curve contact has axis cross ratio "
                    "below 2^-12",
                )
            separation = abs(distance2 - radius2) / max(
                distance2 + radius2, float.fromhex("0x1p-126"))
            if separation < CURVE_CONTACT_SEPARATION_MIN:
                _fail(
                    "near_tangent_curve_contact",
                    f"queries[{query_index}].curves[{primitive}]",
                    "segment/capsule distance separation is below 2^-12",
                )
            entry = _capsule_entry(s, e, a, b, radius)
            if entry is not None and (
                    entry <= CURVE_FRONT_ENTRY_ENDPOINT_MARGIN
                    or entry >= 1.0 - CURVE_FRONT_ENTRY_ENDPOINT_MARGIN):
                _fail(
                    "curve_entry_near_trace_endpoint",
                    f"queries[{query_index}].curves[{primitive}]",
                    "front entry lies within the frozen 2^-12 endpoint guard",
                )
        result.append((*s, *e))
    return tuple(result)


def verify_curve_boolean_motion_segments(
    starts: Sequence[Sequence[float]],
    ends: Sequence[Sequence[float]],
) -> tuple[tuple[float, float, float, float, float, float], ...]:
    """Verify only query shape/type/f32/nonzero properties.

    This function intentionally accepts no static geometry.  Introducing
    control points, widths, or primitive indices here would reintroduce the
    O(query x primitive) CPU collision prepass excluded by Goal5834-B1.
    """

    if not starts or len(starts) != len(ends):
        _fail(
            "query_cardinality", "queries",
            "equal nonzero start/end columns required",
        )
    result = []
    for query_index, (start, end) in enumerate(zip(starts, ends)):
        if len(start) != 3 or len(end) != 3:
            _fail(
                "query_shape", f"queries[{query_index}]",
                "two vec3 values required",
            )
        s = tuple(_f32(value, f"starts[{query_index}]") for value in start)
        e = tuple(_f32(value, f"ends[{query_index}]") for value in end)
        if s == e:
            _fail(
                "zero_direction", f"queries[{query_index}]",
                "nonzero segment required",
            )
        result.append((*s, *e))
    return tuple(result)


def verify_curve_first_contact_expected_outputs(
    observed: Sequence[Sequence[int]],
    expected: Sequence[Sequence[int]],
    normalized_queries: Sequence[Sequence[float]],
    *,
    control_points: Sequence[Sequence[float]],
    widths: Sequence[float],
    segment_indices: Sequence[int],
    application_ids: Sequence[int],
) -> tuple[str, ...]:
    observed_rows = tuple(tuple(row) for row in observed)
    expected_rows = tuple(tuple(row) for row in expected)
    if len(observed_rows) != len(expected_rows) \
            or len(observed_rows) != len(normalized_queries):
        _fail("expected_output_cardinality", "expected_output", "query-aligned rows required")
    policies = []
    for index, (actual, gold) in enumerate(zip(observed_rows, expected_rows)):
        if len(actual) != 3 or len(gold) != 3 or any(
                not isinstance(value, int) or isinstance(value, bool)
                or not 0 <= value <= 0xFFFFFFFF
                for value in (*actual, *gold)):
            _fail("expected_output_shape", f"expected_output[{index}]", "u32x3 required")
        if actual[0] != gold[0] or actual[2] != gold[2]:
            _fail(
                "expected_output_identity", f"expected_output[{index}]",
                "hit flag and application ID require exact equality",
            )
        if gold[0] == 0:
            miss = (0, struct.unpack("<I", struct.pack("<f", 1.0))[0], 0xFFFFFFFF)
            if actual != miss or gold != miss:
                _fail("expected_output_miss_bits", f"expected_output[{index}]", "canonical miss required")
            policies.append("miss_exact_bits")
            continue
        if gold[2] not in application_ids:
            _fail("expected_output_application_id", f"expected_output[{index}]", "unknown ID")
        expected_t = struct.unpack("<f", struct.pack("<I", gold[1]))[0]
        actual_t = struct.unpack("<f", struct.pack("<I", actual[1]))[0]
        if not math.isfinite(expected_t) or not 0.0 <= expected_t <= 1.0 \
                or not math.isfinite(actual_t) or not 0.0 <= actual_t <= 1.0:
            _fail("expected_output_t", f"expected_output[{index}]", "finite unit f32 required")
        if actual[1] != gold[1]:
            _fail(
                "expected_output_t_bits", f"expected_output[{index}]",
                "provider-reported float32 time requires exact expected bits",
            )
        policies.append("exact_provider_t_bits")
    return tuple(policies)


__all__ = [
    "BUILTIN_CURVE_BOOLEAN_TEMPLATE", "BUILTIN_CURVE_CONTRACT",
    "BUILTIN_CURVE_TEMPLATE", "BuiltinCurveBooleanPhysicalSchema",
    "BuiltinCurvePhysicalSchema", "CURVE_BOOLEAN_NUMERIC_POLICY",
    "CURVE_BOOLEAN_NUMERIC_POLICY_ID", "CURVE_BOOLEAN_PROVIDER_SEMANTICS",
    "CURVE_CONTACT_SEPARATION_MIN",
    "CURVE_CONTACT_SEPARATION_MIN_EXPONENT2",
    "CURVE_DIRECTION_CROSS_RATIO_MIN",
    "CURVE_DIRECTION_CROSS_RATIO_MIN_EXPONENT2",
    "CURVE_FRONT_ENTRY_ENDPOINT_MARGIN",
    "CURVE_FRONT_ENTRY_ENDPOINT_MARGIN_EXPONENT2",
    "CURVE_NUMERIC_POLICY", "CURVE_NUMERIC_POLICY_ID",
    "CURVE_PROVIDER_T_SEMANTICS",
    "CurveCanonicalPlan", "CurvePhysicalSchemaError",
    "CurveTargetProfile", "VerifiedCurvePhysicalAuthority",
    "verify_builtin_curve_physical_schema",
    "verify_callback_program_for_builtin_curve",
    "verify_curve_boolean_motion_segments",
    "verify_curve_first_contact_expected_outputs", "verify_curve_motion_segments",
    "verify_reference_curve_contents",
]
