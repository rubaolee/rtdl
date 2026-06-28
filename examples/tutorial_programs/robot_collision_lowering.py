from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _segment_crosses_vertical(segment: dict[str, float | int], x: float, y0: float, y1: float) -> bool:
    x0 = float(segment["x0"])
    x1 = float(segment["x1"])
    if (x0 < x and x1 < x) or (x0 > x and x1 > x):
        return False
    t = (x - x0) / (x1 - x0) if x1 != x0 else 0.0
    if t < 0.0 or t > 1.0:
        return False
    y = float(segment["y0"]) + t * (float(segment["y1"]) - float(segment["y0"]))
    return y0 <= y <= y1


def main() -> int:
    poses = (
        {"pose_id": 1, "base_x": 0.0, "base_y": 0.0, "link_dx": 1.0, "link_dy": 0.0},
        {"pose_id": 2, "base_x": 0.0, "base_y": 0.5, "link_dx": 1.0, "link_dy": 0.0},
    )
    obstacles = ({"obstacle_id": 10, "x": 0.5, "y0": -0.2, "y1": 0.2},)
    link_segments = tuple(
        {
            "pose_id": int(pose["pose_id"]),
            "link_id": 0,
            "x0": float(pose["base_x"]),
            "y0": float(pose["base_y"]),
            "x1": float(pose["base_x"]) + float(pose["link_dx"]),
            "y1": float(pose["base_y"]) + float(pose["link_dy"]),
        }
        for pose in poses
    )
    candidate_rows = tuple(
        {"pose_id": seg["pose_id"], "link_id": seg["link_id"], "obstacle_id": obs["obstacle_id"]}
        for seg in link_segments
        for obs in obstacles
    )
    hit_rows = tuple(
        {
            "pose_id": seg["pose_id"],
            "link_id": seg["link_id"],
            "obstacle_id": obs["obstacle_id"],
            "hit": _segment_crosses_vertical(seg, float(obs["x"]), float(obs["y0"]), float(obs["y1"])),
        }
        for seg in link_segments
        for obs in obstacles
    )
    collision_flags = tuple(
        {"pose_id": pose["pose_id"], "collision": any(row["pose_id"] == pose["pose_id"] and row["hit"] for row in hit_rows)}
        for pose in poses
    )
    plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    payload = {
        "status": "ok",
        "concept": "Robot collision lowers each pose and link into grouped segment queries, then reduces hit rows to pose-level flags",
        "manual_data_flow": "poses + links + obstacles -> link segments -> candidate rows -> hit rows -> pose collision flags",
        "collision_contract": "sampled pose/link segments, not continuous-time motion",
        "link_segments": link_segments,
        "candidate_rows": candidate_rows,
        "hit_rows": hit_rows,
        "collision_flags": collision_flags,
        "v4_surface": {"request": "any_hit", "partner": "torch", "status": plan.status, "surface": plan.api_surface},
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
