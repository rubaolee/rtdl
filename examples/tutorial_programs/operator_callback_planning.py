from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_operator_catalog import plan_v4_operator_request


def main() -> int:
    parser = argparse.ArgumentParser(description="V4 operator and callback planning example.")
    parser.add_argument(
        "--case",
        choices=("tier2", "scalar-callback", "complex-callback"),
        default="tier2",
    )
    args = parser.parse_args()

    if args.case == "tier2":
        plan = plan_v4_operator_request("fixed_radius", partner="torch")
    elif args.case == "scalar-callback":
        plan = plan_v4_operator_request(
            "custom-force-score",
            callback_shape="custom_scalar_reduce",
            numba_device_function=True,
            partner="torch",
        )
    else:
        plan = plan_v4_operator_request(
            "custom-collision-response",
            callback_shape="custom_action",
            mutates_shared_state=True,
            variable_length_output=True,
            dynamic_allocation=True,
            partner="torch",
        )

    raw = plan.as_dict()
    payload = {
        "status": raw["status"],
        "tutorial_classification": "operator_companion_after_kernel_first_lesson",
        "not_first_lesson": True,
        "kernel_first_requirement": "Read ray_triangle_hits.py and continuation_grouped_sum.py before using callback planning.",
        "request": raw["request"],
        "partner": raw["partner"],
        "api_surface": raw.get("api_surface"),
        "generic_primitive": raw.get("generic_primitive"),
        "measured_partner": raw.get("measured_partner"),
        "continuation_class": raw.get("continuation_class"),
        "tier": raw.get("tier"),
    }
    if raw.get("tier3_protocol_doc") or raw.get("tier3_protocol_status"):
        payload["callback_boundary"] = {
            "public_v4_0_support": "not_supported",
            "reason": "this program shape is outside the current V4.0 operator surface",
            "next_step": "rewrite as a recognized filter/reduce operator or keep the custom action outside RTDL",
        }
    if args.case == "complex-callback":
        payload["rejected_shape"] = {
            "mutates_shared_state": True,
            "dynamic_allocation": True,
            "variable_length_output": True,
        }
        payload["guidance"] = (
            "This callback is action-shaped. V4.0 does not expose raw OptiX "
            "callbacks or application-specific native kernels; rewrite the "
            "work as a recognized relation plus continuation, or keep the "
            "custom action in application code."
        )
        payload["rewrite_example"] = {
            "bad_shape": "mutate shared application state during every hit",
            "step_1": "emit hit rows with ray_id, primitive_id, payload_id, and score",
            "step_2": "use a bounded or grouped continuation when the output shape is regular",
            "step_3": "apply irregular mutation in ordinary application code after RTDL returns",
        }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
