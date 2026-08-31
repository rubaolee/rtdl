from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import rtdsl as rt


def _grid_boxes(count: int) -> list[tuple[float, float, float, float]]:
    width = max(1, int(count**0.5))
    boxes: list[tuple[float, float, float, float]] = []
    for index in range(count):
        x = float(index % width) * 2.0
        y = float(index // width) * 2.0
        boxes.append((x, y, x + 1.0, y + 1.0))
    return boxes


def run_gate(*, box_count: int, repeats: int, gpu_label: str) -> dict[str, object]:
    if box_count < 2 or repeats < 3:
        raise ValueError("box_count must be >=2 and repeats must be >=3")
    base_boxes = _grid_boxes(box_count)
    query = ((0.25, 0.25, 0.75, 0.75),)
    near = base_boxes[0]
    far = (-10.0, -10.0, -9.0, -9.0)

    mutable = rt.prepare_mutable_aabb_index_2d(
        base_boxes,
        indexed_ids=range(box_count),
        backend="optix",
    )
    refit_seconds: list[float] = []
    refit_counts: list[int] = []
    refit_models: list[str] = []
    try:
        for iteration in range(repeats):
            replacement = far if iteration % 2 == 0 else near
            start = time.perf_counter()
            mutation = mutable.update(((0, replacement),))
            refit_seconds.append(time.perf_counter() - start)
            refit_models.append(str(mutation["mutation_execution_model"]))
            refit_counts.append(
                mutable.count(box_queries=query, operation="range_intersects")["counts"][
                    "range_intersects"
                ]
            )
    finally:
        mutable.close()

    rebuild_seconds: list[float] = []
    rebuild_counts: list[int] = []
    for iteration in range(repeats):
        candidate = list(base_boxes)
        candidate[0] = far if iteration % 2 == 0 else near
        start = time.perf_counter()
        prepared = rt.prepare_aabb_index_2d(
            candidate,
            indexed_ids=range(box_count),
            backend="optix",
        )
        rebuild_seconds.append(time.perf_counter() - start)
        try:
            rebuild_counts.append(
                prepared.count(box_queries=query, operation="range_intersects")["counts"][
                    "range_intersects"
                ]
            )
        finally:
            prepared.close()

    expected_counts = [0 if index % 2 == 0 else 1 for index in range(repeats)]
    refit_median = statistics.median(refit_seconds)
    rebuild_median = statistics.median(rebuild_seconds)
    matched = bool(
        refit_counts == rebuild_counts == expected_counts
        and set(refit_models) == {"native_sparse_slot_refit_with_rollback"}
    )
    return {
        "schema": "rtdl.generic_optix_aabb_native_refit_gate.v1",
        "status": "matched" if matched else "mismatch",
        "matched": matched,
        "environment": {
            "host": platform.node(),
            "platform": platform.platform(),
            "gpu": gpu_label,
        },
        "workload": {
            "box_count": box_count,
            "repeats": repeats,
            "updated_slot_count_per_iteration": 1,
            "primitive_cardinality_unchanged": True,
        },
        "correctness": {
            "expected_counts": expected_counts,
            "native_refit_counts": refit_counts,
            "snapshot_rebuild_counts": rebuild_counts,
            "mutation_execution_models": refit_models,
        },
        "timing_diagnostic": {
            "native_refit_seconds": refit_seconds,
            "snapshot_rebuild_seconds": rebuild_seconds,
            "native_refit_median_seconds": refit_median,
            "snapshot_rebuild_median_seconds": rebuild_median,
            "same_host_microbenchmark_speedup": rebuild_median / refit_median,
        },
        "claim_boundary": {
            "generic_native_refit_functional_claimed": matched,
            "same_host_microbenchmark_claimed": matched,
            "librts_paper_performance_claimed": False,
            "author_performance_parity_claimed": False,
            "native_incremental_insert_delete_claimed": False,
            "embree_used": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generic OptiX AABB native-refit gate")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--box-count", type=int, default=4096)
    parser.add_argument("--repeats", type=int, default=11)
    parser.add_argument("--gpu-label", default="unspecified")
    args = parser.parse_args()
    payload = run_gate(box_count=args.box_count, repeats=args.repeats, gpu_label=args.gpu_label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
