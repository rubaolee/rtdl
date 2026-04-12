from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded live RTDL-vs-cuNSearch comparison on real KITTI data."
    )
    parser.add_argument("source_root", help="KITTI raw source root on Linux.")
    parser.add_argument("cunsearch_source_root", help="cuNSearch source root on Linux.")
    parser.add_argument("cunsearch_build_root", help="Built cuNSearch build root on Linux.")
    parser.add_argument(
        "--output-dir",
        default="build/goal279_kitti_live_real",
        help="Directory for manifests, packages, request/response, and JSON report.",
    )
    parser.add_argument("--query-start-index", type=int, default=0)
    parser.add_argument("--search-start-index", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=1)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-points-per-frame", type=int, default=64)
    parser.add_argument("--max-total-points", type=int, default=64)
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--k-max", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    query_manifest = output_dir / "query_manifest.json"
    search_manifest = output_dir / "search_manifest.json"
    query_package = output_dir / "query_points.json"
    search_package = output_dir / "search_points.json"
    request_path = output_dir / "request.json"
    response_path = output_dir / "response.json"
    report_path = output_dir / "comparison_report.json"

    rt.write_kitti_bounded_package_manifest(
        query_manifest,
        source_root=args.source_root,
        max_frames=args.max_frames,
        stride=args.stride,
        start_index=args.query_start_index,
        max_points_per_frame=args.max_points_per_frame,
        max_total_points=args.max_total_points,
    )
    rt.write_kitti_bounded_package_manifest(
        search_manifest,
        source_root=args.source_root,
        max_frames=args.max_frames,
        stride=args.stride,
        start_index=args.search_start_index,
        max_points_per_frame=args.max_points_per_frame,
        max_total_points=args.max_total_points,
    )
    rt.write_kitti_bounded_point_package(query_package, query_manifest)
    rt.write_kitti_bounded_point_package(search_package, search_manifest)
    result = rt.compare_bounded_fixed_radius_live_cunsearch(
        query_package_path=query_package,
        search_package_path=search_package,
        request_path=request_path,
        response_path=response_path,
        radius=args.radius,
        k_max=args.k_max,
        cunsearch_source_root=args.cunsearch_source_root,
        cunsearch_build_root=args.cunsearch_build_root,
    )

    payload = {
        "report_kind": "goal279_kitti_live_real_report_v1",
        "dataset_source_root": str(Path(args.source_root).expanduser().resolve()),
        "query_manifest": str(query_manifest),
        "search_manifest": str(search_manifest),
        "query_package": str(query_package),
        "search_package": str(search_package),
        "request": str(request_path),
        "response": str(response_path),
        "radius": args.radius,
        "k_max": args.k_max,
        "result": {
            "workload": result.workload,
            "query_point_count": result.query_point_count,
            "search_point_count": result.search_point_count,
            "reference_row_count": result.reference_row_count,
            "external_row_count": result.external_row_count,
            "parity_ok": result.parity_ok,
            "notes": result.notes,
        },
    }
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
