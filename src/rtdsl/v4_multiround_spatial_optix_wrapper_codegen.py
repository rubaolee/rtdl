"""Trusted OptiX wrapper for V4 prepared spatial candidate rounds."""

from __future__ import annotations

import hashlib

from .v4_bounded_relation import (
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
    verify_bounded_relation_schema,
)
from .v4_callback_abi import CompiledCallbackAbi, verify_compiled_callback_abi
from .v4_callback_ir import CallbackRole, EffectKind
from .v4_callback_optix_wrapper_codegen import (
    GeneratedOptixWrapper,
    _call_block,
    _effect_tag,
    _indent,
    _prototype,
    _verify_cross_entry_composition,
)


class MultiRoundSpatialWrapperError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MultiRoundSpatialWrapperError(message)


def generate_trusted_multiround_spatial_wrapper_v1(
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
) -> GeneratedOptixWrapper:
    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    _require(fresh == authority, "spatial relation authority did not rederive")
    canonical = verify_compiled_callback_abi(
        abi,
        fresh.physical.callback,
        any_hit_proof_authority=any_hit_proof_authority,
        physical_schema_authority=fresh.physical,
    )
    _require(canonical.abi_sha256 == contract.abi_sha256, "ABI contract drift")
    _require(contract.relation_schema_sha256 == fresh.schema.schema_sha256,
             "relation schema contract drift")
    _require(not contract.executable, "non-executable admission contract required")
    _verify_cross_entry_composition(fresh.physical.callback)
    roles = {item.role: item for item in canonical.roles}
    _require(set(roles) == set(CallbackRole), "complete seven-role callback required")

    expected = {
        CallbackRole.BOUNDS: {
            "in.context.launch_index", "in.primitive.lower.x",
            "in.primitive.lower.y", "in.primitive.lower.z",
            "in.primitive.upper.x", "in.primitive.upper.y",
            "in.primitive.upper.z", "in.primitive.item_id",
        },
        CallbackRole.MAKE_RAY: {
            "in.context.launch_index", "in.launch_id",
            "in.queries.columns.lower.x", "in.queries.columns.lower.y",
            "in.queries.columns.lower.z", "in.queries.columns.upper.x",
            "in.queries.columns.upper.y", "in.queries.columns.upper.z",
            "in.queries.columns.diagonal_kind", "in.queries.length",
        },
        CallbackRole.INTERSECTION: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax",
            "in.primitive.lower.x", "in.primitive.lower.y",
            "in.primitive.lower.z", "in.primitive.upper.x",
            "in.primitive.upper.y", "in.primitive.upper.z",
            "in.primitive.item_id",
        },
        CallbackRole.ANY_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.hit_kind",
            "in.payload.hit_count", "in.payload.minimum_id",
        },
        CallbackRole.CLOSEST_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.hit_kind",
            "in.payload.hit_count", "in.payload.minimum_id",
        },
        CallbackRole.MISS: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax",
            "in.payload.hit_count", "in.payload.minimum_id",
        },
        CallbackRole.FINALIZE: {
            "in.context.launch_index", "in.payload.hit_count",
            "in.payload.minimum_id",
        },
    }
    for role, fields in expected.items():
        _require({item.path for item in roles[role].inputs} == fields,
                 f"spatial candidate ABI mismatch: {role.value}")

    prototypes = "\n".join(_prototype(roles[role]) for role in CallbackRole)
    q = "query"
    make_ray, make_ray_out = _call_block(
        roles[CallbackRole.MAKE_RAY], "mr", {
            "in.context.launch_index": q,
            "in.launch_id": q,
            "in.queries.columns.lower.x": "params.query_x",
            "in.queries.columns.lower.y": "params.query_y",
            "in.queries.columns.lower.z": "params.query_z",
            "in.queries.columns.upper.x": "params.query_tmax",
            "in.queries.columns.upper.y": "params.query_zero",
            "in.queries.columns.upper.z": "params.query_zero",
            "in.queries.columns.diagonal_kind": "params.query_zero_u32",
            "in.queries.length": "params.query_count",
        }, query_expression=q, failure_statement="return;")
    finalize, finalize_out = _call_block(
        roles[CallbackRole.FINALIZE], "fin", {
            "in.context.launch_index": q,
            "in.payload.hit_count": "payload_count",
            "in.payload.minimum_id": "payload_minimum",
        }, query_expression=q, failure_statement="return;")

    common = r'''
#include <optix_device.h>
struct V4SpatialPrimitive {
    float lower_x, lower_y, lower_z, upper_x, upper_y, upper_z;
    unsigned int item_id;
};
struct V4SpatialRow { unsigned int source_id, item_id; };
struct V4SpatialStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4SpatialParams {
    OptixTraversableHandle traversable;
    const V4SpatialPrimitive* primitives;
    const float *query_x, *query_y, *query_z, *query_tmax, *query_zero;
    const unsigned int *query_zero_u32, *query_source_ids;
    unsigned int primitive_count, query_count;
    unsigned long long event_capacity;
    unsigned long long* event_count;
    unsigned int* overflowed;
    V4SpatialRow* rows;
    unsigned int* output_hit_count;
    unsigned int* output_minimum_id;
    V4SpatialStatus* status;
    unsigned long long* role_counters;
};
extern "C" { __constant__ V4SpatialParams params; }

static __forceinline__ __device__ void v4_spatial_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    V4SpatialStatus* record = params.status + query;
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
        v4_spatial_first_error(query, error_code ? error_code : 0xffff3001u,
            stage, role, launch_index, error_site, effect_tag, nonce);
        return false;
    }
    atomicOr(&params.status[query].invocation_mask, invocation_mask);
    atomicAdd(params.role_counters + expected_role - 1u, 1ull);
    return true;
}
static __forceinline__ __device__ unsigned long long v4_spatial_reserve_row() {
    const unsigned long long limit = params.event_capacity + 1ull;
    unsigned long long current = atomicAdd(params.event_count, 0ull);
    while (true) {
        if (current >= limit) {
            atomicExch(params.overflowed, 1u); return ~0ull;
        }
        const unsigned long long prior = atomicCAS(
            params.event_count, current, current + 1ull);
        if (prior == current) return current;
        current = prior;
    }
}
'''

    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_multiround_spatial() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
{_indent(make_ray, 4)}
    if ({make_ray_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_spatial_first_error(query, 0xffff3002u, 0u, 0u, query, 0u,
                               {make_ray_out['out.effect_tag']}, 0u); return;
    }}
    unsigned int payload_count = {make_ray_out['out.trace_request.payload.hit_count']};
    unsigned int payload_minimum = {make_ray_out['out.trace_request.payload.minimum_id']};
    const float3 origin = make_float3(
        {make_ray_out['out.trace_request.origin.x']},
        {make_ray_out['out.trace_request.origin.y']},
        {make_ray_out['out.trace_request.origin.z']});
    const float3 direction = make_float3(
        {make_ray_out['out.trace_request.direction.x']},
        {make_ray_out['out.trace_request.direction.y']},
        {make_ray_out['out.trace_request.direction.z']});
    const float ray_tmin = {make_ray_out['out.trace_request.tmin']};
    const float ray_tmax = {make_ray_out['out.trace_request.tmax']};
    unsigned int p2 = __float_as_uint(origin.x), p3 = __float_as_uint(origin.y);
    unsigned int p4 = __float_as_uint(origin.z), p5 = __float_as_uint(direction.x);
    unsigned int p6 = __float_as_uint(direction.y), p7 = __float_as_uint(direction.z);
    unsigned int p8 = __float_as_uint(ray_tmin), p9 = __float_as_uint(ray_tmax);
    optixTrace(params.traversable, origin, direction, ray_tmin, ray_tmax, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE, 0, 1, 0,
        payload_count, payload_minimum, p2, p3, p4, p5, p6, p7, p8, p9);
    if (params.status[query].first_error_claimed != 0u) return;
{_indent(finalize, 4)}
    if ({finalize_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_spatial_first_error(query, 0xffff3003u, 0u, 0u, query, 0u,
                               {finalize_out['out.effect_tag']}, 0u); return;
    }}
    params.output_hit_count[query] = {finalize_out['out.output.value.hit_count']};
    params.output_minimum_id[query] = {finalize_out['out.output.value.minimum_id']};
}}
'''

    primitive = "params.primitives[primitive_index]"
    primitive_inputs = {
        "in.primitive.lower.x": primitive + ".lower_x",
        "in.primitive.lower.y": primitive + ".lower_y",
        "in.primitive.lower.z": primitive + ".lower_z",
        "in.primitive.upper.x": primitive + ".upper_x",
        "in.primitive.upper.y": primitive + ".upper_y",
        "in.primitive.upper.z": primitive + ".upper_z",
        "in.primitive.item_id": primitive + ".item_id",
    }
    ray_inputs = {
        "in.context.launch_index": q,
        "in.ray.origin.x": "origin.x", "in.ray.origin.y": "origin.y",
        "in.ray.origin.z": "origin.z", "in.ray.direction.x": "direction.x",
        "in.ray.direction.y": "direction.y", "in.ray.direction.z": "direction.z",
        "in.ray.tmin": "optixGetRayTmin()", "in.ray.tmax": "optixGetRayTmax()",
    }
    bounds, bounds_out = _call_block(
        roles[CallbackRole.BOUNDS], "bnd",
        {"in.context.launch_index": q, **primitive_inputs},
        query_expression=q, failure_statement="return;")
    intersection_call, intersection_out = _call_block(
        roles[CallbackRole.INTERSECTION], "isect",
        {**ray_inputs, **primitive_inputs},
        query_expression=q, failure_statement="return;")
    intersection = f'''
extern "C" __global__ void __intersection__rtdl_v4_multiround_spatial() {{
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive_index = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive_index >= params.primitive_count) {{
        v4_spatial_first_error(query, 0xffff3004u, 0u, 0u, query, 0u, 0u, 0u); return;
    }}
    const float3 origin = optixGetWorldRayOrigin();
    const float3 direction = optixGetWorldRayDirection();
{_indent(bounds, 4)}
    if ({bounds_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.BOUNDS], EffectKind.AABB)}u ||
        {bounds_out['out.aabb.lower.x']} != {primitive}.lower_x ||
        {bounds_out['out.aabb.lower.y']} != {primitive}.lower_y ||
        {bounds_out['out.aabb.lower.z']} != {primitive}.lower_z ||
        {bounds_out['out.aabb.upper.x']} != {primitive}.upper_x ||
        {bounds_out['out.aabb.upper.y']} != {primitive}.upper_y ||
        {bounds_out['out.aabb.upper.z']} != {primitive}.upper_z) {{
        v4_spatial_first_error(query, 0xffff3005u, 0u, 0u, query, 0u,
                               {bounds_out['out.effect_tag']}, 0u); return;
    }}
{_indent(intersection_call, 4)}
    if ({intersection_out['out.effect_tag']} == {_effect_tag(roles[CallbackRole.INTERSECTION], EffectKind.NO_HIT)}u) return;
    if ({intersection_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.INTERSECTION], EffectKind.HIT)}u ||
        {intersection_out['out.hit.hit_kind']} != 0u ||
        {intersection_out['out.hit.attributes.0']} != {primitive}.item_id) {{
        v4_spatial_first_error(query, 0xffff3006u, 0u, 0u, query, 0u,
                               {intersection_out['out.effect_tag']}, 0u); return;
    }}
    optixReportIntersection({intersection_out['out.hit.t']}, 0u,
                            {intersection_out['out.hit.attributes.0']}, 0u);
}}
'''

    hit_inputs = {
        "in.context.launch_index": q,
        "in.hit.t": "optixGetRayTmax()",
        "in.hit.hit_kind": "optixGetHitKind()",
        "in.payload.hit_count": "optixGetPayload_0()",
        "in.payload.minimum_id": "optixGetPayload_1()",
    }
    anyhit_call, anyhit_out = _call_block(
        roles[CallbackRole.ANY_HIT], "ah", hit_inputs,
        query_expression=q,
        failure_statement="optixIgnoreIntersection(); return;")
    any_hit = f'''
extern "C" __global__ void __anyhit__rtdl_v4_multiround_spatial() {{
    const unsigned int query = optixGetLaunchIndex().x;
{_indent(anyhit_call, 4)}
    if ({anyhit_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.ANY_HIT], EffectKind.ACCEPT_CONTINUE)}u) {{
        v4_spatial_first_error(query, 0xffff3007u, 0u, 0u, query, 0u,
                               {anyhit_out['out.effect_tag']}, 0u);
        optixIgnoreIntersection(); return;
    }}
    const unsigned long long slot = v4_spatial_reserve_row();
    if (slot < params.event_capacity) {{
        params.rows[slot].source_id = params.query_source_ids[query];
        params.rows[slot].item_id = optixGetAttribute_0();
    }} else {{ atomicExch(params.overflowed, 1u); }}
    optixSetPayload_0({anyhit_out['out.accept_continue.payload.hit_count']});
    optixSetPayload_1({anyhit_out['out.accept_continue.payload.minimum_id']});
    // This physical template enumerates every reported candidate.  Accepting
    // one hit would tighten closest-t and let traversal prune later rows.
    // Ignore only after the checked row/status effects have been committed.
    optixIgnoreIntersection();
}}
'''

    closest_call, closest_out = _call_block(
        roles[CallbackRole.CLOSEST_HIT], "ch", hit_inputs,
        query_expression=q, failure_statement="return;")
    closest = f'''
extern "C" __global__ void __closesthit__rtdl_v4_multiround_spatial() {{
    const unsigned int query = optixGetLaunchIndex().x;
{_indent(closest_call, 4)}
    if ({closest_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.CLOSEST_HIT], EffectKind.PAYLOAD)}u) {{
        v4_spatial_first_error(query, 0xffff3008u, 0u, 0u, query, 0u,
                               {closest_out['out.effect_tag']}, 0u); return;
    }}
    optixSetPayload_0({closest_out['out.payload.payload.hit_count']});
    optixSetPayload_1({closest_out['out.payload.payload.minimum_id']});
}}
'''

    miss_call, miss_out = _call_block(
        roles[CallbackRole.MISS], "ms", {
            "in.context.launch_index": q,
            "in.ray.origin.x": "__uint_as_float(optixGetPayload_2())",
            "in.ray.origin.y": "__uint_as_float(optixGetPayload_3())",
            "in.ray.origin.z": "__uint_as_float(optixGetPayload_4())",
            "in.ray.direction.x": "__uint_as_float(optixGetPayload_5())",
            "in.ray.direction.y": "__uint_as_float(optixGetPayload_6())",
            "in.ray.direction.z": "__uint_as_float(optixGetPayload_7())",
            "in.ray.tmin": "__uint_as_float(optixGetPayload_8())",
            "in.ray.tmax": "__uint_as_float(optixGetPayload_9())",
            "in.payload.hit_count": "optixGetPayload_0()",
            "in.payload.minimum_id": "optixGetPayload_1()",
        }, query_expression=q, failure_statement="return;")
    miss = f'''
extern "C" __global__ void __miss__rtdl_v4_multiround_spatial() {{
    const unsigned int query = optixGetLaunchIndex().x;
{_indent(miss_call, 4)}
    if ({miss_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
        v4_spatial_first_error(query, 0xffff3009u, 0u, 0u, query, 0u,
                               {miss_out['out.effect_tag']}, 0u); return;
    }}
    optixSetPayload_0({miss_out['out.payload.payload.hit_count']});
    optixSetPayload_1({miss_out['out.payload.payload.minimum_id']});
}}
'''

    source = common + "\n" + prototypes + "\n" + raygen + intersection + any_hit + closest + miss
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_multiround_spatial_wrapper.v1",
        physical_template="custom_aabb_prepared_multiround_spatial_v1",
        callback_ir_sha256=fresh.physical.callback.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple((role.value, roles[role].symbol) for role in CallbackRole),
    )


__all__ = [
    "MultiRoundSpatialWrapperError",
    "generate_trusted_multiround_spatial_wrapper_v1",
]
