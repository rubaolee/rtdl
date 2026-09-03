"""Trusted custom-AABB wrapper for verified bounded relation emission."""

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


class BoundedRelationWrapperError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BoundedRelationWrapperError(message)


def generate_trusted_bounded_relation_wrapper_v1(
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
) -> GeneratedOptixWrapper:
    from .v4_box_relation_callback import is_exact_standard_relation_callback

    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    _require(fresh == authority, "bounded relation authority did not rederive")
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
    _require(
        is_exact_standard_relation_callback(fresh.physical.callback),
        "fused bounded-relation lowering requires exact standard callback IR",
    )
    roles = {item.role: item for item in canonical.roles}
    _require(set(roles) == set(CallbackRole), "complete seven-role callback required")

    expected = {
        CallbackRole.BOUNDS: {
            "in.context.launch_index", "in.primitive.lower.x", "in.primitive.lower.y",
            "in.primitive.lower.z", "in.primitive.upper.x", "in.primitive.upper.y",
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
            "in.primitive.lower.x", "in.primitive.lower.y", "in.primitive.lower.z",
            "in.primitive.upper.x", "in.primitive.upper.y", "in.primitive.upper.z",
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
            "in.context.launch_index", "in.payload.hit_count", "in.payload.minimum_id",
        },
    }
    for role, fields in expected.items():
        observed = {item.path for item in roles[role].inputs}
        _require(observed == fields, f"bounded relation ABI mismatch: {role.value}")

    prototypes = "\n".join(_prototype(roles[role]) for role in CallbackRole)
    q = "query"
    mr_inputs = {
        "in.context.launch_index": q,
        "in.launch_id": q,
        "in.queries.columns.lower.x": "params.query_lower_x",
        "in.queries.columns.lower.y": "params.query_lower_y",
        "in.queries.columns.lower.z": "params.query_lower_z",
        "in.queries.columns.upper.x": "params.query_upper_x",
        "in.queries.columns.upper.y": "params.query_upper_y",
        "in.queries.columns.upper.z": "params.query_upper_z",
        "in.queries.columns.diagonal_kind": "params.query_diagonal_kind",
        "in.queries.length": "params.query_count",
    }
    mr, mr_out = _call_block(
        roles[CallbackRole.MAKE_RAY], "mr", mr_inputs,
        query_expression=q, failure_statement="return;")
    fin_inputs = {
        "in.context.launch_index": q,
        "in.payload.hit_count": "payload_count",
        "in.payload.minimum_id": "payload_minimum",
    }
    fin, fin_out = _call_block(
        roles[CallbackRole.FINALIZE], "fin", fin_inputs,
        query_expression=q, failure_statement="return;")

    common = r'''
#include <optix_device.h>

struct V4RelationBox {
    float lower_x, lower_y, lower_z, upper_x, upper_y, upper_z;
    unsigned int item_id;
};
struct V4RelationRow { unsigned int source_id, item_id; };
struct V4RelationStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4FastRelationControl {
    unsigned int raw_event_count, unique_event_count, overflowed;
    unsigned int status, legacy_error_seen, error_code, validated_row_count;
};
struct V4RelationParams {
    OptixTraversableHandle traversable;
    const V4RelationBox* primitives;
    const V4RelationBox* queries;
    unsigned int primitive_count, query_count, reverse_orientation;
    float minimum_overlap;
    unsigned long long event_capacity;
    unsigned int* event_count;
    unsigned int* overflowed;
    V4RelationRow* rows;
    unsigned int* output_hit_count;
    unsigned int* output_minimum_id;
    unsigned int* output_intersection_count;
    unsigned int* error_seen;
    V4RelationStatus* status;
    V4FastRelationControl* fast_control;
};
extern "C" { __constant__ V4RelationParams params; }

static __forceinline__ __device__ void v4_relation_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    atomicExch(params.error_seen, 1u);
    if (params.fast_control != nullptr)
        atomicCAS(&params.fast_control->error_code, 0u, code);
    V4RelationStatus* record = params.status + query;
    if (atomicCAS(&record->first_error_claimed, 0u, 1u) == 0u) {
        record->error_code = code; record->stage = stage; record->role = role;
        record->launch_index = launch_index; record->error_site = site;
        record->effect_tag = effect; record->nonce_word = nonce;
    }
}
static __forceinline__ __device__ unsigned long long v4_relation_reserve_row() {
    // Only a successful result needs an exact raw count.  Once the u32
    // semantic storage bound is crossed, ``overflowed`` remains sticky and
    // the host withholds every partial row.  Counter wrap therefore cannot
    // turn an invalid execution into an accepted one or write out of bounds.
    const unsigned int prior = atomicAdd(params.event_count, 1u);
    if ((unsigned long long)prior < params.event_capacity) return prior;
    atomicExch(params.overflowed, 1u);
    return ~0ull;
}
'''

    # The authority above is the exact closed standard callback.  Its seven
    # roles are therefore fused as one proof-carrying OptiX program instead of
    # re-interpreting already-proved status/effect scaffolding per invocation.
    # Generated/compiled leaf identities remain embedded and bound by the
    # compiler; only the executable success path is partially evaluated.
    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_bounded_relation() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) {{
        v4_relation_first_error(query, 0xffff1002u, 2u, 2u, query, 0u,
                                0u, 0u); return;
    }}
    params.status[query] = {{
        0u, 0u, 0u, 0u, (unsigned long long)query, 0u, 0u, 0u, 0u}};
    // Verified partial-evaluation phase marker: this fused producer is now
    // executing the MAKE_RAY obligation for this exact query.
    atomicOr(&params.status[query].invocation_mask, 1u << 1u);
    const V4RelationBox box = params.queries[query];
    float3 origin;
    float3 direction;
    if (params.reverse_orientation == 0u) {{
        origin = make_float3(
            box.upper_x, box.lower_y, 0.0f);
        direction = make_float3(
            box.lower_x - box.upper_x, box.upper_y - box.lower_y, 0.0f);
    }} else {{
        origin = make_float3(
            box.lower_x, box.lower_y, 0.0f);
        direction = make_float3(
            box.upper_x - box.lower_x, box.upper_y - box.lower_y, 0.0f);
    }}
    unsigned int payload_count = 0u;
    unsigned int payload_minimum = 0xffffffffu;
    unsigned int intersection_count = 0u;
    optixTrace(params.traversable, origin, direction, 0.0f, 1.0f, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE, 0, 1, 0,
        payload_count, payload_minimum, intersection_count);
    params.output_hit_count[query] = payload_count;
    params.output_minimum_id[query] = payload_minimum;
    params.output_intersection_count[query] = intersection_count;
    // FINALIZE completes only after trace results are materialized.
    atomicOr(&params.status[query].invocation_mask, 1u << 6u);
    if (params.fast_control != nullptr) {{
        const V4RelationStatus row = params.status[query];
        const unsigned int mask = row.invocation_mask;
        const bool latent_error = row.first_error_claimed != 0u ||
            row.error_code != 0u || row.stage != 0u || row.role != 0u ||
            row.error_site != 0u || row.effect_tag != 0u ||
            row.nonce_word != 0u;
        const unsigned int terminal = mask & ((1u << 4u) | (1u << 5u));
        const bool lifecycle_invalid =
            (mask & ~((1u << 7u) - 1u)) != 0u ||
            (mask & ((1u << 1u) | (1u << 6u))) !=
                ((1u << 1u) | (1u << 6u)) ||
            (terminal != (1u << 4u) && terminal != (1u << 5u));
        const bool evidence_invalid =
            payload_count > intersection_count ||
            (((mask & (1u << 0u)) != 0u) != (intersection_count != 0u)) ||
            (((mask & (1u << 2u)) != 0u) != (intersection_count != 0u)) ||
            (((mask & (1u << 3u)) != 0u) != (payload_count != 0u)) ||
            (((mask & (1u << 4u)) != 0u) != (payload_count != 0u)) ||
            (((mask & (1u << 5u)) != 0u) != (payload_count == 0u));
        if (latent_error || lifecycle_invalid || evidence_invalid) {{
            v4_relation_first_error(
                query, row.error_code ? row.error_code : 0xffff5001u,
                row.stage, row.role, row.launch_index, row.error_site,
                row.effect_tag, row.nonce_word);
            return;
        }}
        atomicAdd(&params.fast_control->validated_row_count, 1u);
    }}
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
    bnd, bnd_out = _call_block(
        roles[CallbackRole.BOUNDS], "bnd",
        {"in.context.launch_index": q, **primitive_inputs},
        query_expression=q, failure_statement="return;")
    inter, inter_out = _call_block(
        roles[CallbackRole.INTERSECTION], "isect",
        {**ray_inputs, **primitive_inputs},
        query_expression=q, failure_statement="return;")
    intersection = f'''
extern "C" __global__ void __intersection__rtdl_v4_bounded_relation() {{
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive_index = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive_index >= params.primitive_count) {{
        v4_relation_first_error(query, 0xffff1004u, 0u, 0u, query, 0u, 0u, 0u); return;
    }}
    const float3 origin = optixGetWorldRayOrigin();
    const float3 direction = optixGetWorldRayDirection();
    const unsigned int prior_intersection_count = optixGetPayload_2();
    if (prior_intersection_count == 0xffffffffu) {{
        v4_relation_first_error(query, 0xffff100au, 3u, 3u, query, 0u,
                                0u, 0u); return;
    }}
    optixSetPayload_2(prior_intersection_count + 1u);
    const float source_x1 = origin.x + direction.x;
    const float source_y1 = origin.y + direction.y;
    const float source_min_x = fminf(origin.x, source_x1);
    const float source_max_x = fmaxf(origin.x, source_x1);
    const float source_min_y = fminf(origin.y, source_y1);
    const float source_max_y = fmaxf(origin.y, source_y1);
    const bool closed =
        {primitive}.lower_x <= source_max_x &&
        {primitive}.upper_x >= source_min_x &&
        {primitive}.lower_y <= source_max_y &&
        {primitive}.upper_y >= source_min_y;
    const float overlap_x = fmaxf(0.0f,
        fminf(source_max_x, {primitive}.upper_x) -
        fmaxf(source_min_x, {primitive}.lower_x));
    const float overlap_y = fmaxf(0.0f,
        fminf(source_max_y, {primitive}.upper_y) -
        fmaxf(source_min_y, {primitive}.lower_y));
    // Both fused BOUNDS and INTERSECTION phases completed for this visit.
    atomicOr(&params.status[query].invocation_mask,
             (1u << 0u) | (1u << 2u));
    if (closed && overlap_x * overlap_y >= params.minimum_overlap)
        optixReportIntersection(0.0f, 0u, {primitive}.item_id, 0u);
}}
'''

    hit_common = {
        "in.context.launch_index": q,
        "in.hit.t": "optixGetRayTmax()",
        "in.hit.hit_kind": "optixGetHitKind()",
        "in.payload.hit_count": "optixGetPayload_0()",
        "in.payload.minimum_id": "optixGetPayload_1()",
    }
    ah, ah_out = _call_block(
        roles[CallbackRole.ANY_HIT], "ah", hit_common,
        query_expression=q, failure_statement="optixIgnoreIntersection(); return;")
    any_hit = f'''
extern "C" __global__ void __anyhit__rtdl_v4_bounded_relation() {{
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int prior_count = optixGetPayload_0();
    if (prior_count == 0xffffffffu) {{
        v4_relation_first_error(
            query, 4u, 3u, 4u, query, 2u, 0u,
            {roles[CallbackRole.ANY_HIT].nonce_word}u);
        optixTerminateRay(); return;
    }}
    const unsigned int updated_count = prior_count + 1u;
    const unsigned int hit_kind = optixGetHitKind();
    const unsigned int prior_minimum = optixGetPayload_1();
    const unsigned int updated_minimum =
        hit_kind < prior_minimum ? hit_kind : prior_minimum;
    const unsigned long long slot = v4_relation_reserve_row();
    if (slot < params.event_capacity) {{
        V4RelationRow row;
        // Pass 0 traces source boxes against indexed boxes.  Pass 1 traces
        // indexed boxes against source boxes to complete the diagonal
        // coverage, but the semantic row orientation stays (source,item).
        if (params.reverse_orientation == 0u) {{
            row.source_id = params.queries[query].item_id;
            row.item_id = optixGetAttribute_0();
        }} else {{
            row.source_id = optixGetAttribute_0();
            row.item_id = params.queries[query].item_id;
        }}
        params.rows[slot] = row;
    }} else {{
        atomicExch(params.overflowed, 1u);
    }}
    optixSetPayload_0(updated_count);
    optixSetPayload_1(updated_minimum);
    atomicOr(&params.status[query].invocation_mask, 1u << 3u);
}}
'''

    ch, ch_out = _call_block(
        roles[CallbackRole.CLOSEST_HIT], "ch", hit_common,
        query_expression=q, failure_statement="return;")
    closest = '''
extern "C" __global__ void __closesthit__rtdl_v4_bounded_relation() {
    const unsigned int query = optixGetLaunchIndex().x;
    if (query < params.query_count)
        atomicOr(&params.status[query].invocation_mask, 1u << 4u);
}
'''

    miss_inputs = {
        "in.context.launch_index": q,
        "in.ray.origin.x": "optixGetWorldRayOrigin().x",
        "in.ray.origin.y": "optixGetWorldRayOrigin().y",
        "in.ray.origin.z": "optixGetWorldRayOrigin().z",
        "in.ray.direction.x": "optixGetWorldRayDirection().x",
        "in.ray.direction.y": "optixGetWorldRayDirection().y",
        "in.ray.direction.z": "optixGetWorldRayDirection().z",
        "in.ray.tmin": "optixGetRayTmin()",
        "in.ray.tmax": "optixGetRayTmax()",
        "in.payload.hit_count": "optixGetPayload_0()",
        "in.payload.minimum_id": "optixGetPayload_1()",
    }
    ms, ms_out = _call_block(
        roles[CallbackRole.MISS], "ms", miss_inputs,
        query_expression=q, failure_statement="return;")
    miss = '''
extern "C" __global__ void __miss__rtdl_v4_bounded_relation() {
    const unsigned int query = optixGetLaunchIndex().x;
    if (query < params.query_count)
        atomicOr(&params.status[query].invocation_mask, 1u << 5u);
}
'''

    source = common + "\n" + prototypes + "\n" + raygen + intersection + any_hit + closest + miss
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_bounded_relation_wrapper.v1",
        physical_template="custom_aabb_bounded_relation_emission_v1",
        callback_ir_sha256=fresh.physical.callback.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple((role.value, roles[role].symbol) for role in CallbackRole),
        # This closed standard callback is partially evaluated by the wrapper;
        # the generated role definitions are identity-bound but not called.
        linked_role_symbols=False,
    )


__all__ = [
    "BoundedRelationWrapperError",
    "generate_trusted_bounded_relation_wrapper_v1",
]
