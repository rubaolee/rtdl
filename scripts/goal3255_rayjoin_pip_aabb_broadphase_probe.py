#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)


SCHEMA = "rtdl.goal3255.rayjoin_pip_aabb_broadphase_probe.v1"
CLAIM_BOUNDARY = {
    "release_authorized": False,
    "public_speedup_claim_authorized": False,
    "rt_core_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
}


@dataclass(frozen=True)
class _AabbRecord:
    id: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float


def _command_output(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _repo_state() -> dict[str, object]:
    return {
        "commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_command_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
    }


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _summary(values: list[float]) -> dict[str, object]:
    return {
        "samples_sec": values,
        "median_sec": _median(values),
        "min_sec": float(min(values)) if values else None,
        "max_sec": float(max(values)) if values else None,
        "count": len(values),
    }


def _int_summary(values: list[int]) -> dict[str, object]:
    return {
        "samples": values,
        "last": values[-1] if values else None,
        "consistent": len(set(values)) <= 1,
        "count": len(values),
    }


def _polygon_aabb(polygon) -> _AabbRecord:
    xs = [float(x) for x, _ in polygon.vertices]
    ys = [float(y) for _, y in polygon.vertices]
    return _AabbRecord(
        id=int(polygon.id),
        min_x=min(xs),
        min_y=min(ys),
        max_x=max(xs),
        max_y=max(ys),
    )


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return float(numerator / denominator)


def _timed_count(fn) -> tuple[int, float]:
    started = time.perf_counter()
    value = int(fn())
    return value, time.perf_counter() - started


def run_probe(
    *,
    dataset: str,
    warmup: int,
    repeat: int,
) -> dict[str, Any]:
    from rtdsl.optix_runtime import pack_points
    from rtdsl.optix_runtime import pack_polygons
    from rtdsl.optix_runtime import prepare_optix_aabb_index_2d
    from rtdsl.optix_runtime import prepare_optix_aabb_point_queries_2d
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    print(f"[goal3255] loading PIP dataset: {dataset}", flush=True)
    case = _load_rayjoin_case("pip", dataset)
    points = tuple(case.inputs["points"])
    polygons = tuple(case.inputs["polygons"])
    boxes = tuple(_polygon_aabb(polygon) for polygon in polygons)
    print(
        f"[goal3255] loaded points={len(points)} polygons={len(polygons)} boxes={len(boxes)}",
        flush=True,
    )

    phase_sec: dict[str, float] = {}
    started = time.perf_counter()
    packed_points = pack_points(records=points, dimension=2)
    phase_sec["pack_points_sec"] = time.perf_counter() - started

    started = time.perf_counter()
    packed_polygons = pack_polygons(records=polygons)
    phase_sec["pack_polygons_sec"] = time.perf_counter() - started

    print("[goal3255] preparing generic AABB broadphase index", flush=True)
    started = time.perf_counter()
    prepared_aabb = prepare_optix_aabb_index_2d(boxes)
    phase_sec["prepare_aabb_index_sec"] = time.perf_counter() - started

    started = time.perf_counter()
    prepared_point_queries = prepare_optix_aabb_point_queries_2d(points)
    phase_sec["prepare_aabb_point_queries_sec"] = time.perf_counter() - started

    print("[goal3255] preparing generic closed-shape exact membership scene", flush=True)
    started = time.perf_counter()
    prepared_closed_shape = prepare_point_closed_shape_membership_2d_optix(packed_polygons)
    phase_sec["prepare_closed_shape_sec"] = time.perf_counter() - started

    aabb_counts: list[int] = []
    aabb_timings: list[float] = []
    exact_counts: list[int] = []
    exact_timings: list[float] = []
    exact_phases: list[dict[str, object] | None] = []
    try:
        for index in range(max(0, warmup)):
            aabb = int(prepared_aabb.count_prepared_queries(prepared_point_queries, operation="point_contains"))
            exact = int(prepared_closed_shape.count_device_filtered(packed_points))
            print(
                f"[goal3255] warmup {index + 1}/{warmup}: aabb_candidates={aabb} exact_positive={exact}",
                flush=True,
            )

        for index in range(repeat):
            aabb, aabb_elapsed = _timed_count(
                lambda: prepared_aabb.count_prepared_queries(
                    prepared_point_queries,
                    operation="point_contains",
                )
            )
            exact, exact_elapsed = _timed_count(
                lambda: prepared_closed_shape.count_device_filtered(packed_points)
            )
            aabb_counts.append(aabb)
            aabb_timings.append(aabb_elapsed)
            exact_counts.append(exact)
            exact_timings.append(exact_elapsed)
            exact_phases.append(prepared_closed_shape.last_phase_timings())
            print(
                f"[goal3255] repeat {index + 1}/{repeat}: "
                f"aabb_candidates={aabb} {aabb_elapsed * 1000.0:.6f} ms; "
                f"exact_positive={exact} {exact_elapsed * 1000.0:.6f} ms",
                flush=True,
            )
    finally:
        prepared_point_queries.close()
        prepared_aabb.close()
        prepared_closed_shape.close()

    aabb_median = _median(aabb_timings)
    exact_median = _median(exact_timings)
    aabb_last = aabb_counts[-1] if aabb_counts else None
    exact_last = exact_counts[-1] if exact_counts else None
    candidate_ratio = _ratio(float(aabb_last) if aabb_last is not None else None, float(exact_last) if exact_last else None)
    speed_ratio = _ratio(aabb_median, exact_median)
    return {
        "goal": 3255,
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "pass" if aabb_counts and exact_counts else "fail",
        "repo_state": _repo_state(),
        "dataset": dataset,
        "inputs": {
            "point_count": len(points),
            "shape_count": len(polygons),
            "aabb_box_count": len(boxes),
        },
        "phase_sec": phase_sec,
        "aabb_point_contains": {
            "primitive": "AABB_INDEX_QUERY_2D",
            "operation": "point_contains",
            "candidate_counts": _int_summary(aabb_counts),
            "timing": _summary(aabb_timings),
            "prepared_point_queries": True,
            "semantic_scope": "generic point-in-AABB broadphase only; not an exact closed-shape membership result",
        },
        "closed_shape_device_filtered": {
            "primitive": "POINT_CLOSED_SHAPE_MEMBERSHIP_2D",
            "operation": "positive_count",
            "positive_counts": _int_summary(exact_counts),
            "timing": _summary(exact_timings),
            "phase_samples": exact_phases,
            "semantic_scope": "generic exact closed-shape positive membership count",
        },
        "comparison": {
            "aabb_candidate_to_exact_positive_ratio": candidate_ratio,
            "aabb_time_over_closed_shape_time_ratio": speed_ratio,
            "aabb_broadphase_is_exact_membership": False,
            "aabb_broadphase_can_replace_closed_shape_count": False,
            "next_design_implication": (
                "If AABB is much faster and the candidate ratio is bounded, a future generic "
                "device-resident candidate-to-predicate continuation may be worth building; "
                "otherwise broadphase-alone is not the RayJoin PIP gap answer."
            ),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Measure the existing generic AABB point_contains broadphase against "
            "the current closed-shape device-filtered exact count on the RayJoin PIP slice."
        )
    )
    parser.add_argument(
        "--dataset",
        default="/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb",
        help="PIP CDB dataset path.",
    )
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=9)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_probe(dataset=args.dataset, warmup=args.warmup, repeat=args.repeat)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
