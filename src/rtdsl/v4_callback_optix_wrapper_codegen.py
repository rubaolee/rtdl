"""Trusted OptiX wrapper generation for the first formal V4 physical template.

The wrapper is compiler output.  It owns OptiX entry points, marshals the
canonical Callback ABI, and is the only component allowed to invoke verified
Numba leaves from OptiX programs.  The initial reviewed template is a generic
analytic-sphere nearest-search shape, selected by semantic/geometry contracts,
never by an application name or IR digest.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

from .v4_callback_abi import (
    AnyHitProofAuthority,
    AbiField,
    CallbackAbiError,
    CompiledCallbackAbi,
    RoleAbi,
    verify_compiled_callback_abi,
)
from .v4_callback_ir import (
    AnyHitDeliveryContract,
    CallbackRole,
    EffectKind,
    ReturnEffectStatement,
    VerifiedCallbackProgram,
)


class CallbackWrapperCodegenError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"V4 wrapper codegen failed: {code}: {detail}")


@dataclass(frozen=True)
class GeneratedOptixWrapper:
    schema: str
    physical_template: str
    callback_ir_sha256: str
    callback_abi_sha256: str
    source: str
    source_sha256: str
    role_symbols: tuple[tuple[str, str], ...]
    linked_role_symbols: bool = True


_SCALAR_C = {
    "bool": "unsigned char",
    "i32": "int",
    "u32": "unsigned int",
    "i64": "long long",
    "u64": "unsigned long long",
    "f32": "float",
    "f64": "double",
}


def _fail(code: str, detail: str) -> None:
    raise CallbackWrapperCodegenError(code, detail)


def _ctype(scalar: str, direction: str) -> str:
    if scalar.startswith("device_ptr<") and scalar.endswith(">"):
        return "const " + _SCALAR_C[scalar[11:-1]] + "*"
    if scalar.startswith("ptr<") and scalar.endswith(">"):
        return _SCALAR_C[scalar[4:-1]] + "*"
    try:
        base = _SCALAR_C[scalar]
        return base + "*" if direction == "out" else base
    except KeyError:
        _fail("scalar", scalar)
        raise AssertionError


def _prototype(role: RoleAbi) -> str:
    fields = list(role.inputs) + list(role.status) + _role_outputs(role)
    params = ", ".join(_ctype(field.scalar, field.direction) for field in fields)
    # Numba 0.65.1's C ABI materializes Python None as an ignored b64 slot.
    return f'extern "C" __device__ unsigned long long {role.symbol}({params});'


def _name(prefix: str, path: str) -> str:
    return prefix + "_" + "".join(ch if ch.isalnum() else "_" for ch in path)


def _role_outputs(role: RoleAbi) -> list[AbiField]:
    by_path = {
        "out.effect_tag": AbiField(
            "out.effect_tag", "u32", "out", "effect_tag", True
        )
    }
    for variant in role.effects:
        for field in variant.fields:
            existing = by_path.setdefault(field.path, field)
            if existing != field:
                _fail("effect_field_conflict", f"{role.role.value}:{field.path}")
    output_paths = role.parameter_order[len(role.inputs) + len(role.status):]
    if set(output_paths) != set(by_path):
        _fail("parameter_order", role.role.value)
    return [by_path[path] for path in output_paths]


def _call_block(
    role: RoleAbi,
    prefix: str,
    inputs: Mapping[str, str],
    *,
    query_expression: str,
    failure_statement: str,
) -> tuple[str, dict[str, str]]:
    if set(inputs) != {field.path for field in role.inputs}:
        _fail("input_shape", f"{role.role.value}:{sorted(set(inputs) ^ {f.path for f in role.inputs})}")
    declarations: list[str] = []
    arguments: list[str] = [inputs[field.path] for field in role.inputs]
    status_names: dict[str, str] = {}
    for field in role.status:
        local = _name(prefix, field.path)
        status_names[field.path] = local
        declarations.append(f"{_SCALAR_C[field.scalar]} {local} = 0;")
        arguments.append("&" + local)
    output_names: dict[str, str] = {}
    for field in _role_outputs(role):
        local = _name(prefix, field.path)
        output_names[field.path] = local
        declarations.append(f"{_SCALAR_C[field.scalar]} {local} = 0;")
        arguments.append("&" + local)
    text = "\n".join(declarations)
    text += f"\n(void){role.symbol}({', '.join(arguments)});"
    text += (
        "\nif (!v4_commit_leaf_status("
        f"{query_expression}, {status_names['status.ok']}, "
        f"{status_names['status.error_code']}, {status_names['status.stage']}, "
        f"{status_names['status.role']}, {status_names['status.launch_index']}, "
        f"{status_names['status.error_site']}, {status_names['status.effect_tag']}, "
        f"{status_names['status.nonce_word']}, {status_names['status.invocation_mask']}, "
        f"{status_names['status.first_error_claimed']}, {role.stage_tag}u, "
        f"{role.role_tag}u, {role.nonce_word}u)) {{ {failure_statement} }}"
    )
    return text, output_names


def _effect_tag(role: RoleAbi, kind: EffectKind) -> int:
    variant = next((item for item in role.effects if item.kind is kind), None)
    if variant is None:
        _fail("effect", f"{role.role.value}:{kind.value}")
    return variant.tag


def _verify_cross_entry_composition(verified: VerifiedCallbackProgram) -> None:
    """Reject role-local proofs that are not sound after OptiX composition."""

    delivery = verified.program.manifest.any_hit_delivery
    if delivery is not AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL:
        return
    closest = verified.program.function_for_role(CallbackRole.CLOSEST_HIT)
    # The initial Goal5750 specimen let any-hit compute a canonical minimum,
    # then closest-hit overwrote it with OptiX's unspecified representative of
    # an equal-distance tie.  Under this delivery contract the only currently
    # admitted closest-hit form is exact identity on the proven payload.  More
    # general confluence needs its own proof authority; it is not inferred.
    if len(closest.body) != 1 or not isinstance(closest.body[0], ReturnEffectStatement):
        _fail("closest_hit_confluence", "requires identity payload under canonical any-hit")
    effect = closest.body[0].effect
    payload = effect.field("payload")
    if (effect.kind is not EffectKind.PAYLOAD or payload is None or
            payload.opcode != "local" or payload.attribute("name") != "payload"):
        _fail("closest_hit_confluence", "closest-hit may not overwrite canonical payload")


def generate_trusted_optix_wrapper_v1(
    verified: VerifiedCallbackProgram,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority: AnyHitProofAuthority,
) -> GeneratedOptixWrapper:
    try:
        canonical = verify_compiled_callback_abi(
            abi, verified, any_hit_proof_authority=any_hit_proof_authority
        )
    except CallbackAbiError as exc:
        raise CallbackWrapperCodegenError(
            "abi_admission", f"{exc.code}@{exc.path}: {exc.message}"
        ) from exc
    _verify_cross_entry_composition(verified)
    geometry = verified.program.manifest.geometry
    if geometry is None or geometry.contract_name != "tested_analytic_sphere_v1":
        _fail("physical_template", "requires tested_analytic_sphere_v1")
    roles = {item.role: item for item in canonical.roles}
    if set(roles) != set(CallbackRole):
        _fail("role_set", repr(sorted(item.value for item in set(CallbackRole) - set(roles))))

    expected_inputs = {
        CallbackRole.BOUNDS: {
            "in.context.launch_index", "in.primitive.center.x", "in.primitive.center.y",
            "in.primitive.center.z", "in.primitive.radius", "in.primitive.item_id",
        },
        CallbackRole.MAKE_RAY: {
            "in.context.launch_index", "in.launch_id", "in.queries.columns.origin.x",
            "in.queries.columns.origin.y", "in.queries.columns.origin.z",
            "in.queries.columns.tmax", "in.queries.length",
        },
        CallbackRole.INTERSECTION: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax",
            "in.primitive.center.x", "in.primitive.center.y", "in.primitive.center.z",
            "in.primitive.radius", "in.primitive.item_id",
        },
        CallbackRole.ANY_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.hit_kind",
            "in.payload.best_t", "in.payload.best_id",
        },
        CallbackRole.CLOSEST_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.hit_kind",
            "in.payload.best_t", "in.payload.best_id",
        },
        CallbackRole.MISS: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax",
            "in.payload.best_t", "in.payload.best_id",
        },
        CallbackRole.FINALIZE: {
            "in.context.launch_index", "in.payload.best_t", "in.payload.best_id",
        },
    }
    for role, expected in expected_inputs.items():
        observed = {field.path for field in roles[role].inputs}
        if observed != expected:
            _fail("template_input_shape", f"{role.value}:{sorted(observed ^ expected)}")

    prototypes = "\n".join(_prototype(roles[role]) for role in CallbackRole)
    common = r'''
#include <optix_device.h>

struct V4Sphere { float cx, cy, cz, radius; unsigned int item_id; };
struct V4LaunchStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4Params {
    OptixTraversableHandle traversable;
    const V4Sphere* spheres;
    const float* query_x; const float* query_y; const float* query_z;
    const float* query_tmax;
    unsigned int sphere_count, query_count;
    unsigned int* output_ids; float* output_distance;
    V4LaunchStatus* status; unsigned long long* role_counters;
};
extern "C" { __constant__ V4Params params; }

static __forceinline__ __device__ void v4_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    V4LaunchStatus* record = params.status + query;
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
        v4_first_error(query, error_code ? error_code : 0xffff0001u,
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
        "in.context.launch_index": q, "in.launch_id": q,
        "in.queries.columns.origin.x": "params.query_x",
        "in.queries.columns.origin.y": "params.query_y",
        "in.queries.columns.origin.z": "params.query_z",
        "in.queries.columns.tmax": "params.query_tmax",
        "in.queries.length": "(unsigned long long)params.query_count",
    }, query_expression=q, failure_statement="return;")
    fin, fin_out = _call_block(roles[CallbackRole.FINALIZE], "fin", {
        "in.context.launch_index": q,
        "in.payload.best_t": "__uint_as_float(payload_t)",
        "in.payload.best_id": "payload_id",
    }, query_expression=q, failure_statement="return;")
    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_formal() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    params.status[query] = {{0u, 0u, 0u, 0u, (unsigned long long)query, 0u, 0u, 0u, 0u}};
{_indent(mr, 4)}
    if ({mr_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_first_error(query, 0xffff0002u, 0u, 0u, query, 0u, {mr_out['out.effect_tag']}, 0u); return;
    }}
    unsigned int payload_t = __float_as_uint({mr_out['out.trace_request.payload.best_t']});
    unsigned int payload_id = {mr_out['out.trace_request.payload.best_id']};
    unsigned int payload_ox = __float_as_uint({mr_out['out.trace_request.origin.x']});
    unsigned int payload_oy = __float_as_uint({mr_out['out.trace_request.origin.y']});
    unsigned int payload_oz = __float_as_uint({mr_out['out.trace_request.origin.z']});
    unsigned int payload_dx = __float_as_uint({mr_out['out.trace_request.direction.x']});
    unsigned int payload_dy = __float_as_uint({mr_out['out.trace_request.direction.y']});
    unsigned int payload_dz = __float_as_uint({mr_out['out.trace_request.direction.z']});
    unsigned int payload_tmin = __float_as_uint({mr_out['out.trace_request.tmin']});
    unsigned int payload_tmax = __float_as_uint({mr_out['out.trace_request.tmax']});
    // These values are overwritten by finalize on every successful launch;
    // on a fail-closed launch they preserve a minimal make-ray diagnostic.
    params.output_ids[query] = payload_dx;
    params.output_distance[query] = {mr_out['out.trace_request.tmin']};
    optixTrace(params.traversable,
        make_float3({mr_out['out.trace_request.origin.x']}, {mr_out['out.trace_request.origin.y']}, {mr_out['out.trace_request.origin.z']}),
        make_float3({mr_out['out.trace_request.direction.x']}, {mr_out['out.trace_request.direction.y']}, {mr_out['out.trace_request.direction.z']}),
        {mr_out['out.trace_request.tmin']}, {mr_out['out.trace_request.tmax']}, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE, 0, 1, 0,
        payload_t, payload_id,
        payload_ox, payload_oy, payload_oz,
        payload_dx, payload_dy, payload_dz, payload_tmin, payload_tmax);
    if (params.status[query].first_error_claimed != 0u) return;
{_indent(fin, 4)}
    if ({fin_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_first_error(query, 0xffff0003u, 0u, 0u, query, 0u, {fin_out['out.effect_tag']}, 0u); return;
    }}
    params.output_ids[query] = {fin_out['out.output.value.item_id']};
    params.output_distance[query] = {fin_out['out.output.value.distance']};
}}
'''

    primitive = "params.spheres[primitive_index]"
    ray_inputs = {
        "in.context.launch_index": q,
        "in.ray.origin.x": "origin.x", "in.ray.origin.y": "origin.y", "in.ray.origin.z": "origin.z",
        "in.ray.direction.x": "direction.x", "in.ray.direction.y": "direction.y", "in.ray.direction.z": "direction.z",
        "in.ray.tmin": "optixGetRayTmin()", "in.ray.tmax": "optixGetRayTmax()",
    }
    primitive_inputs = {
        "in.primitive.center.x": primitive + ".cx", "in.primitive.center.y": primitive + ".cy",
        "in.primitive.center.z": primitive + ".cz", "in.primitive.radius": primitive + ".radius",
        "in.primitive.item_id": primitive + ".item_id",
    }
    bnd, bnd_out = _call_block(roles[CallbackRole.BOUNDS], "bnd", {
        "in.context.launch_index": q, **primitive_inputs,
    }, query_expression=q, failure_statement="return;")
    inter, inter_out = _call_block(roles[CallbackRole.INTERSECTION], "isect", {
        **ray_inputs, **primitive_inputs,
    }, query_expression=q, failure_statement="return;")
    intersection = f'''
extern "C" __global__ void __intersection__rtdl_v4_formal() {{
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive_index = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive_index >= params.sphere_count) {{
        v4_first_error(query, 0xffff0004u, 0u, 0u, query, 0u, 0u, 0u); return;
    }}
    const float3 origin = optixGetWorldRayOrigin();
    const float3 direction = optixGetWorldRayDirection();
{_indent(bnd, 4)}
    if ({bnd_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.BOUNDS], EffectKind.AABB)}u) {{
        v4_first_error(query, 0xffff0005u, 0u, 0u, query, 0u, {bnd_out['out.effect_tag']}, 0u); return;
    }}
    // The user bounds callback is not merely invoked for provenance.  The
    // trusted physical template independently knows the admitted sphere
    // geometry and checks that the callback describes exactly the AABB used
    // to construct the GAS.  A callback cannot silently claim different
    // bounds while traversal uses compiler-owned boxes.
    if ({bnd_out['out.aabb.lower.x']} != {primitive}.cx - {primitive}.radius ||
        {bnd_out['out.aabb.lower.y']} != {primitive}.cy - {primitive}.radius ||
        {bnd_out['out.aabb.lower.z']} != {primitive}.cz - {primitive}.radius ||
        {bnd_out['out.aabb.upper.x']} != {primitive}.cx + {primitive}.radius ||
        {bnd_out['out.aabb.upper.y']} != {primitive}.cy + {primitive}.radius ||
        {bnd_out['out.aabb.upper.z']} != {primitive}.cz + {primitive}.radius) {{
        v4_first_error(query, 0xffff000au, 0u, 0u, query, 0u,
                       {bnd_out['out.effect_tag']}, 0u); return;
    }}
{_indent(inter, 4)}
    if ({inter_out['out.effect_tag']} == {_effect_tag(roles[CallbackRole.INTERSECTION], EffectKind.NO_HIT)}u) return;
    if ({inter_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.INTERSECTION], EffectKind.HIT)}u) {{
        v4_first_error(query, 0xffff0006u, 0u, 0u, query, 0u, {inter_out['out.effect_tag']}, 0u); return;
    }}
    optixReportIntersection({inter_out['out.hit.t']}, 0u, {inter_out['out.hit.attributes.0']}, 0u);
}}
'''

    hit_common = {
        "in.context.launch_index": q,
        "in.hit.t": "optixGetRayTmax()",
        "in.hit.hit_kind": "optixGetAttribute_0()",
        "in.payload.best_t": "__uint_as_float(optixGetPayload_0())",
        "in.payload.best_id": "optixGetPayload_1()",
    }
    ah, ah_out = _call_block(roles[CallbackRole.ANY_HIT], "ah", hit_common,
                             query_expression=q, failure_statement="optixIgnoreIntersection(); return;")
    any_hit = f'''
extern "C" __global__ void __anyhit__rtdl_v4_formal() {{
    const unsigned int query = optixGetLaunchIndex().x;
{_indent(ah, 4)}
    if ({ah_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.ANY_HIT], EffectKind.ACCEPT_CONTINUE)}u) {{
        v4_first_error(query, 0xffff0007u, 0u, 0u, query, 0u, {ah_out['out.effect_tag']}, 0u); optixIgnoreIntersection(); return;
    }}
    optixSetPayload_0(__float_as_uint({ah_out['out.accept_continue.payload.best_t']}));
    optixSetPayload_1({ah_out['out.accept_continue.payload.best_id']});
}}
'''

    ch, ch_out = _call_block(roles[CallbackRole.CLOSEST_HIT], "ch", hit_common,
                             query_expression=q, failure_statement="return;")
    closest = f'''
extern "C" __global__ void __closesthit__rtdl_v4_formal() {{
    const unsigned int query = optixGetLaunchIndex().x;
{_indent(ch, 4)}
    if ({ch_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.CLOSEST_HIT], EffectKind.PAYLOAD)}u) {{
        v4_first_error(query, 0xffff0008u, 0u, 0u, query, 0u, {ch_out['out.effect_tag']}, 0u); return;
    }}
    optixSetPayload_0(__float_as_uint({ch_out['out.payload.payload.best_t']}));
    optixSetPayload_1({ch_out['out.payload.payload.best_id']});
}}
'''

    miss_inputs = {
        "in.context.launch_index": q,
        "in.ray.origin.x": "__uint_as_float(optixGetPayload_2())", "in.ray.origin.y": "__uint_as_float(optixGetPayload_3())",
        "in.ray.origin.z": "__uint_as_float(optixGetPayload_4())", "in.ray.direction.x": "__uint_as_float(optixGetPayload_5())",
        "in.ray.direction.y": "__uint_as_float(optixGetPayload_6())", "in.ray.direction.z": "__uint_as_float(optixGetPayload_7())",
        "in.ray.tmin": "__uint_as_float(optixGetPayload_8())", "in.ray.tmax": "__uint_as_float(optixGetPayload_9())",
        "in.payload.best_t": "__uint_as_float(optixGetPayload_0())", "in.payload.best_id": "optixGetPayload_1()",
    }
    ms, ms_out = _call_block(roles[CallbackRole.MISS], "ms", miss_inputs,
                             query_expression=q, failure_statement="return;")
    miss = f'''
extern "C" __global__ void __miss__rtdl_v4_formal() {{
    const unsigned int query = optixGetLaunchIndex().x;
{_indent(ms, 4)}
    if ({ms_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
        v4_first_error(query, 0xffff0009u, 0u, 0u, query, 0u, {ms_out['out.effect_tag']}, 0u); return;
    }}
    optixSetPayload_0(__float_as_uint({ms_out['out.payload.payload.best_t']}));
    optixSetPayload_1({ms_out['out.payload.payload.best_id']});
}}
'''
    source = common + "\n" + prototypes + "\n" + raygen + intersection + any_hit + closest + miss
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_trusted_optix_wrapper.v1",
        physical_template="tested_analytic_sphere_nearest_search_v1",
        callback_ir_sha256=verified.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple((role.value, roles[role].symbol) for role in CallbackRole),
    )


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.splitlines())


__all__ = [
    "CallbackWrapperCodegenError",
    "GeneratedOptixWrapper",
    "generate_trusted_optix_wrapper_v1",
]
