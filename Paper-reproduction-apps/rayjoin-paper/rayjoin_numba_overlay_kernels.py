#!/usr/bin/env python3
"""Numba partner kernels for RayJoin app-layer continuation.

This module is intentionally internal evidence code. It does not replace RTDL
LSI/PIP primitives and it does not import the bundled RayJoin overlay helper.

The kernels target the Python-side continuation shape exposed by the current
Section 5.7 public-primitives harness:

- sorted intersection rows -> midpoint query points;
- output-chain consecutive point dedupe;
- chain keep decisions from local/other face ids.

Each Numba path has a Python reference implementation and a small synthetic
parity harness.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

try:  # pragma: no cover - availability is environment-dependent.
    from numba import njit

    NUMBA_AVAILABLE = True
except Exception:  # pragma: no cover - exercised when Numba is absent.
    njit = None
    NUMBA_AVAILABLE = False


def _trunc_div2_py(value: int) -> int:
    if value >= 0:
        return value // 2
    return -((-value) // 2)


def midpoint_pairs_reference(
    edge_ids: np.ndarray,
    scaled_x: np.ndarray,
    scaled_y: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reference midpoint generation for sorted intersections.

    For each adjacent pair of intersections on the same edge, emit the
    author-compatible truncating midpoint in scaled coordinates and the owner
    row index of the left intersection.
    """

    edge_ids = np.asarray(edge_ids, dtype=np.int64)
    scaled_x = np.asarray(scaled_x, dtype=np.int64)
    scaled_y = np.asarray(scaled_y, dtype=np.int64)
    out_x: list[int] = []
    out_y: list[int] = []
    owners: list[int] = []
    for index in range(max(0, int(edge_ids.size) - 1)):
        if int(edge_ids[index]) == int(edge_ids[index + 1]):
            out_x.append(_trunc_div2_py(int(scaled_x[index]) + int(scaled_x[index + 1])))
            out_y.append(_trunc_div2_py(int(scaled_y[index]) + int(scaled_y[index + 1])))
            owners.append(index)
    return (
        np.asarray(out_x, dtype=np.int64),
        np.asarray(out_y, dtype=np.int64),
        np.asarray(owners, dtype=np.int64),
    )


def dedupe_consecutive_points_reference(
    x: np.ndarray,
    y: np.ndarray,
) -> np.ndarray:
    """Return a keep mask for exact consecutive point dedupe."""

    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    keep = np.zeros(x.shape, dtype=np.bool_)
    if x.size == 0:
        return keep
    keep[0] = True
    for index in range(1, int(x.size)):
        keep[index] = bool(x[index] != x[index - 1] or y[index] != y[index - 1])
    return keep


def chain_keep_reference(
    left_face_ids: np.ndarray,
    right_face_ids: np.ndarray,
    other_face_ids: np.ndarray,
) -> np.ndarray:
    """Return the RayJoin output-chain keep decision."""

    left = np.asarray(left_face_ids, dtype=np.int64)
    right = np.asarray(right_face_ids, dtype=np.int64)
    other = np.asarray(other_face_ids, dtype=np.int64)
    keep = np.zeros(left.shape, dtype=np.bool_)
    for index in range(int(left.size)):
        keep[index] = bool(left[index] * other[index] != 0 or right[index] * other[index] != 0)
    return keep


def chain_has_xsects_reference(
    chain_offsets: np.ndarray,
    chain_point_counts: np.ndarray,
    xsect_edge_ids: np.ndarray,
) -> np.ndarray:
    """Return whether each chain owns at least one intersected edge.

    The harness numbers edges globally in chain order. For a chain with point
    offset ``p`` and chain index ``c``, the first edge id is ``p - c`` because
    each previous chain contributes one fewer edge than point.
    """

    offsets = np.asarray(chain_offsets, dtype=np.int64)
    counts = np.asarray(chain_point_counts, dtype=np.int64)
    xsect_edges = np.sort(np.asarray(xsect_edge_ids, dtype=np.int64))
    has = np.zeros(offsets.shape, dtype=np.bool_)
    cursor = 0
    for chain_index in range(int(offsets.size)):
        edge_start = int(offsets[chain_index]) - chain_index
        edge_stop = edge_start + max(0, int(counts[chain_index]) - 1)
        while cursor < int(xsect_edges.size) and int(xsect_edges[cursor]) < edge_start:
            cursor += 1
        has[chain_index] = cursor < int(xsect_edges.size) and int(xsect_edges[cursor]) < edge_stop
    return has


def writer_skip_decision_reference(
    has_xsects: np.ndarray,
    terminal_keep: np.ndarray,
) -> np.ndarray:
    """Return chains that are safe to skip before the Python writer loop."""

    has = np.asarray(has_xsects, dtype=np.bool_)
    keep = np.asarray(terminal_keep, dtype=np.bool_)
    return np.logical_and(~has, ~keep)


if NUMBA_AVAILABLE:

    @njit(cache=True)
    def _trunc_div2_numba(value: int) -> int:
        if value >= 0:
            return value // 2
        return -((-value) // 2)

    @njit(cache=True)
    def _midpoint_pairs_numba(edge_ids, scaled_x, scaled_y, out_x, out_y, owners) -> int:
        count = 0
        n = edge_ids.shape[0]
        for index in range(n - 1):
            if edge_ids[index] == edge_ids[index + 1]:
                out_x[count] = _trunc_div2_numba(int(scaled_x[index]) + int(scaled_x[index + 1]))
                out_y[count] = _trunc_div2_numba(int(scaled_y[index]) + int(scaled_y[index + 1]))
                owners[count] = index
                count += 1
        return count

    @njit(cache=True)
    def _dedupe_consecutive_points_numba(x, y, keep) -> None:
        n = x.shape[0]
        if n == 0:
            return
        keep[0] = True
        for index in range(1, n):
            keep[index] = x[index] != x[index - 1] or y[index] != y[index - 1]

    @njit(cache=True)
    def _chain_keep_numba(left_face_ids, right_face_ids, other_face_ids, keep) -> None:
        n = left_face_ids.shape[0]
        for index in range(n):
            keep[index] = (
                left_face_ids[index] * other_face_ids[index] != 0
                or right_face_ids[index] * other_face_ids[index] != 0
            )

    @njit(cache=True)
    def _chain_has_xsects_numba(chain_offsets, chain_point_counts, xsect_edge_ids, has) -> None:
        cursor = 0
        xsect_count = xsect_edge_ids.shape[0]
        for chain_index in range(chain_offsets.shape[0]):
            edge_start = int(chain_offsets[chain_index]) - chain_index
            edge_stop = edge_start + max(0, int(chain_point_counts[chain_index]) - 1)
            while cursor < xsect_count and int(xsect_edge_ids[cursor]) < edge_start:
                cursor += 1
            has[chain_index] = cursor < xsect_count and int(xsect_edge_ids[cursor]) < edge_stop

    @njit(cache=True)
    def _writer_skip_decision_numba(has_xsects, terminal_keep, skip) -> None:
        for index in range(has_xsects.shape[0]):
            skip[index] = (not has_xsects[index]) and (not terminal_keep[index])


def midpoint_pairs_numba(
    edge_ids: np.ndarray,
    scaled_x: np.ndarray,
    scaled_y: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not NUMBA_AVAILABLE:
        return midpoint_pairs_reference(edge_ids, scaled_x, scaled_y)
    edge_ids = np.asarray(edge_ids, dtype=np.int64)
    scaled_x = np.asarray(scaled_x, dtype=np.int64)
    scaled_y = np.asarray(scaled_y, dtype=np.int64)
    capacity = max(0, int(edge_ids.size) - 1)
    out_x = np.empty(capacity, dtype=np.int64)
    out_y = np.empty(capacity, dtype=np.int64)
    owners = np.empty(capacity, dtype=np.int64)
    count = _midpoint_pairs_numba(edge_ids, scaled_x, scaled_y, out_x, out_y, owners)
    return out_x[:count].copy(), out_y[:count].copy(), owners[:count].copy()


def dedupe_consecutive_points_numba(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    if not NUMBA_AVAILABLE:
        return dedupe_consecutive_points_reference(x, y)
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    keep = np.zeros(x.shape, dtype=np.bool_)
    _dedupe_consecutive_points_numba(x, y, keep)
    return keep


def chain_keep_numba(
    left_face_ids: np.ndarray,
    right_face_ids: np.ndarray,
    other_face_ids: np.ndarray,
) -> np.ndarray:
    if not NUMBA_AVAILABLE:
        return chain_keep_reference(left_face_ids, right_face_ids, other_face_ids)
    left = np.asarray(left_face_ids, dtype=np.int64)
    right = np.asarray(right_face_ids, dtype=np.int64)
    other = np.asarray(other_face_ids, dtype=np.int64)
    keep = np.zeros(left.shape, dtype=np.bool_)
    _chain_keep_numba(left, right, other, keep)
    return keep


def chain_has_xsects_numba(
    chain_offsets: np.ndarray,
    chain_point_counts: np.ndarray,
    xsect_edge_ids: np.ndarray,
) -> np.ndarray:
    if not NUMBA_AVAILABLE:
        return chain_has_xsects_reference(chain_offsets, chain_point_counts, xsect_edge_ids)
    offsets = np.asarray(chain_offsets, dtype=np.int64)
    counts = np.asarray(chain_point_counts, dtype=np.int64)
    xsect_edges = np.sort(np.asarray(xsect_edge_ids, dtype=np.int64))
    has = np.zeros(offsets.shape, dtype=np.bool_)
    _chain_has_xsects_numba(offsets, counts, xsect_edges, has)
    return has


def writer_skip_decision_numba(
    has_xsects: np.ndarray,
    terminal_keep: np.ndarray,
) -> np.ndarray:
    if not NUMBA_AVAILABLE:
        return writer_skip_decision_reference(has_xsects, terminal_keep)
    has = np.asarray(has_xsects, dtype=np.bool_)
    keep = np.asarray(terminal_keep, dtype=np.bool_)
    skip = np.zeros(has.shape, dtype=np.bool_)
    _writer_skip_decision_numba(has, keep, skip)
    return skip


def _timed(func, *args):
    start = time.perf_counter()
    value = func(*args)
    return value, time.perf_counter() - start


def run_synthetic_parity() -> dict[str, Any]:
    edge_ids = np.array([2, 2, 2, 5, 8, 8, 9, 9, 9, 9], dtype=np.int64)
    scaled_x = np.array([10, 11, -13, 100, -7, -8, 21, 22, 23, -24], dtype=np.int64)
    scaled_y = np.array([0, -1, -2, 50, 7, -8, -31, -32, 33, 34], dtype=np.int64)
    ref_mid, ref_mid_time = _timed(midpoint_pairs_reference, edge_ids, scaled_x, scaled_y)
    got_mid, got_mid_time = _timed(midpoint_pairs_numba, edge_ids, scaled_x, scaled_y)

    point_x = np.array([1.0, 1.0, 2.5, 2.5, 3.0, 3.0, 3.0, -0.0], dtype=np.float64)
    point_y = np.array([2.0, 2.0, 9.0, 10.0, 4.0, 4.0, 5.0, -0.0], dtype=np.float64)
    ref_dedupe, ref_dedupe_time = _timed(dedupe_consecutive_points_reference, point_x, point_y)
    got_dedupe, got_dedupe_time = _timed(dedupe_consecutive_points_numba, point_x, point_y)

    left_faces = np.array([0, 3, 0, 4, 5, 0], dtype=np.int64)
    right_faces = np.array([0, 0, 7, 0, 0, 2], dtype=np.int64)
    other_faces = np.array([0, 9, 0, 11, 12, 13], dtype=np.int64)
    ref_keep, ref_keep_time = _timed(chain_keep_reference, left_faces, right_faces, other_faces)
    got_keep, got_keep_time = _timed(chain_keep_numba, left_faces, right_faces, other_faces)

    chain_offsets = np.array([0, 3, 7, 8], dtype=np.int64)
    chain_counts = np.array([3, 4, 1, 5], dtype=np.int64)
    xsect_edges = np.array([8, 1, 5], dtype=np.int64)
    ref_has_xsects, ref_has_xsects_time = _timed(
        chain_has_xsects_reference,
        chain_offsets,
        chain_counts,
        xsect_edges,
    )
    got_has_xsects, got_has_xsects_time = _timed(
        chain_has_xsects_numba,
        chain_offsets,
        chain_counts,
        xsect_edges,
    )
    terminal_keep_cases = np.array([False, False, True, False], dtype=np.bool_)
    ref_skip, ref_skip_time = _timed(
        writer_skip_decision_reference,
        ref_has_xsects,
        terminal_keep_cases,
    )
    got_skip, got_skip_time = _timed(
        writer_skip_decision_numba,
        got_has_xsects,
        terminal_keep_cases,
    )

    return {
        "schema": "rtdl.paper_reproduction.rayjoin.numba_overlay_kernel_synthetic_parity.v1",
        "numba_available": NUMBA_AVAILABLE,
        "midpoint_pairs_match": all(np.array_equal(a, b) for a, b in zip(ref_mid, got_mid)),
        "midpoint_pairs_reference": [a.tolist() for a in ref_mid],
        "midpoint_pairs_numba": [a.tolist() for a in got_mid],
        "dedupe_mask_match": bool(np.array_equal(ref_dedupe, got_dedupe)),
        "dedupe_mask_reference": ref_dedupe.astype(np.int8).tolist(),
        "dedupe_mask_numba": got_dedupe.astype(np.int8).tolist(),
        "chain_keep_match": bool(np.array_equal(ref_keep, got_keep)),
        "chain_keep_reference": ref_keep.astype(np.int8).tolist(),
        "chain_keep_numba": got_keep.astype(np.int8).tolist(),
        "chain_has_xsects_match": bool(np.array_equal(ref_has_xsects, got_has_xsects)),
        "chain_has_xsects_reference": ref_has_xsects.astype(np.int8).tolist(),
        "chain_has_xsects_numba": got_has_xsects.astype(np.int8).tolist(),
        "writer_skip_decision_match": bool(np.array_equal(ref_skip, got_skip)),
        "writer_skip_decision_reference": ref_skip.astype(np.int8).tolist(),
        "writer_skip_decision_numba": got_skip.astype(np.int8).tolist(),
        "writer_skip_decision_cases": {
            "case0_has_xsect_do_not_skip": bool(not ref_skip[0]),
            "case1_no_xsect_terminal_drop_skip": bool(ref_skip[1]),
            "case2_no_xsect_terminal_keep_do_not_skip": bool(not ref_skip[2]),
            "case3_has_xsect_do_not_skip": bool(not ref_skip[3]),
        },
        "timings_sec": {
            "midpoint_reference": ref_mid_time,
            "midpoint_numba_or_fallback": got_mid_time,
            "dedupe_reference": ref_dedupe_time,
            "dedupe_numba_or_fallback": got_dedupe_time,
            "chain_keep_reference": ref_keep_time,
            "chain_keep_numba_or_fallback": got_keep_time,
            "chain_has_xsects_reference": ref_has_xsects_time,
            "chain_has_xsects_numba_or_fallback": got_has_xsects_time,
            "writer_skip_decision_reference": ref_skip_time,
            "writer_skip_decision_numba_or_fallback": got_skip_time,
        },
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default="rayjoin_numba_synthetic_parity_summary.json")
    args = parser.parse_args()
    summary = run_synthetic_parity()
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
