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


REQUESTS = (
    ("fixed_radius", ("torch", "cupy"), "radius-neighbor relation rows"),
    ("grouped_sum", ("cupy", "torch"), "grouped continuation over existing rows"),
    ("component_union", ("numba", "torch"), "component labels from neighbor-edge rows"),
    ("aabb_index_query", ("rtdl_native", "cupy"), "AABB predicate rows"),
    ("custom_predicate_early_exit", ("numba", "torch"), "constrained predicate boundary"),
)


def _plan_rows() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for operator, partners, relation_shape in REQUESTS:
        for partner in partners:
            kwargs = {}
            if operator == "custom_predicate_early_exit" and partner == "numba":
                kwargs = {
                    "callback_shape": "pure_boolean_numba_cabi_device_function",
                    "numba_device_function": True,
                }
            plan = rtdl_v4.plan_operator_request_v4(operator, partner=partner, **kwargs)
            rows.append(
                {
                    "operator": operator,
                    "relation_shape": relation_shape,
                    "partner": partner,
                    "status": plan.status,
                    "surface": plan.api_surface,
                    "generic_primitive": plan.generic_primitive,
                    "interpretation": (
                        "measured public route"
                        if "ready" in plan.status
                        else "visible boundary; choose another partner or decompose the program"
                    ),
                }
            )
    return tuple(rows)


def run_relation_mode() -> dict[str, object]:
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Choose the RTDL relation first, such as neighbor rows or grouped "
            "continuation rows. Partner choice is only the execution policy for "
            "that already-defined relation."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "partner choice happens after the RTDL relation shape is known",
        "manual_data_flow": (
            "choose row relation -> choose continuation -> choose partner -> inspect planner status -> run or decompose"
        ),
        "stable_intents": tuple(
            {"operator": operator, "relation_shape": relation_shape}
            for operator, _partners, relation_shape in REQUESTS
        ),
        "teaches": "Torch, CuPy, Numba, and RTDL native are execution policies, not different app meanings.",
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "same operator intent, different partner result",
        "operator": "component_union",
        "relation_shape": "neighbor-edge rows to component labels",
        "partner_outcomes": tuple(
            row for row in _plan_rows() if row["operator"] == "component_union"
        ),
        "lesson": "A deferred partner is not a failed app. It means the user should choose the measured partner or keep that step app-owned.",
    }


def run_v4_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "v4",
        "concept": "planner matrix for explicit partner choice",
        "rows": _plan_rows(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RTDL V4 explicit partner-choice tutorial.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "partner choice is explicit and visible at planning time",
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
