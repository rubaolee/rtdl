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
        description="Probe the cuNSearch duplicate-point correctness boundary on bounded KITTI packages."
    )
    parser.add_argument("package_dir")
    parser.add_argument("cunsearch_source_root")
    parser.add_argument("cunsearch_build_root")
    parser.add_argument("--query-id", type=int, required=True)
    parser.add_argument("--search-ids", required=True, help="Comma-separated search ids to keep.")
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--output-dir", default="build/goal285_cunsearch_duplicate_point_probe")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package_dir = Path(args.package_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    query_points = rt.load_kitti_bounded_point_package(package_dir / "query_points.json").points
    search_points = rt.load_kitti_bounded_point_package(package_dir / "search_points.json").points
    selected_query = tuple(point for point in query_points if point.id == args.query_id)
    search_ids = tuple(int(item.strip()) for item in args.search_ids.split(",") if item.strip())
    selected_search = tuple(point for point in search_points if point.id in search_ids)
    if not selected_query:
        raise ValueError("query-id did not match any point in the package")
    if not selected_search:
        raise ValueError("search-ids did not match any points in the package")

    request_path = output_dir / "request.json"
    response_path = output_dir / "response.json"
    compiled_dir = output_dir / "compiled_driver"

    rt.write_cunsearch_fixed_radius_request(
        request_path,
        selected_query,
        selected_search,
        radius=args.radius,
        k_max=len(selected_search),
        binary_path=Path(args.cunsearch_build_root) / "demo" / "Demo",
    )
    binary_path = rt.compile_cunsearch_fixed_radius_request_driver(
        request_path,
        response_path,
        compiled_dir,
        source_root=args.cunsearch_source_root,
        build_root=args.cunsearch_build_root,
    )
    rt.execute_compiled_cunsearch_fixed_radius_driver(binary_path, response_path=response_path)

    reference_rows = rt.fixed_radius_neighbors_cpu(
        selected_query,
        selected_search,
        radius=args.radius,
        k_max=len(selected_search),
    )
    candidate_rows = rt.load_cunsearch_fixed_radius_response(response_path).rows
    exact_matches = rt.find_exact_cross_package_matches(selected_query, selected_search)
    mismatch = rt.summarize_fixed_radius_mismatch(
        reference_rows,
        candidate_rows,
        strict_parity_ok=rt.compare_baseline_rows(
            "fixed_radius_neighbors",
            reference_rows,
            candidate_rows,
        ),
    )

    payload = {
        "report_kind": "goal285_cunsearch_duplicate_point_probe_v1",
        "query_ids": [point.id for point in selected_query],
        "search_ids": [point.id for point in selected_search],
        "radius": args.radius,
        "reference_rows": [dict(row) for row in reference_rows],
        "candidate_rows": [dict(row) for row in candidate_rows],
        "exact_cross_package_matches": [
            {
                "query_id": item.query_id,
                "search_id": item.search_id,
                "x": item.x,
                "y": item.y,
                "z": item.z,
            }
            for item in exact_matches
        ],
        "mismatch_summary": {
            "strict_parity_ok": mismatch.strict_parity_ok,
            "missing_pair_count": mismatch.missing_pair_count,
            "extra_pair_count": mismatch.extra_pair_count,
            "first_missing_pair": list(mismatch.first_missing_pair) if mismatch.first_missing_pair else None,
            "first_extra_pair": list(mismatch.first_extra_pair) if mismatch.first_extra_pair else None,
            "first_reference_row": mismatch.first_reference_row,
            "first_candidate_row": mismatch.first_candidate_row,
        },
    }
    report_path = output_dir / "duplicate_probe_report.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
