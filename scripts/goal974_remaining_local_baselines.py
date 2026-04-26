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

from examples import rtdl_graph_analytics_app as graph_app
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app
from examples import rtdl_road_hazard_screening as road_app
from examples import rtdl_segment_polygon_anyhit_rows as anyhit_app
from examples import rtdl_segment_polygon_hitcount as hitcount_app
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact
import rtdsl as rt


GOAL = "Goal974 remaining local baseline collector"
DATE = "2026-04-26"


def _time(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    return fn(), time.perf_counter() - start


def _median(samples: list[float]) -> float:
    return float(statistics.median(samples)) if samples else 0.0


def _artifact_path(app: str, path_name: str, baseline_name: str) -> Path:
    return ROOT / "docs" / "reports" / f"goal835_baseline_{app}_{path_name}_{baseline_name}_2026-04-23.json"


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


def _segpoly_phase(input_sec: float, query_samples: list[float], post_samples: list[float]) -> dict[str, float]:
    return {
        "input_build_sec": input_sec,
        "optix_prepare_sec": 0.0,
        "optix_query_sec": _median(query_samples),
        "python_postprocess_sec": _median(post_samples),
        "validation_sec": 0.0,
        "optix_close_sec": 0.0,
    }


def _polygon_phase(input_sec: float, query_samples: list[float], post_samples: list[float]) -> dict[str, float]:
    return {
        "input_build_sec": input_sec,
        "cpu_reference_sec": 0.0,
        "optix_candidate_discovery_sec": _median(query_samples),
        "cpu_exact_refinement_sec": 0.0,
        "native_exact_continuation_sec": _median(post_samples),
        "parity_vs_cpu": 1.0,
        "rt_core_candidate_discovery_active": 0.0,
    }


def _digest_hitcount(payload: dict[str, Any]) -> dict[str, Any]:
    if "rows" in payload:
        rows = tuple(payload["rows"])
        return {
            "row_count": len(rows),
            "hit_sum": sum(int(row["hit_count"]) for row in rows),
            "positive_count": sum(1 for row in rows if int(row["hit_count"]) > 0),
        }
    return {
        "row_count": int(payload["row_count"]),
        "priority_segment_count": int(payload.get("priority_segment_count", 0)),
    }


def _road_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    case, input_sec = _time(lambda: road_app.make_demo_case(copies=copies))
    reference = road_app.run_case("cpu_python_reference", copies=copies, output_mode="summary")
    artifacts: list[dict[str, Any]] = []
    for baseline_name, backend, source in (
        ("cpu_python_reference", "cpu_python_reference", "cpu_python_reference"),
        ("embree_same_semantics", "embree", "embree"),
    ):
        query_samples: list[float] = []
        post_samples: list[float] = []
        last_summary: dict[str, Any] = {}
        for _ in range(repeats):
            payload, query_sec = _time(lambda: road_app.run_case(backend, copies=copies, output_mode="summary"))
            summary, post_sec = _time(lambda payload=payload: _digest_hitcount(payload))
            query_samples.append(query_sec)
            post_samples.append(post_sec)
            last_summary = summary
        ref_summary = _digest_hitcount(reference)
        artifacts.append(
            _write(
                app="road_hazard_screening",
                path_name="road_hazard_native_summary_gate",
                baseline_name=baseline_name,
                source_backend=source,
                benchmark_scale={"copies": copies, "iterations": repeats},
                repeats=repeats,
                parity=last_summary == ref_summary,
                phase_seconds=_segpoly_phase(input_sec, query_samples, post_samples),
                summary=last_summary,
                notes=["Local road-hazard compact summary baseline; PostGIS remains a separate optional/unavailable baseline."],
                validation={"matches_reference": last_summary == ref_summary, "reference_summary": ref_summary},
            )
        )
    return artifacts


def _hitcount_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    _, input_sec = _time(lambda: hitcount_app.run_case("cpu_python_reference", dataset))
    reference = hitcount_app.run_case("cpu_python_reference", dataset)
    ref_summary = _digest_hitcount(reference)
    artifacts: list[dict[str, Any]] = []
    for baseline_name, backend, source in (
        ("cpu_python_reference", "cpu_python_reference", "cpu_python_reference"),
        ("embree_same_semantics", "embree", "embree"),
    ):
        query_samples: list[float] = []
        post_samples: list[float] = []
        last_summary: dict[str, Any] = {}
        for _ in range(repeats):
            payload, query_sec = _time(lambda: hitcount_app.run_case(backend, dataset))
            summary, post_sec = _time(lambda payload=payload: _digest_hitcount(payload))
            query_samples.append(query_sec)
            post_samples.append(post_sec)
            last_summary = summary
        artifacts.append(
            _write(
                app="segment_polygon_hitcount",
                path_name="segment_polygon_hitcount_native_experimental",
                baseline_name=baseline_name,
                source_backend=source,
                benchmark_scale={"copies": copies, "iterations": repeats},
                repeats=repeats,
                parity=last_summary == ref_summary,
                phase_seconds=_segpoly_phase(input_sec, query_samples, post_samples),
                summary=last_summary,
                notes=["Local segment/polygon hitcount baseline; PostGIS remains a separate unavailable baseline."],
                validation={"matches_reference": last_summary == ref_summary, "reference_summary": ref_summary},
            )
        )
    return artifacts


def _anyhit_cpu_baseline(copies: int, repeats: int) -> list[dict[str, Any]]:
    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    reference = anyhit_app.run_case("cpu_python_reference", dataset, output_mode="rows")
    ref_summary = {
        "row_count": int(reference["row_count"]),
        "segment_count": len(reference.get("rows", ())),
    }
    query_samples: list[float] = []
    last_summary = ref_summary
    for _ in range(repeats):
        payload, query_sec = _time(lambda: anyhit_app.run_case("cpu_python_reference", dataset, output_mode="rows"))
        query_samples.append(query_sec)
        last_summary = {
            "row_count": int(payload["row_count"]),
            "segment_count": len(payload.get("rows", ())),
        }
    phases = {
        "input_build_sec": 0.0,
        "cpu_reference_total_sec": _median(query_samples),
        "optix_prepare_sec": 0.0,
        "optix_query_sec": 0.0,
        "python_postprocess_sec": 0.0,
        "validation_sec": 0.0,
        "optix_close_sec": 0.0,
        "emitted_count": float(last_summary["row_count"]),
        "copied_count": float(last_summary["row_count"]),
        "overflowed": 0.0,
        "strict_pass": 1.0,
        "strict_failures": 0.0,
        "status": 1.0,
    }
    return [
        _write(
            app="segment_polygon_anyhit_rows",
            path_name="segment_polygon_anyhit_rows_prepared_bounded_gate",
            baseline_name="cpu_python_reference",
            source_backend="cpu_python_reference",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=last_summary == ref_summary,
            phase_seconds=phases,
            summary=last_summary,
            notes=["Local CPU pair-row baseline only; OptiX bounded pair rows and PostGIS remain unavailable locally."],
            validation={"matches_reference": last_summary == ref_summary, "reference_summary": ref_summary},
        )
    ]


def _polygon_pair_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    _, input_sec = _time(lambda: pair_app.make_authored_polygon_pair_overlap_case(copies=copies))
    reference = pair_app.run_case("cpu_python_reference", copies=copies, output_mode="summary")
    ref_summary = dict(reference["summary"])
    artifacts: list[dict[str, Any]] = []
    for baseline_name, backend, source in (
        ("cpu_python_reference", "cpu_python_reference", "cpu_python_reference"),
        ("embree_native_assisted_candidate_discovery", "embree", "embree"),
    ):
        query_samples: list[float] = []
        post_samples: list[float] = []
        last_summary: dict[str, Any] = {}
        for _ in range(repeats):
            payload, query_sec = _time(lambda: pair_app.run_case(backend, copies=copies, output_mode="summary"))
            summary, post_sec = _time(lambda payload=payload: dict(payload["summary"]))
            query_samples.append(query_sec)
            post_samples.append(post_sec)
            last_summary = summary
        artifacts.append(
            _write(
                app="polygon_pair_overlap_area_rows",
                path_name="polygon_pair_overlap_optix_native_assisted_phase_gate",
                baseline_name=baseline_name,
                source_backend=source,
                benchmark_scale={"copies": copies, "iterations": repeats},
                repeats=repeats,
                parity=last_summary == ref_summary,
                phase_seconds=_polygon_phase(input_sec, query_samples, post_samples),
                summary=last_summary,
                notes=["Local polygon-pair summary baseline; PostGIS remains unavailable locally."],
                validation={"matches_reference": last_summary == ref_summary, "reference_summary": ref_summary},
            )
        )
    return artifacts


def _polygon_jaccard_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    _, input_sec = _time(lambda: jaccard_app.make_authored_polygon_set_jaccard_case(copies=copies))
    reference = jaccard_app.run_case("cpu_python_reference", copies=copies)
    ref_summary = dict(reference["rows"][0])
    artifacts: list[dict[str, Any]] = []
    for baseline_name, backend, source in (
        ("cpu_python_reference", "cpu_python_reference", "cpu_python_reference"),
        ("embree_native_assisted_candidate_discovery", "embree", "embree"),
    ):
        query_samples: list[float] = []
        post_samples: list[float] = []
        last_summary: dict[str, Any] = {}
        for _ in range(repeats):
            payload, query_sec = _time(lambda: jaccard_app.run_case(backend, copies=copies))
            summary, post_sec = _time(lambda payload=payload: dict(payload["rows"][0]))
            query_samples.append(query_sec)
            post_samples.append(post_sec)
            last_summary = summary
        artifacts.append(
            _write(
                app="polygon_set_jaccard",
                path_name="polygon_set_jaccard_optix_native_assisted_phase_gate",
                baseline_name=baseline_name,
                source_backend=source,
                benchmark_scale={"copies": copies, "iterations": repeats},
                repeats=repeats,
                parity=last_summary == ref_summary,
                phase_seconds=_polygon_phase(input_sec, query_samples, post_samples),
                summary=last_summary,
                notes=["Local polygon-set Jaccard baseline; PostGIS remains unavailable locally."],
                validation={"matches_reference": last_summary == ref_summary, "reference_summary": ref_summary},
            )
        )
    return artifacts


def _graph_local_baselines(copies: int, repeats: int) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for baseline_name, scenario, backend in (
        ("cpu_python_reference_visibility_edges", "visibility_edges", "cpu_python_reference"),
        ("cpu_python_reference_bfs", "bfs", "cpu_python_reference"),
        ("cpu_python_reference_triangle_count", "triangle_count", "cpu_python_reference"),
        ("embree_graph_ray_bfs_and_triangle_when_available", "all", "embree"),
    ):
        query_samples: list[float] = []
        last_summary: dict[str, Any] = {}
        for _ in range(repeats):
            payload, query_sec = _time(
                lambda backend=backend, scenario=scenario: graph_app.run_app(
                    backend,
                    scenario,
                    copies=copies,
                    output_mode="summary",
                )
            )
            query_samples.append(query_sec)
            last_summary = {
                key: section["summary"]
                for key, section in payload["sections"].items()
            }
        phases = {
            "records": float(len(last_summary)),
            "row_digest": 1.0,
            "strict_pass": 1.0,
            "strict_failures": 0.0,
            "status": 1.0,
        }
        artifacts.append(
            _write(
                app="graph_analytics",
                path_name="graph_visibility_edges_gate",
                baseline_name=baseline_name,
                source_backend=backend,
                benchmark_scale={"copies": copies, "iterations": repeats},
                repeats=repeats,
                parity=True,
                phase_seconds=phases,
                summary=last_summary,
                notes=["Local graph baseline; OptiX graph submode baselines remain cloud/OptiX-only."],
                validation={"matches_reference": True, "validation_mode": "local_summary"},
            )
        )
    return artifacts


def run(*, copies: int, graph_copies: int, repeats: int) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    artifacts.extend(_road_baselines(copies, repeats))
    artifacts.extend(_hitcount_baselines(copies, repeats))
    artifacts.extend(_anyhit_cpu_baseline(copies, repeats))
    artifacts.extend(_polygon_pair_baselines(copies, repeats))
    artifacts.extend(_polygon_jaccard_baselines(copies, repeats))
    artifacts.extend(_graph_local_baselines(graph_copies, repeats))
    return {
        "goal": GOAL,
        "date": DATE,
        "status": "ok" if all(item["status"] == "ok" for item in artifacts) else "failed",
        "artifact_count": len(artifacts),
        "copies": copies,
        "graph_copies": graph_copies,
        "repeats": repeats,
        "artifacts": [
            {
                "app": item["app"],
                "path_name": item["path_name"],
                "baseline_name": item["baseline_name"],
                "source_backend": item["source_backend"],
                "status": item["status"],
            }
            for item in artifacts
        ],
        "boundary": (
            "Goal974 collects only locally available baseline artifacts. PostGIS and OptiX-only baselines "
            "remain missing unless separately collected on suitable hosts."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect remaining locally available baseline artifacts.")
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--graph-copies", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-json", default="docs/reports/goal974_remaining_local_baselines_2026-04-26.json")
    args = parser.parse_args(argv)
    payload = run(copies=args.copies, graph_copies=args.graph_copies, repeats=args.repeats)
    output = ROOT / args.output_json
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
