from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _dist(left: dict[str, float | int | str], right: dict[str, float | int | str]) -> float:
    dx = float(left["x"]) - float(right["x"])
    dy = float(left["y"]) - float(right["y"])
    return (dx * dx + dy * dy) ** 0.5


def _directed(source: tuple[dict[str, float | int | str], ...], target: tuple[dict[str, float | int | str], ...], name: str) -> dict[str, object]:
    nearest_rows = []
    for src in source:
        best = min(target, key=lambda dst: (_dist(src, dst), int(dst["id"])))
        nearest_rows.append(
            {
                "direction": name,
                "source_id": int(src["id"]),
                "nearest_id": int(best["id"]),
                "distance": round(_dist(src, best), 6),
            }
        )
    directed_distance = max(float(row["distance"]) for row in nearest_rows)
    return {"nearest_rows": tuple(nearest_rows), "directed_distance": directed_distance}


def main() -> int:
    set_a = (
        {"id": 1, "x": 0.0, "y": 0.0},
        {"id": 2, "x": 1.0, "y": 0.0},
    )
    set_b = (
        {"id": 10, "x": 0.2, "y": 0.0},
        {"id": 11, "x": 1.5, "y": 0.0},
    )
    a_to_b = _directed(set_a, set_b, "A_to_B")
    b_to_a = _directed(set_b, set_a, "B_to_A")
    hausdorff = max(float(a_to_b["directed_distance"]), float(b_to_a["directed_distance"]))
    threshold = 0.6
    threshold_decision = hausdorff <= threshold
    witness_plan = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
    threshold_plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    payload = {
        "status": "ok",
        "concept": "Hausdorff distance composes nearest-witness rows: nearest per source, max over sources, then max over both directions",
        "manual_data_flow": "A and B point sets -> directed nearest rows -> directed max distance -> undirected max -> optional threshold decision",
        "set_a": set_a,
        "set_b": set_b,
        "a_to_b": a_to_b,
        "b_to_a": b_to_a,
        "hausdorff_distance": round(hausdorff, 6),
        "threshold": threshold,
        "threshold_decision": threshold_decision,
        "v4_surfaces": {
            "witness": {"request": "point_group_nearest", "status": witness_plan.status, "surface": witness_plan.api_surface},
            "threshold": {"request": "fixed_radius", "status": threshold_plan.status, "surface": threshold_plan.api_surface},
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
