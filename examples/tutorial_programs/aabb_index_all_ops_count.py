from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.aabb_index import Aabb2D
from rtdsl.aabb_index import Point2DLike
import rtdsl.v4 as rtdl_v4

TEACHING_CONTEXT = {
    "concept_tutorial": "examples/tutorial_programs/aabb_spatial_index_predicates.py",
    "manual_data_flow": [
        "User supplies AABB boxes plus point and box query rows.",
        "RTDL builds the prepared AABB index once.",
        "The runner evaluates point-contains, range-contains, and range-intersects counts.",
    ],
    "input_rows": {
        "boxes": "indexed AABB rows",
        "point_queries": "points tested against indexed boxes",
        "box_queries": "query boxes tested against indexed boxes",
    },
    "relation_output": "predicate rows for each selected AABB operation",
    "continuation": "count per operation",
    "benchmark_bridge": "AABB spatial-index query workloads",
}


def _tiny_fixture():
    boxes = (
        Aabb2D(0.0, 0.0, 1.0, 1.0),
        Aabb2D(0.2, 0.2, 0.8, 0.8),
    )
    point_queries = (Point2DLike(0.5, 0.5), Point2DLike(2.0, 2.0))
    box_queries = (
        Aabb2D(0.25, 0.25, 0.75, 0.75),
        Aabb2D(0.9, 0.9, 1.1, 1.1),
    )
    expected_counts = {"point_contains": 2, "range_contains": 2, "range_intersects": 3}
    return boxes, point_queries, box_queries, expected_counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 AABB all-ops count front-door example.")
    parser.add_argument("--backend", default="cpu", choices=("cpu", "embree", "optix", "hiprt"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    boundary = rtdl_v4.aabb_index_query_2d_all_ops_count_claim_boundary_v4(backend=args.backend)
    if args.dry_run:
        payload = {
            "status": "dry_run",
            "surface_status": "tier2_measured_v4_0_0_release_surface",
            "api_surface": boundary["v4_api_surface"],
            "generic_primitive": "AABB_INDEX_QUERY_2D",
            "teaching_context": TEACHING_CONTEXT,
            "backend": args.backend,
            "measured_backend": boundary["measured_backend"],
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "tier3_callback_claim_authorized": False,
            "raw_optix_callback_claim_authorized": False,
            "cupy_performance_claim_authorized": False,
            "embedding_c_abi_claim_authorized": False,
            "non_python_host_binding_claim_authorized": False,
            "app_specific_native_kernel_authorized": False,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    boxes, point_queries, box_queries, expected_counts = _tiny_fixture()
    with rtdl_v4.prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4(
        boxes,
        point_queries_for_bounds=point_queries,
        box_queries_for_bounds=box_queries,
        backend=args.backend,
    ) as session:
        result = session.run(point_queries=point_queries, box_queries=box_queries)

    correctness_passed = result["counts"] == expected_counts
    payload = {
        "status": "measured" if boundary["measured_backend"] else "correctness_only",
        "surface_status": "tier2_measured_v4_0_0_release_surface",
        "api_surface": boundary["v4_api_surface"],
        "generic_primitive": "AABB_INDEX_QUERY_2D",
        "teaching_context": TEACHING_CONTEXT,
        "backend": args.backend,
        "measured_backend": boundary["measured_backend"],
        "counts": result["counts"],
        "correctness_passed": correctness_passed,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "embedding_c_abi_claim_authorized": False,
        "non_python_host_binding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if correctness_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
