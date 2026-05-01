#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_ann_candidate_app as ann_app
from examples import rtdl_barnes_hut_force_app as barnes_app
from examples import rtdl_facility_knn_assignment as facility_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact


GOAL = "Goal973 deferred decision baseline collector"
DATE = "2026-04-26"
DEFAULT_COPIES = 20_000
DEFAULT_BODY_COUNT = 4096


def _time(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    return fn(), time.perf_counter() - start


def _median(samples: list[float]) -> float:
    return float(statistics.median(samples)) if samples else 0.0


def _phases(input_sec: float, query_samples: list[float], post_samples: list[float] | None = None) -> dict[str, float]:
    return {
        "input_build": float(input_sec),
        "backend_prepare": 0.0,
        "native_query": _median(query_samples),
        "materialization_or_copyback": 0.0,
        "postprocess": _median(post_samples or [0.0]),
    }


def _artifact_path(app: str, path_name: str, baseline_name: str) -> Path:
    return (
        ROOT
        / "docs"
        / "reports"
        / f"goal835_baseline_{app}_{path_name}_{baseline_name}_2026-04-23.json"
    )


def _write(
    *,
    app: str,
    path_name: str,
    baseline_name: str,
    source_backend: str,
    benchmark_scale: dict[str, Any] | None,
    repeats: int,
    parity: bool,
    phase_seconds: dict[str, float],
    summary: dict[str, Any],
    notes: list[str],
    validation: dict[str, Any],
) -> dict[str, Any]:
    row = load_goal835_row(app=app, path_name=path_name, baseline_name=baseline_name)
    artifact = build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend=source_backend,
        benchmark_scale=benchmark_scale,
        repeated_runs=repeats,
        correctness_parity=parity,
        phase_seconds=phase_seconds,
        summary=summary,
        notes=notes,
        validation=validation,
    )
    write_baseline_artifact(_artifact_path(app, path_name, baseline_name), artifact)
    return artifact


def _facility_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    case, input_sec = _time(lambda: facility_app.make_facility_knn_case(copies=copies))
    radius = facility_app.DEFAULT_SERVICE_RADIUS
    oracle, oracle_sec = _time(
        lambda: facility_app.facility_coverage_oracle(case["customers"], case["depots"], radius=radius)
    )
    artifacts: list[dict[str, Any]] = [
        _write(
            app="facility_knn_assignment",
            path_name="coverage_threshold_prepared",
            baseline_name="cpu_oracle_same_semantics",
            source_backend="cpu_oracle",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=True,
            phase_seconds=_phases(input_sec, [oracle_sec]),
            summary=oracle,
            notes=["CPU oracle computes the same coverage-threshold decision as the OptiX prepared path."],
            validation={"matches_reference": True, "reference": "deterministic facility coverage oracle"},
        )
    ]

    query_samples: list[float] = []
    post_samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(repeats):
        rows, query_sec = _time(lambda: facility_app._run_rows("embree", case, primary_only=True))

        def summarize() -> dict[str, Any]:
            by_query = {int(row["query_id"]): row for row in rows}
            uncovered = [
                customer.id
                for customer in case["customers"]
                if float(by_query[customer.id]["distance"]) > radius
            ]
            return {
                "radius": radius,
                "customer_count": len(case["customers"]),
                "covered_customer_count": len(case["customers"]) - len(uncovered),
                "all_customers_covered": not uncovered,
                "uncovered_customer_ids": uncovered,
            }

        last_summary, post_sec = _time(summarize)
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    artifacts.append(
        _write(
            app="facility_knn_assignment",
            path_name="coverage_threshold_prepared",
            baseline_name="best_available_non_optix_backend_same_semantics",
            source_backend="embree",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=last_summary == oracle,
            phase_seconds=_phases(input_sec, query_samples, post_samples),
            summary=last_summary,
            notes=["Embree K=1 nearest-depot rows are reduced to the same coverage-threshold decision."],
            validation={"matches_reference": last_summary == oracle, "reference_summary": oracle},
        )
    )
    return artifacts


def _hausdorff_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    case, input_sec = _time(lambda: hausdorff_app.make_authored_point_sets(copies=copies))
    radius = 0.4
    oracle_full = hausdorff_app.expected_tiled_hausdorff(copies=copies)
    oracle = {
        "radius": radius,
        "within_threshold": float(oracle_full["hausdorff_distance"]) <= radius,
        "hausdorff_distance": oracle_full["hausdorff_distance"],
        "point_count_a": len(case["points_a"]),
        "point_count_b": len(case["points_b"]),
    }
    artifacts = [
        _write(
            app="hausdorff_distance",
            path_name="directed_threshold_prepared",
            baseline_name="cpu_oracle_same_semantics",
            source_backend="cpu_oracle",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=True,
            phase_seconds=_phases(input_sec, [0.0]),
            summary=oracle,
            notes=["CPU oracle uses deterministic tiled Hausdorff summary and applies the same threshold decision."],
            validation={"matches_reference": True, "reference": "expected_tiled_hausdorff"},
        )
    ]

    query_samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(repeats):
        payload, query_sec = _time(
            lambda: hausdorff_app.run_app(
                "embree",
                copies=copies,
                embree_result_mode="directed_summary",
            )
        )
        last_summary = {
            "radius": radius,
            "within_threshold": float(payload["hausdorff_distance"]) <= radius,
            "hausdorff_distance": payload["hausdorff_distance"],
            "point_count_a": payload["point_count_a"],
            "point_count_b": payload["point_count_b"],
        }
        query_samples.append(query_sec)
    artifacts.append(
        _write(
            app="hausdorff_distance",
            path_name="directed_threshold_prepared",
            baseline_name="best_available_non_optix_backend_same_semantics",
            source_backend="embree",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=last_summary == oracle,
            phase_seconds=_phases(input_sec, query_samples),
            summary=last_summary,
            notes=["Embree directed-Hausdorff summary is reduced to the same threshold decision."],
            validation={"matches_reference": last_summary == oracle, "reference_summary": oracle},
        )
    )
    return artifacts


def _ann_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    case, input_sec = _time(lambda: ann_app.make_ann_case(copies=copies))
    radius = 0.2
    oracle = ann_app.expected_tiled_candidate_threshold(copies=copies, radius=radius)
    artifacts = [
        _write(
            app="ann_candidate_search",
            path_name="candidate_threshold_prepared",
            baseline_name="cpu_oracle_same_semantics",
            source_backend="cpu_oracle",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=True,
            phase_seconds=_phases(input_sec, [0.0]),
            summary=oracle,
            notes=["CPU oracle computes the same candidate-coverage threshold decision as the OptiX prepared path."],
            validation={"matches_reference": True, "reference": "expected_tiled_candidate_threshold"},
        )
    ]
    query_samples: list[float] = []
    post_samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(repeats):
        rows, query_sec = _time(lambda: ann_app._run_rows("embree", case))

        def summarize() -> dict[str, Any]:
            by_query = {int(row["query_id"]): row for row in rows}
            uncovered = [
                point.id
                for point in case["query_points"]
                if float(by_query[point.id]["distance"]) > radius
            ]
            return {
                "radius": radius,
                "query_count": len(case["query_points"]),
                "covered_query_count": len(case["query_points"]) - len(uncovered),
                "within_candidate_radius": not uncovered,
                "uncovered_query_ids": uncovered,
            }

        last_summary, post_sec = _time(summarize)
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    artifacts.append(
        _write(
            app="ann_candidate_search",
            path_name="candidate_threshold_prepared",
            baseline_name="best_available_non_optix_backend_same_semantics",
            source_backend="embree",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=last_summary == oracle,
            phase_seconds=_phases(input_sec, query_samples, post_samples),
            summary=last_summary,
            notes=["Embree candidate-subset KNN rows are reduced to the same candidate-coverage threshold decision."],
            validation={"matches_reference": last_summary == oracle, "reference_summary": oracle},
        )
    )
    return artifacts


def _barnes_hut_baselines(body_count: int, repeats: int) -> list[dict[str, Any]]:
    bodies, input_sec = _time(lambda: barnes_app.make_generated_bodies(body_count))
    nodes = barnes_app.build_one_level_quadtree(bodies)
    radius = barnes_app.NODE_DISCOVERY_RADIUS
    oracle = barnes_app.node_coverage_oracle(bodies, nodes, radius=radius)
    artifacts = [
        _write(
            app="barnes_hut_force_app",
            path_name="node_coverage_prepared",
            baseline_name="cpu_oracle_same_semantics",
            source_backend="cpu_oracle",
            benchmark_scale={"body_count": body_count, "iterations": repeats},
            repeats=repeats,
            parity=True,
            phase_seconds=_phases(input_sec, [0.0]),
            summary=oracle,
            notes=["CPU oracle computes the same node-coverage decision as the OptiX prepared path."],
            validation={"matches_reference": True, "reference": "node_coverage_oracle"},
        )
    ]
    query_samples: list[float] = []
    post_samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(repeats):
        rows, query_sec = _time(lambda: barnes_app._run_node_candidates("embree", bodies, nodes))

        def summarize() -> dict[str, Any]:
            by_query = {int(row["query_id"]) for row in rows}
            uncovered = [body.id for body in bodies if body.id not in by_query]
            return {
                "radius": radius,
                "body_count": len(bodies),
                "covered_body_count": len(bodies) - len(uncovered),
                "all_bodies_have_node_candidate": not uncovered,
                "uncovered_body_ids": uncovered,
            }

        last_summary, post_sec = _time(summarize)
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    artifacts.append(
        _write(
            app="barnes_hut_force_app",
            path_name="node_coverage_prepared",
            baseline_name="best_available_non_optix_backend_same_semantics",
            source_backend="embree",
            benchmark_scale={"body_count": body_count, "iterations": repeats},
            repeats=repeats,
            parity=last_summary == oracle,
            phase_seconds=_phases(input_sec, query_samples, post_samples),
            summary=last_summary,
            notes=["Embree fixed-radius node candidate rows are reduced to the same node-coverage decision."],
            validation={"matches_reference": last_summary == oracle, "reference_summary": oracle},
        )
    )
    return artifacts


def run(selected_apps: list[str], *, copies: int, body_count: int, repeats: int) -> dict[str, Any]:
    collectors = {
        "facility_knn_assignment": lambda: _facility_baselines(copies, repeats),
        "hausdorff_distance": lambda: _hausdorff_baselines(copies, repeats),
        "ann_candidate_search": lambda: _ann_baselines(copies, repeats),
        "barnes_hut_force_app": lambda: _barnes_hut_baselines(body_count, repeats),
    }
    artifacts: list[dict[str, Any]] = []
    for app in selected_apps:
        artifacts.extend(collectors[app]())
    return {
        "goal": GOAL,
        "date": DATE,
        "status": "ok" if all(item["status"] == "ok" for item in artifacts) else "failed",
        "artifact_count": len(artifacts),
        "apps": selected_apps,
        "copies": copies,
        "body_count": body_count,
        "repeats": repeats,
        "artifacts": [
            {
                "app": item["app"],
                "path_name": item["path_name"],
                "baseline_name": item["baseline_name"],
                "source_backend": item["source_backend"],
                "status": item["status"],
                "summary_sha256": item["summary_sha256"],
            }
            for item in artifacts
        ],
        "boundary": (
            "These are local same-semantics baseline artifacts for deferred decision rows. "
            "They do not authorize RTX speedup claims."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect local baselines for deferred decision RTX rows.")
    parser.add_argument(
        "--app",
        action="append",
        choices=("facility_knn_assignment", "hausdorff_distance", "ann_candidate_search", "barnes_hut_force_app"),
        help="app to collect; repeatable; defaults to all supported apps",
    )
    parser.add_argument("--copies", type=int, default=DEFAULT_COPIES)
    parser.add_argument("--body-count", type=int, default=DEFAULT_BODY_COUNT)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-json", default="docs/reports/goal973_deferred_decision_baselines_2026-04-26.json")
    args = parser.parse_args(argv)
    apps = args.app or [
        "facility_knn_assignment",
        "hausdorff_distance",
        "ann_candidate_search",
        "barnes_hut_force_app",
    ]
    payload = run(apps, copies=args.copies, body_count=args.body_count, repeats=args.repeats)
    output = ROOT / args.output_json
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
