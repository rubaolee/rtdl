"""Trusted OptiX built-in-triangle wrapper for Callback IR v2.

The generated source owns every OptiX builtin and the GAS/SBT-facing ABI.
Verified Numba leaves receive only typed scalar/view arguments.  In
particular, user code cannot call ``optixGetPrimitiveIndex`` or
``optixGetHitKind`` itself and cannot supply an intersection program for a
built-in triangle GAS.
"""

from __future__ import annotations

import hashlib

from .v4_callback_abi import CallbackAbiError, CompiledCallbackAbi, verify_compiled_callback_abi
from .v4_callback_ir import CallbackRole, EffectKind, ScalarKind, TypeKind
from .v4_callback_optix_wrapper_codegen import (
    CallbackWrapperCodegenError,
    GeneratedOptixWrapper,
    _call_block,
    _effect_tag,
    _indent,
    _prototype,
)
from .v4_typed_physical_schema import (
    AdjacencySide,
    BufferSemantic,
    GeometryFamily,
    ReferenceTemplateId,
    VerifiedPhysicalSchemaAuthority,
    CanonicalPhysicalPlan,
    default_reference_templates,
    lower_canonical_reference_plan,
    verify_typed_physical_schema,
)


def _fail(code: str, detail: str) -> None:
    raise CallbackWrapperCodegenError(code, detail)


def _fresh_authority(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
) -> VerifiedPhysicalSchemaAuthority:
    orientation = authority.triangle_orientation_authority
    if orientation is None:
        _fail("triangle_orientation_authority", "live authority is absent")
    fresh = verify_typed_physical_schema(
        authority.callback,
        authority.schema,
        target=authority.target,
        orientation_authorities={orientation.authority_sha256: orientation},
    )
    if fresh != authority:
        _fail("physical_authority_reverification", "authority does not rederive")
    expected_plan = lower_canonical_reference_plan(fresh, default_reference_templates())
    if plan != expected_plan or plan.template_id is not ReferenceTemplateId.BUILTIN_TRIANGLE_V1:
        _fail("canonical_plan_binding", "exact built-in-triangle reference plan required")
    if plan.executable:
        _fail("reference_plan_state", "Goal5755 reference plan must remain non-executable")
    if authority.schema.geometry_family is not GeometryFamily.BUILTIN_TRIANGLE:
        _fail("geometry_family", authority.schema.geometry_family.value)
    if orientation.front_hit_selects is not AdjacencySide.FRONT \
            or orientation.back_hit_selects is not AdjacencySide.BACK:
        _fail("orientation_mapping", "front/back adjacency authority is unsupported")
    return fresh


def _u32_record_fields(authority: VerifiedPhysicalSchemaAuthority, record_name: str) -> tuple[str, ...]:
    record = next(
        (item for item in authority.callback.program.records if item.name == record_name),
        None,
    )
    if record is None or len(record.fields) != 3:
        _fail("u32x3_record", record_name)
    names: list[str] = []
    for field in record.fields:
        if field.value_type.kind is not TypeKind.SCALAR \
                or field.value_type.scalar is not ScalarKind.U32:
            _fail("u32x3_record", f"{record_name}.{field.name}")
        names.append(field.name)
    return tuple(names)


def generate_trusted_optix_triangle_wrapper_v1(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> GeneratedOptixWrapper:
    """Generate the exact four-role built-in-triangle wrapper.

    This first executable triangle template deliberately admits one closed
    shape: ``Query(origin,direction,tmax)``, a three-u32 payload/output, and two
    primitive-indexed read-only u32 metadata columns.  A different shape must
    add a reviewed physical template; it is never inferred from field names.
    """

    fresh = _fresh_authority(authority, plan)
    try:
        canonical = verify_compiled_callback_abi(
            abi,
            fresh.callback,
            physical_schema_authority=fresh,
        )
    except CallbackAbiError as exc:
        raise CallbackWrapperCodegenError(
            "abi_admission", f"{exc.code}@{exc.path}: {exc.message}"
        ) from exc
    roles = {item.role: item for item in canonical.roles}
    required_roles = {
        CallbackRole.MAKE_RAY,
        CallbackRole.CLOSEST_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    }
    if set(roles) != required_roles:
        _fail("role_set", repr(sorted(item.value for item in set(roles) ^ required_roles)))

    program = fresh.callback.program
    payload_fields = _u32_record_fields(fresh, program.manifest.payload_record)
    output_fields = _u32_record_fields(fresh, program.manifest.output_record)
    closest_function = program.function_for_role(CallbackRole.CLOSEST_HIT)
    if len(closest_function.arguments) != 4:
        _fail("closest_hit_shape", "expected hit, payload, and two metadata views")
    first_view = closest_function.arguments[2].name
    second_view = closest_function.arguments[3].name
    metadata_semantics = {
        binding.argument_index: binding.buffer_semantic
        for binding in fresh.schema.hit_metadata_bindings
        if binding.role is CallbackRole.CLOSEST_HIT
    }
    if set(metadata_semantics) != {2, 3}:
        _fail(
            "closest_hit_metadata_bindings",
            "the two trailing closest-hit arguments need exact physical bindings",
        )
    metadata_sources = {
        BufferSemantic.PRIMITIVE_FRONT_VALUE: "params.front_values",
        BufferSemantic.PRIMITIVE_BACK_VALUE: "params.back_values",
    }
    try:
        first_view_source = metadata_sources[metadata_semantics[2]]
        second_view_source = metadata_sources[metadata_semantics[3]]
    except KeyError as exc:
        _fail(
            "closest_hit_metadata_semantic",
            f"unsupported metadata semantic: {exc.args[0]}",
        )
    metadata_binding_manifest = "\n".join((
        "// RTDL_METADATA_ARGUMENT_2="
        f"{metadata_semantics[2].value};SOURCE={first_view_source}",
        "// RTDL_METADATA_ARGUMENT_3="
        f"{metadata_semantics[3].value};SOURCE={second_view_source}",
    ))

    query_input_paths = {
        "in.context.launch_index", "in.launch_id",
        "in.queries.columns.origin.x", "in.queries.columns.origin.y",
        "in.queries.columns.origin.z", "in.queries.columns.direction.x",
        "in.queries.columns.direction.y", "in.queries.columns.direction.z",
        "in.queries.columns.tmax", "in.queries.length",
    }
    payload_paths = {f"in.payload.{name}" for name in payload_fields}
    expected_inputs = {
        CallbackRole.MAKE_RAY: query_input_paths,
        CallbackRole.CLOSEST_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.primitive_index",
            "in.hit.hit_kind", "in.hit.barycentrics.x", "in.hit.barycentrics.y",
            *payload_paths,
            f"in.{first_view}.columns", f"in.{first_view}.length",
            f"in.{second_view}.columns", f"in.{second_view}.length",
        },
        CallbackRole.MISS: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax", *payload_paths,
        },
        CallbackRole.FINALIZE: {"in.context.launch_index", *payload_paths},
    }
    for role, expected in expected_inputs.items():
        observed = {field.path for field in roles[role].inputs}
        if observed != expected:
            _fail("template_input_shape", f"{role.value}:{sorted(observed ^ expected)}")

    prototypes = "\n".join(
        _prototype(roles[role])
        for role in sorted(
            required_roles, key=lambda item: list(CallbackRole).index(item)
        )
    )
    common = r'''
#include <optix_device.h>

struct V4TriangleLaunchStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4TriangleParams {
    OptixTraversableHandle traversable;
    const float* query_ox; const float* query_oy; const float* query_oz;
    const float* query_dx; const float* query_dy; const float* query_dz;
    const float* query_tmax;
    const unsigned int* front_values; const unsigned int* back_values;
    const float3* vertices; const uint3* triangle_indices;
    const unsigned int* boundary_owner;
    unsigned int primitive_count, query_count;
    unsigned int* output_0; unsigned int* output_1; unsigned int* output_2;
    unsigned int* observed_primitive_index; unsigned int* observed_hit_kind;
    float* observed_barycentric_x; float* observed_barycentric_y;
    V4TriangleLaunchStatus* status; unsigned long long* role_counters;
};
extern "C" { __constant__ V4TriangleParams params; }

static __forceinline__ __device__ void v4_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    V4TriangleLaunchStatus* record = params.status + query;
    if (atomicCAS(&record->first_error_claimed, 0u, 1u) == 0u) {
        record->error_code = code; record->stage = stage; record->role = role;
        record->launch_index = launch_index; record->error_site = site;
        record->effect_tag = effect; record->nonce_word = nonce;
    }
}
static __forceinline__ __device__ bool v4_commit_leaf_status(
        unsigned int query, unsigned int ok, unsigned int error_code,
        unsigned int stage, unsigned int role, unsigned long long launch_index,
        unsigned int error_site, unsigned int effect_tag, unsigned int nonce,
        unsigned int invocation_mask, unsigned int first_error_claimed,
        unsigned int expected_stage, unsigned int expected_role,
        unsigned int expected_nonce) {
    const unsigned int expected_mask = 1u << (expected_role - 1u);
    const bool valid = ok == 1u && error_code == 0u &&
        stage == expected_stage && role == expected_role &&
        launch_index == (unsigned long long)query && error_site == 0u &&
        nonce == expected_nonce && invocation_mask == expected_mask &&
        first_error_claimed == 0u && effect_tag != 0u;
    if (!valid) {
        v4_first_error(query, error_code ? error_code : 0xffff1001u,
                       stage, role, launch_index, error_site, effect_tag, nonce);
        return false;
    }
    atomicOr(&params.status[query].invocation_mask, invocation_mask);
    atomicAdd(params.role_counters + expected_role - 1u, 1ull);
    return true;
}
'''

    q = "query"
    mr, mr_out = _call_block(roles[CallbackRole.MAKE_RAY], "mr", {
        "in.context.launch_index": q,
        "in.launch_id": q,
        "in.queries.columns.origin.x": "params.query_ox",
        "in.queries.columns.origin.y": "params.query_oy",
        "in.queries.columns.origin.z": "params.query_oz",
        "in.queries.columns.direction.x": "params.query_dx",
        "in.queries.columns.direction.y": "params.query_dy",
        "in.queries.columns.direction.z": "params.query_dz",
        "in.queries.columns.tmax": "params.query_tmax",
        "in.queries.length": "(unsigned long long)params.query_count",
    }, query_expression=q, failure_statement="return;")
    fin_inputs = {"in.context.launch_index": q}
    for index, name in enumerate(payload_fields):
        fin_inputs[f"in.payload.{name}"] = f"payload_{index}"
    fin, fin_out = _call_block(
        roles[CallbackRole.FINALIZE], "fin", fin_inputs,
        query_expression=q, failure_statement="return;",
    )
    payload_init = "\n".join(
        f"    unsigned int payload_{index} = {mr_out[f'out.trace_request.payload.{name}']};"
        for index, name in enumerate(payload_fields)
    )
    payload_args = ", ".join(f"payload_{index}" for index in range(3))

    # OptiX does not define primitive-index tie breaking for equal-distance
    # built-in-triangle hits.  The compiler-owned any-hit program below
    # therefore enumerates every candidate and carries the canonical
    # (t, primitive_index) minimum in payload registers.  Only after traversal
    # does raygen invoke exactly one verified user closest-hit or miss leaf.
    closest_inputs = {
        "in.context.launch_index": q,
        "in.hit.t": "selected_hit_t",
        "in.hit.primitive_index": "selected_primitive_index",
        "in.hit.hit_kind": "selected_hit_kind",
        "in.hit.barycentrics.x": "selected_barycentrics.x",
        "in.hit.barycentrics.y": "selected_barycentrics.y",
        f"in.{first_view}.columns": first_view_source,
        f"in.{first_view}.length": "(unsigned long long)params.primitive_count",
        f"in.{second_view}.columns": second_view_source,
        f"in.{second_view}.length": "(unsigned long long)params.primitive_count",
    }
    for index, name in enumerate(payload_fields):
        closest_inputs[f"in.payload.{name}"] = f"payload_{index}"
    ch, ch_out = _call_block(
        roles[CallbackRole.CLOSEST_HIT], "ch", closest_inputs,
        query_expression=q, failure_statement="return;",
    )
    assign_closest_payload = "\n".join(
        f"        payload_{index} = {ch_out[f'out.payload.payload.{name}']};"
        for index, name in enumerate(payload_fields)
    )

    miss_inputs = {
        "in.context.launch_index": q,
        "in.ray.origin.x": "__uint_as_float(ray_ox)",
        "in.ray.origin.y": "__uint_as_float(ray_oy)",
        "in.ray.origin.z": "__uint_as_float(ray_oz)",
        "in.ray.direction.x": "__uint_as_float(ray_dx)",
        "in.ray.direction.y": "__uint_as_float(ray_dy)",
        "in.ray.direction.z": "__uint_as_float(ray_dz)",
        "in.ray.tmin": "__uint_as_float(ray_tmin)",
        "in.ray.tmax": "__uint_as_float(ray_tmax)",
    }
    for index, name in enumerate(payload_fields):
        miss_inputs[f"in.payload.{name}"] = f"payload_{index}"
    ms, ms_out = _call_block(
        roles[CallbackRole.MISS], "ms", miss_inputs,
        query_expression=q, failure_statement="return;",
    )
    assign_miss_payload = "\n".join(
        f"        payload_{index} = {ms_out[f'out.payload.payload.{name}']};"
        for index, name in enumerate(payload_fields)
    )

    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_triangle() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    params.status[query] = {{0u, 0u, 0u, 0u, (unsigned long long)query, 0u, 0u, 0u, 0u}};
    params.observed_primitive_index[query] = 0xffffffffu;
    params.observed_hit_kind[query] = 0xffffffffu;
    params.observed_barycentric_x[query] = __int_as_float(0x7fffffffu);
    params.observed_barycentric_y[query] = __int_as_float(0x7fffffffu);
{_indent(mr, 4)}
    if ({mr_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_first_error(query, 0xffff1002u, 0u, 0u, query, 0u, {mr_out['out.effect_tag']}, 0u); return;
    }}
{payload_init}
    unsigned int ray_ox = __float_as_uint({mr_out['out.trace_request.origin.x']});
    unsigned int ray_oy = __float_as_uint({mr_out['out.trace_request.origin.y']});
    unsigned int ray_oz = __float_as_uint({mr_out['out.trace_request.origin.z']});
    unsigned int ray_dx = __float_as_uint({mr_out['out.trace_request.direction.x']});
    unsigned int ray_dy = __float_as_uint({mr_out['out.trace_request.direction.y']});
    unsigned int ray_dz = __float_as_uint({mr_out['out.trace_request.direction.z']});
    unsigned int ray_tmin = __float_as_uint({mr_out['out.trace_request.tmin']});
    unsigned int ray_tmax = __float_as_uint({mr_out['out.trace_request.tmax']});
    unsigned int best_t_bits = 0x7f800000u;
    unsigned int best_primitive = 0xffffffffu;
    unsigned int best_hit_kind = 0xffffffffu;
    unsigned int best_barycentric_x = 0x7fffffffu;
    unsigned int best_barycentric_y = 0x7fffffffu;
    unsigned int best_found = 0u;
    unsigned int collector_reserved_0 = 0u;
    unsigned int collector_reserved_1 = 0u;
    optixTrace(params.traversable,
        make_float3({mr_out['out.trace_request.origin.x']}, {mr_out['out.trace_request.origin.y']}, {mr_out['out.trace_request.origin.z']}),
        make_float3({mr_out['out.trace_request.direction.x']}, {mr_out['out.trace_request.direction.y']}, {mr_out['out.trace_request.direction.z']}),
        {mr_out['out.trace_request.tmin']}, {mr_out['out.trace_request.tmax']}, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE,
        0, 1, 0, {payload_args}, best_t_bits, best_primitive,
        best_hit_kind, best_barycentric_x, best_barycentric_y, best_found,
        collector_reserved_0, collector_reserved_1);
    if (params.status[query].first_error_claimed != 0u) return;
    if (best_found == 1u) {{
        const float selected_hit_t = __uint_as_float(best_t_bits);
        const unsigned int selected_primitive_index = best_primitive;
        if (!isfinite(selected_hit_t) || selected_hit_t < 0.0f ||
                selected_primitive_index >= params.primitive_count) {{
            v4_first_error(query, 0xffff1004u, 0u, 0u, query, 0u, 0u, 0u); return;
        }}
        const uint3 selected_triangle =
            params.triangle_indices[selected_primitive_index];
        const float3 vertex_a = params.vertices[selected_triangle.x];
        const float3 vertex_b = params.vertices[selected_triangle.y];
        const float3 vertex_c = params.vertices[selected_triangle.z];
        const float3 edge_0 = make_float3(
            vertex_b.x - vertex_a.x,
            vertex_b.y - vertex_a.y,
            vertex_b.z - vertex_a.z);
        const float3 edge_1 = make_float3(
            vertex_c.x - vertex_a.x,
            vertex_c.y - vertex_a.y,
            vertex_c.z - vertex_a.z);
        const float3 ray_origin = make_float3(
            __uint_as_float(ray_ox), __uint_as_float(ray_oy),
            __uint_as_float(ray_oz));
        const float3 ray_direction = make_float3(
            __uint_as_float(ray_dx), __uint_as_float(ray_dy),
            __uint_as_float(ray_dz));
        const float3 hit_point = make_float3(
            ray_origin.x + selected_hit_t * ray_direction.x,
            ray_origin.y + selected_hit_t * ray_direction.y,
            ray_origin.z + selected_hit_t * ray_direction.z);
        const float3 point_offset = make_float3(
            hit_point.x - vertex_a.x,
            hit_point.y - vertex_a.y,
            hit_point.z - vertex_a.z);
        const float d00 = edge_0.x * edge_0.x + edge_0.y * edge_0.y + edge_0.z * edge_0.z;
        const float d01 = edge_0.x * edge_1.x + edge_0.y * edge_1.y + edge_0.z * edge_1.z;
        const float d11 = edge_1.x * edge_1.x + edge_1.y * edge_1.y + edge_1.z * edge_1.z;
        const float d20 = point_offset.x * edge_0.x + point_offset.y * edge_0.y + point_offset.z * edge_0.z;
        const float d21 = point_offset.x * edge_1.x + point_offset.y * edge_1.y + point_offset.z * edge_1.z;
        const float barycentric_denominator = d00 * d11 - d01 * d01;
        if (!isfinite(barycentric_denominator) || barycentric_denominator <= 0.0f) {{
            v4_first_error(query, 0xffff1009u, 0u, 0u, query, 0u, 0u, 0u); return;
        }}
        float selected_barycentric_x =
            (d11 * d20 - d01 * d21) / barycentric_denominator;
        float selected_barycentric_y =
            (d00 * d21 - d01 * d20) / barycentric_denominator;
        const float selected_barycentric_a =
            1.0f - selected_barycentric_x - selected_barycentric_y;
        const float barycentric_guard = 2.0e-5f;
        if (!isfinite(selected_barycentric_x) ||
                !isfinite(selected_barycentric_y) ||
                selected_barycentric_x < -barycentric_guard ||
                selected_barycentric_y < -barycentric_guard ||
                selected_barycentric_a < -barycentric_guard ||
                selected_barycentric_x > 1.0f + barycentric_guard ||
                selected_barycentric_y > 1.0f + barycentric_guard ||
                selected_barycentric_a > 1.0f + barycentric_guard) {{
            v4_first_error(query, 0xffff100au, 0u, 0u, query, 0u, 0u, 0u); return;
        }}
        selected_barycentric_x = fminf(1.0f, fmaxf(0.0f, selected_barycentric_x));
        selected_barycentric_y = fminf(1.0f, fmaxf(0.0f, selected_barycentric_y));
        const float2 selected_barycentrics = make_float2(
            selected_barycentric_x, selected_barycentric_y);
        const float3 normal = make_float3(
            edge_0.y * edge_1.z - edge_0.z * edge_1.y,
            edge_0.z * edge_1.x - edge_0.x * edge_1.z,
            edge_0.x * edge_1.y - edge_0.y * edge_1.x);
        const float direction_dot_normal =
            ray_direction.x * normal.x + ray_direction.y * normal.y +
            ray_direction.z * normal.z;
        if (!isfinite(direction_dot_normal) || direction_dot_normal == 0.0f) {{
            v4_first_error(query, 0xffff100bu, 0u, 0u, query, 0u, 0u, 0u); return;
        }}
        const unsigned int selected_hit_kind =
            direction_dot_normal < 0.0f ? 0xfeu : 0xffu;
        params.observed_primitive_index[query] = selected_primitive_index;
        params.observed_hit_kind[query] = selected_hit_kind;
        params.observed_barycentric_x[query] = selected_barycentrics.x;
        params.observed_barycentric_y[query] = selected_barycentrics.y;
{_indent(ch, 8)}
        if ({ch_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.CLOSEST_HIT], EffectKind.PAYLOAD)}u) {{
            v4_first_error(query, 0xffff1005u, 0u, 0u, query, 0u, {ch_out['out.effect_tag']}, 0u); return;
        }}
{assign_closest_payload}
    }} else {{
{_indent(ms, 8)}
        if ({ms_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
            v4_first_error(query, 0xffff1006u, 0u, 0u, query, 0u, {ms_out['out.effect_tag']}, 0u); return;
        }}
{assign_miss_payload}
    }}
{_indent(fin, 4)}
    if ({fin_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_first_error(query, 0xffff1003u, 0u, 0u, query, 0u, {fin_out['out.effect_tag']}, 0u); return;
    }}
    params.output_0[query] = {fin_out[f'out.output.value.{output_fields[0]}']};
    params.output_1[query] = {fin_out[f'out.output.value.{output_fields[1]}']};
    params.output_2[query] = {fin_out[f'out.output.value.{output_fields[2]}']};
}}
'''

    anyhit = r'''
extern "C" __global__ void __anyhit__rtdl_v4_triangle_canonical() {
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive_index = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive_index >= params.primitive_count) {
        v4_first_error(query, 0xffff1004u, 0u, 0u, query, 0u, 0u, 0u);
        optixTerminateRay();
        return;
    }
    const float hit_t = optixGetRayTmax();
    if (!isfinite(hit_t) || hit_t < 0.0f) {
        v4_first_error(query, 0xffff1007u, 0u, 0u, query, 0u, 0u, 0u);
        optixTerminateRay();
        return;
    }
    const float2 barycentrics = optixGetTriangleBarycentrics();
    const float barycentric_a = 1.0f - barycentrics.x - barycentrics.y;
    unsigned int boundary_mask = 0u;
    if (barycentric_a == 0.0f) boundary_mask |= 1u;
    if (barycentrics.x == 0.0f) boundary_mask |= 2u;
    if (barycentrics.y == 0.0f) boundary_mask |= 4u;
    const unsigned int canonical_primitive = boundary_mask == 0u
        ? primitive_index
        : params.boundary_owner[primitive_index * 7u + boundary_mask - 1u];
    if (canonical_primitive >= params.primitive_count) {
        v4_first_error(query, 0xffff1008u, 0u, 0u, query, 0u, 0u, 0u);
        optixTerminateRay();
        return;
    }
    const float current_t = __uint_as_float(optixGetPayload_3());
    const unsigned int current_primitive = optixGetPayload_4();
    if (hit_t < current_t ||
            (hit_t == current_t && canonical_primitive < current_primitive)) {
        optixSetPayload_3(__float_as_uint(hit_t));
        optixSetPayload_4(canonical_primitive);
        optixSetPayload_5(optixGetHitKind());
        optixSetPayload_6(__float_as_uint(barycentrics.x));
        optixSetPayload_7(__float_as_uint(barycentrics.y));
        optixSetPayload_8(1u);
    }
    optixIgnoreIntersection();
}
'''

    # The physical miss program is inert: every intersection is ignored so
    # OptiX reaches it after enumeration.  Raygen invokes the verified user
    # miss leaf only when the collector found no candidate.
    physical_miss = r'''
extern "C" __global__ void __miss__rtdl_v4_triangle() {}
'''

    source = (
        common + "\n" + metadata_binding_manifest + "\n" + prototypes +
        "\n" + raygen + anyhit + physical_miss
    )
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_trusted_optix_triangle_wrapper.v1",
        physical_template="builtin_triangle_adjacency_u32x3_v1",
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple(
            (role.value, roles[role].symbol)
            for role in sorted(required_roles, key=lambda item: list(CallbackRole).index(item))
        ),
    )


__all__ = ["generate_trusted_optix_triangle_wrapper_v1"]
