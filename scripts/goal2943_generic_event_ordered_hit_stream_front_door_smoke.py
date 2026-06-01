from __future__ import annotations

import argparse
import json
from pathlib import Path
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
    print("[goal2943] running generic event-ordered hit-stream grouped front door", flush=True)
    started = time.perf_counter()
    result = rt.run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(
        rays,
        triangles,
        partner="cupy",
        group_count=3,
        max_rows=8,
        deduplicate_primitives=False,
        return_device_buffers=True,
    )
    elapsed = time.perf_counter() - started
    hit_buffers = result["hit_buffers"]
    group_buffers = result["group_buffers"]
    try:
        group_counts = [int(value) for value in group_buffers.group_hit_counts.detach().cpu().tolist()]
        group_sums = [int(value) for value in group_buffers.group_primitive_id_sum.detach().cpu().tolist()]
        payload = {
            "goal": "Goal2943",
            "status": "pass",
            "elapsed_sec": elapsed,
            "summary": result["summary"],
            "group_hit_counts": group_counts,
            "group_primitive_id_sum": group_sums,
            "metadata": result["metadata"],
            "claim_boundary": {
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_5_release_authorized": False,
            },
        }
    finally:
        group_buffers.close()
        hit_buffers.close()

    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2943] wrote {output}", flush=True)


if __name__ == "__main__":
    main()
