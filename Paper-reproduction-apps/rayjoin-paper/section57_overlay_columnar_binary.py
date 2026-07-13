#!/usr/bin/env python3
"""Writer-free Section 5.7 columnar binary route.

This app route keeps RTDL core generic and RayJoin as an app.  It is the
writer-free numeric/binary counterpart to ``section57_overlay.py``:

    LSI pair ids -> columnar numeric xsect arrays -> NumPy sort/group metadata

instead of:

    LSI pair ids -> Python OverlayIntersection objects -> Python object sort

The exact paper text route remains separate.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path

import numpy as np


THIS_DIR = Path(__file__).resolve().parent
REPO = THIS_DIR.parents[1]
SRC_DIR = REPO / "src"
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(SRC_DIR))

import section57_overlay as base  # noqa: E402
from rtdsl import device_column_buffer  # noqa: E402
from rtdsl import device_column_row_buffer_from_native_pair_columns  # noqa: E402
from rtdsl import device_column_row_buffer_from_point_location_id_columns  # noqa: E402
from rtdsl import device_order_by  # noqa: E402
from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points_fast_host  # noqa: E402


GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS = (
    "chain_count",
    "chain_points_scanned",
    "edge_slots_scanned",
    "intersection_run_count",
    "intersection_row_count",
    "intersection_display_point_appends",
    "dedupe_append_calls",
    "split_flush_count",
    "chain_final_flush_count",
    "kept_group_count",
    "skipped_group_count",
    "emitted_point_row_count",
    "sorted_intersection_order_count",
    "run_start_count",
)


DEVICE_QUERY_POINT_DTYPE = np.dtype(
    [
        ("x", np.float32),
        ("y", np.float32),
        ("id", np.uint32),
        ("has_scaled", np.uint32),
        ("sx", np.int64),
        ("sy", np.int64),
    ],
    align=False,
)

if (
    DEVICE_QUERY_POINT_DTYPE.itemsize != 32
    or DEVICE_QUERY_POINT_DTYPE.fields["x"][1] != 0
    or DEVICE_QUERY_POINT_DTYPE.fields["y"][1] != 4
    or DEVICE_QUERY_POINT_DTYPE.fields["id"][1] != 8
    or DEVICE_QUERY_POINT_DTYPE.fields["has_scaled"][1] != 12
    or DEVICE_QUERY_POINT_DTYPE.fields["sx"][1] != 16
    or DEVICE_QUERY_POINT_DTYPE.fields["sy"][1] != 24
):
    raise RuntimeError("DEVICE_QUERY_POINT_DTYPE does not match the native device query point ABI")


try:  # pragma: no cover - availability depends on runtime image.
    from numba import njit  # type: ignore
    from numba import cuda  # type: ignore

    NUMBA_AVAILABLE = True
except Exception:  # pragma: no cover
    njit = None
    cuda = None
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


    @njit(cache=True)
    def _append_dedup_len(x, y, current_len, has_previous, previous_x, previous_y):
        if (not has_previous) or x != previous_x or y != previous_y:
            return current_len + 1, True, x, y
        return current_len, has_previous, previous_x, previous_y


    @njit(cache=True)
    def _build_projected_descriptor_side_numba(
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        order,
        run_start,
        run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        out_group_length,
        out_label_a,
        out_label_b,
        out_work_metrics,
    ):
        out_count = 0
        skipped_group_count = 0
        point_row_count = 0
        edge_id = 0
        chain_points_scanned = 0
        edge_slots_scanned = 0
        intersection_run_count = 0
        intersection_row_count = 0
        intersection_display_point_appends = 0
        dedupe_append_calls = 0
        split_flush_count = 0
        chain_final_flush_count = 0
        for chain_index in range(chain_offsets.shape[0]):
            point_offset = int(chain_offsets[chain_index])
            point_count = int(chain_point_counts[chain_index])
            chain_points_scanned += point_count
            if point_count > 0:
                edge_slots_scanned += point_count - 1
            left_label = int(chain_left_faces[chain_index])
            right_label = int(chain_right_faces[chain_index])
            other_label = 0
            current_len = 0
            has_previous = False
            previous_x = 0.0
            previous_y = 0.0

            for local_point_index in range(point_count):
                point_index = point_offset + local_point_index
                other_label = int(point_faces[point_index])
                dedupe_append_calls += 1
                current_len, has_previous, previous_x, previous_y = _append_dedup_len(
                    float(point_x[point_index]),
                    float(point_y[point_index]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )

                if local_point_index == point_count - 1:
                    continue

                start = int(run_start[edge_id]) if edge_id < run_start.shape[0] else -1
                end = int(run_end[edge_id]) if edge_id < run_end.shape[0] else -1
                if start >= 0 and end > start:
                    run_size = end - start
                    intersection_run_count += 1
                    intersection_row_count += run_size
                    first = int(order[start])
                    dedupe_append_calls += 1
                    intersection_display_point_appends += 1
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len(
                        float(display_x[first]),
                        float(display_y[first]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                    for sorted_pos in range(start, end - 1):
                        xsect_index = int(order[sorted_pos])
                        next_index = int(order[sorted_pos + 1])
                        if current_len > 0:
                            split_flush_count += 1
                            keep = left_label * other_label != 0 or right_label * other_label != 0
                            if keep:
                                out_group_length[out_count] = current_len
                                out_label_a[out_count] = left_label
                                out_label_b[out_count] = other_label
                                point_row_count += current_len
                                out_count += 1
                            else:
                                skipped_group_count += 1
                            current_len = 0
                            has_previous = False
                            previous_x = 0.0
                            previous_y = 0.0
                        other_label = int(midpoint_faces[xsect_index])
                        dedupe_append_calls += 1
                        intersection_display_point_appends += 1
                        current_len, has_previous, previous_x, previous_y = _append_dedup_len(
                            float(display_x[xsect_index]),
                            float(display_y[xsect_index]),
                            current_len,
                            has_previous,
                            previous_x,
                            previous_y,
                        )
                        dedupe_append_calls += 1
                        intersection_display_point_appends += 1
                        current_len, has_previous, previous_x, previous_y = _append_dedup_len(
                            float(display_x[next_index]),
                            float(display_y[next_index]),
                            current_len,
                            has_previous,
                            previous_x,
                            previous_y,
                        )
                    if current_len > 0:
                        split_flush_count += 1
                        keep = left_label * other_label != 0 or right_label * other_label != 0
                        if keep:
                            out_group_length[out_count] = current_len
                            out_label_a[out_count] = left_label
                            out_label_b[out_count] = other_label
                            point_row_count += current_len
                            out_count += 1
                        else:
                            skipped_group_count += 1
                        current_len = 0
                        has_previous = False
                        previous_x = 0.0
                        previous_y = 0.0
                    last = int(order[end - 1])
                    dedupe_append_calls += 1
                    intersection_display_point_appends += 1
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len(
                        float(display_x[last]),
                        float(display_y[last]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                edge_id += 1

            if current_len > 0:
                chain_final_flush_count += 1
                keep = left_label * other_label != 0 or right_label * other_label != 0
                if keep:
                    out_group_length[out_count] = current_len
                    out_label_a[out_count] = left_label
                    out_label_b[out_count] = other_label
                    point_row_count += current_len
                    out_count += 1
                else:
                    skipped_group_count += 1

        out_work_metrics[0] = chain_offsets.shape[0]
        out_work_metrics[1] = chain_points_scanned
        out_work_metrics[2] = edge_slots_scanned
        out_work_metrics[3] = intersection_run_count
        out_work_metrics[4] = intersection_row_count
        out_work_metrics[5] = intersection_display_point_appends
        out_work_metrics[6] = dedupe_append_calls
        out_work_metrics[7] = split_flush_count
        out_work_metrics[8] = chain_final_flush_count
        out_work_metrics[9] = out_count
        out_work_metrics[10] = skipped_group_count
        out_work_metrics[11] = point_row_count
        out_work_metrics[12] = order.shape[0]
        out_work_metrics[13] = run_start.shape[0]
        return out_count, skipped_group_count, point_row_count


if NUMBA_AVAILABLE:

    @cuda.jit
    def _numeric_xsect_columns_kernel(
        pair_left,
        pair_right,
        left_x0,
        left_y0,
        left_x1,
        left_y1,
        right_x0,
        right_y0,
        right_x1,
        right_y1,
        rx_scale,
        ry_scale,
        deltax,
        deltay,
        out_eid0,
        out_eid1,
        out_display_x,
        out_display_y,
        out_scaled_x,
        out_scaled_y,
    ):
        index = cuda.grid(1)
        if index >= pair_left.shape[0]:
            return

        left_index = int(pair_left[index]) - 1
        right_index = int(pair_right[index]) - 1
        lx0 = left_x0[left_index]
        ly0 = left_y0[left_index]
        lx1 = left_x1[left_index]
        ly1 = left_y1[left_index]
        rx0 = right_x0[right_index]
        ry0 = right_y0[right_index]
        rx1 = right_x1[right_index]
        ry1 = right_y1[right_index]

        ldx = lx1 - lx0
        ldy = ly1 - ly0
        rdx = rx1 - rx0
        rdy = ry1 - ry0
        denom = ldx * rdy - ldy * rdx
        qpx = rx0 - lx0
        qpy = ry0 - ly0
        world_x = 0.0
        world_y = 0.0
        if denom != 0.0:
            t = (qpx * rdy - qpy * rdx) / denom
            world_x = lx0 + t * ldx
            world_y = ly0 + t * ldy

        if denom == 0.0 or not math.isfinite(world_x) or not math.isfinite(world_y):
            if abs(ldx) >= abs(ldy) and ldx != 0.0:
                left_lo = lx0 if lx0 <= lx1 else lx1
                left_hi = lx1 if lx0 <= lx1 else lx0
                right_lo = rx0 if rx0 <= rx1 else rx1
                right_hi = rx1 if rx0 <= rx1 else rx0
                lo = left_lo if left_lo >= right_lo else right_lo
                hi = left_hi if left_hi <= right_hi else right_hi
                if lo <= hi:
                    world_x = 0.5 * (lo + hi)
                else:
                    world_x = 0.25 * (lx0 + lx1 + rx0 + rx1)
                world_y = ly0 + ((world_x - lx0) / ldx) * ldy
            elif ldy != 0.0:
                left_lo = ly0 if ly0 <= ly1 else ly1
                left_hi = ly1 if ly0 <= ly1 else ly0
                right_lo = ry0 if ry0 <= ry1 else ry1
                right_hi = ry1 if ry0 <= ry1 else ry0
                lo = left_lo if left_lo >= right_lo else right_lo
                hi = left_hi if left_hi <= right_hi else right_hi
                if lo <= hi:
                    world_y = 0.5 * (lo + hi)
                else:
                    world_y = 0.25 * (ly0 + ly1 + ry0 + ry1)
                world_x = lx0 + ((world_y - ly0) / ldy) * ldx
            else:
                world_x = lx0
                world_y = ly0

        out_eid0[index] = left_index
        out_eid1[index] = right_index
        out_display_x[index] = world_x
        out_display_y[index] = world_y
        out_scaled_x[index] = int(world_x * rx_scale + deltax)
        out_scaled_y[index] = int(world_y * ry_scale + deltay)


    @cuda.jit
    def _sort_key_kernel(
        edge_ids,
        tie_ids,
        scaled_x,
        scaled_y,
        dataset_x0,
        dataset_y0,
        rx_scale,
        ry_scale,
        deltax,
        deltay,
        out_edge,
        out_tie,
        out_dist,
        out_order,
        valid_count,
        sentinel_edge,
    ):
        index = cuda.grid(1)
        if index >= out_edge.shape[0]:
            return
        if index >= valid_count:
            out_edge[index] = sentinel_edge
            out_tie[index] = sentinel_edge
            out_dist[index] = math.inf
            out_order[index] = index
            return

        edge_id = int(edge_ids[index])
        start_sx = int(dataset_x0[edge_id] * rx_scale + deltax)
        start_sy = int(dataset_y0[edge_id] * ry_scale + deltay)
        dx = float(scaled_x[index] - start_sx)
        dy = float(scaled_y[index] - start_sy)
        out_edge[index] = edge_id
        out_tie[index] = int(tie_ids[index])
        out_dist[index] = dx * dx + dy * dy
        out_order[index] = index


    @cuda.jit
    def _bitonic_sort_step(edge_key, dist_key, tie_key, order, j, k):
        i = cuda.grid(1)
        partner = i ^ j
        if partner <= i or partner >= edge_key.shape[0]:
            return

        ascending = (i & k) == 0
        left_better = _lex_key_less(
            edge_key[i],
            dist_key[i],
            tie_key[i],
            order[i],
            edge_key[partner],
            dist_key[partner],
            tie_key[partner],
            order[partner],
        )
        should_swap = (ascending and not left_better) or ((not ascending) and left_better)
        if should_swap:
            tmp_edge = edge_key[i]
            tmp_dist = dist_key[i]
            tmp_tie = tie_key[i]
            tmp_order = order[i]
            edge_key[i] = edge_key[partner]
            dist_key[i] = dist_key[partner]
            tie_key[i] = tie_key[partner]
            order[i] = order[partner]
            edge_key[partner] = tmp_edge
            dist_key[partner] = tmp_dist
            tie_key[partner] = tmp_tie
            order[partner] = tmp_order


    @cuda.jit(device=True)
    def _lex_key_less(a_edge, a_dist, a_tie, a_order, b_edge, b_dist, b_tie, b_order):
        if a_edge < b_edge:
            return True
        if a_edge > b_edge:
            return False
        if a_dist < b_dist:
            return True
        if a_dist > b_dist:
            return False
        if a_tie < b_tie:
            return True
        if a_tie > b_tie:
            return False
        return a_order <= b_order


    @cuda.jit
    def _fill_i64_kernel(values, fill_value):
        index = cuda.grid(1)
        if index < values.shape[0]:
            values[index] = fill_value


    @cuda.jit
    def _fill_f64_kernel(values, fill_value):
        index = cuda.grid(1)
        if index < values.shape[0]:
            values[index] = fill_value


    @cuda.jit
    def _run_bounds_from_sorted_edges_kernel(sorted_edges, run_start, run_end, valid_count):
        index = cuda.grid(1)
        if index >= valid_count:
            return
        edge = int(sorted_edges[index])
        if index == 0 or int(sorted_edges[index - 1]) != edge:
            run_start[edge] = index
        if index == valid_count - 1 or int(sorted_edges[index + 1]) != edge:
            run_end[edge] = index + 1


    @cuda.jit
    def _scatter_u32_by_i64_index_kernel(indices, values, out, count):
        index = cuda.grid(1)
        if index < count:
            out[int(indices[index])] = values[index]


    @cuda.jit(device=True)
    def _trunc_div2_i64_device(value):
        if value >= 0:
            return value // 2
        return -((-value) // 2)


    @cuda.jit
    def _midpoint_device_query_points_kernel(
        order,
        edge_ids,
        scaled_x,
        scaled_y,
        valid_count,
        rrx,
        rry,
        ddeltax,
        ddeltay,
        out_points,
        out_owners,
        out_count,
    ):
        index = cuda.grid(1)
        if index >= valid_count - 1:
            return
        if edge_ids[index] != edge_ids[index + 1]:
            return
        pos = cuda.atomic.add(out_count, 0, 1)
        owner = int(order[index])
        neighbor = int(order[index + 1])
        sx = _trunc_div2_i64_device(int(scaled_x[owner]) + int(scaled_x[neighbor]))
        sy = _trunc_div2_i64_device(int(scaled_y[owner]) + int(scaled_y[neighbor]))
        out_owners[pos] = owner
        out_points[pos]["x"] = sx * rrx + ddeltax
        out_points[pos]["y"] = sy * rry + ddeltay
        out_points[pos]["id"] = pos + 1
        out_points[pos]["has_scaled"] = 1
        out_points[pos]["sx"] = sx
        out_points[pos]["sy"] = sy


    @cuda.jit(device=True)
    def _append_dedup_len_device(x, y, current_len, has_previous, previous_x, previous_y):
        if (not has_previous) or x != previous_x or y != previous_y:
            return current_len + 1, True, x, y
        return current_len, has_previous, previous_x, previous_y


    @cuda.jit(device=True)
    def _carrier_keep_group(left_label, right_label, other_label):
        return left_label * other_label != 0 or right_label * other_label != 0


    @cuda.jit
    def _carrier_side_count_kernel(
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        order,
        run_start,
        run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        group_counts,
        point_row_counts,
        skipped_counts,
    ):
        chain_index = cuda.grid(1)
        if chain_index >= chain_offsets.shape[0]:
            return

        point_offset = int(chain_offsets[chain_index])
        point_count = int(chain_point_counts[chain_index])
        edge_id = point_offset - chain_index
        left_label = int(chain_left_faces[chain_index])
        right_label = int(chain_right_faces[chain_index])
        other_label = 0
        current_len = 0
        has_previous = False
        previous_x = 0.0
        previous_y = 0.0
        group_count = 0
        point_rows = 0
        skipped = 0

        for local_point_index in range(point_count):
            point_index = point_offset + local_point_index
            other_label = int(point_faces[point_index])
            current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                float(point_x[point_index]),
                float(point_y[point_index]),
                current_len,
                has_previous,
                previous_x,
                previous_y,
            )

            if local_point_index == point_count - 1:
                continue

            start = int(run_start[edge_id]) if edge_id < run_start.shape[0] else -1
            end = int(run_end[edge_id]) if edge_id < run_end.shape[0] else -1
            if start >= 0 and end > start:
                first = int(order[start])
                current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                    float(display_x[first]),
                    float(display_y[first]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )
                for sorted_pos in range(start, end - 1):
                    xsect_index = int(order[sorted_pos])
                    next_index = int(order[sorted_pos + 1])
                    if current_len > 0:
                        if _carrier_keep_group(left_label, right_label, other_label):
                            group_count += 1
                            point_rows += current_len
                        else:
                            skipped += 1
                        current_len = 0
                        has_previous = False
                        previous_x = 0.0
                        previous_y = 0.0
                    other_label = int(midpoint_faces[xsect_index])
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                        float(display_x[xsect_index]),
                        float(display_y[xsect_index]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                        float(display_x[next_index]),
                        float(display_y[next_index]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                if current_len > 0:
                    if _carrier_keep_group(left_label, right_label, other_label):
                        group_count += 1
                        point_rows += current_len
                    else:
                        skipped += 1
                    current_len = 0
                    has_previous = False
                    previous_x = 0.0
                    previous_y = 0.0
                last = int(order[end - 1])
                current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                    float(display_x[last]),
                    float(display_y[last]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )
            edge_id += 1

        if current_len > 0:
            if _carrier_keep_group(left_label, right_label, other_label):
                group_count += 1
                point_rows += current_len
            else:
                skipped += 1

        group_counts[chain_index] = group_count
        point_row_counts[chain_index] = point_rows
        skipped_counts[chain_index] = skipped


    @cuda.jit
    def _exclusive_prefix_sum_i64_single_kernel(values, offsets, total_out):
        running = 0
        for index in range(values.shape[0]):
            offsets[index] = running
            running += int(values[index])
        total_out[0] = running


    @cuda.jit
    def _carrier_side_fill_kernel(
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        order,
        run_start,
        run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        chain_group_offsets,
        out_group_length,
        out_label_a,
        out_label_b,
    ):
        chain_index = cuda.grid(1)
        if chain_index >= chain_offsets.shape[0]:
            return

        write_index = int(chain_group_offsets[chain_index])
        point_offset = int(chain_offsets[chain_index])
        point_count = int(chain_point_counts[chain_index])
        edge_id = point_offset - chain_index
        left_label = int(chain_left_faces[chain_index])
        right_label = int(chain_right_faces[chain_index])
        other_label = 0
        current_len = 0
        has_previous = False
        previous_x = 0.0
        previous_y = 0.0

        for local_point_index in range(point_count):
            point_index = point_offset + local_point_index
            other_label = int(point_faces[point_index])
            current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                float(point_x[point_index]),
                float(point_y[point_index]),
                current_len,
                has_previous,
                previous_x,
                previous_y,
            )

            if local_point_index == point_count - 1:
                continue

            start = int(run_start[edge_id]) if edge_id < run_start.shape[0] else -1
            end = int(run_end[edge_id]) if edge_id < run_end.shape[0] else -1
            if start >= 0 and end > start:
                first = int(order[start])
                current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                    float(display_x[first]),
                    float(display_y[first]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )
                for sorted_pos in range(start, end - 1):
                    xsect_index = int(order[sorted_pos])
                    next_index = int(order[sorted_pos + 1])
                    if current_len > 0:
                        if _carrier_keep_group(left_label, right_label, other_label):
                            out_group_length[write_index] = current_len
                            out_label_a[write_index] = left_label
                            out_label_b[write_index] = other_label
                            write_index += 1
                        current_len = 0
                        has_previous = False
                        previous_x = 0.0
                        previous_y = 0.0
                    other_label = int(midpoint_faces[xsect_index])
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                        float(display_x[xsect_index]),
                        float(display_y[xsect_index]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                        float(display_x[next_index]),
                        float(display_y[next_index]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                if current_len > 0:
                    if _carrier_keep_group(left_label, right_label, other_label):
                        out_group_length[write_index] = current_len
                        out_label_a[write_index] = left_label
                        out_label_b[write_index] = other_label
                        write_index += 1
                    current_len = 0
                    has_previous = False
                    previous_x = 0.0
                    previous_y = 0.0
                last = int(order[end - 1])
                current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                    float(display_x[last]),
                    float(display_y[last]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )
            edge_id += 1

        if current_len > 0 and _carrier_keep_group(left_label, right_label, other_label):
            out_group_length[write_index] = current_len
            out_label_a[write_index] = left_label
            out_label_b[write_index] = other_label


    @cuda.jit(device=True)
    def _carrier_emit_group_atomic(
        current_len,
        left_label,
        right_label,
        other_label,
        out_group_length,
        out_label_a,
        out_label_b,
        counters,
        capacity,
        overflow,
    ):
        if current_len <= 0:
            return
        if _carrier_keep_group(left_label, right_label, other_label):
            write_index = cuda.atomic.add(counters, 0, 1)
            cuda.atomic.add(counters, 1, current_len)
            if write_index < capacity:
                out_group_length[write_index] = current_len
                out_label_a[write_index] = left_label
                out_label_b[write_index] = other_label
            else:
                overflow[0] = 1
        else:
            cuda.atomic.add(counters, 2, 1)


    @cuda.jit
    def _carrier_side_atomic_append_kernel(
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        order,
        run_start,
        run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        out_group_length,
        out_label_a,
        out_label_b,
        counters,
        capacity,
        overflow,
    ):
        chain_index = cuda.grid(1)
        if chain_index >= chain_offsets.shape[0]:
            return

        point_offset = int(chain_offsets[chain_index])
        point_count = int(chain_point_counts[chain_index])
        edge_id = point_offset - chain_index
        left_label = int(chain_left_faces[chain_index])
        right_label = int(chain_right_faces[chain_index])
        other_label = 0
        current_len = 0
        has_previous = False
        previous_x = 0.0
        previous_y = 0.0

        for local_point_index in range(point_count):
            point_index = point_offset + local_point_index
            other_label = int(point_faces[point_index])
            current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                float(point_x[point_index]),
                float(point_y[point_index]),
                current_len,
                has_previous,
                previous_x,
                previous_y,
            )

            if local_point_index == point_count - 1:
                continue

            start = int(run_start[edge_id]) if edge_id < run_start.shape[0] else -1
            end = int(run_end[edge_id]) if edge_id < run_end.shape[0] else -1
            if start >= 0 and end > start:
                first = int(order[start])
                current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                    float(display_x[first]),
                    float(display_y[first]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )
                for sorted_pos in range(start, end - 1):
                    xsect_index = int(order[sorted_pos])
                    next_index = int(order[sorted_pos + 1])
                    _carrier_emit_group_atomic(
                        current_len,
                        left_label,
                        right_label,
                        other_label,
                        out_group_length,
                        out_label_a,
                        out_label_b,
                        counters,
                        capacity,
                        overflow,
                    )
                    current_len = 0
                    has_previous = False
                    previous_x = 0.0
                    previous_y = 0.0
                    other_label = int(midpoint_faces[xsect_index])
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                        float(display_x[xsect_index]),
                        float(display_y[xsect_index]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                    current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                        float(display_x[next_index]),
                        float(display_y[next_index]),
                        current_len,
                        has_previous,
                        previous_x,
                        previous_y,
                    )
                _carrier_emit_group_atomic(
                    current_len,
                    left_label,
                    right_label,
                    other_label,
                    out_group_length,
                    out_label_a,
                    out_label_b,
                    counters,
                    capacity,
                    overflow,
                )
                current_len = 0
                has_previous = False
                previous_x = 0.0
                previous_y = 0.0
                last = int(order[end - 1])
                current_len, has_previous, previous_x, previous_y = _append_dedup_len_device(
                    float(display_x[last]),
                    float(display_y[last]),
                    current_len,
                    has_previous,
                    previous_x,
                    previous_y,
                )
            edge_id += 1

        _carrier_emit_group_atomic(
            current_len,
            left_label,
            right_label,
            other_label,
            out_group_length,
            out_label_a,
            out_label_b,
            counters,
            capacity,
            overflow,
        )


    @cuda.jit
    def _copy_carrier_side_to_combined_kernel(
        src_length,
        src_a,
        src_b,
        src_count,
        dst_length,
        dst_a,
        dst_b,
        dst_offset,
    ):
        index = cuda.grid(1)
        if index < src_count:
            dst_index = dst_offset + index
            dst_length[dst_index] = src_length[index]
            dst_a[dst_index] = src_a[index]
            dst_b[dst_index] = src_b[index]


    @cuda.jit
    def _fill_carrier_sentinel_kernel(lengths, label_a, label_b, start, count, sentinel):
        index = cuda.grid(1)
        absolute = start + index
        if index < count and absolute < label_a.shape[0]:
            lengths[absolute] = 0
            label_a[absolute] = sentinel
            label_b[absolute] = sentinel


    @cuda.jit(device=True)
    def _pair_key_less(a_label_a, a_label_b, a_order, b_label_a, b_label_b, b_order):
        if a_label_a < b_label_a:
            return True
        if a_label_a > b_label_a:
            return False
        if a_label_b < b_label_b:
            return True
        if a_label_b > b_label_b:
            return False
        return a_order <= b_order


    @cuda.jit
    def _pair_bitonic_sort_step(label_a, label_b, lengths, order, j, k):
        i = cuda.grid(1)
        partner = i ^ j
        if partner <= i or partner >= label_a.shape[0]:
            return

        ascending = (i & k) == 0
        left_better = _pair_key_less(
            label_a[i],
            label_b[i],
            order[i],
            label_a[partner],
            label_b[partner],
            order[partner],
        )
        should_swap = (ascending and not left_better) or ((not ascending) and left_better)
        if should_swap:
            tmp_a = label_a[i]
            tmp_b = label_b[i]
            tmp_len = lengths[i]
            tmp_order = order[i]
            label_a[i] = label_a[partner]
            label_b[i] = label_b[partner]
            lengths[i] = lengths[partner]
            order[i] = order[partner]
            label_a[partner] = tmp_a
            label_b[partner] = tmp_b
            lengths[partner] = tmp_len
            order[partner] = tmp_order


    @cuda.jit
    def _init_order_kernel(order):
        index = cuda.grid(1)
        if index < order.shape[0]:
            order[index] = index


    @cuda.jit
    def _reduce_sorted_descriptor_pairs_single_kernel(label_a, label_b, lengths, valid_count, out):
        pair_count = 0
        total_groups = 0
        total_points = 0
        previous_a = -1
        previous_b = -1
        for index in range(valid_count):
            a = int(label_a[index])
            b = int(label_b[index])
            total_groups += 1
            total_points += int(lengths[index])
            if index == 0 or a != previous_a or b != previous_b:
                pair_count += 1
                previous_a = a
                previous_b = b
        out[0] = pair_count
        out[1] = total_groups
        out[2] = total_points


    @cuda.jit
    def _reduce_sorted_descriptor_pairs_with_order_single_kernel(label_a, label_b, lengths, order, valid_count, out):
        pair_count = 0
        total_groups = 0
        total_points = 0
        previous_a = -1
        previous_b = -1
        for index in range(valid_count):
            a = int(label_a[index])
            b = int(label_b[index])
            total_groups += 1
            total_points += int(lengths[int(order[index])])
            if index == 0 or a != previous_a or b != previous_b:
                pair_count += 1
                previous_a = a
                previous_b = b
        out[0] = pair_count
        out[1] = total_groups
        out[2] = total_points


    @cuda.jit
    def _sum_two_i64_single_kernel(values_a, values_b, out):
        total_a = 0
        total_b = 0
        for index in range(values_a.shape[0]):
            total_a += int(values_a[index])
            total_b += int(values_b[index])
        out[0] = total_a
        out[1] = total_b


def timed(name, fn, phase_seconds):
    start = time.perf_counter()
    result = fn()
    phase_seconds[name] = time.perf_counter() - start
    return result


def _record_lsi_native_timings(target, label, prepared):
    if target is None:
        return
    target[label] = prepared.last_phase_timings() or {}


def run_lsi(left, right, native_lsi_timings=None):
    with base.prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            row_view = query.run_pair_id_rows()
            try:
                pairs = _pair_id_rows_to_numpy(row_view)
                _record_lsi_native_timings(native_lsi_timings, "host_pair_id_rows", lsi.prepared)
                return pairs
            finally:
                row_view.close()


def _pair_id_rows_to_numpy(row_view):
    columns = row_view.to_numpy_columns(copy=False)
    return np.column_stack(
        (
            columns["left_id"].astype(np.uint32, copy=False),
            columns["right_id"].astype(np.uint32, copy=False),
        )
    )


def _run_lsi_query_pair_id_rows(query):
    row_view = query.run_pair_id_rows()
    try:
        return _pair_id_rows_to_numpy(row_view)
    finally:
        row_view.close()


def _device_pair_columns_to_numpy(device_columns):
    left = _copy_cuda_device_column_to_numpy(
        device_columns.left_ids_device_ptr,
        device_columns.row_count,
        np.uint64,
        "exact LSI left_id column",
    ).astype(np.uint32, copy=False)
    right = _copy_cuda_device_column_to_numpy(
        device_columns.right_ids_device_ptr,
        device_columns.row_count,
        np.uint64,
        "exact LSI right_id column",
    ).astype(np.uint32, copy=False)
    return np.column_stack((left, right))


def _copy_cuda_device_column_to_numpy(device_ptr: int, row_count: int, dtype, label: str) -> np.ndarray:
    output = np.empty(int(row_count), dtype=dtype)
    if row_count == 0:
        return output
    cuda = ctypes.CDLL("libcuda.so.1")
    copy = getattr(cuda, "cuMemcpyDtoH_v2", None) or getattr(cuda, "cuMemcpyDtoH")
    copy.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_size_t]
    copy.restype = ctypes.c_int
    status = copy(
        output.ctypes.data_as(ctypes.c_void_p),
        ctypes.c_uint64(int(device_ptr)),
        ctypes.c_size_t(int(row_count) * output.dtype.itemsize),
    )
    if status != 0:
        raise RuntimeError(f"cuMemcpyDtoH failed while copying {label}: {status}")
    return output


def _point_location_face_id_device_columns_to_numpy(device_columns) -> np.ndarray:
    return _copy_cuda_device_column_to_numpy(
        device_columns.ids_device_ptr,
        device_columns.row_count,
        np.uint32,
        "directed point-location face_id column",
    )


def _point_face_host(value):
    if isinstance(value, dict) and "host" in value:
        return value["host"]
    return value


def _point_face_device(value):
    if isinstance(value, dict):
        return value.get("device")
    return None


def _close_point_face_value(value) -> None:
    if isinstance(value, dict):
        owner = value.get("prepared_points_owner")
        if owner is not None:
            owner.close()


def run_point_location_face_id_device_columns(
    locator,
    points,
    point_count: int,
    *,
    phase_prefix: str,
    phase_seconds: dict[str, float],
    metadata_records: dict[str, object],
    prepared_points=None,
    retain_device: bool = False,
    copy_host: bool = True,
):
    owns_prepared_points = prepared_points is None
    if prepared_points is None:
        prepared_points = timed(
            f"{phase_prefix}_prepare_device_points_sec",
            lambda: locator.prepare_query_points(points),
            phase_seconds,
        )
    try:
        device_columns = timed(
            f"{phase_prefix}_face_id_device_columns_sec",
            lambda: locator.face_id_device_columns(prepared_points),
            phase_seconds,
        )
        row_buffer = device_column_row_buffer_from_point_location_id_columns(device_columns)
        metadata_records[phase_prefix] = {
            "device_columns": device_columns.to_metadata(),
            "row_buffer": row_buffer.to_metadata(),
            "downstream_numpy_copy_used": bool(copy_host),
            "true_zero_copy_claim_authorized": False,
        }
        host = None
        if copy_host:
            host = timed(
                f"{phase_prefix}_face_id_device_columns_to_numpy_sec",
                lambda: _point_location_face_id_device_columns_to_numpy(device_columns),
                phase_seconds,
            )
        if retain_device:
            device_array = cuda.as_cuda_array(row_buffer.columns["face_id"])
            prepared_owner = prepared_points if (owns_prepared_points or getattr(prepared_points, "owner", None) is not None) else None
            result = {
                "host": host,
                "device": device_array,
                "device_columns": device_columns,
                "row_buffer": row_buffer.to_metadata(),
                "prepared_points_owner": prepared_owner,
            }
            owns_prepared_points = False
            return result
        return host
    finally:
        if owns_prepared_points:
            prepared_points.close()


def run_lsi_exact_device_columns(left, right, phase_seconds, native_lsi_timings=None):
    device_columns = produce_lsi_exact_device_columns(left, right, phase_seconds, native_lsi_timings)
    try:
        return timed(
            "lsi_exact_pair_id_device_columns_to_numpy_sec",
            lambda: _device_pair_columns_to_numpy(device_columns),
            phase_seconds,
        )
    finally:
        device_columns.close()


def produce_lsi_exact_device_columns(left, right, phase_seconds, native_lsi_timings=None):
    with base.prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            return produce_lsi_exact_device_columns_from_prepared_query(
                lsi,
                query,
                phase_seconds,
                native_lsi_timings,
            )


def produce_lsi_exact_device_columns_from_prepared_base(
    lsi,
    left,
    phase_seconds,
    native_lsi_timings=None,
):
    with lsi.prepare_query(left.lsi_segments) as query:
        return produce_lsi_exact_device_columns_from_prepared_query(
            lsi,
            query,
            phase_seconds,
            native_lsi_timings,
        )


def produce_lsi_exact_device_columns_from_prepared_query(lsi, query, phase_seconds, native_lsi_timings=None):
    device_columns = timed(
        "lsi_exact_pair_id_device_columns_sec",
        lambda: query.run_pair_id_device_columns(),
        phase_seconds,
    )
    exact_timings = lsi.prepared.last_phase_timings() or {}
    exact_timings = {
        **exact_timings,
        "native_output_traversal_seconds": float(device_columns.traversal_seconds),
        "native_output_row_count": int(device_columns.row_count),
        "native_output_candidate_event_count": int(device_columns.candidate_event_count),
    }
    if native_lsi_timings is not None:
        native_lsi_timings["exact_pair_id_device_columns"] = exact_timings
    return device_columns


def run_lsi_bounded_exact_device_columns(left, right, phase_seconds, native_lsi_timings=None, *, capacity: int):
    device_columns = produce_lsi_bounded_exact_device_columns(
        left,
        right,
        phase_seconds,
        native_lsi_timings,
        capacity=capacity,
    )
    try:
        return timed(
            "lsi_bounded_exact_pair_id_device_columns_to_numpy_sec",
            lambda: _device_pair_columns_to_numpy(device_columns),
            phase_seconds,
        )
    finally:
        device_columns.close()


def produce_lsi_bounded_exact_device_columns(left, right, phase_seconds, native_lsi_timings=None, *, capacity: int):
    if capacity <= 0:
        raise ValueError("--bounded-exact-lsi-capacity must be positive")
    with base.prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            return produce_lsi_bounded_exact_device_columns_from_prepared_query(
                lsi,
                query,
                phase_seconds,
                native_lsi_timings,
                capacity=capacity,
            )


def produce_lsi_bounded_exact_device_columns_from_prepared_base(
    lsi,
    left,
    phase_seconds,
    native_lsi_timings=None,
    *,
    capacity: int,
):
    if capacity <= 0:
        raise ValueError("--bounded-exact-lsi-capacity must be positive")
    with lsi.prepare_query(left.lsi_segments) as query:
        return produce_lsi_bounded_exact_device_columns_from_prepared_query(
            lsi,
            query,
            phase_seconds,
            native_lsi_timings,
            capacity=capacity,
        )


def produce_lsi_bounded_exact_device_columns_from_prepared_query(
    lsi,
    query,
    phase_seconds,
    native_lsi_timings=None,
    *,
    capacity: int,
):
    if capacity <= 0:
        raise ValueError("--bounded-exact-lsi-capacity must be positive")
    device_columns = timed(
        "lsi_bounded_exact_pair_id_device_columns_sec",
        lambda: query.run_bounded_pair_id_device_columns(max_rows=int(capacity)),
        phase_seconds,
    )
    exact_timings = lsi.prepared.last_phase_timings() or {}
    exact_timings = {
        **exact_timings,
        "native_output_traversal_seconds": float(device_columns.traversal_seconds),
        "native_output_row_count": int(device_columns.row_count),
        "native_output_capacity": int(device_columns.capacity),
        "native_output_candidate_event_count": int(device_columns.candidate_event_count),
        "native_output_overflow": bool(device_columns.overflow),
    }
    if native_lsi_timings is not None:
        native_lsi_timings["bounded_exact_pair_id_device_columns"] = exact_timings
    if device_columns.overflow:
        device_columns.close()
        raise RuntimeError(
            "bounded exact LSI device-column route overflowed: "
            f"capacity={device_columns.capacity}, required={device_columns.candidate_event_count}"
        )
    return device_columns


def run_lsi_bounded_exact_repeat_diagnostic(left, right, *, capacity: int, repeat_count: int) -> dict[str, object]:
    if capacity <= 0:
        raise ValueError("--bounded-exact-lsi-capacity must be positive for repeat diagnostic")
    if repeat_count <= 0:
        raise ValueError("--bounded-exact-lsi-repeat-diagnostic must be positive")
    runs: list[dict[str, object]] = []
    with base.prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            for index in range(repeat_count):
                start = time.perf_counter()
                device_columns = query.run_bounded_pair_id_device_columns(max_rows=int(capacity))
                elapsed = time.perf_counter() - start
                try:
                    timings = lsi.prepared.last_phase_timings() or {}
                    runs.append(
                        {
                            "index": index,
                            "elapsed_sec": float(elapsed),
                            "row_count": int(device_columns.row_count),
                            "capacity": int(device_columns.capacity),
                            "candidate_event_count": int(device_columns.candidate_event_count),
                            "overflow": bool(device_columns.overflow),
                            "native_output_traversal_seconds": float(device_columns.traversal_seconds),
                            "native_timings": timings,
                        }
                    )
                    if device_columns.overflow:
                        break
                finally:
                    device_columns.close()
    first = float(runs[0]["elapsed_sec"]) if runs else None
    later = [float(run["elapsed_sec"]) for run in runs[1:]]
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.section57.bounded_exact_lsi_repeat_diagnostic.v1",
        "capacity": int(capacity),
        "repeat_count_requested": int(repeat_count),
        "repeat_count_completed": len(runs),
        "runs": runs,
        "first_run_sec": first,
        "later_run_min_sec": min(later) if later else None,
        "later_run_median_sec": float(np.median(np.asarray(later, dtype=np.float64))) if later else None,
        "claim_boundary": {
            "diagnostic_only": True,
            "same_process_same_prepared_query": True,
            "no_numpy_copy": True,
            "no_author_comparison": True,
            "public_speedup_claim_authorized": False,
        },
    }


def run_lsi_prepared_replay(left, right, phase_seconds, native_lsi_timings=None):
    prepare_start = time.perf_counter()
    with base.prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            phase_seconds["prepare_lsi_session_sec"] = time.perf_counter() - prepare_start
            workspace = timed("lsi_prepare_workspace_sec", query.prepare_workspace, phase_seconds)
            if native_lsi_timings is not None:
                native_lsi_timings["prepared_workspace"] = workspace
            pairs = timed("lsi_prepared_replay_rows_sec", lambda: _run_lsi_query_pair_id_rows(query), phase_seconds)
            _record_lsi_native_timings(native_lsi_timings, "prepared_replay_pair_id_rows", lsi.prepared)
            return pairs


def _sum_phase_seconds(phase_seconds: dict[str, float], keys: list[str]) -> float:
    return float(sum(float(phase_seconds.get(key, 0.0)) for key in keys if key))


def build_lsi_cost_decomposition(
    *,
    phase_seconds: dict[str, float],
    native_lsi_timings: dict[str, object],
    lsi_key: str,
    copy_key: str,
    timing_label: str,
) -> dict[str, object]:
    lsi_phase_sec = float(phase_seconds.get(lsi_key, 0.0))
    copy_sec = float(phase_seconds.get(copy_key, 0.0)) if copy_key else 0.0
    native = native_lsi_timings.get(timing_label, {}) if native_lsi_timings else {}
    extended = native.get("extended", {}) if isinstance(native, dict) else {}
    native_total = None
    if isinstance(extended, dict) and "total_native" in extended:
        native_total = float(extended["total_native"])
    elif isinstance(native, dict) and "native_output_traversal_seconds" in native:
        native_total = float(native["native_output_traversal_seconds"])
    unaccounted = None if native_total is None else lsi_phase_sec - native_total
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.section57.lsi_cost_decomposition.v1",
        "lsi_phase_key": lsi_key,
        "lsi_phase_sec": lsi_phase_sec,
        "copy_key": copy_key or None,
        "copy_sec": copy_sec,
        "native_timing_label": timing_label,
        "native_total_sec": native_total,
        "python_wrapper_or_unaccounted_sec": unaccounted,
        "native_timings": native,
    }


def build_downstream_floor_breakdown(
    *,
    phase_seconds: dict[str, float],
    lsi_key: str,
    copy_key: str,
    compiled_group_enabled: bool,
    device_columnar_enabled: bool,
    device_resident_carrier_enabled: bool = False,
) -> dict[str, object]:
    downstream_keys = [
        "intersection_reprojection_device_columnar_sec" if device_columnar_enabled else "intersection_reprojection_columnar_sec",
        "sort_map0_device_columnar_sec" if device_columnar_enabled else "sort_map0_columnar_sec",
        "sort_map1_device_columnar_sec" if device_columnar_enabled else "sort_map1_columnar_sec",
        "vertex_pip_map0_in_map1_sec",
        "vertex_pip_map1_in_map0_sec",
        "midpoint_points_map0_device_query_points_sec"
        if device_resident_carrier_enabled
        else "midpoint_points_map0_columnar_sec",
        "midpoint_points_map1_device_query_points_sec"
        if device_resident_carrier_enabled
        else "midpoint_points_map1_columnar_sec",
        "midpoint_pip_map0_sec",
        "midpoint_pip_map1_sec",
        "assign_midpoint_faces_map0_device_scatter_sec"
        if device_resident_carrier_enabled
        else "assign_midpoint_faces_map0_columnar_sec",
        "assign_midpoint_faces_map1_device_scatter_sec"
        if device_resident_carrier_enabled
        else "assign_midpoint_faces_map1_columnar_sec",
        "device_resident_carrier_construction_sec"
        if device_resident_carrier_enabled
        else "grouped_compiled_columnar_carrier_construction_sec"
        if compiled_group_enabled
        else "grouped_columnar_carrier_construction_sec",
        "device_resident_descriptor_pair_count_consumer_sec"
        if device_resident_carrier_enabled
        else "grouped_descriptor_pair_count_consumer_sec",
    ]
    components = {key: float(phase_seconds.get(key, 0.0)) for key in downstream_keys}
    downstream_total = _sum_phase_seconds(phase_seconds, downstream_keys)
    lsi_total = float(phase_seconds.get(lsi_key, 0.0))
    copy_total = float(phase_seconds.get(copy_key, 0.0)) if copy_key else 0.0
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.section57.downstream_floor_breakdown.v1",
        "lsi_phase_key": lsi_key,
        "lsi_phase_sec": lsi_total,
        "copy_key": copy_key or None,
        "copy_sec": copy_total,
        "downstream_keys": downstream_keys,
        "downstream_components_sec": components,
        "downstream_floor_sec": downstream_total,
        "writer_free_hot_recomputed_sec": lsi_total + copy_total + downstream_total,
        "largest_downstream_component": max(components.items(), key=lambda item: item[1]) if components else None,
        "claim_boundary": {
            "writer_excluded": True,
            "author_comparison_authorized": False,
            "steady_state_floor_measurement": True,
        },
    }


def _dedupe_consecutive_point_count(points: list[tuple[float, float]]) -> int:
    if not points:
        return 0
    count = 1
    previous = points[0]
    for point in points[1:]:
        if point != previous:
            count += 1
            previous = point
    return count


def _warm_numba() -> None:
    if not NUMBA_AVAILABLE:
        return
    carrier = {
        "label_a": np.asarray([1, 1, 2], dtype=np.int64),
        "label_b": np.asarray([10, 10, 20], dtype=np.int64),
        "group_length": np.asarray([2, 3, 4], dtype=np.int64),
    }
    descriptor_pair_count_projected(carrier)
    out_len = np.empty(2, dtype=np.int64)
    out_a = np.empty(2, dtype=np.int64)
    out_b = np.empty(2, dtype=np.int64)
    out_metrics = np.zeros(len(GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS), dtype=np.int64)
    _build_projected_descriptor_side_numba(
        np.asarray([0], dtype=np.int64),
        np.asarray([2], dtype=np.int64),
        np.asarray([1], dtype=np.int64),
        np.asarray([2], dtype=np.int64),
        np.asarray([0.0, 1.0], dtype=np.float64),
        np.asarray([0.0, 0.0], dtype=np.float64),
        np.asarray([], dtype=np.int64),
        np.asarray([-1], dtype=np.int64),
        np.asarray([-1], dtype=np.int64),
        np.asarray([], dtype=np.float64),
        np.asarray([], dtype=np.float64),
        np.asarray([3, 3], dtype=np.uint32),
        np.asarray([], dtype=np.uint32),
        out_len,
        out_a,
        out_b,
        out_metrics,
    )


def _warm_numba_cuda_device_columnar() -> None:
    if not _cuda_is_available():
        return
    pair_left = cuda.to_device(np.asarray([1], dtype=np.int64))
    pair_right = cuda.to_device(np.asarray([1], dtype=np.int64))
    one_f64 = cuda.to_device(np.asarray([0.0], dtype=np.float64))
    out_eid0 = cuda.device_array(1, dtype=np.int64)
    out_eid1 = cuda.device_array(1, dtype=np.int64)
    out_display_x = cuda.device_array(1, dtype=np.float64)
    out_display_y = cuda.device_array(1, dtype=np.float64)
    out_scaled_x = cuda.device_array(1, dtype=np.int64)
    out_scaled_y = cuda.device_array(1, dtype=np.int64)
    _numeric_xsect_columns_kernel[1, 1](
        pair_left,
        pair_right,
        one_f64,
        one_f64,
        cuda.to_device(np.asarray([1.0], dtype=np.float64)),
        one_f64,
        one_f64,
        one_f64,
        one_f64,
        cuda.to_device(np.asarray([1.0], dtype=np.float64)),
        1.0,
        1.0,
        0.0,
        0.0,
        out_eid0,
        out_eid1,
        out_display_x,
        out_display_y,
        out_scaled_x,
        out_scaled_y,
    )
    edge_key = cuda.device_array(2, dtype=np.int64)
    tie_key = cuda.device_array(2, dtype=np.int64)
    dist_key = cuda.device_array(2, dtype=np.float64)
    order = cuda.device_array(2, dtype=np.int64)
    _sort_key_kernel[1, 2](
        out_eid0,
        out_eid1,
        out_scaled_x,
        out_scaled_y,
        one_f64,
        one_f64,
        1.0,
        1.0,
        0.0,
        0.0,
        edge_key,
        tie_key,
        dist_key,
        order,
        1,
        int(np.iinfo(np.int64).max),
    )
    _bitonic_sort_device(edge_key, dist_key, tie_key, order)
    _compute_run_bounds_device(cuda.to_device(np.asarray([0, 0], dtype=np.int64)), 2, 1)
    midpoint_order = cuda.to_device(np.asarray([0, 1], dtype=np.int64))
    midpoint_edges = cuda.to_device(np.asarray([7, 7], dtype=np.int64))
    midpoint_scaled_x = cuda.to_device(np.asarray([0, 2], dtype=np.int64))
    midpoint_scaled_y = cuda.to_device(np.asarray([0, 2], dtype=np.int64))
    midpoint_points = cuda.device_array(1, dtype=DEVICE_QUERY_POINT_DTYPE)
    midpoint_owners = cuda.device_array(1, dtype=np.int64)
    midpoint_count = cuda.to_device(np.zeros(1, dtype=np.int64))
    _midpoint_device_query_points_kernel[1, 2](
        midpoint_order,
        midpoint_edges,
        midpoint_scaled_x,
        midpoint_scaled_y,
        2,
        1.0,
        1.0,
        0.0,
        0.0,
        midpoint_points,
        midpoint_owners,
        midpoint_count,
    )
    chain_offsets = cuda.to_device(np.asarray([0], dtype=np.int64))
    chain_point_counts = cuda.to_device(np.asarray([2], dtype=np.int64))
    chain_left_faces = cuda.to_device(np.asarray([1], dtype=np.int64))
    chain_right_faces = cuda.to_device(np.asarray([2], dtype=np.int64))
    point_x = cuda.to_device(np.asarray([0.0, 1.0], dtype=np.float64))
    point_y = cuda.to_device(np.asarray([0.0, 0.0], dtype=np.float64))
    carrier_order = cuda.to_device(np.asarray([0, 1], dtype=np.int64))
    carrier_run_start = cuda.to_device(np.asarray([0], dtype=np.int64))
    carrier_run_end = cuda.to_device(np.asarray([2], dtype=np.int64))
    display_x = cuda.to_device(np.asarray([0.25, 0.75], dtype=np.float64))
    display_y = cuda.to_device(np.asarray([0.0, 0.0], dtype=np.float64))
    point_faces = cuda.to_device(np.asarray([3, 3], dtype=np.uint32))
    midpoint_faces = cuda.to_device(np.asarray([4, 4], dtype=np.uint32))
    group_counts = cuda.device_array(1, dtype=np.int64)
    point_row_counts = cuda.device_array(1, dtype=np.int64)
    skipped_counts = cuda.device_array(1, dtype=np.int64)
    _carrier_side_count_kernel[1, 1](
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        carrier_order,
        carrier_run_start,
        carrier_run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        group_counts,
        point_row_counts,
        skipped_counts,
    )
    offsets = cuda.device_array(1, dtype=np.int64)
    total_out = cuda.device_array(1, dtype=np.int64)
    _exclusive_prefix_sum_i64_single_kernel[1, 1](group_counts, offsets, total_out)
    out_group_length = cuda.device_array(2, dtype=np.int64)
    out_label_a = cuda.device_array(2, dtype=np.int64)
    out_label_b = cuda.device_array(2, dtype=np.int64)
    _carrier_side_fill_kernel[1, 1](
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        carrier_order,
        carrier_run_start,
        carrier_run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        offsets,
        out_group_length,
        out_label_a,
        out_label_b,
    )
    atomic_length = cuda.device_array(2, dtype=np.int64)
    atomic_a = cuda.device_array(2, dtype=np.int64)
    atomic_b = cuda.device_array(2, dtype=np.int64)
    atomic_counters = cuda.to_device(np.zeros(3, dtype=np.int64))
    atomic_overflow = cuda.to_device(np.zeros(1, dtype=np.int64))
    _carrier_side_atomic_append_kernel[1, 1](
        chain_offsets,
        chain_point_counts,
        chain_left_faces,
        chain_right_faces,
        point_x,
        point_y,
        carrier_order,
        carrier_run_start,
        carrier_run_end,
        display_x,
        display_y,
        point_faces,
        midpoint_faces,
        atomic_length,
        atomic_a,
        atomic_b,
        atomic_counters,
        2,
        atomic_overflow,
    )
    combined_length = cuda.device_array(2, dtype=np.int64)
    combined_a = cuda.device_array(2, dtype=np.int64)
    combined_b = cuda.device_array(2, dtype=np.int64)
    _copy_carrier_side_to_combined_kernel[1, 1](
        out_group_length,
        out_label_a,
        out_label_b,
        1,
        combined_length,
        combined_a,
        combined_b,
        0,
    )
    _fill_carrier_sentinel_kernel[1, 1](
        combined_length,
        combined_a,
        combined_b,
        1,
        1,
        int(np.iinfo(np.int64).max),
    )
    descriptor_pair_count_projected_device(
        {
            "group_length_device": combined_length,
            "label_a_device": combined_a,
            "label_b_device": combined_b,
            "group_count": 1,
            "point_row_count": 2,
            "skipped_group_count": 0,
            "padded_group_count": 2,
        }
    )
    cuda.synchronize()


def _generic_lsi_tiny_prewarm() -> dict[str, object]:
    right = base.pack_segments(
        ids=np.asarray([1], dtype=np.int64),
        x0=np.asarray([0.0], dtype=np.float64),
        y0=np.asarray([1.0], dtype=np.float64),
        x1=np.asarray([1.0], dtype=np.float64),
        y1=np.asarray([0.0], dtype=np.float64),
    )
    left = base.pack_segments(
        ids=np.asarray([2], dtype=np.int64),
        x0=np.asarray([0.0], dtype=np.float64),
        y0=np.asarray([0.0], dtype=np.float64),
        x1=np.asarray([1.0], dtype=np.float64),
        y1=np.asarray([1.0], dtype=np.float64),
    )
    start = time.perf_counter()
    with base.prepare_planar_map_lsi_2d_optix(right) as lsi:
        with lsi.prepare_query(left) as query:
            columns = query.run_bounded_pair_id_device_columns(max_rows=8)
            try:
                row_count = int(columns.row_count)
                traversal_seconds = float(columns.traversal_seconds)
            finally:
                columns.close()
            timings = lsi.prepared.last_extended_phase_timings() or {}
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.generic_lsi_tiny_prewarm.v1",
        "elapsed_sec": time.perf_counter() - start,
        "row_count": row_count,
        "traversal_seconds": traversal_seconds,
        "extended_timings": timings,
        "claim_boundary": {
            "generic_lsi_primitive": True,
            "prewarm_time_excluded_from_writer_free_hot": True,
            "cold_cli_one_shot_speedup_claim_authorized": False,
            "true_query_many_measurement": False,
            "ten_x_claim_authorized": False,
        },
    }


def _slice_dataset_by_chain_range(dataset, *, start_chain: int, end_chain: int):
    start_chain = int(start_chain)
    end_chain = int(end_chain)
    if start_chain < 0 or end_chain > int(dataset.chain_count) or start_chain >= end_chain:
        raise ValueError(
            f"invalid chain range [{start_chain}, {end_chain}) for dataset with "
            f"{dataset.chain_count} chains"
        )
    chain_point_counts = np.asarray(dataset.chain_point_counts[start_chain:end_chain], dtype=np.int64).copy()
    chain_count = int(chain_point_counts.size)
    point_start = int(dataset.chain_offsets[start_chain])
    last_chain = end_chain - 1
    point_end = int(dataset.chain_offsets[last_chain] + dataset.chain_point_counts[last_chain])
    point_x = np.asarray(dataset.point_x[point_start:point_end], dtype=np.float64).copy()
    point_y = np.asarray(dataset.point_y[point_start:point_end], dtype=np.float64).copy()
    if chain_count:
        chain_offsets = np.empty(chain_count, dtype=np.int64)
        chain_offsets[0] = 0
        if chain_count > 1:
            chain_offsets[1:] = np.cumsum(chain_point_counts[:-1], dtype=np.int64)
    else:
        chain_offsets = np.asarray([], dtype=np.int64)
    edge_start = int(dataset.chain_offsets[start_chain] - start_chain)
    edge_count = int(np.sum(np.maximum(chain_point_counts - 1, 0), dtype=np.int64))
    edge_end = edge_start + edge_count
    x0 = np.asarray(dataset.x0[edge_start:edge_end], dtype=np.float64).copy()
    y0 = np.asarray(dataset.y0[edge_start:edge_end], dtype=np.float64).copy()
    x1 = np.asarray(dataset.x1[edge_start:edge_end], dtype=np.float64).copy()
    y1 = np.asarray(dataset.y1[edge_start:edge_end], dtype=np.float64).copy()
    left_face_ids = np.asarray(dataset.left_face_ids[edge_start:edge_end], dtype=np.uint32).copy()
    right_face_ids = np.asarray(dataset.right_face_ids[edge_start:edge_end], dtype=np.uint32).copy()
    seg_ids = np.arange(1, edge_count + 1, dtype=np.int64)
    point_ids = np.arange(1, point_x.size + 1, dtype=np.int64)
    lsi_segments = base.pack_segments(ids=seg_ids, x0=x0, y0=y0, x1=x1, y1=y1)
    cdb_segments = base.pack_cdb_segments_from_arrays(seg_ids, x0, y0, x1, y1, left_face_ids, right_face_ids)
    points = base.pack_points(ids=point_ids, x=point_x, y=point_y, dimension=2)
    name = f"{dataset.name}_chains_{start_chain}_{end_chain}"
    return base.DatasetArrays(
        path=f"{dataset.path}#chains={start_chain}:{end_chain}",
        name=name,
        chain_count=chain_count,
        point_count=int(point_x.size),
        edge_count=edge_count,
        min_x=float(np.min(point_x)) if point_x.size else float("nan"),
        max_x=float(np.max(point_x)) if point_x.size else float("nan"),
        min_y=float(np.min(point_y)) if point_y.size else float("nan"),
        max_y=float(np.max(point_y)) if point_y.size else float("nan"),
        chain_offsets=chain_offsets,
        chain_point_counts=chain_point_counts,
        chain_left_faces=np.asarray(dataset.chain_left_faces[start_chain:end_chain], dtype=np.uint32).copy(),
        chain_right_faces=np.asarray(dataset.chain_right_faces[start_chain:end_chain], dtype=np.uint32).copy(),
        point_x=point_x,
        point_y=point_y,
        seg_ids=seg_ids,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        left_face_ids=left_face_ids,
        right_face_ids=right_face_ids,
        lsi_segments=lsi_segments,
        cdb_segments=cdb_segments,
        points=points,
    )


def _split_dataset_by_chain_batches(dataset, batch_count: int):
    batch_count = int(batch_count)
    if batch_count <= 0:
        return []
    chain_count = int(dataset.chain_count)
    if batch_count > chain_count:
        raise ValueError(
            f"--query-chain-batches={batch_count} exceeds left chain count {chain_count}"
        )
    boundaries = np.linspace(0, chain_count, batch_count + 1, dtype=np.int64)
    batches = []
    for index in range(batch_count):
        start_chain = int(boundaries[index])
        end_chain = int(boundaries[index + 1])
        if start_chain == end_chain:
            continue
        batches.append(
            {
                "index": index,
                "start_chain": start_chain,
                "end_chain": end_chain,
                "dataset": _slice_dataset_by_chain_range(
                    dataset,
                    start_chain=start_chain,
                    end_chain=end_chain,
                ),
            }
        )
    return batches


def _trunc_div2_array(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.int64)
    return np.where(values >= 0, values // 2, -((-values) // 2)).astype(np.int64, copy=False)


def numeric_xsect_columns_from_pairs(pairs, left, right, *, scale_bounds):
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
    scaled_x = base._scale_array(world_x, rx_scale, deltax).astype(np.int64, copy=False)
    scaled_y = base._scale_array(world_y, ry_scale, deltay).astype(np.int64, copy=False)

    return {
        "eid0": left_index.astype(np.int64, copy=False),
        "eid1": right_index.astype(np.int64, copy=False),
        "display_x": np.asarray(world_x, dtype=np.float64),
        "display_y": np.asarray(world_y, dtype=np.float64),
        "scaled_x": scaled_x,
        "scaled_y": scaled_y,
    }


def _cuda_is_available() -> bool:
    if not NUMBA_AVAILABLE or cuda is None:
        return False
    try:
        if cuda.is_available():
            return True
        # Some Numba/CUDA toolkit combinations can detect and use the driver
        # even when the conservative availability predicate returns False.
        # Treat a successfully-created context as the real execution gate.
        cuda.current_context()
        return True
    except Exception:
        return False


def _copy_dataset_segment_arrays_to_device(dataset):
    return {
        "x0": cuda.to_device(np.ascontiguousarray(dataset.x0, dtype=np.float64)),
        "y0": cuda.to_device(np.ascontiguousarray(dataset.y0, dtype=np.float64)),
        "x1": cuda.to_device(np.ascontiguousarray(dataset.x1, dtype=np.float64)),
        "y1": cuda.to_device(np.ascontiguousarray(dataset.y1, dtype=np.float64)),
    }


def _numeric_xsect_columns_from_device_pair_arrays(
    pair_left,
    pair_right,
    left,
    right,
    *,
    scale_bounds,
    left_device=None,
    right_device=None,
):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for --device-columnar")
    count = int(pair_left.shape[0])
    if left_device is None:
        left_device = _copy_dataset_segment_arrays_to_device(left)
    if right_device is None:
        right_device = _copy_dataset_segment_arrays_to_device(right)
    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)

    out_eid0 = cuda.device_array(count, dtype=np.int64)
    out_eid1 = cuda.device_array(count, dtype=np.int64)
    out_display_x = cuda.device_array(count, dtype=np.float64)
    out_display_y = cuda.device_array(count, dtype=np.float64)
    out_scaled_x = cuda.device_array(count, dtype=np.int64)
    out_scaled_y = cuda.device_array(count, dtype=np.int64)
    threads = 256
    blocks = max(1, (count + threads - 1) // threads)
    _numeric_xsect_columns_kernel[blocks, threads](
        pair_left,
        pair_right,
        left_device["x0"],
        left_device["y0"],
        left_device["x1"],
        left_device["y1"],
        right_device["x0"],
        right_device["y0"],
        right_device["x1"],
        right_device["y1"],
        float(rx_scale),
        float(ry_scale),
        float(deltax),
        float(deltay),
        out_eid0,
        out_eid1,
        out_display_x,
        out_display_y,
        out_scaled_x,
        out_scaled_y,
    )
    cuda.synchronize()
    device = {
        "eid0": out_eid0,
        "eid1": out_eid1,
        "display_x": out_display_x,
        "display_y": out_display_y,
        "scaled_x": out_scaled_x,
        "scaled_y": out_scaled_y,
    }
    return {
        "eid0": out_eid0.copy_to_host(),
        "eid1": out_eid1.copy_to_host(),
        "display_x": out_display_x.copy_to_host(),
        "display_y": out_display_y.copy_to_host(),
        "scaled_x": out_scaled_x.copy_to_host(),
        "scaled_y": out_scaled_y.copy_to_host(),
        "_device": device,
        "_device_resident_projection": True,
    }


def numeric_xsect_columns_from_pairs_numba_device(pairs, left, right, *, scale_bounds, left_device=None, right_device=None):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for --device-columnar")
    pairs = np.asarray(pairs, dtype=np.uint32).reshape((-1, 2))
    pair_left = cuda.to_device(pairs[:, 0].astype(np.int64, copy=False))
    pair_right = cuda.to_device(pairs[:, 1].astype(np.int64, copy=False))
    result = _numeric_xsect_columns_from_device_pair_arrays(
        pair_left,
        pair_right,
        left,
        right,
        scale_bounds=scale_bounds,
        left_device=left_device,
        right_device=right_device,
    )
    result["_pair_input_device_resident"] = False
    result["_pair_host_to_device_copy_used"] = True
    return result


def numeric_xsect_columns_from_pair_device_columns_numba_device(
    device_columns,
    left,
    right,
    *,
    scale_bounds,
    left_device=None,
    right_device=None,
):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for --device-columnar")
    row_buffer = device_column_row_buffer_from_native_pair_columns(device_columns)
    pair_left = cuda.as_cuda_array(row_buffer.columns["left_id"])
    pair_right = cuda.as_cuda_array(row_buffer.columns["right_id"])
    result = _numeric_xsect_columns_from_device_pair_arrays(
        pair_left,
        pair_right,
        left,
        right,
        scale_bounds=scale_bounds,
        left_device=left_device,
        right_device=right_device,
    )
    row_buffer_metadata = row_buffer.to_metadata()
    result["_pair_input_device_resident"] = bool(row_buffer.device_resident_candidate)
    result["_pair_host_to_device_copy_used"] = bool(row_buffer.materializes_host_rows_for_bridge)
    result["_pair_row_buffer"] = row_buffer_metadata
    return result


def _next_power_of_two(value: int) -> int:
    power = 1
    while power < int(value):
        power <<= 1
    return power


def _bitonic_sort_device(edge_key, dist_key, tie_key, order):
    count = int(edge_key.shape[0])
    if count <= 1:
        return
    threads = 256
    blocks = max(1, (count + threads - 1) // threads)
    k = 2
    while k <= count:
        j = k >> 1
        while j > 0:
            _bitonic_sort_step[blocks, threads](edge_key, dist_key, tie_key, order, j, k)
            j >>= 1
        k <<= 1
    cuda.synchronize()


def _compute_run_bounds_device(sorted_edges_device, valid_count: int, edge_count: int):
    run_start = cuda.device_array(int(edge_count), dtype=np.int64)
    run_end = cuda.device_array(int(edge_count), dtype=np.int64)
    threads = 256
    fill_blocks = max(1, (int(edge_count) + threads - 1) // threads)
    _fill_i64_kernel[fill_blocks, threads](run_start, -1)
    _fill_i64_kernel[fill_blocks, threads](run_end, -1)
    if int(valid_count) > 0:
        blocks = max(1, (int(valid_count) + threads - 1) // threads)
        _run_bounds_from_sorted_edges_kernel[blocks, threads](
            sorted_edges_device,
            run_start,
            run_end,
            int(valid_count),
        )
    cuda.synchronize()
    return run_start, run_end


def _run_public_device_order_by_native_lexsort(
    edge_key,
    dist_key,
    tie_key,
    order_key,
    *,
    count: int,
    producer: str,
):
    valid_count = int(count)
    key_buffer = device_column_buffer(
        {
            "edge_key": edge_key[:valid_count],
            "dist_key": dist_key[:valid_count],
            "tie_key": tie_key[:valid_count],
            "order_key": order_key[:valid_count],
        },
        row_count=valid_count,
        producer=producer,
        producer_consumer_stream_ordering="same_stream",
        native_device_column_output_proven_on_hardware=True,
    )
    result = device_order_by(
        key_buffer,
        keys=("edge_key", "dist_key", "tie_key", "order_key"),
        backend="native_cuda",
    )
    metadata = dict(result.metadata)
    metadata["public_device_order_by_used"] = True
    metadata["public_device_order_by_contract_version"] = result.metadata.get(
        "public_device_order_by_contract_version"
    )
    return metadata


def sort_xsect_indices_for_map_numba_device(
    columns,
    dataset,
    map_index: int,
    scale_bounds,
    *,
    with_device_run_bounds: bool = False,
    with_host_run_tables: bool = True,
    native_lexsort: bool = False,
    phase_seconds=None,
    phase_prefix: str | None = None,
    segment_device_arrays=None,
):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for --device-columnar")
    if "_device" not in columns:
        raise RuntimeError("device sort requires device-resident numeric xsect columns")

    device_columns = columns["_device"]
    edge_device = device_columns["eid0"] if map_index == 0 else device_columns["eid1"]
    tie_device = device_columns["eid1"] if map_index == 0 else device_columns["eid0"]
    valid_count = int(edge_device.shape[0])
    padded_count = _next_power_of_two(max(1, valid_count))
    out_edge = cuda.device_array(padded_count, dtype=np.int64)
    out_tie = cuda.device_array(padded_count, dtype=np.int64)
    out_dist = cuda.device_array(padded_count, dtype=np.float64)
    out_order = cuda.device_array(padded_count, dtype=np.int64)
    if segment_device_arrays is None:
        segment_upload_start = time.perf_counter()
        dataset_x0 = cuda.to_device(np.ascontiguousarray(dataset.x0, dtype=np.float64))
        dataset_y0 = cuda.to_device(np.ascontiguousarray(dataset.y0, dtype=np.float64))
        _record_elapsed(
            segment_upload_start,
            phase_seconds,
            f"{phase_prefix}_segment_xy_to_device_sec" if phase_prefix else None,
        )
    else:
        dataset_x0 = segment_device_arrays["x0"]
        dataset_y0 = segment_device_arrays["y0"]
        if phase_seconds is not None and phase_prefix:
            phase_seconds[f"{phase_prefix}_segment_xy_reused"] = 1.0
    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    sentinel = np.iinfo(np.int64).max
    threads = 256
    blocks = max(1, (padded_count + threads - 1) // threads)
    key_start = time.perf_counter()
    _sort_key_kernel[blocks, threads](
        edge_device,
        tie_device,
        device_columns["scaled_x"],
        device_columns["scaled_y"],
        dataset_x0,
        dataset_y0,
        float(rx_scale),
        float(ry_scale),
        float(deltax),
        float(deltay),
        out_edge,
        out_tie,
        out_dist,
        out_order,
        valid_count,
        int(sentinel),
    )
    cuda.synchronize()
    _record_elapsed(key_start, phase_seconds, f"{phase_prefix}_key_kernel_sec" if phase_prefix else None)
    sort_backend = "numba_bitonic"
    native_sort_metadata = None
    if native_lexsort:
        native_sort_count = int(valid_count)
        native_sort_start = time.perf_counter()
        native_sort_metadata = _run_public_device_order_by_native_lexsort(
            out_edge,
            out_dist,
            out_tie,
            out_order,
            count=native_sort_count,
            producer=f"section57_sort_map{map_index}_keys",
        )
        _record_elapsed(
            native_sort_start,
            phase_seconds,
            f"{phase_prefix}_native_lexsort_sec" if phase_prefix else None,
        )
        sort_backend = str(native_sort_metadata.get("backend", "native_thrust_lexsort_i64_f64_i64_i64"))
    else:
        bitonic_sort_start = time.perf_counter()
        _bitonic_sort_device(out_edge, out_dist, out_tie, out_order)
        _record_elapsed(
            bitonic_sort_start,
            phase_seconds,
            f"{phase_prefix}_bitonic_sort_sec" if phase_prefix else None,
        )
    copy_order_start = time.perf_counter()
    order = out_order.copy_to_host()[:valid_count].astype(np.int64, copy=False)
    _record_elapsed(
        copy_order_start,
        phase_seconds,
        f"{phase_prefix}_copy_order_to_host_sec" if phase_prefix else None,
    )
    copy_edge_start = time.perf_counter()
    sorted_edges = out_edge.copy_to_host()[:valid_count].astype(np.int64, copy=False)
    _record_elapsed(
        copy_edge_start,
        phase_seconds,
        f"{phase_prefix}_copy_edges_to_host_sec" if phase_prefix else None,
    )
    device_view = {
        "order": out_order,
        "edge_ids": out_edge,
        "valid_count": int(valid_count),
        "padded_count": int(padded_count),
    }
    if with_device_run_bounds:
        device_bounds_start = time.perf_counter()
        run_start_device, run_end_device = _compute_run_bounds_device(out_edge, valid_count, dataset.edge_count)
        _record_elapsed(
            device_bounds_start,
            phase_seconds,
            f"{phase_prefix}_device_run_bounds_sec" if phase_prefix else None,
        )
        device_view["run_start"] = run_start_device
        device_view["run_end"] = run_end_device
    if with_host_run_tables:
        host_run_start = time.perf_counter()
        run_start = _run_start_table(sorted_edges, dataset.edge_count)
        _record_elapsed(
            host_run_start,
            phase_seconds,
            f"{phase_prefix}_host_run_start_table_sec" if phase_prefix else None,
        )
        host_run_end = time.perf_counter()
        run_end = _run_end_table(sorted_edges, dataset.edge_count)
        _record_elapsed(
            host_run_end,
            phase_seconds,
            f"{phase_prefix}_host_run_end_table_sec" if phase_prefix else None,
        )
    else:
        run_start = np.asarray([], dtype=np.int64)
        run_end = np.asarray([], dtype=np.int64)
        if phase_seconds is not None and phase_prefix:
            phase_seconds[f"{phase_prefix}_host_run_tables_skipped"] = 1.0
    return {
        "order": order,
        "edge_ids": sorted_edges,
        "run_start": run_start,
        "run_end": run_end,
        "device_sort_used": True,
        "device_sort_backend": sort_backend,
        "device_sort_padded_count": int(padded_count),
        "device_sort_native_count": int(valid_count) if native_lexsort else None,
        "native_sort_metadata": native_sort_metadata,
        "_device": device_view,
    }


def sort_xsect_indices_for_map(columns, dataset, map_index: int, scale_bounds):
    edge_ids = columns["eid0"] if map_index == 0 else columns["eid1"]
    tie_ids = columns["eid1"] if map_index == 0 else columns["eid0"]
    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    start_sx = base._scale_array(dataset.x0[edge_ids], rx_scale, deltax).astype(np.int64, copy=False)
    start_sy = base._scale_array(dataset.y0[edge_ids], ry_scale, deltay).astype(np.int64, copy=False)
    # Scaled coordinates may be around 1e13; squaring them in int64 silently
    # overflows and changes the author/object-route order.  Use extended
    # floating precision for the ordering distance while keeping ids integer.
    dx = (columns["scaled_x"] - start_sx).astype(np.longdouble, copy=False)
    dy = (columns["scaled_y"] - start_sy).astype(np.longdouble, copy=False)
    dist = dx * dx + dy * dy
    # Python's per-edge ``list.sort(key=(dist, tie))`` is stable. Preserve that
    # final tie behavior explicitly so the columnar route remains semantically
    # equivalent to the object route on degenerate equal-distance/equal-tie
    # events.
    original_index = np.arange(edge_ids.shape[0], dtype=np.int64)
    order = np.lexsort((original_index, tie_ids, dist, edge_ids)).astype(np.int64, copy=False)
    sorted_edges = edge_ids[order]
    return {
        "order": order,
        "edge_ids": sorted_edges,
        "run_start": _run_start_table(sorted_edges, dataset.edge_count),
        "run_end": _run_end_table(sorted_edges, dataset.edge_count),
    }


def _run_start_table(sorted_edges: np.ndarray, edge_count: int) -> np.ndarray:
    starts = np.full(int(edge_count), -1, dtype=np.int64)
    if sorted_edges.size == 0:
        return starts
    change = np.empty(sorted_edges.size, dtype=np.bool_)
    change[0] = True
    change[1:] = sorted_edges[1:] != sorted_edges[:-1]
    positions = np.nonzero(change)[0]
    starts[sorted_edges[positions].astype(np.int64)] = positions.astype(np.int64)
    return starts


def _run_end_table(sorted_edges: np.ndarray, edge_count: int) -> np.ndarray:
    ends = np.full(int(edge_count), -1, dtype=np.int64)
    if sorted_edges.size == 0:
        return ends
    change = np.empty(sorted_edges.size, dtype=np.bool_)
    change[:-1] = sorted_edges[1:] != sorted_edges[:-1]
    change[-1] = True
    positions = np.nonzero(change)[0]
    ends[sorted_edges[positions].astype(np.int64)] = (positions + 1).astype(np.int64)
    return ends


def _record_elapsed(start: float, phase_seconds: dict[str, float] | None, key: str | None) -> None:
    if phase_seconds is not None and key:
        phase_seconds[key] = float(time.perf_counter() - start)


def _scatter_midpoint_faces_device(owners: np.ndarray, faces_device, out_device, count: int) -> None:
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for device midpoint face scatter")
    if faces_device is None:
        raise RuntimeError("device midpoint face scatter requires face-id device columns")
    count = int(count)
    if count <= 0:
        return
    owners_device = (
        owners
        if hasattr(owners, "__cuda_array_interface__")
        else cuda.to_device(np.ascontiguousarray(owners[:count], dtype=np.int64))
    )
    threads = 256
    blocks = max(1, (count + threads - 1) // threads)
    _scatter_u32_by_i64_index_kernel[blocks, threads](owners_device, faces_device, out_device, count)
    cuda.synchronize()


def _cuda_device_pointer(device_array) -> int:
    return int(device_array.device_ctypes_pointer.value)


def midpoint_query_points_device(locator, columns, sorted_view, side_id: int, *, scale_bounds, phase_seconds=None, phase_prefix=None):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for device midpoint query points")
    if "_device" not in columns or "_device" not in sorted_view:
        raise RuntimeError("device midpoint query points require device columns and device sorted views")
    valid_count = int(sorted_view["_device"]["valid_count"])
    capacity = max(1, valid_count - 1)
    device_points = cuda.device_array(capacity, dtype=DEVICE_QUERY_POINT_DTYPE)
    owners_device = cuda.device_array(capacity, dtype=np.int64)
    count_device = cuda.to_device(np.zeros(1, dtype=np.int64))
    *_, rrx, rry, ddeltax, ddeltay = base._rayjoin_scaling_constants(scale_bounds)
    start = time.perf_counter()
    threads = 256
    blocks = max(1, (max(1, valid_count - 1) + threads - 1) // threads)
    _midpoint_device_query_points_kernel[blocks, threads](
        sorted_view["_device"]["order"],
        sorted_view["_device"]["edge_ids"],
        columns["_device"]["scaled_x"],
        columns["_device"]["scaled_y"],
        int(valid_count),
        float(rrx),
        float(rry),
        float(ddeltax),
        float(ddeltay),
        device_points,
        owners_device,
        count_device,
    )
    cuda.synchronize()
    _record_elapsed(
        start,
        phase_seconds,
        f"{phase_prefix}_device_query_points_kernel_sec" if phase_prefix else None,
    )
    count = int(count_device.copy_to_host()[0])
    start = time.perf_counter()
    prepared_points = locator.prepare_device_query_points(
        _cuda_device_pointer(device_points),
        count,
        owner=device_points,
    )
    _record_elapsed(
        start,
        phase_seconds,
        f"{phase_prefix}_prepare_device_query_points_sec" if phase_prefix else None,
    )
    return prepared_points, owners_device, count, device_points


def midpoint_points_columnar(
    columns,
    sorted_view,
    side_id: int,
    *,
    scale_bounds,
    phase_seconds: dict[str, float] | None = None,
    phase_prefix: str | None = None,
    fast_scaled_point_pack: bool = False,
):
    order = sorted_view["order"]
    edges = sorted_view["edge_ids"]
    if order.size <= 1:
        return base.pack_rayjoin_cdb_scaled_points(
            ids=np.asarray([], dtype=np.int64),
            x=np.asarray([], dtype=np.float64),
            y=np.asarray([], dtype=np.float64),
            sx=np.asarray([], dtype=np.int64),
            sy=np.asarray([], dtype=np.int64),
        ), np.asarray([], dtype=np.int64), 0

    start = time.perf_counter()
    same_edge = edges[1:] == edges[:-1]
    left_owner_positions = np.nonzero(same_edge)[0]
    owners = order[left_owner_positions]
    right_neighbors = order[left_owner_positions + 1]
    _record_elapsed(
        start,
        phase_seconds,
        f"{phase_prefix}_adjacent_owner_scan_sec" if phase_prefix else None,
    )

    start = time.perf_counter()
    sx = _trunc_div2_array(columns["scaled_x"][owners] + columns["scaled_x"][right_neighbors])
    sy = _trunc_div2_array(columns["scaled_y"][owners] + columns["scaled_y"][right_neighbors])
    _record_elapsed(
        start,
        phase_seconds,
        f"{phase_prefix}_scaled_midpoint_arrays_sec" if phase_prefix else None,
    )

    start = time.perf_counter()
    *_, rrx, rry, ddeltax, ddeltay = base._rayjoin_scaling_constants(scale_bounds)
    mx = sx.astype(np.float64) * float(rrx) + float(ddeltax)
    my = sy.astype(np.float64) * float(rry) + float(ddeltay)
    finite = np.isfinite(mx) & np.isfinite(my)
    if not np.all(finite):
        owners = owners[finite]
        sx = sx[finite]
        sy = sy[finite]
        mx = mx[finite]
        my = my[finite]
    _record_elapsed(
        start,
        phase_seconds,
        f"{phase_prefix}_world_and_finite_filter_sec" if phase_prefix else None,
    )

    start = time.perf_counter()
    ids = np.arange(1, owners.size + 1, dtype=np.int64)
    packer = pack_rayjoin_cdb_scaled_points_fast_host if fast_scaled_point_pack else base.pack_rayjoin_cdb_scaled_points
    packed = packer(ids=ids, x=mx, y=my, sx=sx, sy=sy)
    _record_elapsed(
        start,
        phase_seconds,
        f"{phase_prefix}_pack_scaled_points_sec" if phase_prefix else None,
    )
    return packed, owners.astype(np.int64, copy=False), int(owners.size)


def build_projected_descriptor_carrier_columnar(datasets, columns, sorted_views, point_faces, midpoint_faces):
    group_offset = []
    group_length = []
    label_a = []
    label_b = []
    skipped_group_count = 0
    projected_point_payload_rows = 0

    def flush(display_points, left_label, right_label, other_label):
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
        view = sorted_views[side_id]
        order = view["order"]
        starts = view["run_start"]
        ends = view["run_end"]
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

                run_start = int(starts[edge_id]) if edge_id < starts.size else -1
                run_end = int(ends[edge_id]) if edge_id < ends.size else -1
                if run_start >= 0 and run_end > run_start:
                    first = int(order[run_start])
                    display_points.append((float(columns["display_x"][first]), float(columns["display_y"][first])))
                    for sorted_pos in range(run_start, run_end - 1):
                        xsect_index = int(order[sorted_pos])
                        next_index = int(order[sorted_pos + 1])
                        flush(display_points, left_label, right_label, other_label)
                        other_label = int(midpoint_faces[side_id][xsect_index])
                        display_points.append(
                            (float(columns["display_x"][xsect_index]), float(columns["display_y"][xsect_index]))
                        )
                        display_points.append(
                            (float(columns["display_x"][next_index]), float(columns["display_y"][next_index]))
                        )
                    flush(display_points, left_label, right_label, other_label)
                    last = int(order[run_end - 1])
                    display_points.append((float(columns["display_x"][last]), float(columns["display_y"][last])))
                edge_id += 1

            flush(display_points, left_label, right_label, other_label)

    carrier = {
        "group_offset": np.asarray(group_offset, dtype=np.int64),
        "group_length": np.asarray(group_length, dtype=np.int64),
        "label_a": np.asarray(label_a, dtype=np.int64),
        "label_b": np.asarray(label_b, dtype=np.int64),
    }
    stats = {
        "schema": "rtdl.paper_reproduction.rayjoin.section57_columnar_binary_carrier.v1",
        "group_count": int(carrier["group_offset"].size),
        "point_row_count": int(carrier["group_length"].sum()),
        "skipped_group_count": int(skipped_group_count),
        "full_geometry_payload_columns_materialized": False,
        "transient_display_point_tuples_used_for_dedupe_count": True,
        "projected_out_columns": ("x", "y", "alt_label", "source_side_id", "source_element_id"),
        "projection_pushdown": True,
        "columnar_xsect_arrays": True,
    }
    return carrier, stats


def build_projected_descriptor_carrier_columnar_compiled(
    datasets,
    columns,
    sorted_views,
    point_faces,
    midpoint_faces,
    *,
    phase_seconds=None,
    phase_prefix="grouped_compiled_carrier",
    side_order=(0, 1),
):
    if not NUMBA_AVAILABLE:
        raise RuntimeError("Numba is required for --compiled-group")
    parts = []
    side_work_metrics = {}
    total_skipped = 0
    total_point_rows = 0
    for side_id in side_order:
        dataset = datasets[side_id]
        side_start = time.perf_counter()
        prepare_start = time.perf_counter()
        view = sorted_views[side_id]
        max_groups = int(dataset.chain_count) + int(view["order"].size)
        lengths = np.empty(max_groups, dtype=np.int64)
        label_a = np.empty(max_groups, dtype=np.int64)
        label_b = np.empty(max_groups, dtype=np.int64)
        work_metrics = np.zeros(len(GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS), dtype=np.int64)
        chain_offsets = np.asarray(dataset.chain_offsets, dtype=np.int64)
        chain_point_counts = np.asarray(dataset.chain_point_counts, dtype=np.int64)
        chain_left_faces = np.asarray(dataset.chain_left_faces, dtype=np.int64)
        chain_right_faces = np.asarray(dataset.chain_right_faces, dtype=np.int64)
        point_x = np.asarray(dataset.point_x, dtype=np.float64)
        point_y = np.asarray(dataset.point_y, dtype=np.float64)
        order = np.asarray(view["order"], dtype=np.int64)
        run_start = np.asarray(view["run_start"], dtype=np.int64)
        run_end = np.asarray(view["run_end"], dtype=np.int64)
        display_x = np.asarray(columns["display_x"], dtype=np.float64)
        display_y = np.asarray(columns["display_y"], dtype=np.float64)
        point_faces_side = np.asarray(point_faces[side_id], dtype=np.uint32)
        midpoint_faces_side = np.asarray(midpoint_faces[side_id], dtype=np.uint32)
        _record_elapsed(
            prepare_start,
            phase_seconds,
            f"{phase_prefix}_side{side_id}_prepare_inputs_sec",
        )

        builder_start = time.perf_counter()
        out_count, skipped, point_rows = _build_projected_descriptor_side_numba(
            chain_offsets,
            chain_point_counts,
            chain_left_faces,
            chain_right_faces,
            point_x,
            point_y,
            order,
            run_start,
            run_end,
            display_x,
            display_y,
            point_faces_side,
            midpoint_faces_side,
            lengths,
            label_a,
            label_b,
            work_metrics,
        )
        _record_elapsed(
            builder_start,
            phase_seconds,
            f"{phase_prefix}_side{side_id}_numba_builder_sec",
        )
        side_work_metrics[f"side{side_id}"] = _grouped_carrier_side_work_metrics(work_metrics)

        slice_start = time.perf_counter()
        parts.append((lengths[:out_count].copy(), label_a[:out_count].copy(), label_b[:out_count].copy()))
        _record_elapsed(
            slice_start,
            phase_seconds,
            f"{phase_prefix}_side{side_id}_slice_copy_sec",
        )
        _record_elapsed(
            side_start,
            phase_seconds,
            f"{phase_prefix}_side{side_id}_total_sec",
        )
        total_skipped += int(skipped)
        total_point_rows += int(point_rows)

    concat_start = time.perf_counter()
    group_length = np.concatenate([part[0] for part in parts]) if parts else np.asarray([], dtype=np.int64)
    label_a = np.concatenate([part[1] for part in parts]) if parts else np.asarray([], dtype=np.int64)
    label_b = np.concatenate([part[2] for part in parts]) if parts else np.asarray([], dtype=np.int64)
    _record_elapsed(
        concat_start,
        phase_seconds,
        f"{phase_prefix}_concatenate_sec",
    )

    offset_start = time.perf_counter()
    if group_length.size:
        group_offset = np.empty(group_length.size, dtype=np.int64)
        group_offset[0] = 0
        if group_length.size > 1:
            group_offset[1:] = np.cumsum(group_length[:-1], dtype=np.int64)
    else:
        group_offset = np.asarray([], dtype=np.int64)
    _record_elapsed(
        offset_start,
        phase_seconds,
        f"{phase_prefix}_group_offset_cumsum_sec",
    )

    stats_start = time.perf_counter()
    carrier = {
        "group_offset": group_offset,
        "group_length": group_length,
        "label_a": label_a,
        "label_b": label_b,
    }
    stats = {
        "schema": "rtdl.paper_reproduction.rayjoin.section57_columnar_binary_carrier.v1",
        "group_count": int(group_length.size),
        "point_row_count": int(total_point_rows),
        "skipped_group_count": int(total_skipped),
        "side_work_metrics": side_work_metrics,
        "side_work_metrics_total": _sum_grouped_carrier_side_work_metrics(side_work_metrics),
        "full_geometry_payload_columns_materialized": False,
        "transient_display_point_tuples_used_for_dedupe_count": True,
        "projected_out_columns": ("x", "y", "alt_label", "source_side_id", "source_element_id"),
        "projection_pushdown": True,
        "columnar_xsect_arrays": True,
        "compiled_columnar_group_builder": True,
        "compiled_group_execution_mode": "numba_cpu_njit",
        "compiled_group_side_order": tuple(int(side_id) for side_id in side_order),
    }
    _record_elapsed(
        stats_start,
        phase_seconds,
        f"{phase_prefix}_stats_packaging_sec",
    )
    return carrier, stats


def parse_compiled_group_side_order(value: str) -> tuple[int, int]:
    try:
        parts = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise ValueError("--compiled-group-side-order must be either 0,1 or 1,0") from exc
    if parts not in ((0, 1), (1, 0)):
        raise ValueError("--compiled-group-side-order must be either 0,1 or 1,0")
    return parts


def _grouped_carrier_side_work_metrics(metrics):
    return {
        key: int(metrics[index])
        for index, key in enumerate(GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS)
    }


def _sum_grouped_carrier_side_work_metrics(side_metrics):
    totals = {key: 0 for key in GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS}
    for metrics in side_metrics.values():
        for key in GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS:
            totals[key] += int(metrics.get(key, 0))
    return totals


def _copy_dataset_carrier_arrays_to_device(dataset):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for device-resident carrier")
    return {
        "chain_offsets": cuda.to_device(np.ascontiguousarray(dataset.chain_offsets, dtype=np.int64)),
        "chain_point_counts": cuda.to_device(np.ascontiguousarray(dataset.chain_point_counts, dtype=np.int64)),
        "chain_left_faces": cuda.to_device(np.ascontiguousarray(dataset.chain_left_faces, dtype=np.int64)),
        "chain_right_faces": cuda.to_device(np.ascontiguousarray(dataset.chain_right_faces, dtype=np.int64)),
        "point_x": cuda.to_device(np.ascontiguousarray(dataset.point_x, dtype=np.float64)),
        "point_y": cuda.to_device(np.ascontiguousarray(dataset.point_y, dtype=np.float64)),
    }


def _copy_run_bounds_to_device(sorted_view, *, side_id: int, phase_seconds=None, phase_prefix="device_resident_carrier"):
    device_view = sorted_view.get("_device")
    if device_view is None:
        raise RuntimeError("device-resident carrier requires device sorted views")
    if "run_start" in device_view and "run_end" in device_view:
        return device_view["run_start"], device_view["run_end"]
    start = time.perf_counter()
    run_start = cuda.to_device(np.ascontiguousarray(sorted_view["run_start"], dtype=np.int64))
    run_end = cuda.to_device(np.ascontiguousarray(sorted_view["run_end"], dtype=np.int64))
    _record_elapsed(start, phase_seconds, f"{phase_prefix}_side{side_id}_run_bounds_to_device_sec")
    return run_start, run_end


def _bitonic_sort_pairs_device(label_a, label_b, lengths, valid_count: int):
    padded_count = _next_power_of_two(max(1, int(valid_count)))
    if int(label_a.shape[0]) != padded_count:
        raise ValueError("pair sort arrays must already be padded")
    order = cuda.device_array(padded_count, dtype=np.int64)
    threads = 256
    blocks = max(1, (padded_count + threads - 1) // threads)
    _init_order_kernel[blocks, threads](order)
    sentinel_count = padded_count - int(valid_count)
    if sentinel_count > 0:
        _fill_carrier_sentinel_kernel[blocks, threads](
            lengths,
            label_a,
            label_b,
            int(valid_count),
            int(sentinel_count),
            int(np.iinfo(np.int64).max),
        )
    cuda.synchronize()
    k = 2
    while k <= padded_count:
        j = k >> 1
        while j > 0:
            _pair_bitonic_sort_step[blocks, threads](label_a, label_b, lengths, order, j, k)
            j >>= 1
        k <<= 1
    cuda.synchronize()


def descriptor_pair_count_projected_device(carrier):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for device descriptor consumer")
    valid_count = int(carrier["group_count"])
    if valid_count <= 0:
        return {
            "pair_count": 0,
            "total_groups": 0,
            "total_point_rows": 0,
            "top_pairs_by_point_rows": [],
            "partner": "numba_cuda_device_pair_sort_scan",
            "cuda_device_resident_continuation": True,
        }
    carrier_label_a = carrier["label_a_device"]
    carrier_label_b = carrier["label_b_device"]
    carrier_lengths = carrier["group_length_device"]
    threads = 256
    blocks_valid = max(1, (valid_count + threads - 1) // threads)
    out = cuda.device_array(3, dtype=np.int64)
    partner = "native_thrust_lexsort_i64_f64_i64_i64_descriptor_pair_scan"
    fallback_error = None
    native_direct_carrier_prefix = False
    try:
        order = cuda.device_array(valid_count, dtype=np.int64)
        zero_dist = cuda.device_array(valid_count, dtype=np.float64)
        _init_order_kernel[blocks_valid, threads](order)
        _fill_f64_kernel[blocks_valid, threads](zero_dist, 0.0)
        cuda.synchronize()
        _run_public_device_order_by_native_lexsort(
            carrier_label_a,
            zero_dist,
            carrier_label_b,
            order,
            count=valid_count,
            producer="section57_descriptor_pair_keys",
        )
        _reduce_sorted_descriptor_pairs_with_order_single_kernel[1, 1](
            carrier_label_a,
            carrier_label_b,
            carrier_lengths,
            order,
            valid_count,
            out,
        )
        native_direct_carrier_prefix = True
    except RuntimeError as exc:
        fallback_error = str(exc)
        partner = "numba_cuda_device_pair_sort_scan_fallback"
        padded_count = _next_power_of_two(valid_count)
        padded_label_a = cuda.device_array(padded_count, dtype=np.int64)
        padded_label_b = cuda.device_array(padded_count, dtype=np.int64)
        padded_lengths = cuda.device_array(padded_count, dtype=np.int64)
        padded_blocks = max(1, (padded_count + threads - 1) // threads)
        _copy_carrier_side_to_combined_kernel[blocks_valid, threads](
            carrier["group_length_device"],
            carrier["label_a_device"],
            carrier["label_b_device"],
            valid_count,
            padded_lengths,
            padded_label_a,
            padded_label_b,
            0,
        )
        cuda.synchronize()
        _bitonic_sort_pairs_device(padded_label_a, padded_label_b, padded_lengths, valid_count)
        _reduce_sorted_descriptor_pairs_single_kernel[1, 1](
            padded_label_a,
            padded_label_b,
            padded_lengths,
            valid_count,
            out,
        )
    cuda.synchronize()
    host = out.copy_to_host()
    result = {
        "pair_count": int(host[0]),
        "total_groups": int(host[1]),
        "total_point_rows": int(host[2]),
        "top_pairs_by_point_rows": [],
        "partner": partner,
        "cuda_device_resident_continuation": True,
        "native_lexsort_descriptor_pair_scan": fallback_error is None,
        "native_lexsort_direct_carrier_prefix": native_direct_carrier_prefix,
    }
    if fallback_error is not None:
        result["native_lexsort_descriptor_pair_scan_error"] = fallback_error
    return result


def _build_projected_descriptor_carrier_device_side(
    dataset,
    columns,
    sorted_view,
    point_faces_device,
    midpoint_faces_device,
    *,
    side_id: int,
    prepared_dataset_arrays=None,
    phase_seconds=None,
    phase_prefix="device_resident_carrier",
):
    if "_device" not in sorted_view:
        raise RuntimeError("device-resident carrier requires device sorted views")
    if "_device" not in columns:
        raise RuntimeError("device-resident carrier requires device xsect columns")
    if point_faces_device is None or midpoint_faces_device is None:
        raise RuntimeError("device-resident carrier requires point and midpoint face-id device columns")

    if prepared_dataset_arrays is None:
        start = time.perf_counter()
        arrays = _copy_dataset_carrier_arrays_to_device(dataset)
        _record_elapsed(start, phase_seconds, f"{phase_prefix}_side{side_id}_dataset_to_device_sec")
    else:
        arrays = prepared_dataset_arrays
        if phase_seconds is not None:
            phase_seconds.setdefault(f"{phase_prefix}_side{side_id}_dataset_to_device_sec", 0.0)
    run_start_device, run_end_device = _copy_run_bounds_to_device(
        sorted_view,
        side_id=side_id,
        phase_seconds=phase_seconds,
        phase_prefix=phase_prefix,
    )

    count_start = time.perf_counter()
    chain_count = int(dataset.chain_count)
    group_counts = cuda.device_array(chain_count, dtype=np.int64)
    point_row_counts = cuda.device_array(chain_count, dtype=np.int64)
    skipped_counts = cuda.device_array(chain_count, dtype=np.int64)
    threads = 128
    blocks = max(1, (chain_count + threads - 1) // threads)
    _carrier_side_count_kernel[blocks, threads](
        arrays["chain_offsets"],
        arrays["chain_point_counts"],
        arrays["chain_left_faces"],
        arrays["chain_right_faces"],
        arrays["point_x"],
        arrays["point_y"],
        sorted_view["_device"]["order"],
        run_start_device,
        run_end_device,
        columns["_device"]["display_x"],
        columns["_device"]["display_y"],
        point_faces_device,
        midpoint_faces_device,
        group_counts,
        point_row_counts,
        skipped_counts,
    )
    cuda.synchronize()
    _record_elapsed(count_start, phase_seconds, f"{phase_prefix}_side{side_id}_count_kernel_sec")

    prefix_start = time.perf_counter()
    chain_group_offsets = cuda.device_array(chain_count, dtype=np.int64)
    total_group_device = cuda.device_array(1, dtype=np.int64)
    _exclusive_prefix_sum_i64_single_kernel[1, 1](group_counts, chain_group_offsets, total_group_device)
    totals_device = cuda.device_array(2, dtype=np.int64)
    _sum_two_i64_single_kernel[1, 1](point_row_counts, skipped_counts, totals_device)
    cuda.synchronize()
    total_group_count = int(total_group_device.copy_to_host()[0])
    point_rows, skipped = (int(value) for value in totals_device.copy_to_host())
    _record_elapsed(prefix_start, phase_seconds, f"{phase_prefix}_side{side_id}_prefix_sum_sec")

    fill_start = time.perf_counter()
    capacity = max(1, int(dataset.chain_count) + int(sorted_view["order"].size))
    group_length = cuda.device_array(capacity, dtype=np.int64)
    label_a = cuda.device_array(capacity, dtype=np.int64)
    label_b = cuda.device_array(capacity, dtype=np.int64)
    _carrier_side_fill_kernel[blocks, threads](
        arrays["chain_offsets"],
        arrays["chain_point_counts"],
        arrays["chain_left_faces"],
        arrays["chain_right_faces"],
        arrays["point_x"],
        arrays["point_y"],
        sorted_view["_device"]["order"],
        run_start_device,
        run_end_device,
        columns["_device"]["display_x"],
        columns["_device"]["display_y"],
        point_faces_device,
        midpoint_faces_device,
        chain_group_offsets,
        group_length,
        label_a,
        label_b,
    )
    cuda.synchronize()
    _record_elapsed(fill_start, phase_seconds, f"{phase_prefix}_side{side_id}_fill_kernel_sec")
    return {
        "group_length": group_length,
        "label_a": label_a,
        "label_b": label_b,
        "group_count": total_group_count,
        "point_rows": point_rows,
        "skipped": skipped,
        "capacity": int(capacity),
        "owners": arrays,
    }


def _build_projected_descriptor_carrier_device_atomic_append_side(
    dataset,
    columns,
    sorted_view,
    point_faces_device,
    midpoint_faces_device,
    group_length,
    label_a,
    label_b,
    counters,
    overflow,
    *,
    side_id: int,
    prepared_dataset_arrays=None,
    phase_seconds=None,
    phase_prefix="device_resident_carrier",
    stream=None,
    synchronize=True,
):
    if "_device" not in sorted_view:
        raise RuntimeError("device-resident carrier requires device sorted views")
    if "_device" not in columns:
        raise RuntimeError("device-resident carrier requires device xsect columns")
    if point_faces_device is None or midpoint_faces_device is None:
        raise RuntimeError("device-resident carrier requires point and midpoint face-id device columns")

    if prepared_dataset_arrays is None:
        start = time.perf_counter()
        arrays = _copy_dataset_carrier_arrays_to_device(dataset)
        _record_elapsed(start, phase_seconds, f"{phase_prefix}_side{side_id}_dataset_to_device_sec")
    else:
        arrays = prepared_dataset_arrays
        if phase_seconds is not None:
            phase_seconds.setdefault(f"{phase_prefix}_side{side_id}_dataset_to_device_sec", 0.0)
    run_start_device, run_end_device = _copy_run_bounds_to_device(
        sorted_view,
        side_id=side_id,
        phase_seconds=phase_seconds,
        phase_prefix=phase_prefix,
    )

    append_start = time.perf_counter()
    chain_count = int(dataset.chain_count)
    threads = 128
    blocks = max(1, (chain_count + threads - 1) // threads)
    kernel_args = (
        arrays["chain_offsets"],
        arrays["chain_point_counts"],
        arrays["chain_left_faces"],
        arrays["chain_right_faces"],
        arrays["point_x"],
        arrays["point_y"],
        sorted_view["_device"]["order"],
        run_start_device,
        run_end_device,
        columns["_device"]["display_x"],
        columns["_device"]["display_y"],
        point_faces_device,
        midpoint_faces_device,
        group_length,
        label_a,
        label_b,
        counters,
        int(group_length.shape[0]),
        overflow,
    )
    if stream is None:
        _carrier_side_atomic_append_kernel[blocks, threads](*kernel_args)
    else:
        _carrier_side_atomic_append_kernel[blocks, threads, stream](*kernel_args)
    if synchronize:
        if stream is None:
            cuda.synchronize()
        else:
            stream.synchronize()
        _record_elapsed(append_start, phase_seconds, f"{phase_prefix}_side{side_id}_atomic_append_kernel_sec")
    else:
        _record_elapsed(append_start, phase_seconds, f"{phase_prefix}_side{side_id}_atomic_append_launch_sec")
    if phase_seconds is not None:
        phase_seconds[f"{phase_prefix}_side{side_id}_count_kernel_sec"] = 0.0
        phase_seconds[f"{phase_prefix}_side{side_id}_prefix_sum_sec"] = 0.0
        phase_seconds[f"{phase_prefix}_side{side_id}_fill_kernel_sec"] = 0.0
        phase_seconds[f"{phase_prefix}_side{side_id}_atomic_append_used"] = 1.0
    return {"owners": arrays}


def build_projected_descriptor_carrier_columnar_device(
    datasets,
    columns,
    sorted_views,
    point_faces,
    midpoint_faces,
    *,
    prepared_dataset_arrays=None,
    phase_seconds=None,
    phase_prefix="device_resident_carrier",
    concurrent_side_kernels=False,
):
    if not _cuda_is_available():
        raise RuntimeError("Numba CUDA is required for --device-resident-carrier")
    side_parts = []
    prepared_dataset_arrays = prepared_dataset_arrays or (None, None)
    total_capacity = 0
    for side_id, dataset in enumerate(datasets):
        total_capacity += int(dataset.chain_count) + int(sorted_views[side_id]["order"].size)
    capacity = max(1, int(total_capacity))
    group_length = cuda.device_array(capacity, dtype=np.int64)
    label_a = cuda.device_array(capacity, dtype=np.int64)
    label_b = cuda.device_array(capacity, dtype=np.int64)
    counters = cuda.to_device(np.zeros(3, dtype=np.int64))
    overflow = cuda.to_device(np.zeros(1, dtype=np.int64))

    combine_start = time.perf_counter()
    if concurrent_side_kernels and len(datasets) == 2:
        streams = [cuda.stream(), cuda.stream()]
        append_start = time.perf_counter()
        for side_id, dataset in enumerate(datasets):
            side = _build_projected_descriptor_carrier_device_atomic_append_side(
                dataset,
                columns,
                sorted_views[side_id],
                _point_face_device(point_faces[side_id]),
                midpoint_faces[side_id].get("device") if isinstance(midpoint_faces[side_id], dict) else None,
                group_length,
                label_a,
                label_b,
                counters,
                overflow,
                side_id=side_id,
                prepared_dataset_arrays=prepared_dataset_arrays[side_id],
                phase_seconds=phase_seconds,
                phase_prefix=phase_prefix,
                stream=streams[side_id],
                synchronize=False,
            )
            side_parts.append(side)
        for stream in streams:
            stream.synchronize()
        _record_elapsed(append_start, phase_seconds, f"{phase_prefix}_concurrent_side_append_kernels_sec")
        if phase_seconds is not None:
            phase_seconds[f"{phase_prefix}_concurrent_side_append_used"] = 1.0
    else:
        for side_id, dataset in enumerate(datasets):
            side = _build_projected_descriptor_carrier_device_atomic_append_side(
                dataset,
                columns,
                sorted_views[side_id],
                _point_face_device(point_faces[side_id]),
                midpoint_faces[side_id].get("device") if isinstance(midpoint_faces[side_id], dict) else None,
                group_length,
                label_a,
                label_b,
                counters,
                overflow,
                side_id=side_id,
                prepared_dataset_arrays=prepared_dataset_arrays[side_id],
                phase_seconds=phase_seconds,
                phase_prefix=phase_prefix,
            )
            side_parts.append(side)
    cuda.synchronize()
    counters_host = counters.copy_to_host()
    overflow_host = overflow.copy_to_host()
    total_groups = int(counters_host[0])
    total_point_rows = int(counters_host[1])
    total_skipped = int(counters_host[2])
    if int(overflow_host[0]) != 0 or total_groups > capacity:
        raise RuntimeError(
            "device-resident carrier atomic append overflowed: "
            f"capacity={capacity}, required={total_groups}"
        )
    _record_elapsed(combine_start, phase_seconds, f"{phase_prefix}_combine_sides_sec")

    carrier = {
        "group_length_device": group_length,
        "label_a_device": label_a,
        "label_b_device": label_b,
        "group_count": int(total_groups),
        "point_row_count": int(total_point_rows),
        "skipped_group_count": int(total_skipped),
        "padded_group_count": int(capacity),
        "_side_parts": side_parts,
        "_atomic_append_counters": counters,
    }
    stats = {
        "schema": "rtdl.paper_reproduction.rayjoin.section57_device_resident_binary_carrier.v1",
        "group_count": int(total_groups),
        "point_row_count": int(total_point_rows),
        "skipped_group_count": int(total_skipped),
        "full_geometry_payload_columns_materialized": False,
        "transient_display_point_tuples_used_for_dedupe_count": False,
        "projection_pushdown": True,
        "columnar_xsect_arrays": True,
        "device_resident_carrier": True,
        "device_resident_consumer_required": True,
        "device_resident_carrier_atomic_append_used": True,
        "compiled_group_execution_mode": "numba_cuda_device_kernels",
        "rayjoin_specific_core_primitive": False,
        "rtdl_core_change": False,
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


def run_pipeline(args):
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected: rtdsl.rayjoin_overlay")

    phase_seconds = {}
    native_point_location_timings = {}
    native_lsi_timings = {}
    point_location_device_face_column_metadata = {}
    device_columnar_enabled = bool(getattr(args, "device_columnar", False))
    native_lexsort_enabled = bool(getattr(args, "native_lexsort", False))
    compiled_group_enabled = bool(getattr(args, "compiled_group", False))
    validate_device_order = bool(getattr(args, "validate_device_order", False))
    prepared_lsi_replay_enabled = bool(getattr(args, "prepared_lsi_replay", False))
    exact_lsi_device_columns_enabled = bool(getattr(args, "exact_lsi_device_columns", False))
    bounded_exact_lsi_device_columns_enabled = bool(getattr(args, "bounded_exact_lsi_device_columns", False))
    point_location_device_face_columns_enabled = bool(getattr(args, "point_location_device_face_columns", False))
    fast_scaled_point_pack_enabled = bool(getattr(args, "fast_scaled_point_pack", False))
    device_resident_carrier_enabled = bool(getattr(args, "device_resident_carrier", False))
    device_carrier_concurrent_sides_enabled = bool(getattr(args, "device_carrier_concurrent_sides", False))
    compiled_group_side_order = parse_compiled_group_side_order(
        str(getattr(args, "compiled_group_side_order", "0,1"))
    )
    selected_lsi_routes = sum(
        int(flag)
        for flag in (
            prepared_lsi_replay_enabled,
            exact_lsi_device_columns_enabled,
            bounded_exact_lsi_device_columns_enabled,
        )
    )
    if selected_lsi_routes > 1:
        raise RuntimeError(
            "--prepared-lsi-replay, --exact-lsi-device-columns, and "
            "--bounded-exact-lsi-device-columns are mutually exclusive"
        )
    if device_columnar_enabled and not _cuda_is_available():
        raise RuntimeError("--device-columnar requires Numba CUDA availability")
    if native_lexsort_enabled and not device_columnar_enabled:
        raise RuntimeError("--native-lexsort requires --device-columnar")
    if compiled_group_enabled and not NUMBA_AVAILABLE:
        raise RuntimeError("--compiled-group requires Numba availability")
    if device_resident_carrier_enabled:
        if not device_columnar_enabled:
            raise RuntimeError("--device-resident-carrier requires --device-columnar")
        if not point_location_device_face_columns_enabled:
            raise RuntimeError("--device-resident-carrier requires --point-location-device-face-columns")
        if not (exact_lsi_device_columns_enabled or bounded_exact_lsi_device_columns_enabled):
            raise RuntimeError("--device-resident-carrier requires exact or bounded exact LSI device columns")
    if device_carrier_concurrent_sides_enabled and not device_resident_carrier_enabled:
        raise RuntimeError("--device-carrier-concurrent-sides requires --device-resident-carrier")
    preloaded_left = getattr(args, "_preloaded_left", None)
    preloaded_right = getattr(args, "_preloaded_right", None)
    preloaded_bounds = getattr(args, "_preloaded_bounds", None)
    left = (
        preloaded_left
        if preloaded_left is not None
        else timed("load_pack_left_sec", lambda: base.load_dataset_arrays(Path(args.left)), phase_seconds)
    )
    right = (
        preloaded_right
        if preloaded_right is not None
        else timed("load_pack_right_sec", lambda: base.load_dataset_arrays(Path(args.right)), phase_seconds)
    )
    bounds = (
        preloaded_bounds
        if preloaded_bounds is not None
        else timed("shared_bounds_sec", lambda: base.shared_bounds(left, right), phase_seconds)
    )
    prepared_lsi_session = getattr(args, "_prepared_lsi_session", None)
    prepared_lsi_query = getattr(args, "_prepared_lsi_query", None)
    device_segment_arrays_left = getattr(args, "_device_segment_arrays_left", None)
    device_segment_arrays_right = getattr(args, "_device_segment_arrays_right", None)
    device_carrier_arrays_left = getattr(args, "_device_carrier_arrays_left", None)
    device_carrier_arrays_right = getattr(args, "_device_carrier_arrays_right", None)
    pairs = None
    lsi_device_columns = None
    exact_lsi_pair_numpy_copy_used = False
    bounded_exact_lsi_pair_numpy_copy_used = False
    if prepared_lsi_replay_enabled:
        pairs = run_lsi_prepared_replay(left, right, phase_seconds, native_lsi_timings)
    elif exact_lsi_device_columns_enabled:
        if device_columnar_enabled:
            if prepared_lsi_session is not None and prepared_lsi_query is not None:
                lsi_device_columns = produce_lsi_exact_device_columns_from_prepared_query(
                    prepared_lsi_session,
                    prepared_lsi_query,
                    phase_seconds,
                    native_lsi_timings,
                )
            elif prepared_lsi_session is not None:
                lsi_device_columns = produce_lsi_exact_device_columns_from_prepared_base(
                    prepared_lsi_session,
                    left,
                    phase_seconds,
                    native_lsi_timings,
                )
            else:
                lsi_device_columns = produce_lsi_exact_device_columns(left, right, phase_seconds, native_lsi_timings)
        else:
            pairs = run_lsi_exact_device_columns(left, right, phase_seconds, native_lsi_timings)
            exact_lsi_pair_numpy_copy_used = True
    elif bounded_exact_lsi_device_columns_enabled:
        if device_columnar_enabled:
            if prepared_lsi_session is not None and prepared_lsi_query is not None:
                lsi_device_columns = produce_lsi_bounded_exact_device_columns_from_prepared_query(
                    prepared_lsi_session,
                    prepared_lsi_query,
                    phase_seconds,
                    native_lsi_timings,
                    capacity=int(args.bounded_exact_lsi_capacity),
                )
            elif prepared_lsi_session is not None:
                lsi_device_columns = produce_lsi_bounded_exact_device_columns_from_prepared_base(
                    prepared_lsi_session,
                    left,
                    phase_seconds,
                    native_lsi_timings,
                    capacity=int(args.bounded_exact_lsi_capacity),
                )
            else:
                lsi_device_columns = produce_lsi_bounded_exact_device_columns(
                    left,
                    right,
                    phase_seconds,
                    native_lsi_timings,
                    capacity=int(args.bounded_exact_lsi_capacity),
                )
        else:
            pairs = run_lsi_bounded_exact_device_columns(
                left,
                right,
                phase_seconds,
                native_lsi_timings,
                capacity=int(args.bounded_exact_lsi_capacity),
            )
            bounded_exact_lsi_pair_numpy_copy_used = True
    else:
        pairs = timed("lsi_public_rows_sec", lambda: run_lsi(left, right, native_lsi_timings), phase_seconds)
    try:
        columns = timed(
            "intersection_reprojection_device_columnar_sec" if device_columnar_enabled else "intersection_reprojection_columnar_sec",
            lambda: (
                numeric_xsect_columns_from_pair_device_columns_numba_device(
                    lsi_device_columns,
                    left,
                    right,
                    scale_bounds=bounds,
                    left_device=device_segment_arrays_left,
                    right_device=device_segment_arrays_right,
                )
                if device_columnar_enabled and lsi_device_columns is not None
                else numeric_xsect_columns_from_pairs_numba_device(
                    pairs,
                    left,
                    right,
                    scale_bounds=bounds,
                    left_device=device_segment_arrays_left,
                    right_device=device_segment_arrays_right,
                )
                if device_columnar_enabled
                else numeric_xsect_columns_from_pairs(pairs, left, right, scale_bounds=bounds)
            ),
            phase_seconds,
        )
    finally:
        if lsi_device_columns is not None:
            lsi_device_columns.close()
    lsi_row_count = int(np.asarray(columns["eid0"]).shape[0])
    sorted0 = timed(
        "sort_map0_device_columnar_sec" if device_columnar_enabled else "sort_map0_columnar_sec",
        lambda: (
            sort_xsect_indices_for_map_numba_device(
                columns,
                left,
                0,
                bounds,
                native_lexsort=native_lexsort_enabled,
                phase_seconds=phase_seconds,
                phase_prefix="sort_map0_device_columnar",
                segment_device_arrays=device_segment_arrays_left,
                with_device_run_bounds=device_resident_carrier_enabled,
                with_host_run_tables=not device_resident_carrier_enabled,
            )
            if device_columnar_enabled
            else sort_xsect_indices_for_map(columns, left, 0, bounds)
        ),
        phase_seconds,
    )
    sorted1 = timed(
        "sort_map1_device_columnar_sec" if device_columnar_enabled else "sort_map1_columnar_sec",
        lambda: (
            sort_xsect_indices_for_map_numba_device(
                columns,
                right,
                1,
                bounds,
                native_lexsort=native_lexsort_enabled,
                phase_seconds=phase_seconds,
                phase_prefix="sort_map1_device_columnar",
                segment_device_arrays=device_segment_arrays_right,
                with_device_run_bounds=device_resident_carrier_enabled,
                with_host_run_tables=not device_resident_carrier_enabled,
            )
            if device_columnar_enabled
            else sort_xsect_indices_for_map(columns, right, 1, bounds)
        ),
        phase_seconds,
    )
    device_order_validation = None
    if validate_device_order and device_columnar_enabled:
        cpu_sorted0 = timed(
            "validate_device_sort_map0_cpu_reference_sec",
            lambda: sort_xsect_indices_for_map(columns, left, 0, bounds),
            phase_seconds,
        )
        cpu_sorted1 = timed(
            "validate_device_sort_map1_cpu_reference_sec",
            lambda: sort_xsect_indices_for_map(columns, right, 1, bounds),
            phase_seconds,
        )
        map0_same = bool(np.array_equal(sorted0["order"], cpu_sorted0["order"]))
        map1_same = bool(np.array_equal(sorted1["order"], cpu_sorted1["order"]))
        device_order_validation = {
            "map0_order_matches_cpu_longdouble_reference": map0_same,
            "map1_order_matches_cpu_longdouble_reference": map1_same,
        }
        if not map0_same or not map1_same:
            raise RuntimeError(f"device sort order mismatch: {device_order_validation}")

    map0_query_map_id = 1 if args.swap_query_map_ids else 0
    map1_query_map_id = 0 if args.swap_query_map_ids else 1
    external_map0_in_map1 = getattr(args, "_prepared_point_location_map0_in_map1", None)
    external_map1_in_map0 = getattr(args, "_prepared_point_location_map1_in_map0", None)
    map0_in_map1 = (
        external_map0_in_map1
        if external_map0_in_map1 is not None
        else timed(
            "prepare_point_location_map0_in_map1_sec",
            lambda: base.prepare_planar_map_point_location_2d_optix(
                right.cdb_segments,
                query_map_id=map0_query_map_id,
                scale_bounds=bounds,
            ),
            phase_seconds,
        )
    )
    map1_in_map0 = (
        external_map1_in_map0
        if external_map1_in_map0 is not None
        else timed(
            "prepare_point_location_map1_in_map0_sec",
            lambda: base.prepare_planar_map_point_location_2d_optix(
                left.cdb_segments,
                query_map_id=map1_query_map_id,
                scale_bounds=bounds,
            ),
            phase_seconds,
        )
    )

    try:
        prepared_vertex_points_map0 = getattr(args, "_prepared_vertex_points_map0_in_map1", None)
        prepared_vertex_points_map1 = getattr(args, "_prepared_vertex_points_map1_in_map0", None)
        retained_midpoint_face_values = []
        point_faces0 = timed(
            "vertex_pip_map0_in_map1_sec",
            lambda: (
                run_point_location_face_id_device_columns(
                    map0_in_map1,
                    left.points,
                    left.point_count,
                    phase_prefix="vertex_pip_map0_in_map1",
                    phase_seconds=phase_seconds,
                    metadata_records=point_location_device_face_column_metadata,
                    prepared_points=prepared_vertex_points_map0,
                    retain_device=device_resident_carrier_enabled,
                    copy_host=not device_resident_carrier_enabled,
                )
                if point_location_device_face_columns_enabled
                else base.run_point_location(map0_in_map1, left.points, left.point_count)
            ),
            phase_seconds,
        )
        native_point_location_timings["vertex_pip_map0_in_map1"] = map0_in_map1.last_phase_timings() or {}
        point_faces1 = timed(
            "vertex_pip_map1_in_map0_sec",
            lambda: (
                run_point_location_face_id_device_columns(
                    map1_in_map0,
                    right.points,
                    right.point_count,
                    phase_prefix="vertex_pip_map1_in_map0",
                    phase_seconds=phase_seconds,
                    metadata_records=point_location_device_face_column_metadata,
                    prepared_points=prepared_vertex_points_map1,
                    retain_device=device_resident_carrier_enabled,
                    copy_host=not device_resident_carrier_enabled,
                )
                if point_location_device_face_columns_enabled
                else base.run_point_location(map1_in_map0, right.points, right.point_count)
            ),
            phase_seconds,
        )
        native_point_location_timings["vertex_pip_map1_in_map0"] = map1_in_map0.last_phase_timings() or {}

        midpoint_faces = (
            [
                {"host": None, "device": cuda.device_array(lsi_row_count, dtype=np.uint32)},
                {"host": None, "device": cuda.device_array(lsi_row_count, dtype=np.uint32)},
            ]
            if device_resident_carrier_enabled
            else [
                np.zeros(lsi_row_count, dtype=np.uint32),
                np.zeros(lsi_row_count, dtype=np.uint32),
            ]
        )
        for side_id, locator, sorted_view in ((0, map0_in_map1, sorted0), (1, map1_in_map0, sorted1)):
            if device_resident_carrier_enabled:
                midpoint_prepared_points, owners, midpoint_count, _midpoint_device_points = timed(
                    f"midpoint_points_map{side_id}_device_query_points_sec",
                    lambda locator=locator, sorted_view=sorted_view, side_id=side_id: midpoint_query_points_device(
                        locator,
                        columns,
                        sorted_view,
                        side_id,
                        scale_bounds=bounds,
                        phase_seconds=phase_seconds,
                        phase_prefix=f"midpoint_points_map{side_id}",
                    ),
                    phase_seconds,
                )
                scaled_points = None
            else:
                midpoint_prepared_points = None
                scaled_points, owners, midpoint_count = timed(
                    f"midpoint_points_map{side_id}_columnar_sec",
                    lambda sorted_view=sorted_view, side_id=side_id: midpoint_points_columnar(
                        columns,
                        sorted_view,
                        side_id,
                        scale_bounds=bounds,
                        phase_seconds=phase_seconds,
                        phase_prefix=f"midpoint_points_map{side_id}",
                        fast_scaled_point_pack=fast_scaled_point_pack_enabled,
                    ),
                    phase_seconds,
                )
            faces = timed(
                f"midpoint_pip_map{side_id}_sec",
                lambda locator=locator, scaled_points=scaled_points, count=midpoint_count, side_id=side_id: (
                    run_point_location_face_id_device_columns(
                        locator,
                        scaled_points,
                        count,
                        phase_prefix=f"midpoint_pip_map{side_id}",
                        phase_seconds=phase_seconds,
                        metadata_records=point_location_device_face_column_metadata,
                        prepared_points=midpoint_prepared_points,
                        retain_device=device_resident_carrier_enabled,
                        copy_host=not device_resident_carrier_enabled,
                    )
                    if point_location_device_face_columns_enabled
                    else base.run_point_location(
                        locator,
                        scaled_points,
                        count,
                    )
                ),
                phase_seconds,
            )
            native_point_location_timings[f"midpoint_pip_map{side_id}"] = locator.last_phase_timings() or {}
            if device_resident_carrier_enabled:
                if isinstance(faces, dict):
                    retained_midpoint_face_values.append(faces)
                timed(
                    f"assign_midpoint_faces_map{side_id}_device_scatter_sec",
                    lambda side_id=side_id, owners=owners, faces=faces: _scatter_midpoint_faces_device(
                        owners,
                        _point_face_device(faces),
                        midpoint_faces[side_id]["device"],
                        midpoint_count,
                    ),
                    phase_seconds,
                )
            else:
                timed(
                    f"assign_midpoint_faces_map{side_id}_columnar_sec",
                    lambda side_id=side_id, owners=owners, faces=faces: midpoint_faces[side_id].__setitem__(
                        owners,
                        faces.astype(np.uint32, copy=False),
                    ),
                    phase_seconds,
                )
    finally:
        if external_map0_in_map1 is None and external_map1_in_map0 is None:
            timed("destroy_point_location_sessions_sec", lambda: (map0_in_map1.close(), map1_in_map0.close()), phase_seconds)

    carrier_phase_name = (
        "device_resident_carrier_construction_sec"
        if device_resident_carrier_enabled
        else "grouped_compiled_columnar_carrier_construction_sec"
        if compiled_group_enabled
        else "grouped_columnar_carrier_construction_sec"
    )
    carrier, carrier_stats = timed(
        carrier_phase_name,
        lambda: (
            build_projected_descriptor_carrier_columnar_device(
                (left, right),
                columns,
                (sorted0, sorted1),
                (point_faces0, point_faces1),
                midpoint_faces,
                prepared_dataset_arrays=(device_carrier_arrays_left, device_carrier_arrays_right),
                phase_seconds=phase_seconds,
                concurrent_side_kernels=device_carrier_concurrent_sides_enabled,
            )
            if device_resident_carrier_enabled
            else build_projected_descriptor_carrier_columnar_compiled(
                (left, right),
                columns,
                (sorted0, sorted1),
                (point_faces0, point_faces1),
                midpoint_faces,
                phase_seconds=phase_seconds,
                side_order=compiled_group_side_order,
            )
            if compiled_group_enabled
            else build_projected_descriptor_carrier_columnar(
                (left, right),
                columns,
                (sorted0, sorted1),
                (point_faces0, point_faces1),
                midpoint_faces,
            )
        ),
        phase_seconds,
    )
    consumer = timed(
        "device_resident_descriptor_pair_count_consumer_sec"
        if device_resident_carrier_enabled
        else "grouped_descriptor_pair_count_consumer_sec",
        lambda: (
            descriptor_pair_count_projected_device(carrier)
            if device_resident_carrier_enabled
            else descriptor_pair_count_projected(carrier)
        ),
        phase_seconds,
    )
    for retained in locals().get("retained_midpoint_face_values", []):
        _close_point_face_value(retained)

    writer_free_hot_keys = [
        "lsi_prepared_replay_rows_sec"
        if prepared_lsi_replay_enabled
        else "lsi_bounded_exact_pair_id_device_columns_sec"
        if bounded_exact_lsi_device_columns_enabled
        else "lsi_exact_pair_id_device_columns_sec"
        if exact_lsi_device_columns_enabled
        else "lsi_public_rows_sec",
        "lsi_bounded_exact_pair_id_device_columns_to_numpy_sec"
        if bounded_exact_lsi_pair_numpy_copy_used
        else "lsi_exact_pair_id_device_columns_to_numpy_sec"
        if exact_lsi_pair_numpy_copy_used
        else "",
        "intersection_reprojection_device_columnar_sec" if device_columnar_enabled else "intersection_reprojection_columnar_sec",
        "sort_map0_device_columnar_sec" if device_columnar_enabled else "sort_map0_columnar_sec",
        "sort_map1_device_columnar_sec" if device_columnar_enabled else "sort_map1_columnar_sec",
        "vertex_pip_map0_in_map1_sec",
        "vertex_pip_map1_in_map0_sec",
        "midpoint_points_map0_device_query_points_sec"
        if device_resident_carrier_enabled
        else "midpoint_points_map0_columnar_sec",
        "midpoint_points_map1_device_query_points_sec"
        if device_resident_carrier_enabled
        else "midpoint_points_map1_columnar_sec",
        "midpoint_pip_map0_sec",
        "midpoint_pip_map1_sec",
        "assign_midpoint_faces_map0_device_scatter_sec"
        if device_resident_carrier_enabled
        else "assign_midpoint_faces_map0_columnar_sec",
        "assign_midpoint_faces_map1_device_scatter_sec"
        if device_resident_carrier_enabled
        else "assign_midpoint_faces_map1_columnar_sec",
        "device_resident_carrier_construction_sec"
        if device_resident_carrier_enabled
        else "grouped_compiled_columnar_carrier_construction_sec"
        if compiled_group_enabled
        else "grouped_columnar_carrier_construction_sec",
        "device_resident_descriptor_pair_count_consumer_sec"
        if device_resident_carrier_enabled
        else "grouped_descriptor_pair_count_consumer_sec",
    ]
    lsi_phase_key = writer_free_hot_keys[0]
    lsi_copy_key = (
        "lsi_bounded_exact_pair_id_device_columns_to_numpy_sec"
        if bounded_exact_lsi_pair_numpy_copy_used
        else "lsi_exact_pair_id_device_columns_to_numpy_sec"
        if exact_lsi_pair_numpy_copy_used
        else ""
    )
    lsi_native_timing_label = (
        "prepared_replay_pair_id_rows"
        if prepared_lsi_replay_enabled
        else "bounded_exact_pair_id_device_columns"
        if bounded_exact_lsi_device_columns_enabled
        else "exact_pair_id_device_columns"
        if exact_lsi_device_columns_enabled
        else "host_pair_id_rows"
    )
    writer_free_hot_sec = _sum_phase_seconds(phase_seconds, writer_free_hot_keys)
    ratio = None
    if args.author_overlay_compute_sec and args.author_overlay_compute_sec > 0:
        ratio = writer_free_hot_sec / args.author_overlay_compute_sec
    bounded_exact_repeat_diagnostic = None
    if args.bounded_exact_lsi_repeat_diagnostic:
        bounded_exact_repeat_diagnostic = run_lsi_bounded_exact_repeat_diagnostic(
            left,
            right,
            capacity=int(args.bounded_exact_lsi_capacity),
            repeat_count=int(args.bounded_exact_lsi_repeat_diagnostic),
        )
    lsi_cost_decomposition = build_lsi_cost_decomposition(
        phase_seconds=phase_seconds,
        native_lsi_timings=native_lsi_timings,
        lsi_key=lsi_phase_key,
        copy_key=lsi_copy_key,
        timing_label=lsi_native_timing_label,
    )
    downstream_floor_breakdown = build_downstream_floor_breakdown(
        phase_seconds=phase_seconds,
        lsi_key=lsi_phase_key,
        copy_key=lsi_copy_key,
        compiled_group_enabled=compiled_group_enabled,
        device_columnar_enabled=device_columnar_enabled,
        device_resident_carrier_enabled=device_resident_carrier_enabled,
    )
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.section57_columnar_binary.v1",
        "pair_name": args.pair_name,
        "route": (
            "device_columnar_xsect_numeric_binary_descriptor_route_public_lsi_pip_numba_consumer"
            if device_columnar_enabled
            else "columnar_xsect_numeric_binary_descriptor_route_public_lsi_pip_numba_consumer"
        ),
        "claim_boundary": {
            "numeric_binary_route": True,
            "projection_pushdown": True,
            "columnar_xsect_arrays": True,
            "device_columnar_requested": device_columnar_enabled,
            "numba_cuda_reprojection": device_columnar_enabled,
            "numba_cuda_sort": device_columnar_enabled,
            "native_cuda_lexsort_requested": native_lexsort_enabled,
            "sort_backend_side0": sorted0.get("device_sort_backend") if device_columnar_enabled else "numpy_lexsort",
            "sort_backend_side1": sorted1.get("device_sort_backend") if device_columnar_enabled else "numpy_lexsort",
            "lsi_pair_input_device_resident": bool(columns.get("_pair_input_device_resident", False)),
            "lsi_pair_host_to_device_copy_used": bool(columns.get("_pair_host_to_device_copy_used", False)),
            "lsi_pair_row_buffer_contract": columns.get("_pair_row_buffer"),
            "numba_compiled_group": compiled_group_enabled,
            "device_resident_carrier_requested": device_resident_carrier_enabled,
            "device_resident_carrier_used": device_resident_carrier_enabled,
            "device_carrier_concurrent_sides_requested": device_carrier_concurrent_sides_enabled,
            "device_carrier_concurrent_sides_used": bool(
                device_resident_carrier_enabled and device_carrier_concurrent_sides_enabled
            ),
            "device_resident_descriptor_consumer_used": device_resident_carrier_enabled,
            "midpoint_face_ids_copied_to_host": not device_resident_carrier_enabled,
            "midpoint_face_ids_device_scatter_used": device_resident_carrier_enabled,
            "midpoint_query_points_device_resident": device_resident_carrier_enabled,
            "midpoint_query_points_host_pack_used": not device_resident_carrier_enabled,
            "compiled_group_side_order": compiled_group_side_order if compiled_group_enabled else None,
            "compiled_group_side_order_scope": (
                "writer_free_binary_descriptor_route_only"
                if compiled_group_enabled
                else None
            ),
            "paper_text_order_claim_authorized": False,
            "prepared_lsi_replay_requested": prepared_lsi_replay_enabled,
            "prepared_lsi_replay_cached_diagnostic_only": prepared_lsi_replay_enabled,
            "exact_lsi_device_columns_requested": exact_lsi_device_columns_enabled,
            "exact_lsi_device_columns_downstream_numpy_copy_used": exact_lsi_pair_numpy_copy_used,
            "exact_lsi_device_columns_numba_direct_handoff_used": bool(
                exact_lsi_device_columns_enabled and device_columnar_enabled
            ),
            "bounded_exact_lsi_device_columns_requested": bounded_exact_lsi_device_columns_enabled,
            "bounded_exact_lsi_capacity": int(args.bounded_exact_lsi_capacity)
            if bounded_exact_lsi_device_columns_enabled
            else None,
            "bounded_exact_lsi_downstream_numpy_copy_used": bounded_exact_lsi_pair_numpy_copy_used,
            "bounded_exact_lsi_numba_direct_handoff_used": bool(
                bounded_exact_lsi_device_columns_enabled and device_columnar_enabled
            ),
            "point_location_device_face_columns_requested": point_location_device_face_columns_enabled,
            "point_location_device_face_columns_downstream_numpy_copy_used": (
                point_location_device_face_columns_enabled and not device_resident_carrier_enabled
            ),
            "point_location_device_face_columns_true_zero_copy_claim_authorized": False,
            "fast_scaled_point_pack_requested": fast_scaled_point_pack_enabled,
            "fast_scaled_point_pack_scope": (
                "vectorized_host_pack_same_scaled_point_abi"
                if fast_scaled_point_pack_enabled
                else None
            ),
            "fast_scaled_point_pack_device_resident_claim_authorized": False,
            "sort_order_validated_against_cpu_reference": bool(
                device_order_validation
                and device_order_validation.get("map0_order_matches_cpu_longdouble_reference")
                and device_order_validation.get("map1_order_matches_cpu_longdouble_reference")
            ),
            "full_carrier_geometry_payload_columns_materialized": False,
            "transient_display_point_tuples_used_for_dedupe_count": True,
            "paper_byte_equal_route": False,
            "paper_exact_sink_separate": True,
            "layer4_fusion": False,
            "public_high_performance_claim_authorized": False,
            "paper_byte_equality_claim_authorized_for_numeric_route": False,
            "layer4_claim_authorized": False,
            "rtdl_core_change": point_location_device_face_columns_enabled,
            "rtdl_core_change_scope": (
                "generic_planar_map_point_location_device_column_wrapper"
                if point_location_device_face_columns_enabled
                else None
            ),
            "rayjoin_specific_core_primitive": False,
            "bundled_rayjoin_overlay_imported": False,
            "rayjoin_app_adapter_used": True,
            "generic_contract_goal": True,
            "implementation_change": "internal_app_owned_measurement_script_only",
            "prepared_operator_session_used": bool(getattr(args, "_prepared_operator_session_active", False)),
        },
        "left": {"path": left.path, "chains": left.chain_count, "points": left.point_count, "edges": left.edge_count},
        "right": {"path": right.path, "chains": right.chain_count, "points": right.point_count, "edges": right.edge_count},
        "scale_bounds": bounds,
        "lsi_row_count": lsi_row_count,
        "xsect_sorted_counts": {"side0": int(sorted0["order"].size), "side1": int(sorted1["order"].size)},
        "xsect_sort_backends": {
            "side0": sorted0.get("device_sort_backend") if device_columnar_enabled else "numpy_lexsort",
            "side1": sorted1.get("device_sort_backend") if device_columnar_enabled else "numpy_lexsort",
        },
        "vertex_positive_counts": {
            "side0_in_side1": int(np.count_nonzero(_point_face_host(point_faces0))),
            "side1_in_side0": int(np.count_nonzero(_point_face_host(point_faces1))),
        },
        "grouped_carrier": carrier_stats,
        "downstream_consumer": consumer,
        "phase_seconds": phase_seconds,
        "native_lsi_timings": native_lsi_timings,
        "lsi_cost_decomposition": lsi_cost_decomposition,
        "downstream_floor_breakdown": downstream_floor_breakdown,
        "bounded_exact_lsi_repeat_diagnostic": bounded_exact_repeat_diagnostic,
        "native_point_location_timings": native_point_location_timings,
        "point_location_device_face_column_metadata": point_location_device_face_column_metadata,
        "device_order_validation": device_order_validation,
        "writer_free_hot_keys": writer_free_hot_keys,
        "writer_free_hot_sec": writer_free_hot_sec,
        "author_overlay_compute_sec": args.author_overlay_compute_sec,
        "writer_free_hot_vs_author_overlay_compute_ratio": ratio,
    }


def _compact_repeat_run_summary(summary, *, run_kind, run_index):
    phase_seconds = summary.get("phase_seconds", {})
    floor = summary.get("downstream_floor_breakdown", {})
    boundary = summary.get("claim_boundary", {})
    downstream_consumer = summary.get("downstream_consumer", {})
    lsi_cost = summary.get("lsi_cost_decomposition", {})
    lsi_native = lsi_cost.get("native_timings", {}) if isinstance(lsi_cost, dict) else {}
    lsi_extended = lsi_native.get("extended", {}) if isinstance(lsi_native, dict) else {}
    return {
        "run_kind": run_kind,
        "run_index": int(run_index),
        "query_batch": summary.get("query_batch"),
        "writer_free_hot_sec": float(summary.get("writer_free_hot_sec", 0.0)),
        "lsi_phase_sec": float(floor.get("lsi_phase_sec", 0.0)),
        "downstream_floor_sec": float(floor.get("downstream_floor_sec", 0.0)),
        "lsi_row_count": int(summary.get("lsi_row_count", 0)),
        "descriptor_pair_count": int(downstream_consumer.get("pair_count", 0)),
        "downstream_consumer_partner": downstream_consumer.get("partner"),
        "downstream_consumer_native_lexsort_descriptor_pair_scan": downstream_consumer.get(
            "native_lexsort_descriptor_pair_scan"
        ),
        "downstream_consumer_native_lexsort_direct_carrier_prefix": downstream_consumer.get(
            "native_lexsort_direct_carrier_prefix"
        ),
        "lsi_pair_input_device_resident": bool(boundary.get("lsi_pair_input_device_resident", False)),
        "lsi_pair_host_to_device_copy_used": bool(boundary.get("lsi_pair_host_to_device_copy_used", True)),
        "bounded_exact_lsi_numba_direct_handoff_used": bool(
            boundary.get("bounded_exact_lsi_numba_direct_handoff_used", False)
        ),
        "lsi_extended_timings": lsi_extended,
        "key_phase_seconds": {
            key: float(phase_seconds[key])
            for key in (
                "lsi_bounded_exact_pair_id_device_columns_sec",
                "lsi_exact_pair_id_device_columns_sec",
                "lsi_public_rows_sec",
                "prepare_point_location_map0_in_map1_sec",
                "prepare_point_location_map1_in_map0_sec",
                "intersection_reprojection_device_columnar_sec",
                "sort_map0_device_columnar_sec",
                "sort_map1_device_columnar_sec",
                "sort_map0_device_columnar_key_kernel_sec",
                "sort_map0_device_columnar_segment_xy_to_device_sec",
                "sort_map0_device_columnar_segment_xy_reused",
                "sort_map0_device_columnar_native_lexsort_sec",
                "sort_map0_device_columnar_bitonic_sort_sec",
                "sort_map0_device_columnar_copy_order_to_host_sec",
                "sort_map0_device_columnar_copy_edges_to_host_sec",
                "sort_map0_device_columnar_device_run_bounds_sec",
                "sort_map0_device_columnar_host_run_start_table_sec",
                "sort_map0_device_columnar_host_run_end_table_sec",
                "sort_map0_device_columnar_host_run_tables_skipped",
                "sort_map1_device_columnar_key_kernel_sec",
                "sort_map1_device_columnar_segment_xy_to_device_sec",
                "sort_map1_device_columnar_segment_xy_reused",
                "sort_map1_device_columnar_native_lexsort_sec",
                "sort_map1_device_columnar_bitonic_sort_sec",
                "sort_map1_device_columnar_copy_order_to_host_sec",
                "sort_map1_device_columnar_copy_edges_to_host_sec",
                "sort_map1_device_columnar_device_run_bounds_sec",
                "sort_map1_device_columnar_host_run_start_table_sec",
                "sort_map1_device_columnar_host_run_end_table_sec",
                "sort_map1_device_columnar_host_run_tables_skipped",
                "vertex_pip_map0_in_map1_sec",
                "vertex_pip_map1_in_map0_sec",
                "midpoint_points_map0_columnar_sec",
                "midpoint_points_map1_columnar_sec",
                "midpoint_points_map0_device_query_points_sec",
                "midpoint_points_map1_device_query_points_sec",
                "midpoint_points_map0_device_query_points_kernel_sec",
                "midpoint_points_map1_device_query_points_kernel_sec",
                "midpoint_points_map0_prepare_device_query_points_sec",
                "midpoint_points_map1_prepare_device_query_points_sec",
                "midpoint_pip_map0_sec",
                "midpoint_pip_map1_sec",
                "assign_midpoint_faces_map0_columnar_sec",
                "assign_midpoint_faces_map1_columnar_sec",
                "assign_midpoint_faces_map0_device_scatter_sec",
                "assign_midpoint_faces_map1_device_scatter_sec",
                "grouped_compiled_columnar_carrier_construction_sec",
                "device_resident_carrier_construction_sec",
                "device_resident_carrier_side0_dataset_to_device_sec",
                "device_resident_carrier_side0_run_bounds_to_device_sec",
                "device_resident_carrier_side0_count_kernel_sec",
                "device_resident_carrier_side0_prefix_sum_sec",
                "device_resident_carrier_side0_fill_kernel_sec",
                "device_resident_carrier_side0_atomic_append_kernel_sec",
                "device_resident_carrier_side0_atomic_append_launch_sec",
                "device_resident_carrier_side0_atomic_append_used",
                "device_resident_carrier_side1_dataset_to_device_sec",
                "device_resident_carrier_side1_run_bounds_to_device_sec",
                "device_resident_carrier_side1_count_kernel_sec",
                "device_resident_carrier_side1_prefix_sum_sec",
                "device_resident_carrier_side1_fill_kernel_sec",
                "device_resident_carrier_side1_atomic_append_kernel_sec",
                "device_resident_carrier_side1_atomic_append_launch_sec",
                "device_resident_carrier_side1_atomic_append_used",
                "device_resident_carrier_concurrent_side_append_kernels_sec",
                "device_resident_carrier_concurrent_side_append_used",
                "device_resident_carrier_combine_sides_sec",
                "grouped_compiled_carrier_side0_prepare_inputs_sec",
                "grouped_compiled_carrier_side0_numba_builder_sec",
                "grouped_compiled_carrier_side0_slice_copy_sec",
                "grouped_compiled_carrier_side0_total_sec",
                "grouped_compiled_carrier_side1_prepare_inputs_sec",
                "grouped_compiled_carrier_side1_numba_builder_sec",
                "grouped_compiled_carrier_side1_slice_copy_sec",
                "grouped_compiled_carrier_side1_total_sec",
                "grouped_compiled_carrier_concatenate_sec",
                "grouped_compiled_carrier_group_offset_cumsum_sec",
                "grouped_compiled_carrier_stats_packaging_sec",
                "grouped_descriptor_pair_count_consumer_sec",
                "device_resident_descriptor_pair_count_consumer_sec",
            )
            if key in phase_seconds
        },
    }


def _median(values):
    clean = [float(value) for value in values]
    return float(statistics.median(clean)) if clean else None


def summarize_repeat_protocol(*, args, warmup_summaries, measured_summaries, session_prepare_phase_seconds=None):
    warmup_rows = [
        _compact_repeat_run_summary(summary, run_kind="warmup", run_index=index + 1)
        for index, summary in enumerate(warmup_summaries)
    ]
    measured_rows = [
        _compact_repeat_run_summary(summary, run_kind="measured", run_index=index + 1)
        for index, summary in enumerate(measured_summaries)
    ]
    measured_writer_free = [row["writer_free_hot_sec"] for row in measured_rows]
    measured_lsi = [row["lsi_phase_sec"] for row in measured_rows]
    measured_downstream = [row["downstream_floor_sec"] for row in measured_rows]
    all_descriptor_counts = {row["descriptor_pair_count"] for row in warmup_rows + measured_rows}
    all_lsi_counts = {row["lsi_row_count"] for row in warmup_rows + measured_rows}
    prepared_operator_session = bool(getattr(args, "prepared_operator_session", False))
    prepared_lsi_base_session = bool(getattr(args, "prepared_lsi_base_session", False))
    query_chain_batches = int(getattr(args, "query_chain_batches", 0))
    distinct_query_batches = query_chain_batches > 0
    if prepared_operator_session:
        claim_scope = (
            "Same-process prepared operator body measurement for the writer-free binary operator. "
            "It excludes explicit session preparation and must be reported beside, not instead of, "
            "the fresh one-shot route. It is not a true query-many measurement unless distinct "
            "query batches are provided and reported separately."
        )
    elif prepared_lsi_base_session and distinct_query_batches:
        claim_scope = (
            "Same-process prepared LSI base-session full-overlay query-batch measurement. "
            "It prepares the right/base LSI planar map once, splits the left input into distinct "
            "chain-contiguous query batches, and runs a full writer-free binary overlay route for "
            "each batch. It excludes cold CLI startup and base-session preparation; first-batch and "
            "later-batch costs must be reported separately."
        )
    elif prepared_lsi_base_session:
        claim_scope = (
            "Same-process prepared LSI base-session measurement for the writer-free binary operator. "
            "It prepares the right/base LSI planar map once, builds a fresh LSI query object for each "
            "measured route, and excludes explicit base-session preparation and warmup rows. It is not "
            "a cold CLI one-shot headline and not a true query-many measurement unless distinct query "
            "batches are provided and reported separately."
        )
    else:
        claim_scope = (
            "Same-process warm-process fresh measurement for the writer-free binary operator. "
            "It excludes cold process/runtime startup and excludes warmup rows from repeat medians. "
            "It is not a true query-many measurement unless distinct query batches are provided and "
            "reported separately."
        )
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.section57.binary_repeat_protocol.v1",
        "pair_name": str(getattr(args, "pair_name", "unnamed_pair")),
        "repeat_count": int(getattr(args, "repeat", 1)),
        "warmup_runs": int(getattr(args, "warmup_runs", 0)),
        "route": {
            "device_columnar": bool(getattr(args, "device_columnar", False)),
            "compiled_group": bool(getattr(args, "compiled_group", False)),
            "bounded_exact_lsi_device_columns": bool(getattr(args, "bounded_exact_lsi_device_columns", False)),
            "exact_lsi_device_columns": bool(getattr(args, "exact_lsi_device_columns", False)),
            "point_location_device_face_columns": bool(getattr(args, "point_location_device_face_columns", False)),
            "fast_scaled_point_pack": bool(getattr(args, "fast_scaled_point_pack", False)),
            "prepared_operator_session": prepared_operator_session,
            "prepared_lsi_base_session": bool(getattr(args, "prepared_lsi_base_session", False)),
            "query_chain_batches": query_chain_batches,
            "prepared_query_batch_right_vertex_points": bool(
                getattr(args, "prepared_query_batch_right_vertex_points", False)
            ),
            "prepared_query_batch_left_vertex_points": bool(
                getattr(args, "prepared_query_batch_left_vertex_points", False)
            ),
            "prepared_query_batch_segment_arrays": bool(
                getattr(args, "prepared_query_batch_segment_arrays", False)
            ),
            "prepared_lsi_base_workspace_warmup": bool(
                getattr(args, "prepared_lsi_base_workspace_warmup", False)
            ),
            "prepared_query_batch_lsi_query_workspaces": bool(
                getattr(args, "prepared_query_batch_lsi_query_workspaces", False)
            ),
            "device_resident_carrier": bool(getattr(args, "device_resident_carrier", False)),
            "device_carrier_concurrent_sides": bool(getattr(args, "device_carrier_concurrent_sides", False)),
        },
        "session_prepare_phase_seconds": session_prepare_phase_seconds or {},
        "warmup_rows": warmup_rows,
        "measured_rows": measured_rows,
        "median_writer_free_hot_sec": _median(measured_writer_free),
        "median_lsi_phase_sec": _median(measured_lsi),
        "median_downstream_floor_sec": _median(measured_downstream),
        "best_writer_free_hot_sec": min(measured_writer_free) if measured_writer_free else None,
        "worst_writer_free_hot_sec": max(measured_writer_free) if measured_writer_free else None,
        "structural_consistency": {
            "single_lsi_row_count": len(all_lsi_counts) == 1,
            "single_descriptor_pair_count": len(all_descriptor_counts) == 1,
            "lsi_row_counts": sorted(all_lsi_counts),
            "descriptor_pair_counts": sorted(all_descriptor_counts),
        },
        "claim_boundary": {
            "writer_excluded": True,
            "paper_text_route": False,
            "fresh_one_shot_headline": False,
            "prepared_operator_body_measurement": prepared_operator_session,
            "prepared_lsi_base_session_measurement": prepared_lsi_base_session,
            "true_query_many_measurement": bool(prepared_lsi_base_session and distinct_query_batches),
            "distinct_query_batches": distinct_query_batches,
            "query_many_measurement_kind": "chain_contiguous_full_overlay_batches"
            if prepared_lsi_base_session and distinct_query_batches
            else None,
            "prepared_operator_session": prepared_operator_session,
            "prepared_lsi_base_session": prepared_lsi_base_session,
            "prepared_query_batch_right_vertex_points": bool(
                getattr(args, "prepared_query_batch_right_vertex_points", False)
            ),
            "prepared_query_batch_right_vertex_points_scope": (
                "same_right_vertex_point_set_reused_across_chain_contiguous_left_batches"
                if bool(getattr(args, "prepared_query_batch_right_vertex_points", False))
                else None
            ),
            "prepared_query_batch_left_vertex_points": bool(
                getattr(args, "prepared_query_batch_left_vertex_points", False)
            ),
            "prepared_query_batch_left_vertex_points_scope": (
                "left_batch_vertex_point_sets_prepared_once_per_distinct_batch_and_reused_in_hot_body"
                if bool(getattr(args, "prepared_query_batch_left_vertex_points", False))
                else None
            ),
            "prepared_query_batch_segment_arrays": bool(
                getattr(args, "prepared_query_batch_segment_arrays", False)
            ),
            "prepared_query_batch_segment_arrays_scope": (
                "right_segment_arrays_reused_and_left_batch_segment_arrays_prepared_per_batch"
                if bool(getattr(args, "prepared_query_batch_segment_arrays", False))
                else None
            ),
            "prepared_lsi_base_workspace_warmup": bool(
                getattr(args, "prepared_lsi_base_workspace_warmup", False)
            ),
            "prepared_lsi_base_workspace_warmup_scope": (
                "session_prepares_base_lsi_workspace_with_tiny_unmeasured_query"
                if bool(getattr(args, "prepared_lsi_base_workspace_warmup", False))
                else None
            ),
            "prepared_query_batch_lsi_query_workspaces": bool(
                getattr(args, "prepared_query_batch_lsi_query_workspaces", False)
            ),
            "prepared_query_batch_lsi_query_workspaces_scope": (
                "session_prepares_and_warms_each_distinct_batch_lsi_query_workspace_without_reusing_results"
                if bool(getattr(args, "prepared_query_batch_lsi_query_workspaces", False))
                else None
            ),
            "author_comparison_authorized": False,
            "warmup_rows_excluded_from_median": True,
            "warmup_only_headline_authorized": False,
            "claim_scope": claim_scope,
        },
    }


def run_pipeline_repeat_protocol(args):
    repeat = int(getattr(args, "repeat", 1))
    warmup_runs = int(getattr(args, "warmup_runs", 0))
    query_chain_batches = int(getattr(args, "query_chain_batches", 0))
    if repeat < 1:
        raise ValueError("--repeat must be >= 1")
    if warmup_runs < 0:
        raise ValueError("--warmup-runs must be >= 0")
    if query_chain_batches < 0:
        raise ValueError("--query-chain-batches must be >= 0")
    if repeat == 1 and warmup_runs == 0 and not bool(getattr(args, "prepared_lsi_base_session", False)):
        return run_pipeline(args)

    if bool(getattr(args, "prepared_operator_session", False)) and bool(
        getattr(args, "prepared_lsi_base_session", False)
    ):
        raise ValueError("--prepared-operator-session and --prepared-lsi-base-session are mutually exclusive")
    if bool(getattr(args, "prepared_query_batch_right_vertex_points", False)):
        if not bool(getattr(args, "prepared_lsi_base_session", False)) or query_chain_batches <= 0:
            raise ValueError(
                "--prepared-query-batch-right-vertex-points requires "
                "--prepared-lsi-base-session with --query-chain-batches > 0"
            )
        if not bool(getattr(args, "point_location_device_face_columns", False)):
            raise ValueError(
                "--prepared-query-batch-right-vertex-points requires "
                "--point-location-device-face-columns"
            )
    if bool(getattr(args, "prepared_query_batch_left_vertex_points", False)):
        if not bool(getattr(args, "prepared_lsi_base_session", False)) or query_chain_batches <= 0:
            raise ValueError(
                "--prepared-query-batch-left-vertex-points requires "
                "--prepared-lsi-base-session with --query-chain-batches > 0"
            )
        if not bool(getattr(args, "point_location_device_face_columns", False)):
            raise ValueError(
                "--prepared-query-batch-left-vertex-points requires "
                "--point-location-device-face-columns"
            )
    if bool(getattr(args, "prepared_query_batch_segment_arrays", False)):
        if not bool(getattr(args, "prepared_lsi_base_session", False)) or query_chain_batches <= 0:
            raise ValueError(
                "--prepared-query-batch-segment-arrays requires "
                "--prepared-lsi-base-session with --query-chain-batches > 0"
            )
        if not bool(getattr(args, "device_columnar", False)):
            raise ValueError("--prepared-query-batch-segment-arrays requires --device-columnar")
    if bool(getattr(args, "prepared_lsi_base_workspace_warmup", False)):
        if not bool(getattr(args, "prepared_lsi_base_session", False)) or query_chain_batches <= 0:
            raise ValueError(
                "--prepared-lsi-base-workspace-warmup requires "
                "--prepared-lsi-base-session with --query-chain-batches > 0"
            )
        if not bool(getattr(args, "bounded_exact_lsi_device_columns", False)):
            raise ValueError("--prepared-lsi-base-workspace-warmup requires --bounded-exact-lsi-device-columns")
    if bool(getattr(args, "prepared_query_batch_lsi_query_workspaces", False)):
        if not bool(getattr(args, "prepared_lsi_base_session", False)) or query_chain_batches <= 0:
            raise ValueError(
                "--prepared-query-batch-lsi-query-workspaces requires "
                "--prepared-lsi-base-session with --query-chain-batches > 0"
            )
        if not bool(getattr(args, "bounded_exact_lsi_device_columns", False)):
            raise ValueError(
                "--prepared-query-batch-lsi-query-workspaces requires "
                "--bounded-exact-lsi-device-columns"
            )

    if bool(getattr(args, "prepared_operator_session", False)):
        if not bool(getattr(args, "device_columnar", False)):
            raise ValueError("--prepared-operator-session requires --device-columnar")
        session_phase_seconds = {}
        left = timed(
            "session_load_pack_left_sec",
            lambda: base.load_dataset_arrays(Path(args.left)),
            session_phase_seconds,
        )
        right = timed(
            "session_load_pack_right_sec",
            lambda: base.load_dataset_arrays(Path(args.right)),
            session_phase_seconds,
        )
        bounds = timed("session_shared_bounds_sec", lambda: base.shared_bounds(left, right), session_phase_seconds)
        map0_query_map_id = 1 if getattr(args, "swap_query_map_ids", False) else 0
        map1_query_map_id = 0 if getattr(args, "swap_query_map_ids", False) else 1
        lsi = query = map0_in_map1 = map1_in_map0 = None
        vertex_points_map0 = vertex_points_map1 = None
        device_segment_arrays_left = device_segment_arrays_right = None
        device_carrier_arrays_left = device_carrier_arrays_right = None
        try:
            lsi = timed(
                "session_prepare_lsi_right_sec",
                lambda: base.prepare_planar_map_lsi_2d_optix(right.lsi_segments),
                session_phase_seconds,
            )
            query = timed(
                "session_prepare_lsi_left_query_sec",
                lambda: lsi.prepare_query(left.lsi_segments),
                session_phase_seconds,
            )
            map0_in_map1 = timed(
                "session_prepare_point_location_map0_in_map1_sec",
                lambda: base.prepare_planar_map_point_location_2d_optix(
                    right.cdb_segments,
                    query_map_id=map0_query_map_id,
                    scale_bounds=bounds,
                ),
                session_phase_seconds,
            )
            map1_in_map0 = timed(
                "session_prepare_point_location_map1_in_map0_sec",
                lambda: base.prepare_planar_map_point_location_2d_optix(
                    left.cdb_segments,
                    query_map_id=map1_query_map_id,
                    scale_bounds=bounds,
                ),
                session_phase_seconds,
            )
            vertex_points_map0 = timed(
                "session_prepare_vertex_points_map0_in_map1_sec",
                lambda: map0_in_map1.prepare_query_points(left.points),
                session_phase_seconds,
            )
            vertex_points_map1 = timed(
                "session_prepare_vertex_points_map1_in_map0_sec",
                lambda: map1_in_map0.prepare_query_points(right.points),
                session_phase_seconds,
            )
            device_segment_arrays_left = timed(
                "session_prepare_reprojection_left_segment_device_arrays_sec",
                lambda: _copy_dataset_segment_arrays_to_device(left),
                session_phase_seconds,
            )
            device_segment_arrays_right = timed(
                "session_prepare_reprojection_right_segment_device_arrays_sec",
                lambda: _copy_dataset_segment_arrays_to_device(right),
                session_phase_seconds,
            )
            if bool(getattr(args, "device_resident_carrier", False)):
                device_carrier_arrays_left = timed(
                    "session_prepare_carrier_left_device_arrays_sec",
                    lambda: _copy_dataset_carrier_arrays_to_device(left),
                    session_phase_seconds,
                )
                device_carrier_arrays_right = timed(
                    "session_prepare_carrier_right_device_arrays_sec",
                    lambda: _copy_dataset_carrier_arrays_to_device(right),
                    session_phase_seconds,
                )
            setattr(args, "_preloaded_left", left)
            setattr(args, "_preloaded_right", right)
            setattr(args, "_preloaded_bounds", bounds)
            setattr(args, "_device_segment_arrays_left", device_segment_arrays_left)
            setattr(args, "_device_segment_arrays_right", device_segment_arrays_right)
            setattr(args, "_device_carrier_arrays_left", device_carrier_arrays_left)
            setattr(args, "_device_carrier_arrays_right", device_carrier_arrays_right)
            setattr(args, "_prepared_lsi_session", lsi)
            setattr(args, "_prepared_lsi_query", query)
            setattr(args, "_prepared_point_location_map0_in_map1", map0_in_map1)
            setattr(args, "_prepared_point_location_map1_in_map0", map1_in_map0)
            setattr(args, "_prepared_vertex_points_map0_in_map1", vertex_points_map0)
            setattr(args, "_prepared_vertex_points_map1_in_map0", vertex_points_map1)
            setattr(args, "_prepared_operator_session_active", True)
            warmup_summaries = [run_pipeline(args) for _ in range(warmup_runs)]
            measured_summaries = [run_pipeline(args) for _ in range(repeat)]
        finally:
            for name in (
                "_preloaded_left",
                "_preloaded_right",
                "_preloaded_bounds",
                "_device_segment_arrays_left",
                "_device_segment_arrays_right",
                "_device_carrier_arrays_left",
                "_device_carrier_arrays_right",
                "_prepared_lsi_session",
                "_prepared_lsi_query",
                "_prepared_point_location_map0_in_map1",
                "_prepared_point_location_map1_in_map0",
                "_prepared_vertex_points_map0_in_map1",
                "_prepared_vertex_points_map1_in_map0",
                "_prepared_operator_session_active",
            ):
                if hasattr(args, name):
                    delattr(args, name)
            for handle in (vertex_points_map1, vertex_points_map0, map1_in_map0, map0_in_map1, query, lsi):
                if handle is not None:
                    handle.close()
    else:
        session_phase_seconds = {}
        if bool(getattr(args, "prepared_lsi_base_session", False)):
            left = timed(
                "session_load_pack_left_sec",
                lambda: base.load_dataset_arrays(Path(args.left)),
                session_phase_seconds,
            )
            right = timed(
                "session_load_pack_right_sec",
                lambda: base.load_dataset_arrays(Path(args.right)),
                session_phase_seconds,
            )
            bounds = timed("session_shared_bounds_sec", lambda: base.shared_bounds(left, right), session_phase_seconds)
            lsi = None
            query_batch_right_vertex_locator = None
            query_batch_right_vertex_points = None
            query_batch_left_vertex_locator = None
            query_batch_left_vertex_points = []
            query_batch_lsi_queries = []
            query_batch_right_segment_arrays = None
            query_batch_left_segment_arrays = []
            query_batch_right_carrier_arrays = None
            query_batch_left_carrier_arrays = []
            try:
                lsi = timed(
                    "session_prepare_lsi_right_sec",
                    lambda: base.prepare_planar_map_lsi_2d_optix(right.lsi_segments),
                    session_phase_seconds,
                )
                setattr(args, "_preloaded_left", left)
                setattr(args, "_preloaded_right", right)
                setattr(args, "_preloaded_bounds", bounds)
                setattr(args, "_prepared_lsi_session", lsi)
                setattr(args, "_prepared_lsi_base_session_active", True)
                query_batches = _split_dataset_by_chain_batches(left, query_chain_batches)
                if query_batches and bool(getattr(args, "prepared_lsi_base_workspace_warmup", False)):
                    warmup_left = _slice_dataset_by_chain_range(left, start_chain=0, end_chain=1)

                    def _run_lsi_base_workspace_warmup():
                        warmup_phase = {}
                        warmup_native = {}
                        device_columns = produce_lsi_bounded_exact_device_columns_from_prepared_base(
                            lsi,
                            warmup_left,
                            warmup_phase,
                            warmup_native,
                            capacity=int(args.bounded_exact_lsi_capacity),
                        )
                        try:
                            session_phase_seconds[
                                "session_prepare_lsi_base_workspace_warmup_traversal_sec"
                            ] = float(device_columns.traversal_seconds)
                            for key, value in warmup_phase.items():
                                session_phase_seconds[
                                    f"session_prepare_lsi_base_workspace_warmup_{key}"
                                ] = float(value)
                            timing_keys = {
                                "count_download",
                                "device_alloc",
                                "exact_pipeline_ensure",
                                "grouped_range_ensure",
                                "optix_launch",
                                "param_upload",
                                "scaled_cache_ensure",
                                "split_kernel_ensure",
                                "split_kernel_launch",
                                "total_native",
                            }
                            for key, value in (warmup_native.get("extended") or {}).items():
                                if key in timing_keys and isinstance(value, (int, float, np.integer, np.floating)):
                                    session_phase_seconds[
                                        f"session_prepare_lsi_base_workspace_warmup_native_{key}"
                                    ] = float(value)
                        finally:
                            device_columns.close()

                    timed(
                        "session_prepare_lsi_base_workspace_warmup_sec",
                        _run_lsi_base_workspace_warmup,
                        session_phase_seconds,
                    )
                if query_batches and bool(getattr(args, "prepared_query_batch_lsi_query_workspaces", False)):
                    query_batch_lsi_queries = [
                        timed(
                            f"session_prepare_query_batch_{int(batch['index'])}_lsi_query_sec",
                            lambda batch=batch: lsi.prepare_query(batch["dataset"].lsi_segments),
                            session_phase_seconds,
                        )
                        for batch in query_batches
                    ]

                    for batch, prepared_query in zip(query_batches, query_batch_lsi_queries):
                        batch_index = int(batch["index"])

                        def _warm_query_batch_lsi_workspace(prepared_query=prepared_query):
                            warmup_phase = {}
                            warmup_native = {}
                            device_columns = produce_lsi_bounded_exact_device_columns_from_prepared_query(
                                lsi,
                                prepared_query,
                                warmup_phase,
                                warmup_native,
                                capacity=int(args.bounded_exact_lsi_capacity),
                            )
                            try:
                                for key, value in warmup_phase.items():
                                    session_phase_seconds[
                                        f"session_prepare_query_batch_{batch_index}_lsi_workspace_warmup_{key}"
                                    ] = float(value)
                                for key, value in (warmup_native.get("extended") or {}).items():
                                    if isinstance(value, (int, float, np.integer, np.floating)):
                                        session_phase_seconds[
                                            f"session_prepare_query_batch_{batch_index}_lsi_workspace_warmup_native_{key}"
                                        ] = float(value)
                            finally:
                                device_columns.close()

                        timed(
                            f"session_prepare_query_batch_{batch_index}_lsi_workspace_warmup_sec",
                            _warm_query_batch_lsi_workspace,
                            session_phase_seconds,
                        )
                if query_batches and bool(getattr(args, "prepared_query_batch_segment_arrays", False)):
                    query_batch_right_segment_arrays = timed(
                        "session_prepare_query_batch_right_segment_device_arrays_sec",
                        lambda: _copy_dataset_segment_arrays_to_device(right),
                        session_phase_seconds,
                    )
                    query_batch_left_segment_arrays = [
                        timed(
                            f"session_prepare_query_batch_{int(batch['index'])}_left_segment_device_arrays_sec",
                            lambda batch=batch: _copy_dataset_segment_arrays_to_device(batch["dataset"]),
                            session_phase_seconds,
                        )
                        for batch in query_batches
                    ]
                    setattr(args, "_device_segment_arrays_right", query_batch_right_segment_arrays)
                if query_batches and bool(getattr(args, "device_resident_carrier", False)):
                    query_batch_right_carrier_arrays = timed(
                        "session_prepare_query_batch_right_carrier_device_arrays_sec",
                        lambda: _copy_dataset_carrier_arrays_to_device(right),
                        session_phase_seconds,
                    )
                    query_batch_left_carrier_arrays = [
                        timed(
                            f"session_prepare_query_batch_{int(batch['index'])}_left_carrier_device_arrays_sec",
                            lambda batch=batch: _copy_dataset_carrier_arrays_to_device(batch["dataset"]),
                            session_phase_seconds,
                        )
                        for batch in query_batches
                    ]
                    setattr(args, "_device_carrier_arrays_right", query_batch_right_carrier_arrays)
                if query_batches and bool(getattr(args, "prepared_query_batch_right_vertex_points", False)):
                    map1_query_map_id = 0 if getattr(args, "swap_query_map_ids", False) else 1
                    query_batch_right_vertex_locator = timed(
                        "session_prepare_query_batch_right_vertex_point_locator_sec",
                        lambda: base.prepare_planar_map_point_location_2d_optix(
                            query_batches[0]["dataset"].cdb_segments,
                            query_map_id=map1_query_map_id,
                            scale_bounds=bounds,
                        ),
                        session_phase_seconds,
                    )
                    query_batch_right_vertex_points = timed(
                        "session_prepare_query_batch_right_vertex_points_sec",
                        lambda: query_batch_right_vertex_locator.prepare_query_points(right.points),
                        session_phase_seconds,
                    )
                    setattr(args, "_prepared_vertex_points_map1_in_map0", query_batch_right_vertex_points)
                if query_batches and bool(getattr(args, "prepared_query_batch_left_vertex_points", False)):
                    map0_query_map_id = 1 if getattr(args, "swap_query_map_ids", False) else 0
                    query_batch_left_vertex_locator = timed(
                        "session_prepare_query_batch_left_vertex_point_locator_sec",
                        lambda: base.prepare_planar_map_point_location_2d_optix(
                            right.cdb_segments,
                            query_map_id=map0_query_map_id,
                            scale_bounds=bounds,
                        ),
                        session_phase_seconds,
                    )
                    query_batch_left_vertex_points = [
                        timed(
                            f"session_prepare_query_batch_{int(batch['index'])}_left_vertex_points_sec",
                            lambda batch=batch: query_batch_left_vertex_locator.prepare_query_points(
                                batch["dataset"].points
                            ),
                            session_phase_seconds,
                        )
                        for batch in query_batches
                    ]
                    setattr(args, "_prepared_point_location_map0_in_map1", query_batch_left_vertex_locator)
                if query_batches:
                    warmup_summaries = []
                    measured_summaries = []
                    for batch in query_batches:
                        setattr(args, "_preloaded_left", batch["dataset"])
                        if query_batch_left_vertex_points:
                            setattr(
                                args,
                                "_prepared_vertex_points_map0_in_map1",
                                query_batch_left_vertex_points[int(batch["index"])],
                            )
                        if bool(getattr(args, "prepared_query_batch_segment_arrays", False)):
                            setattr(
                                args,
                                "_device_segment_arrays_left",
                                query_batch_left_segment_arrays[int(batch["index"])],
                            )
                        if bool(getattr(args, "device_resident_carrier", False)):
                            setattr(
                                args,
                                "_device_carrier_arrays_left",
                                query_batch_left_carrier_arrays[int(batch["index"])],
                            )
                        if query_batch_lsi_queries:
                            setattr(args, "_prepared_lsi_query", query_batch_lsi_queries[int(batch["index"])])
                        summary = run_pipeline(args)
                        summary["query_batch"] = {
                            "index": int(batch["index"]),
                            "start_chain": int(batch["start_chain"]),
                            "end_chain": int(batch["end_chain"]),
                            "chain_count": int(batch["dataset"].chain_count),
                            "point_count": int(batch["dataset"].point_count),
                            "edge_count": int(batch["dataset"].edge_count),
                        }
                        measured_summaries.append(summary)
                else:
                    warmup_summaries = [run_pipeline(args) for _ in range(warmup_runs)]
                    measured_summaries = [run_pipeline(args) for _ in range(repeat)]
            finally:
                for name in (
                    "_preloaded_left",
                    "_preloaded_right",
                    "_preloaded_bounds",
                    "_prepared_lsi_session",
                    "_prepared_lsi_query",
                    "_prepared_lsi_base_session_active",
                    "_prepared_point_location_map0_in_map1",
                    "_prepared_vertex_points_map0_in_map1",
                    "_prepared_vertex_points_map1_in_map0",
                    "_device_segment_arrays_left",
                    "_device_segment_arrays_right",
                    "_device_carrier_arrays_left",
                    "_device_carrier_arrays_right",
                ):
                    if hasattr(args, name):
                        delattr(args, name)
                if query_batch_right_vertex_points is not None:
                    query_batch_right_vertex_points.close()
                if query_batch_right_vertex_locator is not None:
                    query_batch_right_vertex_locator.close()
                for prepared_points in query_batch_left_vertex_points:
                    prepared_points.close()
                if query_batch_left_vertex_locator is not None:
                    query_batch_left_vertex_locator.close()
                for prepared_query in query_batch_lsi_queries:
                    prepared_query.close()
                if lsi is not None:
                    lsi.close()
        else:
            warmup_summaries = [run_pipeline(args) for _ in range(warmup_runs)]
            measured_summaries = [run_pipeline(args) for _ in range(repeat)]
    return summarize_repeat_protocol(
        args=args,
        warmup_summaries=warmup_summaries,
        measured_summaries=measured_summaries,
        session_prepare_phase_seconds=session_phase_seconds,
    )


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
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help=(
            "Run the writer-free binary route multiple times in the same process after "
            "optional warmup runs. With --prepared-operator-session this is a prepared "
            "operator body measurement, not a fresh one-shot headline or a true "
            "query-many proof."
        ),
    )
    parser.add_argument(
        "--warmup-runs",
        type=int,
        default=0,
        help=(
            "Same-process warmup runs excluded from repeat medians. Warmup rows remain "
            "reported so the prepared/query-many boundary is auditable."
        ),
    )
    parser.add_argument(
        "--prepared-operator-session",
        action="store_true",
        help=(
            "For repeat measurements, load datasets and prepare reusable LSI/PIP sessions once, "
            "then run warmup/measured binary operator iterations against those prepared handles. "
            "This measures prepared operator body cost after explicit prepare; it is not a fresh "
            "one-shot headline and not a true query-many proof without distinct query batches."
        ),
    )
    parser.add_argument(
        "--prepared-lsi-base-session",
        action="store_true",
        help=(
            "For repeat measurements, prepare only the LSI base/right planar-map session once, "
            "then build a fresh LSI query object for each measured overlay route. This is not "
            "same-query replay and not a true query-many proof without distinct query batches."
        ),
    )
    parser.add_argument(
        "--query-chain-batches",
        type=int,
        default=0,
        help=(
            "With --prepared-lsi-base-session, split the left dataset into this many contiguous "
            "chain batches and run each batch as a distinct full overlay query against the same "
            "prepared LSI base. This is an app-level query-many probe, not a paper-text route."
        ),
    )
    parser.add_argument(
        "--prepared-query-batch-right-vertex-points",
        action="store_true",
        help=(
            "With --prepared-lsi-base-session and --query-chain-batches, prepare the unchanged "
            "right-side vertex query-point buffer once and reuse it for map1-in-map0 PIP across "
            "the distinct left chain batches. This is a prepared query-batch route, not a fresh "
            "one-shot headline."
        ),
    )
    parser.add_argument(
        "--prepared-query-batch-left-vertex-points",
        action="store_true",
        help=(
            "With --prepared-lsi-base-session and --query-chain-batches, prepare each left "
            "batch's vertex query-point buffer once during session preparation and reuse it "
            "for map0-in-map1 PIP in the measured body. This is a prepared query-batch route, "
            "not a cold CLI or paper-text headline."
        ),
    )
    parser.add_argument(
        "--prepared-query-batch-segment-arrays",
        action="store_true",
        help=(
            "With --prepared-lsi-base-session and --query-chain-batches, prepare the unchanged "
            "right-side segment arrays once and each left batch segment array once for the "
            "device-columnar reprojection stage. This is a prepared query-batch route, not a "
            "fresh one-shot headline."
        ),
    )
    parser.add_argument(
        "--prepared-lsi-base-workspace-warmup",
        action="store_true",
        help=(
            "With --prepared-lsi-base-session and --query-chain-batches, run one tiny "
            "unmeasured LSI query during session preparation to build reusable base "
            "workspace before measured query batches. This is a prepared service route, "
            "not a cold CLI or same-query replay headline."
        ),
    )
    parser.add_argument(
        "--prepared-query-batch-lsi-query-workspaces",
        action="store_true",
        help=(
            "With --prepared-lsi-base-session and --query-chain-batches, prepare and warm "
            "each distinct batch's LSI query workspace during session preparation. Measured "
            "rows still recompute LSI pair-id device columns; this only moves scaled-cache "
            "workspace setup out of the hot query-batch body."
        ),
    )
    parser.add_argument(
        "--device-columnar",
        action="store_true",
        help="Use Numba CUDA for numeric xsect reprojection and xsect sort ordering.",
    )
    parser.add_argument(
        "--validate-device-order",
        action="store_true",
        help="Compare Numba CUDA sort order against the CPU longdouble reference and fail closed on mismatch.",
    )
    parser.add_argument(
        "--native-lexsort",
        action="store_true",
        help=(
            "Use the optional native CUDA/Thrust generic lexsort helper for device-columnar "
            "intersection ordering. This is an opt-in probe; the default remains the Numba "
            "bitonic implementation until POD evidence shows it wins."
        ),
    )
    parser.add_argument(
        "--compiled-group",
        action="store_true",
        help="Use Numba-compiled columnar group construction for the writer-free binary carrier.",
    )
    parser.add_argument(
        "--device-resident-carrier",
        action="store_true",
        help=(
            "Use an experimental app-layer CUDA carrier and descriptor consumer for the "
            "writer-free binary route. This requires --device-columnar, point-location "
            "device face columns, and exact LSI device columns; it is not a RTDL core "
            "RayJoin primitive."
        ),
    )
    parser.add_argument(
        "--device-carrier-concurrent-sides",
        action="store_true",
        help=(
            "Experimental writer-free binary route optimization: launch the two "
            "device-resident carrier side append kernels on separate CUDA streams. "
            "This is valid only for the binary descriptor route where carrier row order "
            "is not a paper-text ordering contract."
        ),
    )
    parser.add_argument(
        "--compiled-group-side-order",
        default="0,1",
        help=(
            "Diagnostic order for the two compiled carrier side-builder calls. "
            "Allowed values: 0,1 or 1,0. This is a side-order/locality diagnostic, "
            "not a paper-text ordering policy or author-performance headline."
        ),
    )
    parser.add_argument(
        "--prepared-lsi-replay",
        action="store_true",
        help=(
            "Measure the LSI phase as a prepared hot replay: build the public LSI session, "
            "explicitly prepare the reusable planar-map LSI workspace, then feed a hot "
            "exact pair-id replay into the writer-free binary route. The workspace and "
            "prepare costs remain reported "
            "outside writer_free_hot_sec."
        ),
    )
    parser.add_argument(
        "--exact-lsi-device-columns",
        action="store_true",
        help=(
            "Use the exact planar-map LSI pair-id device-column route before copying into "
            "the current NumPy downstream app path. This is a measurement route, not an "
            "end-to-end zero-copy claim."
        ),
    )
    parser.add_argument(
        "--bounded-exact-lsi-device-columns",
        action="store_true",
        help=(
            "Use a bounded single-pass exact planar-map LSI pair-id device-column route. "
            "The route fails closed on overflow and is a measurement route, not an "
            "end-to-end zero-copy claim."
        ),
    )
    parser.add_argument(
        "--bounded-exact-lsi-capacity",
        type=int,
        default=0,
        help="Maximum exact LSI pair rows for --bounded-exact-lsi-device-columns.",
    )
    parser.add_argument(
        "--bounded-exact-lsi-repeat-diagnostic",
        type=int,
        default=0,
        help=(
            "Diagnostic-only same-process repeat count for bounded exact LSI device-column "
            "runs on one prepared query. Used to separate first-run setup from steady-state "
            "bounded exact LSI cost."
        ),
    )
    parser.add_argument(
        "--point-location-device-face-columns",
        action="store_true",
        help=(
            "Use generic directed point-location face-id device columns for PIP phases, "
            "then explicitly copy the face-id column to NumPy for the current downstream "
            "RayJoin app path. This is a measurement route, not a true-zero-copy claim."
        ),
    )
    parser.add_argument(
        "--fast-scaled-point-pack",
        action="store_true",
        help=(
            "Use vectorized host packing for midpoint scaled query points while preserving "
            "the existing scaled-point ABI. This removes per-row ctypes object construction "
            "but is still host packing, not a device-resident prepared-points claim."
        ),
    )
    parser.add_argument(
        "--generic-lsi-prewarm",
        action="store_true",
        help=(
            "Run a tiny generic planar-map LSI prewarm before the measured route. The prewarm "
            "time is reported separately and is not part of writer_free_hot_sec; this is a "
            "warm long-lived-process route option, not a cold CLI one-shot speedup claim."
        ),
    )
    args = parser.parse_args()

    if args.cache_dir:
        import os

        old_cache_dir = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))
    else:
        old_cache_dir = None
    try:
        if not args.no_numba_warmup:
            _warm_numba()
            if args.device_columnar:
                _warm_numba_cuda_device_columnar()
        generic_lsi_prewarm = _generic_lsi_tiny_prewarm() if args.generic_lsi_prewarm else None
        summary = run_pipeline_repeat_protocol(args)
        if generic_lsi_prewarm is not None:
            summary["generic_lsi_prewarm"] = generic_lsi_prewarm
            summary["generic_lsi_prewarm_requested"] = True
            summary["generic_lsi_prewarm_time_excluded_from_writer_free_hot"] = True
            summary["cold_cli_one_shot_speedup_claim_authorized"] = False
            if isinstance(summary.get("claim_boundary"), dict):
                summary["claim_boundary"]["generic_lsi_prewarm_requested"] = True
                summary["claim_boundary"]["generic_lsi_prewarm_time_excluded_from_writer_free_hot"] = True
                summary["claim_boundary"]["cold_cli_one_shot_speedup_claim_authorized"] = False
    finally:
        if args.cache_dir:
            import os

            if old_cache_dir is None:
                os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
            else:
                os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_cache_dir

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
