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


def _collision_relation() -> dict[str, object]:
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
        {
            "pose_id": pose["pose_id"],
            "collision": any(int(row["pose_id"]) == int(pose["pose_id"]) and bool(row["hit"]) for row in hit_rows),
        }
        for pose in poses
    )
    return {
        "poses": poses,
        "obstacles": obstacles,
        "link_segments": link_segments,
        "candidate_rows": candidate_rows,
        "hit_rows": hit_rows,
        "collision_flags": collision_flags,
    }


def run_relation_mode() -> dict[str, object]:
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Lower robot poses into link segments, emit link/obstacle hit rows, "
            "then reduce to pose collision flags. The V4 any-hit surface is only "
            "the execution route for the recognized hit relation."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "robot collision lowers sampled poses into link-hit rows and pose-level any-hit flags",
        "manual_data_flow": "poses + links + obstacles -> link segments -> candidate rows -> hit rows -> pose collision flags",
        "collision_contract": "sampled pose/link segments, not continuous-time motion",
        **_collision_relation(),
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "a pose collides when any emitted link/obstacle row has hit=true",
        "pose_id": 1,
        "candidate_row": {"pose_id": 1, "link_id": 0, "obstacle_id": 10},
        "hit_row": {"pose_id": 1, "link_id": 0, "obstacle_id": 10, "hit": True},
        "collision_flag": {"pose_id": 1, "collision": True},
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
        "relationship_to_relation": "The relation mode names link segments, obstacle rows, and pose groups. V4 maps the recognized any-hit flag shape to a measured surface.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Robot collision lowering tutorial.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "robot collision uses RTDL hit rows and grouped any-hit flags",
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
