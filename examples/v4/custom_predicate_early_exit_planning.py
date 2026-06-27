from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    plan = rtdl_v4.plan_ray_triangle_custom_predicate_early_exit_v4(
        callback_shape="pure_boolean_numba_cabi_device_function",
        action="terminate_on_first_accept",
        partner="numba",
        numba_device_function=True,
    )
    boundary = rtdl_v4.ray_triangle_custom_predicate_early_exit_claim_boundary_v4()
    unsafe = rtdl_v4.plan_operator_request_v4(
        "custom_predicate_early_exit",
        partner="numba",
        callback_shape="pure_boolean_numba_cabi_device_function",
        numba_device_function=True,
        mutates_shared_state=True,
    )
    payload = {
        "status": "ok",
        "surface": boundary["v4_api_surface"],
        "generic_primitive": boundary["generic_primitive"],
        "partner": boundary["partner"],
        "callback_shape": plan.callback_shape,
        "action": plan.action,
        "planner_accepts_constrained_predicate": True,
        "unsafe_callback_status": unsafe.status,
        "serious_scale_v4_vs_v2_14_geomean": boundary[
            "goal4717_serious_scale_primary_v2_speedup_geomean"
        ],
        "serious_scale_v4_vs_v3_0_2_geomean": boundary[
            "goal4717_serious_scale_primary_v3_speedup_geomean"
        ],
        "serious_scale_min_primary_v3_speedup": boundary[
            "goal4717_serious_scale_min_primary_v3_speedup"
        ],
        "comparison_class": boundary["comparison_class"],
        "release_claim_authorized": boundary["release_claim_authorized"],
        "whole_app_speedup_claim_authorized": boundary["whole_app_speedup_claim_authorized"],
        "arbitrary_python_callback_authorized": boundary["arbitrary_python_callback_authorized"],
        "tier3_callback_claim_authorized": boundary["tier3_callback_claim_authorized"],
        "raw_optix_callback_claim_authorized": boundary["raw_optix_callback_claim_authorized"],
        "public_tier3_support_authorized": boundary["public_tier3_support_authorized"],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
