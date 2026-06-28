from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _candidate_rows() -> tuple[dict[str, float | int], ...]:
    return (
        {"query_id": 1, "candidate_id": 10, "distance": 0.10, "score": 9.0},
        {"query_id": 1, "candidate_id": 11, "distance": 0.20, "score": 7.0},
        {"query_id": 1, "candidate_id": 12, "distance": 0.55, "score": 3.0},
        {"query_id": 2, "candidate_id": 20, "distance": 0.15, "score": 8.0},
        {"query_id": 2, "candidate_id": 21, "distance": 0.25, "score": 6.0},
    )


def _rank_rows(
    candidate_rows: tuple[dict[str, float | int], ...],
    *,
    radius: float,
    top_k: int,
) -> dict[str, object]:
    eligible_rows = tuple(row for row in candidate_rows if float(row["distance"]) <= radius)
    ranked_rows: list[dict[str, float | int]] = []
    summary_rows: list[dict[str, float | int | None]] = []
    for query_id in sorted({int(row["query_id"]) for row in candidate_rows}):
        rows = [row for row in eligible_rows if int(row["query_id"]) == query_id]
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
    return {
        "eligible_rows": eligible_rows,
        "ranked_rows": tuple(ranked_rows),
        "summary_rows": tuple(summary_rows),
    }


def run_relation_mode() -> dict[str, object]:
    radius = 0.30
    top_k = 2
    rows = _candidate_rows()
    ranked = _rank_rows(rows, radius=radius, top_k=top_k)
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Emit candidate rows, filter by radius, rank deterministically, and "
            "summarize per query. V4 planning is shown only after the row contract "
            "and continuation rule are visible."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "ranked summary is a continuation over candidate rows, not a hidden nearest-neighbor app",
        "manual_data_flow": "candidate rows -> radius filter -> order by score/distance/id -> top-k rows -> per-query summary",
        "radius": radius,
        "top_k": top_k,
        "candidate_rows": rows,
        **ranked,
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "for one query, keep only eligible candidates and rank them deterministically",
        "query_id": 1,
        "input_rows": tuple(row for row in _candidate_rows() if int(row["query_id"]) == 1),
        "eligible_candidate_ids": (10, 11),
        "rank_rule": "higher score first, then shorter distance, then lower candidate id",
        "ranked_candidate_ids": (10, 11),
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("ranked_summary", partner="rtdl_native")
    return {
        "status": "ok",
        "mode": "v4",
        "operator": "ranked_summary",
        "partner": "rtdl_native",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "relationship_to_relation": "The relation mode names candidate rows and ranking rules. V4 planning identifies whether this recognized ranked-summary shape has a public measured surface.",
        "teaches": "V4 can plan recognized top-k summary patterns, while the app still owns the scoring semantics.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ranked summary continuation over RTDL candidate rows.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "ranked summary turns emitted candidate rows into bounded top-k rows",
    }
    if args.mode in {"relation", "both"}:
        payload["relation_mode"] = run_relation_mode()
    if args.mode in {"v4", "both"}:
        payload["v4_mode"] = run_v4_mode()
    if args.mode == "visible":
        payload["visible_flow"] = run_visible_mode()

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
