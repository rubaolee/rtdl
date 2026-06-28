from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt
import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Ray2D
from rtdsl.reference import Triangle


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hit_count_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def make_case() -> dict[str, object]:
    return {
        "rays": (
            Ray2D(id=1, ox=-1.0, oy=0.25, dx=1.0, dy=0.0, tmax=4.0),
            Ray2D(id=2, ox=-1.0, oy=2.0, dx=1.0, dy=0.0, tmax=4.0),
            Ray2D(id=3, ox=-1.0, oy=0.75, dx=1.0, dy=0.0, tmax=4.0),
        ),
        "triangles": (
            Triangle(id=10, x0=0.0, y0=0.0, x1=1.0, y1=0.0, x2=0.0, y2=1.0),
            Triangle(id=20, x0=2.0, y0=0.0, x1=3.0, y1=0.0, x2=2.0, y2=1.0),
        ),
        "ray_groups": {1: 100, 2: 100, 3: 200},
        "ray_weights": {1: 0.5, 2: 1.25, 3: 2.0},
    }


def _group_hit_count_rows(
    hit_count_rows: tuple[dict[str, int], ...],
    *,
    ray_groups: dict[int, int],
    ray_weights: dict[int, float],
) -> tuple[dict[str, float | int], ...]:
    grouped_count: defaultdict[int, int] = defaultdict(int)
    grouped_weighted_sum: defaultdict[int, float] = defaultdict(float)
    for row in hit_count_rows:
        ray_id = int(row["ray_id"])
        group_id = int(ray_groups[ray_id])
        hit_count = int(row["hit_count"])
        grouped_count[group_id] += hit_count
        grouped_weighted_sum[group_id] += float(ray_weights[ray_id]) * hit_count
    return tuple(
        {
            "group_id": group_id,
            "hit_count_sum": grouped_count[group_id],
            "weighted_hit_sum": round(grouped_weighted_sum[group_id], 4),
        }
        for group_id in sorted(grouped_count)
    )


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    kernel_inputs = {"rays": case["rays"], "triangles": case["triangles"]}
    compiled = rt.compile_kernel(ray_triangle_hit_count_kernel)
    hit_count_rows = tuple(rt.run_cpu_python_reference(ray_triangle_hit_count_kernel, **kernel_inputs))
    grouped_rows = _group_hit_count_rows(
        hit_count_rows,
        ray_groups=case["ray_groups"],
        ray_weights=case["ray_weights"],
    )
    return {
        "mode": "kernel_plus_continuation",
        "status": "ok",
        "teaches": (
            "RTDL kernel emits per-ray hit-count rows; the continuation groups "
            "those rows by app-owned group ids and computes compact summaries"
        ),
        "kernel_summary": compiled.format(),
        "hit_count_rows": tuple(
            {"ray_id": int(row["ray_id"]), "hit_count": int(row["hit_count"])}
            for row in hit_count_rows
        ),
        "grouped_rows": grouped_rows,
    }


def run_visible_flow() -> dict[str, object]:
    hit_rows = (
        {"group": 1, "primitive": 10, "weight": 0.50},
        {"group": 1, "primitive": 11, "weight": 1.25},
        {"group": 2, "primitive": 12, "weight": 3.00},
        {"group": 2, "primitive": 13, "weight": -0.25},
    )
    grouped_sum: defaultdict[int, float] = defaultdict(float)
    for row in hit_rows:
        grouped_sum[int(row["group"])] += float(row["weight"])
    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual grouped continuation over already emitted relation rows",
        "hit_rows": hit_rows,
        "grouped_sum": {
            str(group): value for group, value in sorted(grouped_sum.items())
        },
    }


def run_v4_mode() -> dict[str, object]:
    grouped_plan = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
    i64_plan = rtdl_v4.plan_operator_request_v4("grouped_i64", partner="torch")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for grouped continuation surfaces",
        "planner": {
            "grouped_sum": {
                "operator": "grouped_sum",
                "partner": "cupy",
                "status": grouped_plan.status,
                "surface": grouped_plan.api_surface,
                "generic_primitive": grouped_plan.generic_primitive,
            },
            "grouped_i64": {
                "operator": "grouped_i64",
                "partner": "torch",
                "status": i64_plan.status,
                "surface": i64_plan.api_surface,
                "generic_primitive": i64_plan.generic_primitive,
            },
        },
        "relationship_to_kernel": (
            "The kernel produces relation rows. The continuation consumes those "
            "rows and writes compact grouped outputs. V4 surfaces provide measured "
            "partner-backed implementations for recognized grouped continuations."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "continuation is the step after traversal rows: reduce many RT rows "
            "into compact app-owned outputs"
        ),
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "hit_rows_to_grouped_summary_rows",
            "kernel_output_field": "hit_count_rows",
            "continuation_output_field": "grouped_rows",
            "v4_execution_targets": {
                "grouped_sum": v4["planner"]["grouped_sum"]["surface"],
                "grouped_i64": v4["planner"]["grouped_i64"]["surface"],
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL grouped-continuation tutorial")
    parser.add_argument("--mode", choices=("kernel", "v4", "both", "visible"), default="both")
    args = parser.parse_args()
    if args.mode == "kernel":
        payload = run_kernel_mode()
    elif args.mode == "v4":
        payload = run_v4_mode()
    elif args.mode == "visible":
        payload = run_visible_flow()
    else:
        payload = run_both_modes()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
