from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }


def _import_shapely():
    try:
        from shapely.geometry import Polygon as ShapelyPolygon  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised on pods with optional oracle dep
        raise RuntimeError(
            "Goal3474 oracle requires the optional Shapely/GEOS package. "
            "Install it only as oracle tooling, not as an RTDL runtime dependency."
        ) from exc
    try:
        from shapely.validation import make_valid  # type: ignore
    except Exception:  # pragma: no cover - Shapely 1.x fallback
        make_valid = None
    try:
        import shapely  # type: ignore

        version = str(getattr(shapely, "__version__", "unknown"))
    except Exception:  # pragma: no cover
        version = "unknown"
    return ShapelyPolygon, make_valid, version


def _polygon_vertices(record) -> tuple[tuple[float, float], ...]:
    vertices = tuple((float(x), float(y)) for x, y in record.vertices)
    if len(vertices) >= 2 and vertices[0] == vertices[-1]:
        return vertices[:-1]
    return vertices


def _build_oracle_polygon(record, ShapelyPolygon, make_valid):
    raw = ShapelyPolygon(_polygon_vertices(record))
    if raw.is_empty:
        return raw, "empty_raw"
    if raw.is_valid:
        return raw, "valid"
    if make_valid is not None:
        fixed = make_valid(raw)
        return fixed, "make_valid"
    return raw.buffer(0), "buffer0"


def _build_oracle_polygons(records, ShapelyPolygon, make_valid):
    geometries = []
    status_counts: dict[str, int] = {}
    for record in records:
        geometry, status = _build_oracle_polygon(record, ShapelyPolygon, make_valid)
        geometries.append(geometry)
        status_counts[status] = status_counts.get(status, 0) + 1
    return tuple(geometries), status_counts


def _synthetic_oracle(ShapelyPolygon, make_valid) -> dict[str, object]:
    class _Shape:
        def __init__(self, vertices):
            self.vertices = tuple(vertices)

    left = _Shape(((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)))
    right = _Shape(((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)))
    left_polygon, left_status = _build_oracle_polygon(left, ShapelyPolygon, make_valid)
    right_polygon, right_status = _build_oracle_polygon(right, ShapelyPolygon, make_valid)
    area = float(left_polygon.intersection(right_polygon).area)
    expected = 1.0
    return {
        "expected_area": expected,
        "measured_area": area,
        "absolute_error": abs(area - expected),
        "left_status": left_status,
        "right_status": right_status,
        "passed": abs(area - expected) <= 1.0e-12,
    }


def _compute_exact_areas(
    *,
    left_geometries,
    right_geometries,
    left_ordinals,
    right_ordinals,
    progress_label: str,
    progress_every: int,
) -> dict[str, object]:
    row_count = int(len(left_ordinals))
    positive_count = 0
    zero_count = 0
    exception_count = 0
    total_area = 0.0
    max_area = 0.0
    sample_rows: list[dict[str, object]] = []
    started = time.perf_counter()

    for index, (left_ordinal, right_ordinal) in enumerate(zip(left_ordinals, right_ordinals)):
        if progress_every > 0 and index > 0 and index % progress_every == 0:
            elapsed = time.perf_counter() - started
            print(
                f"[{progress_label}] exact_oracle_rows={index}/{row_count} elapsed={elapsed:.3f}s",
                flush=True,
            )
        try:
            area = float(left_geometries[int(left_ordinal)].intersection(right_geometries[int(right_ordinal)]).area)
        except Exception as exc:  # pragma: no cover - captured in pod artifacts if a topology issue appears
            exception_count += 1
            if len(sample_rows) < 8:
                sample_rows.append(
                    {
                        "row": int(index),
                        "left_ordinal": int(left_ordinal),
                        "right_ordinal": int(right_ordinal),
                        "exception": f"{type(exc).__name__}: {exc}",
                    }
                )
            continue
        total_area += area
        max_area = max(max_area, area)
        if area > 0.0:
            positive_count += 1
            if len(sample_rows) < 8:
                sample_rows.append(
                    {
                        "row": int(index),
                        "left_ordinal": int(left_ordinal),
                        "right_ordinal": int(right_ordinal),
                        "area": area,
                    }
                )
        else:
            zero_count += 1

    return {
        "row_count": row_count,
        "positive_area_row_count": positive_count,
        "zero_area_row_count": zero_count,
        "exception_count": exception_count,
        "total_exact_area": total_area,
        "max_row_area": max_area,
        "sample_rows": sample_rows,
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    ShapelyPolygon, make_valid, shapely_version = _import_shapely()
    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    build_start = time.perf_counter()
    left_geometries, left_geometry_status = _build_oracle_polygons(left_shapes, ShapelyPolygon, make_valid)
    right_geometries, right_geometry_status = _build_oracle_polygons(right_shapes, ShapelyPolygon, make_valid)
    geometry_build_sec = time.perf_counter() - build_start

    synthetic = _synthetic_oracle(ShapelyPolygon, make_valid)
    row_counts: list[int] = []
    relation_times: list[float] = []
    copy_times: list[float] = []
    oracle_times: list[float] = []
    total_areas: list[float] = []
    positive_counts: list[int] = []
    exception_counts: list[int] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3474 external Shapely exact overlay-area oracle over RTDL relation rows.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            relation_start = time.perf_counter()
            with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
                cp.cuda.Stream.null.synchronize()
                relation_sec = time.perf_counter() - relation_start
                copy_start = time.perf_counter()
                ordinals = columns.as_cupy_ordinal_columns()
                left_ordinals = cp.asnumpy(ordinals["left_ordinal"]).astype("uint32", copy=False)
                right_ordinals = cp.asnumpy(ordinals["right_ordinal"]).astype("uint32", copy=False)
                cp.cuda.Stream.null.synchronize()
                copy_sec = time.perf_counter() - copy_start

            oracle_start = time.perf_counter()
            oracle = _compute_exact_areas(
                left_geometries=left_geometries,
                right_geometries=right_geometries,
                left_ordinals=left_ordinals,
                right_ordinals=right_ordinals,
                progress_label="goal3474",
                progress_every=int(args.progress_every),
            )
            oracle_sec = time.perf_counter() - oracle_start
            row_counts.append(int(oracle["row_count"]))
            relation_times.append(relation_sec)
            copy_times.append(copy_sec)
            oracle_times.append(oracle_sec)
            total_areas.append(float(oracle["total_exact_area"]))
            positive_counts.append(int(oracle["positive_area_row_count"]))
            exception_counts.append(int(oracle["exception_count"]))
            run = {
                "iteration": index,
                "row_count": int(oracle["row_count"]),
                "relation_columns_sec": relation_sec,
                "ordinal_copy_to_host_sec": copy_sec,
                "shapely_exact_overlay_oracle_sec": oracle_sec,
                "oracle": oracle,
                "claim_boundary": _claim_boundary(),
            }
            runs.append(run)
            print(
                "[goal3474] "
                f"iteration={index} rows={oracle['row_count']} positive={oracle['positive_area_row_count']} "
                f"exceptions={oracle['exception_count']} total_area={oracle['total_exact_area']:.12f} "
                f"relation={relation_sec:.6f}s copy={copy_sec:.6f}s oracle={oracle_sec:.6f}s",
                flush=True,
            )

    return {
        "schema": "rtdl.goal3474.shape_pair_exact_overlay_area_shapely_oracle.v1",
        "goal": 3474,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "shapely_version": shapely_version,
        "oracle_dependency_scope": "external_cpu_correctness_oracle_not_rtdl_runtime_dependency",
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "left_geometry_status_counts": left_geometry_status,
        "right_geometry_status_counts": right_geometry_status,
        "geometry_build_sec": geometry_build_sec,
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "synthetic_exact_overlay_fixture": synthetic,
        "row_counts": row_counts,
        "positive_area_row_counts": positive_counts,
        "exception_counts": exception_counts,
        "total_exact_areas": total_areas,
        "all_row_counts_stable": len(set(row_counts)) == 1,
        "all_total_exact_areas_stable": len(set(round(value, 12) for value in total_areas)) == 1,
        "all_oracle_exception_counts_zero": all(count == 0 for count in exception_counts),
        "relation_columns_sec": _stats(relation_times),
        "ordinal_copy_to_host_sec": _stats(copy_times),
        "shapely_exact_overlay_oracle_sec": _stats(oracle_times),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3474 Shapely exact overlay-area oracle over RTDL relation rows.")
    parser.add_argument(
        "--left-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["synthetic_exact_overlay_fixture"]["passed"]:
        raise SystemExit(1)
    if not payload["all_row_counts_stable"]:
        raise SystemExit(1)
    if not payload["all_total_exact_areas_stable"]:
        raise SystemExit(1)
    if not payload["all_oracle_exception_counts_zero"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
