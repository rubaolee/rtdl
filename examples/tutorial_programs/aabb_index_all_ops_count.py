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
    "tutorial_classification": "operator_companion_after_kernel_first_lesson",
    "not_first_lesson": True,
    "kernel_first_requirement": "Read and run aabb_spatial_index_predicates.py before this device-array surface.",
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
    "field_map": {
        "kernel_box_id": "boxes index",
        "kernel_point_query": "point_queries",
        "kernel_box_query": "box_queries",
        "predicate_point_contains": "box contains query point",
        "predicate_range_contains": "indexed box fully contains query box",
        "predicate_range_intersects": "indexed box intersects query box",
        "output_counts": "count per selected predicate operation",
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
            "claim_boundary": {
                "public_claim": "AABB all-ops count prepared-runner example",
                "not_claimed": [
                    "broad V4 speedup",
                    "whole-application speedup",
                    "all-benchmark speedup",
                    "public zero-copy claim",
                    "arbitrary callback support",
                    "CuPy performance claim for this route",
                    "C ABI or non-Python host binding",
                    "application-specific native kernel",
                ],
            },
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
        "claim_boundary": {
            "public_claim": "AABB all-ops count prepared-runner example",
            "not_claimed": [
                "broad V4 speedup",
                "whole-application speedup",
                "all-benchmark speedup",
                "public zero-copy claim",
                "arbitrary callback support",
                "CuPy performance claim for this route",
                "C ABI or non-Python host binding",
                "application-specific native kernel",
            ],
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if correctness_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
