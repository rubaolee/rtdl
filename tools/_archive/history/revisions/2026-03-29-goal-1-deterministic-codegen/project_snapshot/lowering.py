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
}


def lower_to_rayjoin(kernel: CompiledKernel) -> RayJoinPlan:
    if kernel.backend != "rayjoin":
        raise ValueError(f"unsupported backend for RayJoin lowering: {kernel.backend}")

    if kernel.candidates is None or kernel.refine_op is None or kernel.emit_op is None:
        raise ValueError("kernel is incomplete and cannot be lowered")

    if kernel.candidates.left.geometry.name != "segments" or kernel.candidates.right.geometry.name != "segments":
        raise ValueError("the current RayJoin lowering only supports segment-vs-segment workloads")

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

    predicate = kernel.refine_op.predicate
    if predicate.name != "segment_intersection" or predicate.options.get("exact") is not False:
        raise ValueError(
            "the current RayJoin lowering supports only float-based segment_intersection predicates; "
            "use segment_intersection(exact=False)"
        )

    build_input, probe_input = _choose_roles(kernel)

    output_record = _build_output_record(kernel.emit_op.fields)

    return RayJoinPlan(
        kernel_name=kernel.name,
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
            LaunchParam(name=f"{build_input.name}_segments", c_type=f"const {build_input.layout.name}*", role="device_input_build"),
            LaunchParam(name=f"{probe_input.name}_segments", c_type=f"const {probe_input.layout.name}*", role="device_input_probe"),
            LaunchParam(name="output_records", c_type=f"{output_record.name}*", role="device_output"),
            LaunchParam(name="output_count", c_type="uint32_t*", role="device_counter"),
            LaunchParam(name="output_capacity", c_type="uint32_t", role="device_limit"),
            LaunchParam(name="probe_count", c_type="uint32_t", role="launch_size"),
        ),
        host_steps=(
            f"Upload `{build_input.name}` and `{probe_input.name}` arrays using `{build_input.layout.name}` / `{probe_input.layout.name}` layouts.",
            f"Build {kernel.candidates.accel.upper()} over `{build_input.name}` and export an OptixTraversableHandle.",
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
            BufferSpec(
                name=f"{build_input.name}_segments",
                element=build_input.layout.name,
                role="device_input_build",
            ),
            BufferSpec(
                name=f"{probe_input.name}_segments",
                element=probe_input.layout.name,
                role="device_input_probe",
            ),
            BufferSpec(
                name="output_records",
                element=output_record.name,
                role="device_output",
            ),
            BufferSpec(
                name="output_count",
                element="uint32_t",
                role="device_counter",
            ),
            BufferSpec(
                name="output_capacity",
                element="uint32_t",
                role="device_limit",
            ),
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
    return right, left


def _build_output_record(emit_fields: tuple[str, ...]) -> OutputRecord:
    if not emit_fields:
        raise ValueError("emit schema must contain at least one field")

    fields = []
    for name in emit_fields:
        c_type = _EMIT_FIELD_TYPES.get(name)
        if c_type is None:
            raise ValueError(f"unsupported emitted field for current RayJoin lowering: {name}")
        fields.append(OutputField(name=name, c_type=c_type))

    return OutputRecord(name="IntersectionRecord", fields=tuple(fields))
