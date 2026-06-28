from __future__ import annotations

import json
from pathlib import Path
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    setup_start = time.perf_counter()
    rows = tuple({"query_id": query_id, "candidate_id": query_id + 100} for query_id in range(4))
    setup_seconds = time.perf_counter() - setup_start

    hot_start = time.perf_counter()
    relation_rows = tuple({**row, "hit": row["query_id"] % 2 == 0} for row in rows)
    hot_seconds = time.perf_counter() - hot_start

    continuation_start = time.perf_counter()
    hit_count = sum(1 for row in relation_rows if row["hit"])
    continuation_seconds = time.perf_counter() - continuation_start

    validation_start = time.perf_counter()
    validated = hit_count == 2
    validation_seconds = time.perf_counter() - validation_start

    plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    payload = {
        "status": "ok",
        "concept": "measure setup, hot relation work, continuation, and validation separately",
        "surface": plan.api_surface,
        "measurement": {
            "setup_seconds": setup_seconds,
            "hot_seconds": hot_seconds,
            "continuation_seconds": continuation_seconds,
            "validation_seconds": validation_seconds,
            "validated": validated,
        },
        "relation_rows": relation_rows,
        "app_output": {"hit_count": hit_count},
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if validated else 1


if __name__ == "__main__":
    raise SystemExit(main())
