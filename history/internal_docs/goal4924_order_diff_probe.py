#!/usr/bin/env python3
"""Compare Goal4924 reprojection/sort against the proven Goal4880 route."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


THIS_DIR = Path(__file__).resolve().parent
GOAL4880 = THIS_DIR / "goal4880_section57_public_primitives_overlay_harness.py"
GOAL4924 = THIS_DIR / "goal4924_columnar_reprojection_sort_probe.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load(GOAL4880, "goal4880_for_goal4924_diff")
probe = _load(GOAL4924, "goal4924_for_diff")


def _row_sig(row):
    return (
        int(row.eid0),
        int(row.eid1),
        int(row.scaled_x),
        int(row.scaled_y),
        float(row.display_x),
        float(row.display_y),
    )


def _order_sig(row, map_index: int):
    return int(row.eid0 if map_index == 0 else row.eid1), int(row.eid1 if map_index == 0 else row.eid0), int(row.scaled_x), int(row.scaled_y)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--cache-dir", default=None)
    args = parser.parse_args()

    import os

    if args.cache_dir:
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))

    left = base.load_dataset_arrays(Path(args.left))
    right = base.load_dataset_arrays(Path(args.right))
    bounds = base.shared_bounds(left, right)
    with base.prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            row_view = query.run_pair_id_rows()
            try:
                columns = row_view.to_numpy_columns(copy=True)
                pairs = np.column_stack(
                    (
                        columns["left_id"].astype(np.uint32, copy=False),
                        columns["right_id"].astype(np.uint32, copy=False),
                    )
                )
            finally:
                row_view.close()

    original = base.intersection_rows_from_pairs(pairs, left, right, scale_bounds=bounds)
    candidate = probe.intersection_rows_from_pairs_no_fraction(pairs, left, right, scale_bounds=bounds)

    row_mismatches = []
    for index, (old, new) in enumerate(zip(original, candidate)):
        if _row_sig(old) != _row_sig(new):
            row_mismatches.append({"index": index, "old": _row_sig(old), "new": _row_sig(new)})
            if len(row_mismatches) >= 5:
                break

    sort_results = {}
    old_sort_func = base.sort_xsects_for_map
    for mode in ("scaled_int", "exact_cmp"):
        os.environ["GOAL4924_SORT_MODE"] = mode
        mode_result = {}
        for map_index, dataset in ((0, left), (1, right)):
            old_sorted = old_sort_func(list(original), dataset, map_index, bounds)
            new_sorted = probe.sort_xsects_for_map_goal4924(list(candidate), dataset, map_index, bounds)
            first_mismatches = []
            for index, (old, new) in enumerate(zip(old_sorted, new_sorted)):
                if _order_sig(old, map_index) != _order_sig(new, map_index):
                    first_mismatches.append({"index": index, "old": _order_sig(old, map_index), "new": _order_sig(new, map_index)})
                    if len(first_mismatches) >= 5:
                        break
            mode_result[f"map{map_index}"] = {
                "old_count": len(old_sorted),
                "new_count": len(new_sorted),
                "first_mismatches": first_mismatches,
                "order_equal_prefix_checked": not first_mismatches,
            }
        sort_results[mode] = mode_result

    Path(args.summary).write_text(
        json.dumps(
            {
                "pairs": int(pairs.shape[0]),
                "row_mismatches": row_mismatches,
                "row_prefix_equal_checked": not row_mismatches,
                "sort_results": sort_results,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
