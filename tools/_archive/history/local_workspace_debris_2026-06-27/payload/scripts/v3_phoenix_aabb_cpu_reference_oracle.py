#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.current.research_benchmarks.librts_spatial_index import (  # noqa: E402
    rtdl_librts_spatial_index_benchmark_app as app,
)


DEFAULT_EXPECTED_COUNTS = {
    "point_contains": 46_343_760,
    "range_contains": 32_302_908,
    "range_intersects": 70_429_254,
}


def _fixture_arrays(fixture: app.LibRTSFixture, *, dtype: np.dtype[Any] = np.dtype(np.float64)) -> dict[str, np.ndarray]:
    boxes = np.asarray(
        [(box.min_x, box.min_y, box.max_x, box.max_y) for box in fixture.boxes],
        dtype=dtype,
    )
    points = np.asarray([(point.x, point.y) for point in fixture.point_queries], dtype=dtype)
    query_boxes = np.asarray(
        [(box.min_x, box.min_y, box.max_x, box.max_y) for box in fixture.box_queries],
        dtype=dtype,
    )
    return {"boxes": boxes, "points": points, "query_boxes": query_boxes}


def _chunk_slices(length: int, chunk_size: int):
    for start in range(0, length, chunk_size):
        yield slice(start, min(length, start + chunk_size))


def count_point_contains(boxes: np.ndarray, points: np.ndarray, *, chunk_size: int) -> int:
    total = 0
    min_x = boxes[:, 0]
    min_y = boxes[:, 1]
    max_x = boxes[:, 2]
    max_y = boxes[:, 3]
    for chunk in _chunk_slices(len(points), chunk_size):
        qx = points[chunk, 0][:, None]
        qy = points[chunk, 1][:, None]
        hits = (min_x <= qx) & (max_x >= qx) & (min_y <= qy) & (max_y >= qy)
        total += int(np.count_nonzero(hits))
    return total


def count_range_contains(boxes: np.ndarray, query_boxes: np.ndarray, *, chunk_size: int) -> int:
    total = 0
    min_x = boxes[:, 0]
    min_y = boxes[:, 1]
    max_x = boxes[:, 2]
    max_y = boxes[:, 3]
    for chunk in _chunk_slices(len(query_boxes), chunk_size):
        qmin_x = query_boxes[chunk, 0][:, None]
        qmin_y = query_boxes[chunk, 1][:, None]
        qmax_x = query_boxes[chunk, 2][:, None]
        qmax_y = query_boxes[chunk, 3][:, None]
        hits = (min_x <= qmin_x) & (min_y <= qmin_y) & (max_x >= qmax_x) & (max_y >= qmax_y)
        total += int(np.count_nonzero(hits))
    return total


def count_range_intersects(boxes: np.ndarray, query_boxes: np.ndarray, *, chunk_size: int) -> int:
    total = 0
    min_x = boxes[:, 0]
    min_y = boxes[:, 1]
    max_x = boxes[:, 2]
    max_y = boxes[:, 3]
    for chunk in _chunk_slices(len(query_boxes), chunk_size):
        qmin_x = query_boxes[chunk, 0][:, None]
        qmin_y = query_boxes[chunk, 1][:, None]
        qmax_x = query_boxes[chunk, 2][:, None]
        qmax_y = query_boxes[chunk, 3][:, None]
        hits = (qmin_x <= max_x) & (qmax_x >= min_x) & (qmin_y <= max_y) & (qmax_y >= min_y)
        total += int(np.count_nonzero(hits))
    return total


def run_oracle(
    *,
    box_count: int,
    query_count: int,
    seed: int,
    chunk_size: int,
    dtype_name: str,
    expected_counts: dict[str, int] | None,
) -> dict[str, Any]:
    fixture = app.make_uniform_fixture(box_count=box_count, query_count=query_count, seed=seed)
    if dtype_name == "float32":
        dtype = np.dtype(np.float32)
    elif dtype_name == "float64":
        dtype = np.dtype(np.float64)
    else:
        raise ValueError("dtype_name must be float32 or float64")
    arrays = _fixture_arrays(fixture, dtype=dtype)
    started = time.perf_counter()
    counts: dict[str, int] = {}
    operation_times: dict[str, float] = {}

    op_started = time.perf_counter()
    counts["point_contains"] = count_point_contains(arrays["boxes"], arrays["points"], chunk_size=chunk_size)
    operation_times["point_contains_sec"] = time.perf_counter() - op_started

    op_started = time.perf_counter()
    counts["range_contains"] = count_range_contains(arrays["boxes"], arrays["query_boxes"], chunk_size=chunk_size)
    operation_times["range_contains_sec"] = time.perf_counter() - op_started

    op_started = time.perf_counter()
    counts["range_intersects"] = count_range_intersects(arrays["boxes"], arrays["query_boxes"], chunk_size=chunk_size)
    operation_times["range_intersects_sec"] = time.perf_counter() - op_started

    elapsed = time.perf_counter() - started
    expected = expected_counts or {}
    expected_comparison = {
        name: {
            "expected": int(expected[name]),
            "actual": int(counts[name]),
            "matches": int(counts[name]) == int(expected[name]),
        }
        for name in expected
        if name in counts
    }
    return {
        "tool": "v3_phoenix_aabb_cpu_reference_oracle",
        "status": "pass" if expected_comparison and all(row["matches"] for row in expected_comparison.values()) else "complete",
        "mode": "numpy_chunked_cpu_reference",
        "numeric_dtype": dtype_name,
        "app": "librts_spatial_index",
        "generic_capability": "aabb_candidate_stream",
        "primitive_contract": "generic_prepared_aabb_index_query_2d",
        "operation": "all",
        "fixture": fixture.metadata(),
        "chunk_size": int(chunk_size),
        "counts": counts,
        "expected_comparison": expected_comparison,
        "elapsed_sec": elapsed,
        "operation_times_sec": operation_times,
        "oracle_boundary": (
            "Independent chunked NumPy CPU oracle for Phoenix V3 evidence. "
            "It is not a product runtime path, not LibRTS authors-code timing, "
            "and not public speedup wording."
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 AABB Chunked CPU Reference Oracle",
        "",
        "Status: evidence oracle, not release authorization.",
        "",
        "This artifact validates the large 32,768/32,768 AABB count-only row",
        "with an independent chunked NumPy CPU oracle. It is not a product runtime",
        "path and not LibRTS authors-code timing.",
        "",
        "```text",
        f"status: {payload['status']}",
        f"box_count: {payload['fixture']['box_count']}",
        f"point_query_count: {payload['fixture']['point_query_count']}",
        f"box_query_count: {payload['fixture']['box_query_count']}",
        f"chunk_size: {payload['chunk_size']}",
        f"elapsed_sec: {payload['elapsed_sec']:.6f}",
        "```",
        "",
        "## Counts",
        "",
        "| Operation | Count | Matches expected |",
        "| --- | ---: | --- |",
    ]
    comparisons = payload.get("expected_comparison", {})
    for name, value in payload["counts"].items():
        match = comparisons.get(name, {}).get("matches")
        match_text = "n/a" if match is None else str(bool(match)).lower()
        lines.append(f"| `{name}` | {int(value):,} | `{match_text}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This closes the `cpu_reference_skipped_and_matches_reference_null` evidence gap for the exact large AABB row.",
            "- It does not make the row paper-equivalent.",
            "- It does not provide LibRTS authors-code timing.",
            "- It does not authorize V3-over-V2 wording.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chunked NumPy CPU oracle for Phoenix V3 AABB count-only rows.")
    parser.add_argument("--box-count", type=int, default=32768)
    parser.add_argument("--query-count", type=int, default=32768)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--chunk-size", type=int, default=256)
    parser.add_argument("--dtype", choices=("float32", "float64"), default="float64")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--no-default-expected", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected = None if args.no_default_expected else DEFAULT_EXPECTED_COUNTS
    payload = run_oracle(
        box_count=args.box_count,
        query_count=args.query_count,
        seed=args.seed,
        chunk_size=args.chunk_size,
        dtype_name=args.dtype,
        expected_counts=expected,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"pass", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
