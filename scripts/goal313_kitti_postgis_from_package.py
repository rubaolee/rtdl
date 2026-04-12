from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run PostGIS 3D nearest-neighbor workloads on saved KITTI point packages."
    )
    parser.add_argument("package_dir")
    parser.add_argument("--postgis-dsn", required=True)
    parser.add_argument("--fixed-repeats", type=int, default=3)
    parser.add_argument("--bounded-repeats", type=int, default=3)
    parser.add_argument("--knn-repeats", type=int, default=1)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _time_postgis(workload_name: str, fn, connection, query_points, search_points, repeats: int, **kwargs) -> dict[str, object]:
    timings: list[float] = []
    rows = ()
    for _ in range(repeats):
        connection.rollback()
        start = time.perf_counter()
        rows = fn(connection, query_points, search_points, **kwargs)
        timings.append(time.perf_counter() - start)
        connection.rollback()
    return {
        "workload": workload_name,
        "postgis_runs_sec": timings,
        "postgis_median_sec": _median(timings),
        "row_count": len(rows),
        "rows": rows,
    }


def main() -> int:
    args = parse_args()
    package_dir = Path(args.package_dir)
    query_pkg = rt.load_kitti_bounded_point_package(package_dir / "query_points.json")
    search_pkg = rt.load_kitti_bounded_point_package(package_dir / "search_points.json")
    query_manifest = json.loads((package_dir / "query_manifest.json").read_text(encoding="utf-8"))
    search_manifest = json.loads((package_dir / "search_manifest.json").read_text(encoding="utf-8"))

    conn = rt.connect_postgis(args.postgis_dsn)
    try:
        fixed = _time_postgis(
            "fixed_radius_neighbors",
            rt.run_postgis_fixed_radius_neighbors_3d,
            conn,
            query_pkg.points,
            search_pkg.points,
            args.fixed_repeats,
            radius=1.0,
            k_max=1,
        )
        bounded = _time_postgis(
            "bounded_knn_rows",
            rt.run_postgis_bounded_knn_rows_3d,
            conn,
            query_pkg.points,
            search_pkg.points,
            args.bounded_repeats,
            radius=1.0,
            k_max=4,
        )
        knn = _time_postgis(
            "knn_rows",
            rt.run_postgis_knn_rows_3d,
            conn,
            query_pkg.points,
            search_pkg.points,
            args.knn_repeats,
            k=4,
        )
    finally:
        conn.rollback()
        conn.close()

    payload = {
        "report_kind": "goal313_kitti_postgis_from_package_v1",
        "package_dir": str(package_dir.resolve()),
        "postgis_dsn": args.postgis_dsn,
        "query_start_index": int(query_manifest["start_index"]),
        "search_start_index": int(search_manifest["start_index"]),
        "query_sequence": query_manifest["frames"][0]["sequence"],
        "query_frame_id": query_manifest["frames"][0]["frame_id"],
        "search_sequence": search_manifest["frames"][0]["sequence"],
        "search_frame_id": search_manifest["frames"][0]["frame_id"],
        "point_count": int(query_pkg.selected_point_count),
        "workloads": [
            {
                "workload": fixed["workload"],
                "postgis_runs_sec": fixed["postgis_runs_sec"],
                "postgis_median_sec": fixed["postgis_median_sec"],
                "row_count": fixed["row_count"],
            },
            {
                "workload": bounded["workload"],
                "postgis_runs_sec": bounded["postgis_runs_sec"],
                "postgis_median_sec": bounded["postgis_median_sec"],
                "row_count": bounded["row_count"],
            },
            {
                "workload": knn["workload"],
                "postgis_runs_sec": knn["postgis_runs_sec"],
                "postgis_median_sec": knn["postgis_median_sec"],
                "row_count": knn["row_count"],
            },
        ],
    }
    output_path = Path(args.output) if args.output else package_dir / "postgis_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
