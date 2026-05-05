#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt

from scripts.goal1292_v1_5_generic_optix_evidence_runner import _make_ray_triangle_case


GOAL = "Goal1296 v1.5 prepared scene session evidence"


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _cpu_count(rays: tuple[rt.Ray2D, ...], triangles: tuple[rt.Triangle, ...]) -> int:
    result = rt.run_generic_ray_triangle_any_hit_count(
        rays,
        triangles,
        backend="cpu",
        include_rows=False,
    )
    return int(result["hit_count"])


def build_payload(
    *,
    copies: int,
    query_repeats: int,
    prepare_scene=None,
    prepare_rays=None,
) -> dict[str, Any]:
    if copies <= 1:
        raise ValueError("copies must be greater than 1")
    if query_repeats <= 0:
        raise ValueError("query_repeats must be positive")

    rays, triangles = _make_ray_triangle_case(copies)
    split = (copies // 2) * 2
    ray_batches = (
        ("batch_a", rays[:split]),
        ("batch_b", rays[split:]),
    )
    expected_counts = {
        label: _cpu_count(batch_rays, triangles)
        for label, batch_rays in ray_batches
    }

    batch_results: list[dict[str, Any]] = []
    with rt.prepare_generic_ray_triangle_any_hit_scene(
        triangles=triangles,
        backend="optix",
        prepare_scene=prepare_scene,
        prepare_rays=prepare_rays,
    ) as session:
        scene_prepare_sec = float(session.scene_prepare_sec)
        for label, batch_rays in ray_batches:
            result = session.count(
                batch_rays,
                query_repeats=query_repeats,
                prepare_rays=prepare_rays,
            )
            batch_results.append(
                {
                    "label": label,
                    "ray_count": len(batch_rays),
                    "expected_hit_count": expected_counts[label],
                    "hit_count": int(result["hit_count"]),
                    "matches_cpu": int(result["hit_count"]) == expected_counts[label],
                    "query_batch_index": int(result["query_batch_index"]),
                    "scene_reusable": bool(result["scene_reusable"]),
                    "run_phases": result["run_phases"],
                }
            )

    return {
        "goal": GOAL,
        "source_commit": _git_head(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "fixture": {
            "copies": copies,
            "ray_count": len(rays),
            "triangle_count": len(triangles),
            "batch_count": len(batch_results),
            "query_repeats_per_batch": query_repeats,
        },
        "active_backends": ["optix"],
        "frozen_backends_before_v2_1": ["vulkan", "hiprt", "apple_rt"],
        "scene_prepare_sec": scene_prepare_sec,
        "batch_results": batch_results,
        "scene_prepare_paid_once": all(
            result["run_phases"]["scene_prepare_sec_this_batch"] == 0.0
            for result in batch_results
        ),
        "all_batches_match_cpu": all(result["matches_cpu"] for result in batch_results),
        "public_wording_authorized": False,
        "boundary": (
            "Internal v1.5 reusable prepared scene evidence only; no public speedup wording, "
            "whole-app claim, or Vulkan/HIPRT/Apple RT work is authorized."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run v1.5 reusable prepared scene evidence.")
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--query-repeats", type=int, default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = build_payload(copies=args.copies, query_repeats=args.query_repeats)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
