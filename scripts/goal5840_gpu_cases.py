"""Deterministic mode cases for Goal5840 target-evidence capture."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from case_studies.goal5838_selected_sphere_any_hit_count.fixture import (
    selected_exam_fixture,
)
from case_studies.goal5838_selected_sphere_any_hit_count.sphere_any_hit_count_oracle import (
    count_batch,
)
from rtdsl.v4_callback_lifecycle import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    standard_protocol_physical_plan,
)
from rtdsl.v4_family_route_adapters import (
    bounded_relation_family_route,
    triangle_reduction_family_route,
)
from rtdsl.v4_sphere_any_hit_count import (
    MotionSegmentBatch,
    SphereAnyHitCountStaticInput,
    sphere_any_hit_count_family_route,
)
from rtdsl.v4_sphere_any_hit_count_prepared_runtime import (
    sphere_any_hit_count_output,
)


ROOT = Path(__file__).resolve().parents[1]
BOUNDED_ROUTE = "stable::bounded_relation::canonical_bounded_pair_collection"
TRIANGLE_ROUTE = "stable::triangle_reduction::checked_u64_reduction"
SPHERE_ROUTE = (
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query"
)
PROOF_SOURCE_BY_ROUTE = {
    BOUNDED_ROUTE: "scripts/goal5760_m2_consumer_fixtures.py",
    TRIANGLE_ROUTE: "scripts/goal5758_m1_independent_oracles.py",
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _proof(protocol: object, route_id: str) -> AnyHitProtocolProof:
    physical = standard_protocol_physical_plan(protocol)
    source_path = PROOF_SOURCE_BY_ROUTE[route_id]
    source_sha256 = hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest()
    proof_sha256 = hashlib.sha256(_canonical({
        "schema": "rtdl.goal5840.inherited_order_independence_proof_binding.v1",
        "route_id": route_id,
        "protocol": protocol.to_dict(),
        "physical_plan_sha256": physical.plan_sha256,
        "callback_ir_sha256": physical.callback_ir_sha256,
        "effect_digest": physical.effect_digest,
        "proof_source": source_path,
        "proof_source_sha256": source_sha256,
        "statement": (
            "reuse_prior_machine_checked_order_independence_evidence_only;"
            "goal5840_does_not_reprove_application_correctness"
        ),
    })).hexdigest()
    return AnyHitProtocolProof(
        physical.callback_ir_sha256,
        physical.effect_digest,
        proof_sha256,
        "external_machine_checked_order_independence_v1",
    )


def _bounded_expected(sources, indexed) -> tuple[tuple[int, int], ...]:
    rows = []
    for source in sources:
        for item in indexed:
            if (
                item[0] <= source[2]
                and item[2] >= source[0]
                and item[1] <= source[3]
                and item[3] >= source[1]
            ):
                rows.append((int(source[4]), int(item[4])))
    return tuple(sorted(set(rows)))


def _triangle_geometry(count: int):
    vertices = []
    triangles = []
    for index in range(count):
        z = float(index + 1)
        base = len(vertices)
        vertices.extend((
            (-0.75, -0.75, z),
            (0.75, -0.75, z),
            (0.0, 0.75, z),
        ))
        triangles.append((base, base + 1, base + 2))
    return tuple(vertices), tuple(triangles)


@dataclass(frozen=True)
class Goal5840ModeCase:
    route_id: str
    mode: str
    route: Any
    static_input: object
    batch: object
    expected_output: object
    fixture_document: dict[str, object]
    target_kind: str

    @property
    def key(self) -> str:
        return f"{self.route_id}::{self.mode}"


def goal5840_mode_cases() -> tuple[Goal5840ModeCase, ...]:
    indexed = (
        (0.0, 0.0, 2.0, 2.0, 10),
        (4.0, 4.0, 6.0, 6.0, 20),
        (2.0, 0.0, 3.0, 1.0, 30),
        (12.0, 12.0, 13.0, 13.0, 40),
    )
    sources = (
        (1.0, 1.0, 2.5, 2.5, 100),
        (5.0, 5.0, 7.0, 7.0, 200),
        (20.0, 20.0, 21.0, 21.0, 300),
    )
    bounded_protocol = BoundedRelationProtocol(32, 0.0)
    bounded_expected = _bounded_expected(sources, indexed)
    bounded = Goal5840ModeCase(
        BOUNDED_ROUTE,
        "capacity_fail_closed_collection",
        bounded_relation_family_route(
            bounded_protocol, _proof(bounded_protocol, BOUNDED_ROUTE)
        ),
        BoundedRelationStaticInput(indexed),
        BoundedRelationBatch(sources, bounded_expected),
        bounded_expected,
        {
            "indexed_boxes": indexed,
            "source_boxes": sources,
            "capacity": bounded_protocol.capacity,
            "minimum_overlap_f32": bounded_protocol.minimum_overlap_f32,
        },
        "stable",
    )

    vertices, triangles = _triangle_geometry(5)
    queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 10.0),)
    triangle_cases = []
    for mode, weight, expected in (
        (TriangleReductionMode.ALL_HIT_COUNT, None, 5),
        (TriangleReductionMode.WEIGHTED_HIT_COUNT, 7, 35),
    ):
        protocol = TriangleReductionProtocol(mode)
        query_metadata = {} if weight is None else {"query.weight": (weight,)}
        triangle_cases.append(Goal5840ModeCase(
            TRIANGLE_ROUTE,
            mode.value,
            triangle_reduction_family_route(
                protocol, _proof(protocol, TRIANGLE_ROUTE)
            ),
            TriangleReductionStaticInput(vertices, triangles, {}, 1),
            TriangleReductionBatch(queries, query_metadata),
            expected,
            {
                "vertices": vertices,
                "triangles": triangles,
                "queries": queries,
                "query_metadata": query_metadata,
                "expected_hit_count": len(triangles),
            },
            "stable",
        ))

    sphere_fixture = selected_exam_fixture()
    sphere_counts = count_batch(
        sphere_fixture["queries"],
        sphere_fixture["centers"],
        sphere_fixture["radii"],
    )
    sphere = Goal5840ModeCase(
        SPHERE_ROUTE,
        "accept_every_hit_and_continue",
        sphere_any_hit_count_family_route(),
        SphereAnyHitCountStaticInput(
            sphere_fixture["centers"], sphere_fixture["radii"]
        ),
        MotionSegmentBatch(sphere_fixture["queries"]),
        sphere_any_hit_count_output(sphere_counts),
        {
            "centers": sphere_fixture["centers"],
            "radii": sphere_fixture["radii"],
            "queries": sphere_fixture["queries"],
            "case_names": sphere_fixture["case_names"],
        },
        "sphere",
    )
    return (bounded, *triangle_cases, sphere)


__all__ = [
    "BOUNDED_ROUTE",
    "Goal5840ModeCase",
    "SPHERE_ROUTE",
    "TRIANGLE_ROUTE",
    "goal5840_mode_cases",
]
