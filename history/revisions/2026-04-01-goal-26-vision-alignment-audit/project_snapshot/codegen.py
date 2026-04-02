from __future__ import annotations

import json
from pathlib import Path

from .ir import RTExecutionPlan


def generate_optix_project(plan: RTExecutionPlan, output_dir: str | Path) -> dict[str, Path]:
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


def _render_device(plan: RTExecutionPlan) -> str:
    if plan.workload_kind == "lsi":
        return _render_lsi_device(plan)
    if plan.workload_kind == "pip":
        return _render_pip_device(plan)
    if plan.workload_kind == "overlay":
        return _render_overlay_device(plan)
    if plan.workload_kind == "ray_tri_hitcount":
        return _render_ray_tri_hitcount_device(plan)
    if plan.workload_kind == "segment_polygon_hitcount":
        return _render_segment_polygon_hitcount_device(plan)
    if plan.workload_kind == "point_nearest_segment":
        return _render_point_nearest_segment_device(plan)
    raise ValueError(f"unsupported workload kind for codegen: {plan.workload_kind}")


def _render_lsi_device(plan: RTExecutionPlan) -> str:
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


def _render_pip_device(plan: RTExecutionPlan) -> str:
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


def _render_overlay_device(plan: RTExecutionPlan) -> str:
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


def _render_ray_tri_hitcount_device(plan: RTExecutionPlan) -> str:
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

static __forceinline__ __device__ float rtdl_cross2(float2 a, float2 b) {{
    return a.x * b.y - a.y * b.x;
}}

static __forceinline__ __device__ bool rtdl_segment_intersection(
    float2 p,
    float2 r,
    float2 q,
    float2 s
) {{
    const float denom = rtdl_cross2(r, s);
    if (fabsf(denom) < 1.0e-7f) {{
        return false;
    }}
    const float2 qp = make_float2(q.x - p.x, q.y - p.y);
    const float t = rtdl_cross2(qp, s) / denom;
    const float u = rtdl_cross2(qp, r) / denom;
    return t >= 0.0f && t <= 1.0f && u >= 0.0f && u <= 1.0f;
}}

static __forceinline__ __device__ bool rtdl_point_in_triangle(float2 p, const {plan.build_input.layout.name}& tri) {{
    const float2 a = make_float2(tri.x0, tri.y0);
    const float2 b = make_float2(tri.x1, tri.y1);
    const float2 c = make_float2(tri.x2, tri.y2);
    const float2 v0 = make_float2(c.x - a.x, c.y - a.y);
    const float2 v1 = make_float2(b.x - a.x, b.y - a.y);
    const float2 v2 = make_float2(p.x - a.x, p.y - a.y);

    const float dot00 = v0.x * v0.x + v0.y * v0.y;
    const float dot01 = v0.x * v1.x + v0.y * v1.y;
    const float dot02 = v0.x * v2.x + v0.y * v2.y;
    const float dot11 = v1.x * v1.x + v1.y * v1.y;
    const float dot12 = v1.x * v2.x + v1.y * v2.y;
    const float denom = dot00 * dot11 - dot01 * dot01;
    if (fabsf(denom) < 1.0e-7f) {{
        return false;
    }}
    const float inv = 1.0f / denom;
    const float u = (dot11 * dot02 - dot01 * dot12) * inv;
    const float v = (dot00 * dot12 - dot01 * dot02) * inv;
    return u >= 0.0f && v >= 0.0f && (u + v) <= 1.0f;
}}

static __forceinline__ __device__ bool rtdl_ray_hits_triangle(
    const {plan.probe_input.layout.name}& ray,
    const {plan.build_input.layout.name}& tri
) {{
    const float2 origin = make_float2(ray.ox, ray.oy);
    const float2 delta = make_float2(ray.dx * ray.tmax, ray.dy * ray.tmax);
    const float2 end = make_float2(origin.x + delta.x, origin.y + delta.y);

    if (rtdl_point_in_triangle(origin, tri) || rtdl_point_in_triangle(end, tri)) {{
        return true;
    }}

    const float2 a = make_float2(tri.x0, tri.y0);
    const float2 b = make_float2(tri.x1, tri.y1);
    const float2 c = make_float2(tri.x2, tri.y2);
    return rtdl_segment_intersection(origin, delta, a, make_float2(b.x - a.x, b.y - a.y))
        || rtdl_segment_intersection(origin, delta, b, make_float2(c.x - b.x, c.y - b.y))
        || rtdl_segment_intersection(origin, delta, c, make_float2(a.x - c.x, a.y - c.y));
}}

static __forceinline__ __device__ void rtdl_store_record(uint32_t ray_id, uint32_t hit_count) {{
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {{
        return;
    }}
    {plan.output_record.name} record = {{}};
    record.ray_id = ray_id;
    record.hit_count = hit_count;
    params.output_records[slot] = record;
}}

extern "C" __global__ void __raygen__rtdl_ray_hitcount() {{
    const uint32_t ray_index = optixGetLaunchIndex().x;
    if (ray_index >= params.probe_count) {{
        return;
    }}

    const {plan.probe_input.layout.name} probe = params.{probe_buffer}[ray_index];
    const float3 origin = make_float3({plan.ray_spec.origin[0]}, {plan.ray_spec.origin[1]}, {plan.ray_spec.origin[2]});
    const float3 direction = make_float3({plan.ray_spec.direction[0]}, {plan.ray_spec.direction[1]}, {plan.ray_spec.direction[2]});

    unsigned int p0 = ray_index;
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

    rtdl_store_record(probe.id, p2);
}}

extern "C" __global__ void __miss__rtdl_miss() {{
    // Intentionally empty for the ray-triangle hit-count path.
}}

extern "C" __global__ void __anyhit__rtdl_triangle_count() {{
    const uint32_t hit_count = optixGetPayload_2() + 1u;
    optixSetPayload_2(hit_count);
    optixIgnoreIntersection();
}}

extern "C" __global__ void __intersection__rtdl_triangles() {{
{payload_comments}
    const uint32_t triangle_index = optixGetPrimitiveIndex();
    const {plan.build_input.layout.name} tri = params.{build_buffer}[triangle_index];
    const uint32_t ray_index = optixGetPayload_0();
    const {plan.probe_input.layout.name} ray = params.{probe_buffer}[ray_index];

    if (!rtdl_ray_hits_triangle(ray, tri)) {{
        return;
    }}

    optixSetPayload_1(triangle_index);
    optixSetPayload_3(1u);
    optixReportIntersection(0.0f, 0u);
}}
"""


def _render_segment_polygon_hitcount_device(plan: RTExecutionPlan) -> str:
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

extern "C" __global__ void __raygen__rtdl_segment_polygon_probe() {{
    // Goal 10 placeholder: segment-vs-polygon hitcount lowers to a finite-segment
    // probe over polygon bounds. The runtime contract is fixed here even though
    // the full OptiX implementation remains future backend work.
}}

extern "C" __global__ void __closesthit__rtdl_segment_polygon_refine() {{
    // Count polygon hits per probe segment and materialize one record per segment.
}}

extern "C" __global__ void __intersection__rtdl_polygon_refs() {{
    // Reuse polygon-ref intersection semantics for segment-vs-polygon hitcount.
}}
"""


def _render_point_nearest_segment_device(plan: RTExecutionPlan) -> str:
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

extern "C" __global__ void __raygen__rtdl_point_nearest_segment() {{
    // Goal 10 placeholder: nearest-segment queries are represented in the IR and
    // plan, while the current executable implementation lives in the CPU/Embree
    // runtime rather than the OptiX backend.
}}

extern "C" __global__ void __closesthit__rtdl_point_nearest_segment_refine() {{
    // Materialize nearest segment id plus float distance for each probe point.
}}
"""


def _render_layout_structs(plan: RTExecutionPlan) -> str:
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


def _render_output_struct(plan: RTExecutionPlan) -> str:
    fields = "\n".join(f"    {field.c_type} {field.name};" for field in plan.output_record.fields)
    return f"""struct {plan.output_record.name} {{
{fields}
}};"""


def _render_host(plan: RTExecutionPlan) -> str:
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


def _render_readme(plan: RTExecutionPlan) -> str:
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


def _render_payload_comments(plan: RTExecutionPlan) -> str:
    return "\n".join(
        f"    // p{register.index} -> {register.name} ({register.encoding})"
        for register in plan.payload_registers
    )


def _input_buffer_name(geometry_input) -> str:
    if geometry_input.name == geometry_input.geometry.name:
        return geometry_input.name
    return f"{geometry_input.name}_{geometry_input.geometry.name}"
