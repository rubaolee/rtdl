from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _contribution(body: dict[str, float | int], source: dict[str, float | int]) -> dict[str, float | int]:
    dx = float(source["x"]) - float(body["x"])
    dy = float(source["y"]) - float(body["y"])
    dist_sq = dx * dx + dy * dy + 0.01
    inv_dist3 = 1.0 / (dist_sq ** 1.5)
    return {
        "body_id": int(body["id"]),
        "source_id": int(source["id"]),
        "fx": round(float(source["mass"]) * dx * inv_dist3, 6),
        "fy": round(float(source["mass"]) * dy * inv_dist3, 6),
    }


def main() -> int:
    bodies = (
        {"id": 1, "x": 0.0, "y": 0.0, "mass": 1.0},
        {"id": 2, "x": 0.2, "y": 0.1, "mass": 1.0},
        {"id": 3, "x": 3.0, "y": 0.0, "mass": 2.0},
    )
    aggregate_cells = (
        {"id": 100, "x": 0.1, "y": 0.05, "mass": 2.0, "half_width": 0.3},
        {"id": 101, "x": 3.0, "y": 0.0, "mass": 2.0, "half_width": 0.2},
    )
    theta = 0.5

    frontier_rows = []
    for body in bodies:
        for cell in aggregate_cells:
            dx = float(cell["x"]) - float(body["x"])
            dy = float(cell["y"]) - float(body["y"])
            distance = (dx * dx + dy * dy + 1.0e-9) ** 0.5
            width = 2.0 * float(cell["half_width"])
            accepts_aggregate = width / distance < theta
            if accepts_aggregate:
                frontier_rows.append(
                    {
                        "body_id": int(body["id"]),
                        "frontier_id": int(cell["id"]),
                        "kind": "aggregate_cell",
                        "opening_ratio": round(width / distance, 4),
                    }
                )
            else:
                for other in bodies:
                    if int(other["id"]) == int(body["id"]):
                        continue
                    frontier_rows.append(
                        {
                            "body_id": int(body["id"]),
                            "frontier_id": int(other["id"]),
                            "kind": "exact_body",
                            "opening_ratio": round(width / distance, 4),
                        }
                    )
                break

    sources_by_id = {
        **{int(body["id"]): body for body in bodies},
        **{int(cell["id"]): {"id": cell["id"], "x": cell["x"], "y": cell["y"], "mass": cell["mass"]} for cell in aggregate_cells},
    }
    contribution_rows = tuple(
        _contribution(next(body for body in bodies if int(body["id"]) == row["body_id"]), sources_by_id[int(row["frontier_id"])])
        for row in frontier_rows
    )
    force_by_body = []
    for body in bodies:
        rows = [row for row in contribution_rows if row["body_id"] == int(body["id"])]
        force_by_body.append(
            {
                "body_id": int(body["id"]),
                "fx": round(sum(float(row["fx"]) for row in rows), 6),
                "fy": round(sum(float(row["fy"]) for row in rows), 6),
                "frontier_count": len(rows),
            }
        )

    frontier_plan = rtdl_v4.plan_operator_request_v4("aggregate_frontier", partner="rtdl_native")
    grouped_plan = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
    payload = {
        "status": "ok",
        "concept": "Barnes-Hut starts by choosing aggregate-cell or exact-body frontier rows, then reduces vector contributions per body",
        "manual_data_flow": "bodies + aggregate cells -> frontier rows -> contribution rows -> grouped vector force",
        "theta": theta,
        "frontier_rows": tuple(frontier_rows),
        "contribution_rows": contribution_rows,
        "force_by_body": tuple(force_by_body),
        "v4_surfaces": {
            "frontier": {
                "request": "aggregate_frontier",
                "status": frontier_plan.status,
                "surface": frontier_plan.api_surface,
            },
            "continuation": {
                "request": "grouped_sum",
                "partner": "cupy",
                "status": grouped_plan.status,
                "surface": grouped_plan.api_surface,
            },
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
