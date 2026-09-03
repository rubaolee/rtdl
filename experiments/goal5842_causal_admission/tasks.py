"""Three frozen public-route tasks for Goal5842.

The relation and triangle tasks reuse the exact Goal5798 inputs.  The sphere
task is a deterministic one-hit-per-query workload for the post-freeze public
generic lifecycle.  This module contains no timer and performs no GPU action.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from experiments.goal5798_premeasurement.workload import (
    digest,
    relation_workload,
    triangle_workload,
)
from rtdsl.v4 import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    compile_protocol_program,
    standard_protocol_physical_plan,
)
from rtdsl.v4_family_route_adapters import (
    DeclarativeFamilyRouteV1,
    bounded_relation_family_route,
    triangle_reduction_family_route,
)
from rtdsl.v4_public_builtin_sphere import MotionSegmentBatch
from rtdsl.v4_public_sphere_any_hit_count import SphereAnyHitCountStaticInput
from rtdsl.v4_sphere_any_hit_count_family_route import (
    sphere_any_hit_count_family_route,
)
from rtdsl.v4_sphere_any_hit_count_prepared_runtime import (
    sphere_any_hit_count_output,
)

from .contracts import RELATION_TASK, SPHERE_TASK, TRIANGLE_TASK

# Sphere has no provider-performance row in Goal5842.  This fixture exists to
# witness a third admitted topology and its exact CHECK_ON/CHECK_OFF identity.
# The public runtime deliberately checks every query/sphere numeric pair, so a
# 16K-square fixture would spend hours in untimed exact-rational validation
# without strengthening the causal admission estimand.
SPHERE_SIZE = 1_024
PROOF_KIND = "external_machine_checked_order_independence_v1"


@dataclass(frozen=True, slots=True)
class Goal5842TaskInput:
    task_id: str
    static_input: object
    batch: object
    expected_output: object
    input_sha256: str
    route_factory: Callable[[], DeclarativeFamilyRouteV1]
    provider_fixture: object | None


def _proof(protocol: object, label: str) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=hashlib.sha256(
            f"rtdl.goal5842.proof::{label}".encode("ascii")
        ).hexdigest(),
        proof_kind=PROOF_KIND,
    )


def _relation_task() -> Goal5842TaskInput:
    raw = relation_workload()
    protocol = BoundedRelationProtocol(
        capacity=int(raw["capacity"]),
        minimum_overlap_f32=float(raw["minimum_overlap"]),
    )
    static_input = BoundedRelationStaticInput(
        tuple(tuple(row) for row in raw["indexed"])
    )
    expected = tuple(tuple(row) for row in raw["expected_rows"])
    batch = BoundedRelationBatch(
        tuple(tuple(row) for row in raw["sources"]),
        expected_rows=expected,
    )
    return Goal5842TaskInput(
        RELATION_TASK,
        static_input,
        batch,
        expected,
        digest(
            {
                "indexed": raw["indexed"],
                "sources": raw["sources"],
                "capacity": raw["capacity"],
                "minimum_overlap": raw["minimum_overlap"],
            }
        ),
        lambda: bounded_relation_family_route(
            protocol, _proof(protocol, "bounded_relation")
        ),
        raw,
    )


def _triangle_task() -> Goal5842TaskInput:
    raw = triangle_workload()
    protocol = TriangleReductionProtocol(TriangleReductionMode.WEIGHTED_HIT_COUNT)
    vertices = tuple(tuple(row) for row in raw["vertices"])
    triangles = tuple(
        (index, index + 1, index + 2) for index in range(0, len(vertices), 3)
    )
    static_input = TriangleReductionStaticInput(
        vertices=vertices,
        triangles=triangles,
        primitive_metadata={},
        event_capacity=len(raw["expected_per_ray"]),
    )
    queries = tuple(
        (tuple(origin), tuple(direction), float(raw["tmax"]))
        for origin, direction in raw["rays"]
    )
    weights = tuple(int(value) for value in raw["weights"])
    batch = TriangleReductionBatch(
        queries=queries,
        query_metadata={"query.weight": weights},
    )
    expected = {
        "weighted_sum": int(raw["expected_weighted_sum"]),
        "per_ray": tuple(int(value) for value in raw["expected_per_ray"]),
    }
    return Goal5842TaskInput(
        TRIANGLE_TASK,
        static_input,
        batch,
        expected,
        digest(
            {
                "vertices": raw["vertices"],
                "rays": raw["rays"],
                "weights": raw["weights"],
                "tmin": raw["tmin"],
                "tmax": raw["tmax"],
            }
        ),
        lambda: triangle_reduction_family_route(
            protocol, _proof(protocol, "triangle_weighted")
        ),
        raw,
    )


def sphere_workload() -> dict[str, object]:
    centers = tuple((float(4 * index), 0.0, 0.0) for index in range(SPHERE_SIZE))
    radii = (0.5,) * SPHERE_SIZE
    queries = tuple(
        ((float(4 * index), 0.0, -1.0), (float(4 * index), 0.0, 1.0))
        for index in range(SPHERE_SIZE)
    )
    expected_counts = (1,) * SPHERE_SIZE
    return {
        "id": "GOAL5842_SPHERE_1024_ONE_TO_ONE",
        "centers": centers,
        "radii": radii,
        "queries": queries,
        "expected_counts": expected_counts,
    }


def _sphere_task() -> Goal5842TaskInput:
    raw = sphere_workload()
    static_input = SphereAnyHitCountStaticInput(raw["centers"], raw["radii"])
    batch = MotionSegmentBatch(raw["queries"])
    expected = sphere_any_hit_count_output(raw["expected_counts"])
    return Goal5842TaskInput(
        SPHERE_TASK,
        static_input,
        batch,
        expected,
        digest(
            {
                "centers": raw["centers"],
                "radii": raw["radii"],
                "queries": raw["queries"],
            }
        ),
        sphere_any_hit_count_family_route,
        None,
    )


def build_task(task_id: str) -> Goal5842TaskInput:
    factories = {
        RELATION_TASK: _relation_task,
        TRIANGLE_TASK: _triangle_task,
        SPHERE_TASK: _sphere_task,
    }
    try:
        factory = factories[task_id]
    except KeyError as exc:
        raise ValueError(f"unsupported Goal5842 task: {task_id}") from exc
    return factory()


def build_triangle_auxiliary_program():
    """Build the fixed-protocol owner used only for untimed full-output checking."""

    protocol = TriangleReductionProtocol(TriangleReductionMode.WEIGHTED_HIT_COUNT)
    return compile_protocol_program(
        protocol,
        physical_plan=standard_protocol_physical_plan(protocol),
        any_hit_proof=_proof(protocol, "triangle_weighted"),
    )


def program_signature(program: object) -> dict[str, str]:
    plan = program.plan
    artifacts = program.artifacts
    projection = program.provider_projection
    descriptor = program._descriptor
    return {
        "plan_sha256": plan.plan_sha256,
        "artifacts_sha256": artifacts.bundle_sha256,
        "provider_projection_sha256": projection.projection_sha256,
        "provider_descriptor_sha256": descriptor.descriptor_sha256,
    }


def checker_off_program(route: DeclarativeFamilyRouteV1):
    """Construct the experiment-only unchecked counterfactual.

    This intentionally reaches a private construction token.  It must remain
    confined to this experiment and must never be exported by RTDL.  The
    caller must compare all identities with the normal admitted capability.
    """

    from rtdsl import v4_generic_family_lifecycle as core

    descriptor = route.provider.descriptor
    projection = route.provider.project(route.plan, route.artifacts)
    return core.VerifiedGenericFamilyProgram(
        route.plan,
        route.provider,
        projection,
        route.artifacts,
        descriptor,
        _token=core._CONSTRUCTION_TOKEN,
    )


__all__ = [
    "PROOF_KIND",
    "SPHERE_SIZE",
    "Goal5842TaskInput",
    "build_task",
    "build_triangle_auxiliary_program",
    "checker_off_program",
    "program_signature",
    "sphere_workload",
]
