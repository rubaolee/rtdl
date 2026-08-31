"""Hand-written OptiX leaf controls for the Goal5779 code-quality audit.

This is evaluation code, not a production callback/provider API.  It emits
three exact C++/CUDA leaf functions with the *same verified ABI* as their V4
counterparts.  A controlled comparator replaces exactly one generated leaf in
an otherwise byte-identical wrapper/leaf set.  Consequently a later device
measurement can attribute a difference to leaf code generation rather than a
different GAS, ray layout, wrapper, output contract, or application route.

The controls are deliberately finite and closed.  They do not accept source,
PTX, callables, application names, or effect implementations from a caller.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Iterable

from rtdsl.v4_callback_abi import AbiField, RoleAbi
from rtdsl.v4_callback_ir import CallbackRole, EffectKind
from rtdsl.v4_callback_numba_codegen import audit_ptx
from rtdsl.v4_callback_poc import DeviceFunctionArtifact
from rtdsl.v4_triangle_optix_compiler import _compile_nvrtc


@dataclass(frozen=True)
class HandwrittenLeafControl:
    family_id: str
    role: CallbackRole
    semantic_contract: str
    source_provenance: str
    source: str
    source_sha256: str


_SCALAR_C = {
    "bool": "unsigned char",
    "i32": "int",
    "u32": "unsigned int",
    "i64": "long long",
    "u64": "unsigned long long",
    "f32": "float",
    "f64": "double",
}


def _ctype(field: AbiField) -> str:
    scalar = field.scalar
    if scalar.startswith("device_ptr<") and scalar.endswith(">"):
        return "const " + _SCALAR_C[scalar[11:-1]] + "*"
    if scalar.startswith("ptr<") and scalar.endswith(">"):
        return _SCALAR_C[scalar[4:-1]] + "*"
    base = _SCALAR_C[scalar]
    return base + "*" if field.direction == "out" else base


def _identifier(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", path)


def _output_fields(role: RoleAbi) -> tuple[AbiField, ...]:
    fields = {
        "out.effect_tag": AbiField(
            "out.effect_tag", "u32", "out", "effect_tag", True
        )
    }
    for variant in role.effects:
        for field in variant.fields:
            previous = fields.setdefault(field.path, field)
            if previous != field:
                raise ValueError(f"conflicting output field: {field.path}")
    output_paths = role.parameter_order[len(role.inputs) + len(role.status):]
    if set(output_paths) != set(fields):
        raise ValueError(f"output parameter order drift: {role.role.value}")
    return tuple(fields[path] for path in output_paths)


def _fields(role: RoleAbi) -> tuple[AbiField, ...]:
    return tuple(role.inputs) + tuple(role.status) + _output_fields(role)


def _name_map(role: RoleAbi) -> dict[str, str]:
    names = {field.path: _identifier(field.path) for field in _fields(role)}
    if len(set(names.values())) != len(names):
        raise ValueError(f"C identifier collision: {role.role.value}")
    return names


def _prototype(role: RoleAbi) -> tuple[str, dict[str, str]]:
    names = _name_map(role)
    parameters = ", ".join(
        f"{_ctype(field)} {names[field.path]}" for field in _fields(role)
    )
    return (
        f'extern "C" __device__ unsigned long long '
        f"{role.symbol}({parameters})",
        names,
    )


def _effect_tag(role: RoleAbi, kind: EffectKind) -> int:
    matches = [item.tag for item in role.effects if item.kind is kind]
    if len(matches) != 1:
        raise ValueError(f"effect absent or ambiguous: {role.role.value}:{kind.value}")
    return int(matches[0])


def _success_status(role: RoleAbi, names: dict[str, str], effect: str) -> str:
    launch = names["in.context.launch_index"]
    return "\n".join((
        f"*{names['status.ok']} = 1u;",
        f"*{names['status.error_code']} = 0u;",
        f"*{names['status.stage']} = {role.stage_tag}u;",
        f"*{names['status.role']} = {role.role_tag}u;",
        f"*{names['status.launch_index']} = {launch};",
        f"*{names['status.error_site']} = 0u;",
        f"*{names['status.effect_tag']} = {effect};",
        f"*{names['status.nonce_word']} = {role.nonce_word}u;",
        f"*{names['status.invocation_mask']} = {1 << (role.role_tag - 1)}u;",
        f"*{names['status.first_error_claimed']} = 0u;",
        f"*{names['out.effect_tag']} = {effect};",
    ))


def _failure_status(
    role: RoleAbi,
    names: dict[str, str],
    *,
    error_code: int,
    error_site: int,
) -> str:
    launch = names["in.context.launch_index"]
    return "\n".join((
        f"*{names['status.ok']} = 0u;",
        f"*{names['status.error_code']} = {error_code}u;",
        f"*{names['status.stage']} = {role.stage_tag}u;",
        f"*{names['status.role']} = {role.role_tag}u;",
        f"*{names['status.launch_index']} = {launch};",
        f"*{names['status.error_site']} = {error_site}u;",
        f"*{names['status.effect_tag']} = 0u;",
        f"*{names['status.nonce_word']} = {role.nonce_word}u;",
        f"*{names['status.invocation_mask']} = {1 << (role.role_tag - 1)}u;",
        f"*{names['status.first_error_claimed']} = 1u;",
        f"*{names['out.effect_tag']} = 0u;",
        "return 0ull;",
    ))


def _finite_guard(
    role: RoleAbi,
    names: dict[str, str],
    paths: Iterable[str],
) -> str:
    # Avoid host libc headers in NVRTC JIT mode.  Both infinities exceed the
    # finite float32 maximum and NaN makes both ordered comparisons false.
    condition = " || ".join(
        f"!({names[path]} <= 3.402823466e+38F && "
        f"{names[path]} >= -3.402823466e+38F)"
        for path in paths
    )
    return (
        f"if ({condition}) {{\n"
        + _indent(_failure_status(role, names, error_code=2, error_site=1), 4)
        + "\n}"
    )


def _indent(text: str, width: int) -> str:
    prefix = " " * width
    return "\n".join(prefix + line if line else line for line in text.splitlines())


def _control(
    *,
    family_id: str,
    role: RoleAbi,
    semantic_contract: str,
    source_provenance: str,
    body: str,
) -> HandwrittenLeafControl:
    prototype, _ = _prototype(role)
    source = prototype + " {\n" + _indent(body, 4) + "\n}\n"
    return HandwrittenLeafControl(
        family_id=family_id,
        role=role.role,
        semantic_contract=semantic_contract,
        source_provenance=source_provenance,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
    )


def triangle_count_any_hit_control(role: RoleAbi) -> HandwrittenLeafControl:
    if role.role is not CallbackRole.ANY_HIT:
        raise ValueError("triangle control requires any_hit ABI")
    names = _name_map(role)
    effect = _effect_tag(role, EffectKind.ACCEPT_CONTINUE)
    count = names["in.payload.count"]
    output = names["out.accept_continue.payload.count"]
    body = f"""
if ({count} == 0xffffffffffffffffull) {{
{_indent(_failure_status(role, names, error_code=4, error_site=1), 4)}
}}
{_success_status(role, names, str(effect) + 'u')}
*{output} = {count} + 1ull;
return 0ull;""".strip()
    return _control(
        family_id="TRIANGLE_ANY_HIT_U64_COUNT",
        role=role,
        semantic_contract="each accepted built-in-triangle any-hit increments one u64 per-ray count with checked overflow and accept-continue delivery",
        source_provenance=(
            "independently hand-authored direct-OptiX control implementing the "
            "frozen built-in-triangle hit-count contract; the historical direct "
            "family is pinned in rtdl_optix_core.cpp (kRayHitCount3DKernelSrc) "
            "and rtdl_optix_workloads.cpp; this is not a byte-copy claim"),
        body=body,
    )


def box_closed_overlap_intersection_control(role: RoleAbi) -> HandwrittenLeafControl:
    if role.role is not CallbackRole.INTERSECTION:
        raise ValueError("box control requires intersection ABI")
    n = _name_map(role)
    hit = _effect_tag(role, EffectKind.HIT)
    no_hit = _effect_tag(role, EffectKind.NO_HIT)
    floats = tuple(field.path for field in role.inputs if field.scalar == "f32")
    body = f"""
{_finite_guard(role, n, floats)}
const float source_x1 = {n['in.ray.origin.x']} + {n['in.ray.direction.x']};
const float source_y1 = {n['in.ray.origin.y']} + {n['in.ray.direction.y']};
const float source_min_x = source_x1 < {n['in.ray.origin.x']} ? source_x1 : {n['in.ray.origin.x']};
const float source_max_x = source_x1 < {n['in.ray.origin.x']} ? {n['in.ray.origin.x']} : source_x1;
const float source_min_y = source_y1 < {n['in.ray.origin.y']} ? source_y1 : {n['in.ray.origin.y']};
const float source_max_y = source_y1 < {n['in.ray.origin.y']} ? {n['in.ray.origin.y']} : source_y1;
const bool overlap =
    {n['in.primitive.lower.x']} <= source_max_x &&
    {n['in.primitive.upper.x']} >= source_min_x &&
    {n['in.primitive.lower.y']} <= source_max_y &&
    {n['in.primitive.upper.y']} >= source_min_y;
if (overlap) {{
{_indent(_success_status(role, n, str(hit) + 'u'), 4)}
    *{n['out.hit.t']} = 0.0f;
    *{n['out.hit.hit_kind']} = 0u;
    *{n['out.hit.attributes.0']} = {n['in.primitive.item_id']};
}} else {{
{_indent(_success_status(role, n, str(no_hit) + 'u'), 4)}
}}
return 0ull;""".strip()
    return _control(
        family_id="CUSTOM_AABB_CLOSED_BOX_INTERSECTION",
        role=role,
        semantic_contract="closed two-dimensional AABB overlap encoded by the exact diagonal ray and reported as a custom intersection",
        source_provenance=(
            "independently hand-authored direct-OptiX control implementing the "
            "frozen closed-box intersection contract in the historical custom-AABB "
            "programming style; this is not a claim that an identical prior V2 "
            "leaf body existed"),
        body=body,
    )


def spatial_sphere_intersection_control(role: RoleAbi) -> HandwrittenLeafControl:
    if role.role is not CallbackRole.INTERSECTION:
        raise ValueError("spatial control requires intersection ABI")
    n = _name_map(role)
    hit = _effect_tag(role, EffectKind.HIT)
    no_hit = _effect_tag(role, EffectKind.NO_HIT)
    floats = tuple(field.path for field in role.inputs if field.scalar == "f32")
    body = f"""
{_finite_guard(role, n, floats)}
const float cx = ({n['in.primitive.lower.x']} + {n['in.primitive.upper.x']}) * 0.5f;
const float cy = ({n['in.primitive.lower.y']} + {n['in.primitive.upper.y']}) * 0.5f;
const float cz = ({n['in.primitive.lower.z']} + {n['in.primitive.upper.z']}) * 0.5f;
const float radius = ({n['in.primitive.upper.x']} - {n['in.primitive.lower.x']}) * 0.5f;
const float ox = {n['in.ray.origin.x']} - cx;
const float oy = {n['in.ray.origin.y']} - cy;
const float oz = {n['in.ray.origin.z']} - cz;
const float b = ox * {n['in.ray.direction.x']} + oy * {n['in.ray.direction.y']} + oz * {n['in.ray.direction.z']};
const float c = ox * ox + oy * oy + oz * oz - radius * radius;
const float discriminant = b * b - c;
bool accepted = false;
float selected_t = 0.0f;
if (discriminant >= 0.0f) {{
    float root;
    asm("sqrt.rn.f32 %0, %1;" : "=f"(root) : "f"(discriminant));
    const float near_t = -b - root;
    const float far_t = -b + root;
    selected_t = near_t >= {n['in.ray.tmin']} ? near_t : far_t;
    accepted = selected_t >= {n['in.ray.tmin']} && selected_t <= {n['in.ray.tmax']};
}}
if (accepted) {{
{_indent(_success_status(role, n, str(hit) + 'u'), 4)}
    *{n['out.hit.t']} = selected_t;
    *{n['out.hit.hit_kind']} = 0u;
    *{n['out.hit.attributes.0']} = {n['in.primitive.item_id']};
}} else {{
{_indent(_success_status(role, n, str(no_hit) + 'u'), 4)}
}}
return 0ull;""".strip()
    return _control(
        family_id="CUSTOM_AABB_ANALYTIC_SPHERE_INTERSECTION",
        role=role,
        semantic_contract="analytic sphere intersection over custom AABB primitives with the first valid root in the closed ray interval",
        source_provenance=(
            "independently hand-authored direct-OptiX control implementing the "
            "frozen analytic-sphere intersection contract in the historical "
            "fixed-radius custom-AABB programming style; this is not a claim that "
            "an identical prior V2 leaf body existed"),
        body=body,
    )


def compile_handwritten_control(
    control: HandwrittenLeafControl,
    role: RoleAbi,
    *,
    compiler_options: tuple[str, ...],
    compute_capability: tuple[int, int],
    callback_ir_sha256: str,
) -> tuple[DeviceFunctionArtifact, str]:
    """Compile one closed hand-written control with the wrapper's exact target."""

    if control.role is not role.role or role.symbol not in control.source:
        raise ValueError("control/ABI binding drift")
    ptx, log = _compile_nvrtc(control.source, compiler_options)
    audit = audit_ptx(
        ptx,
        abi_name=role.symbol,
        accepted_isa=("8.0", "9.0"),
        allowed_external_symbols=frozenset(),
    )
    # The trusted composer strips one unreferenced Numba environment per leaf.
    # Hand-written NVRTC code has no such environment; add a unique inert
    # declaration so the *same* composer and wrapper are used on both sides.
    environment = (
        ".common .global .align 8 .u64 "
        f"_ZN08NumbaEnv_goal5779_{control.family_id};\n"
    )
    lines = ptx.splitlines(keepends=True)
    address = next(
        index for index, line in enumerate(lines)
        if line.lstrip().startswith(".address_size")
    )
    lines.insert(address + 1, environment)
    composed_ptx = "".join(lines)
    artifact = DeviceFunctionArtifact(
        schema="rtdl.goal5779.handwritten_device_function_control.v1",
        role=role.role.value,
        abi_name=role.symbol,
        compute_capability=tuple(compute_capability),
        numeric_mode="strict_handwritten_control",
        generated_source_sha256=control.source_sha256,
        ir_sha256=callback_ir_sha256,
        ptx=composed_ptx,
        ptx_sha256=hashlib.sha256(composed_ptx.encode("utf-8")).hexdigest(),
        ptx_version=str(audit["ptx_version"]),
        ptx_target=str(audit["ptx_target"]),
        external_symbols=tuple(audit["external_symbols"]),
        numba_version="not_applicable_handwritten_nvrtc_control",
        python_version="not_applicable_handwritten_nvrtc_control",
        nonce_word=role.nonce_word,
        compiler_function_count=1,
    )
    return artifact, log


__all__ = [
    "HandwrittenLeafControl",
    "box_closed_overlap_intersection_control",
    "compile_handwritten_control",
    "spatial_sphere_intersection_control",
    "triangle_count_any_hit_control",
]
