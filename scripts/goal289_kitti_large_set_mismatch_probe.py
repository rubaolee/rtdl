from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe the first large-set cuNSearch mismatch on a duplicate-free KITTI package."
    )
    parser.add_argument("package_dir")
    parser.add_argument("cunsearch_source_root")
    parser.add_argument("cunsearch_build_root")
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--k-max", type=int, default=1)
    parser.add_argument("--top-candidates", type=int, default=20)
    parser.add_argument("--output-dir", default="build/goal289_kitti_large_set_mismatch_probe")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package_dir = Path(args.package_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    query_points = rt.load_kitti_bounded_point_package(package_dir / "query_points.json").points
    search_points = rt.load_kitti_bounded_point_package(package_dir / "search_points.json").points
    reference_rows = rt.fixed_radius_neighbors_cpu(
        query_points,
        search_points,
        radius=args.radius,
        k_max=args.k_max,
    )
    candidate_rows = rt.load_cunsearch_fixed_radius_response(package_dir / "response.json").rows
    mismatch = rt.summarize_fixed_radius_mismatch(
        reference_rows,
        candidate_rows,
        strict_parity_ok=rt.compare_baseline_rows(
            "fixed_radius_neighbors",
            reference_rows,
            candidate_rows,
        ),
    )
    if mismatch.first_reference_row is None:
        raise RuntimeError("No mismatch was found in the provided package")

    query_id = int(mismatch.first_reference_row["query_id"])
    query_point = next(point for point in query_points if point.id == query_id)
    true_candidates: list[tuple[float, int, object]] = []
    for search_point in search_points:
        distance = math.sqrt(
            (query_point.x - search_point.x) ** 2
            + (query_point.y - search_point.y) ** 2
            + (query_point.z - search_point.z) ** 2
        )
        if distance <= args.radius:
            true_candidates.append((distance, search_point.id, search_point))
    true_candidates.sort(key=lambda item: (item[0], item[1]))
    subset_search_points = tuple(item[2] for item in true_candidates[: args.top_candidates])

    request_path = output_dir / "request.json"
    response_path = output_dir / "response.json"
    compiled_dir = output_dir / "compiled_driver"
    rt.write_cunsearch_fixed_radius_request(
        request_path,
        (query_point,),
        subset_search_points,
        radius=args.radius,
        k_max=args.top_candidates,
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
    subset_candidate_rows = rt.load_cunsearch_fixed_radius_response(response_path).rows
    subset_reference_rows = rt.fixed_radius_neighbors_cpu(
        (query_point,),
        subset_search_points,
        radius=args.radius,
        k_max=args.top_candidates,
    )

    payload = {
        "report_kind": "goal289_kitti_large_set_mismatch_probe_v1",
        "strict_parity_ok": mismatch.strict_parity_ok,
        "full_reference_row_count": mismatch.reference_row_count,
        "full_candidate_row_count": mismatch.candidate_row_count,
        "missing_pair_count": mismatch.missing_pair_count,
        "extra_pair_count": mismatch.extra_pair_count,
        "first_missing_pair": list(mismatch.first_missing_pair) if mismatch.first_missing_pair else None,
        "first_extra_pair": list(mismatch.first_extra_pair) if mismatch.first_extra_pair else None,
        "first_reference_row": mismatch.first_reference_row,
        "first_candidate_row": mismatch.first_candidate_row,
        "query_id": query_id,
        "top_candidate_count": args.top_candidates,
        "subset_reference_rows": [dict(row) for row in subset_reference_rows],
        "subset_candidate_rows": [dict(row) for row in subset_candidate_rows],
        "subset_parity_ok": rt.compare_baseline_rows(
            "fixed_radius_neighbors",
            subset_reference_rows,
            subset_candidate_rows,
        ),
    }
    report_path = output_dir / "large_set_mismatch_probe.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
