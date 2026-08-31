"""Lifecycle-matched prepared V2/V3/V4 front doors for Goal5774.

Every owner prepares one immutable scene/index and executes two genuinely
different dynamic requests.  This module is measurement infrastructure: it
does not choose between paper algorithms and it never substitutes a cold
front door inside ``execute``.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Mapping

import numpy as np

import rtdsl as rt
from rtdsl.aggregate_hierarchy_native import (
    PreparedNativeAggregateHierarchy3D,
    compile_aggregate_frontier_reduce_default_3d,
    prepare_aggregate_frontier_reduce_explicit_native_3d,
)
from rtdsl.direct_optix_physical import prepare_direct_optix_bounded_selection_3d
from rtdsl.generic_primitives import Ray3D, Triangle3D
from rtdsl.optix_runtime import (
    prepare_certified_nearest_global_witness_3d_optix,
    prepare_optix_static_triangle_scene_3d,
)

from goal5768_three_way_frontdoors import (
    LANES,
    LANE_BY_ID,
    METHODS as THREE_WAY_METHODS,
    V2,
    V3,
    V4,
    Lane,
    _aabb_columns,
    _digest,
    _load,
    _matched,
    _module,
    _overlap,
    _particle_geometry,
    _particle_project,
    _rayjoin_finish,
    _rtbh_project,
    _runtime_v4_kwargs,
    _stable_output,
    _v4,
)

# Owner priority amendment (2026-08-13): V2-direct versus V4 is the first
# publication-critical comparison.  V3 code remains available for later
# diagnostics, but is deliberately outside Goal5774 admission and execution.
METHODS = (V2, V4)


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _triangle_rows(data):
    return tuple(Triangle3D(
        triangle_id,
        *(
            coordinate
            for vertex_index in indices
            for coordinate in data.vertices[vertex_index]
        ),
    ) for triangle_id, indices in enumerate(data.triangles))


def _ray_rows(query_rows):
    return tuple(Ray3D(
        ray_id,
        float(origin[0]), float(origin[1]), float(origin[2]),
        float(direction[0]), float(direction[1]), float(direction[2]),
        float(tmax),
    ) for ray_id, (origin, direction, tmax) in enumerate(query_rows))


def _dynamic_request(lane: Lane, data, call_index: int):
    if call_index not in (0, 1, 2):
        raise ValueError("Goal5774 call_index must be zero, one, or activation index two")
    reverse = call_index == 1
    activate = call_index == 2
    if lane.app == "triangle_counting":
        queries = tuple(data.queries)
        if reverse:
            queries = tuple(reversed(queries))
        elif activate:
            # Preserve the exact finite segment while changing its parameter
            # representation: o + t*d == o + (t/2)*(2*d).
            queries = tuple(
                (tuple(origin), tuple(2.0 * float(v) for v in direction),
                 float(tmax) / 2.0)
                for origin, direction, tmax in queries)
        metadata = dict(data.metadata)
        if "query.weight" in metadata:
            weights = tuple(metadata["query.weight"])
            if reverse:
                metadata["query.weight"] = tuple(reversed(weights))
        return {"queries": queries, "query_metadata": metadata}
    if lane.app == "raydb":
        # RayDB's paper contract assigns each query position to the matching
        # canonical group id.  Reordering queries would therefore change the
        # application-level identity, not merely exercise a second request.
        # Vary the finite ray extent instead: all frozen triangles are within
        # the original extent, so this is a distinct legal request with the
        # same exact paper result and stable query/group binding.
        queries = tuple(
            (tuple(origin), tuple(direction),
             float(tmax) + (2.0 if activate else (1.0 if reverse else 0.0)))
            for origin, direction, tmax in data.queries)
        return {"queries": queries}
    if lane.app in {"librts", "rayjoin"}:
        sources = tuple(data["sources"])
        if reverse:
            sources = tuple(reversed(sources))
        elif activate:
            sources = sources[1:] + sources[:1]
        return {"source_boxes": sources}
    if lane.app == "rtnn":
        rows = data["queries"]
        if reverse:
            rows = rows[::-1]
        elif activate:
            rows = np.roll(rows, -1, axis=0)
        queries = np.ascontiguousarray(
            rows, dtype=np.float32)
        return {
            "queries": queries, "k": 4, "minimum_distance": 0.0,
            "maximum_distance": 3.0,
        }
    if lane.app == "rt_dbscan":
        return {"epsilon": 0.35,
                "min_points": 6 if activate else (4 if reverse else 5)}
    if lane.app == "x_hd":
        rows = data["sources"]
        if reverse:
            rows = rows[::-1]
        elif activate:
            # A duplicate of source zero cannot change the directed-Hausdorff
            # maximum or its deterministic minimum source-id witness, but it
            # creates a third legal dynamic request shape.
            rows = np.concatenate((rows, rows[:1]), axis=0)
        sources = np.ascontiguousarray(
            rows, dtype=np.float32)
        return {"sources": sources}
    if lane.app == "rt_barneshut":
        return {"softening": 0.02 if activate else (0.01 if reverse else 0.0)}
    if lane.app == "particle_tracking":
        queries = tuple(data["queries"])
        if reverse:
            queries = tuple(reversed(queries))
        elif activate:
            queries = tuple(
                (tuple(origin), tuple(2.0 * float(v) for v in direction),
                 float(tmax) / 2.0)
                for origin, direction, tmax in queries)
        return {"queries": queries}
    raise AssertionError(lane.app)


def _dynamic_input_digest(lane: Lane, request: Mapping[str, object]) -> str:
    serializable = {}
    for key, value in request.items():
        if isinstance(value, np.ndarray):
            serializable[key] = value.tolist()
        else:
            serializable[key] = value
    return _sha({"lane_id": lane.lane_id, "request": serializable})


class _Adapter:
    def execute(self, call_index: int) -> dict[str, object]:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


@dataclass
class _V4Adapter(_Adapter):
    lane: Lane
    data: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        raw = self.owner.execute(**request)
        actual = _stable_output(self.lane, raw["output"])
        expected = _stable_output(self.lane, raw["expected"])
        return _finish_call(
            self.lane, V4, call_index, request, actual, expected, raw,
            self.prepare_seconds,
        )

    def close(self) -> None:
        self.owner.close()


def _prepare_v4(lane: Lane, runtime: Mapping[str, object]) -> _V4Adapter:
    module = _v4(lane)
    started = time.perf_counter()
    kwargs = _runtime_v4_kwargs(runtime)
    if lane.app in {"triangle_counting", "librts", "rayjoin"}:
        owner = module.prepare_v4(lane.paper_algorithm, **kwargs)
        data = module.build_v4_input(lane.paper_algorithm)
    elif lane.app == "rt_barneshut":
        owner = module.prepare_v4()
        data = module.build_v4_input()
    else:
        owner = module.prepare_v4(**kwargs)
        data = module.build_v4_input()
    elapsed = time.perf_counter() - started
    return _V4Adapter(lane, data, owner, elapsed)


@dataclass
class _TriangleV2Adapter(_Adapter):
    lane: Lane
    data: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        rays = _ray_rows(request["queries"])
        started = time.perf_counter()
        if self.lane.paper_algorithm == "RT-1A2":
            raw = self.owner.ray_hit_count_sum(rays)
            value = int(raw["hit_count_sum"])
        else:
            weights = request["query_metadata"]["query.weight"]
            raw = self.owner.ray_any_hit_weighted_sum(rays, weights)
            value = int(raw["weighted_hit_sum"])
        elapsed = time.perf_counter() - started
        raw = dict(raw)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, V2, call_index, request,
            {"triangle_count": value},
            {"triangle_count": self.data.expected_triangle_count}, raw,
            self.prepare_seconds,
        )

    def close(self) -> None:
        self.owner.close()


def _prepare_triangle_v2(lane: Lane) -> _TriangleV2Adapter:
    data = _v4(lane).build_v4_input(lane.paper_algorithm)
    started = time.perf_counter()
    owner = prepare_optix_static_triangle_scene_3d(_triangle_rows(data))
    return _TriangleV2Adapter(
        lane, data, owner, time.perf_counter() - started)


@dataclass
class _TriangleV3Adapter(_Adapter):
    lane: Lane
    data: object
    owner: object

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        rays = _ray_rows(request["queries"])
        weights = request["query_metadata"].get("query.weight")
        raw = self.owner.execute(rays=rays, ray_weights=weights)
        return _finish_call(
            self.lane, V3, call_index, request,
            _stable_output(self.lane, raw["output"]),
            _stable_output(self.lane, raw["expected"]), raw,
            self.owner.total_prepare_seconds,
        )

    def close(self) -> None:
        self.owner.close()


def _prepare_triangle_v3(lane: Lane) -> _TriangleV3Adapter:
    module = _module(lane, "rtdl3_whole_app.py", "v3_prepared")
    owner = module.prepare_v3(paper_algorithm=lane.paper_algorithm)
    return _TriangleV3Adapter(
        lane, _v4(lane).build_v4_input(lane.paper_algorithm), owner)


@dataclass
class _RaydbAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    owner: object
    group_tuples: tuple
    default_rays: tuple
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        rays = tuple(reversed(self.default_rays)) if call_index else self.default_rays
        started = time.perf_counter()
        if self.method == V2:
            physical = self.owner.run(rays, reduction="sum")
            sums = {int(row["group_id"]): int(row["sum"])
                    for row in physical["rows"]}
            rows = tuple(
                {"group": list(group), "value": sums.get(index, 0)}
                for index, group in enumerate(self.group_tuples)
                if sums.get(index, 0) != 0)
            raw = physical
        else:
            physical = self.owner.execute_rays(rays)
            rows = tuple(physical["actual_rows"])
            raw = physical
        elapsed = time.perf_counter() - started
        raw = dict(raw)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, {"grouped_rows": rows}),
            _stable_output(self.lane, {"grouped_rows": self.data.expected_paper_rows}),
            raw, self.prepare_seconds)

    def close(self) -> None:
        self.owner.close()


def _prepare_raydb(lane: Lane, method: str) -> _RaydbAdapter:
    migration = _module(lane, "rtdl3_action_migration.py", f"{method}_prepared")
    rows = tuple(migration.bounded_q21_rows())
    predicate = migration.bounded_q21_predicate()
    workload = migration.lower_rows_to_generic_rt(rows, predicate)
    data = _v4(lane).build_v4_input()
    started = time.perf_counter()
    if method == V2:
        includes = tuple(predicate.accepts(row.scan_values) for row in rows)
        values = tuple(
            int(value) if includes[index] else 0
            for index, value in enumerate(workload["primitive_values"]))
        owner = rt.prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            workload["triangles"],
            primitive_group_ids=tuple(workload["primitive_group_ids"]),
            primitive_values=values,
            backend="optix",
        )
    else:
        owner = migration.prepare_compiler_rows(rows, predicate)
    return _RaydbAdapter(
        lane, method, data, owner, tuple(workload["group_tuples"]),
        tuple(workload["rays"]),
        time.perf_counter() - started)


@dataclass
class _AabbAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        sources = request["source_boxes"]
        started = time.perf_counter()
        if self.lane.app == "librts":
            if self.method == V2:
                queries = tuple(tuple(float(v) for v in row[:4]) for row in sources)
                ids = tuple(int(row[4]) for row in sources)
                candidates = self.owner.intersection_rows(
                    queries, ids, row_capacity=len(self.data["indexed"]) * len(sources))
                threshold = float(self.data["minimum_overlap"])
                boxes = self._indexed_boxes
                output = tuple(
                    (query_id, indexed_id)
                    for query_id, indexed_id in candidates
                    if _overlap(boxes[indexed_id], self._query_by_id[query_id]) >= threshold)
                raw = {"rows": candidates}
            else:
                physical = self.owner.execute_boxes(sources)
                output = tuple(physical["rows"])
                raw = physical
            expected = tuple(self.data["expected_rows"])
        else:
            queries = tuple(tuple(float(v) for v in row[:4]) for row in sources)
            ids = tuple(int(row[4]) for row in sources)
            capacity = len(self.data["indexed"]) * len(sources)
            if self.method == V2:
                candidates = self.owner.intersection_rows(
                    queries, ids, row_capacity=capacity)
            else:
                candidates = self.owner.intersection_rows(
                    queries, ids, row_capacity=capacity)
            output, expected = _rayjoin_finish(
                self.lane, self.data, candidates)
            raw = {"rows": candidates}
        elapsed = time.perf_counter() - started
        raw = dict(raw)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, output if self.lane.app != "librts" else {"relation_rows": output}),
            _stable_output(self.lane, expected if self.lane.app != "librts" else {"relation_rows": expected}),
            raw, self.prepare_seconds)

    def close(self) -> None:
        self.owner.close()


def _prepare_aabb(lane: Lane, method: str) -> _AabbAdapter:
    data = _v4(lane).build_v4_input(lane.paper_algorithm)
    started = time.perf_counter()
    if lane.app == "librts":
        app = _v4(lane)._load_app()
        boxes = tuple(app.load_boxes(lane.app_dir / "data/fixtures/tiny_boxes.wkt"))
        if method == V2:
            owner = rt.prepare_aabb_index_2d(boxes, backend="optix")
        else:
            migration = _module(lane, "rtdl3_action_migration.py", "v3_prepared")
            owner = migration.prepare_compiler_boxes(
                boxes, minimum_overlap=float(data["minimum_overlap"]),
                row_capacity=len(boxes) * len(data["sources"]))
        adapter = _AabbAdapter(
            lane, method, data, owner, time.perf_counter() - started)
        adapter._indexed_boxes = boxes
        query_boxes = tuple(app.load_boxes(
            lane.app_dir / "data/fixtures/tiny_range_queries.wkt"))
        adapter._query_by_id = {
            int(row[4]): query_boxes[index]
            for index, row in enumerate(data["sources"])}
        return adapter
    columns = _aabb_columns(data["indexed"])
    capacity = max(1, len(data["indexed"]) * len(data["sources"]))
    if method == V2:
        owner = rt.prepare_aabb_index_2d_columns(columns, backend="optix")
    else:
        owner = rt.prepare_compiler_aabb_index_2d_columns(
            columns, operations=("range_intersection_rows",),
            max_query_count=len(data["sources"]), max_output_rows=capacity)
    return _AabbAdapter(
        lane, method, data, owner, time.perf_counter() - started)


@dataclass
class _RtnnAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    migration: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        queries = request["queries"]
        packed = self.migration._pack_point_rows(queries)
        started = time.perf_counter()
        if self.method == V2:
            physical = self.owner.run(
                packed, minimum_distance=0.0, maximum_distance=3.0, k=4,
                minimum_boundary="open", maximum_boundary="open")
            relation = self.migration._relation_rows_from_rows(physical["rows"])
        else:
            result = self.owner.execute_queries(
                packed,
                parameters={"k": 4, "min_distance": 0.0, "max_distance": 3.0},
                extents={self.migration.ExtentKind.QUERY_COUNT: len(queries)})
            payload = result.payload
            relation = (
                self.migration._relation_rows_from_columns(payload["columns"])
                if "columns" in payload
                else self.migration._relation_rows_from_rows(payload["rows"])
            )
            physical = payload
        actual = self.migration._canonical_rows(relation)
        elapsed = time.perf_counter() - started
        expected = self.migration._expected_for_points(
            self.data["search"], queries, k=4,
            min_distance=0.0, max_distance=3.0)
        raw = dict(physical)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, actual),
            _stable_output(self.lane, expected), raw, self.prepare_seconds)

    def close(self) -> None:
        self.owner.close()


def _prepare_rtnn(lane: Lane, method: str) -> _RtnnAdapter:
    migration = _module(lane, "rtdl3_action_migration.py", f"{method}_prepared")
    data = _v4(lane).build_v4_input()
    search = np.ascontiguousarray(data["search"], dtype=np.float32)
    queries = np.ascontiguousarray(data["queries"], dtype=np.float32)
    packed_search = migration._pack_point_rows(search)
    started = time.perf_counter()
    if method == V2:
        owner = prepare_direct_optix_bounded_selection_3d(
            packed_search, max_distance_bound=3.0)
    else:
        packed_queries = migration._pack_point_rows(queries)
        compiled = migration.compile_action_source(
            migration.ACTION_SOURCE, migration.action_contract())
        bound = migration.bind_action_producer(
            compiled, migration.ActionProducerKind.PREPARED_POINT_CANDIDATES_3D)
        target = migration.detect_action_target_profile(
            producer_kind=migration.ActionProducerKind.PREPARED_POINT_CANDIDATES_3D,
            cpu_reference_available=False)
        parameters = {"k": 4, "min_distance": 0.0, "max_distance": 3.0}
        extents = {migration.ExtentKind.QUERY_COUNT: len(queries)}
        planned = migration.plan_registered_point_bounded_selection(
            bound, target, prepared_search_points=packed_search,
            query_points=packed_queries, extents=extents,
            parameters=parameters,
            **migration._canonical_authority_kwargs(
                target, "ranked_distance_window"))
        owner = migration.prepare_action_execution(
            planned, extents=extents, parameters=parameters,
            prepared_input=packed_search, max_distance_bound=3.0)
    return _RtnnAdapter(
        lane, method, data, migration, owner,
        time.perf_counter() - started)


def _rtdbscan_project(columns, point_count: int):
    point_ids = np.asarray(columns["point_ids"].copy_to_host(), dtype=np.int64)
    labels_in = np.asarray(
        columns["component_labels"].copy_to_host(), dtype=np.int64)
    core_in = np.asarray(columns["is_core"].copy_to_host(), dtype=np.int64)
    labels = [-1] * point_count
    core = [False] * point_count
    for index, point_id in enumerate(point_ids.tolist()):
        labels[int(point_id)] = int(labels_in[index])
        core[int(point_id)] = bool(core_in[index])
    result = {
        "canonical_component_labels": rt.canonical_partition_labels(labels),
        "core_flags": tuple(core),
    }
    return result


@dataclass
class _RtDbscanAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    migration: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        started = time.perf_counter()
        if self.method == V2:
            physical = rt.radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                self.owner, min_neighbors=int(request["min_points"]),
                return_metadata=True)
            actual = _rtdbscan_project(
                physical["columns"], len(self.data["points"]))
            raw = physical
        else:
            physical = self.migration.run_compiler_selected_fixed_radius_graph_route(
                self.data["points"], epsilon=float(request["epsilon"]),
                min_points=int(request["min_points"]),
                collect_phase_trace=False, compiler_prepared=self.owner)
            actual = physical["actual"]
            raw = physical
        elapsed = time.perf_counter() - started
        expected_full = self.migration._expected_from_points(
            self.data["points"], epsilon=float(request["epsilon"]),
            min_points=int(request["min_points"]))
        expected = {
            "canonical_component_labels": expected_full[
                "canonical_component_labels"],
            "core_flags": expected_full["core_flags"],
        }
        raw = dict(raw)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, actual),
            _stable_output(self.lane, expected), raw, self.prepare_seconds)

    def close(self) -> None:
        if self.method == V2:
            self.owner.close()
        else:
            self.migration.close_compiler_fixed_radius_graph_route(self.owner)


def _prepare_rtdbscan(lane: Lane, method: str) -> _RtDbscanAdapter:
    migration = _module(lane, "rtdl3_action_migration.py", f"{method}_prepared")
    data = _v4(lane).build_v4_input()
    started = time.perf_counter()
    if method == V2:
        points = np.asarray(data["points"], dtype=np.float32)
        point_rows = tuple(rt.Point3D(
            id=index, x=float(row[0]), y=float(row[1]), z=float(row[2]))
            for index, row in enumerate(points))
        owner = rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
            point_rows, radius=0.35, partner="numba")
    else:
        owner = migration.prepare_compiler_fixed_radius_graph_route()
    return _RtDbscanAdapter(
        lane, method, data, migration, owner,
        time.perf_counter() - started)


@dataclass
class _XhdAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        sources = request["sources"]
        started = time.perf_counter()
        if self.method == V2:
            physical = self.owner.run(sources)
            actual = dict(physical["actual"])
        else:
            result = self.owner.execute_queries(
                np.ascontiguousarray(sources, dtype=np.float64),
                extents={"query_count": len(sources)}, parameters={})
            physical = result.payload
            actual = dict(physical["actual"])
        elapsed = time.perf_counter() - started
        expected = _v4(self.lane)._expected_for(
            np.ascontiguousarray(sources, dtype=np.float32),
            np.ascontiguousarray(self.data["targets"], dtype=np.float32))
        raw = dict(physical)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, actual),
            _stable_output(self.lane, expected), raw, self.prepare_seconds)

    def close(self) -> None:
        self.owner.close()


def _prepare_xhd(lane: Lane, method: str) -> _XhdAdapter:
    migration = _module(lane, "rtdl3_action_migration.py", f"{method}_prepared")
    data = _v4(lane).build_v4_input()
    sources = np.ascontiguousarray(data["sources"], dtype=np.float64)
    targets = np.ascontiguousarray(data["targets"], dtype=np.float64)
    started = time.perf_counter()
    if method == V2:
        owner = prepare_certified_nearest_global_witness_3d_optix(
            np.ascontiguousarray(targets, dtype=np.float32),
            target_ids=np.arange(len(targets), dtype=np.int64),
            grid_shape=(32, 32, 32),
            query_domain_lower_bounds=np.min(sources, axis=0),
            query_domain_upper_bounds=np.max(sources, axis=0),
            max_inline_points=64,
            max_heavy_point_evaluations=len(sources) * len(targets),
            application_selected_backend=True)
    else:
        compiled = migration.compile_action_source(
            migration.ACTION_SOURCE, migration.action_contract())
        bound = migration.bind_action_producer(
            compiled, migration.ActionProducerKind.CERTIFIED_NEAREST_STATE_3D)
        target = migration.detect_action_target_profile(
            producer_kind=migration.ActionProducerKind.CERTIFIED_NEAREST_STATE_3D,
            cpu_reference_available=True)
        planned = migration.compile_bound_action_for_target(
            bound, target,
            extents={"query_count": len(sources), "primitive_count": len(targets)},
            parameters={},
            consumer_composition=(
                migration.ActionConsumerCompositionKind.
                CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS),
            **migration._canonical_authority_kwargs(
                target, "cell_mbr_exact_witness"))
        payload = migration.PreparedCertifiedNearestGridPayload3D(
            target_points=targets, grid_shape=(32, 32, 32),
            independent_validation_sample_count=0)
        owner = migration.prepare_action_execution(
            planned, extents={"query_count": len(sources)}, parameters={},
            prepared_input=payload)
    return _XhdAdapter(
        lane, method, data, owner, time.perf_counter() - started)


@dataclass
class _RtBarnesHutAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        started = time.perf_counter()
        physical = self.owner.execute(softening=float(request["softening"]))
        actual = _rtbh_project(physical["rows"], self.data["force_scale"])
        elapsed = time.perf_counter() - started
        expected = _v4(self.lane)._reference_rows(
            self.data["spec"], softening=float(request["softening"]),
            force_scale=float(self.data["force_scale"]))
        raw = dict(physical)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, actual),
            _stable_output(self.lane, expected), raw, self.prepare_seconds)

    def close(self) -> None:
        self.owner.close()


def _prepare_rtbh(lane: Lane, method: str) -> _RtBarnesHutAdapter:
    data = _v4(lane).build_v4_input()
    spec = data["spec"]
    maximum = spec.prepared_hierarchy.hierarchy.point_count
    started = time.perf_counter()
    if method == V2:
        owner = prepare_aggregate_frontier_reduce_explicit_native_3d(
            spec, backend="optix_traversal", max_output_rows=maximum)
    else:
        plan = compile_aggregate_frontier_reduce_default_3d(
            spec, max_output_rows=maximum)
        owner = PreparedNativeAggregateHierarchy3D(plan)
    return _RtBarnesHutAdapter(
        lane, method, data, owner, time.perf_counter() - started)


@dataclass
class _ParticleAdapter(_Adapter):
    lane: Lane
    method: str
    data: object
    owner: object
    prepare_seconds: float

    def execute(self, call_index: int) -> dict[str, object]:
        request = _dynamic_request(self.lane, self.data, call_index)
        queries = request["queries"]
        started = time.perf_counter()
        if self.method == V2:
            dynamic_data = dict(self.data)
            dynamic_data["queries"] = queries
            rays, _ = _particle_geometry(dynamic_data)
            rows = self.owner.ray_closest_hit_rows(rays)
            actual = _particle_project(dynamic_data, rows)
            v4 = _v4(self.lane)
            exact_vertices = tuple(
                tuple(v4.Fraction(str(value)) for value in row)
                for row in dynamic_data["vertices"])
            exact_queries = tuple(
                tuple(v4.Fraction(str(value)) for value in row[0])
                for row in queries)
            face_rows = tuple(zip(
                dynamic_data["triangles"], dynamic_data["front_values"],
                dynamic_data["back_values"]))
            expected = tuple(v4._ray_triangle_expected(
                query, exact_vertices, face_rows) for query in exact_queries)
            raw = {"rows": rows}
        else:
            result = self.owner.execute(queries=queries)
            actual = result["output"]
            expected = result["expected"]
            raw = result
        elapsed = time.perf_counter() - started
        raw = dict(raw)
        raw["registered_prepared_execution_seconds"] = elapsed
        return _finish_call(
            self.lane, self.method, call_index, request,
            _stable_output(self.lane, actual),
            _stable_output(self.lane, expected), raw, self.prepare_seconds)

    def close(self) -> None:
        self.owner.close()


def _prepare_particle(lane: Lane, method: str) -> _ParticleAdapter:
    data = _v4(lane).build_v4_input()
    _, triangles = _particle_geometry(data)
    started = time.perf_counter()
    if method == V2:
        owner = prepare_optix_static_triangle_scene_3d(triangles)
        prepare_seconds = time.perf_counter() - started
    else:
        module = _module(lane, "rtdl3_whole_app.py", "v3_prepared")
        owner = module.prepare_v3()
        prepare_seconds = owner.total_prepare_seconds
    return _ParticleAdapter(
        lane, method, data, owner, prepare_seconds)


def _finish_call(
    lane: Lane,
    method: str,
    call_index: int,
    request: Mapping[str, object],
    actual,
    expected,
    raw: Mapping[str, object],
    prepare_seconds: float,
) -> dict[str, object]:
    if not _matched(lane, actual, expected):
        raise RuntimeError(
            f"{lane.lane_id}:{method}:call{call_index} exact output mismatch")
    seconds = float(raw.get(
        "registered_prepared_execution_seconds",
        raw.get("elapsed_seconds", raw.get("native_elapsed_sec", 0.0))))
    result = {
        "schema": "rtdl.goal5774.prepared_three_way_call.v1",
        "lane_id": lane.lane_id,
        "app": lane.app,
        "paper_algorithm": lane.paper_algorithm,
        "method": method,
        "call_index": call_index,
        "dynamic_input_sha256": _dynamic_input_digest(lane, request),
        "output": actual,
        "expected": expected,
        "output_sha256": _digest(actual),
        "expected_sha256": _digest(expected),
        "matched": True,
        "reported_total_prepare_seconds": float(prepare_seconds),
        "prepare_is_free": False,
        "cold_result_replaced": False,
        "default_selected_between_application_algorithms": False,
        "raw_metadata": {
            key: raw[key] for key in (
                "schema", "lifecycle_receipt", "traversal_receipt",
                "native_library_sha256", "native_summary", "plan",
                "runtime_metadata", "query_metadata",
            ) if key in raw
        },
    }
    if call_index == 2:
        result["activation_only"] = True
        result["registered_performance_observation"] = False
        result["activation_seconds"] = seconds
    else:
        result["activation_only"] = False
        result["registered_performance_observation"] = True
        result["registered_prepared_execution_seconds"] = seconds
    return result


def prepare_three_way(
    lane_id: str,
    method: str,
    *,
    runtime: Mapping[str, object],
) -> _Adapter:
    if lane_id not in LANE_BY_ID:
        raise ValueError("unknown Goal5774 lane")
    if method not in METHODS:
        raise ValueError("unknown Goal5774 method")
    lane = LANE_BY_ID[lane_id]
    if method == V4:
        return _prepare_v4(lane, runtime)
    if lane.app == "triangle_counting":
        return _prepare_triangle_v2(lane) if method == V2 else _prepare_triangle_v3(lane)
    if lane.app == "raydb":
        return _prepare_raydb(lane, method)
    if lane.app in {"librts", "rayjoin"}:
        return _prepare_aabb(lane, method)
    if lane.app == "rtnn":
        return _prepare_rtnn(lane, method)
    if lane.app == "rt_dbscan":
        return _prepare_rtdbscan(lane, method)
    if lane.app == "x_hd":
        return _prepare_xhd(lane, method)
    if lane.app == "rt_barneshut":
        return _prepare_rtbh(lane, method)
    if lane.app == "particle_tracking":
        return _prepare_particle(lane, method)
    raise AssertionError(lane.app)


__all__ = [
    "LANES", "LANE_BY_ID", "METHODS", "V2", "V3", "V4",
    "prepare_three_way",
]
