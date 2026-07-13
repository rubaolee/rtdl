#!/usr/bin/env python3
"""Goal4954-D non-RayJoin grouped carrier proof.

This script intentionally imports no RayJoin paper-reproduction code. It proves
that the grouped columnar carrier and descriptor-pair consumer from Goal4954-C
can be understood and used as a generic spatial/dataflow representation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def make_synthetic_spatial_overlap_carrier():
    """Create a small non-RayJoin grouped spatial result.

    The scenario is deliberately generic:

    - input A contains feature/region labels 10 and 20;
    - input B contains feature/region labels 100, 200, and 300;
    - each group is a polyline/polygon-fragment-like list of points;
    - the consumer aggregates by descriptor pair.
    """

    groups = [
        # label_a, label_b, alt_label, source_side_id, source_element_id, points
        (10, 100, 1, 0, 5000, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]),
        (10, 100, 1, 0, 5001, [(1.0, 1.0), (2.0, 1.0)]),
        (10, 200, 2, 0, 5002, [(2.0, 1.0), (3.0, 1.5), (4.0, 1.5)]),
        (20, 200, 2, 1, 6000, [(0.0, 2.0), (1.0, 2.5)]),
        (20, 300, 3, 1, 6001, [(1.0, 2.5), (2.0, 3.0), (3.0, 3.5), (4.0, 4.0)]),
    ]

    group_offset = []
    group_length = []
    label_a = []
    label_b = []
    alt_label = []
    source_side_id = []
    source_element_id = []
    x = []
    y = []

    for la, lb, alt, side, element, points in groups:
        group_offset.append(len(x))
        group_length.append(len(points))
        label_a.append(la)
        label_b.append(lb)
        alt_label.append(alt)
        source_side_id.append(side)
        source_element_id.append(element)
        for px, py in points:
            x.append(px)
            y.append(py)

    return {
        "group_offset": np.asarray(group_offset, dtype=np.int64),
        "group_length": np.asarray(group_length, dtype=np.int64),
        "label_a": np.asarray(label_a, dtype=np.int64),
        "label_b": np.asarray(label_b, dtype=np.int64),
        "alt_label": np.asarray(alt_label, dtype=np.int64),
        "source_side_id": np.asarray(source_side_id, dtype=np.int32),
        "source_element_id": np.asarray(source_element_id, dtype=np.int64),
        "x": np.asarray(x, dtype=np.float64),
        "y": np.asarray(y, dtype=np.float64),
    }


def descriptor_pair_count_grouped(carrier):
    pairs = np.column_stack((carrier["label_a"], carrier["label_b"]))
    unique_pairs, inverse = np.unique(pairs, axis=0, return_inverse=True)
    group_counts = np.bincount(inverse)
    point_counts = np.bincount(inverse, weights=carrier["group_length"]).astype(np.int64, copy=False)
    order = np.lexsort((unique_pairs[:, 1], unique_pairs[:, 0]))
    return [
        {
            "label_a": int(unique_pairs[index, 0]),
            "label_b": int(unique_pairs[index, 1]),
            "group_count": int(group_counts[index]),
            "point_row_count": int(point_counts[index]),
        }
        for index in order
    ]


def main() -> int:
    carrier = make_synthetic_spatial_overlap_carrier()
    result = descriptor_pair_count_grouped(carrier)
    expected = [
        {"label_a": 10, "label_b": 100, "group_count": 2, "point_row_count": 5},
        {"label_a": 10, "label_b": 200, "group_count": 1, "point_row_count": 3},
        {"label_a": 20, "label_b": 200, "group_count": 1, "point_row_count": 2},
        {"label_a": 20, "label_b": 300, "group_count": 1, "point_row_count": 4},
    ]
    ok = result == expected
    payload = {
        "schema": "rtdl.internal.goal4954d.non_rayjoin_grouped_carrier_proof.v1",
        "rayjoin_imported": False,
        "cdb_required": False,
        "authorofficial_required": False,
        "paper_text_required": False,
        "carrier": {
            "group_count": int(carrier["group_offset"].size),
            "point_row_count": int(carrier["x"].size),
            "columns": sorted(carrier.keys()),
        },
        "consumer": "descriptor_pair_count_grouped",
        "result": result,
        "expected": expected,
        "pass": ok,
    }
    output = Path(__file__).with_name("goal4954d_non_rayjoin_grouped_carrier_proof.json")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
