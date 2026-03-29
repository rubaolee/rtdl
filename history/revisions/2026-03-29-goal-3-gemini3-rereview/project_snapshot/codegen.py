from __future__ import annotations

import json
from pathlib import Path

from .ir import RayJoinPlan


def generate_optix_project(plan: RayJoinPlan, output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    metadata_path = root / "plan.json"
    device_path = root / "device_kernels.cu"
    host_path = root / "host_launcher.cpp"
    readme_path = root / "README.md"

    metadata_path.write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    device_path.write_text(_render_device(plan), encoding="utf-8")
    host_path.write_text(_render_host(plan), encoding="utf-8")
    readme_path.write_text(_render_readme(plan), encoding="utf-8")

    return {
        "metadata": metadata_path,
        "device": device_path,
        "host": host_path,
        "readme": readme_path,
    }


def _render_device(plan: RayJoinPlan) -> str:
    if plan.workload_kind == "lsi":
        return _render_lsi_device(plan)
    if plan.workload_kind == "pip":
        return _render_pip_device(plan)
    if plan.workload_kind == "overlay":
        return _render_overlay_device(plan)
    raise ValueError(f"unsupported workload kind for codegen: {plan.workload_kind}")


def _render_lsi_device(plan: RayJoinPlan) -> str:
    build_buffer = _input_buffer_name(plan.build_input)
    probe_buffer = _input_buffer_name(plan.probe_input)
    payload_comments = _render_payload_comments(plan)
    return f"""#include <optix.h>
#include <optix_device.h>
#include <math.h>
#include <stdint.h>

{_render_layout_structs(plan)}

{_render_output_struct(plan)}

struct LaunchParams {{
    OptixTraversableHandle traversable;
    const {plan.build_input.layout.name}* {build_buffer};
    const {plan.probe_input.layout.name}* {probe_buffer};
    {plan.output_record.name}* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
}};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ uint32_t rtdl_float_as_u32(float value) {{
    return __float_as_uint(value);
}}

static __forceinline__ __device__ float rtdl_u32_as_float(uint32_t value) {{
    return __uint_as_float(value);
}}

static __forceinline__ __device__ float rtdl_cross2(float2 a, float2 b) {{
    return a.x * b.y - a.y * b.x;
}}

static __forceinline__ __device__ bool rtdl_intersect_segments(
    const {plan.probe_input.layout.name}& probe,
    const {plan.build_input.layout.name}& build,
    float* hit_t,
    float* ix,
    float* iy
) {{
    const float2 p = make_float2(probe.x0, probe.y0);
    const float2 r = make_float2(probe.x1 - probe.x0, probe.y1 - probe.y0);
    const float2 q = make_float2(build.x0, build.y0);
    const float2 s = make_float2(build.x1 - build.x0, build.y1 - build.y0);
    const float2 qp = make_float2(q.x - p.x, q.y - p.y);
    const float denom = rtdl_cross2(r, s);

    if (fabsf(denom) < 1.0e-7f) {{
        return false;
    }}

    const float t = rtdl_cross2(qp, s) / denom;
    const float u = rtdl_cross2(qp, r) / denom;
    if (t < 0.0f || t > 1.0f || u < 0.0f || u > 1.0f) {{
        return false;
    }}

    *hit_t = t;
    *ix = p.x + t * r.x;
    *iy = p.y + t * r.y;
    return true;
}}

static __forceinline__ __device__ void rtdl_pack_payload(uint32_t probe_index, uint32_t build_primitive_index, float hit_t, uint32_t hit_kind) {{
    optixSetPayload_0(probe_index);
    optixSetPayload_1(build_primitive_index);
    optixSetPayload_2(rtdl_float_as_u32(hit_t));
    optixSetPayload_3(hit_kind);
}}

static __forceinline__ __device__ void rtdl_store_record(uint32_t probe_id, uint32_t build_id, float ix, float iy) {{
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {{
        return;
    }}
    {plan.output_record.name} record = {{}};
    record.left_id = probe_id;
    record.right_id = build_id;
    record.intersection_point_x = ix;
    record.intersection_point_y = iy;
    params.output_records[slot] = record;
}}

extern "C" __global__ void __raygen__rtdl_probe() {{
    const uint32_t probe_index = optixGetLaunchIndex().x;
    if (probe_index >= params.probe_count) {{
        return;
    }}

    const {plan.probe_input.layout.name} probe = params.{probe_buffer}[probe_index];
    const float3 origin = make_float3({plan.ray_spec.origin[0]}, {plan.ray_spec.origin[1]}, {plan.ray_spec.origin[2]});
    const float3 direction = make_float3({plan.ray_spec.direction[0]}, {plan.ray_spec.direction[1]}, {plan.ray_spec.direction[2]});

    unsigned int p0 = probe_index;
    unsigned int p1 = 0u;
    unsigned int p2 = rtdl_float_as_u32(-1.0f);
    unsigned int p3 = 0u;

    optixTrace(
        params.traversable,
        origin,
        direction,
        {plan.ray_spec.tmin},
        {plan.ray_spec.tmax},
        0.0f,
        OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE,
        0,
        1,
        0,
        p0,
        p1,
        p2,
        p3
    );
}}

extern "C" __global__ void __miss__rtdl_miss() {{
    // Intentionally empty for the LSI path.
}}

extern "C" __global__ void __closesthit__rtdl_refine() {{
    const uint32_t probe_index = optixGetPayload_0();
    const uint32_t build_primitive_index = optixGetPayload_1();
    const {plan.probe_input.layout.name} probe = params.{probe_buffer}[probe_index];
    const {plan.build_input.layout.name} build = params.{build_buffer}[build_primitive_index];
    float refined_hit_t = 0.0f;
    float ix = 0.0f;
    float iy = 0.0f;

    if (!rtdl_intersect_segments(probe, build, &refined_hit_t, &ix, &iy)) {{
        return;
    }}

    rtdl_store_record(probe.id, build.id, ix, iy);
}}

extern "C" __global__ void __intersection__rtdl_segments() {{
{payload_comments}
    const uint32_t primitive_index = optixGetPrimitiveIndex();
    const {plan.build_input.layout.name} build = params.{build_buffer}[primitive_index];
    const uint32_t probe_index = optixGetPayload_0();
    const {plan.probe_input.layout.name} probe = params.{probe_buffer}[probe_index];
    float hit_t = 0.0f;
    float ix = 0.0f;
    float iy = 0.0f;

    if (!rtdl_intersect_segments(probe, build, &hit_t, &ix, &iy)) {{
        return;
    }}

    rtdl_pack_payload(probe_index, primitive_index, hit_t, 1u);
    optixReportIntersection(hit_t, 0u);
}}
"""


def _render_pip_device(plan: RayJoinPlan) -> str:
    build_buffer = _input_buffer_name(plan.build_input)
    probe_buffer = _input_buffer_name(plan.probe_input)
    payload_comments = _render_payload_comments(plan)
    return f"""#include <float.h>
#include <optix.h>
#include <optix_device.h>
#include <stdint.h>

{_render_layout_structs(plan)}

{_render_output_struct(plan)}

struct LaunchParams {{
    OptixTraversableHandle traversable;
    const {plan.build_input.layout.name}* {build_buffer};
    const {plan.probe_input.layout.name}* {probe_buffer};
    {plan.output_record.name}* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
}};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ void rtdl_store_record(uint32_t point_id, uint32_t polygon_id, uint32_t contains) {{
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {{
        return;
    }}
    {plan.output_record.name} record = {{}};
    record.point_id = point_id;
    record.polygon_id = polygon_id;
    record.contains = contains;
    params.output_records[slot] = record;
}}

extern "C" __global__ void __raygen__rtdl_pip_probe() {{
    const uint32_t point_index = optixGetLaunchIndex().x;
    if (point_index >= params.probe_count) {{
        return;
    }}

    const {plan.probe_input.layout.name} probe = params.{probe_buffer}[point_index];
    const float3 origin = make_float3({plan.ray_spec.origin[0]}, {plan.ray_spec.origin[1]}, {plan.ray_spec.origin[2]});
    const float3 direction = make_float3({plan.ray_spec.direction[0]}, {plan.ray_spec.direction[1]}, {plan.ray_spec.direction[2]});

    unsigned int p0 = point_index;
    unsigned int p1 = 0u;
    unsigned int p2 = 0u;
    unsigned int p3 = 0u;

    optixTrace(
        params.traversable,
        origin,
        direction,
        {plan.ray_spec.tmin},
        {plan.ray_spec.tmax},
        0.0f,
        OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE,
        0,
        1,
        0,
        p0,
        p1,
        p2,
        p3
    );
}}

extern "C" __global__ void __miss__rtdl_miss() {{
    // Intentionally empty for the PIP path.
}}

extern "C" __global__ void __closesthit__rtdl_pip_refine() {{
    const uint32_t point_index = optixGetPayload_0();
    const uint32_t polygon_face_index = optixGetPayload_1();
    const uint32_t winding_hits = optixGetPayload_2();
    const {plan.probe_input.layout.name} point = params.{probe_buffer}[point_index];
    const {plan.build_input.layout.name} polygon = params.{build_buffer}[polygon_face_index];
    const uint32_t contains = winding_hits & 1u;

    // Current backend contract only materializes a workload-specific skeleton here.
    rtdl_store_record(point.id, polygon.id, contains);
}}

extern "C" __global__ void __intersection__rtdl_polygon_refs() {{
{payload_comments}
    // Polygon edge traversal and parity counting are deferred to a later runtime milestone.
    // This skeleton fixes the payload and launch contract for the PIP workload now.
}}
"""


def _render_overlay_device(plan: RayJoinPlan) -> str:
    build_buffer = _input_buffer_name(plan.build_input)
    probe_buffer = _input_buffer_name(plan.probe_input)
    return f"""#include <optix.h>
#include <optix_device.h>
#include <stdint.h>

{_render_layout_structs(plan)}

{_render_output_struct(plan)}

struct LaunchParams {{
    OptixTraversableHandle traversable;
    const {plan.build_input.layout.name}* {build_buffer};
    const {plan.probe_input.layout.name}* {probe_buffer};
    {plan.output_record.name}* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
}};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ void rtdl_store_record(uint32_t left_polygon_id, uint32_t right_polygon_id, uint32_t requires_lsi, uint32_t requires_pip) {{
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {{
        return;
    }}
    {plan.output_record.name} record = {{}};
    record.left_polygon_id = left_polygon_id;
    record.right_polygon_id = right_polygon_id;
    record.requires_lsi = requires_lsi;
    record.requires_pip = requires_pip;
    params.output_records[slot] = record;
}}

extern "C" __global__ void __raygen__rtdl_overlay_dispatch() {{
    const uint32_t polygon_index = optixGetLaunchIndex().x;
    if (polygon_index >= params.probe_count) {{
        return;
    }}

    // Overlay composition is represented as a plan-level workload for now.
    // The runtime implementation will dispatch LSI and PIP subqueries from this seed stage.
}}

extern "C" __global__ void __miss__rtdl_miss() {{
    // Intentionally empty for the overlay path.
}}

extern "C" __global__ void __closesthit__rtdl_overlay_compose() {{
    // Overlay seed emission is deferred to a later runtime milestone.
    // This skeleton keeps the workload contract explicit in generated backend code.
}}
"""


def _render_layout_structs(plan: RayJoinPlan) -> str:
    seen = set()
    rendered = []

    for layout in (plan.build_input.layout, plan.probe_input.layout):
        if layout.name in seen:
            continue
        seen.add(layout.name)
        rendered.append(_render_layout_struct(layout))

    return "\n\n".join(rendered)


def _render_layout_struct(layout) -> str:
    fields = "\n".join(f"    {field.dtype.cuda_type} {field.name};" for field in layout.fields)
    return f"""struct {layout.name} {{
{fields}
}};"""


def _render_output_struct(plan: RayJoinPlan) -> str:
    fields = "\n".join(f"    {field.c_type} {field.name};" for field in plan.output_record.fields)
    return f"""struct {plan.output_record.name} {{
{fields}
}};"""


def _render_host(plan: RayJoinPlan) -> str:
    host_steps = "\n".join(f"    // {step}" for step in plan.host_steps)
    launch_params = "\n".join(
        f"    // {param.name}: {param.c_type} [{param.role}]"
        for param in plan.launch_params
    )
    return f"""#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

int main() {{
{host_steps}

    // LaunchParams contract
{launch_params}

    std::cout << "Generated OptiX skeleton for kernel: {plan.kernel_name}\\n";
    std::cout << "Workload kind: {plan.workload_kind}\\n";
    std::cout << "BVH policy: {plan.bvh_policy}\\n";
    std::cout << "Ray t-range: [{plan.ray_spec.tmin}, {plan.ray_spec.tmax}]\\n";
    std::cout << "Output record: {plan.output_record.name}\\n";
    std::cout << "Precision mode: {plan.precision}\\n";
    return 0;
}}
"""


def _render_readme(plan: RayJoinPlan) -> str:
    programs = "\n".join(f"- `{name}`" for name in plan.device_programs)
    buffers = "\n".join(f"- `{spec.name}`: `{spec.element}` ({spec.role})" for spec in plan.buffers)
    launch_params = "\n".join(f"- `{param.name}`: `{param.c_type}` ({param.role})" for param in plan.launch_params)
    return f"""# Generated OptiX Skeleton

This directory contains generated backend artifacts for the RTDL kernel `{plan.kernel_name}`.

## Workload

- `{plan.workload_kind}`
- predicate: `{plan.predicate}`
- refine mode: `{plan.exact_refine_mode}`

## Contents

- `plan.json`: serialized backend plan.
- `device_kernels.cu`: OptiX device program skeletons.
- `host_launcher.cpp`: host-side launcher skeleton.

## Device Programs

{programs}

## Launch Params

{launch_params}

## Buffers

{buffers}
"""


def _render_payload_comments(plan: RayJoinPlan) -> str:
    return "\n".join(
        f"    // p{register.index} -> {register.name} ({register.encoding})"
        for register in plan.payload_registers
    )


def _input_buffer_name(geometry_input) -> str:
    if geometry_input.name == geometry_input.geometry.name:
        return geometry_input.name
    return f"{geometry_input.name}_{geometry_input.geometry.name}"
