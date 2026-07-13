#!/usr/bin/env python3
"""Goal4955 projected descriptor pipeline measurement.

This internal measurement script continues Goal4954-E, but applies a narrower
database-style optimization:

    if the downstream consumer only needs descriptor-pair counts, do not
    materialize point-geometry payload columns.

That is projection pushdown / late materialization, not a RayJoin-specific RTDL
core primitive.  The exact paper text route remains separate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import goal4954c_grouped_carrier_measure as c  # noqa: E402
import goal4954e_numeric_binary_route_measure as e  # noqa: E402

base = c.base


try:  # pragma: no cover - availability depends on the runtime image.
    from numba import njit  # type: ignore

    NUMBA_AVAILABLE = True
except Exception:  # pragma: no cover
    njit = None
    NUMBA_AVAILABLE = False


if NUMBA_AVAILABLE:

    @njit(cache=True)
    def _aggregate_sorted_pairs_numba(label_a, label_b, group_length, out_a, out_b, out_groups, out_points):
        if label_a.shape[0] == 0:
            return 0
        out_count = 0
        current_a = label_a[0]
        current_b = label_b[0]
        current_groups = 0
        current_points = 0
        for index in range(label_a.shape[0]):
            a = label_a[index]
            b = label_b[index]
            if a != current_a or b != current_b:
                out_a[out_count] = current_a
                out_b[out_count] = current_b
                out_groups[out_count] = current_groups
                out_points[out_count] = current_points
                out_count += 1
                current_a = a
                current_b = b
                current_groups = 0
                current_points = 0
            current_groups += 1
            current_points += group_length[index]
        out_a[out_count] = current_a
        out_b[out_count] = current_b
        out_groups[out_count] = current_groups
        out_points[out_count] = current_points
        return out_count + 1


def _dedupe_consecutive_point_count(points: list[tuple[float, float]]) -> int:
    """Return the exact count produced by ``dedupe_point_pairs`` without payload."""

    if not points:
        return 0
    count = 1
    previous = points[0]
    for point in points[1:]:
        if point != previous:
            count += 1
            previous = point
    return count


def build_projected_descriptor_carrier(datasets, xsects_sorted, point_faces):
    """Build only the descriptor columns required by the current downstream.

    Compared with Goal4954-C, this intentionally does not allocate or fill
    ``x``/``y`` payload columns.  It still walks the same chain/event structure
    and computes the same deduped group lengths, so the descriptor-pair consumer
    sees the same rows it needs.
    """

    group_offset = []
    group_length = []
    label_a = []
    label_b = []
    skipped_group_count = 0
    projected_point_payload_rows = 0

    def flush(display_points, left_label, right_label, other_label, side_id, element_id):
        nonlocal skipped_group_count, projected_point_payload_rows
        if not display_points:
            return
        keep = int(left_label) * int(other_label) != 0 or int(right_label) * int(other_label) != 0
        if not keep:
            skipped_group_count += 1
            display_points.clear()
            return

        length = _dedupe_consecutive_point_count(display_points)
        group_offset.append(projected_point_payload_rows)
        group_length.append(length)
        label_a.append(int(left_label))
        label_b.append(int(other_label))
        projected_point_payload_rows += length
        display_points.clear()

    for side_id, dataset in enumerate(datasets):
        edge_attr = "eid0" if side_id == 0 else "eid1"
        grouped = {}
        for xsect in xsects_sorted[side_id]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)

        edge_id = 0
        for chain_index in range(dataset.chain_count):
            point_offset = int(dataset.chain_offsets[chain_index])
            point_count = int(dataset.chain_point_counts[chain_index])
            display_points: list[tuple[float, float]] = []
            left_label = int(dataset.chain_left_faces[chain_index])
            right_label = int(dataset.chain_right_faces[chain_index])
            other_label = 0

            for local_point_index in range(point_count):
                point_index = point_offset + local_point_index
                other_label = int(point_faces[side_id][point_index])
                display_points.append((float(dataset.point_x[point_index]), float(dataset.point_y[point_index])))

                if local_point_index == point_count - 1:
                    continue

                xsects = grouped.get(edge_id)
                if xsects:
                    first_point = base.xsect_output_point(xsects[0])
                    display_points.append(first_point)
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        flush(
                            display_points,
                            left_label,
                            right_label,
                            other_label,
                            side_id,
                            edge_id,
                        )
                        other_label = base.midpoint_face_for_map(xsect, side_id)
                        display_points.append(base.xsect_output_point(xsect))
                        display_points.append(base.xsect_output_point(next_xsect))
                    flush(
                        display_points,
                        left_label,
                        right_label,
                        other_label,
                        side_id,
                        edge_id,
                    )
                    display_points.append(base.xsect_output_point(xsects[-1]))
                edge_id += 1

            flush(
                display_points,
                left_label,
                right_label,
                other_label,
                side_id,
                max(edge_id - 1, 0),
            )

    carrier = {
        "group_offset": np.asarray(group_offset, dtype=np.int64),
        "group_length": np.asarray(group_length, dtype=np.int64),
        "label_a": np.asarray(label_a, dtype=np.int64),
        "label_b": np.asarray(label_b, dtype=np.int64),
    }
    stats = {
        "schema": "rtdl.internal.goal4955.projected_descriptor_carrier.v1",
        "group_count": int(carrier["group_offset"].size),
        "point_row_count": int(carrier["group_length"].sum()),
        "skipped_group_count": int(skipped_group_count),
        "geometry_payload_columns_materialized": False,
        "projected_out_columns": ("x", "y", "alt_label", "source_side_id", "source_element_id"),
        "projection_pushdown": True,
    }
    return carrier, stats


def descriptor_pair_count_projected(carrier):
    if carrier["label_a"].size == 0:
        return {
            "pair_count": 0,
            "total_groups": 0,
            "total_point_rows": 0,
            "top_pairs_by_point_rows": [],
            "partner": "numba" if NUMBA_AVAILABLE else "numpy_reference",
        }

    label_a = np.asarray(carrier["label_a"], dtype=np.int64)
    label_b = np.asarray(carrier["label_b"], dtype=np.int64)
    lengths = np.asarray(carrier["group_length"], dtype=np.int64)
    order = np.lexsort((label_b, label_a))
    sorted_a = label_a[order]
    sorted_b = label_b[order]
    sorted_lengths = lengths[order]

    if NUMBA_AVAILABLE:
        out_a = np.empty(sorted_a.shape[0], dtype=np.int64)
        out_b = np.empty(sorted_b.shape[0], dtype=np.int64)
        out_groups = np.empty(sorted_a.shape[0], dtype=np.int64)
        out_points = np.empty(sorted_a.shape[0], dtype=np.int64)
        count = _aggregate_sorted_pairs_numba(sorted_a, sorted_b, sorted_lengths, out_a, out_b, out_groups, out_points)
        unique_pairs = np.column_stack((out_a[:count], out_b[:count]))
        group_counts = out_groups[:count]
        point_counts = out_points[:count]
        partner = "numba_sorted_pair_scan"
    else:
        unique_pairs, inverse = np.unique(np.column_stack((label_a, label_b)), axis=0, return_inverse=True)
        group_counts = np.bincount(inverse)
        point_counts = np.bincount(inverse, weights=lengths).astype(np.int64, copy=False)
        partner = "numpy_reference"

    top_order = np.argsort(point_counts)[::-1]
    top = [
        {
            "label_a": int(unique_pairs[index, 0]),
            "label_b": int(unique_pairs[index, 1]),
            "group_count": int(group_counts[index]),
            "point_row_count": int(point_counts[index]),
        }
        for index in top_order[:10]
    ]
    return {
        "pair_count": int(unique_pairs.shape[0]),
        "total_groups": int(label_a.size),
        "total_point_rows": int(lengths.sum()),
        "top_pairs_by_point_rows": top,
        "partner": partner,
        "numba_available": bool(NUMBA_AVAILABLE),
        "numba_execution_mode": "cpu_njit" if NUMBA_AVAILABLE else "not_used",
        "cuda_device_resident_continuation": False,
    }


def _warm_numba() -> None:
    if not NUMBA_AVAILABLE:
        return
    carrier = {
        "label_a": np.asarray([1, 1, 2], dtype=np.int64),
        "label_b": np.asarray([10, 10, 20], dtype=np.int64),
        "group_length": np.asarray([2, 3, 4], dtype=np.int64),
    }
    descriptor_pair_count_projected(carrier)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--pair-name", default="unnamed_pair")
    parser.add_argument("--author-overlay-compute-sec", type=float, default=None)
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--swap-query-map-ids", action="store_true")
    parser.add_argument("--no-numba-warmup", action="store_true")
    args = parser.parse_args()

    if not args.no_numba_warmup:
        _warm_numba()

    old_reprojection = c.base.intersection_rows_from_pairs
    old_sort = c.base.sort_xsects_for_map
    old_builder = c.build_grouped_columnar_carrier
    old_consumer = c.descriptor_pair_count_grouped
    c.base.intersection_rows_from_pairs = e.intersection_rows_from_pairs_numeric
    c.base.sort_xsects_for_map = e.sort_xsects_for_map_numeric
    c.build_grouped_columnar_carrier = build_projected_descriptor_carrier
    c.descriptor_pair_count_grouped = descriptor_pair_count_projected
    try:
        summary = c.run_pipeline(args)
    finally:
        c.base.intersection_rows_from_pairs = old_reprojection
        c.base.sort_xsects_for_map = old_sort
        c.build_grouped_columnar_carrier = old_builder
        c.descriptor_pair_count_grouped = old_consumer

    summary["schema"] = "rtdl.internal.goal4955.projected_descriptor_pipeline_measure.v1"
    summary["route"] = "projected_binary_descriptor_route_public_lsi_pip_numba_consumer"
    summary["claim_boundary"]["numeric_binary_route"] = True
    summary["claim_boundary"]["projection_pushdown"] = True
    summary["claim_boundary"]["geometry_payload_materialized"] = False
    summary["claim_boundary"]["paper_byte_equal_route"] = False
    summary["claim_boundary"]["paper_exact_sink_separate"] = True
    summary["claim_boundary"]["layer4_fusion"] = False
    summary["claim_boundary"]["rtdl_core_change"] = False
    summary["claim_boundary"]["rayjoin_specific_core_primitive"] = False
    summary["numba_partner"] = {
        "available": bool(NUMBA_AVAILABLE),
        "used_for_downstream_consumer": bool(NUMBA_AVAILABLE),
        "execution_mode": "cpu_njit_sorted_pair_scan" if NUMBA_AVAILABLE else "not_used",
        "cuda_device_resident_continuation": False,
        "forced_on_string_or_object_work": False,
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
