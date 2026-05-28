"""Bounded contact-witness app over generic COLLECT_K_BOUNDED rows."""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


BENCHMARK_APP = "bounded_collision_witness_contact_manifold"
PRIMITIVE = "COLLECT_K_BOUNDED"
DISCOVERY_PRIMITIVE = "AABB_INDEX_QUERY_2D"
V2_4_BOUNDED_WITNESS_PRIMITIVE = "aabb_index_2d_bounded_i64_rows"
ROW_WIDTH = 3
ROW_SCHEMA = ("query_group_id", "query_triangle_id", "scene_triangle_id")
EPSILON = 1.0e-9
CPP_BASELINE_SOURCE = Path(__file__).with_name("cpp_contact_witness_baseline.cpp")
CPP_BASELINE_BINARY = ROOT / "build" / "goal2621_contact_witness_cpp_baseline"


Point2D = tuple[float, float]
WitnessRow = tuple[int, int, int]


@dataclass(frozen=True)
class Triangle2D:
    triangle_id: int
    vertices: tuple[Point2D, Point2D, Point2D]
    query_group_id: int | None = None


@dataclass(frozen=True)
class CollisionWitnessFixture:
    name: str
    scene_triangles: tuple[Triangle2D, ...]
    query_triangles: tuple[Triangle2D, ...]
    expected_witness_rows: tuple[WitnessRow, ...]
    contract_note: str


def scope_payload() -> dict[str, Any]:
    return {
        "app": BENCHMARK_APP,
        "status": "promoted_benchmark_internal_no_public_speedup_claim",
        "primitive_under_test": PRIMITIVE,
        "candidate_discovery_primitive": DISCOVERY_PRIMITIVE,
        "primitive_behavior": "bounded generic int64 witness row collection",
        "row_width": ROW_WIDTH,
        "row_schema": ROW_SCHEMA,
        "input_scene_contract": (
            "static scene triangles plus query triangles grouped by app-owned query_group_id"
        ),
        "query_geometry_contract": (
            "the app may call these contact/collision witnesses, but RTDL receives only "
            "candidate-id rows with no collision vocabulary"
        ),
        "overflow_behavior": {
            "policy": "fail_closed_before_result_materialization",
            "partial_rows_returned_on_overflow": False,
            "silent_truncation_allowed": False,
        },
        "correctness_oracle": (
            "deterministic Python exact 2-D triangle intersection; optimized path first uses "
            "generic AABB_INDEX_QUERY_2D broadphase rows and then exact Python refinement"
        ),
        "engine_boundary": {
            "native_collision_logic_allowed": False,
            "candidate_discovery_owner": DISCOVERY_PRIMITIVE,
            "contact_manifold_logic_owner": "Python app/reference or partner continuation",
            "engine_primitive_owner": PRIMITIVE,
        },
        "promotion_evidence": (
            "deterministic Python fixtures",
            "generic collect-k fail-closed tests",
            "local Mac Embree parity",
            "RTX A5000 OptiX parity",
            "standalone C++ CPU baseline comparison",
            "generic AABB broadphase row discovery before exact refinement",
            "3-AI follow-up promotion consensus",
        ),
        "promotion_qualification": (
            "no public speedup claim; Linux Embree parity has not been separately "
            "recorded, while Mac Embree and Linux OptiX cover the generic primitive surface"
        ),
    }


def _triangle(
    triangle_id: int,
    vertices: tuple[Point2D, Point2D, Point2D],
    *,
    query_group_id: int | None = None,
) -> Triangle2D:
    return Triangle2D(
        triangle_id=int(triangle_id),
        vertices=tuple((float(x), float(y)) for x, y in vertices),  # type: ignore[arg-type]
        query_group_id=None if query_group_id is None else int(query_group_id),
    )


def tiny_fixture() -> CollisionWitnessFixture:
    scene_triangles = (
        _triangle(0, ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),
        _triangle(1, ((3.0, 0.0), (4.0, 0.0), (3.0, 1.0))),
        _triangle(2, ((0.0, 3.0), (1.0, 3.0), (0.0, 4.0))),
    )
    query_triangles = (
        _triangle(10, ((0.10, 0.10), (0.80, 0.10), (0.10, 0.80)), query_group_id=0),
        _triangle(11, ((3.20, 0.20), (3.70, 0.20), (3.20, 0.70)), query_group_id=0),
        _triangle(20, ((5.00, 5.00), (6.00, 5.00), (5.00, 6.00)), query_group_id=1),
        _triangle(30, ((0.20, 3.20), (0.70, 3.20), (0.20, 3.70)), query_group_id=2),
    )
    return CollisionWitnessFixture(
        name="tiny",
        scene_triangles=scene_triangles,
        query_triangles=query_triangles,
        expected_witness_rows=((0, 10, 0), (0, 11, 1), (2, 30, 2)),
        contract_note="small deterministic fixture with three exact witness rows",
    )


def grid_fixture(*, cell_count: int) -> CollisionWitnessFixture:
    if cell_count <= 0:
        raise ValueError("grid fixture cell_count must be positive")
    scene_triangles: list[Triangle2D] = []
    query_triangles: list[Triangle2D] = []
    expected_rows: list[WitnessRow] = []
    for index in range(cell_count):
        x0 = float(index * 3)
        scene_id = 10_000 + index
        query_id = 20_000 + index
        group_id = index
        scene_triangles.append(
            _triangle(scene_id, ((x0, 0.0), (x0 + 1.0, 0.0), (x0, 1.0)))
        )
        query_triangles.append(
            _triangle(
                query_id,
                ((x0 + 0.10, 0.10), (x0 + 0.80, 0.10), (x0 + 0.10, 0.80)),
                query_group_id=group_id,
            )
        )
        expected_rows.append((group_id, query_id, scene_id))
    return CollisionWitnessFixture(
        name=f"grid_{cell_count}",
        scene_triangles=tuple(scene_triangles),
        query_triangles=tuple(query_triangles),
        expected_witness_rows=tuple(expected_rows),
        contract_note="scaled deterministic one-witness-per-cell fixture",
    )


def build_fixture(dataset: str, *, grid_count: int = 64) -> CollisionWitnessFixture:
    normalized = dataset.strip().lower()
    if normalized in {"tiny", "overflow"}:
        # Overflow is a capacity condition over the tiny exact fixture, not a separate scene.
        return tiny_fixture()
    if normalized == "grid":
        return grid_fixture(cell_count=grid_count)
    raise ValueError(f"unknown contact witness dataset: {dataset}")


def default_aabb_resolution(*, grid_count: int) -> int:
    """Choose a bounded grid resolution that avoids skinny-scene cell explosion."""

    return min(256, max(16, int(math.sqrt(max(1, int(grid_count))))))


def _cross(origin: Point2D, a: Point2D, b: Point2D) -> float:
    return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])


def _on_segment(a: Point2D, b: Point2D, p: Point2D) -> bool:
    if abs(_cross(a, b, p)) > EPSILON:
        return False
    return (
        min(a[0], b[0]) - EPSILON <= p[0] <= max(a[0], b[0]) + EPSILON
        and min(a[1], b[1]) - EPSILON <= p[1] <= max(a[1], b[1]) + EPSILON
    )


def _segment_intersects(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    ab_c = _cross(a, b, c)
    ab_d = _cross(a, b, d)
    cd_a = _cross(c, d, a)
    cd_b = _cross(c, d, b)
    if (
        (ab_c > EPSILON and ab_d < -EPSILON or ab_c < -EPSILON and ab_d > EPSILON)
        and (cd_a > EPSILON and cd_b < -EPSILON or cd_a < -EPSILON and cd_b > EPSILON)
    ):
        return True
    return (
        _on_segment(a, b, c)
        or _on_segment(a, b, d)
        or _on_segment(c, d, a)
        or _on_segment(c, d, b)
    )


def _point_in_triangle(point: Point2D, triangle: tuple[Point2D, Point2D, Point2D]) -> bool:
    a, b, c = triangle
    c1 = _cross(a, b, point)
    c2 = _cross(b, c, point)
    c3 = _cross(c, a, point)
    has_negative = c1 < -EPSILON or c2 < -EPSILON or c3 < -EPSILON
    has_positive = c1 > EPSILON or c2 > EPSILON or c3 > EPSILON
    return not (has_negative and has_positive)


def triangles_intersect(
    left: tuple[Point2D, Point2D, Point2D],
    right: tuple[Point2D, Point2D, Point2D],
) -> bool:
    if any(_point_in_triangle(point, right) for point in left):
        return True
    if any(_point_in_triangle(point, left) for point in right):
        return True
    left_edges = ((left[0], left[1]), (left[1], left[2]), (left[2], left[0]))
    right_edges = ((right[0], right[1]), (right[1], right[2]), (right[2], right[0]))
    return any(_segment_intersects(a, b, c, d) for a, b in left_edges for c, d in right_edges)


def reference_witness_rows(fixture: CollisionWitnessFixture) -> tuple[WitnessRow, ...]:
    rows: set[WitnessRow] = set()
    for query in fixture.query_triangles:
        if query.query_group_id is None:
            raise ValueError("query triangles must carry query_group_id")
        for scene in fixture.scene_triangles:
            if triangles_intersect(query.vertices, scene.vertices):
                rows.add((query.query_group_id, query.triangle_id, scene.triangle_id))
    return tuple(sorted(rows))


def _triangle_aabb(triangle: Triangle2D) -> tuple[float, float, float, float]:
    xs = [point[0] for point in triangle.vertices]
    ys = [point[1] for point in triangle.vertices]
    return (min(xs), min(ys), max(xs), max(ys))


def aabb_broadphase_witness_rows(
    fixture: CollisionWitnessFixture,
    *,
    resolution: int = 64,
    discovery_backend: str = "cpu",
    row_capacity: int | None = None,
    warmup_count: int = 0,
    repeat_count: int = 1,
) -> dict[str, Any]:
    """Discover candidate triangle pairs with generic AABB rows, then refine exactly."""

    scene_by_id = {triangle.triangle_id: triangle for triangle in fixture.scene_triangles}
    query_by_id = {triangle.triangle_id: triangle for triangle in fixture.query_triangles}
    normalized_discovery_backend = discovery_backend.strip().lower().replace("-", "_")
    if normalized_discovery_backend in {"python", "cpu_python_reference"}:
        normalized_discovery_backend = "cpu"
    if normalized_discovery_backend in {"nvidia_rt", "cuda_optix"}:
        normalized_discovery_backend = "optix"
    if normalized_discovery_backend not in {"cpu", "embree", "optix"}:
        raise ValueError("discovery_backend must be cpu, embree, or optix")
    if warmup_count < 0:
        raise ValueError("warmup_count must be non-negative")
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive")
    resolved_row_capacity = row_capacity
    if normalized_discovery_backend == "optix" and resolved_row_capacity is None:
        resolved_row_capacity = max(
            1,
            2 * len(fixture.scene_triangles),
            2 * len(fixture.query_triangles),
        )
    indexed_boxes = tuple(_triangle_aabb(triangle) for triangle in fixture.scene_triangles)
    query_boxes = tuple(_triangle_aabb(triangle) for triangle in fixture.query_triangles)
    indexed_ids = tuple(triangle.triangle_id for triangle in fixture.scene_triangles)
    query_ids = tuple(triangle.triangle_id for triangle in fixture.query_triangles)
    broadphase_started = time.perf_counter()

    if normalized_discovery_backend in {"embree", "optix"} and (warmup_count > 0 or repeat_count > 1):
        prepare_started = time.perf_counter()
        prepared = rt.prepare_aabb_index_2d(
            indexed_boxes,
            indexed_ids=indexed_ids,
            resolution=resolution,
            backend=normalized_discovery_backend,
        )
        prepare_sec = time.perf_counter() - prepare_started
        query_times: list[float] = []
        rows: tuple[tuple[int, int], ...] | None = None
        try:
            for iteration in range(warmup_count + repeat_count):
                query_started = time.perf_counter()
                if normalized_discovery_backend == "optix":
                    emitted_rows = prepared.intersection_rows(
                        query_boxes,
                        query_ids,
                        row_capacity=resolved_row_capacity,
                    )
                else:
                    emitted_rows = prepared.intersection_rows(query_boxes, query_ids)
                query_sec = time.perf_counter() - query_started
                if iteration >= warmup_count:
                    query_times.append(query_sec)
                    rows = emitted_rows
        finally:
            close = getattr(prepared, "close", None)
            if callable(close):
                close()
        if rows is None:
            raise RuntimeError("prepared AABB discovery did not run a measured query")
        query_median_sec = statistics.median(query_times)
        broadphase = {
            "primitive": DISCOVERY_PRIMITIVE,
            "contract": "generic_aabb_intersection_pair_rows_2d",
            "backend": normalized_discovery_backend,
            "prepared": True,
            "operation": "range_intersection_rows",
            "row_schema": ("query_id", "indexed_id"),
            "candidate_id_rows": tuple(sorted(rows)),
            "valid_count": len(rows),
            "indexed_box_count": len(indexed_boxes),
            "query_box_count": len(query_boxes),
            "candidate_checks": None,
            "all_pairs_count": len(indexed_boxes) * len(query_boxes),
            "candidate_checks_avoided": None,
            "pruning_ratio": None,
            "row_capacity": resolved_row_capacity,
            "complete_candidate_coverage": True,
            "run_phases": {
                "prepare_aabb_index_2d_sec": prepare_sec,
                "emit_aabb_intersection_pair_rows_2d_median_sec": query_median_sec,
                "emit_aabb_intersection_pair_rows_2d_min_sec": min(query_times),
                "emit_aabb_intersection_pair_rows_2d_max_sec": max(query_times),
            },
            "discovery_warmup_count": int(warmup_count),
            "discovery_repeat_count": int(repeat_count),
            "rt_core_accelerated": normalized_discovery_backend == "optix",
            "native_engine_customization": False,
            "claim_boundary": (
                "Generic prepared AABB_INDEX_QUERY_2D broadphase row output only; exact app "
                "semantics and final witness interpretation remain outside the engine."
            ),
        }
    else:
        broadphase = rt.aabb_intersection_pair_rows_2d(
            indexed_boxes,
            query_boxes,
            indexed_ids=indexed_ids,
            query_ids=query_ids,
            resolution=resolution,
            backend=normalized_discovery_backend,
            row_capacity=resolved_row_capacity,
        )
    broadphase_elapsed_sec = time.perf_counter() - broadphase_started
    broadphase_run_phases = dict(broadphase.get("run_phases") or {})
    if "emit_aabb_intersection_pair_rows_2d_median_sec" in broadphase_run_phases:
        broadphase_metric_sec = float(
            broadphase_run_phases["emit_aabb_intersection_pair_rows_2d_median_sec"]
        )
    else:
        broadphase_metric_sec = broadphase_elapsed_sec

    refine_started = time.perf_counter()
    rows: set[WitnessRow] = set()
    exact_refinement_checks = 0
    for query_id, scene_id in broadphase["candidate_id_rows"]:
        query = query_by_id[int(query_id)]
        scene = scene_by_id[int(scene_id)]
        if query.query_group_id is None:
            raise ValueError("query triangles must carry query_group_id")
        exact_refinement_checks += 1
        if triangles_intersect(query.vertices, scene.vertices):
            rows.add((query.query_group_id, query.triangle_id, scene.triangle_id))
    refine_elapsed_sec = time.perf_counter() - refine_started

    all_pairs_count = len(fixture.scene_triangles) * len(fixture.query_triangles)
    return {
        "candidate_discovery_primitive": DISCOVERY_PRIMITIVE,
        "candidate_discovery_contract": "generic_aabb_intersection_pair_rows_2d",
        "candidate_discovery_backend": broadphase["backend"],
        "aabb_candidate_pairs": broadphase["candidate_id_rows"],
        "aabb_candidate_pair_count": broadphase["valid_count"],
        "candidate_id_rows": tuple(sorted(rows)),
        "valid_count": len(rows),
        "all_pairs_count": all_pairs_count,
        "aabb_candidate_checks": broadphase["candidate_checks"],
        "aabb_candidate_checks_avoided": broadphase["candidate_checks_avoided"],
        "aabb_pruning_ratio": broadphase["pruning_ratio"],
        "discovery_row_capacity": resolved_row_capacity,
        "discovery_warmup_count": int(warmup_count),
        "discovery_repeat_count": int(repeat_count),
        "exact_refinement_checks": exact_refinement_checks,
        "exact_refinement_checks_avoided": max(0, all_pairs_count - exact_refinement_checks),
        "resolution": int(resolution),
        "run_phases": broadphase_run_phases
        | {
            "generic_aabb_broadphase_sec": broadphase_metric_sec,
            "generic_aabb_broadphase_wall_sec": broadphase_elapsed_sec,
            "python_exact_refinement_sec": refine_elapsed_sec,
        },
        "native_engine_customization": False,
        "complete_candidate_coverage": True,
        "claim_boundary": (
            "AABB candidate discovery is generic RTDL broadphase behavior. The final "
            "triangle-intersection refinement and contact interpretation remain app-owned; "
            "no collision-specific native engine logic or public speedup claim is made."
        ),
    }


def _centroid(vertices: tuple[Point2D, Point2D, Point2D]) -> Point2D:
    return (
        sum(point[0] for point in vertices) / 3.0,
        sum(point[1] for point in vertices) / 3.0,
    )


def app_owned_contact_summaries(
    fixture: CollisionWitnessFixture,
    rows: Iterable[WitnessRow],
) -> tuple[dict[str, Any], ...]:
    query_by_id = {triangle.triangle_id: triangle for triangle in fixture.query_triangles}
    scene_by_id = {triangle.triangle_id: triangle for triangle in fixture.scene_triangles}
    summaries = []
    for group_id, query_id, scene_id in rows:
        query = query_by_id[query_id]
        scene = scene_by_id[scene_id]
        query_centroid = _centroid(query.vertices)
        scene_centroid = _centroid(scene.vertices)
        summaries.append(
            {
                "query_group_id": group_id,
                "query_triangle_id": query_id,
                "scene_triangle_id": scene_id,
                "representative_midpoint": (
                    (query_centroid[0] + scene_centroid[0]) / 2.0,
                    (query_centroid[1] + scene_centroid[1]) / 2.0,
                ),
                "owner": "python_app_contact_summary_not_native_engine",
            }
        )
    return tuple(summaries)


def cpu_reference_payload(*, dataset: str = "tiny", grid_count: int = 64) -> dict[str, Any]:
    fixture = build_fixture(dataset, grid_count=grid_count)
    started = time.perf_counter()
    rows = reference_witness_rows(fixture)
    elapsed_sec = time.perf_counter() - started
    if rows != fixture.expected_witness_rows:
        raise AssertionError(
            f"fixture {fixture.name} expected {fixture.expected_witness_rows}, got {rows}"
        )
    return {
        "app": BENCHMARK_APP,
        "mode": "cpu_reference",
        "dataset": fixture.name,
        "primitive_under_test": PRIMITIVE,
        "row_schema": ROW_SCHEMA,
        "scene_triangle_count": len(fixture.scene_triangles),
        "query_triangle_count": len(fixture.query_triangles),
        "candidate_id_rows": rows,
        "valid_count": len(rows),
        "elapsed_sec": elapsed_sec,
        "correctness_oracle": "deterministic_python_triangle_intersection",
        "contact_summaries": app_owned_contact_summaries(fixture, rows),
        "claim_boundary": (
            "CPU reference establishes exact app-owned contact witnesses; it is not a native "
            "engine primitive or performance claim."
        ),
    }


def collect_k_reference_payload(
    *,
    dataset: str = "tiny",
    witness_capacity: int = 8,
    grid_count: int = 64,
    backend: str = "cpu_python_reference",
) -> dict[str, Any]:
    reference = cpu_reference_payload(dataset=dataset, grid_count=grid_count)
    started = time.perf_counter()
    result = rt.collect_k_bounded_rows(
        reference["candidate_id_rows"],
        k=int(witness_capacity),
        row_width=ROW_WIDTH,
    ) | {
        "backend": backend,
        "benchmark_app": BENCHMARK_APP,
        "row_schema": ROW_SCHEMA,
    }
    validated = rt.validate_collect_k_bounded_result(
        result,
        row_width=ROW_WIDTH,
        backend=backend,
    )
    collect_elapsed_sec = time.perf_counter() - started
    v2_4_session = describe_v2_4_bounded_witness_session(
        backend="cpu",
        candidate_row_count=len(reference["candidate_id_rows"]),
        witness_capacity=int(witness_capacity),
    )
    return {
        "app": BENCHMARK_APP,
        "mode": "collect_k_reference",
        "dataset": reference["dataset"],
        "backend": backend,
        "primitive_under_test": PRIMITIVE,
        "row_schema": ROW_SCHEMA,
        "witness_capacity": int(witness_capacity),
        "candidate_id_rows": validated["candidate_id_rows"],
        "valid_count": validated["valid_count"],
        "overflowed": validated["overflowed"],
        "complete_candidate_coverage": validated["complete_candidate_coverage"],
        "cpu_reference_valid_count": reference["valid_count"],
        "matches_cpu_reference": validated["candidate_id_rows"] == reference["candidate_id_rows"],
        "cpu_reference_elapsed_sec": reference["elapsed_sec"],
        "collect_elapsed_sec": collect_elapsed_sec,
        "v2_4_prepared_session": v2_4_session,
        "engine_boundary": scope_payload()["engine_boundary"],
        "claim_boundary": (
            "This mode exercises only generic COLLECT_K_BOUNDED row collection. Collision/contact "
            "meaning remains Python app metadata outside native engines."
        ),
    }


def aabb_broadphase_collect_k_payload(
    *,
    dataset: str = "tiny",
    witness_capacity: int = 8,
    grid_count: int = 64,
    resolution: int | None = None,
    backend: str = "cpu_python_reference",
    discovery_backend: str = "cpu",
    discovery_row_capacity: int | None = None,
    discovery_warmup_count: int = 0,
    discovery_repeat_count: int = 1,
) -> dict[str, Any]:
    fixture = build_fixture(dataset, grid_count=grid_count)
    resolved_resolution = (
        default_aabb_resolution(grid_count=grid_count)
        if resolution is None
        else int(resolution)
    )
    broadphase = aabb_broadphase_witness_rows(
        fixture,
        resolution=resolved_resolution,
        discovery_backend=discovery_backend,
        row_capacity=discovery_row_capacity,
        warmup_count=discovery_warmup_count,
        repeat_count=discovery_repeat_count,
    )
    reference_rows = fixture.expected_witness_rows
    if broadphase["candidate_id_rows"] != reference_rows:
        raise AssertionError(
            f"generic AABB broadphase/refinement expected {reference_rows}, "
            f"got {broadphase['candidate_id_rows']}"
        )
    started = time.perf_counter()
    result = rt.collect_k_bounded_rows(
        broadphase["candidate_id_rows"],
        k=int(witness_capacity),
        row_width=ROW_WIDTH,
    ) | {
        "backend": backend,
        "benchmark_app": BENCHMARK_APP,
        "row_schema": ROW_SCHEMA,
    }
    validated = rt.validate_collect_k_bounded_result(
        result,
        row_width=ROW_WIDTH,
        backend=backend,
    )
    collect_elapsed_sec = time.perf_counter() - started
    v2_4_session = describe_v2_4_bounded_witness_session(
        backend=normalized_discovery_backend,
        candidate_row_count=len(broadphase["candidate_id_rows"]),
        witness_capacity=int(witness_capacity),
    )
    return {
        "app": BENCHMARK_APP,
        "mode": "aabb_broadphase_collect_k",
        "dataset": fixture.name,
        "backend": backend,
        "primitive_under_test": PRIMITIVE,
        "candidate_discovery_primitive": DISCOVERY_PRIMITIVE,
        "candidate_discovery_contract": broadphase["candidate_discovery_contract"],
        "candidate_discovery_backend": broadphase["candidate_discovery_backend"],
        "row_schema": ROW_SCHEMA,
        "witness_capacity": int(witness_capacity),
        "discovery_row_capacity": broadphase["discovery_row_capacity"],
        "resolution": int(resolved_resolution),
        "resolution_policy": (
            "adaptive_sqrt_capped_16_256" if resolution is None else "explicit"
        ),
        "candidate_id_rows": validated["candidate_id_rows"],
        "valid_count": validated["valid_count"],
        "overflowed": validated["overflowed"],
        "complete_candidate_coverage": validated["complete_candidate_coverage"],
        "matches_cpu_reference": validated["candidate_id_rows"] == reference_rows,
        "aabb_candidate_pair_count": broadphase["aabb_candidate_pair_count"],
        "all_pairs_count": broadphase["all_pairs_count"],
        "aabb_candidate_checks": broadphase["aabb_candidate_checks"],
        "aabb_candidate_checks_avoided": broadphase["aabb_candidate_checks_avoided"],
        "aabb_pruning_ratio": broadphase["aabb_pruning_ratio"],
        "exact_refinement_checks": broadphase["exact_refinement_checks"],
        "exact_refinement_checks_avoided": broadphase["exact_refinement_checks_avoided"],
        "run_phases": broadphase["run_phases"]
        | {"collect_k_bounded_rows_sec": collect_elapsed_sec},
        "v2_4_prepared_session": v2_4_session,
        "engine_boundary": scope_payload()["engine_boundary"],
        "claim_boundary": broadphase["claim_boundary"],
    }


def describe_v2_4_bounded_witness_session(
    *,
    backend: str,
    candidate_row_count: int,
    witness_capacity: int,
    row_width: int = ROW_WIDTH,
) -> dict[str, Any]:
    """Describe bounded witness collection with generic v2.4 buffers.

    The app may interpret rows as contact witnesses, but the protocol surface is
    only generic int64 candidate rows plus a bounded int64 output buffer.
    """

    normalized_backend = backend.strip().lower().replace("-", "_")
    if normalized_backend in {"python", "cpu_python_reference"}:
        normalized_backend = "cpu"
    if normalized_backend not in {"cpu", "embree", "optix"}:
        raise ValueError("v2.4 bounded witness descriptor supports cpu, embree, or optix")
    native_symbols = ()
    if normalized_backend in {"embree", "optix"}:
        native_symbols = (f"rtdl_{normalized_backend}_collect_k_bounded_i64",)
    session = rt.RtdlPreparedSessionDescriptor(
        session_id=(
            f"generic_bounded_i64_rows_{normalized_backend}_"
            f"{int(candidate_row_count)}x{int(witness_capacity)}"
        ),
        backend=normalized_backend,
        primitive=V2_4_BOUNDED_WITNESS_PRIMITIVE,
        input_buffers=(
            rt.RtdlBufferDescriptor(
                name="candidate_id_rows",
                dtype="int64",
                shape=(int(candidate_row_count), int(row_width)),
                device_type="cpu",
                access_mode="read",
                source_protocol="rtdl_generic_i64_rows",
                lifetime="session_retained",
            ),
        ),
        output_buffers=(
            rt.RtdlBufferDescriptor(
                name="bounded_witness_rows",
                dtype="int64",
                shape=(int(witness_capacity), int(row_width)),
                device_type="cpu",
                access_mode="write",
                source_protocol="rtdl_generic_i64_rows",
                lifetime="session_retained",
                mutability="mutable",
            ),
            rt.RtdlBufferDescriptor(
                name="valid_count",
                dtype="uint64",
                shape=(1,),
                device_type="cpu",
                access_mode="write",
                source_protocol="rtdl_scalar_status",
                lifetime="session_retained",
                mutability="mutable",
            ),
        ),
        reusable_scene=True,
        reusable_query_buffers=True,
        reusable_output_buffers=True,
        phase_contract="bounded_witness_collection",
        native_symbols=native_symbols,
    )
    return {
        **session.to_metadata(),
        "v2_4_protocol_version": rt.V2_4_PARTNER_PROTOCOL_VERSION,
        "row_schema": ROW_SCHEMA,
        "overflow_policy": "fail_closed_no_partial_rows",
        "app_owned_interpretation": (
            "Rows may represent contact witnesses in this benchmark, but RTDL sees only "
            "bounded int64 rows and valid_count."
        ),
        "same_phase_contract_as_basis_required": True,
        "descriptor_only": True,
    }


def _default_library_path(backend: str) -> Path | None:
    normalized = backend.strip().lower()
    env_var = "RTDL_EMBREE_LIBRARY" if normalized == "embree" else "RTDL_OPTIX_LIBRARY"
    if os.environ.get(env_var):
        return Path(os.environ[env_var])
    candidates = (
        (ROOT / "build" / "librtdl_embree.dylib", ROOT / "build" / "librtdl_embree.so")
        if normalized == "embree"
        else (ROOT / "build" / "librtdl_optix.dylib", ROOT / "build" / "librtdl_optix.so")
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def native_collect_k_payload(
    *,
    dataset: str = "tiny",
    witness_capacity: int = 8,
    grid_count: int = 64,
    backend: str = "embree",
    library_path: str | None = None,
) -> dict[str, Any]:
    normalized_backend = backend.strip().lower()
    if normalized_backend not in {"embree", "optix"}:
        raise ValueError("native collect backend must be embree or optix")
    resolved_library = Path(library_path) if library_path else _default_library_path(normalized_backend)
    if resolved_library is None:
        raise RuntimeError(
            f"no {normalized_backend} library found; set RTDL_{normalized_backend.upper()}_LIBRARY"
        )
    reference = cpu_reference_payload(dataset=dataset, grid_count=grid_count)
    library = ctypes.CDLL(str(resolved_library))
    symbol_name = f"rtdl_{normalized_backend}_collect_k_bounded_i64"
    started = time.perf_counter()
    native = rt.collect_native_i64_rows_with_backend_symbol(
        reference["candidate_id_rows"],
        capacity=int(witness_capacity),
        row_width=ROW_WIDTH,
        backend=normalized_backend,
        library=library,
        symbol_name=symbol_name,
        candidate_source_symbol="python_exact_triangle_intersection_oracle",
    )
    native_elapsed_sec = time.perf_counter() - started
    v2_4_session = describe_v2_4_bounded_witness_session(
        backend=normalized_backend,
        candidate_row_count=len(reference["candidate_id_rows"]),
        witness_capacity=int(witness_capacity),
    )
    return {
        "app": BENCHMARK_APP,
        "mode": "native_collect_k",
        "dataset": reference["dataset"],
        "backend": normalized_backend,
        "library_path": str(resolved_library),
        "native_generic_symbol": native["native_generic_symbol"],
        "primitive_under_test": PRIMITIVE,
        "row_schema": ROW_SCHEMA,
        "witness_capacity": int(witness_capacity),
        "candidate_id_rows": native["candidate_id_rows"],
        "valid_count": native["valid_count"],
        "overflowed": native["overflowed"],
        "complete_candidate_coverage": native["complete_candidate_coverage"],
        "matches_cpu_reference": native["candidate_id_rows"] == reference["candidate_id_rows"],
        "cpu_reference_valid_count": reference["valid_count"],
        "cpu_reference_elapsed_sec": reference["elapsed_sec"],
        "native_collect_elapsed_sec": native_elapsed_sec,
        "v2_4_prepared_session": v2_4_session,
        "engine_boundary": scope_payload()["engine_boundary"],
        "claim_boundary": (
            "Native mode validates only the generic app-name-free COLLECT_K_BOUNDED i64 "
            "collector over Python oracle rows; it is not native collision/contact logic."
        ),
    }


def baseline_comparison_payload(
    *,
    dataset: str = "grid",
    grid_count: int = 512,
    witness_capacity: int = 512,
    repeat_count: int = 5,
) -> dict[str, Any]:
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive")
    cpu_times = []
    collect_times = []
    broadphase_times = []
    last_reference: dict[str, Any] | None = None
    last_collect: dict[str, Any] | None = None
    last_broadphase: dict[str, Any] | None = None
    for _ in range(repeat_count):
        last_reference = cpu_reference_payload(dataset=dataset, grid_count=grid_count)
        last_collect = collect_k_reference_payload(
            dataset=dataset,
            grid_count=grid_count,
            witness_capacity=witness_capacity,
        )
        last_broadphase = aabb_broadphase_collect_k_payload(
            dataset=dataset,
            grid_count=grid_count,
            witness_capacity=witness_capacity,
        )
        cpu_times.append(float(last_reference["elapsed_sec"]))
        collect_times.append(float(last_collect["collect_elapsed_sec"]))
        broadphase_times.append(
            sum(float(value) for value in last_broadphase["run_phases"].values())
        )
    assert last_reference is not None
    assert last_collect is not None
    assert last_broadphase is not None
    return {
        "app": BENCHMARK_APP,
        "mode": "baseline_comparison",
        "dataset": last_reference["dataset"],
        "repeat_count": repeat_count,
        "valid_count": last_reference["valid_count"],
        "witness_capacity": witness_capacity,
        "cpu_reference_best_sec": min(cpu_times),
        "collect_k_reference_best_sec": min(collect_times),
        "aabb_broadphase_collect_k_best_sec": min(broadphase_times),
        "matches_cpu_reference": last_collect["matches_cpu_reference"],
        "aabb_broadphase_matches_cpu_reference": last_broadphase["matches_cpu_reference"],
        "aabb_candidate_pair_count": last_broadphase["aabb_candidate_pair_count"],
        "all_pairs_count": last_broadphase["all_pairs_count"],
        "aabb_pruning_ratio": last_broadphase["aabb_pruning_ratio"],
        "baseline_scope": "straightforward Python exact triangle-intersection baseline",
        "claim_boundary": (
            "Local CPU timing is a correctness/overhead smoke only. The AABB path removes "
            "full all-pairs Python discovery through a generic primitive, but native "
            "Embree/OptiX row-output evidence remains a separate gate before speedup wording."
        ),
    }


def _compile_cpp_baseline() -> Path:
    compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        raise RuntimeError("no C++ compiler found for standalone baseline")
    CPP_BASELINE_BINARY.parent.mkdir(parents=True, exist_ok=True)
    needs_compile = (
        not CPP_BASELINE_BINARY.exists()
        or CPP_BASELINE_SOURCE.stat().st_mtime > CPP_BASELINE_BINARY.stat().st_mtime
    )
    if needs_compile:
        subprocess.run(
            [
                compiler,
                "-std=c++17",
                "-O3",
                "-Wall",
                "-Wextra",
                str(CPP_BASELINE_SOURCE),
                "-o",
                str(CPP_BASELINE_BINARY),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    return CPP_BASELINE_BINARY


def cpp_baseline_payload(
    *,
    dataset: str = "tiny",
    grid_count: int = 64,
    repeat_count: int = 5,
) -> dict[str, Any]:
    binary = _compile_cpp_baseline()
    completed = subprocess.run(
        [
            str(binary),
            "--dataset",
            dataset,
            "--grid-count",
            str(grid_count),
            "--repeat-count",
            str(repeat_count),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    baseline = json.loads(completed.stdout)
    reference = cpu_reference_payload(dataset=dataset, grid_count=grid_count)
    baseline_rows = tuple(tuple(int(value) for value in row) for row in baseline["candidate_id_rows"])
    return {
        "app": BENCHMARK_APP,
        "mode": "cpp_baseline",
        "dataset": reference["dataset"],
        "baseline": baseline["baseline"],
        "baseline_binary": str(binary),
        "primitive_under_test": PRIMITIVE,
        "row_schema": ROW_SCHEMA,
        "scene_triangle_count": baseline["scene_triangle_count"],
        "query_triangle_count": baseline["query_triangle_count"],
        "repeat_count": baseline["repeat_count"],
        "candidate_id_rows": baseline_rows,
        "valid_count": baseline["valid_count"],
        "elapsed_sec": baseline["elapsed_sec"],
        "matches_cpu_reference": baseline_rows == reference["candidate_id_rows"],
        "cpu_reference_valid_count": reference["valid_count"],
        "claim_boundary": (
            "Standalone C++ exact baseline uses the same witness-row contract without RTDL "
            "engine calls; it is a CPU baseline, not an RT-core or native collision claim."
        ),
    }


def run_app(
    *,
    mode: str,
    dataset: str = "tiny",
    witness_capacity: int = 8,
    grid_count: int = 64,
    repeat_count: int = 5,
    backend: str = "cpu_python_reference",
    discovery_backend: str = "cpu",
    discovery_row_capacity: int | None = None,
    discovery_warmup_count: int = 0,
    discovery_repeat_count: int = 1,
) -> dict[str, Any]:
    if mode == "scope":
        return scope_payload()
    if mode == "cpu_reference":
        return cpu_reference_payload(dataset=dataset, grid_count=grid_count)
    if mode == "collect_k_reference":
        return collect_k_reference_payload(
            dataset=dataset,
            witness_capacity=witness_capacity,
            grid_count=grid_count,
            backend=backend,
        )
    if mode == "aabb_broadphase_collect_k":
        return aabb_broadphase_collect_k_payload(
            dataset=dataset,
            witness_capacity=witness_capacity,
            grid_count=grid_count,
            backend=backend,
            discovery_backend=discovery_backend,
            discovery_row_capacity=discovery_row_capacity,
            discovery_warmup_count=discovery_warmup_count,
            discovery_repeat_count=discovery_repeat_count,
        )
    if mode == "native_collect_k":
        return native_collect_k_payload(
            dataset=dataset,
            witness_capacity=witness_capacity,
            grid_count=grid_count,
            backend=backend,
        )
    if mode == "baseline_comparison":
        return baseline_comparison_payload(
            dataset=dataset,
            grid_count=grid_count,
            witness_capacity=witness_capacity,
            repeat_count=repeat_count,
        )
    if mode == "cpp_baseline":
        return cpp_baseline_payload(
            dataset=dataset,
            grid_count=grid_count,
            repeat_count=repeat_count,
        )
    raise ValueError(f"unknown mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=(
            "scope",
            "cpu_reference",
            "collect_k_reference",
            "aabb_broadphase_collect_k",
            "native_collect_k",
            "baseline_comparison",
            "cpp_baseline",
        ),
        default="scope",
    )
    parser.add_argument("--dataset", choices=("tiny", "overflow", "grid"), default="tiny")
    parser.add_argument("--witness-capacity", type=int, default=8)
    parser.add_argument("--grid-count", type=int, default=64)
    parser.add_argument("--repeat-count", type=int, default=5)
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("--discovery-backend", choices=("cpu", "embree", "optix"), default="cpu")
    parser.add_argument("--discovery-row-capacity", type=int)
    parser.add_argument("--discovery-warmup", type=int, default=0)
    parser.add_argument("--discovery-repeat", type=int, default=1)
    args = parser.parse_args(argv)
    payload = run_app(
        mode=args.mode,
        dataset=args.dataset,
        witness_capacity=args.witness_capacity,
        grid_count=args.grid_count,
        repeat_count=args.repeat_count,
        backend=args.backend,
        discovery_backend=args.discovery_backend,
        discovery_row_capacity=args.discovery_row_capacity,
        discovery_warmup_count=args.discovery_warmup,
        discovery_repeat_count=args.discovery_repeat,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
