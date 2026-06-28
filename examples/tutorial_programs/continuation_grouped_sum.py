from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    hit_rows = (
        {"group": 1, "primitive": 10, "weight": 0.50},
        {"group": 1, "primitive": 11, "weight": 1.25},
        {"group": 2, "primitive": 12, "weight": 3.00},
        {"group": 2, "primitive": 13, "weight": -0.25},
    )
    grouped_sum: defaultdict[int, float] = defaultdict(float)
    for row in hit_rows:
        grouped_sum[int(row["group"])] += float(row["weight"])

    plan = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
    payload = {
        "status": "ok",
        "concept": "continuation turns relation rows into compact app outputs such as grouped sums",
        "hit_rows": hit_rows,
        "grouped_sum": {
            str(group): value for group, value in sorted(grouped_sum.items())
        },
        "planner": {
            "operator": "grouped_sum",
            "partner": "cupy",
            "status": plan.status,
            "surface": plan.api_surface,
            "generic_primitive": plan.generic_primitive,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
