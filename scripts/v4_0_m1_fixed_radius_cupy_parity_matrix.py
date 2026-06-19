#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _case(
    name: str,
    *,
    search_xy: list[tuple[float, float]],
    query_xy: list[tuple[float, float]],
    radius: float,
    threshold: int,
) -> dict[str, object]:
    return {
        "name": name,
        "search_xy": search_xy,
        "query_xy": query_xy,
        "radius": float(radius),
        "threshold": int(threshold),
    }


def _random_case() -> dict[str, object]:
    rng = np.random.default_rng(7)
    search = rng.uniform(-1.0, 1.0, size=(8, 2))
    query = rng.uniform(-1.0, 1.0, size=(5, 2))
    return _case(
        "random_seed_7",
        search_xy=[tuple(map(float, row)) for row in search],
        query_xy=[tuple(map(float, row)) for row in query],
        radius=0.65,
        threshold=2,
    )


def _cases() -> list[dict[str, object]]:
    return [
        _case(
            "smoke",
            search_xy=[(0.0, 0.0), (3.0, 0.0), (0.0, 4.0)],
            query_xy=[(0.0, 0.0), (3.0, 0.0), (9.0, 9.0)],
            radius=1.1,
            threshold=1,
        ),
        _case(
            "all_miss",
            search_xy=[(0.0, 0.0), (2.0, 2.0)],
            query_xy=[(5.0, 5.0), (-5.0, -5.0)],
            radius=0.5,
            threshold=1,
        ),
        _case(
            "boundary_inclusive",
            search_xy=[(1.0, 0.0), (0.0, 2.0)],
            query_xy=[(0.0, 0.0)],
            radius=1.0,
            threshold=1,
        ),
        _case(
            "threshold_caps_count",
            search_xy=[(0.0, 0.0), (0.2, 0.0), (2.0, 0.0)],
            query_xy=[(0.0, 0.0)],
            radius=0.5,
            threshold=2,
        ),
        _case(
            "empty_query",
            search_xy=[(0.0, 0.0), (1.0, 1.0)],
            query_xy=[],
            radius=1.0,
            threshold=1,
        ),
        _random_case(),
    ]


def _ids(count: int, *, offset: int) -> list[int]:
    return [offset + i for i in range(count)]


def _cpu_reference(case: dict[str, object]) -> dict[str, list[int]]:
    search_xy = np.asarray(case["search_xy"], dtype=np.float64)
    query_xy = np.asarray(case["query_xy"], dtype=np.float64)
    radius = float(case["radius"])
    threshold = int(case["threshold"])
    query_ids = _ids(len(query_xy), offset=1)
    if len(query_xy) == 0:
        return {"query_ids": [], "neighbor_counts": [], "threshold_flags": []}

    radius_sq = radius * radius
    counts: list[int] = []
    flags: list[int] = []
    for query in query_xy:
        delta = search_xy - query
        actual = int(np.count_nonzero(np.sum(delta * delta, axis=1) <= radius_sq + 1e-12))
        counts.append(min(actual, threshold) if threshold > 0 else actual)
        flags.append(1 if threshold > 0 and actual >= threshold else 0)
    return {
        "query_ids": query_ids,
        "neighbor_counts": counts,
        "threshold_flags": flags,
    }


def _cupy_columns(cp, ids: list[int], xy: list[tuple[float, float]]) -> dict[str, object]:
    arr = np.asarray(xy, dtype=np.float64).reshape((len(xy), 2))
    return {
        "ids": cp.asarray(ids, dtype=cp.uint32),
        "x": cp.asarray(arr[:, 0], dtype=cp.float64),
        "y": cp.asarray(arr[:, 1], dtype=cp.float64),
    }


def _empty_outputs(cp, count: int) -> dict[str, object]:
    return {
        "query_ids": cp.zeros((count,), dtype=cp.uint32),
        "neighbor_counts": cp.zeros((count,), dtype=cp.uint32),
        "threshold_flags": cp.zeros((count,), dtype=cp.uint32),
    }


def _to_lists(outputs: dict[str, object]) -> dict[str, list[int]]:
    return {name: [int(value) for value in column.get().tolist()] for name, column in outputs.items()}


def run_parity_matrix() -> dict[str, object]:
    import cupy as cp
    import rtdsl

    case_results = []
    for case in _cases():
        search_xy = list(case["search_xy"])
        query_xy = list(case["query_xy"])
        search = _cupy_columns(cp, _ids(len(search_xy), offset=10), search_xy)
        query = _cupy_columns(cp, _ids(len(query_xy), offset=1), query_xy)
        outputs = _empty_outputs(cp, len(query_xy))
        expected = _cpu_reference(case)
        stream = cp.cuda.Stream(non_blocking=True)
        with stream:
            result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
                query,
                search,
                radius=float(case["radius"]),
                threshold=int(case["threshold"]),
                partner="cupy",
                output_columns=outputs,
                stream=stream.ptr,
                return_metadata=True,
            )
        stream.synchronize()
        observed = _to_lists(outputs)
        passed = observed == expected
        if not passed:
            raise AssertionError(
                f"V4 M1 parity failed for {case['name']}: observed={observed!r} expected={expected!r}"
            )
        case_results.append(
            {
                "name": case["name"],
                "radius": float(case["radius"]),
                "threshold": int(case["threshold"]),
                "query_count": len(query_xy),
                "search_count": len(search_xy),
                "observed": observed,
                "expected": expected,
                "passed": True,
                "native_async_ready": bool(result["metadata"]["native_async_ready"]),
                "v4_true_zero_copy_claim_authorized": bool(
                    result["metadata"]["v4_true_zero_copy_claim_authorized"]
                ),
            }
        )

    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "case_count": len(case_results),
        "pass_count": sum(1 for row in case_results if row["passed"]),
        "cases": case_results,
        "claim_boundaries": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 M1 CuPy correctness parity matrix.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_parity_matrix()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
