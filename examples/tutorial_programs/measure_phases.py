from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _measure_flow() -> dict[str, object]:
    setup_start = time.perf_counter()
    input_rows = tuple({"query_id": query_id, "candidate_id": query_id + 100} for query_id in range(4))
    setup_seconds = time.perf_counter() - setup_start

    hot_start = time.perf_counter()
    relation_rows = tuple({**row, "hit": int(row["query_id"]) % 2 == 0} for row in input_rows)
    hot_seconds = time.perf_counter() - hot_start

    continuation_start = time.perf_counter()
    hit_count = sum(1 for row in relation_rows if bool(row["hit"]))
    continuation_seconds = time.perf_counter() - continuation_start

    validation_start = time.perf_counter()
    validated = hit_count == 2
    validation_seconds = time.perf_counter() - validation_start

    return {
        "input_rows": input_rows,
        "relation_rows": relation_rows,
        "app_output": {"hit_count": hit_count},
        "measurement": {
            "setup_seconds": setup_seconds,
            "hot_relation_seconds": hot_seconds,
            "continuation_seconds": continuation_seconds,
            "validation_seconds": validation_seconds,
            "validated": validated,
        },
    }


def run_relation_mode() -> dict[str, object]:
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Measure the same RTDL program shape every time: setup inputs, emit "
            "hot relation rows, run continuations, then validate/materialize. "
            "This file teaches phase boundaries rather than a new operator."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "measurement boundaries follow the RTDL program shape",
        "manual_data_flow": "setup inputs -> hot relation work -> continuation -> validation/materialization",
        **_measure_flow(),
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "phase_boundaries": (
            {"phase": "setup", "meaning": "build inputs and prepare reusable state"},
            {"phase": "hot_relation", "meaning": "emit relation rows or device outputs"},
            {"phase": "continuation", "meaning": "reduce, rank, group, or summarize rows"},
            {"phase": "validation", "meaning": "check correctness and materialize only what the app needs"},
        ),
        "lesson": "Do not compare setup-heavy timing with hot-path timing unless the denominator says so.",
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    return {
        "status": "ok",
        "mode": "v4",
        "operator": "any_hit",
        "partner": "torch",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "relationship_to_relation": "The measurement phases stay the same when the relation is executed by a V4 surface.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RTDL V4 phase-measurement tutorial.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "measure setup, hot relation work, continuation, and validation separately",
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
