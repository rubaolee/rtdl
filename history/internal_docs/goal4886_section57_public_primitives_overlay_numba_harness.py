#!/usr/bin/env python3
"""Goal4886 Numba-enabled Section 5.7 public-primitives harness.

This wrapper keeps the proven Goal4880 public RTDL route intact, then replaces
selected Python app-layer continuation helpers with Goal4886 Numba partner
helpers when Numba is available.

It deliberately does not modify RTDL core and does not import
``rtdsl.rayjoin_overlay``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import numpy as np


THIS_DIR = Path(__file__).resolve().parent
GOAL4880 = THIS_DIR / "goal4880_section57_public_primitives_overlay_harness.py"
KERNELS = THIS_DIR / "goal4886_rayjoin_numba_overlay_kernels.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load_module(GOAL4880, "goal4880_section57_public_primitives_overlay_harness")
kernels = _load_module(KERNELS, "goal4886_rayjoin_numba_overlay_kernels")


def midpoint_points_numba_enabled(xsects, map_index: int, *, scale_bounds):
    edge_attr = "eid0" if map_index == 0 else "eid1"
    *_, rrx, rry, ddeltax, ddeltay = base._rayjoin_scaling_constants(scale_bounds)
    if not xsects:
        return [], [], []
    edge_ids = np.asarray([int(getattr(row, edge_attr)) for row in xsects], dtype=np.int64)
    scaled_x = np.asarray([int(row.scaled_x) for row in xsects], dtype=np.int64)
    scaled_y = np.asarray([int(row.scaled_y) for row in xsects], dtype=np.int64)
    sx, sy, owner_indices = kernels.midpoint_pairs_numba(edge_ids, scaled_x, scaled_y)
    midpoints = [(float(x) * rrx + ddeltax, float(y) * rry + ddeltay) for x, y in zip(sx, sy)]
    scaled_midpoints = [(int(x), int(y)) for x, y in zip(sx, sy)]
    owners = [xsects[int(index)] for index in owner_indices]
    return midpoints, scaled_midpoints, owners


def dedupe_point_pairs_numba_enabled(points, display_points):
    if not points:
        return points, display_points
    if display_points is points:
        x = np.asarray([float(point[0]) for point in points], dtype=np.float64)
        y = np.asarray([float(point[1]) for point in points], dtype=np.float64)
        keep = kernels.dedupe_consecutive_points_numba(x, y)
        out_points = [point for point, flag in zip(points, keep) if bool(flag)]
        return out_points, out_points
    x = np.asarray([float(point[0]) for point in points], dtype=np.float64)
    y = np.asarray([float(point[1]) for point in points], dtype=np.float64)
    keep = kernels.dedupe_consecutive_points_numba(x, y)
    out_points = [point for point, flag in zip(points, keep) if bool(flag)]
    out_display = [display for display, flag in zip(display_points, keep) if bool(flag)]
    return out_points, out_display


def _writer_skip_plan(dataset, point_faces_for_map, xsects, map_index: int):
    edge_attr = "eid0" if map_index == 0 else "eid1"
    xsect_edge_ids = np.asarray([int(getattr(row, edge_attr)) for row in xsects], dtype=np.int64)
    has_xsects = kernels.chain_has_xsects_numba(
        np.asarray(dataset.chain_offsets, dtype=np.int64),
        np.asarray(dataset.chain_point_counts, dtype=np.int64),
        xsect_edge_ids,
    )
    last_point_indices = (
        np.asarray(dataset.chain_offsets, dtype=np.int64)
        + np.asarray(dataset.chain_point_counts, dtype=np.int64)
        - 1
    )
    terminal_other_faces = np.asarray(point_faces_for_map[last_point_indices], dtype=np.int64)
    terminal_keep = kernels.chain_keep_numba(
        np.asarray(dataset.chain_left_faces, dtype=np.int64),
        np.asarray(dataset.chain_right_faces, dtype=np.int64),
        terminal_other_faces,
    )
    skip_chain = kernels.writer_skip_decision_numba(has_xsects, terminal_keep)
    return has_xsects, terminal_keep, skip_chain


def write_output_chains_streaming_numba_skip(
    datasets,
    xsects_sorted,
    point_faces,
    output_path: Path,
):
    """Goal4886 writer wrapper with a Numba-generated no-output skip plan.

    This preserves the Goal4880 writer semantics. It only skips a chain before
    entering the per-point Python loop when both are true:

    - the chain has no intersection edge;
    - the current writer's terminal-face keep rule would drop the chain anyway.

    Chains with intersections and chains that the current writer would keep are
    still processed by the original Python writer logic.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    face_ids: dict[tuple[int, int], int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    point_counter = 0
    chain_count = 0
    line_count = 0
    streamed_point_count = 0
    skipped_no_xsect_chains = 0
    skipped_no_xsect_points = 0
    processed_chains = 0
    descriptor_direct_chains = 0
    descriptor_direct_points = 0
    output_lines: list[str] = []
    writer_phase_seconds: dict[str, float] = {}
    point_records: dict[tuple[float, float], tuple[int, str]] = {}
    display_line_cache: dict[tuple[float, float], str] = {}
    skip_start = time.perf_counter()
    skip_plans = [
        _writer_skip_plan(datasets[0], point_faces[0], xsects_sorted[0], 0),
        _writer_skip_plan(datasets[1], point_faces[1], xsects_sorted[1], 1),
    ]
    writer_phase_seconds["skip_plan_sec"] = time.perf_counter() - skip_start
    dump_center_env = os.environ.get("RTDL_DUMP_OUTPUT_CHAIN_INDEX")
    dump_radius_env = os.environ.get("RTDL_DUMP_OUTPUT_CHAIN_RADIUS")
    dump_center = int(dump_center_env) if dump_center_env is not None else None
    dump_radius = int(dump_radius_env) if dump_radius_env is not None else 2

    def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
        return face_ids[key]

    def point_record(point: tuple[float, float]) -> tuple[int, str]:
        nonlocal point_counter
        record = point_records.get(point)
        if record is None:
            record = (point_counter, f"{point[0]:.6f} {point[1]:.6f}\n")
            point_records[point] = record
            point_counter += 1
        return record

    def display_line(point: tuple[float, float]) -> str:
        line = display_line_cache.get(point)
        if line is None:
            line = f"{point[0]:.6f} {point[1]:.6f}\n"
            display_line_cache[point] = line
        return line

    def emit_direct_dataset_chain(
        dataset,
        chain_index: int,
        point_offset: int,
        point_count: int,
        other_map_polygon_id: int,
    ) -> None:
        nonlocal chain_count, line_count, streamed_point_count
        left_raw = int(dataset.chain_left_faces[chain_index])
        right_raw = int(dataset.chain_right_faces[chain_index])
        keep = (
            left_raw * other_map_polygon_id != 0
            or right_raw * other_map_polygon_id != 0
        )
        if not keep or point_count <= 0:
            return
        point_lines: list[str] = []
        first_point_idx: int | None = None
        last_point_idx = 0
        last_point: tuple[float, float] | None = None
        point_stop = point_offset + point_count
        for point_index in range(point_offset, point_stop):
            point = (float(dataset.point_x[point_index]), float(dataset.point_y[point_index]))
            if last_point is not None and point == last_point:
                continue
            point_idx, line = point_record(point)
            if first_point_idx is None:
                first_point_idx = point_idx
            last_point_idx = point_idx
            point_lines.append(line)
            last_point = point
        if first_point_idx is None:
            return
        other = int(other_map_polygon_id)
        left_polygon_id = create_polygon(*sorted((left_raw, other)))
        right_polygon_id = create_polygon(*sorted((right_raw, other)))
        chain_count += 1
        output_lines.append(
            f"{chain_count} {len(point_lines)} {first_point_idx} {last_point_idx} "
            f"{left_polygon_id} {right_polygon_id}\n"
        )
        output_lines.extend(point_lines)
        line_count += 1 + len(point_lines)
        streamed_point_count += len(point_lines)

    def flush(output_chain):
        nonlocal chain_count, line_count, streamed_point_count
        if not output_chain.points:
            return
        if output_chain.display_points is None:
            output_chain.display_points = output_chain.points
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            points, display_points = base.dedupe_point_pairs(output_chain.points, output_chain.display_points)
            raw_chain_index = chain_count
            if dump_center is not None and abs(raw_chain_index - dump_center) <= dump_radius:
                print(
                    "RTDL_DUMP raw_index="
                    f"{raw_chain_index} output_chain_no={raw_chain_index + 1} "
                    f"point_count={len(points)} left={int(output_chain.left_polygon_id)} "
                    f"right={int(output_chain.right_polygon_id)} "
                    f"other={int(output_chain.other_map_polygon_id)} "
                    f"context={output_chain.debug_context}",
                    file=sys.stderr,
                    flush=True,
                )
                for point_index, point in enumerate(display_points):
                    print(
                        "RTDL_DUMP point raw_index="
                        f"{raw_chain_index} point_index={point_index} "
                        f"x={point[0]} y={point[1]}",
                        file=sys.stderr,
                        flush=True,
                    )
            other = int(output_chain.other_map_polygon_id)
            left_polygon_id = create_polygon(*sorted((int(output_chain.left_polygon_id), other)))
            right_polygon_id = create_polygon(*sorted((int(output_chain.right_polygon_id), other)))
            records = [point_record(point) for point in points]
            first_point_idx = records[0][0]
            last_point_idx = records[-1][0]
            chain_count += 1
            output_lines.append(
                f"{chain_count} {len(points)} {first_point_idx} {last_point_idx} "
                f"{left_polygon_id} {right_polygon_id}\n"
            )
            line_count += 1
            if display_points is points:
                for _, line in records:
                    output_lines.append(line)
                    line_count += 1
                    streamed_point_count += 1
            else:
                for point in display_points:
                    output_lines.append(display_line(point))
                    line_count += 1
                    streamed_point_count += 1
        output_chain.points.clear()
        if output_chain.display_points is not None and output_chain.display_points is not output_chain.points:
            output_chain.display_points.clear()

    def flush_plain_chain(
        points: list[tuple[float, float]],
        left_raw: int,
        right_raw: int,
        other_map_polygon_id: int,
    ) -> None:
        nonlocal chain_count, line_count, streamed_point_count
        if not points:
            return
        keep = (
            left_raw * other_map_polygon_id != 0
            or right_raw * other_map_polygon_id != 0
        )
        if keep:
            deduped_points, display_points = base.dedupe_point_pairs(points, points)
            if deduped_points:
                other = int(other_map_polygon_id)
                left_polygon_id = create_polygon(*sorted((int(left_raw), other)))
                right_polygon_id = create_polygon(*sorted((int(right_raw), other)))
                records = [point_record(point) for point in deduped_points]
                first_point_idx = records[0][0]
                last_point_idx = records[-1][0]
                chain_count += 1
                output_lines.append(
                    f"{chain_count} {len(deduped_points)} {first_point_idx} {last_point_idx} "
                    f"{left_polygon_id} {right_polygon_id}\n"
                )
                line_count += 1
                if display_points is deduped_points:
                    for _, line in records:
                        output_lines.append(line)
                        line_count += 1
                        streamed_point_count += 1
                else:
                    for point in display_points:
                        output_lines.append(display_line(point))
                        line_count += 1
                        streamed_point_count += 1
        points.clear()

    with output_path.open("w", encoding="utf-8") as handle:
        for map_index, dataset in enumerate(datasets):
            edge_attr = "eid0" if map_index == 0 else "eid1"
            group_start = time.perf_counter()
            grouped: dict[int, list[object]] = {}
            for xsect in xsects_sorted[map_index]:
                grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
            writer_phase_seconds[f"group_xsects_map{map_index}_sec"] = time.perf_counter() - group_start
            has_xsects, terminal_keep, skip_chain = skip_plans[map_index]
            edge_id = 0
            loop_start = time.perf_counter()
            for chain_index in range(dataset.chain_count):
                point_offset = int(dataset.chain_offsets[chain_index])
                point_count = int(dataset.chain_point_counts[chain_index])
                if bool(skip_chain[chain_index]):
                    skipped_no_xsect_chains += 1
                    skipped_no_xsect_points += point_count
                    edge_id += max(0, point_count - 1)
                    continue
                processed_chains += 1
                if not bool(has_xsects[chain_index]):
                    descriptor_direct_chains += 1
                    descriptor_direct_points += point_count
                    emit_direct_dataset_chain(
                        dataset,
                        chain_index,
                        point_offset,
                        point_count,
                        int(point_faces[map_index][point_offset + point_count - 1]),
                    )
                    edge_id += max(0, point_count - 1)
                    continue
                points: list[tuple[float, float]] = []
                left_raw = int(dataset.chain_left_faces[chain_index])
                right_raw = int(dataset.chain_right_faces[chain_index])
                other_map_polygon_id = 0
                for local_point_index in range(point_count):
                    point_index = point_offset + local_point_index
                    other_map_polygon_id = int(point_faces[map_index][point_index])
                    points.append((float(dataset.point_x[point_index]), float(dataset.point_y[point_index])))
                    if local_point_index == point_count - 1:
                        continue
                    xsects = grouped.get(edge_id)
                    if xsects:
                        first_point = base.xsect_output_point(xsects[0])
                        points.append(first_point)
                        for xsect, next_xsect in zip(xsects, xsects[1:]):
                            flush_plain_chain(points, left_raw, right_raw, other_map_polygon_id)
                            other_map_polygon_id = base.midpoint_face_for_map(xsect, map_index)
                            xsect_point = base.xsect_output_point(xsect)
                            next_xsect_point = base.xsect_output_point(next_xsect)
                            points.append(xsect_point)
                            points.append(next_xsect_point)
                        flush_plain_chain(points, left_raw, right_raw, other_map_polygon_id)
                        last_point = base.xsect_output_point(xsects[-1])
                        points.append(last_point)
                    edge_id += 1
                flush_plain_chain(points, left_raw, right_raw, other_map_polygon_id)
            writer_phase_seconds[f"chain_loop_map{map_index}_sec"] = time.perf_counter() - loop_start
        write_start = time.perf_counter()
        handle.writelines(output_lines)
        writer_phase_seconds["bulk_writelines_sec"] = time.perf_counter() - write_start
    return {
        "path": str(output_path),
        "chain_count": chain_count,
        "face_count": len(face_ids),
        "line_count": line_count,
        "point_count": streamed_point_count,
        "goal4886_writer_skip_plan": {
            "skipped_no_xsect_chains": skipped_no_xsect_chains,
            "skipped_no_xsect_points": skipped_no_xsect_points,
            "processed_chains": processed_chains,
            "descriptor_direct_chains": descriptor_direct_chains,
            "descriptor_direct_points": descriptor_direct_points,
            "numba_available": bool(kernels.NUMBA_AVAILABLE),
        },
        "goal4905_writer_phase_seconds": writer_phase_seconds,
        "buffered_output_line_count": len(output_lines),
        "goal4907_writer_cache_counts": {
            "unique_point_records": len(point_records),
            "unique_display_lines": len(display_line_cache),
        },
    }


def _summary_arg(argv: list[str]) -> Path | None:
    for index, value in enumerate(argv):
        if value == "--summary" and index + 1 < len(argv):
            return Path(argv[index + 1])
        if value.startswith("--summary="):
            return Path(value.split("=", 1)[1])
    return None


def main() -> None:
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected before Goal4886 wrapper start")

    wrapper_start = time.perf_counter()
    base.midpoint_points = midpoint_points_numba_enabled
    base.dedupe_point_pairs = dedupe_point_pairs_numba_enabled
    base.write_output_chains_streaming = write_output_chains_streaming_numba_skip
    base.main()

    summary_path = _summary_arg(sys.argv[1:])
    if summary_path is not None and summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        payload["schema"] = "rtdl.goal4886.section57_public_primitives_overlay_numba_harness.v1"
        payload["route"] = "public_rtdl_lsi_pip_plus_numba_partner_app_continuation"
        payload.setdefault("claim_boundary", {})
        payload["claim_boundary"]["numba_on_app_continuation_path"] = bool(kernels.NUMBA_AVAILABLE)
        payload["claim_boundary"]["numba_on_rtdl_primitive_path"] = False
        payload["claim_boundary"]["numba_available"] = bool(kernels.NUMBA_AVAILABLE)
        payload["claim_boundary"]["numba_kernel_module"] = str(KERNELS)
        payload["phase_seconds"]["goal4886_wrapper_total_sec"] = time.perf_counter() - wrapper_start
        summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
