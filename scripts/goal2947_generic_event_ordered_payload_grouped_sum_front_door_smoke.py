from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time

import rtdsl as rt
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D


def _fixture() -> tuple[tuple[Ray3D, ...], tuple[Triangle3D, ...]]:
    triangles = (
        Triangle3D(
            id=0,
            x0=0.0,
            y0=0.0,
            z0=0.0,
            x1=1.0,
            y1=0.0,
            z1=0.0,
            x2=0.0,
            y2=1.0,
            z2=0.0,
        ),
        Triangle3D(
            id=1,
            x0=0.0,
            y0=0.0,
            z0=1.0,
            x1=1.0,
            y1=0.0,
            z1=1.0,
            x2=0.0,
            y2=1.0,
            z2=1.0,
        ),
    )
    rays = (
        Ray3D(id=0, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0),
        Ray3D(id=1, ox=2.0, oy=2.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0),
        Ray3D(id=2, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0),
    )
    return rays, triangles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    rays, triangles = _fixture()
    print("[goal2947] running generic event-ordered primitive-payload grouped sum", flush=True)
    started = time.perf_counter()
    result = rt.run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
        rays,
        triangles,
        primitive_group_ids=(0, 2),
        primitive_values=(10.5, 1.25),
        group_count=3,
        partner="cupy",
        max_rows=8,
        deduplicate_primitives=False,
        return_device_buffers=True,
    )
    elapsed = time.perf_counter() - started
    hit_buffers = result["hit_buffers"]
    output_buffers = result["output_buffers"]
    try:
        payload = {
            "goal": "Goal2947",
            "status": "pass",
            "source_commit": _git_output("rev-parse", "HEAD"),
            "source_dirty": _git_output("status", "--short").splitlines(),
            "elapsed_sec": elapsed,
            "summary": result["summary"],
            "group_hit_counts": list(result["group_hit_counts"]),
            "group_payload_sums": list(result["group_payload_sums"]),
            "metadata": result["metadata"],
            "claim_boundary": {
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_5_release_authorized": False,
            },
        }
    finally:
        output_buffers.close()
        hit_buffers.close()

    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2947] wrote {output}", flush=True)


def _git_output(*args: str) -> str:
    try:
        completed = subprocess.run(
            ("git", *args),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception:
        return ""
    return completed.stdout.strip()


if __name__ == "__main__":
    main()
