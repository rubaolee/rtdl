"""Trusted built-in-triangle wrapper for the Goal5758 reduction contract.

The wrapper is deliberately closed over one schema family.  OptiX owns
triangle intersection; verified Callback-IR owns per-hit acceptance and the
per-ray U64 value; the wrapper may additionally materialize accepted,
capacity-bounded event rows for a compiler-owned checked reducer.  No
application identity or user-provided PTX enters this module.
"""

from __future__ import annotations

import hashlib

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole, EffectKind, ScalarKind, TypeKind
from .v4_callback_optix_wrapper_codegen import (
    CallbackWrapperCodegenError,
    GeneratedOptixWrapper,
    _call_block,
    _effect_tag,
    _indent,
    _prototype,
)
from .v4_triangle_reduction import (
    CompiledTriangleReductionContract,
    MetadataDomain,
    ReducerAlgebra,
    VerifiedTriangleReductionAuthority,
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)


def _fail(code: str, detail: str) -> None:
    raise CallbackWrapperCodegenError(code, detail)


def _single_u64_record_field(authority: VerifiedTriangleReductionAuthority, name: str) -> str:
    record = next((item for item in authority.callback.program.records if item.name == name), None)
    if record is None or len(record.fields) != 1:
        _fail("single_u64_record", name)
    field = record.fields[0]
    if field.value_type.kind is not TypeKind.SCALAR or field.value_type.scalar is not ScalarKind.U64:
        _fail("single_u64_record", f"{name}.{field.name}")
    return field.name


def _channel_expression(authority: VerifiedTriangleReductionAuthority, semantic_id: str) -> str:
    channel = next(
        (item for item in authority.schema.metadata_channels if item.semantic_id == semantic_id),
        None,
    )
    if channel is None:
        _fail("metadata_channel", semantic_id)
    if channel.domain is MetadataDomain.PRIMITIVE:
        index = "primitive"
    elif channel.domain is MetadataDomain.QUERY:
        index = "query"
    else:  # pragma: no cover - closed enum defense
        _fail("metadata_domain", channel.domain.value)
    if channel.scalar is ScalarKind.U64:
        base = "params.primitive_u64" if channel.domain is MetadataDomain.PRIMITIVE else "params.query_u64"
    elif channel.scalar is ScalarKind.I64:
        base = "params.primitive_i64" if channel.domain is MetadataDomain.PRIMITIVE else "params.query_i64"
    elif channel.scalar is ScalarKind.U32:
        base = "params.primitive_u32" if channel.domain is MetadataDomain.PRIMITIVE else "params.query_u32"
    else:
        _fail("metadata_scalar", channel.scalar.value)
    return f"{base}[{index}]"


def generate_trusted_optix_triangle_reduction_wrapper_v1(
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
) -> GeneratedOptixWrapper:
    """Generate the exact four-role any-hit reduction wrapper."""

    fresh = verify_triangle_reduction_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority:
        _fail("authority_reverification", "live reduction authority changed")
    expected_abi = compile_triangle_reduction_abi(
        fresh, any_hit_proof_authority=any_hit_proof_authority)
    if abi != expected_abi:
        _fail("abi_binding", "exact successor ABI is required")
    expected_contract = compile_triangle_reduction_contract(
        fresh, abi_sha256=abi.abi_sha256)
    if contract != expected_contract or contract.executable:
        _fail("contract_binding", "exact non-executable M1 contract is required")

    roles = {item.role: item for item in abi.roles}
    # This tuple is part of the executable identity.  A set here made both the
    # generated prototype order and ``role_symbols`` depend on PYTHONHASHSEED,
    # so equal semantic inputs could acquire different wrapper/cache digests.
    required = (
        CallbackRole.MAKE_RAY,
        CallbackRole.ANY_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    )
    if set(roles) != set(required):
        _fail(
            "role_set",
            repr(sorted(item.value for item in set(roles) ^ set(required))),
        )

    manifest = fresh.callback.program.manifest
    payload_field = _single_u64_record_field(fresh, manifest.payload_record)
    output_field = _single_u64_record_field(fresh, manifest.output_record)
    prototypes = "\n".join(_prototype(roles[role]) for role in required)

    channel_inputs: dict[str, str] = {}
    for binding in fresh.schema.metadata_bindings:
        function = fresh.callback.program.function_for_role(binding.role)
        argument = function.arguments[binding.argument_index]
        expression = _channel_expression(fresh, binding.semantic_id)
        channel = next(
            item for item in fresh.schema.metadata_channels
            if item.semantic_id == binding.semantic_id)
        length = "params.primitive_count" if channel.domain is MetadataDomain.PRIMITIVE else "params.query_count"
        channel_inputs[f"in.{argument.name}.columns"] = expression.rsplit("[", 1)[0]
        channel_inputs[f"in.{argument.name}.length"] = f"(unsigned long long){length}"

    keyed = fresh.schema.reducer.algebra is ReducerAlgebra.CHECKED_KEYED_I64_SUM
    # Exact-IR guarded whole-protocol specialization for the closed standard
    # count callback.  The generic diagnostic route remains below.  This is a
    # standard-library protocol intrinsic, not an application/workload check:
    # every app using this sealed callback IR and either checked U64 reducer
    # receives the same lowering.
    count_intrinsic = (
        fresh.callback.ir_sha256
        == "fedb71e837dedce85608e94e9f75a2fa9bb702077a8bb9a2ddc6ebaa4258adc3"
        and fresh.schema.reducer.algebra in {
            ReducerAlgebra.CHECKED_U64_SUM,
            ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
        }
    )
    if keyed:
        stable = _channel_expression(fresh, "primitive.stable_id")
        signed = _channel_expression(fresh, "primitive.signed_value")
        include = _channel_expression(fresh, "primitive.include")
        event_block = f"""
        const unsigned long long slot = atomicAdd(params.event_count, 1ull);
        if (slot >= params.event_capacity) {{
            v4_first_error(query, 0xffff2005u, 3u, 3u, query, 0u,
                           ah_out_effect_tag, 0u);
            optixTerminateRay(); return;
        }}
        params.event_query[slot] = query;
        params.event_primitive[slot] = primitive;
        params.event_stable_id[slot] = {stable};
        params.event_signed_value[slot] = {signed};
        params.event_include[slot] = {include};
"""
    else:
        event_block = ""

    fast_raygen = ""
    fast_any_hit = ""
    fast_miss = ""
    if count_intrinsic:
        fast_raygen = r'''
    if (params.fast_control != nullptr) {
        unsigned int payload_lo = 0u;
        unsigned int payload_hi = 0u;
        optixTrace(params.traversable,
            make_float3(params.query_ox[query], params.query_oy[query],
                        params.query_oz[query]),
            make_float3(params.query_dx[query], params.query_dy[query],
                        params.query_dz[query]),
            0.0f, params.query_tmax[query], 0.0f,
            OptixVisibilityMask(255), OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT,
            0, 1, 0, payload_lo, payload_hi);
        if (params.fast_control->error_code != 0u) return;
        const unsigned long long final_value =
            ((unsigned long long)payload_hi << 32) | payload_lo;
        params.per_ray_u64[query] = final_value;
        const unsigned long long multiplier = params.product_multipliers != nullptr
            ? params.product_multipliers[query] : 1ull;
        if (multiplier != 0ull && final_value > ~0ull / multiplier) {
            atomicExch(&params.fast_control->overflowed, 1u);
        } else {
            const unsigned long long product = final_value * multiplier;
            const unsigned long long prior = atomicAdd(
                params.fast_product_value, product);
            if (prior > ~0ull - product)
                atomicExch(&params.fast_control->overflowed, 1u);
        }
        return;
    }
'''
        fast_any_hit = r'''
    if (params.fast_control != nullptr) {
        unsigned long long payload_u64 =
            ((unsigned long long)optixGetPayload_1() << 32) |
            optixGetPayload_0();
        if (payload_u64 == ~0ull) {
            atomicCAS(&params.fast_control->error_code, 0u, 0xffff2005u);
            optixTerminateRay(); return;
        }
        ++payload_u64;
        optixSetPayload_0((unsigned int)payload_u64);
        optixSetPayload_1((unsigned int)(payload_u64 >> 32));
        optixIgnoreIntersection();
        return;
    }
'''
        fast_miss = r'''
    if (params.fast_control != nullptr) return;
'''

    common = r'''
#include <optix_device.h>

struct V4ReductionLaunchStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4FastTriangleControl {
    unsigned int error_code, validated_row_count, overflowed, reserved;
    unsigned long long event_count, per_ray_sum;
    unsigned long long role_counters[7];
};
struct V4TriangleReductionParams {
    OptixTraversableHandle traversable;
    const float* query_ox; const float* query_oy; const float* query_oz;
    const float* query_dx; const float* query_dy; const float* query_dz;
    const float* query_tmax;
    const unsigned long long* primitive_u64; const long long* primitive_i64;
    const unsigned int* primitive_u32;
    const unsigned long long* query_u64; const long long* query_i64;
    const unsigned int* query_u32;
    unsigned int primitive_count, query_count;
    unsigned long long* per_ray_u64;
    unsigned long long event_capacity; unsigned long long* event_count;
    unsigned int* event_query; unsigned int* event_primitive;
    unsigned long long* event_stable_id; long long* event_signed_value;
    unsigned int* event_include;
    V4ReductionLaunchStatus* status; unsigned long long* role_counters;
    V4FastTriangleControl* fast_control;
    unsigned long long* fast_product_value;
    const unsigned long long* product_multipliers;
};
extern "C" { __constant__ V4TriangleReductionParams params; }

static __forceinline__ __device__ void v4_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    if (params.fast_control != nullptr) {
        atomicCAS(&params.fast_control->error_code, 0u, code);
        return;
    }
    V4ReductionLaunchStatus* record = params.status + query;
    if (atomicCAS(&record->first_error_claimed, 0u, 1u) == 0u) {
        record->error_code = code; record->stage = stage; record->role = role;
        record->launch_index = launch_index; record->error_site = site;
        record->effect_tag = effect; record->nonce_word = nonce;
    }
}
static __forceinline__ __device__ unsigned int v4_lane_id() {
    unsigned int lane;
    asm("mov.u32 %0, %laneid;" : "=r"(lane));
    return lane;
}
static __forceinline__ __device__ void v4_count_role(
        unsigned long long* counter) {
    if (params.fast_control == nullptr) {
        atomicAdd(counter, 1ull);
        return;
    }
    const unsigned int active = __activemask();
    const unsigned int leader = (unsigned int)(__ffs((int)active) - 1);
    if (v4_lane_id() == leader)
        atomicAdd(counter, (unsigned long long)__popc(active));
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
        v4_first_error(query, error_code ? error_code : 0xffff2001u,
                       stage, role, launch_index, error_site, effect_tag, nonce);
        return false;
    }
    if (params.fast_control == nullptr) {
        atomicOr(&params.status[query].invocation_mask, invocation_mask);
        v4_count_role(params.role_counters + expected_role - 1u);
    }
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
    payload_path = f"out.trace_request.payload.{payload_field}"
    finalize, fin_out = _call_block(roles[CallbackRole.FINALIZE], "fin", {
        "in.context.launch_index": q,
        f"in.payload.{payload_field}": "payload_u64",
    }, query_expression=q, failure_statement="return;")
    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_triangle_reduction() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
{fast_raygen}
    if (params.fast_control == nullptr)
        params.status[query] = {{0u,0u,0u,0u,(unsigned long long)query,0u,0u,0u,0u}};
{_indent(mr, 4)}
    if ({mr_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_first_error(query, 0xffff2002u, 0u, 0u, query, 0u,
                       {mr_out['out.effect_tag']}, 0u); return;
    }}
    unsigned long long payload_u64 = {mr_out[payload_path]};
    unsigned int payload_lo = (unsigned int)payload_u64;
    unsigned int payload_hi = (unsigned int)(payload_u64 >> 32);
    optixTrace(params.traversable,
        make_float3({mr_out['out.trace_request.origin.x']}, {mr_out['out.trace_request.origin.y']}, {mr_out['out.trace_request.origin.z']}),
        make_float3({mr_out['out.trace_request.direction.x']}, {mr_out['out.trace_request.direction.y']}, {mr_out['out.trace_request.direction.z']}),
        {mr_out['out.trace_request.tmin']}, {mr_out['out.trace_request.tmax']}, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT,
        0, 1, 0, payload_lo, payload_hi);
    if (params.fast_control != nullptr) {{
        if (params.fast_control->error_code != 0u) return;
    }} else if (params.status[query].first_error_claimed != 0u) return;
    payload_u64 = ((unsigned long long)payload_hi << 32) | payload_lo;
{_indent(finalize, 4)}
    if ({fin_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_first_error(query, 0xffff2003u, 0u, 0u, query, 0u,
                       {fin_out['out.effect_tag']}, 0u); return;
    }}
    const unsigned long long final_value =
        {fin_out[f'out.output.value.{output_field}']};
    params.per_ray_u64[query] = final_value;
    if (params.fast_control != nullptr) {{
        const unsigned long long multiplier = params.product_multipliers != nullptr
            ? params.product_multipliers[query] : 1ull;
        if (multiplier != 0ull && final_value > ~0ull / multiplier) {{
            atomicExch(&params.fast_control->overflowed, 1u);
        }} else {{
            const unsigned long long product = final_value * multiplier;
            const unsigned long long prior_product = atomicAdd(
                params.fast_product_value, product);
            if (prior_product > ~0ull - product)
                atomicExch(&params.fast_control->overflowed, 1u);
        }}
    }}
}}
'''

    hit_inputs = {
        "in.context.launch_index": q,
        "in.hit.t": "optixGetRayTmax()",
        "in.hit.primitive_index": "primitive",
        "in.hit.hit_kind": "optixGetHitKind()",
        "in.hit.barycentrics.x": "bary.x",
        "in.hit.barycentrics.y": "bary.y",
        f"in.payload.{payload_field}": "payload_u64",
        **channel_inputs,
    }
    ah, ah_out = _call_block(
        roles[CallbackRole.ANY_HIT], "ah", hit_inputs,
        query_expression=q,
        failure_statement="optixTerminateRay(); return;")
    accept_tag = _effect_tag(roles[CallbackRole.ANY_HIT], EffectKind.ACCEPT_CONTINUE)
    ignore_tags = {
        item.kind: _effect_tag(roles[CallbackRole.ANY_HIT], item.kind)
        for item in roles[CallbackRole.ANY_HIT].effects
        if item.kind is EffectKind.IGNORE
    }
    ignore_branch = ""
    if EffectKind.IGNORE in ignore_tags:
        ignore_branch = f''' else if (ah_out_effect_tag == {ignore_tags[EffectKind.IGNORE]}u) {{
        payload_u64 = {ah_out[f'out.ignore.payload.{payload_field}']};
    }}'''
    any_hit = f'''
extern "C" __global__ void __anyhit__rtdl_v4_triangle_reduction() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) {{
        v4_first_error(query, 0xffff2004u, 0u, 0u, query, 0u, 0u, 0u);
        optixTerminateRay(); return;
    }}
{fast_any_hit}
    const unsigned int primitive = optixGetPrimitiveIndex();
    if (primitive >= params.primitive_count) {{
        v4_first_error(query, 0xffff2004u, 0u, 0u, query, 0u, 0u, 0u);
        optixTerminateRay(); return;
    }}
    const float2 bary = optixGetTriangleBarycentrics();
    unsigned long long payload_u64 =
        ((unsigned long long)optixGetPayload_1() << 32) | optixGetPayload_0();
{_indent(ah, 4)}
    if (ah_out_effect_tag == {accept_tag}u) {{
        payload_u64 = {ah_out[f'out.accept_continue.payload.{payload_field}']};
{_indent(event_block.rstrip(), 8)}
    }}{ignore_branch} else {{
        v4_first_error(query, 0xffff2006u, 0u, 0u, query, 0u,
                       ah_out_effect_tag, 0u);
        optixTerminateRay(); return;
    }}
    optixSetPayload_0((unsigned int)payload_u64);
    optixSetPayload_1((unsigned int)(payload_u64 >> 32));
    // ACCEPT_CONTINUE is a logical accepted event.  Physical intersection is
    // ignored so traversal cannot shrink tmax and omit later all-hit events.
    optixIgnoreIntersection();
}}
'''

    miss, miss_out = _call_block(roles[CallbackRole.MISS], "ms", {
        "in.context.launch_index": q,
        "in.ray.origin.x": "optixGetWorldRayOrigin().x",
        "in.ray.origin.y": "optixGetWorldRayOrigin().y",
        "in.ray.origin.z": "optixGetWorldRayOrigin().z",
        "in.ray.direction.x": "optixGetWorldRayDirection().x",
        "in.ray.direction.y": "optixGetWorldRayDirection().y",
        "in.ray.direction.z": "optixGetWorldRayDirection().z",
        "in.ray.tmin": "optixGetRayTmin()",
        "in.ray.tmax": "optixGetRayTmax()",
        f"in.payload.{payload_field}": "payload_u64",
    }, query_expression=q, failure_statement="return;")
    miss_source = f'''
extern "C" __global__ void __miss__rtdl_v4_triangle_reduction() {{
    const unsigned int query = optixGetLaunchIndex().x;
{fast_miss}
    unsigned long long payload_u64 =
        ((unsigned long long)optixGetPayload_1() << 32) | optixGetPayload_0();
{_indent(miss, 4)}
    if ({miss_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
        v4_first_error(query, 0xffff2007u, 0u, 0u, query, 0u,
                       {miss_out['out.effect_tag']}, 0u); return;
    }}
    payload_u64 = {miss_out[f'out.payload.payload.{payload_field}']};
    optixSetPayload_0((unsigned int)payload_u64);
    optixSetPayload_1((unsigned int)(payload_u64 >> 32));
}}
'''
    diagnostic_source = ""
    if count_intrinsic:
        # Keep the fast entry points physically separate from the generic
        # diagnostic lowering.  Merely branching around the generic calls
        # leaves their register demand attached to the hot OptiX entry point
        # and materially reduces occupancy.  The exact IR digest above is the
        # proof obligation for this standard-protocol intrinsic.
        diagnostic_source = (
            raygen.replace(
                "__raygen__rtdl_v4_triangle_reduction",
                "__raygen__rtdl_v4_triangle_reduction_diagnostic",
                1,
            )
            + any_hit.replace(
                "__anyhit__rtdl_v4_triangle_reduction",
                "__anyhit__rtdl_v4_triangle_reduction_diagnostic",
                1,
            )
            + miss_source.replace(
                "__miss__rtdl_v4_triangle_reduction",
                "__miss__rtdl_v4_triangle_reduction_diagnostic",
                1,
            )
        )
        raygen = r'''
extern "C" __global__ void __raygen__rtdl_v4_triangle_reduction() {
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count || params.fast_control == nullptr) return;
    unsigned int payload_lo = 0u;
    unsigned int payload_hi = 0u;
    optixTrace(params.traversable,
        make_float3(params.query_ox[query], params.query_oy[query],
                    params.query_oz[query]),
        make_float3(params.query_dx[query], params.query_dy[query],
                    params.query_dz[query]),
        0.0f, params.query_tmax[query], 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE,
        0, 1, 0, payload_lo, payload_hi);
    if (params.fast_control->error_code != 0u) return;
    const unsigned long long final_value =
        ((unsigned long long)payload_hi << 32) | payload_lo;
    params.per_ray_u64[query] = final_value;
    const unsigned long long multiplier = params.product_multipliers != nullptr
        ? params.product_multipliers[query] : 1ull;
    if (multiplier != 0ull && final_value > ~0ull / multiplier) {
        atomicExch(&params.fast_control->overflowed, 1u);
        return;
    }
    const unsigned long long product = final_value * multiplier;
    const unsigned long long prior = atomicAdd(
        params.fast_product_value, product);
    if (prior > ~0ull - product)
        atomicExch(&params.fast_control->overflowed, 1u);
}
'''
        any_hit = r'''
extern "C" __global__ void __anyhit__rtdl_v4_triangle_reduction() {
    unsigned long long payload_u64 =
        ((unsigned long long)optixGetPayload_1() << 32) |
        optixGetPayload_0();
    if (payload_u64 == ~0ull) {
        atomicCAS(&params.fast_control->error_code, 0u, 0xffff2005u);
        optixTerminateRay(); return;
    }
    ++payload_u64;
    optixSetPayload_0((unsigned int)payload_u64);
    optixSetPayload_1((unsigned int)(payload_u64 >> 32));
    optixIgnoreIntersection();
}
'''
        miss_source = r'''
extern "C" __global__ void __miss__rtdl_v4_triangle_reduction() {}
'''
    source = (
        common + "\n" + prototypes + "\n" + raygen + any_hit + miss_source
        + diagnostic_source
    )
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_trusted_triangle_reduction_wrapper.v1",
        physical_template=contract.template_id,
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_abi_sha256=abi.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple((role.value, roles[role].symbol) for role in required),
        linked_role_symbols=True,
    )


__all__ = ["generate_trusted_optix_triangle_reduction_wrapper_v1"]
