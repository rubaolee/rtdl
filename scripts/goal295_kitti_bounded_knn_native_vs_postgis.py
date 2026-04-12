from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.external_baselines import prepare_postgis_point3d_tables
from rtdsl.external_baselines import query_postgis_bounded_knn_rows_3d


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_3d_perf_kernel():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run duplicate-free KITTI 3D bounded-KNN benchmarks across RTDL reference, RTDL native oracle, and PostGIS."
    )
    parser.add_argument("source_root")
    parser.add_argument("postgis_dsn")
    parser.add_argument("--point-counts", default="512,1024,2048,4096")
    parser.add_argument("--output-dir", default="build/goal295_kitti_bounded_knn_native_vs_postgis")
    parser.add_argument("--query-start-index", type=int, default=0)
    parser.add_argument("--max-search-offset", type=int, default=8)
    parser.add_argument("--max-frames", type=int, default=1)
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--k-max", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    return parser.parse_args()


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes = tuple(int(item.strip()) for item in args.point_counts.split(",") if item.strip())
    records = rt.discover_kitti_velodyne_frames(args.source_root)
    runs = []

    for point_count in sizes:
        run_dir = output_dir / f"points_{point_count}"
        selector_dir = run_dir / "selector"
        pair = rt.find_duplicate_free_kitti_pair(
            source_root=args.source_root,
            candidate_records=records,
            query_start_index=args.query_start_index,
            max_search_offset=args.max_search_offset,
            max_points_per_frame=point_count,
            max_total_points=point_count,
            work_dir=selector_dir,
        )
        rt.write_kitti_bounded_package_manifest(
            run_dir / "query_manifest.json",
            source_root=args.source_root,
            max_frames=args.max_frames,
            start_index=pair.query_start_index,
            max_points_per_frame=point_count,
            max_total_points=point_count,
        )
        rt.write_kitti_bounded_package_manifest(
            run_dir / "search_manifest.json",
            source_root=args.source_root,
            max_frames=args.max_frames,
            start_index=pair.search_start_index,
            max_points_per_frame=point_count,
            max_total_points=point_count,
        )
        rt.write_kitti_bounded_point_package(run_dir / "query_points.json", run_dir / "query_manifest.json")
        rt.write_kitti_bounded_point_package(run_dir / "search_points.json", run_dir / "search_manifest.json")

        query_pkg = rt.load_kitti_bounded_point_package(run_dir / "query_points.json")
        search_pkg = rt.load_kitti_bounded_point_package(run_dir / "search_points.json")

        reference_rows = ()
        reference_times = []
        native_rows = ()
        native_times = []
        for _ in range(args.repeats):
            t0 = time.perf_counter()
            reference_rows = rt.run_cpu_python_reference(
                bounded_knn_rows_3d_perf_kernel,
                query_points=query_pkg.points,
                search_points=search_pkg.points,
            )
            reference_times.append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            native_rows = rt.run_cpu(
                bounded_knn_rows_3d_perf_kernel,
                query_points=query_pkg.points,
                search_points=search_pkg.points,
            )
            native_times.append(time.perf_counter() - t0)

        conn = rt.connect_postgis(args.postgis_dsn)
        try:
            prep_start = time.perf_counter()
            prepare_postgis_point3d_tables(conn, query_pkg.points, search_pkg.points)
            postgis_prep_sec = time.perf_counter() - prep_start
            postgis_rows = ()
            postgis_times = []
            for _ in range(args.repeats):
                t0 = time.perf_counter()
                postgis_rows = query_postgis_bounded_knn_rows_3d(
                    conn,
                    radius=args.radius,
                    k_max=args.k_max,
                )
                postgis_times.append(time.perf_counter() - t0)
        finally:
            conn.close()

        report = {
            "point_count": point_count,
            "query_start_index": pair.query_start_index,
            "search_start_index": pair.search_start_index,
            "query_sequence": pair.query_record.sequence,
            "query_frame_id": pair.query_record.frame_id,
            "search_sequence": pair.search_record.sequence,
            "search_frame_id": pair.search_record.frame_id,
            "duplicate_match_count": pair.duplicate_match_count,
            "radius": args.radius,
            "k_max": args.k_max,
            "reference_median_sec": _median(reference_times),
            "native_median_sec": _median(native_times),
            "native_parity_ok": native_rows == reference_rows,
            "postgis_median_sec": _median(postgis_times),
            "postgis_prep_sec": postgis_prep_sec,
            "postgis_parity_ok": postgis_rows == reference_rows,
            "row_count": len(reference_rows),
        }
        (run_dir / "bounded_knn_native_vs_postgis_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        runs.append(report)

    payload = {
        "report_kind": "goal295_kitti_bounded_knn_native_vs_postgis_v1",
        "source_root": str(Path(args.source_root).expanduser().resolve()),
        "radius": args.radius,
        "k_max": args.k_max,
        "repeats": args.repeats,
        "runs": runs,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(summary_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
