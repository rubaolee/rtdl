#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_barnes_hut_force_app as barnes_app
from examples import rtdl_facility_knn_assignment as facility_app


GOAL = "Goal1101 current-contract non-OptiX baseline profiler"
DATE = "2026-04-29"
SCHEMA_VERSION = "goal1101_current_contract_non_optix_baseline_v1"


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _host() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def _source_commit() -> str | None:
    if os.environ.get("RTDL_SOURCE_COMMIT"):
        return os.environ["RTDL_SOURCE_COMMIT"]
    source_file = ROOT / ".rtdl_source_commit"
    if source_file.exists():
        value = source_file.read_text(encoding="utf-8").strip()
        return value or None
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode == 0:
        value = completed.stdout.strip()
        return value or None
    return None


def _facility_copy_offset(point: rt.Point) -> float:
    return float((int(point.id) // 100) * 6)


def _recenter_facility_points(points: tuple[rt.Point, ...]) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=point.id, x=float(point.x) - _facility_copy_offset(point), y=point.y) for point in points)


def _canonical_facility_depots() -> tuple[rt.Point, ...]:
    return facility_app.make_facility_knn_case(copies=1)["depots"]


def _build_facility_case(copies: int) -> tuple[tuple[rt.Point, ...], tuple[rt.Point, ...], float]:
    case, case_sec = _time_call(lambda: facility_app.make_facility_knn_case(copies=copies))
    customers, recenter_sec = _time_call(lambda: _recenter_facility_points(case["customers"]))
    depots, depot_sec = _time_call(_canonical_facility_depots)
    return customers, depots, case_sec + recenter_sec + depot_sec


def _build_barnes_case(
    body_count: int,
    barnes_tree_depth: int,
    hit_threshold: int,
) -> tuple[
    tuple[barnes_app.Body, ...],
    tuple[barnes_app.QuadNode, ...],
    tuple[rt.Point, ...],
    tuple[rt.Point, ...],
    float,
]:
    def build_case() -> tuple[
        tuple[barnes_app.Body, ...],
        tuple[barnes_app.QuadNode, ...],
        tuple[rt.Point, ...],
        tuple[rt.Point, ...],
    ]:
        bodies = barnes_app.make_generated_bodies(body_count)
        nodes = (
            barnes_app.build_one_level_quadtree(bodies)
            if barnes_tree_depth == 1 and hit_threshold == 1
            else barnes_app.build_fixed_depth_quadtree_cells(bodies, depth=barnes_tree_depth)
        )
        return bodies, nodes, barnes_app._body_points(bodies), barnes_app._node_points(nodes)

    (bodies, nodes, body_points, node_points), input_sec = _time_call(build_case)
    return bodies, nodes, body_points, node_points, input_sec


def _profile_threshold(
    *,
    backend: str,
    build_points: tuple[rt.Point, ...],
    query_points: tuple[rt.Point, ...],
    radius: float,
    hit_threshold: int,
    iterations: int,
    skip_validation: bool,
    oracle_fn: Callable[[], dict[str, Any]],
    oracle_result_key: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    pack_sec = 0.0
    prepare_sec = 0.0
    close_sec = 0.0
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last: dict[str, Any] = {}

    if backend == "cpu_oracle":
        for _ in range(iterations):
            oracle, query_sec = _time_call(oracle_fn)
            query_samples.append(query_sec)
            all_covered, postprocess_sec = _time_call(lambda: bool(oracle[oracle_result_key]))
            postprocess_samples.append(postprocess_sec)
            last = {
                "radius": radius,
                "query_count": len(query_points),
                "build_count": len(build_points),
                "hit_threshold": hit_threshold,
                "threshold_reached_count": len(query_points) if all_covered else None,
                "all_queries_reached_threshold": all_covered,
                "oracle_all_queries_reached_threshold": all_covered,
                "matches_oracle": True,
            }
    elif backend == "embree":
        prepared, prepare_sec = _time_call(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(build_points))
        try:
            for _ in range(iterations):
                rows, query_sec = _time_call(
                    lambda: prepared.run(query_points, radius=radius, threshold=hit_threshold)
                )
                reached_count = sum(1 for row in rows if int(row["threshold_reached"]) != 0)
                query_samples.append(query_sec)
                all_covered, postprocess_sec = _time_call(lambda: int(reached_count) == len(query_points))
                postprocess_samples.append(postprocess_sec)
                oracle_value: bool | None = None
                if not skip_validation:
                    oracle, validation_sec = _time_call(oracle_fn)
                    oracle_value = bool(oracle[oracle_result_key])
                    validation_samples.append(validation_sec)
                last = {
                    "radius": radius,
                    "query_count": len(query_points),
                    "build_count": len(build_points),
                    "hit_threshold": hit_threshold,
                    "threshold_reached_count": int(reached_count),
                    "all_queries_reached_threshold": all_covered,
                    "oracle_all_queries_reached_threshold": oracle_value,
                    "matches_oracle": None if skip_validation else all_covered == oracle_value,
                }
        finally:
            _, close_sec = _time_call(prepared.close)
    else:
        raise ValueError("backend must be cpu_oracle or embree")

    return (
        {
            "point_pack_sec": pack_sec,
            "backend_prepare_sec": prepare_sec,
            "native_query_sec": _stats(query_samples),
            "python_postprocess_sec": _stats(postprocess_samples),
            "validation_sec": _stats(validation_samples),
            "backend_close_sec": close_sec,
        },
        last,
    )


def run_profile(
    *,
    scenario: str,
    backend: str,
    copies: int,
    body_count: int,
    iterations: int,
    radius: float | None,
    barnes_tree_depth: int,
    hit_threshold: int,
    skip_validation: bool,
) -> dict[str, Any]:
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    if copies < 1:
        raise ValueError("copies must be at least 1")
    if body_count < 1:
        raise ValueError("body_count must be at least 1")
    if barnes_tree_depth < 1:
        raise ValueError("barnes_tree_depth must be at least 1")
    if hit_threshold < 1:
        raise ValueError("hit_threshold must be at least 1")

    if scenario == "facility_service_coverage_recentered":
        customers, depots, input_sec = _build_facility_case(copies)
        effective_radius = facility_app.DEFAULT_SERVICE_RADIUS if radius is None else radius
        timings, result = _profile_threshold(
            backend=backend,
            build_points=depots,
            query_points=customers,
            radius=effective_radius,
            hit_threshold=1,
            iterations=iterations,
            skip_validation=skip_validation,
            oracle_fn=lambda: facility_app.facility_coverage_oracle(customers, depots, radius=effective_radius),
            oracle_result_key="all_customers_covered",
        )
        result["coordinate_mapping"] = "copy_local_recentered_queries_canonical_depots"
        path_name = "coverage_threshold_prepared_recentered"
    elif scenario == "barnes_hut_node_coverage":
        bodies, nodes, body_points, node_points, input_sec = _build_barnes_case(
            body_count,
            barnes_tree_depth,
            hit_threshold,
        )
        effective_radius = barnes_app.NODE_DISCOVERY_RADIUS if radius is None else radius
        timings, result = _profile_threshold(
            backend=backend,
            build_points=node_points,
            query_points=body_points,
            radius=effective_radius,
            hit_threshold=hit_threshold,
            iterations=iterations,
            skip_validation=skip_validation,
            oracle_fn=lambda: barnes_app.node_coverage_oracle(bodies, nodes, radius=effective_radius, threshold=hit_threshold),
            oracle_result_key="all_bodies_have_node_candidate",
        )
        result.update({"node_count": len(nodes), "barnes_tree_depth": barnes_tree_depth})
        path_name = "node_coverage_prepared_rich"
    else:
        raise ValueError("unsupported scenario")

    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "app": "facility_knn_assignment" if scenario == "facility_service_coverage_recentered" else "barnes_hut_force_app",
        "path_name": path_name,
        "backend": backend,
        "source_commit": _source_commit(),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": _host(),
        "parameters": {
            "scenario": scenario,
            "backend": backend,
            "copies": copies,
            "body_count": body_count,
            "iterations": iterations,
            "radius": radius,
            "barnes_tree_depth": barnes_tree_depth,
            "hit_threshold": hit_threshold,
            "skip_validation": skip_validation,
        },
        "scenario": {
            "scenario": scenario,
            "mode": backend,
            "timings_sec": {"input_build_sec": input_sec, **timings},
            "result": result,
        },
        "public_speedup_claim_authorized": False,
        "boundary": (
            "Goal1101 collects same-current-contract non-OptiX baseline artifacts for later review. "
            "It does not authorize public RTX speedup claims; claim review still requires artifact intake and 2+ AI consensus."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile current-contract non-OptiX baselines for post-pod RTX rows.")
    parser.add_argument(
        "--scenario",
        choices=("facility_service_coverage_recentered", "barnes_hut_node_coverage"),
        required=True,
    )
    parser.add_argument("--backend", choices=("cpu_oracle", "embree"), required=True)
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--body-count", type=int, default=1000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--radius", type=float)
    parser.add_argument("--barnes-tree-depth", type=int, default=1)
    parser.add_argument("--hit-threshold", type=int, default=1)
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_profile(
        scenario=args.scenario,
        backend=args.backend,
        copies=args.copies,
        body_count=args.body_count,
        iterations=args.iterations,
        radius=args.radius,
        barnes_tree_depth=args.barnes_tree_depth,
        hit_threshold=args.hit_threshold,
        skip_validation=args.skip_validation,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"scenario": args.scenario, "backend": args.backend, "output_json": str(args.output_json)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
