from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count
import rtdsl as rt


BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan")
SCENARIOS = ("bfs", "triangle_count", "visibility_edges", "all")


def _enforce_rt_core_requirement(backend: str, scenario: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    if scenario != "visibility_edges":
        raise RuntimeError(
            "graph_analytics RT-core path is limited to --scenario visibility_edges; "
            "BFS and triangle_count native graph-ray mode remain RTX-gated before "
            "any RT-core claim"
        )


def make_visibility_edge_case(copies: int = 1) -> dict[str, tuple[object, ...]]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    observers: list[rt.Point] = []
    targets: list[rt.Point] = []
    candidate_edges: list[tuple[rt.Point, rt.Point]] = []
    blockers: list[rt.Triangle] = []
    for copy_index in range(copies):
        offset = float(copy_index * 20)
        id_offset = copy_index * 100
        copy_observers = (
            rt.Point(id=id_offset + 1, x=0.0 + offset, y=0.0),
            rt.Point(id=id_offset + 2, x=0.0 + offset, y=2.0),
        )
        copy_targets = (
            rt.Point(id=id_offset + 10, x=10.0 + offset, y=0.0),
            rt.Point(id=id_offset + 11, x=10.0 + offset, y=2.0),
        )
        observers.extend(copy_observers)
        targets.extend(copy_targets)
        candidate_edges.extend((observer, target) for observer in copy_observers for target in copy_targets)
        blockers.append(
            rt.Triangle(
                id=id_offset + 100,
                x0=5.0 + offset,
                y0=-1.0,
                x1=5.0 + offset,
                y1=1.0,
                x2=6.0 + offset,
                y2=0.0,
            )
        )
    return {
        "observers": tuple(observers),
        "targets": tuple(targets),
        "candidate_edges": tuple(candidate_edges),
        "blockers": tuple(blockers),
    }


def _pack_visibility_summary_rays(copies: int):
    input_start = time.perf_counter()
    offsets = [float(copy_index * 20) for copy_index in range(copies)]
    id_offsets = [copy_index * 100 for copy_index in range(copies)]
    ray_count = copies * 4
    blocker_ids = [id_offset + 100 for id_offset in id_offsets]
    blocker_x0 = [offset + 5.0 for offset in offsets]
    blocker_y0 = [-1.0] * copies
    blocker_x1 = [offset + 5.0 for offset in offsets]
    blocker_y1 = [1.0] * copies
    blocker_x2 = [offset + 6.0 for offset in offsets]
    blocker_y2 = [0.0] * copies
    ids = list(range(ray_count))
    ox = [offset for offset in offsets for _ in range(4)]
    oy = [value for _ in range(copies) for value in (0.0, 0.0, 2.0, 2.0)]
    dx = [10.0] * ray_count
    dy = [value for _ in range(copies) for value in (0.0, 2.0, -2.0, 0.0)]
    tmax = [1.0] * ray_count
    input_construction_sec = time.perf_counter() - input_start

    blocker_pack_start = time.perf_counter()
    try:
        blockers = rt.pack_triangles_2d_from_arrays(
            ids=blocker_ids,
            x0=blocker_x0,
            y0=blocker_y0,
            x1=blocker_x1,
            y1=blocker_y1,
            x2=blocker_x2,
            y2=blocker_y2,
        )
        blocker_pack_mode = "numpy_packed_triangles"
    except RuntimeError:
        blockers = rt.pack_triangles(
            ids=blocker_ids,
            x0=blocker_x0,
            y0=blocker_y0,
            x1=blocker_x1,
            y1=blocker_y1,
            x2=blocker_x2,
            y2=blocker_y2,
            dimension=2,
        )
        blocker_pack_mode = "packed_triangles"
    blocker_pack_sec = time.perf_counter() - blocker_pack_start

    ray_pack_start = time.perf_counter()
    try:
        rays = rt.pack_rays_2d_from_arrays(ids=ids, ox=ox, oy=oy, dx=dx, dy=dy, tmax=tmax)
        ray_pack_mode = "numpy_packed_rays"
    except RuntimeError:
        rays = tuple(
            rt.Ray2D(id=ids[index], ox=ox[index], oy=oy[index], dx=dx[index], dy=dy[index], tmax=tmax[index])
            for index in range(ray_count)
        )
        ray_pack_mode = "python_ray_object_fallback"
    ray_pack_sec = time.perf_counter() - ray_pack_start
    return {
        "blockers": blockers,
        "rays": rays,
        "ray_count": ray_count,
        "observer_count": copies * 2,
        "target_count": copies * 2,
        "blocker_count": copies,
        "ray_pack_mode": ray_pack_mode,
        "blocker_pack_mode": blocker_pack_mode,
        "input_construction_sec": input_construction_sec,
        "blocker_pack_sec": blocker_pack_sec,
        "ray_pack_sec": ray_pack_sec,
    }


def _run_visibility_edges(backend: str, copies: int, output_mode: str) -> dict[str, Any]:
    visibility_backend = "cpu" if backend == "cpu_python_reference" else backend
    if backend == "optix" and output_mode == "summary":
        packed_case = _pack_visibility_summary_rays(copies)
        rays = packed_case["rays"]
        scene_prepare_start = time.perf_counter()
        with rt.prepare_optix_ray_triangle_any_hit_2d(packed_case["blockers"]) as prepared_scene:
            scene_prepare_sec = time.perf_counter() - scene_prepare_start
            ray_prepare_start = time.perf_counter()
            with rt.prepare_optix_rays_2d(rays) as prepared_rays:
                ray_prepare_sec = time.perf_counter() - ray_prepare_start
                query_start = time.perf_counter()
                blocked_count = int(prepared_scene.count(prepared_rays))
                query_sec = time.perf_counter() - query_start
        rows = ()
        postprocess_start = time.perf_counter()
        visible_count = int(packed_case["ray_count"]) - blocked_count
        native_continuation_active = True
        native_continuation_backend = "optix_prepared_visibility_anyhit_count"
        postprocess_sec = time.perf_counter() - postprocess_start
        run_phases = {
            "input_construction_sec": float(packed_case["input_construction_sec"]),
            "blocker_pack_sec": float(packed_case["blocker_pack_sec"]),
            "ray_pack_sec": float(packed_case["ray_pack_sec"]),
            "scene_prepare_sec": scene_prepare_sec,
            "ray_prepare_sec": ray_prepare_sec,
            "query_anyhit_count_sec": query_sec,
            "summary_postprocess_sec": postprocess_sec,
        }
        observer_count = int(packed_case["observer_count"])
        target_count = int(packed_case["target_count"])
        candidate_edge_count = int(packed_case["ray_count"])
        blocker_count = int(packed_case["blocker_count"])
        ray_pack_mode = str(packed_case["ray_pack_mode"])
        blocker_pack_mode = str(packed_case["blocker_pack_mode"])
    else:
        input_start = time.perf_counter()
        case = make_visibility_edge_case(copies)
        input_construction_sec = time.perf_counter() - input_start
        query_start = time.perf_counter()
        rows = rt.visibility_pair_rows(
            case["candidate_edges"],
            case["blockers"],
            backend=visibility_backend,
        )
        query_sec = time.perf_counter() - query_start
        postprocess_start = time.perf_counter()
        visible_count = sum(1 for row in rows if int(row["visible"]) == 1)
        blocked_count = len(rows) - visible_count
        native_continuation_active = backend == "optix"
        native_continuation_backend = "optix_visibility_pair_rows" if backend == "optix" else "none"
        postprocess_sec = time.perf_counter() - postprocess_start
        run_phases = {
            "input_construction_sec": input_construction_sec,
            "query_visibility_pair_rows_sec": query_sec,
            "summary_postprocess_sec": postprocess_sec,
        }
        observer_count = len(case["observers"])
        target_count = len(case["targets"])
        candidate_edge_count = len(case["candidate_edges"])
        blocker_count = len(case["blockers"])
        ray_pack_mode = "not_applicable"
        blocker_pack_mode = "not_applicable"
    return {
        "app": "graph_visibility_edges",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "observer_count": observer_count,
        "target_count": target_count,
        "candidate_edge_count": candidate_edge_count,
        "blocker_count": blocker_count,
        "row_count": candidate_edge_count,
        "rows": rows if output_mode == "rows" else [],
        "summary": {
            "visible_edge_count": visible_count,
            "blocked_edge_count": blocked_count,
        },
        "run_phases": run_phases,
        "ray_pack_mode": ray_pack_mode,
        "blocker_pack_mode": blocker_pack_mode,
        "native_continuation_active": native_continuation_active,
        "native_continuation_backend": native_continuation_backend,
        "rt_core_accelerated": backend == "optix",
        "boundary": (
            "Graph visibility_edges maps candidate graph edges to RTDL visibility "
            "rays and uses ray/triangle any-hit traversal. It is not BFS, "
            "triangle-count, shortest path, or general graph database acceleration."
        ),
    }


def run_app(
    backend: str,
    scenario: str = "all",
    copies: int = 1,
    output_mode: str = "rows",
    *,
    require_rt_core: bool = False,
    optix_graph_mode: str = "auto",
) -> dict[str, Any]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")
    if copies <= 0:
        raise ValueError("copies must be positive")
    if output_mode not in {"rows", "summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    if optix_graph_mode not in {"auto", "host_indexed", "native"}:
        raise ValueError(f"unsupported optix_graph_mode: {optix_graph_mode}")
    _enforce_rt_core_requirement(backend, scenario, require_rt_core)

    sections: dict[str, Any] = {}
    if scenario in {"bfs", "all"}:
        sections["bfs"] = rtdl_graph_bfs.run_backend(
            backend,
            copies=copies,
            output_mode=output_mode,
            optix_graph_mode=optix_graph_mode,
        )
    if scenario in {"triangle_count", "all"}:
        sections["triangle_count"] = rtdl_graph_triangle_count.run_backend(
            backend,
            copies=copies,
            output_mode=output_mode,
            optix_graph_mode=optix_graph_mode,
        )
    if scenario in {"visibility_edges", "all"}:
        sections["visibility_edges"] = _run_visibility_edges(backend, copies=copies, output_mode=output_mode)
    native_continuation_backends = tuple(
        str(section.get("native_continuation_backend", "none"))
        for section in sections.values()
        if section.get("native_continuation_active")
    )
    phase_totals: dict[str, float] = {}
    for section in sections.values():
        for name, value in section.get("run_phases", {}).items():
            phase_totals[name] = phase_totals.get(name, 0.0) + float(value)

    return {
        "app": "graph_analytics",
        "backend": backend,
        "scenario": scenario,
        "copies": copies,
        "output_mode": output_mode,
        "optix_graph_mode": optix_graph_mode if backend == "optix" else "not_applicable",
        "sections": sections,
        "data_flow": [
            "application graph data",
            "bounded RTDL graph kernels",
            "BFS discovery rows and triangle rows",
            "visibility edge rows for the RT-core sub-path",
            "native C++ summary continuation for BFS and triangle_count summary mode",
            "Python-owned unified app JSON assembly",
        ],
        "unifies": [
            "examples/rtdl_graph_bfs.py",
            "examples/rtdl_graph_triangle_count.py",
        ],
        "optix_performance": {
            "class": rt.optix_app_performance_support("graph_analytics").performance_class,
            "note": rt.optix_app_performance_support("graph_analytics").note,
        },
        "native_continuation_active": bool(native_continuation_backends),
        "native_continuation_backend": (
            "+".join(native_continuation_backends)
            if native_continuation_backends
            else "none"
        ),
        "graph_phase_totals_sec": phase_totals,
        "phase_contract": (
            "Graph phase totals split fixture construction, ray packing or row "
            "query/materialization, prepared any-hit count, and summary "
            "postprocess where the public app can observe them. They are local "
            "diagnostics, not public RTX speedup claims."
        ),
        "ray_tracing_accelerated": backend == "embree" or (
            backend == "optix" and scenario == "visibility_edges"
        ),
        "ray_tracing_note": (
            "For Embree, BFS and triangle_count now use ray traversal over "
            "graph-edge primitives for candidate generation, and visibility_edges "
            "uses ray/triangle any-hit. For OptiX, BFS and triangle_count have "
            "an explicit native graph-ray mode behind --optix-graph-mode native, "
            "visibility_edges summary mode uses prepared any-hit count to avoid "
            "row materialization, and graph summary mode uses native C++ "
            "continuation after rows are produced. Only visibility_edges is a "
            "current RT-core claim until cloud validation promotes the graph-ray path."
        ),
        "rt_core_accelerated": backend == "optix" and scenario == "visibility_edges",
        "honesty_boundary": (
            "Unified app over bounded graph kernels. Embree BFS and triangle_count "
            "use CPU ray-tracing traversal for candidate generation. Only "
            "visibility_edges is an OptiX ray/triangle any-hit RT-core candidate; "
            "OptiX BFS and triangle_count remain host-indexed by default, and "
            "native graph-ray mode remains gated. BFS and triangle_count summary "
            "mode uses native C++ continuation, but this is not a full graph "
            "database or distributed graph analytics system."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Unified RTDL graph analytics app over BFS and triangle-count kernels."
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=BACKENDS,
    )
    parser.add_argument(
        "--scenario",
        default="all",
        choices=SCENARIOS,
        help="Run one graph scenario or the complete unified app.",
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic graph fixture this many times.")
    parser.add_argument("--output-mode", default="rows", choices=("rows", "summary"))
    parser.add_argument("--optix-graph-mode", default="auto", choices=("auto", "host_indexed", "native"))
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                args.scenario,
                copies=args.copies,
                output_mode=args.output_mode,
                require_rt_core=args.require_rt_core,
                optix_graph_mode=args.optix_graph_mode,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
