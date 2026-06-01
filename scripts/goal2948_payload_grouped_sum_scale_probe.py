from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

import rtdsl as rt
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D


def _triangles(count: int) -> tuple[Triangle3D, ...]:
    return tuple(
        Triangle3D(
            id=index,
            x0=0.0,
            y0=0.0,
            z0=float(index),
            x1=1.0,
            y1=0.0,
            z1=float(index),
            x2=0.0,
            y2=1.0,
            z2=float(index),
        )
        for index in range(count)
    )


def _rays(count: int, triangle_count: int) -> tuple[Ray3D, ...]:
    return tuple(
        Ray3D(
            id=index,
            ox=0.25,
            oy=0.25,
            oz=-1.0,
            dx=0.0,
            dy=0.0,
            dz=1.0,
            tmax=float(triangle_count + 2),
        )
        for index in range(count)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--ray-count", type=int, default=4096)
    parser.add_argument("--triangle-count", type=int, default=64)
    parser.add_argument("--group-count", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    args = parser.parse_args()

    if args.ray_count <= 0 or args.triangle_count <= 0 or args.group_count <= 0:
        raise ValueError("ray-count, triangle-count, and group-count must be positive")
    if args.repeats <= 0 or args.warmups < 0:
        raise ValueError("repeats must be positive and warmups non-negative")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    triangles = _triangles(args.triangle_count)
    rays = _rays(args.ray_count, args.triangle_count)
    primitive_group_ids = tuple(index % args.group_count for index in range(args.triangle_count))
    primitive_values = tuple(1.0 + 0.25 * (index % 5) for index in range(args.triangle_count))
    max_rows = args.ray_count * args.triangle_count

    expected_counts = [0 for _ in range(args.group_count)]
    expected_sums = [0.0 for _ in range(args.group_count)]
    for group_id, value in zip(primitive_group_ids, primitive_values):
        expected_counts[group_id] += args.ray_count
        expected_sums[group_id] += args.ray_count * value

    print(
        "[goal2948] preparing payload grouped sum "
        f"rays={args.ray_count} triangles={args.triangle_count} rows={max_rows}",
        flush=True,
    )
    with rt.prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
        triangles,
        primitive_group_ids=primitive_group_ids,
        primitive_values=primitive_values,
        group_count=args.group_count,
        partner="cupy",
    ) as prepared:
        warmup_results = []
        for warmup_index in range(args.warmups):
            print(f"[goal2948] warmup {warmup_index + 1}/{args.warmups}", flush=True)
            warmup_results.append(_run_once(prepared, rays, max_rows))
        timed_results = []
        for repeat_index in range(args.repeats):
            print(f"[goal2948] timed repeat {repeat_index + 1}/{args.repeats}", flush=True)
            timed_results.append(_run_once(prepared, rays, max_rows))

    for result in timed_results:
        if result["summary"]["row_count"] != max_rows:
            raise RuntimeError("unexpected hit-stream row count")
        if result["group_hit_counts"] != expected_counts:
            raise RuntimeError("group hit counts do not match expected all-plane hits")
        for observed, expected in zip(result["group_payload_sums"], expected_sums):
            if abs(observed - expected) > 1e-6 * max(1.0, abs(expected)):
                raise RuntimeError("group payload sums do not match expected all-plane hits")

    elapsed_values = [row["elapsed_sec"] for row in timed_results]
    consumer_values = [
        row["metadata"]["phase_timing_seconds"][
            "event_ordered_partner_payload_grouped_sum_consumer_and_materialization"
        ]
        for row in timed_results
    ]
    native_launch_values = [
        row["metadata"]["phase_timing_seconds"]["native_async_launch_enqueue"]
        for row in timed_results
    ]
    payload = {
        "goal": "Goal2948",
        "status": "pass",
        "source_commit": _git_output("rev-parse", "HEAD"),
        "source_dirty": _git_output("status", "--short").splitlines(),
        "ray_count": args.ray_count,
        "triangle_count": args.triangle_count,
        "expected_row_count": max_rows,
        "group_count": args.group_count,
        "warmups": args.warmups,
        "repeats": args.repeats,
        "elapsed_median_sec": statistics.median(elapsed_values),
        "consumer_median_sec": statistics.median(consumer_values),
        "native_launch_enqueue_median_sec": statistics.median(native_launch_values),
        "rows_per_second_median": max_rows / statistics.median(elapsed_values),
        "consumer_rows_per_second_median": max_rows / statistics.median(consumer_values),
        "timed_results": timed_results,
        "warmup_results": warmup_results,
        "expected_group_hit_counts": expected_counts,
        "expected_group_payload_sums": expected_sums,
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_5_release_authorized": False,
            "rayjoin_paper_claim_authorized": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "[goal2948] wrote "
        f"{output} median={payload['elapsed_median_sec']:.6f}s "
        f"consumer={payload['consumer_median_sec']:.6f}s",
        flush=True,
    )


def _run_once(prepared, rays, max_rows: int) -> dict[str, object]:
    started = time.perf_counter()
    result = prepared.run(
        rays,
        max_rows=max_rows,
        deduplicate_primitives=False,
        return_device_buffers=True,
    )
    elapsed = time.perf_counter() - started
    hit_buffers = result["hit_buffers"]
    output_buffers = result["output_buffers"]
    try:
        return {
            "elapsed_sec": elapsed,
            "summary": result["summary"],
            "group_hit_counts": list(result["group_hit_counts"]),
            "group_payload_sums": list(result["group_payload_sums"]),
            "metadata": result["metadata"],
        }
    finally:
        output_buffers.close()
        hit_buffers.close()


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
