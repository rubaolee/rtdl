"""Same-input complete front doors for the scoped V2/V3/V4 cohort.

The module is measurement infrastructure, not product selection logic.  It
freezes thirteen representative application lanes and makes the provenance of
each predecessor explicit.  In particular, the held-out particle lane uses
newly frozen comparison backports; it is never described as historical V2/V3.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Callable, Mapping

import rtdsl as rt
from rtdsl.aggregate_hierarchy_native import (
    prepare_aggregate_frontier_reduce_explicit_native_3d,
    run_aggregate_frontier_reduce_default_3d,
)
from rtdsl.generic_primitives import (
    Ray3D,
    Triangle3D,
    run_generic_ray_triangle_closest_hit,
    run_generic_ray_triangle_primitive_grouped_i64_reduction_3d,
)
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_exact_predicate_witness import (
    directed_point_location_sos,
    grouped_exact_segment_pair_counts,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "Paper-reproduction-apps"

V2 = "v2_direct_true_optix_backport"
V3 = "v3_compiler_true_optix"
V4 = "v4_restricted_callback_true_optix"
METHODS = (V2, V3, V4)


@dataclass(frozen=True)
class Lane:
    lane_id: str
    app: str
    paper_algorithm: str
    directory: str
    predecessor_provenance: str = "historical_reviewed_true_optix_frontdoors"

    @property
    def app_dir(self) -> Path:
        return APPS / self.directory


LANES = (
    Lane("triangle__rt_1a2", "triangle_counting", "RT-1A2",
         "triangle-counting-paper"),
    Lane("triangle__rt_2a1", "triangle_counting", "RT-2A1",
         "triangle-counting-paper"),
    Lane("raydb__q21", "raydb", "partitioned_triangle_grouped_i64_sum",
         "raydb-paper"),
    Lane("librts__range_rows", "librts",
         "aabb_index.prepared_query_2d.v1", "librts-paper"),
    Lane("librts__overlap_filter", "librts",
         "aabb_overlap.filter_bounded_emit_2d.v1", "librts-paper"),
    Lane("rtnn__ranked_window", "rtnn", "exact_ranked_distance_window_topk",
         "rtnn-paper"),
    Lane("rtdbscan__components", "rt_dbscan",
         "bounded_radius_graph_component_partition", "rt-dbscan-paper"),
    Lane("xhd__global_witness", "x_hd",
         "directed_exact_max_of_nearest_witness", "x-hd-paper"),
    Lane("rayjoin__point_location", "rayjoin",
         "planar_map.directed_segment_point_location_2d.v1", "rayjoin-paper"),
    Lane("rayjoin__segment_pairs", "rayjoin",
         "planar_map.segment_pair_grouped_range_exact_count_2d.v1",
         "rayjoin-paper"),
    Lane("rayjoin__grouped_events", "rayjoin",
         "logical_events.grouped_i64x2_count_sum.v1", "rayjoin-paper"),
    Lane("rtbh__force", "rt_barneshut",
         "aggregate_hierarchy_inverse_square_scalar_force", "rt-barneshut-paper"),
    Lane("particle__cell_transition", "particle_tracking",
         "tetrahedral_closest_face_cell_transition",
         "goal5753-held-out-particle-tracking",
         "new_fair_comparison_backports_frozen_before_any_v4_timing"),
)
LANE_BY_ID = {lane.lane_id: lane for lane in LANES}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load(name: str, path: Path):
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    search_roots = (str(path.parent), str(APPS))
    for root in reversed(search_roots):
        sys.path.insert(0, root)
    try:
        spec.loader.exec_module(module)
    finally:
        for root in search_roots:
            sys.path.remove(root)
    return module


def _module(lane: Lane, filename: str, suffix: str):
    return _load(
        f"goal5768_{lane.lane_id}_{suffix}".replace("-", "_"),
        lane.app_dir / filename,
    )


def _v4(lane: Lane):
    return _module(lane, "v4_whole_app.py", "v4")


def _runtime_v4_kwargs(runtime: Mapping[str, object]) -> dict[str, object]:
    required = (
        "target", "compute_capability", "optix_include", "cuda_include",
        "expected_python_version", "expected_numba_version",
        "expected_numpy_version", "native_library_path",
    )
    missing = [name for name in required if name not in runtime]
    if missing:
        raise ValueError(f"missing V4 runtime fields: {', '.join(missing)}")
    values = {name: runtime[name] for name in required}
    if isinstance(values["target"], Mapping):
        values["target"] = ReferenceTargetProfile(**values["target"])
    values["compute_capability"] = tuple(values["compute_capability"])
    values["optix_include"] = Path(str(values["optix_include"]))
    values["cuda_include"] = Path(str(values["cuda_include"]))
    values["native_library_path"] = Path(str(values["native_library_path"]))
    return values


def _stable_output(lane: Lane, value: object):
    if lane.app == "triangle_counting":
        return {"triangle_count": int(value["triangle_count"])}
    if lane.app == "raydb":
        rows = value["grouped_rows"]
        return tuple(sorted(
            (tuple(int(item) for item in row["group"]), int(row["value"]))
            for row in rows
        ))
    if lane.app == "librts":
        return tuple(sorted((int(a), int(b)) for a, b in value["relation_rows"]))
    if lane.app == "rtnn":
        return tuple(tuple(row) for row in value)
    if lane.app == "rt_dbscan":
        return {
            "canonical_component_labels": tuple(
                int(item) for item in value["canonical_component_labels"]),
            "core_flags": tuple(bool(item) for item in value["core_flags"]),
        }
    if lane.app == "x_hd":
        return {
            "source_id": int(value["source_id"]),
            "item_id": int(value["item_id"]),
            "value": float(format(float(value["value"]), ".9g")),
        }
    if lane.app == "rayjoin":
        if lane.lane_id == "rayjoin__segment_pairs":
            return {
                "exact_pairs": tuple(tuple(map(int, row)) for row in value["exact_pairs"]),
                "grouped_counts": tuple(tuple(map(int, row)) for row in value["grouped_counts"]),
            }
        return tuple(tuple(map(int, row)) for row in value)
    if lane.app == "rt_barneshut":
        return tuple(
            (int(row["source_id"]), float(format(float(row["scalar_force"]), ".9g")))
            for row in value
        )
    if lane.app == "particle_tracking":
        return tuple(tuple(map(int, row)) for row in value)
    raise AssertionError(lane.app)


def _matched(lane: Lane, actual: object, expected: object) -> bool:
    if lane.app == "rt_barneshut":
        if len(actual) != len(expected):
            return False
        return all(
            left[0] == right[0]
            and math.isclose(left[1], right[1], rel_tol=0.0, abs_tol=1e-8)
            for left, right in zip(actual, expected, strict=True)
        )
    if lane.app == "x_hd":
        return (
            actual["source_id"] == expected["source_id"]
            and actual["item_id"] == expected["item_id"]
            and math.isclose(
                actual["value"], expected["value"], rel_tol=0.0, abs_tol=1e-6)
        )
    return actual == expected


def _v4_run(lane: Lane, runtime: Mapping[str, object]) -> dict[str, object]:
    module = _v4(lane)
    if lane.app == "triangle_counting":
        raw = module.run_v4_complete(lane.paper_algorithm, **_runtime_v4_kwargs(runtime))
    elif lane.app in {"librts", "rayjoin"}:
        raw = module.run_v4_complete(lane.paper_algorithm, **_runtime_v4_kwargs(runtime))
    elif lane.app == "rt_barneshut":
        raw = module.run_v4_complete()
    else:
        raw = module.run_v4_complete(**_runtime_v4_kwargs(runtime))
    actual = _stable_output(lane, raw["output"])
    expected = _stable_output(lane, raw["expected"])
    return {
        "input_sha256": raw["input_sha256"],
        "actual": actual,
        "expected": expected,
        "matched": _matched(lane, actual, expected),
        "seconds": float(raw["registered_complete_seconds"]),
        "traversal_receipt": raw["traversal_receipt"],
        "native_library_sha256": raw["native_library_sha256"],
        "route_metadata": {
            "schema": raw["schema"],
            "complete_timer_includes": list(raw["complete_timer_includes"]),
            "default_selected_between_paper_algorithms": raw[
                "default_selected_between_paper_algorithms"],
        },
    }


def _triangle_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    if method == V2:
        module = _module(lane, "v2_14_whole_app.py", "v2")
        raw = module.run_v2_14(
            paper_algorithm=lane.paper_algorithm, backend="optix")
    else:
        module = _module(lane, "rtdl3_whole_app.py", "v3")
        raw = module.run_v3(paper_algorithm=lane.paper_algorithm)
    seconds = time.perf_counter() - started
    data = _v4(lane).build_v4_input(lane.paper_algorithm)
    return data.input_sha256, raw["output"], {
        "triangle_count": data.expected_triangle_count}, seconds, {
            "schema": raw.get("schema"),
            "backend": raw.get("backend", "compiler_default"),
            "paper_algorithm": lane.paper_algorithm,
        }


def _raydb_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    migration = _module(lane, "rtdl3_action_migration.py", "migration")
    rows = tuple(migration.bounded_q21_rows())
    predicate = migration.bounded_q21_predicate()
    if method == V2:
        workload = migration.lower_rows_to_generic_rt(rows, predicate)
        includes = tuple(predicate.accepts(row.scan_values) for row in rows)
        values = tuple(
            int(value) if includes[index] else 0
            for index, value in enumerate(workload["primitive_values"])
        )
        physical = run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            workload["rays"], workload["triangles"],
            primitive_group_ids=tuple(workload["primitive_group_ids"]),
            primitive_values=values, reduction="sum", backend="optix",
        )
        sums = {int(row["group_id"]): int(row["sum"]) for row in physical["rows"]}
        paper_rows = tuple(
            {"group": list(group), "value": sums.get(index, 0)}
            for index, group in enumerate(workload["group_tuples"])
            if sums.get(index, 0) != 0
        )
        raw = physical
    else:
        raw = migration.run_optix_rows(rows, predicate, collect_phase_trace=False)
        paper_rows = tuple(raw["actual_rows"])
    seconds = time.perf_counter() - started
    data = _v4(lane).build_v4_input()
    return (
        data.input_sha256,
        {"grouped_rows": paper_rows},
        {"grouped_rows": data.expected_paper_rows},
        seconds,
        {
            "backend": raw.get("backend"),
            "physical_family": raw.get("primitive", raw.get("selected_producer_kind")),
        },
    )


def _overlap(box, query) -> float:
    dx = max(0.0, min(box.max_x, query.max_x) - max(box.min_x, query.min_x))
    dy = max(0.0, min(box.max_y, query.max_y) - max(box.min_y, query.min_y))
    return dx * dy


def _librts_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    v4 = _v4(lane)
    app = v4._load_app()
    indexed_path = lane.app_dir / "data/fixtures/tiny_boxes.wkt"
    query_path = lane.app_dir / "data/fixtures/tiny_range_queries.wkt"
    boxes = tuple(app.load_boxes(indexed_path))
    queries = tuple(app.load_boxes(query_path))
    threshold = 0.0 if lane.lane_id == "librts__range_rows" else 0.75
    if method == V2:
        prepared = rt.prepare_aabb_index_2d(boxes, backend="optix")
        try:
            candidates = prepared.intersection_rows(
                queries, tuple(range(len(queries))),
                row_capacity=len(boxes) * len(queries))
        finally:
            prepared.close()
        output = tuple(
            (query_id, indexed_id)
            for query_id, indexed_id in candidates
            if _overlap(boxes[indexed_id], queries[query_id]) >= threshold
        )
        raw = {"backend": "explicit_optix_aabb_index", "rows": output}
    else:
        module = _module(lane, "rtdl3_whole_app.py", "v3")
        raw = module.run_v3_wkt(
            indexed_path, query_path, minimum_overlap=threshold,
            execution_mode="compiler", validate_against_reference=False)
        output = tuple(raw["output"])
    seconds = time.perf_counter() - started
    data = v4.build_v4_input(lane.paper_algorithm)
    return (
        data["input_sha256"], {"relation_rows": output},
        {"relation_rows": data["expected_rows"]}, seconds, {
            "backend": raw.get("backend", raw.get("selected_execution")),
            "physical_family": "aabb_intersection_pair_rows_2d",
        })


def _rtnn_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    data = _v4(lane).build_v4_input()
    if method == V2:
        module = _module(lane, "rtdl3_action_migration.py", "migration")
        raw = module.run_v2_direct_true_optix_backport_points(
            data["search"], data["queries"], k=4,
            min_distance=0.0, max_distance=3.0, validate_reference=False)
        output = raw["actual_rows"]
    else:
        module = _module(lane, "rtdl3_whole_app.py", "v3")
        raw = module.run_v3_points(
            data["search"], data["queries"], k=4,
            min_distance=0.0, max_distance=3.0,
            execution_mode="compiler", collect_phase_trace=False)
        output = raw["output"]
    seconds = time.perf_counter() - started
    return data["input_sha256"], output, data["expected"], seconds, {
        "backend": raw.get("backend", raw.get("selected_execution")),
        "physical_family": raw.get("physical_family", "action_bounded_selection_3d"),
    }


def _rtdbscan_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    data = _v4(lane).build_v4_input()
    if method == V2:
        module = _module(lane, "rtdl3_action_migration.py", "migration")
        raw = module.run_prepared_spatial_radius_route(
            data["points"], epsilon=0.35, min_points=5,
            collect_phase_trace=False)
        output = raw["actual"]
    else:
        module = _module(lane, "rtdl3_whole_app.py", "v3")
        raw = module.run_v3_points(
            data["points"], epsilon=0.35, min_points=5,
            execution_mode="compiler", collect_phase_trace=False,
            validate_reference=False)
        output = raw["output"]
    seconds = time.perf_counter() - started
    return data["input_sha256"], output, data["expected"], seconds, {
        "backend": raw.get("backend", raw.get("selected_execution")),
        "physical_family": raw.get(
            "physical_producer_kind", "fixed_radius_graph_components"),
    }


def _xhd_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    data = _v4(lane).build_v4_input()
    if method == V2:
        module = _module(lane, "v2_true_optix_direct.py", "v2")
        raw = module.run_loaded_cell_mbr_true_optix_direct(
            data["sources"], data["targets"])
        output = {
            "source_id": raw["witness"]["source_id"],
            "item_id": raw["witness"]["target_id"],
            "value": raw["witness"]["distance"],
        }
    else:
        module = _module(lane, "rtdl3_whole_app.py", "v3")
        raw = module.run_v3_points(
            data["sources"], data["targets"], execution_mode="compiler",
            validate_against_reference=False, collect_phase_trace=False)
        output = raw["output"]
    seconds = time.perf_counter() - started
    return data["input_sha256"], output, data["expected"], seconds, {
        "backend": raw.get("method", raw.get("selected_execution")),
        "physical_family": "cell_mbr_exact_witness_3d_optix_traversal",
    }


def _aabb_columns(rows):
    return rt.Aabb2DColumns.from_mapping({
        "id": [int(row[4]) for row in rows],
        "min_x": [float(row[0]) for row in rows],
        "min_y": [float(row[1]) for row in rows],
        "max_x": [float(row[2]) for row in rows],
        "max_y": [float(row[3]) for row in rows],
    })


def _rayjoin_finish(lane: Lane, data, candidates):
    v4 = _v4(lane)
    if lane.lane_id in {"rayjoin__point_location", "rayjoin__grouped_events"}:
        result = directed_point_location_sos(
            data["points"], data["segments"], candidates,
            query_map_id=0, capacity=4096)
        if lane.lane_id == "rayjoin__point_location":
            return result["rows"], data["expected_rows"]
        # The predecessor contract predates M5.  Use the exact logical rows and
        # the same app-owned grouping algebra, explicitly not the V4 M5 path.
        face_by_point = {
            int(row[0]): (int(row[1]), int(row[2])) for row in result["rows"]
            if int(row[2]) != 0xFFFFFFFF
        }
        group_by_segment = {
            int(row.segment_id): int(row.group_id) for row in data["segments"]
        }
        counts: dict[tuple[int, int], list[int]] = {}
        for point_id, (face_id, segment_id) in face_by_point.items():
            key = (face_id, group_by_segment[segment_id])
            entry = counts.setdefault(key, [0, 0])
            entry[0] += 1
            entry[1] += 1
        rows = tuple((a, b, values[0], values[1])
                     for (a, b), values in sorted(counts.items()))
        return rows, rows
    result = grouped_exact_segment_pair_counts(
        data["left"], data["right"], candidates, capacity=4096)
    return {
        "exact_pairs": result["exact_pairs"],
        "grouped_counts": result["grouped_counts"],
    }, {
        "exact_pairs": data["expected_pairs"],
        "grouped_counts": data["expected_groups"],
    }


def _rayjoin_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    data = _v4(lane).build_v4_input(lane.paper_algorithm)
    columns = _aabb_columns(data["indexed"])
    query_boxes = tuple(tuple(float(value) for value in row[:4])
                        for row in data["sources"])
    query_ids = tuple(int(row[4]) for row in data["sources"])
    capacity = max(1, len(data["indexed"]) * len(data["sources"]))
    if method == V2:
        prepared = rt.prepare_aabb_index_2d_columns(columns, backend="optix")
        route = "explicit_optix_aabb_relation"
    else:
        prepared = rt.prepare_compiler_aabb_index_2d_columns(
            columns, operations=("range_intersection_rows",),
            max_query_count=len(query_boxes), max_output_rows=capacity)
        route = "compiler_default_aabb_relation"
    try:
        candidates = prepared.intersection_rows(
            query_boxes, query_ids, row_capacity=capacity)
    finally:
        prepared.close()
    output, expected = _rayjoin_finish(lane, data, candidates)
    seconds = time.perf_counter() - started
    return data["input_sha256"], output, expected, seconds, {
        "route": route, "candidate_rows": candidates}


def _rtbh_project(rows, scale: float):
    return tuple({
        "source_id": int(row["source_id"]),
        "scalar_force": float(row["reducer_value_0"]) * scale,
    } for row in rows)


def _rtbh_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    data = _v4(lane).build_v4_input()
    spec = data["spec"]
    if method == V2:
        with prepare_aggregate_frontier_reduce_explicit_native_3d(
            spec, backend="optix_traversal",
            max_output_rows=spec.prepared_hierarchy.hierarchy.point_count,
        ) as prepared:
            raw = prepared.execute(softening=0.0)
    else:
        raw = run_aggregate_frontier_reduce_default_3d(
            spec, softening=0.0,
            max_output_rows=spec.prepared_hierarchy.hierarchy.point_count)
    output = _rtbh_project(raw["rows"], data["force_scale"])
    seconds = time.perf_counter() - started
    return data["input_sha256"], output, data["expected_rows"], seconds, {
        "backend": raw.get("backend", raw.get("selected_backend")),
        "physical_family": "aggregate_hierarchy_optix_traversal",
    }


def _particle_geometry(data):
    triangle_rows = []
    for triangle_id, indices in enumerate(data["triangles"]):
        a, b, c = (data["vertices"][index] for index in indices)
        triangle_rows.append(Triangle3D(
            triangle_id,
            float(a[0]), float(a[1]), float(a[2]),
            float(b[0]), float(b[1]), float(b[2]),
            float(c[0]), float(c[1]), float(c[2]),
        ))
    triangles = tuple(triangle_rows)
    rays = tuple(
        Ray3D(
            ray_id,
            float(origin[0]), float(origin[1]), float(origin[2]),
            float(direction[0]), float(direction[1]), float(direction[2]),
            float(tmax),
        )
        for ray_id, (origin, direction, tmax) in enumerate(data["queries"])
    )
    return rays, triangles


def _particle_project(data, rows):
    by_ray = {int(row["ray_id"]): row for row in rows}
    result = []
    for ray_id in range(len(data["queries"])):
        row = by_ray.get(ray_id)
        if row is None:
            result.append((0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF))
            continue
        reported_face_id = int(row["triangle_id"])
        if not 0 <= reported_face_id < len(data["triangles"]):
            raise ValueError("particle closest-hit face is outside the topology")
        triangle = data["triangles"][reported_face_id]
        a, b, c = (data["vertices"][index] for index in triangle)
        # The particle contract is an exact front/back semantic decision.  Do
        # not let a floating cross/dot projection become a hidden comparator.
        ab = tuple(Fraction(str(b[i])) - Fraction(str(a[i])) for i in range(3))
        ac = tuple(Fraction(str(c[i])) - Fraction(str(a[i])) for i in range(3))
        normal = (
            ab[1] * ac[2] - ab[2] * ac[1],
            ab[2] * ac[0] - ab[0] * ac[2],
            ab[0] * ac[1] - ab[1] * ac[0],
        )
        direction = tuple(
            Fraction(str(value)) for value in data["queries"][ray_id][1])
        origin = tuple(
            Fraction(str(value)) for value in data["queries"][ray_id][0])
        denominator = sum(normal[i] * direction[i] for i in range(3))
        if denominator == 0:
            raise ValueError("reported particle face is parallel to the query")
        distance = sum(
            normal[i] * (Fraction(str(a[i])) - origin[i])
            for i in range(3)
        ) / denominator
        if distance < 0:
            raise ValueError("reported particle face is behind the query")
        reported_t = float(row["t"])
        if not math.isfinite(reported_t) or not math.isclose(
            reported_t, float(distance), rel_tol=0.0, abs_tol=1.0e-5,
        ):
            raise ValueError("reported particle hit distance is not exact evidence")
        point = tuple(origin[i] + distance * direction[i] for i in range(3))
        offset = tuple(point[i] - Fraction(str(a[i])) for i in range(3))
        d00 = sum(ab[i] * ab[i] for i in range(3))
        d01 = sum(ab[i] * ac[i] for i in range(3))
        d11 = sum(ac[i] * ac[i] for i in range(3))
        d20 = sum(offset[i] * ab[i] for i in range(3))
        d21 = sum(offset[i] * ac[i] for i in range(3))
        bary_denominator = d00 * d11 - d01 * d01
        if bary_denominator == 0:
            raise ValueError("reported particle face is degenerate")
        bary_b = (d11 * d20 - d01 * d21) / bary_denominator
        bary_c = (d00 * d21 - d01 * d20) / bary_denominator
        bary_a = Fraction(1) - bary_b - bary_c
        barycentric = (bary_a, bary_b, bary_c)
        if min(barycentric) < 0:
            raise ValueError("reported particle face does not contain the exact hit")

        zero_positions = tuple(
            index for index, value in enumerate(barycentric) if value == 0)
        if len(zero_positions) == 0:
            face_id = reported_face_id
        elif len(zero_positions) == 1:
            boundary_vertices = frozenset(
                triangle[index] for index in range(3)
                if index != zero_positions[0])
            incident = tuple(
                face_id for face_id, candidate in enumerate(data["triangles"])
                if boundary_vertices.issubset(candidate)
            )
            if not incident:
                raise ValueError("particle edge has no incident face owner")
            face_id = min(incident)
        elif len(zero_positions) == 2:
            vertex = triangle[next(
                index for index in range(3) if index not in zero_positions)]
            incident = tuple(
                face_id for face_id, candidate in enumerate(data["triangles"])
                if vertex in candidate
            )
            if not incident:
                raise ValueError("particle vertex has no incident face owner")
            face_id = min(incident)
        else:
            raise ValueError("particle hit has no nonzero barycentric coordinate")

        canonical_triangle = data["triangles"][face_id]
        ca, cb, cc = (data["vertices"][index] for index in canonical_triangle)
        cab = tuple(Fraction(str(cb[i])) - Fraction(str(ca[i])) for i in range(3))
        cac = tuple(Fraction(str(cc[i])) - Fraction(str(ca[i])) for i in range(3))
        canonical_normal = (
            cab[1] * cac[2] - cab[2] * cac[1],
            cab[2] * cac[0] - cab[0] * cac[2],
            cab[0] * cac[1] - cab[1] * cac[0],
        )
        is_front = sum(
            canonical_normal[i] * direction[i] for i in range(3)) < 0
        selected = data["front_values"][face_id] if is_front else data["back_values"][face_id]
        neighbor = data["back_values"][face_id] if is_front else data["front_values"][face_id]
        result.append((int(selected), int(neighbor), face_id))
    return tuple(result)


def _particle_predecessor(lane: Lane, method: str):
    started = time.perf_counter()
    data = _v4(lane).build_v4_input()
    rays, triangles = _particle_geometry(data)
    if method == V2:
        from rtdsl.optix_runtime import prepare_optix_static_triangle_scene_3d
        with prepare_optix_static_triangle_scene_3d(triangles) as prepared:
            rows = prepared.ray_closest_hit_rows(rays)
            raw = {"route": "new_v2_direct_closest_hit_backport", "rows": rows}
    else:
        rows = run_generic_ray_triangle_closest_hit(
            rays, triangles, backend="optix")
        raw = {"route": "new_v3_canonical_closest_hit_backport", "rows": rows}
    output = _particle_project(data, rows)
    raw["exact_topology_owner"] = (
        "host_exact_min_incident_face_from_reported_boundary")
    raw["topology_owner_inside_complete_timer"] = True
    raw["all_triangle_oracle_used_as_output"] = False
    seconds = time.perf_counter() - started
    return data["input_sha256"], output, data["expected"], seconds, raw


_PREDECESSORS: dict[str, Callable[[Lane, str], tuple[object, ...]]] = {
    "triangle_counting": _triangle_predecessor,
    "raydb": _raydb_predecessor,
    "librts": _librts_predecessor,
    "rtnn": _rtnn_predecessor,
    "rt_dbscan": _rtdbscan_predecessor,
    "x_hd": _xhd_predecessor,
    "rayjoin": _rayjoin_predecessor,
    "rt_barneshut": _rtbh_predecessor,
    "particle_tracking": _particle_predecessor,
}


def run_complete(
    lane_id: str,
    method: str,
    *,
    runtime: Mapping[str, object],
) -> dict[str, object]:
    """Run one fresh-process complete endpoint and bind behavioral traversal."""

    if lane_id not in LANE_BY_ID:
        raise ValueError("unknown Goal5768 lane")
    if method not in METHODS:
        raise ValueError("unknown Goal5768 method")
    lane = LANE_BY_ID[lane_id]
    if method == V4:
        result = _v4_run(lane, runtime)
    else:
        native_path = Path(str(runtime["native_library_path"])).resolve()
        from rtdsl import optix_runtime
        library = optix_runtime._load_optix_library()
        loaded_path = Path(str(library._rtdl_library_path)).resolve()
        if loaded_path != native_path:
            raise RuntimeError(
                "loaded OptiX provider differs from the frozen native path")
        with OptixTraversalAuditSession.open(
            library=library, library_path=native_path) as audit:
            input_sha, raw_actual, raw_expected, seconds, route = (
                _PREDECESSORS[lane.app](lane, method))
            actual = _stable_output(lane, raw_actual)
            expected = _stable_output(lane, raw_expected)
            receipt = audit.finish(
                semantic_digest=str(input_sha),
                output_digest=_digest(actual),
                route_identity=f"goal5768:{lane_id}:{method}",
            )
        result = {
            "input_sha256": input_sha,
            "actual": actual,
            "expected": expected,
            "matched": _matched(lane, actual, expected),
            "seconds": float(seconds),
            "traversal_receipt": receipt,
            "native_library_sha256": receipt["provider_library_sha256"],
            "route_metadata": route,
        }
    if not result["matched"]:
        raise RuntimeError(f"{lane_id}:{method} exact output mismatch")
    return {
        "schema": "rtdl.goal5768.three_way_complete_endpoint.v1",
        "lane_id": lane.lane_id,
        "app": lane.app,
        "paper_algorithm": lane.paper_algorithm,
        "method": method,
        "predecessor_provenance": lane.predecessor_provenance,
        "input_sha256": result["input_sha256"],
        "output": result["actual"],
        "expected": result["expected"],
        "output_sha256": _digest(result["actual"]),
        "expected_sha256": _digest(result["expected"]),
        "matched": True,
        "registered_complete_seconds": result["seconds"],
        "comparator_inside_registered_timer": False,
        "traversal_receipt": result["traversal_receipt"],
        "native_library_sha256": result["native_library_sha256"],
        "route_metadata": result["route_metadata"],
        "default_selected_between_application_algorithms": False,
        "stock_v2_or_v3_claimed": False,
        "performance_claimed": False,
    }


__all__ = [
    "LANES", "LANE_BY_ID", "METHODS", "V2", "V3", "V4", "run_complete",
]
