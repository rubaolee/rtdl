"""Successor physical authority for static OptiX built-in spheres.

The Goal5755 v1 schema is byte-frozen.  Goal5833 therefore adds this closed
successor instead of extending that enum in place.  The authority binds a
four-role Callback IR program to one static sphere GAS, one primitive-aligned
application-id column, and the compiler-owned stable first-contact wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import re
import struct
from typing import Mapping, Sequence

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


SPHERE_PHYSICAL_SCHEMA_ID = "https://rtdl.dev/schemas/v4-builtin-sphere-physical-v1.json"
SPHERE_PHYSICAL_SCHEMA_VERSION = "v1"
BUILTIN_SPHERE_CONTRACT = "optix_builtin_sphere_v1"
BUILTIN_SPHERE_TEMPLATE = "builtin_sphere_first_contact_u32x3_v1"
SPHERE_CANONICAL_FIELD_IDS = (
    "sphere_centers", "sphere_radii", "application_ids",
    "motion_segments", "first_contacts", "device_status",
)

# Binary32 unit roundoff is 2^-24.  For an ordinary (non-tangent) pair, the
# exact discriminant must be separated from zero by at least 4096 unit
# roundoffs relative to the two terms whose subtraction forms it:
#
#   |h^2-a*c| / (h^2+|a*c|) >= 2^-12.
#
# The ratio is dimensionless.  The 4096-u guard is deliberately much larger
# than the operation count of a direct binary32 quadratic and leaves room for
# the implementation-defined OptiX built-in intersection route.  Exact
# tangencies are outside this public path: OptiX's built-in sphere contract
# reports front-face intersections, but does not guarantee that a grazing
# equality (D dot N == 0) is reported as a hit.
BINARY32_UNIT_ROUNDOFF = Fraction(1, 1 << 24)
SPHERE_DISCRIMINANT_SEPARATION_MIN = Fraction(1, 1 << 12)
SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS = 1 << 12
SPHERE_FRONT_ENTRY_ENDPOINT_MARGIN = Fraction(1, 1 << 12)
SPHERE_NONEXACT_TOI_ULP_BOUND = 4
SPHERE_NUMERIC_POLICY = (
    "binary32_projection__disc_ratio_ge_2^-12__"
    "exact_tangent_prelaunch_reject__front_entry_endpoint_margin_2^-12__"
    "nonexact_toi_ulp_le_4_v3"
)


class SpherePhysicalSchemaError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 sphere physical schema rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise SpherePhysicalSchemaError(code, path, message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _strict_decimal_version(value: object, components: int, path: str) -> tuple[int, ...]:
    if not isinstance(value, str) or re.fullmatch(
            rf"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){{{components - 1}}}",
            value) is None:
        _fail("target_version", path, f"strict {components}-component decimal required")
    result = tuple(int(item) for item in value.split("."))
    if result[0] == 0 or any(item >= 100 for item in result[1:]):
        _fail("target_version", path, "major must be positive and later components < 100")
    return result


@dataclass(frozen=True)
class SphereTargetProfile:
    provider: str
    optix_sdk: str
    compute_capability: str
    native_sha256: str
    supports_builtin_sphere: bool = True
    max_graph_depth: int = 1

    def __post_init__(self) -> None:
        if type(self.provider) is not str or self.provider != "optix" \
                or not _is_sha(self.native_sha256):
            _fail("target_identity", "target", "exact OptiX SDK/device/native identity required")
        _strict_decimal_version(self.optix_sdk, 3, "target.optix_sdk")
        _strict_decimal_version(
            self.compute_capability, 2, "target.compute_capability")
        if type(self.supports_builtin_sphere) is not bool \
                or self.supports_builtin_sphere is not True \
                or type(self.max_graph_depth) is not int \
                or self.max_graph_depth != 1:
            _fail("target_capability", "target", "static built-in sphere single-GAS support required")

    @property
    def target_sha256(self) -> str:
        return _sha({
            "provider": self.provider,
            "optix_sdk": self.optix_sdk,
            "compute_capability": self.compute_capability,
            "native_sha256": self.native_sha256,
            "supports_builtin_sphere": self.supports_builtin_sphere,
            "max_graph_depth": self.max_graph_depth,
        })


@dataclass(frozen=True)
class BuiltinSpherePhysicalSchema:
    callback_ir_sha256: str
    effect_digest: str
    center_field_id: str
    radius_field_id: str
    application_id_field_id: str
    query_field_id: str
    output_field_id: str
    status_field_id: str
    contract_name: str = BUILTIN_SPHERE_CONTRACT
    template_id: str = BUILTIN_SPHERE_TEMPLATE
    geometry_family: str = "builtin_sphere"
    gas_update_policy: str = "static"
    graph_depth: int = 1
    sbt_record_count: int = 1
    motion_blur: bool = False
    primitive_index_offset: int = 0
    # Application IDs are required to be unique, so primitive_index can never
    # decide a legal tie.  Keep it as observed physical provenance only; the
    # semantic selection order contains exactly the two decision-bearing keys.
    stable_order: tuple[str, ...] = (
        "ordered_float32_t", "application_id")
    schema_id: str = SPHERE_PHYSICAL_SCHEMA_ID
    schema_version: str = SPHERE_PHYSICAL_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "center_field_id": self.center_field_id,
            "radius_field_id": self.radius_field_id,
            "application_id_field_id": self.application_id_field_id,
            "query_field_id": self.query_field_id,
            "output_field_id": self.output_field_id,
            "status_field_id": self.status_field_id,
            "contract_name": self.contract_name,
            "template_id": self.template_id,
            "geometry_family": self.geometry_family,
            "gas_update_policy": self.gas_update_policy,
            "graph_depth": self.graph_depth,
            "sbt_record_count": self.sbt_record_count,
            "motion_blur": self.motion_blur,
            "primitive_index_offset": self.primitive_index_offset,
            "stable_order": list(self.stable_order),
            "buffers": {
                "centers": "primitive:vec3f32:read_only:primitive_count",
                "radii": "primitive:f32:read_only:primitive_count",
                "application_ids": "primitive:u32:read_only:primitive_count",
                "queries": "query:motion_segment_f32x6:read_only:query_count",
                "outputs": "output:u32x3:write_only:query_count",
                "status": "status:status_record:internal:query_count",
            },
            "hit_channels": {
                "t": "optix_builtin:f32",
                "hit_kind": "optix_builtin:u32",
                "primitive_index": "optix_builtin:u32",
                "application_id": "compiler_metadata_lookup:u32",
            },
        }

    @property
    def schema_sha256(self) -> str:
        return _sha(self.semantic_dict())


@dataclass(frozen=True, eq=False)
class SphereCanonicalPlan:
    schema_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    target_sha256: str
    authority_nonce: str
    template_id: str = BUILTIN_SPHERE_TEMPLATE
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
        return type(other) is SphereCanonicalPlan \
            and _canonical(self.semantic_dict()) == _canonical(other.semantic_dict())

    def __hash__(self) -> int:
        return hash(self.plan_sha256)


@dataclass(frozen=True)
class VerifiedSpherePhysicalAuthority:
    callback: VerifiedCallbackProgram
    schema: BuiltinSpherePhysicalSchema
    target: SphereTargetProfile
    canonical_plan: SphereCanonicalPlan

    @property
    def authority_nonce(self) -> str:
        return self.canonical_plan.authority_nonce


def verify_callback_program_for_builtin_sphere(
    program: CallbackProgramSpec,
) -> VerifiedCallbackProgram:
    if program.schema_version != CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION:
        _fail("callback_schema", "program.schema_version", CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION)
    if program.manifest.geometry.contract_name != BUILTIN_SPHERE_CONTRACT:
        _fail("sphere_contract", "manifest.geometry.contract_name", BUILTIN_SPHERE_CONTRACT)
    if program.manifest.attribute_types:
        _fail("sphere_attributes", "manifest.attribute_types", "built-in sphere attributes are compiler-owned")
    verified = _verify_callback_program_with_role_contract(
        program,
        required_roles=frozenset({
            CallbackRole.MAKE_RAY,
            CallbackRole.CLOSEST_HIT,
            CallbackRole.MISS,
            CallbackRole.FINALIZE,
        }),
        forbidden_roles=frozenset({
            CallbackRole.BOUNDS,
            CallbackRole.INTERSECTION,
            CallbackRole.ANY_HIT,
        }),
        hit_value_type=HIT,
        allow_hit_read_only_views=True,
        allowed_geometry_admissions=frozenset({GeometryAdmission.OPTIX_BUILTIN_SEMANTICS}),
        expected_schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    closest = verified.program.function_for_role(CallbackRole.CLOSEST_HIT)
    if len(closest.arguments) < 2 or closest.arguments[0].value_type != HIT \
            or closest.arguments[1].value_type.kind is not TypeKind.RECORD \
            or closest.arguments[1].value_type.name != verified.program.manifest.payload_record:
        _fail("closest_hit_signature", "closest_hit", "Hit and payload must be the first two arguments")
    if len(closest.arguments) != 3:
        _fail("closest_hit_metadata", "closest_hit", "one application-id view is required")
    view = closest.arguments[2].value_type
    if view.kind is not TypeKind.READ_ONLY_VIEW \
            or view.items[0].to_dict() != {"kind": "scalar", "scalar": "u32"}:
        _fail("closest_hit_metadata", "closest_hit.arguments[2]", "ReadOnlyView[u32] required")
    return verified


def verify_builtin_sphere_physical_schema(
    callback: VerifiedCallbackProgram,
    schema: BuiltinSpherePhysicalSchema,
    *,
    target: SphereTargetProfile,
) -> VerifiedSpherePhysicalAuthority:
    if type(schema) is not BuiltinSpherePhysicalSchema:
        _fail("schema_type", "schema", type(schema).__name__)
    if type(target) is not SphereTargetProfile:
        _fail("target_type", "target", type(target).__name__)
    # A frozen dataclass can still be forged with object.__setattr__.  Rebuild
    # the exact target so its constructor checks every populated target leaf;
    # use that canonical instance for all downstream identities.
    fresh_target = SphereTargetProfile(
        provider=target.provider,
        optix_sdk=target.optix_sdk,
        compute_capability=target.compute_capability,
        native_sha256=target.native_sha256,
        supports_builtin_sphere=target.supports_builtin_sphere,
        max_graph_depth=target.max_graph_depth,
    )
    fresh = verify_callback_program_for_builtin_sphere(callback.program)
    if fresh != callback:
        _fail("callback_reverification", "callback", "Callback IR does not rederive exactly")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "exact callback/effect identity required")
    if schema.schema_id != SPHERE_PHYSICAL_SCHEMA_ID \
            or schema.schema_version != SPHERE_PHYSICAL_SCHEMA_VERSION \
            or schema.contract_name != BUILTIN_SPHERE_CONTRACT \
            or schema.template_id != BUILTIN_SPHERE_TEMPLATE \
            or schema.geometry_family != "builtin_sphere":
        _fail("schema_identity", "schema", "unsupported sphere schema identity")
    identifiers = (
        schema.center_field_id, schema.radius_field_id,
        schema.application_id_field_id, schema.query_field_id,
        schema.output_field_id, schema.status_field_id,
    )
    if identifiers != SPHERE_CANONICAL_FIELD_IDS:
        _fail(
            "field_identity", "schema",
            "closed sphere schema requires the exact canonical six-field tuple")
    if schema.gas_update_policy != "static" \
            or type(schema.graph_depth) is not int or schema.graph_depth != 1 \
            or type(schema.sbt_record_count) is not int \
            or schema.sbt_record_count != 1 \
            or type(schema.motion_blur) is not bool \
            or schema.motion_blur is not False \
            or type(schema.primitive_index_offset) is not int \
            or schema.primitive_index_offset != 0:
        _fail("gas_contract", "schema", "static single-GAS sphere contract required")
    if type(schema.stable_order) is not tuple or schema.stable_order != (
            "ordered_float32_t", "application_id"):
        _fail("stable_order", "schema", repr(schema.stable_order))
    nonce = _sha({
        "kind": "builtin_sphere_physical_authority_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "schema": schema.schema_sha256,
        "target": fresh_target.target_sha256,
    })
    plan = SphereCanonicalPlan(
        schema.schema_sha256, callback.ir_sha256, callback.effect_digest,
        fresh_target.target_sha256, nonce)
    return VerifiedSpherePhysicalAuthority(callback, schema, fresh_target, plan)


def verify_reference_sphere_contents(
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    application_ids: Sequence[int],
) -> tuple[tuple[tuple[float, float, float], ...], tuple[float, ...], tuple[int, ...]]:
    if not centers or len(centers) != len(radii) or len(centers) != len(application_ids):
        _fail("sphere_cardinality", "static_input", "equal nonzero center/radius/id columns required")
    normalized_centers: list[tuple[float, float, float]] = []
    normalized_radii: list[float] = []
    normalized_ids: list[int] = []
    for index, center in enumerate(centers):
        if len(center) != 3:
            _fail("sphere_center", f"centers[{index}]", "vec3 required")
        row = tuple(_f32(value, f"centers[{index}]") for value in center)
        radius = _f32(radii[index], f"radii[{index}]")
        if radius <= 0.0:
            _fail("sphere_radius", f"radii[{index}]", "strictly positive target-f32 radius required")
        identity = application_ids[index]
        if not isinstance(identity, int) or isinstance(identity, bool) or not 0 <= identity <= 0xFFFFFFFF:
            _fail("application_id", f"application_ids[{index}]", "u32 required")
        normalized_centers.append(row)
        normalized_radii.append(radius)
        normalized_ids.append(identity)
    if len(set(normalized_ids)) != len(normalized_ids):
        _fail("duplicate_application_id", "application_ids", "IDs must be unique")
    return tuple(normalized_centers), tuple(normalized_radii), tuple(normalized_ids)


def verify_motion_segments(
    starts: Sequence[Sequence[float]],
    ends: Sequence[Sequence[float]],
    *,
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
) -> tuple[tuple[float, float, float, float, float, float], ...]:
    if not starts or len(starts) != len(ends):
        _fail("query_cardinality", "queries", "equal nonzero start/end columns required")
    result = []
    for index, (start, end) in enumerate(zip(starts, ends)):
        if len(start) != 3 or len(end) != 3:
            _fail("query_shape", f"queries[{index}]", "two vec3 values required")
        s = tuple(_f32(value, f"starts[{index}]") for value in start)
        e = tuple(_f32(value, f"ends[{index}]") for value in end)
        d = tuple(_f32(e[axis] - s[axis], f"queries[{index}].direction") for axis in range(3))
        if d == (0.0, 0.0, 0.0):
            _fail("zero_direction", f"queries[{index}]", "nonzero target-f32 segment required")
        for primitive, (center, radius) in enumerate(zip(centers, radii)):
            exact_offsets = tuple(
                Fraction.from_float(s[axis]) - Fraction.from_float(center[axis])
                for axis in range(3))
            exact_distance2 = sum(
                (item * item for item in exact_offsets), Fraction(0))
            exact_radius = Fraction.from_float(radius)
            if exact_distance2 <= exact_radius * exact_radius:
                _fail("start_not_strictly_outside", f"queries[{index}]", f"sphere {primitive}")
            _verify_conditioned_pair(
                s, d, center, radius,
                path=f"queries[{index}].spheres[{primitive}]",
            )
        result.append((*s, *e))
    return tuple(result)


def _pair_coefficients(
    start: Sequence[float], direction: Sequence[float],
    center: Sequence[float], radius: float,
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    exact_start = tuple(Fraction.from_float(item) for item in start)
    exact_direction = tuple(Fraction.from_float(item) for item in direction)
    exact_center = tuple(Fraction.from_float(item) for item in center)
    exact_radius = Fraction.from_float(radius)
    m = tuple(exact_start[i] - exact_center[i] for i in range(3))
    a = sum((item * item for item in exact_direction), Fraction(0))
    half_b = sum(
        (m[i] * exact_direction[i] for i in range(3)), Fraction(0))
    c = sum((item * item for item in m), Fraction(0)) \
        - exact_radius * exact_radius
    discriminant = half_b * half_b - a * c
    return a, half_b, c, discriminant


def _verify_conditioned_pair(
    start: Sequence[float], direction: Sequence[float],
    center: Sequence[float], radius: float, *, path: str,
) -> None:
    a, half_b, c, discriminant = _pair_coefficients(
        start, direction, center, radius)
    if discriminant == 0:
        _fail(
            "exact_tangent_unsupported_by_optix9_front_face_contract", path,
            "exact grazing contact is outside the bounded nondegenerate "
            "front-face-entry domain",
        )
    scale = half_b * half_b + abs(a * c)
    if abs(discriminant) * SPHERE_DISCRIMINANT_SEPARATION_MIN.denominator \
            < scale * SPHERE_DISCRIMINANT_SEPARATION_MIN.numerator:
        _fail(
            "near_degenerate_contact", path,
            "exact discriminant separation ratio is below 2^-12",
        )
    if discriminant > 0:
        margin = SPHERE_FRONT_ENTRY_ENDPOINT_MARGIN
        for boundary, lower, upper in (
            ("tmin=0", -margin, margin),
            ("tmax=1", Fraction(1) - margin, Fraction(1) + margin),
        ):
            if _compare_rational_to_front_entry(
                    lower, a=a, half_b=half_b,
                    discriminant=discriminant) <= 0 \
                    and _compare_rational_to_front_entry(
                        upper, a=a, half_b=half_b,
                        discriminant=discriminant) >= 0:
                _fail(
                    "front_entry_near_closed_trace_interval_boundary", path,
                    "front-face entry lies within the frozen 2^-12 guard of "
                    + boundary,
                )


def _compare_rational_to_front_entry(
    value: Fraction, *, a: Fraction, half_b: Fraction,
    discriminant: Fraction,
) -> int:
    """Return the exact sign of ``value - front_entry`` without a sqrt.

    For ``r=(-half_b-sqrt(discriminant))/a`` and
    ``y=a*value+half_b``, ``value-r`` has the sign of
    ``y+sqrt(discriminant)``.  When ``y < 0`` that sign is exactly the sign of
    ``discriminant-y*y``.  All operands are Fractions projected from f32.
    """

    y = a * value + half_b
    if y >= 0:
        return 1
    residual = discriminant - y * y
    return 1 if residual > 0 else (-1 if residual < 0 else 0)


def verify_first_contact_expected_outputs(
    observed: Sequence[Sequence[int]],
    expected: Sequence[Sequence[int]],
    normalized_queries: Sequence[Sequence[float]],
    *,
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    application_ids: Sequence[int],
) -> tuple[str, ...]:
    """Check output identity and return the policy applied to every row.

    Hit times are first required to be finite nonnegative binary32 values in
    ``[0,1]``.  Their unsigned encodings are therefore monotone in numerical
    order, making integer encoding distance the exact positive-f32 ULP
    distance.  Exact roots require identical bits; other conditioned roots may
    differ by at most :data:`SPHERE_NONEXACT_TOI_ULP_BOUND` encodings.
    """

    observed_rows = tuple(tuple(row) for row in observed)
    expected_rows = tuple(tuple(row) for row in expected)
    if len(observed_rows) != len(expected_rows) \
            or len(observed_rows) != len(normalized_queries):
        _fail("expected_output_cardinality", "expected_output", "query-aligned rows required")
    id_to_primitive = {identity: index for index, identity in enumerate(application_ids)}
    policies: list[str] = []
    for index, (actual, gold, query) in enumerate(
            zip(observed_rows, expected_rows, normalized_queries)):
        if len(actual) != 3 or len(gold) != 3 \
                or any(not isinstance(item, int) or isinstance(item, bool)
                       or not 0 <= item <= 0xFFFFFFFF for item in (*actual, *gold)):
            _fail("expected_output_shape", f"expected_output[{index}]", "u32x3 required")
        if actual[0] not in (0, 1) or gold[0] not in (0, 1):
            _fail("expected_output_hit_flag", f"expected_output[{index}]", "0/1 required")
        if actual[0] != gold[0] or actual[2] != gold[2]:
            _fail("expected_output_identity", f"expected_output[{index}]",
                  "hit flag and application identity require exact equality")
        if gold[0] == 0:
            miss_bits = struct.unpack("<I", struct.pack("<f", 1.0))[0]
            if gold != (0, miss_bits, 0xFFFFFFFF) or actual != gold:
                _fail("expected_output_miss_bits", f"expected_output[{index}]",
                      "canonical miss sentinel requires bit equality")
            policies.append("miss_exact_bits")
            continue
        primitive = id_to_primitive.get(gold[2])
        if primitive is None:
            _fail("expected_output_application_id", f"expected_output[{index}]",
                  "expected hit ID is absent from static input")
        expected_t = struct.unpack("<f", struct.pack("<I", gold[1]))[0]
        actual_t = struct.unpack("<f", struct.pack("<I", actual[1]))[0]
        if not math.isfinite(expected_t) or not 0.0 <= expected_t <= 1.0:
            _fail("expected_output_t", f"expected_output[{index}]", "finite unit f32 required")
        if not math.isfinite(actual_t) or not 0.0 <= actual_t <= 1.0:
            _fail("observed_output_t", f"observed_output[{index}]", "finite unit f32 required")
        start = tuple(query[:3]); end = tuple(query[3:])
        direction = tuple(_f32(end[axis] - start[axis], "expected.direction")
                          for axis in range(3))
        a, half_b, c, _ = _pair_coefficients(
            start, direction, centers[primitive], radii[primitive])
        exact_t = Fraction.from_float(expected_t)
        exact_root = a * exact_t * exact_t + 2 * half_b * exact_t + c == 0
        if exact_root:
            if actual[1] != gold[1]:
                _fail("expected_output_exact_root_bits", f"expected_output[{index}]",
                      "exact root requires bit equality")
            policies.append("exact_root_bits")
        else:
            if abs(actual[1] - gold[1]) > SPHERE_NONEXACT_TOI_ULP_BOUND:
                _fail("expected_output_t_ulp", f"expected_output[{index}]",
                      f"nonexact time exceeds {SPHERE_NONEXACT_TOI_ULP_BOUND} ULP")
            policies.append(f"nonexact_t_ulp_le_{SPHERE_NONEXACT_TOI_ULP_BOUND}")
    return tuple(policies)


def _f32(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        _fail("nonfinite_f32", path, repr(value))
    result = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    if not math.isfinite(result):
        _fail("nonfinite_f32", path, repr(value))
    return result


__all__ = [
    "BINARY32_UNIT_ROUNDOFF",
    "BUILTIN_SPHERE_CONTRACT", "BUILTIN_SPHERE_TEMPLATE",
    "BuiltinSpherePhysicalSchema", "SphereCanonicalPlan",
    "SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS",
    "SPHERE_DISCRIMINANT_SEPARATION_MIN", "SPHERE_FRONT_ENTRY_ENDPOINT_MARGIN",
    "SPHERE_NONEXACT_TOI_ULP_BOUND",
    "SPHERE_NUMERIC_POLICY",
    "SpherePhysicalSchemaError", "SphereTargetProfile",
    "VerifiedSpherePhysicalAuthority", "verify_builtin_sphere_physical_schema",
    "verify_callback_program_for_builtin_sphere", "verify_motion_segments",
    "verify_first_contact_expected_outputs", "verify_reference_sphere_contents",
]
