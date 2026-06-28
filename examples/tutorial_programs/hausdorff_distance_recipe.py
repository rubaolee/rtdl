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


Point = dict[str, float | int]


def _dist(left: Point, right: Point) -> float:
    dx = float(left["x"]) - float(right["x"])
    dy = float(left["y"]) - float(right["y"])
    return (dx * dx + dy * dy) ** 0.5


def _directed(source: tuple[Point, ...], target: tuple[Point, ...], name: str) -> dict[str, object]:
    candidate_rows = tuple(
        {
            "direction": name,
            "source_id": int(src["id"]),
            "target_id": int(dst["id"]),
            "distance": round(_dist(src, dst), 6),
        }
        for src in source
        for dst in target
    )
    nearest_rows = []
    for src in source:
        rows = [row for row in candidate_rows if int(row["source_id"]) == int(src["id"])]
        best = min(rows, key=lambda row: (float(row["distance"]), int(row["target_id"])))
        nearest_rows.append(
            {
                "direction": name,
                "source_id": int(best["source_id"]),
                "nearest_id": int(best["target_id"]),
                "distance": float(best["distance"]),
            }
        )
    directed_distance = max(float(row["distance"]) for row in nearest_rows)
    return {
        "candidate_rows": candidate_rows,
        "nearest_rows": tuple(nearest_rows),
        "directed_distance": directed_distance,
    }


def _sets() -> tuple[tuple[Point, ...], tuple[Point, ...]]:
    set_a = (
        {"id": 1, "x": 0.0, "y": 0.0},
        {"id": 2, "x": 1.0, "y": 0.0},
    )
    set_b = (
        {"id": 10, "x": 0.2, "y": 0.0},
        {"id": 11, "x": 1.5, "y": 0.0},
    )
    return set_a, set_b


def run_relation_mode() -> dict[str, object]:
    set_a, set_b = _sets()
    a_to_b = _directed(set_a, set_b, "A_to_B")
    b_to_a = _directed(set_b, set_a, "B_to_A")
    hausdorff = max(float(a_to_b["directed_distance"]), float(b_to_a["directed_distance"]))
    threshold = 0.6
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Express directed Hausdorff as candidate rows, nearest-witness rows, "
            "and max reductions. The V4 route is an execution target for those "
            "recognized relations, not the source of the algorithm."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "Hausdorff composition is nearest-witness rows followed by max reductions in both directions",
        "manual_data_flow": "A/B point sets -> directed candidate rows -> nearest rows -> directed max -> symmetric max -> threshold decision",
        "set_a": set_a,
        "set_b": set_b,
        "a_to_b": a_to_b,
        "b_to_a": b_to_a,
        "hausdorff_distance": round(hausdorff, 6),
        "threshold": threshold,
        "threshold_decision": hausdorff <= threshold,
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "one directed Hausdorff row is the nearest target for a source point; the directed distance is the max of those nearest distances",
        "source_point": {"id": 2, "x": 1.0, "y": 0.0},
        "candidate_distances": ((10, 0.8), (11, 0.5)),
        "nearest_row": {"source_id": 2, "nearest_id": 11, "distance": 0.5},
        "directed_reduce": "max nearest distance over all sources",
    }


def run_v4_mode() -> dict[str, object]:
    witness_plan = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
    threshold_plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    return {
        "status": "ok",
        "mode": "v4",
        "relationship_to_relation": "The relation mode names candidate rows, nearest witness rows, and max reductions. V4 maps nearest-witness and threshold-decision shapes to explicit operator surfaces.",
        "v4_surfaces": {
            "witness": {
                "request": "point_group_nearest",
                "partner": "torch",
                "status": witness_plan.status,
                "surface": witness_plan.api_surface,
            },
            "threshold": {
                "request": "fixed_radius",
                "partner": "torch",
                "status": threshold_plan.status,
                "surface": threshold_plan.api_surface,
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hausdorff distance composition tutorial.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "Hausdorff is composed from nearest-witness rows and max reductions",
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
