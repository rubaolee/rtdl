#!/usr/bin/env python3
"""Goal4954-E numeric binary-route measurement.

This script measures Option B from Goal4954-D:

- paper sink keeps the exact rational route for byte-for-byte correctness;
- binary operator route may use numeric coordinates for database-style
  downstream consumers.

This is internal app-owned measurement code, not RTDL core/runtime code.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import goal4954c_grouped_carrier_measure as c  # noqa: E402

base = c.base


def intersection_rows_from_pairs_numeric(pairs, left, right, *, scale_bounds):
    pairs = np.asarray(pairs, dtype=np.uint32).reshape((-1, 2))
    left_index = pairs[:, 0].astype(np.int64, copy=False) - 1
    right_index = pairs[:, 1].astype(np.int64, copy=False) - 1

    lx0 = left.x0[left_index]
    ly0 = left.y0[left_index]
    lx1 = left.x1[left_index]
    ly1 = left.y1[left_index]
    rx0 = right.x0[right_index]
    ry0 = right.y0[right_index]
    rx1 = right.x1[right_index]
    ry1 = right.y1[right_index]

    ldx = lx1 - lx0
    ldy = ly1 - ly0
    rdx = rx1 - rx0
    rdy = ry1 - ry0
    denom = ldx * rdy - ldy * rdx
    qpx = rx0 - lx0
    qpy = ry0 - ly0
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (qpx * rdy - qpy * rdx) / denom
        world_x = lx0 + t * ldx
        world_y = ly0 + t * ldy

    fallback_x, fallback_y = base._overlap_midpoint_fallback(lx0, ly0, lx1, ly1, rx0, ry0, rx1, ry1)
    invalid = ~np.isfinite(world_x) | ~np.isfinite(world_y) | (np.abs(denom) <= 0.0)
    if np.any(invalid):
        world_x = world_x.copy()
        world_y = world_y.copy()
        world_x[invalid] = fallback_x[invalid]
        world_y[invalid] = fallback_y[invalid]

    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    scaled_x = base._scale_array(world_x, rx_scale, deltax)
    scaled_y = base._scale_array(world_y, ry_scale, deltay)

    rows = []
    for index in range(int(pairs.shape[0])):
        sx = int(scaled_x[index])
        sy = int(scaled_y[index])
        rows.append(
            base.OverlayIntersection(
                eid0=int(pairs[index, 0]) - 1,
                eid1=int(pairs[index, 1]) - 1,
                x=float(world_x[index]),
                y=float(world_y[index]),
                display_x=float(world_x[index]),
                display_y=float(world_y[index]),
                scaled_x=sx,
                scaled_y=sy,
                scaled_x_rational=Fraction(sx, 1),
                scaled_y_rational=Fraction(sy, 1),
            )
        )
    return rows


def sort_xsects_for_map_numeric(xsects, dataset, map_index, scale_bounds):
    edge_attr = "eid0" if map_index == 0 else "eid1"
    tie_attr = "eid1" if map_index == 0 else "eid0"
    grouped = {}
    for xsect in xsects:
        grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    sorted_rows = []
    for eid in sorted(grouped):
        start_sx = int(base._scale_array([dataset.x0[eid]], rx_scale, deltax)[0])
        start_sy = int(base._scale_array([dataset.y0[eid]], ry_scale, deltay)[0])

        def key(x):
            dx = int(x.scaled_x) - start_sx
            dy = int(x.scaled_y) - start_sy
            return (dx * dx + dy * dy, int(getattr(x, tie_attr)))

        group = grouped[eid]
        group.sort(key=key)
        sorted_rows.extend(group)
    return sorted_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--pair-name", default="unnamed_pair")
    parser.add_argument("--author-overlay-compute-sec", type=float, default=None)
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--swap-query-map-ids", action="store_true")
    args = parser.parse_args()

    old_reprojection = c.base.intersection_rows_from_pairs
    old_sort = c.base.sort_xsects_for_map
    c.base.intersection_rows_from_pairs = intersection_rows_from_pairs_numeric
    c.base.sort_xsects_for_map = sort_xsects_for_map_numeric
    try:
        summary = c.run_pipeline(args)
    finally:
        c.base.intersection_rows_from_pairs = old_reprojection
        c.base.sort_xsects_for_map = old_sort

    summary["schema"] = "rtdl.internal.goal4954e.numeric_binary_route_measure.v1"
    summary["route"] = "numeric_binary_route_public_lsi_pip_plus_grouped_carrier"
    summary["claim_boundary"]["numeric_binary_route"] = True
    summary["claim_boundary"]["paper_byte_equal_route"] = False
    summary["claim_boundary"]["paper_exact_sink_separate"] = True
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
