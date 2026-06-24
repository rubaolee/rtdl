from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    boundary = rtdl_v4.claim_boundary_v4()
    catalog = rtdl_v4.measured_operator_catalog_v4()
    tier2_plan = rtdl_v4.plan_operator_request_v4("any-hit", partner="torch")
    complex_callback_plan = rtdl_v4.plan_operator_request_v4(
        "custom-collision-response",
        callback_shape="custom_action",
        mutates_shared_state=True,
        variable_length_output=True,
        dynamic_allocation=True,
        partner="torch",
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "front_door_status": boundary["status"],
                "measured_surface_count": len(boundary["measured_surfaces"]),
                "catalog_operator_count": len(catalog),
                "tier2_plan_status": tier2_plan.status,
                "tier2_plan_surface": tier2_plan.api_surface,
                "complex_callback_status": complex_callback_plan.status,
                "release_claim_authorized": boundary["release_claim_authorized"],
                "tier3_callback_claim_authorized": boundary["tier3_callback_claim_authorized"],
                "app_specific_native_kernel_authorized": boundary["app_specific_native_kernel_authorized"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

