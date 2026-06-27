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
        plan = plan_v4_operator_request("fixed-radius", partner="torch")
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

    payload = plan.as_dict()
    if payload.get("tier3_protocol_doc"):
        payload["callback_protocol"] = "deferred_v4_x_callback_spike"
        payload.pop("tier3_protocol_doc", None)
    if payload.get("tier3_protocol_status"):
        payload["callback_protocol_status"] = "not_public_v4_0_support"
        payload.pop("tier3_protocol_status", None)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
