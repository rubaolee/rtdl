"""Goal4951 Section 5.7 app adapter for compiled generic path splitting.

This is an internal Gate C/D experiment. The generic compiled materializer
lives in ``goal4951_compiled_path_split_spike.py``; this file owns the
paper-reproduction application mapping and final text formatting.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

from rtdsl.output_assembly import materialize_grouped_output_row_buffer


ROOT = Path(__file__).resolve().parents[2]
SECTION57_OVERLAY = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay.py"
SPIKE = ROOT / "history" / "internal_docs" / "goal4951_compiled_path_split_spike.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load_module(SECTION57_OVERLAY, "goal4951_base_section57_overlay")
spike = _load_module(SPIKE, "goal4951_compiled_path_split_spike")


def _edge_lookup(dataset):
    edge_chain = np.empty(int(dataset.edge_count), dtype=np.int64)
    edge_local = np.empty(int(dataset.edge_count), dtype=np.int64)
    cursor = 0
    for chain_index, point_count in enumerate(dataset.chain_point_counts):
        local_edges = max(0, int(point_count) - 1)
        if local_edges:
            stop = cursor + local_edges
            edge_chain[cursor:stop] = int(chain_index)
            edge_local[cursor:stop] = np.arange(local_edges, dtype=np.int64)
            cursor = stop
    if cursor != int(dataset.edge_count):
        raise ValueError(f"edge lookup mismatch: {cursor} != {dataset.edge_count}")
    return edge_chain, edge_local


def _interval_other_face(dataset, point_faces_for_map, events, event_index, map_index):
    if not events:
        return 0
    chain_index = int(events[0][3])
    point_offset = int(dataset.chain_offsets[chain_index])
    point_count = int(dataset.chain_point_counts[chain_index])
    if point_count <= 0:
        return 0
    if event_index == len(events):
        return int(point_faces_for_map[point_offset + point_count - 1])
    edge_order, _event_order, xsect, _chain_index = events[event_index]
    if event_index > 0:
        prev_edge, _prev_order, prev_xsect, _prev_chain = events[event_index - 1]
        if int(prev_edge) == int(edge_order):
            return int(base.midpoint_face_for_map(prev_xsect, map_index))
    return int(point_faces_for_map[point_offset + int(edge_order)])


def _build_path_split_inputs(dataset, xsects, point_faces_for_map, map_index):
    edge_attr = "eid0" if map_index == 0 else "eid1"
    edge_chain, edge_local = _edge_lookup(dataset)
    events_by_chain: list[list[tuple[int, int, object, int]]] = [
        [] for _ in range(int(dataset.chain_count))
    ]
    per_edge_order: dict[int, int] = {}
    split_chain_ids: list[int] = []
    split_edge_orders: list[int] = []
    split_event_orders: list[int] = []
    split_x: list[float] = []
    split_y: list[float] = []

    for xsect in xsects:
        edge_id = int(getattr(xsect, edge_attr))
        chain_index = int(edge_chain[edge_id])
        local_edge = int(edge_local[edge_id])
        event_order = int(per_edge_order.get(edge_id, 0))
        per_edge_order[edge_id] = event_order + 1
        x, y = base.xsect_output_point(xsect)
        split_chain_ids.append(chain_index)
        split_edge_orders.append(local_edge)
        split_event_orders.append(event_order)
        split_x.append(float(x))
        split_y.append(float(y))
        events_by_chain[chain_index].append((local_edge, event_order, xsect, chain_index))

    chain_ids = np.arange(int(dataset.chain_count), dtype=np.int64)
    left_raw: list[int] = []
    right_raw: list[int] = []
    other_face: list[int] = []
    validity: list[bool] = []
    group_ids: list[int] = []
    group_id = 1

    for chain_index in range(int(dataset.chain_count)):
        events = sorted(events_by_chain[chain_index], key=lambda item: (item[0], item[1]))
        if not events:
            fake_events = [(0, 0, None, chain_index)]
            event_count = 0
        else:
            fake_events = events
            event_count = len(events)
        for interval_index in range(event_count + 1):
            left = int(dataset.chain_left_faces[chain_index])
            right = int(dataset.chain_right_faces[chain_index])
            if events:
                other = _interval_other_face(dataset, point_faces_for_map, events, interval_index, map_index)
            else:
                point_offset = int(dataset.chain_offsets[chain_index])
                point_count = int(dataset.chain_point_counts[chain_index])
                other = (
                    int(point_faces_for_map[point_offset + point_count - 1])
                    if point_count > 0
                    else 0
                )
            left_raw.append(left)
            right_raw.append(right)
            other_face.append(other)
            validity.append(bool(left * other != 0 or right * other != 0))
            group_ids.append(group_id)
            group_id += 1
        del fake_events

    return {
        "chain_ids": chain_ids,
        "chain_point_offsets": np.asarray(dataset.chain_offsets, dtype=np.int64),
        "chain_point_counts": np.asarray(dataset.chain_point_counts, dtype=np.int64),
        "point_x": np.asarray(dataset.point_x, dtype=np.float64),
        "point_y": np.asarray(dataset.point_y, dtype=np.float64),
        "split_chain_ids": np.asarray(split_chain_ids, dtype=np.int64),
        "split_edge_orders": np.asarray(split_edge_orders, dtype=np.int64),
        "split_event_orders": np.asarray(split_event_orders, dtype=np.int64),
        "split_x": np.asarray(split_x, dtype=np.float64),
        "split_y": np.asarray(split_y, dtype=np.float64),
        "interval_descriptor_columns": {
            "left_raw": np.asarray(left_raw, dtype=np.int64),
            "right_raw": np.asarray(right_raw, dtype=np.int64),
            "other_face": np.asarray(other_face, dtype=np.int64),
        },
        "interval_validity": np.asarray(validity, dtype=np.bool_),
        "output_group_ids": np.asarray(group_ids, dtype=np.int64),
    }


def write_output_chains_streaming_compiled_path_split(
    datasets,
    xsects_sorted,
    point_faces,
    output_path: Path,
):
    if not spike.NUMBA_AVAILABLE:
        raise RuntimeError("Goal4951 compiled path-split adapter requires numba")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    phase_seconds: dict[str, float] = {}
    face_ids: dict[tuple[int, int], int] = {}
    point_records: dict[tuple[float, float], tuple[int, str]] = {}
    point_counter = 0
    chain_count = 0
    line_count = 0
    streamed_point_count = 0
    output_lines: list[str] = []

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

    for map_index, dataset in enumerate(datasets):
        build_start = time.perf_counter()
        inputs = _build_path_split_inputs(dataset, xsects_sorted[map_index], point_faces[map_index], map_index)
        phase_seconds[f"build_path_split_inputs_map{map_index}_sec"] = time.perf_counter() - build_start

        compile_start = time.perf_counter()
        row_buffer = spike.assemble_compiled_path_split_records(**inputs)
        materialized = materialize_grouped_output_row_buffer(row_buffer)
        phase_seconds[f"compiled_path_split_materialize_map{map_index}_sec"] = time.perf_counter() - compile_start

        format_start = time.perf_counter()
        for group_index in range(materialized.group_count):
            rows = materialized.group_slice(group_index)
            points = [
                (float(x), float(y))
                for x, y in zip(
                    materialized.item_columns["x"][rows],
                    materialized.item_columns["y"][rows],
                )
            ]
            if not points:
                continue
            left = int(materialized.descriptor_columns["left_raw"][group_index])
            right = int(materialized.descriptor_columns["right_raw"][group_index])
            other = int(materialized.descriptor_columns["other_face"][group_index])
            left_polygon_id = create_polygon(*sorted((left, other)))
            right_polygon_id = create_polygon(*sorted((right, other)))
            records = [point_record(point) for point in points]
            first_point_idx = records[0][0]
            last_point_idx = records[-1][0]

            chain_count += 1
            output_lines.append(
                f"{chain_count} {len(points)} {first_point_idx} {last_point_idx} "
                f"{left_polygon_id} {right_polygon_id}\n"
            )
            for _point_id, line in records:
                output_lines.append(line)
            line_count += 1 + len(points)
            streamed_point_count += len(points)
        phase_seconds[f"format_compiled_path_split_map{map_index}_sec"] = time.perf_counter() - format_start

    write_start = time.perf_counter()
    output_path.write_text("".join(output_lines), encoding="utf-8")
    phase_seconds["bulk_write_text_sec"] = time.perf_counter() - write_start

    return {
        "path": str(output_path),
        "chain_count": chain_count,
        "face_count": len(face_ids),
        "line_count": line_count,
        "point_count": streamed_point_count,
        "writer_phase_seconds": phase_seconds,
        "writer_cache_counts": {
            "unique_point_records": len(point_records),
        },
        "compiled_path_split": {
            "enabled": True,
            "schema": "rtdl.paper_reproduction.section57.compiled_path_split_adapter.v1",
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
    wrapper_start = time.perf_counter()
    base.write_output_chains_streaming = write_output_chains_streaming_compiled_path_split
    base.main()

    summary_path = _summary_arg(sys.argv[1:])
    if summary_path is not None and summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        payload["schema"] = "rtdl.paper_reproduction.rayjoin.section57_compiled_path_split.v1"
        payload["route"] = "public_lsi_pip_plus_internal_compiled_generic_path_split_adapter"
        payload.setdefault("claim_boundary", {})
        payload["claim_boundary"]["compiled_path_split_adapter"] = True
        payload["claim_boundary"]["public_api_claim"] = False
        payload["claim_boundary"]["default_route_claim"] = False
        payload["phase_seconds"]["compiled_path_split_wrapper_total_sec"] = time.perf_counter() - wrapper_start
        summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
