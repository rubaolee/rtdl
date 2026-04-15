from __future__ import annotations

from dataclasses import dataclass, field

from .layout_types import GeometryType
from .layout_types import Layout

RTDL_PLAN_SCHEMA_ID = "https://rtdl.dev/schemas/rtdl-plan-v1alpha1.json"


@dataclass(frozen=True)
class GeometryInput:
    name: str
    geometry: GeometryType
    layout: Layout
    role: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "geometry": self.geometry.name,
            "layout": self.layout.name,
            "role": self.role,
            "fields": [field.to_dict() for field in self.layout.fields],
        }


@dataclass(frozen=True)
class CandidateSet:
    left: GeometryInput
    right: GeometryInput
    accel: str
    mode: str | None = None


@dataclass(frozen=True)
class Predicate:
    name: str
    options: dict[str, object]


@dataclass(frozen=True)
class RefineOp:
    candidates: CandidateSet
    predicate: Predicate


@dataclass(frozen=True)
class EmitOp:
    source: RefineOp
    fields: tuple[str, ...]


@dataclass(frozen=True)
class BufferSpec:
    name: str
    element: str
    role: str


@dataclass(frozen=True)
class PayloadRegister:
    index: int
    name: str
    encoding: str

    def to_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "name": self.name,
            "encoding": self.encoding,
        }


@dataclass(frozen=True)
class LaunchParam:
    name: str
    c_type: str
    role: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "c_type": self.c_type,
            "role": self.role,
        }


@dataclass(frozen=True)
class OutputField:
    name: str
    c_type: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "c_type": self.c_type,
        }


@dataclass(frozen=True)
class OutputRecord:
    name: str
    fields: tuple[OutputField, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "fields": [field.to_dict() for field in self.fields],
        }


@dataclass(frozen=True)
class RaySpec:
    origin: tuple[str, str, str]
    direction: tuple[str, str, str]
    tmin: str
    tmax: str
    description: str

    def to_dict(self) -> dict[str, object]:
        return {
            "origin": list(self.origin),
            "direction": list(self.direction),
            "tmin": self.tmin,
            "tmax": self.tmax,
            "description": self.description,
        }


@dataclass(frozen=True)
class RTExecutionPlan:
    kernel_name: str
    workload_kind: str
    backend: str
    precision: str
    build_input: GeometryInput
    probe_input: GeometryInput
    accel_kind: str
    predicate: str
    exact_refine_mode: str
    emit_fields: tuple[str, ...]
    payload_registers: tuple[PayloadRegister, ...]
    launch_params: tuple[LaunchParam, ...]
    host_steps: tuple[str, ...]
    device_programs: tuple[str, ...]
    buffers: tuple[BufferSpec, ...]
    output_record: OutputRecord
    ray_spec: RaySpec
    bvh_policy: str

    def to_dict(self) -> dict[str, object]:
        return {
            "$schema": RTDL_PLAN_SCHEMA_ID,
            "schema_version": "v1alpha1",
            "kernel_name": self.kernel_name,
            "workload_kind": self.workload_kind,
            "backend": self.backend,
            "precision": self.precision,
            "build_input": self.build_input.to_dict(),
            "probe_input": self.probe_input.to_dict(),
            "accel_kind": self.accel_kind,
            "predicate": self.predicate,
            "exact_refine_mode": self.exact_refine_mode,
            "emit_fields": list(self.emit_fields),
            "payload_registers": [register.to_dict() for register in self.payload_registers],
            "launch_params": [param.to_dict() for param in self.launch_params],
            "buffers": [
                {"name": spec.name, "element": spec.element, "role": spec.role}
                for spec in self.buffers
            ],
            "output_record": self.output_record.to_dict(),
            "ray_spec": self.ray_spec.to_dict(),
            "device_programs": list(self.device_programs),
            "host_steps": list(self.host_steps),
            "bvh_policy": self.bvh_policy,
        }

    def format(self) -> str:
        lines = [
            "RTDL Backend Plan",
            "--------------------",
            f"kernel    : {self.kernel_name}",
            f"workload  : {self.workload_kind}",
            f"backend   : {self.backend}",
            f"precision : {self.precision}",
            f"build     : {self.build_input.name} ({self.build_input.geometry.name}, {self.build_input.layout.name})",
            f"probe     : {self.probe_input.name} ({self.probe_input.geometry.name}, {self.probe_input.layout.name})",
            f"accel     : {self.accel_kind}",
            f"predicate : {self.predicate}",
            f"refine    : {self.exact_refine_mode}",
            f"emit      : {', '.join(self.emit_fields)}",
            f"bvh policy: {self.bvh_policy}",
            "",
            "Payload Registers",
            "-----------------",
        ]

        for register in self.payload_registers:
            lines.append(f"- p{register.index}: {register.name} ({register.encoding})")

        lines.extend(["", "Launch Params", "-------------"])
        for param in self.launch_params:
            lines.append(f"- {param.name}: {param.c_type} [{param.role}]")

        lines.extend(["", "Buffers", "-------"])
        for spec in self.buffers:
            lines.append(f"- {spec.name}: {spec.element} [{spec.role}]")

        lines.extend(["", "Ray Spec", "--------"])
        lines.append(f"- origin    : {self.ray_spec.origin}")
        lines.append(f"- direction : {self.ray_spec.direction}")
        lines.append(f"- t-range   : [{self.ray_spec.tmin}, {self.ray_spec.tmax}]")
        lines.append(f"- note      : {self.ray_spec.description}")

        lines.extend(["", "Host Steps", "----------"])
        for index, step in enumerate(self.host_steps, start=1):
            lines.append(f"{index}. {step}")

        lines.extend(["", "Device Programs", "---------------"])
        for name in self.device_programs:
            lines.append(f"- {name}")

        return "\n".join(lines)


@dataclass(frozen=True)
class CompiledKernel:
    name: str
    backend: str
    precision: str
    inputs: tuple[GeometryInput, ...]
    candidates: CandidateSet | None
    refine_op: RefineOp | None
    emit_op: EmitOp | None
    lowering_plan: tuple[str, ...] = field(default_factory=tuple)

    def format(self) -> str:
        lines = [
            "Compiled RT Kernel",
            "------------------",
            f"name      : {self.name}",
            f"backend   : {self.backend}",
            f"precision : {self.precision}",
            "inputs    :",
        ]

        for item in self.inputs:
            role_text = item.role if item.role is not None else "unspecified"
            lines.append(f"  - {item.name}: {item.geometry.name} [{item.layout.name}, role={role_text}]")

        if self.candidates is not None:
            lines.append(
                "candidates: "
                f"{self.candidates.left.name} x {self.candidates.right.name} "
                f"via accel={self.candidates.accel}"
            )

        if self.refine_op is not None:
            lines.append(
                "refine    : "
                f"{self.refine_op.predicate.name} "
                f"{self.refine_op.predicate.options}"
            )

        if self.emit_op is not None:
            lines.append(f"emit      : {', '.join(self.emit_op.fields)}")

        lines.extend(["", "Lowering Plan", "-------------"])
        for index, step in enumerate(self.lowering_plan, start=1):
            lines.append(f"{index}. {step}")

        return "\n".join(lines)


# Legacy compatibility alias for the current v0.1 RayJoin slice.
RayJoinPlan = RTExecutionPlan
