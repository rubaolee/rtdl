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
    plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    payload = {
        "status": "ok",
        "message": "hello rtdl v4",
        "operator": "fixed_radius",
        "partner": "torch",
        "planner_status": plan.status,
        "api_surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
