from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    info = rtdl_v4.claim_boundary_v4()
    any_hit = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    fixed_radius = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    nearest = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
    aabb = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    callback = rtdl_v4.plan_operator_request_v4(
        "custom_predicate_early_exit",
        partner="numba",
        callback_shape="pure_boolean_numba_cabi_device_function",
        numba_device_function=True,
    )

    payload = {
        "status": "ok",
        "tutorial_classification": "operator_companion_after_kernel_first_lesson",
        "not_first_lesson": True,
        "kernel_first_requirement": "Run hello_world.py, sorting_rows.py, and at least one relation tutorial before this front door.",
        "concept": "import V4, name a relation-producing operator, choose a partner, then read the planned surface",
        "filename_note": (
            "Despite the historical quickstart name, this is an operator "
            "companion. Run kernel-first lessons before using it."
        ),
        "release": info["public_release_tag"],
        "import": "import rtdsl.v4 as rtdl_v4",
        "measured_surface_count": info["measured_surface_count"],
        "measured_partners": list(info["measured_partners"]),
        "benchmark_app_count": info["complete_rt_core_app_matrix_app_count"],
        "benchmark_matrix_rows": info["complete_rt_core_app_matrix_row_count"],
        "example_operator_plans": {
            "fixed_radius": fixed_radius.api_surface,
            "point_group_nearest": nearest.api_surface,
            "ray_triangle_any_hit": any_hit.api_surface,
            "aabb_index_query": aabb.api_surface,
            "custom_predicate_early_exit": callback.api_surface,
        },
        "first_lessons": [
            "hello_world.py",
            "sorting_rows.py",
            "operator_primitives.py",
            "fixed_radius_neighbors.py",
            "nearest_neighbor.py",
        ],
        "boundary_notes": [
            "V4 surfaces are generic operators, not app-specific kernels.",
            "Partners are explicit choices.",
            "Benchmark apps combine the small concepts after you learn them.",
        ],
        "next_steps": [
            "python examples/tutorial_programs/operator_primitives.py",
            "python examples/tutorial_programs/fixed_radius_neighbors.py",
            "python examples/tutorial_programs/nearest_neighbor.py",
            "python examples/tutorial_programs/benchmark_app_recipes.py",
            "open tutorials/current/README.md",
            "open examples/benchmark_apps/README.md",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
