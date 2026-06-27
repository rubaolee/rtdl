from __future__ import annotations

from .ir import BufferSpec
from .ir import CompiledKernel
from .ir import LaunchParam
from .ir import OutputField
from .ir import OutputRecord
from .ir import PayloadRegister
from .ir import RayJoinPlan
from .ir import RaySpec


_EMIT_FIELD_TYPES = {
    "left_id": "uint32_t",
    "right_id": "uint32_t",
    "intersection_point_x": "float",
    "intersection_point_y": "float",
    "point_id": "uint32_t",
    "polygon_id": "uint32_t",
    "contains": "uint32_t",
    "left_polygon_id": "uint32_t",
    "right_polygon_id": "uint32_t",
    "requires_lsi": "uint32_t",
    "requires_pip": "uint32_t",
    "ray_id": "uint32_t",
    "hit_count": "uint32_t",
}


def lower_to_rayjoin(kernel: CompiledKernel) -> RayJoinPlan:
    if kernel.backend != "rayjoin":
        raise ValueError(f"unsupported backend for RayJoin lowering: {kernel.backend}")

    if kernel.candidates is None or kernel.refine_op is None or kernel.emit_op is None:
        raise ValueError("kernel is incomplete and cannot be lowered")

    if kernel.candidates.accel != "bvh":
        raise ValueError(
            "the current RayJoin lowering supports only accel='bvh' "
            f"(got accel={kernel.candidates.accel!r})"
        )

    if kernel.precision != "float_approx":
        raise ValueError(
            "the current RayJoin lowering supports only precision='float_approx'; "
            "precision='exact' is not implemented yet"
        )

    build_input, probe_input = _choose_roles(kernel)
    predicate = kernel.refine_op.predicate

    if predicate.name == "segment_intersection":
        return _lower_lsi(kernel, build_input, probe_input)
    if predicate.name == "point_in_polygon":
        return _lower_pip(kernel, build_input, probe_input)
    if predicate.name == "overlay_compose":
        return _lower_overlay(kernel, build_input, probe_input)
    if predicate.name == "ray_triangle_hit_count":
        return _lower_ray_triangle_hitcount(kernel, build_input, probe_input)

    raise ValueError(f"unsupported predicate for current RayJoin lowering: {predicate.name}")


def _lower_lsi(kernel: CompiledKernel, build_input, probe_input) -> RayJoinPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "segments" or probe_input.geometry.name != "segments":
        raise ValueError("the current LSI lowering only supports segment-vs-segment workloads")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "the current RayJoin lowering supports only float-based segment_intersection predicates; "
            "use segment_intersection(exact=False)"
        )

    output_record = _build_output_record("IntersectionRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RayJoinPlan(
        kernel_name=kernel.name,
        workload_kind="lsi",
        backend=kernel.backend,
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind=kernel.candidates.accel,
        predicate=predicate.name,
        exact_refine_mode="analytic_float_segment_intersection",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="probe_index", encoding="u32"),
            PayloadRegister(index=1, name="build_primitive_index", encoding="u32"),
            PayloadRegister(index=2, name="hit_t_bits", encoding="f32_bits"),
            PayloadRegister(index=3, name="hit_kind", encoding="u32"),
        ),
        launch_params=(
            LaunchParam(name="traversable", c_type="OptixTraversableHandle", role="rt_accel"),
            LaunchParam(name=build_buffer_name, c_type=f"const {build_input.layout.name}*", role="device_input_build"),
            LaunchParam(name=probe_buffer_name, c_type=f"const {probe_input.layout.name}*", role="device_input_probe"),
            LaunchParam(name="output_records", c_type=f"{output_record.name}*", role="device_output"),
            LaunchParam(name="output_count", c_type="uint32_t*", role="device_counter"),
            LaunchParam(name="output_capacity", c_type="uint32_t", role="device_limit"),
            LaunchParam(name="probe_count", c_type="uint32_t", role="launch_size"),
        ),
        host_steps=(
            f"Upload `{build_input.name}` and `{probe_input.name}` arrays using `{build_input.layout.name}` / `{probe_input.layout.name}` layouts.",
            f"Build BVH over `{build_input.name}` and export an OptixTraversableHandle.",
            "Bind launch parameters with segment buffers, output buffer, output capacity, and atomic output counter.",
            "Create OptiX module, raygen/miss/closesthit/intersection program groups, and shader binding table.",
            f"Launch one probe ray per `{probe_input.name}` segment with t-range [0, 1].",
            "Pack probe/build indices into payload registers p0-p3 and run float-based refinement before emitting records.",
        ),
        device_programs=(
            "__raygen__rtdl_probe",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_refine",
            "__intersection__rtdl_segments",
        ),
        buffers=(
            BufferSpec(name=build_buffer_name, element=build_input.layout.name, role="device_input_build"),
            BufferSpec(name=probe_buffer_name, element=probe_input.layout.name, role="device_input_probe"),
            BufferSpec(name="output_records", element=output_record.name, role="device_output"),
            BufferSpec(name="output_count", element="uint32_t", role="device_counter"),
            BufferSpec(name="output_capacity", element="uint32_t", role="device_limit"),
        ),
        output_record=output_record,
        ray_spec=RaySpec(
            origin=("probe.x0", "probe.y0", "0.0f"),
            direction=("probe.x1 - probe.x0", "probe.y1 - probe.y0", "0.0f"),
            tmin="0.0f",
            tmax="1.0f",
            description="Cast each probe segment as a finite ray over the build-side BVH.",
        ),
        bvh_policy=f"build over `{build_input.name}`, probe with `{probe_input.name}`",
    )


def _lower_pip(kernel: CompiledKernel, build_input, probe_input) -> RayJoinPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "points":
        raise ValueError("the current PIP lowering requires polygon build input and point probe input")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "the current RayJoin lowering supports only float-based point_in_polygon predicates; "
            "use point_in_polygon(exact=False)"
        )
    if predicate.options.get("boundary_mode") != "inclusive":
        raise ValueError("the current PIP lowering supports only boundary_mode='inclusive'")

    output_record = _build_output_record("PointInPolygonRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RayJoinPlan(
        kernel_name=kernel.name,
        workload_kind="pip",
        backend=kernel.backend,
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind=kernel.candidates.accel,
        predicate=predicate.name,
        exact_refine_mode="analytic_float_point_in_polygon",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="point_index", encoding="u32"),
            PayloadRegister(index=1, name="polygon_face_index", encoding="u32"),
            PayloadRegister(index=2, name="winding_hits", encoding="u32"),
            PayloadRegister(index=3, name="hit_kind", encoding="u32"),
        ),
        launch_params=(
            LaunchParam(name="traversable", c_type="OptixTraversableHandle", role="rt_accel"),
            LaunchParam(name=build_buffer_name, c_type=f"const {build_input.layout.name}*", role="device_input_build"),
            LaunchParam(name=probe_buffer_name, c_type=f"const {probe_input.layout.name}*", role="device_input_probe"),
            LaunchParam(name="output_records", c_type=f"{output_record.name}*", role="device_output"),
            LaunchParam(name="output_count", c_type="uint32_t*", role="device_counter"),
            LaunchParam(name="output_capacity", c_type="uint32_t", role="device_limit"),
            LaunchParam(name="probe_count", c_type="uint32_t", role="launch_size"),
        ),
        host_steps=(
            f"Upload `{build_input.name}` polygon refs and `{probe_input.name}` points using `{build_input.layout.name}` / `{probe_input.layout.name}` layouts.",
            f"Build BVH over polygon references from `{build_input.name}` and export an OptixTraversableHandle.",
            "Bind launch parameters with polygon refs, point probes, output buffer, output capacity, and atomic output counter.",
            "Create OptiX module, raygen/miss/closesthit/intersection program groups, and shader binding table.",
            f"Launch one vertical parity ray per `{probe_input.name}` point.",
            "Pack point/polygon indices into payload registers and run float-based point-in-polygon refinement before emitting records.",
        ),
        device_programs=(
            "__raygen__rtdl_pip_probe",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_pip_refine",
            "__intersection__rtdl_polygon_refs",
        ),
        buffers=(
            BufferSpec(name=build_buffer_name, element=build_input.layout.name, role="device_input_build"),
            BufferSpec(name=probe_buffer_name, element=probe_input.layout.name, role="device_input_probe"),
            BufferSpec(name="output_records", element=output_record.name, role="device_output"),
            BufferSpec(name="output_count", element="uint32_t", role="device_counter"),
            BufferSpec(name="output_capacity", element="uint32_t", role="device_limit"),
        ),
        output_record=output_record,
        ray_spec=RaySpec(
            origin=("probe.x", "probe.y", "0.0f"),
            direction=("0.0f", "1.0f", "0.0f"),
            tmin="0.0f",
            tmax="FLT_MAX",
            description="Cast one upward parity ray from each probe point over the build-side polygon BVH.",
        ),
        bvh_policy=f"build over `{build_input.name}`, probe with `{probe_input.name}`",
    )


def _lower_overlay(kernel: CompiledKernel, build_input, probe_input) -> RayJoinPlan:
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "polygons":
        raise ValueError("the current overlay lowering requires polygon-vs-polygon workloads")

    output_record = _build_output_record("OverlaySeedRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RayJoinPlan(
        kernel_name=kernel.name,
        workload_kind="overlay",
        backend=kernel.backend,
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind=kernel.candidates.accel,
        predicate="overlay_compose",
        exact_refine_mode="compose_lsi_plus_pip",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="left_polygon_index", encoding="u32"),
            PayloadRegister(index=1, name="right_polygon_index", encoding="u32"),
            PayloadRegister(index=2, name="overlay_flags", encoding="u32"),
            PayloadRegister(index=3, name="hit_kind", encoding="u32"),
        ),
        launch_params=(
            LaunchParam(name="traversable", c_type="OptixTraversableHandle", role="rt_accel"),
            LaunchParam(name=build_buffer_name, c_type=f"const {build_input.layout.name}*", role="device_input_build"),
            LaunchParam(name=probe_buffer_name, c_type=f"const {probe_input.layout.name}*", role="device_input_probe"),
            LaunchParam(name="output_records", c_type=f"{output_record.name}*", role="device_output"),
            LaunchParam(name="output_count", c_type="uint32_t*", role="device_counter"),
            LaunchParam(name="output_capacity", c_type="uint32_t", role="device_limit"),
            LaunchParam(name="probe_count", c_type="uint32_t", role="launch_size"),
        ),
        host_steps=(
            f"Upload `{build_input.name}` and `{probe_input.name}` polygon refs using `{build_input.layout.name}` layouts.",
            f"Build BVH over `{build_input.name}` polygon refs and export an OptixTraversableHandle.",
            "Bind launch parameters for overlay seed generation and output buffering.",
            "Create OptiX program groups for overlay dispatch and composition skeletons.",
            f"Launch one probe polygon per `{probe_input.name}` polygon to collect overlay candidate seeds.",
            "Compose overlay seeds from LSI-style edge intersections plus PIP-style containment checks before emitting records.",
        ),
        device_programs=(
            "__raygen__rtdl_overlay_dispatch",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_overlay_compose",
        ),
        buffers=(
            BufferSpec(name=build_buffer_name, element=build_input.layout.name, role="device_input_build"),
            BufferSpec(name=probe_buffer_name, element=probe_input.layout.name, role="device_input_probe"),
            BufferSpec(name="output_records", element=output_record.name, role="device_output"),
            BufferSpec(name="output_count", element="uint32_t", role="device_counter"),
            BufferSpec(name="output_capacity", element="uint32_t", role="device_limit"),
        ),
        output_record=output_record,
        ray_spec=RaySpec(
            origin=("0.0f", "0.0f", "0.0f"),
            direction=("0.0f", "0.0f", "1.0f"),
            tmin="0.0f",
            tmax="1.0f",
            description="Dispatch polygon-pair overlay seeds and compose LSI/PIP subqueries at the plan level.",
        ),
        bvh_policy=f"build over `{build_input.name}`, probe with `{probe_input.name}`",
    )


def _lower_ray_triangle_hitcount(kernel: CompiledKernel, build_input, probe_input) -> RayJoinPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "triangles" or probe_input.geometry.name != "rays":
        raise ValueError("the current ray hit-count lowering requires triangle build input and ray probe input")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "the current ray hit-count lowering supports only float-based ray_triangle_hit_count predicates; "
            "use ray_triangle_hit_count(exact=False)"
        )

    output_record = _build_output_record("RayHitCountRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RayJoinPlan(
        kernel_name=kernel.name,
        workload_kind="ray_tri_hitcount",
        backend=kernel.backend,
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind=kernel.candidates.accel,
        predicate=predicate.name,
        exact_refine_mode="analytic_float_ray_triangle_hit_count",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="ray_index", encoding="u32"),
            PayloadRegister(index=1, name="triangle_index", encoding="u32"),
            PayloadRegister(index=2, name="hit_count", encoding="u32"),
            PayloadRegister(index=3, name="hit_kind", encoding="u32"),
        ),
        launch_params=(
            LaunchParam(name="traversable", c_type="OptixTraversableHandle", role="rt_accel"),
            LaunchParam(name=build_buffer_name, c_type=f"const {build_input.layout.name}*", role="device_input_build"),
            LaunchParam(name=probe_buffer_name, c_type=f"const {probe_input.layout.name}*", role="device_input_probe"),
            LaunchParam(name="output_records", c_type=f"{output_record.name}*", role="device_output"),
            LaunchParam(name="output_count", c_type="uint32_t*", role="device_counter"),
            LaunchParam(name="output_capacity", c_type="uint32_t", role="device_limit"),
            LaunchParam(name="probe_count", c_type="uint32_t", role="launch_size"),
        ),
        host_steps=(
            f"Upload `{build_input.name}` triangles and `{probe_input.name}` rays using `{build_input.layout.name}` / `{probe_input.layout.name}` layouts.",
            f"Build BVH over `{build_input.name}` triangles and export an OptixTraversableHandle.",
            "Bind launch parameters with triangle buffers, ray buffers, output buffer, output capacity, and atomic output counter.",
            "Create OptiX module, raygen/miss/anyhit/intersection program groups, and shader binding table.",
            f"Launch one finite ray per `{probe_input.name}` record.",
            "Accumulate one hit count per ray across intersected triangles before emitting a single output record.",
        ),
        device_programs=(
            "__raygen__rtdl_ray_hitcount",
            "__miss__rtdl_miss",
            "__anyhit__rtdl_triangle_count",
            "__intersection__rtdl_triangles",
        ),
        buffers=(
            BufferSpec(name=build_buffer_name, element=build_input.layout.name, role="device_input_build"),
            BufferSpec(name=probe_buffer_name, element=probe_input.layout.name, role="device_input_probe"),
            BufferSpec(name="output_records", element=output_record.name, role="device_output"),
            BufferSpec(name="output_count", element="uint32_t", role="device_counter"),
            BufferSpec(name="output_capacity", element="uint32_t", role="device_limit"),
        ),
        output_record=output_record,
        ray_spec=RaySpec(
            origin=("probe.ox", "probe.oy", "0.0f"),
            direction=("probe.dx", "probe.dy", "0.0f"),
            tmin="0.0f",
            tmax="probe.tmax",
            description="Trace each finite 2D ray against the build-side triangle BVH and count triangle hits.",
        ),
        bvh_policy=f"build over `{build_input.name}`, probe with `{probe_input.name}`",
    )


def _choose_roles(kernel: CompiledKernel):
    left = kernel.candidates.left
    right = kernel.candidates.right

    if left.role is not None and left.role == right.role:
        raise ValueError("candidate inputs cannot share the same explicit role")

    if left.role == "build" and right.role == "probe":
        return left, right
    if left.role == "probe" and right.role == "build":
        return right, left
    if left.role == "build":
        return left, right
    if right.role == "build":
        return right, left
    if left.role == "probe":
        return right, left
    if right.role == "probe":
        return left, right

    left_geometry = left.geometry.name
    right_geometry = right.geometry.name
    if left_geometry == "points" and right_geometry == "polygons":
        return right, left
    if left_geometry == "polygons" and right_geometry == "points":
        return left, right
    if left_geometry == "rays" and right_geometry == "triangles":
        return right, left
    if left_geometry == "triangles" and right_geometry == "rays":
        return left, right

    return right, left


def _build_output_record(record_name: str, emit_fields: tuple[str, ...]) -> OutputRecord:
    if not emit_fields:
        raise ValueError("emit schema must contain at least one field")

    fields = []
    for name in emit_fields:
        c_type = _EMIT_FIELD_TYPES.get(name)
        if c_type is None:
            raise ValueError(f"unsupported emitted field for current RayJoin lowering: {name}")
        fields.append(OutputField(name=name, c_type=c_type))

    return OutputRecord(name=record_name, fields=tuple(fields))


def _input_buffer_name(geometry_input) -> str:
    if geometry_input.name == geometry_input.geometry.name:
        return geometry_input.name
    return f"{geometry_input.name}_{geometry_input.geometry.name}"
