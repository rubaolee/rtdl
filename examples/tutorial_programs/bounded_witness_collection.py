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
    candidate_rows = (
        {"pair_id": 1, "witness_id": 100, "depth": 0.05},
        {"pair_id": 1, "witness_id": 101, "depth": 0.08},
        {"pair_id": 1, "witness_id": 102, "depth": 0.02},
        {"pair_id": 2, "witness_id": 200, "depth": 0.03},
    )
    capacity = 2
    collected_rows = []
    validation_rows = []
    for pair_id in sorted({row["pair_id"] for row in candidate_rows}):
        rows = [row for row in candidate_rows if row["pair_id"] == pair_id]
        rows.sort(key=lambda row: (-float(row["depth"]), int(row["witness_id"])))
        kept = rows[:capacity]
        overflowed = len(rows) > capacity
        collected_rows.extend({**row, "slot": slot} for slot, row in enumerate(kept))
        validation_rows.append(
            {
                "pair_id": pair_id,
                "candidate_count": len(rows),
                "kept_count": len(kept),
                "capacity": capacity,
                "overflowed": overflowed,
            }
        )

    plan = rtdl_v4.plan_operator_request_v4("closest_hit_argmin", partner="torch")
    payload = {
        "status": "ok",
        "concept": "Contact-style apps collect a bounded number of witnesses per pair and must report overflow instead of silently dropping evidence",
        "manual_data_flow": "candidate witness rows -> sort by contact depth -> keep K rows per pair -> overflow validation",
        "capacity": capacity,
        "candidate_rows": candidate_rows,
        "collected_rows": tuple(collected_rows),
        "validation_rows": tuple(validation_rows),
        "v4_surface": {
            "request": "closest_hit_argmin",
            "partner": "torch",
            "status": plan.status,
            "surface": plan.api_surface,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
