from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.external_baselines import prepare_postgis_point3d_tables
from rtdsl.external_baselines import query_postgis_fixed_radius_neighbors_3d


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded three-way RTDL/cuNSearch/PostGIS KITTI fixed-radius benchmark."
    )
    parser.add_argument("source_root")
    parser.add_argument("cunsearch_source_root")
    parser.add_argument("cunsearch_build_root")
    parser.add_argument("postgis_dsn")
    parser.add_argument("--output-dir", default="build/goal283_kitti_three_way_performance")
    parser.add_argument("--query-start-index", type=int, default=0)
    parser.add_argument("--search-start-index", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=1)
    parser.add_argument("--max-points-per-frame", type=int, default=512)
    parser.add_argument("--max-total-points", type=int, default=512)
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--k-max", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    return parser.parse_args()


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def measure_reference(query_points, search_points, *, radius: float, k_max: int, repeats: int):
    times = []
    rows = ()
    for _ in range(repeats):
        t0 = time.perf_counter()
        rows = rt.fixed_radius_neighbors_cpu(query_points, search_points, radius=radius, k_max=k_max)
        times.append(time.perf_counter() - t0)
    return rows, times


def main() -> int:
    args = parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    query_manifest = out / "query_manifest.json"
    search_manifest = out / "search_manifest.json"
    query_package = out / "query_points.json"
    search_package = out / "search_points.json"
    request_path = out / "request.json"
    response_path = out / "response.json"
    compiled_dir = out / "compiled_cunsearch_driver"
    report_path = out / "three_way_report.json"

    rt.write_kitti_bounded_package_manifest(
        query_manifest,
        source_root=args.source_root,
        max_frames=args.max_frames,
        start_index=args.query_start_index,
        max_points_per_frame=args.max_points_per_frame,
        max_total_points=args.max_total_points,
    )
    rt.write_kitti_bounded_package_manifest(
        search_manifest,
        source_root=args.source_root,
        max_frames=args.max_frames,
        start_index=args.search_start_index,
        max_points_per_frame=args.max_points_per_frame,
        max_total_points=args.max_total_points,
    )
    rt.write_kitti_bounded_point_package(query_package, query_manifest)
    rt.write_kitti_bounded_point_package(search_package, search_manifest)
    query_pkg = rt.load_kitti_bounded_point_package(query_package)
    search_pkg = rt.load_kitti_bounded_point_package(search_package)

    reference_rows, reference_times = measure_reference(
        query_pkg.points,
        search_pkg.points,
        radius=args.radius,
        k_max=args.k_max,
        repeats=args.repeats,
    )

    conn = rt.connect_postgis(args.postgis_dsn)
    try:
        prep_start = time.perf_counter()
        prepare_postgis_point3d_tables(conn, query_pkg.points, search_pkg.points)
        postgis_prep_sec = time.perf_counter() - prep_start
        postgis_times = []
        postgis_rows = ()
        for _ in range(args.repeats):
            t0 = time.perf_counter()
            postgis_rows = query_postgis_fixed_radius_neighbors_3d(
                conn,
                radius=args.radius,
                k_max=args.k_max,
            )
            postgis_times.append(time.perf_counter() - t0)
    finally:
        conn.close()

    rt.write_cunsearch_fixed_radius_request(
        request_path,
        query_pkg.points,
        search_pkg.points,
        radius=args.radius,
        k_max=args.k_max,
        binary_path=Path(args.cunsearch_build_root) / "demo" / "Demo",
    )
    compile_start = time.perf_counter()
    binary_path = rt.compile_cunsearch_fixed_radius_request_driver(
        request_path,
        response_path,
        compiled_dir,
        source_root=args.cunsearch_source_root,
        build_root=args.cunsearch_build_root,
    )
    cunsearch_compile_sec = time.perf_counter() - compile_start
    cunsearch_times = []
    for _ in range(args.repeats):
        response_path.unlink(missing_ok=True)
        elapsed = rt.execute_compiled_cunsearch_fixed_radius_driver(
            binary_path,
            response_path=response_path,
        )
        cunsearch_times.append(elapsed)
    cunsearch_rows = rt.load_cunsearch_fixed_radius_response(response_path).rows

    payload = {
        "report_kind": "goal283_kitti_three_way_performance_v1",
        "dataset_source_root": str(Path(args.source_root).expanduser().resolve()),
        "query_package": str(query_package),
        "search_package": str(search_package),
        "query_point_count": len(query_pkg.points),
        "search_point_count": len(search_pkg.points),
        "radius": args.radius,
        "k_max": args.k_max,
        "repeats": args.repeats,
        "reference": {
            "times_sec": reference_times,
            "median_sec": median(reference_times),
            "row_count": len(reference_rows),
        },
        "postgis": {
            "dsn": args.postgis_dsn,
            "prep_sec": postgis_prep_sec,
            "times_sec": postgis_times,
            "median_sec": median(postgis_times),
            "row_count": len(postgis_rows),
            "parity_ok": postgis_rows == reference_rows,
        },
        "cunsearch": {
            "compile_sec": cunsearch_compile_sec,
            "times_sec": cunsearch_times,
            "median_sec": median(cunsearch_times),
            "row_count": len(cunsearch_rows),
            "parity_ok": rt.compare_baseline_rows("fixed_radius_neighbors", reference_rows, cunsearch_rows),
        },
        "notes": {
            "reference": "Python truth-path execution only.",
            "postgis": "Table load/index build measured separately from repeated query execution.",
            "cunsearch": "CUDA driver compile measured separately from repeated binary execution.",
        },
    }
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
