#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import socket
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_ann_candidate_app as ann_app
from examples import rtdl_barnes_hut_force_app as barnes_app
from examples import rtdl_facility_knn_assignment as facility_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app


GOAL = "Goal887 prepared decision OptiX phase profiler"
DATE = "2026-04-24"
SCHEMA_VERSION = "goal887_prepared_decision_phase_contract_v1"


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


def _cloud_claim_contract(scenario: str) -> dict[str, object]:
    contracts = {
        "hausdorff_threshold": (
            "prepared OptiX fixed-radius threshold traversal for Hausdorff <= radius decisions",
            "not exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, or a whole-app speedup claim",
        ),
        "ann_candidate_coverage": (
            "prepared OptiX fixed-radius threshold traversal for ANN candidate-coverage decisions",
            "not a full ANN index, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ, or recall optimizer claim",
        ),
        "facility_service_coverage": (
            "prepared OptiX fixed-radius threshold traversal for facility service-coverage decisions",
            "not ranked nearest-depot assignment, KNN fallback assignment, or facility-location optimization",
        ),
        "barnes_hut_node_coverage": (
            "prepared OptiX fixed-radius threshold traversal for Barnes-Hut node-coverage decisions",
            "not Barnes-Hut opening-rule evaluation, force-vector reduction, or a full N-body solver",
        ),
    }
    claim_scope, non_claim = contracts[scenario]
    return {
        "claim_scope": claim_scope,
        "non_claim": non_claim,
        "required_phase_groups": (
            "input_build_sec",
            "point_pack_sec",
            "optix_prepare_sec",
            "optix_query_sec",
            "python_postprocess_sec",
            "validation_sec",
            "optix_close_sec",
        ),
        "activation_status": "deferred_until_real_rtx_phase_run_and_review",
        "cloud_policy": "include in the same deferred RTX batch after the active evidence batch succeeds",
    }


def _host() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def _pack(points: tuple[rt.Point, ...]) -> Any:
    return rt.pack_points(records=points, dimension=2)


def _profile_hausdorff(*, mode: str, copies: int, iterations: int, radius: float, skip_validation: bool) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: hausdorff_app.make_authored_point_sets(copies=copies))
    points_a = case["points_a"]
    points_b = case["points_b"]
    if mode == "dry-run":
        oracle, reference_sec = _time_call(lambda: hausdorff_app.expected_tiled_hausdorff(copies=copies))
        return {
            "scenario": "hausdorff_threshold",
            "mode": mode,
            "timings_sec": {"input_build_sec": input_sec, "cpu_reference_total_sec": reference_sec},
            "result": {
                "point_count_a": len(points_a),
                "point_count_b": len(points_b),
                "radius": radius,
                "oracle_within_threshold": float(oracle["hausdorff_distance"]) <= radius + 1e-12,
            },
        }

    packed_a, pack_a_sec = _time_call(lambda: _pack(points_a))
    packed_b, pack_b_sec = _time_call(lambda: _pack(points_b))
    prepared_b, prepare_b_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_b, max_radius=radius)
    )
    prepared_a, prepare_a_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_a, max_radius=radius)
    )
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last: dict[str, object] = {}
    try:
        for _ in range(iterations):
            count_ab, sec_ab = _time_call(
                lambda: prepared_b.count_threshold_reached(packed_a, radius=radius, threshold=1)
            )
            count_ba, sec_ba = _time_call(
                lambda: prepared_a.count_threshold_reached(packed_b, radius=radius, threshold=1)
            )
            query_samples.append(sec_ab + sec_ba)
            within, postprocess_sec = _time_call(lambda: int(count_ab) == len(points_a) and int(count_ba) == len(points_b))
            postprocess_samples.append(postprocess_sec)
            oracle_within: bool | None = None
            if not skip_validation:
                oracle, validation_sec = _time_call(lambda: hausdorff_app.expected_tiled_hausdorff(copies=copies))
                oracle_within = float(oracle["hausdorff_distance"]) <= radius + 1e-12
                validation_samples.append(validation_sec)
            last = {
                "point_count_a": len(points_a),
                "point_count_b": len(points_b),
                "radius": radius,
                "covered_a_to_b": int(count_ab),
                "covered_b_to_a": int(count_ba),
                "within_threshold": within,
                "oracle_within_threshold": oracle_within,
                "matches_oracle": None if skip_validation else within == oracle_within,
            }
    finally:
        _, close_b_sec = _time_call(prepared_b.close)
        _, close_a_sec = _time_call(prepared_a.close)
    return {
        "scenario": "hausdorff_threshold",
        "mode": mode,
        "timings_sec": {
            "input_build_sec": input_sec,
            "point_pack_sec": pack_a_sec + pack_b_sec,
            "optix_prepare_sec": prepare_a_sec + prepare_b_sec,
            "optix_query_sec": _stats(query_samples),
            "python_postprocess_sec": _stats(postprocess_samples),
            "validation_sec": _stats(validation_samples),
            "optix_close_sec": close_a_sec + close_b_sec,
        },
        "result": last,
    }


def _profile_ann(*, mode: str, copies: int, iterations: int, radius: float, skip_validation: bool) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: ann_app.make_ann_case(copies=copies))
    queries = case["query_points"]
    candidates = case["candidate_points"]
    if mode == "dry-run":
        oracle, reference_sec = _time_call(lambda: ann_app.expected_tiled_candidate_threshold(copies=copies, radius=radius))
        return {
            "scenario": "ann_candidate_coverage",
            "mode": mode,
            "timings_sec": {"input_build_sec": input_sec, "cpu_reference_total_sec": reference_sec},
            "result": oracle,
        }
    return _profile_single_threshold(
        scenario="ann_candidate_coverage",
        input_sec=input_sec,
        build_points=candidates,
        query_points=queries,
        radius=radius,
        iterations=iterations,
        skip_validation=skip_validation,
        oracle_fn=lambda: ann_app.expected_tiled_candidate_threshold(copies=copies, radius=radius),
        oracle_result_key="within_candidate_radius",
    )


def _profile_facility(*, mode: str, copies: int, iterations: int, radius: float, skip_validation: bool) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: facility_app.make_facility_knn_case(copies=copies))
    customers = case["customers"]
    depots = case["depots"]
    if mode == "dry-run":
        oracle, reference_sec = _time_call(lambda: facility_app.facility_coverage_oracle(customers, depots, radius=radius))
        return {
            "scenario": "facility_service_coverage",
            "mode": mode,
            "timings_sec": {"input_build_sec": input_sec, "cpu_reference_total_sec": reference_sec},
            "result": oracle,
        }
    return _profile_single_threshold(
        scenario="facility_service_coverage",
        input_sec=input_sec,
        build_points=depots,
        query_points=customers,
        radius=radius,
        iterations=iterations,
        skip_validation=skip_validation,
        oracle_fn=lambda: facility_app.facility_coverage_oracle(customers, depots, radius=radius),
        oracle_result_key="all_customers_covered",
    )


def _profile_barnes(*, mode: str, body_count: int, iterations: int, radius: float, skip_validation: bool) -> dict[str, Any]:
    def build_case() -> tuple[tuple[barnes_app.Body, ...], tuple[barnes_app.QuadNode, ...], tuple[rt.Point, ...], tuple[rt.Point, ...]]:
        bodies = barnes_app.make_generated_bodies(body_count)
        nodes = barnes_app.build_one_level_quadtree(bodies)
        return bodies, nodes, barnes_app._body_points(bodies), barnes_app._node_points(nodes)

    (bodies, nodes, body_points, node_points), input_sec = _time_call(build_case)
    if mode == "dry-run":
        oracle, reference_sec = _time_call(lambda: barnes_app.node_coverage_oracle(bodies, nodes, radius=radius))
        return {
            "scenario": "barnes_hut_node_coverage",
            "mode": mode,
            "timings_sec": {"input_build_sec": input_sec, "cpu_reference_total_sec": reference_sec},
            "result": oracle,
        }
    return _profile_single_threshold(
        scenario="barnes_hut_node_coverage",
        input_sec=input_sec,
        build_points=node_points,
        query_points=body_points,
        radius=radius,
        iterations=iterations,
        skip_validation=skip_validation,
        oracle_fn=lambda: barnes_app.node_coverage_oracle(bodies, nodes, radius=radius),
        oracle_result_key="all_bodies_have_node_candidate",
    )


def _profile_single_threshold(
    *,
    scenario: str,
    input_sec: float,
    build_points: tuple[rt.Point, ...],
    query_points: tuple[rt.Point, ...],
    radius: float,
    iterations: int,
    skip_validation: bool,
    oracle_fn: Callable[[], dict[str, object]],
    oracle_result_key: str,
) -> dict[str, Any]:
    packed_build, pack_build_sec = _time_call(lambda: _pack(build_points))
    packed_query, pack_query_sec = _time_call(lambda: _pack(query_points))
    prepared, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_build, max_radius=radius)
    )
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last: dict[str, object] = {}
    try:
        for _ in range(iterations):
            reached_count, query_sec = _time_call(
                lambda: prepared.count_threshold_reached(packed_query, radius=radius, threshold=1)
            )
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
                "threshold_reached_count": int(reached_count),
                "all_queries_reached_threshold": all_covered,
                "oracle_all_queries_reached_threshold": oracle_value,
                "matches_oracle": None if skip_validation else all_covered == oracle_value,
            }
    finally:
        _, close_sec = _time_call(prepared.close)
    return {
        "scenario": scenario,
        "mode": "optix",
        "timings_sec": {
            "input_build_sec": input_sec,
            "point_pack_sec": pack_build_sec + pack_query_sec,
            "optix_prepare_sec": prepare_sec,
            "optix_query_sec": _stats(query_samples),
            "python_postprocess_sec": _stats(postprocess_samples),
            "validation_sec": _stats(validation_samples),
            "optix_close_sec": close_sec,
        },
        "result": last,
    }


def run_profile(
    *,
    scenario: str,
    mode: str,
    copies: int,
    body_count: int,
    iterations: int,
    radius: float | None,
    skip_validation: bool,
) -> dict[str, Any]:
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    if copies < 1:
        raise ValueError("copies must be at least 1")
    if body_count < 1:
        raise ValueError("body_count must be at least 1")

    if scenario == "hausdorff_threshold":
        scenario_payload = _profile_hausdorff(
            mode=mode,
            copies=copies,
            iterations=iterations,
            radius=0.4 if radius is None else radius,
            skip_validation=skip_validation,
        )
    elif scenario == "ann_candidate_coverage":
        scenario_payload = _profile_ann(
            mode=mode,
            copies=copies,
            iterations=iterations,
            radius=0.2 if radius is None else radius,
            skip_validation=skip_validation,
        )
    elif scenario == "facility_service_coverage":
        scenario_payload = _profile_facility(
            mode=mode,
            copies=copies,
            iterations=iterations,
            radius=facility_app.DEFAULT_SERVICE_RADIUS if radius is None else radius,
            skip_validation=skip_validation,
        )
    elif scenario == "barnes_hut_node_coverage":
        scenario_payload = _profile_barnes(
            mode=mode,
            body_count=body_count,
            iterations=iterations,
            radius=barnes_app.NODE_DISCOVERY_RADIUS if radius is None else radius,
            skip_validation=skip_validation,
        )
    else:
        raise ValueError("unsupported scenario")

    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "cloud_claim_contract": _cloud_claim_contract(scenario),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": _host(),
        "scenario": scenario_payload,
        "parameters": {
            "mode": mode,
            "copies": copies,
            "body_count": body_count,
            "iterations": iterations,
            "radius": radius,
            "skip_validation": skip_validation,
        },
        "boundary": (
            "This profiler separates input build, point packing, OptiX preparation, "
            "prepared query, Python postprocess, validation, and close phases for "
            "prepared decision sub-paths. It does not authorize an RTX speedup claim "
            "without a real RTX run, same-semantics baselines, and independent review."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile prepared OptiX decision sub-path phases.")
    parser.add_argument(
        "--scenario",
        choices=(
            "hausdorff_threshold",
            "ann_candidate_coverage",
            "facility_service_coverage",
            "barnes_hut_node_coverage",
        ),
        required=True,
    )
    parser.add_argument("--mode", choices=("dry-run", "optix"), default="dry-run")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--body-count", type=int, default=1000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--radius", type=float)
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_profile(
        scenario=args.scenario,
        mode=args.mode,
        copies=args.copies,
        body_count=args.body_count,
        iterations=args.iterations,
        radius=args.radius,
        skip_validation=args.skip_validation,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"scenario": args.scenario, "mode": args.mode, "output_json": str(args.output_json)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
