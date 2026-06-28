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
        {"query_id": 1, "candidate_id": 10, "distance": 0.10, "score": 9.0},
        {"query_id": 1, "candidate_id": 11, "distance": 0.20, "score": 7.0},
        {"query_id": 1, "candidate_id": 12, "distance": 0.55, "score": 3.0},
        {"query_id": 2, "candidate_id": 20, "distance": 0.15, "score": 8.0},
        {"query_id": 2, "candidate_id": 21, "distance": 0.25, "score": 6.0},
    )
    radius = 0.30
    top_k = 2
    eligible_rows = tuple(row for row in candidate_rows if float(row["distance"]) <= radius)
    ranked_rows = []
    summary_rows = []
    for query_id in sorted({row["query_id"] for row in candidate_rows}):
        rows = [row for row in eligible_rows if row["query_id"] == query_id]
        rows.sort(key=lambda row: (-float(row["score"]), float(row["distance"]), int(row["candidate_id"])))
        for rank, row in enumerate(rows[:top_k], 1):
            ranked_rows.append({**row, "rank": rank})
        summary_rows.append(
            {
                "query_id": query_id,
                "kept": len(rows[:top_k]),
                "best_candidate": rows[0]["candidate_id"] if rows else None,
                "best_score": rows[0]["score"] if rows else None,
            }
        )

    plan = rtdl_v4.plan_operator_request_v4("ranked_summary", partner="rtdl_native")
    payload = {
        "status": "ok",
        "concept": "RTNN ranked summary keeps bounded top candidates after a radius or nearest-witness relation has emitted rows",
        "manual_data_flow": "candidate rows -> radius filter -> sort by score and distance -> top-k rows -> per-query summary",
        "radius": radius,
        "top_k": top_k,
        "candidate_rows": candidate_rows,
        "eligible_rows": eligible_rows,
        "ranked_rows": tuple(ranked_rows),
        "summary_rows": tuple(summary_rows),
        "v4_surface": {
            "request": "ranked_summary",
            "partner": "rtdl_native",
            "status": plan.status,
            "surface": plan.api_surface,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
