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
    aabb = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    callback = rtdl_v4.plan_operator_request_v4(
        "custom_predicate_early_exit",
        partner="numba",
        callback_shape="pure_boolean_numba_cabi_device_function",
        numba_device_function=True,
    )

    payload = {
        "status": "ok",
        "release": info["public_release_tag"],
        "import": "import rtdsl.v4 as rtdl_v4",
        "measured_surface_count": info["measured_surface_count"],
        "measured_partners": list(info["measured_partners"]),
        "benchmark_app_count": info["complete_rt_core_app_matrix_app_count"],
        "benchmark_matrix_rows": info["complete_rt_core_app_matrix_row_count"],
        "example_operator_plans": {
            "ray_triangle_any_hit": any_hit.api_surface,
            "aabb_index_query": aabb.api_surface,
            "custom_predicate_early_exit": callback.api_surface,
        },
        "next_steps": [
            "python examples/simple/benchmark_app_recipes.py",
            "open tutorials/current/README.md",
            "open examples/benchmark_apps/README.md",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
