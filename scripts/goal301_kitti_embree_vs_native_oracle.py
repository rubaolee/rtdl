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


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_3d_embree_goal301():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=1))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_3d_embree_goal301():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_3d_embree_goal301():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run duplicate-free KITTI 3D native-vs-Embree benchmarks on Linux."
    )
    parser.add_argument("source_root")
    parser.add_argument("--point-counts", default="16384")
    parser.add_argument("--output-dir", default="build/goal301_kitti_embree_vs_native_oracle")
    parser.add_argument("--query-start-index", type=int, default=0)
    parser.add_argument("--max-search-offset", type=int, default=32)
    parser.add_argument("--max-frames", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    return parser.parse_args()


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _time_native(kernel, *, query_points, search_points, repeats: int) -> tuple[tuple[dict[str, object], ...], float]:
    rows = ()
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        rows = rt.run_cpu(kernel, query_points=query_points, search_points=search_points)
        timings.append(time.perf_counter() - start)
    return rows, _median(timings)


def _time_prepared_embree(kernel, *, query_points, search_points, repeats: int) -> dict[str, object]:
    prepare_start = time.perf_counter()
    prepared_kernel = rt.prepare_embree(kernel)
    prepare_kernel_sec = time.perf_counter() - prepare_start

    pack_start = time.perf_counter()
    packed_query = rt.pack_points(records=query_points, dimension=3)
    packed_search = rt.pack_points(records=search_points, dimension=3)
    pack_inputs_sec = time.perf_counter() - pack_start

    bind_start = time.perf_counter()
    prepared_execution = prepared_kernel.bind(
        query_points=packed_query,
        search_points=packed_search,
    )
    bind_sec = time.perf_counter() - bind_start

    first_run_start = time.perf_counter()
    first_rows = prepared_execution.run()
    first_run_sec = time.perf_counter() - first_run_start

    hot_timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        prepared_execution.run()
        hot_timings.append(time.perf_counter() - start)

    return {
        "prepare_kernel_sec": prepare_kernel_sec,
        "pack_inputs_sec": pack_inputs_sec,
        "bind_sec": bind_sec,
        "first_run_sec": first_run_sec,
        "hot_median_sec": _median(hot_timings),
        "rows": first_rows,
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes = tuple(int(item.strip()) for item in args.point_counts.split(",") if item.strip())
    records = rt.discover_kitti_velodyne_frames(args.source_root)
    runs = []
    workloads = (
        ("fixed_radius_neighbors", fixed_radius_neighbors_3d_embree_goal301),
        ("bounded_knn_rows", bounded_knn_rows_3d_embree_goal301),
        ("knn_rows", knn_rows_3d_embree_goal301),
    )

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

        workload_reports = []
        for workload_name, kernel in workloads:
            native_rows, native_median_sec = _time_native(
                kernel,
                query_points=query_pkg.points,
                search_points=search_pkg.points,
                repeats=args.repeats,
            )
            embree = _time_prepared_embree(
                kernel,
                query_points=query_pkg.points,
                search_points=search_pkg.points,
                repeats=args.repeats,
            )
            workload_reports.append(
                {
                    "workload": workload_name,
                    "native_median_sec": native_median_sec,
                    "embree_prepare_kernel_sec": embree["prepare_kernel_sec"],
                    "embree_pack_inputs_sec": embree["pack_inputs_sec"],
                    "embree_bind_sec": embree["bind_sec"],
                    "embree_first_run_sec": embree["first_run_sec"],
                    "embree_hot_median_sec": embree["hot_median_sec"],
                    "embree_parity_ok": embree["rows"] == native_rows,
                    "row_count": len(native_rows),
                }
            )

        report = {
            "point_count": point_count,
            "query_start_index": pair.query_start_index,
            "search_start_index": pair.search_start_index,
            "query_sequence": pair.query_record.sequence,
            "query_frame_id": pair.query_record.frame_id,
            "search_sequence": pair.search_record.sequence,
            "search_frame_id": pair.search_record.frame_id,
            "duplicate_match_count": pair.duplicate_match_count,
            "repeats": args.repeats,
            "workloads": workload_reports,
        }
        (run_dir / "embree_vs_native_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        runs.append(report)

    payload = {
        "report_kind": "goal301_kitti_embree_vs_native_oracle_v1",
        "source_root": str(Path(args.source_root).expanduser().resolve()),
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
