from __future__ import annotations

from .ir import BufferSpec
from .ir import CompiledKernel
from .ir import LaunchParam
from .ir import OutputField
from .ir import OutputRecord
from .ir import PayloadRegister
from .ir import RTExecutionPlan
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
    "intersection_area": "uint32_t",
    "left_area": "uint32_t",
    "right_area": "uint32_t",
    "union_area": "uint32_t",
    "jaccard_similarity": "float",
    "ray_id": "uint32_t",
    "hit_count": "uint32_t",
    "any_hit": "uint32_t",
    "segment_id": "uint32_t",
    "query_id": "uint32_t",
    "neighbor_id": "uint32_t",
    "distance": "float",
    "neighbor_rank": "uint32_t",
}


def lower_to_execution_plan(kernel: CompiledKernel) -> RTExecutionPlan:
    if kernel.backend not in {"rtdl", "rayjoin"}:
        raise ValueError(f"unsupported backend for RTDL lowering: {kernel.backend}")

    if kernel.candidates is None or kernel.refine_op is None or kernel.emit_op is None:
        raise ValueError("kernel is incomplete and cannot be lowered")

    if kernel.candidates.accel != "bvh":
        raise ValueError(
            "the current RTDL lowering supports only accel='bvh' "
            f"(got accel={kernel.candidates.accel!r})"
        )

    if kernel.precision != "float_approx":
        raise ValueError(
            "the current RTDL lowering supports only precision='float_approx'; "
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
    if predicate.name == "ray_triangle_any_hit":
        return _lower_ray_triangle_any_hit(kernel, build_input, probe_input)
    if predicate.name == "segment_polygon_hitcount":
        return _lower_segment_polygon_hitcount(kernel, build_input, probe_input)
    if predicate.name == "segment_polygon_anyhit_rows":
        return _lower_segment_polygon_anyhit_rows(kernel, build_input, probe_input)
    if predicate.name == "polygon_pair_overlap_area_rows":
        return _lower_polygon_pair_overlap_area_rows(kernel, build_input, probe_input)
    if predicate.name == "polygon_set_jaccard":
        return _lower_polygon_set_jaccard(kernel, build_input, probe_input)
    if predicate.name == "point_nearest_segment":
        return _lower_point_nearest_segment(kernel, build_input, probe_input)
    if predicate.name == "fixed_radius_neighbors":
        return _lower_fixed_radius_neighbors(kernel, build_input, probe_input)
    if predicate.name == "knn_rows":
        return _lower_knn_rows(kernel, build_input, probe_input)
    if predicate.name == "bounded_knn_rows":
        return _lower_bounded_knn_rows(kernel, build_input, probe_input)

    raise ValueError(f"unsupported predicate for current RTDL lowering: {predicate.name}")


def _lower_lsi(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "segments" or probe_input.geometry.name != "segments":
        raise ValueError("the current LSI lowering only supports segment-vs-segment workloads")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "the current RTDL lowering supports only float-based segment_intersection predicates; "
            "use segment_intersection(exact=False)"
        )

    output_record = _build_output_record("IntersectionRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="lsi",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
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
            "Current local backend uses a native analytic nested-loop segment intersection path for correctness.",
            "Bind launch parameters with segment buffers, output buffer, output capacity, and atomic output counter.",
            "Future GPU backends may still lower this workload through BVH-backed candidate traversal once candidate completeness is demonstrated.",
            "Run one analytic segment-vs-segment pass per probe/build pair and emit intersection rows.",
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
            description="Current local backend does not use the historical segment-as-ray Embree path; this placeholder records the intended finite-segment query shape.",
        ),
        bvh_policy="current local backend uses native_loop for this workload; BVH-backed candidate traversal is suspended pending a parity-safe redesign",
    )


def _lower_pip(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "points":
        raise ValueError("the current PIP lowering requires polygon build input and point probe input")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "the current RTDL lowering supports only float-based point_in_polygon predicates; "
            "use point_in_polygon(exact=False)"
        )
    if predicate.options.get("boundary_mode") != "inclusive":
        raise ValueError("the current PIP lowering supports only boundary_mode='inclusive'")
    if predicate.options.get("result_mode", "full_matrix") not in {"full_matrix", "positive_hits"}:
        raise ValueError("the current PIP lowering supports only result_mode='full_matrix' or 'positive_hits'")

    output_record = _build_output_record("PointInPolygonRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="pip",
        backend="rtdl",
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


def _lower_overlay(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "polygons":
        raise ValueError("the current overlay lowering requires polygon-vs-polygon workloads")

    output_record = _build_output_record("OverlaySeedRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="overlay",
        backend="rtdl",
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


def _lower_segment_polygon_hitcount(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "segments":
        raise ValueError("segment_polygon_hitcount lowering requires polygon build input and segment probe input")

    output_record = _build_output_record("SegmentPolygonHitCountRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="segment_polygon_hitcount",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="segment_polygon_hitcount",
        exact_refine_mode="analytic_float_segment_polygon_hitcount",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="segment_index", encoding="u32"),
            PayloadRegister(index=1, name="polygon_index", encoding="u32"),
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
            f"Upload `{build_input.name}` polygons and `{probe_input.name}` segments.",
            "Current local backend uses a native nested-loop polygon hit-count path.",
            "Launch one finite probe segment per segment input and count intersected polygons.",
        ),
        device_programs=(
            "__raygen__rtdl_segment_polygon_probe",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_segment_polygon_refine",
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
            origin=("probe.x0", "probe.y0", "0.0f"),
            direction=("probe.x1 - probe.x0", "probe.y1 - probe.y0", "0.0f"),
            tmin="0.0f",
            tmax="1.0f",
            description="Cast each probe segment as a finite ray against polygon bounds and count polygon hits.",
        ),
        bvh_policy="current local backend uses native_loop for this workload; BVH build is not yet implemented",
    )


def _lower_point_nearest_segment(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "segments" or probe_input.geometry.name != "points":
        raise ValueError("point_nearest_segment lowering requires segment build input and point probe input")

    output_record = _build_output_record("PointNearestSegmentRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="point_nearest_segment",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="point_nearest_segment",
        exact_refine_mode="analytic_float_point_segment_distance",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="point_index", encoding="u32"),
            PayloadRegister(index=1, name="segment_index", encoding="u32"),
            PayloadRegister(index=2, name="distance_bits", encoding="f32_bits"),
            PayloadRegister(index=3, name="query_kind", encoding="u32"),
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
            f"Upload `{build_input.name}` segments and `{probe_input.name}` points.",
            "Current local backend uses a native nested-loop nearest-segment path.",
            "Run nearest-segment queries per point and materialize nearest id plus distance.",
        ),
        device_programs=(
            "__raygen__rtdl_point_nearest_segment",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_point_nearest_segment_refine",
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
            description="Nearest-query placeholder over segment bounds; current runtime uses a native float nearest-segment path.",
        ),
        bvh_policy="current local backend uses native_loop for this workload; BVH build is not yet implemented",
    )


def _lower_fixed_radius_neighbors(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "points" or probe_input.geometry.name != "points":
        raise ValueError("fixed_radius_neighbors lowering requires point build input and point probe input")

    output_record = _build_output_record("FixedRadiusNeighborRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)
    radius = kernel.refine_op.predicate.options["radius"]
    k_max = kernel.refine_op.predicate.options["k_max"]

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="fixed_radius_neighbors",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="fixed_radius_neighbors",
        exact_refine_mode="analytic_float_fixed_radius_neighbors",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="query_index", encoding="u32"),
            PayloadRegister(index=1, name="neighbor_index", encoding="u32"),
            PayloadRegister(index=2, name="distance_bits", encoding="f32_bits"),
            PayloadRegister(index=3, name="query_kind", encoding="u32"),
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
            f"Upload `{build_input.name}` search points and `{probe_input.name}` query points.",
            "Current local backend uses a native nested-loop fixed-radius-neighbor path.",
            f"Apply inclusive radius filtering with radius={radius!r}, sort per query by distance then neighbor id, and truncate to k_max={k_max!r}.",
        ),
        device_programs=(
            "__raygen__rtdl_fixed_radius_neighbors",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_fixed_radius_neighbors_refine",
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
            description="Fixed-radius-neighbor placeholder over point sets; current runtime uses a native float nested-loop path.",
        ),
        bvh_policy="current local backend uses native_loop for this workload; BVH build is not yet implemented",
    )


def _lower_knn_rows(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "points" or probe_input.geometry.name != "points":
        raise ValueError("knn_rows lowering requires point build input and point probe input")

    output_record = _build_output_record("KnnNeighborRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)
    k = kernel.refine_op.predicate.options["k"]

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="knn_rows",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="knn_rows",
        exact_refine_mode="analytic_float_knn_rows",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="query_index", encoding="u32"),
            PayloadRegister(index=1, name="neighbor_index", encoding="u32"),
            PayloadRegister(index=2, name="distance_bits", encoding="f32_bits"),
            PayloadRegister(index=3, name="neighbor_rank", encoding="u32"),
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
            f"Upload `{build_input.name}` search points and `{probe_input.name}` query points.",
            "Current local backend for this planned workload is still a native analytic nearest-neighbor pass.",
            f"Sort each query's candidate set by distance then neighbor id, assign 1-based neighbor_rank, and emit at most k={k!r} rows.",
        ),
        device_programs=(
            "__raygen__rtdl_knn_rows",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_knn_rows_refine",
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
            description="KNN placeholder over point sets; current runtime is planned as a native float nearest-neighbor pass.",
        ),
        bvh_policy="current local backend uses native_loop for this workload; BVH build is not yet implemented",
    )


def _lower_bounded_knn_rows(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "points" or probe_input.geometry.name != "points":
        raise ValueError("bounded_knn_rows lowering requires point build input and point probe input")

    output_record = _build_output_record("BoundedKnnNeighborRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)
    radius = kernel.refine_op.predicate.options["radius"]
    k_max = kernel.refine_op.predicate.options["k_max"]

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="bounded_knn_rows",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="bounded_knn_rows",
        exact_refine_mode="analytic_float_bounded_knn_rows",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="query_index", encoding="u32"),
            PayloadRegister(index=1, name="neighbor_index", encoding="u32"),
            PayloadRegister(index=2, name="distance_bits", encoding="f32_bits"),
            PayloadRegister(index=3, name="neighbor_rank", encoding="u32"),
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
            f"Upload `{build_input.name}` search points and `{probe_input.name}` query points.",
            "Current local backend for this planned workload is a native analytic bounded nearest-neighbor pass.",
            f"Filter neighbors by inclusive radius={radius!r}, sort each query by distance then neighbor id, assign 1-based neighbor_rank, and emit at most k_max={k_max!r} rows.",
        ),
        device_programs=(
            "__raygen__rtdl_bounded_knn_rows",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_bounded_knn_rows_refine",
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
            description="Bounded KNN placeholder over point sets; current runtime is planned as a native float bounded nearest-neighbor pass.",
        ),
        bvh_policy="current local backend uses native_loop for this workload; BVH build is not yet implemented",
    )


def _lower_ray_triangle_hitcount(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
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

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="ray_tri_hitcount",
        backend="rtdl",
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


def _lower_ray_triangle_any_hit(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "triangles" or probe_input.geometry.name != "rays":
        raise ValueError("the current ray any-hit lowering requires triangle build input and ray probe input")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "the current ray any-hit lowering supports only float-based ray_triangle_any_hit predicates; "
            "use ray_triangle_any_hit(exact=False)"
        )

    output_record = _build_output_record("RayAnyHitRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="ray_tri_anyhit",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind=kernel.candidates.accel,
        predicate=predicate.name,
        exact_refine_mode="analytic_float_ray_triangle_any_hit",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="ray_index", encoding="u32"),
            PayloadRegister(index=1, name="triangle_index", encoding="u32"),
            PayloadRegister(index=2, name="any_hit", encoding="u32"),
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
            "Launch one finite ray per probe and terminate traversal after the first accepted triangle hit.",
            "Emit exactly one row per ray with any_hit=1 for a blocker and any_hit=0 otherwise.",
        ),
        device_programs=(
            "__raygen__rtdl_ray_anyhit",
            "__miss__rtdl_miss",
            "__anyhit__rtdl_triangle_terminate",
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
            description="Trace each finite ray against the build-side triangle BVH and stop after the first accepted hit.",
        ),
        bvh_policy=f"build over `{build_input.name}`, probe with `{probe_input.name}`; any-hit traversal is bounded by early termination",
    )


def _lower_segment_polygon_anyhit_rows(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "segments":
        raise ValueError("segment_polygon_anyhit_rows lowering requires polygon build input and segment probe input")

    output_record = _build_output_record("SegmentPolygonAnyHitRowRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="segment_polygon_anyhit_rows",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="segment_polygon_anyhit_rows",
        exact_refine_mode="analytic_float_segment_polygon_anyhit_rows",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="segment_index", encoding="u32"),
            PayloadRegister(index=1, name="polygon_index", encoding="u32"),
            PayloadRegister(index=2, name="hit_kind", encoding="u32"),
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
            f"Upload `{build_input.name}` polygons and `{probe_input.name}` segments.",
            "Current local backend uses a native exact any-hit row materialization path.",
            "Emit one `(segment_id, polygon_id)` row per exact segment/polygon hit.",
        ),
        device_programs=(
            "__raygen__rtdl_segment_polygon_probe",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_segment_polygon_refine",
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
            origin=("probe.x0", "probe.y0", "0.0f"),
            direction=("probe.x1 - probe.x0", "probe.y1 - probe.y0", "0.0f"),
            tmin="0.0f",
            tmax="1.0f",
            description="Finite 2D segment against polygon set with one emitted row per true segment/polygon hit.",
        ),
        bvh_policy=f"build over `{build_input.name}`, probe with `{probe_input.name}`",
    )


def _lower_polygon_pair_overlap_area_rows(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "polygons":
        raise ValueError("polygon_pair_overlap_area_rows lowering requires polygon-vs-polygon workloads")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "polygon_pair_overlap_area_rows currently supports only exact=False under the "
            "integer-grid pathology contract"
        )

    output_record = _build_output_record("PolygonPairOverlapAreaRowRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="polygon_pair_overlap_area_rows",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="polygon_pair_overlap_area_rows",
        exact_refine_mode="integer_grid_polygon_overlap_area_rows",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="left_polygon_index", encoding="u32"),
            PayloadRegister(index=1, name="right_polygon_index", encoding="u32"),
            PayloadRegister(index=2, name="intersection_area", encoding="u32"),
            PayloadRegister(index=3, name="union_area", encoding="u32"),
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
            f"Upload `{build_input.name}` and `{probe_input.name}` pathology-style polygons.",
            "Validate the current narrow contract: integer-grid vertices, orthogonal edges, no hole support.",
            "Current local backend uses a native CPU-style cell-coverage overlap path instead of full polygon overlay.",
            "Emit only positive-overlap polygon-pair rows with overlap, side areas, and union area.",
        ),
        device_programs=(
            "__raygen__rtdl_polygon_pair_overlap_area_rows",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_polygon_pair_overlap_area_rows_refine",
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
            description="Current primitive is a CPU/oracle-first overlap-area materialization path for orthogonal integer-grid polygons.",
        ),
        bvh_policy="current local backend uses native_loop for this primitive; BVH-backed polygon overlap traversal is not implemented",
    )


def _lower_polygon_set_jaccard(kernel: CompiledKernel, build_input, probe_input) -> RTExecutionPlan:
    predicate = kernel.refine_op.predicate
    if build_input.geometry.name != "polygons" or probe_input.geometry.name != "polygons":
        raise ValueError("polygon_set_jaccard lowering requires polygon-vs-polygon workloads")
    if predicate.options.get("exact") is not False:
        raise ValueError(
            "polygon_set_jaccard currently supports only exact=False under the integer-grid pathology contract"
        )

    output_record = _build_output_record("PolygonSetJaccardRecord", kernel.emit_op.fields)
    build_buffer_name = _input_buffer_name(build_input)
    probe_buffer_name = _input_buffer_name(probe_input)

    return RTExecutionPlan(
        kernel_name=kernel.name,
        workload_kind="polygon_set_jaccard",
        backend="rtdl",
        precision=kernel.precision,
        build_input=build_input,
        probe_input=probe_input,
        accel_kind="native_loop",
        predicate="polygon_set_jaccard",
        exact_refine_mode="integer_grid_polygon_set_jaccard",
        emit_fields=kernel.emit_op.fields,
        payload_registers=(
            PayloadRegister(index=0, name="left_area", encoding="u32"),
            PayloadRegister(index=1, name="right_area", encoding="u32"),
            PayloadRegister(index=2, name="intersection_area", encoding="u32"),
            PayloadRegister(index=3, name="union_area", encoding="u32"),
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
            f"Upload `{build_input.name}` and `{probe_input.name}` pathology-style polygon sets.",
            "Validate the same narrow contract used by polygon_pair_overlap_area_rows: orthogonal integer-grid polygons and unit-cell area.",
            "Current local backend computes one aggregate Jaccard row for the entire left set against the entire right set.",
            "This first closure computes aggregate set coverage by unit-cell union across each polygon set.",
        ),
        device_programs=(
            "__raygen__rtdl_polygon_set_jaccard",
            "__miss__rtdl_miss",
            "__closesthit__rtdl_polygon_set_jaccard_refine",
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
            description="Current aggregate Jaccard path is CPU/oracle-first and not a BVH-backed traversal story.",
        ),
        bvh_policy="current local backend uses native_loop for this aggregate primitive; BVH-backed set Jaccard traversal is not implemented",
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
            raise ValueError(f"unsupported emitted field for current RTDL lowering: {name}")
        fields.append(OutputField(name=name, c_type=c_type))

    return OutputRecord(name=record_name, fields=tuple(fields))


def _input_buffer_name(geometry_input) -> str:
    if geometry_input.name == geometry_input.geometry.name:
        return geometry_input.name
    return f"{geometry_input.name}_{geometry_input.geometry.name}"


def lower_to_rayjoin(kernel: CompiledKernel) -> RTExecutionPlan:
    """Legacy alias for the current v0.1 RayJoin-oriented lowering entry point."""
    return lower_to_execution_plan(kernel)
