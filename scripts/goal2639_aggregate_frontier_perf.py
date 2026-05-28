from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app


def _parse_sizes(text: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("sizes must be positive comma-separated integers")
    return values


def _loops_for_size(size: int) -> int:
    if size <= 2048:
        return 7
    if size <= 8192:
        return 5
    if size <= 16384:
        return 4
    return 3


def run_perf(*, sizes: tuple[int, ...], bucket_size: int, warmups: int) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for body_count in sizes:
        bodies = app.make_generated_bodies(body_count)
        tree_t0 = time.perf_counter()
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=bucket_size)
        tree_seconds = time.perf_counter() - tree_t0
        expected = rt.collect_aggregate_frontier_2d(bodies, tree["nodes"], theta=app.THETA)
        expected_rows = expected["summary"]["frontier_row_count"]
        print(
            f"RUN n={body_count} nodes={len(tree['nodes'])} frontier_rows={expected_rows}",
            flush=True,
        )

        for backend, fn in (
            ("embree_native", rt.collect_aggregate_frontier_2d_embree),
            ("optix_native", rt.collect_aggregate_frontier_2d_optix),
        ):
            for _ in range(warmups):
                result = fn(bodies, tree["nodes"], theta=app.THETA, max_total_rows=expected_rows)
                if result["frontier_i64_rows"] != expected["frontier_i64_rows"]:
                    raise RuntimeError(f"warmup mismatch backend={backend} body_count={body_count}")

            loops = _loops_for_size(body_count)
            samples = []
            for _ in range(loops):
                t0 = time.perf_counter()
                result = fn(bodies, tree["nodes"], theta=app.THETA, max_total_rows=expected_rows)
                elapsed = time.perf_counter() - t0
                if (
                    result["frontier_i64_rows"] != expected["frontier_i64_rows"]
                    or result["row_offsets"] != expected["row_offsets"]
                ):
                    raise RuntimeError(f"mismatch backend={backend} body_count={body_count}")
                samples.append(elapsed)
            row = {
                "backend": backend,
                "body_count": body_count,
                "bucket_size": bucket_size,
                "frontier_row_count": expected_rows,
                "loops": loops,
                "mean_seconds": statistics.mean(samples),
                "median_seconds": statistics.median(samples),
                "min_seconds": min(samples),
                "samples_seconds": samples,
                "tree_build_seconds": tree_seconds,
                "tree_node_count": len(tree["nodes"]),
                "warmups": warmups,
            }
            rows.append(row)
            print(
                f"  {backend}: median={row['median_seconds']:.6f}s min={row['min_seconds']:.6f}s",
                flush=True,
            )

    pairs = []
    for body_count in sizes:
        embree = next(row for row in rows if row["body_count"] == body_count and row["backend"] == "embree_native")
        optix = next(row for row in rows if row["body_count"] == body_count and row["backend"] == "optix_native")
        embree_median = float(embree["median_seconds"])
        optix_median = float(optix["median_seconds"])
        pairs.append(
            {
                "body_count": body_count,
                "frontier_row_count": embree["frontier_row_count"],
                "embree_median_seconds": embree_median,
                "optix_median_seconds": optix_median,
                "optix_over_embree_speedup": embree_median / optix_median if optix_median else None,
                "winner": "optix_native" if optix_median < embree_median else "embree_native",
            }
        )

    return {
        "claim_boundary": (
            "Embree native vs OptiX-library native row collection only; current "
            "OptiX symbol is host-side generic traversal, not RT-core traversal "
            "or Barnes-Hut whole-app acceleration."
        ),
        "goal": "Goal2639 aggregate-frontier Embree vs OptiX row-collector perf",
        "pairs": pairs,
        "rows": rows,
        "sizes": sizes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=_parse_sizes, default=(2048, 8192, 16384, 32768))
    parser.add_argument("--bucket-size", type=int, default=16)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.bucket_size <= 0:
        raise ValueError("--bucket-size must be positive")
    if args.warmups < 0:
        raise ValueError("--warmups must be non-negative")

    payload = run_perf(sizes=args.sizes, bucket_size=args.bucket_size, warmups=args.warmups)
    text = json.dumps(payload, indent=2, sort_keys=True)
    print("JSON_RESULT_START")
    print(text)
    print("JSON_RESULT_END")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
