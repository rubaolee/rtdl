from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from rtdsl import rayjoin_overlay as overlay


def _load_packed_cache(path: Path):
    meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
    segments = np.load(path / "segments.npy", mmap_mode="r")
    cdb_segments = np.load(path / "cdb_segments.npy", mmap_mode="r")
    points = np.load(path / "points.npy", mmap_mode="r")
    return overlay._overlay_inputs_from_native_arrays(
        name=str(meta["name"]),
        chain_count=int(meta["chain_count"]),
        segment_array=segments,
        cdb_array=cdb_segments,
        point_array=points,
    )


def _stream_chain_probe_packed(
    packed_inputs,
    xsect_edges_sorted,
    point_in_polygon,
    *,
    scale_bounds,
    target_start: int,
    target_end: int,
):
    records = []
    face_ids: dict[tuple[int, int], int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    output_index = 0
    point_counter = 0
    map_by_public_id: dict[int, tuple[int, int]] = {}
    snap_events = []

    def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
        nonlocal face_ids, map_by_public_id
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
            map_by_public_id[face_ids[key]] = key
        return face_ids[key]

    min_x, max_x, min_y, max_y = (float(value) for value in scale_bounds)
    internal_max = (1 << 46) - 1
    internal_min = -(1 << 46)
    margin = 1.0
    box_max_x = max_x + margin
    box_min_x = min_x - margin
    box_max_y = max_y + margin
    box_min_y = min_y - margin
    internal_range = float(internal_max - internal_min)
    rx_scale = internal_range / (box_max_x - box_min_x)
    ry_scale = internal_range / (box_max_y - box_min_y)
    deltax = 0.5 * (float(internal_max + internal_min) - (box_max_x + box_min_x) * rx_scale)
    deltay = 0.5 * (float(internal_max + internal_min) - (box_max_y + box_min_y) * ry_scale)

    def scale_x(value: float) -> int:
        return int(float(value) * rx_scale + deltax)

    def scale_y(value: float) -> int:
        return int(float(value) * ry_scale + deltay)

    class Chain:
        def __init__(self, left: int = 0, right: int = 0):
            self.points = []
            self.left_polygon_id = int(left)
            self.right_polygon_id = int(right)
            self.other_map_polygon_id = 0
            self.debug = {}

    def flush(output_chain: Chain):
        nonlocal output_index, point_counter
        if not output_chain.points:
            return False
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            deduped = overlay._dedupe_consecutive_points(list(output_chain.points))
            raw_left = int(output_chain.left_polygon_id)
            raw_right = int(output_chain.right_polygon_id)
            raw_other = int(output_chain.other_map_polygon_id)
            mapped_left = create_polygon(*sorted((raw_left, raw_other)))
            mapped_right = create_polygon(*sorted((raw_right, raw_other)))
            for point in deduped:
                if point not in point_ids:
                    point_ids[point] = point_counter
                    point_counter += 1
            output_index += 1
            if target_start <= output_index <= target_end:
                records.append(
                    {
                        "output_index": int(output_index),
                        "point_count": int(len(deduped)),
                        "first_point_idx": int(point_ids[deduped[0]]),
                        "last_point_idx": int(point_ids[deduped[-1]]),
                        "raw_left": raw_left,
                        "raw_right": raw_right,
                        "raw_other": raw_other,
                        "mapped_left": int(mapped_left),
                        "mapped_right": int(mapped_right),
                        "points": [[float(x), float(y)] for x, y in deduped],
                        "debug": dict(output_chain.debug),
                    }
                )
        output_chain.points.clear()
        return output_index >= target_end

    def append_xsect_point(output_chain: Chain, xsect, adjacent_points=(), label: str = ""):
        output_chain.points.append((float(xsect.x), float(xsect.y)))

    stop = False
    for map_index, packed in enumerate(packed_inputs):
        edge_attr = "eid0" if map_index == 0 else "eid1"
        grouped: dict[int, list[overlay.RayjoinOverlayIntersection]] = {}
        for xsect in xsect_edges_sorted[map_index]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
        segments = packed.segments.owner[0]
        cdb_segments = packed.cdb_segments.owner[1]
        if int(packed.chain_count) != int(packed.edge_count) or int(packed.point_count) != int(packed.edge_count) * 2:
            raise RuntimeError(
                "packed-only output-chain probe expects Section 5.7 two-point chains; "
                f"chain_count={packed.chain_count}, edge_count={packed.edge_count}, point_count={packed.point_count}"
            )
        for edge_id in range(int(segments.size)):
            segment = segments[edge_id]
            cdb = cdb_segments[edge_id]
            output_chain = Chain(int(cdb["left_face_id"]), int(cdb["right_face_id"]))
            output_chain.debug = {
                "map_index": int(map_index),
                "edge_id": int(edge_id),
                "kind": "segment_start_to_first_xsect_or_endpoint",
            }
            point_index0 = edge_id * 2
            output_chain.other_map_polygon_id = int(point_in_polygon[map_index][point_index0])
            output_chain.points.append((float(segment["x0"]), float(segment["y0"])))
            xsects = grouped.get(edge_id)
            if xsects:
                append_xsect_point(
                    output_chain,
                    xsects[0],
                    ((segment["x0"], segment["y0"]),),
                    label=f"map{map_index}:edge{edge_id}:first_start",
                )
                for xsect, next_xsect in zip(xsects, xsects[1:]):
                    output_chain.debug = {
                        "map_index": int(map_index),
                        "edge_id": int(edge_id),
                        "kind": "pre_midpoint_flush",
                        "xsect_eid0": int(xsect.eid0),
                        "xsect_eid1": int(xsect.eid1),
                        "xsect_mid_point_polygon_id": int(xsect.mid_point_polygon_id),
                    }
                    stop = flush(output_chain)
                    if stop:
                        break
                    output_chain.other_map_polygon_id = int(xsect.mid_point_polygon_id)
                    output_chain.debug = {
                        "map_index": int(map_index),
                        "edge_id": int(edge_id),
                        "kind": "between_xsects",
                        "left_xsect_eid0": int(xsect.eid0),
                        "left_xsect_eid1": int(xsect.eid1),
                        "right_xsect_eid0": int(next_xsect.eid0),
                        "right_xsect_eid1": int(next_xsect.eid1),
                        "mid_point_polygon_id": int(xsect.mid_point_polygon_id),
                    }
                    append_xsect_point(output_chain, xsect, label=f"map{map_index}:edge{edge_id}:between_left")
                    append_xsect_point(output_chain, next_xsect, label=f"map{map_index}:edge{edge_id}:between_right")
                if stop:
                    break
                stop = flush(output_chain)
                if stop:
                    break
                output_chain.debug = {
                    "map_index": int(map_index),
                    "edge_id": int(edge_id),
                    "kind": "last_xsect_to_endpoint",
                    "last_xsect_eid0": int(xsects[-1].eid0),
                    "last_xsect_eid1": int(xsects[-1].eid1),
                }
                append_xsect_point(
                    output_chain,
                    xsects[-1],
                    ((segment["x1"], segment["y1"]),),
                    label=f"map{map_index}:edge{edge_id}:last_end",
                )
            point_index1 = edge_id * 2 + 1
            output_chain.other_map_polygon_id = int(point_in_polygon[map_index][point_index1])
            output_chain.points.append((float(segment["x1"]), float(segment["y1"])))
            stop = flush(output_chain)
            if stop:
                break
        if stop:
            break
    return {
        "records": records,
        "snap_events": snap_events,
        "created_face_count_at_stop": int(len(face_ids)),
        "public_id_to_raw_pair_nearby": {
            str(key): list(value)
            for key, value in sorted(map_by_public_id.items())
            if target_start == 0 or (50 <= key <= 90)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-root", required=True)
    parser.add_argument("--left-cache-name", default="dtl_cnty_Point")
    parser.add_argument("--right-cache-name", default="USAZIPCodeArea_Point")
    parser.add_argument("--target-start", type=int, default=10258)
    parser.add_argument("--target-end", type=int, default=10266)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    cache_root = Path(args.cache_root)
    left_cache = next(cache_root.glob(f"{args.left_cache_name}_*_rtdl_rayjoin_overlay_packed_v1"))
    right_cache = next(cache_root.glob(f"{args.right_cache_name}_*_rtdl_rayjoin_overlay_packed_v1"))
    left_inputs = _load_packed_cache(left_cache)
    right_inputs = _load_packed_cache(right_cache)
    scale_bounds = overlay._shared_rayjoin_bounds(left_inputs, right_inputs)
    phase_seconds = {"load_packed_sec": float(time.perf_counter() - started)}

    lsi_started = time.perf_counter()
    lsi_rows, lsi_timings = overlay._run_lsi_rows(
        "optix",
        left_inputs.segments,
        right_inputs.segments,
        None,
        None,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
        scale_bounds=scale_bounds,
    )
    phase_seconds["lsi_sec"] = float(time.perf_counter() - lsi_started)

    materialize_started = time.perf_counter()
    xsects = overlay._intersections_from_lsi_rows(lsi_rows)
    xsects_sorted = (
        overlay._sort_xsects_for_map(xsects, left_inputs.edge_starts, 0, scale_bounds=scale_bounds),
        overlay._sort_xsects_for_map(xsects, right_inputs.edge_starts, 1, scale_bounds=scale_bounds),
    )
    phase_seconds["materialize_sort_sec"] = float(time.perf_counter() - materialize_started)

    midpoint_filter_stats = {"map0_nonfinite_midpoints_dropped": 0, "map1_nonfinite_midpoints_dropped": 0}
    with overlay._prepared_point_location_pair(
        "optix",
        right_inputs.cdb_segments,
        left_inputs.cdb_segments,
        scale_bounds,
        point_counts=(int(left_inputs.points.count), int(right_inputs.points.count)),
    ) as (map0_in_map1, map1_in_map0, prepare_wall_sec):
        pip_started = time.perf_counter()
        vertex0_faces, vertex0_timings = map0_in_map1.faces(left_inputs.points, int(left_inputs.points.count))
        vertex1_faces, vertex1_timings = map1_in_map0.faces(right_inputs.points, int(right_inputs.points.count))
        for map_index, locator in ((0, map0_in_map1), (1, map1_in_map0)):
            midpoints, owners, scaled_midpoints = overlay._midpoints_for_sorted_xsects(
                xsects_sorted[map_index],
                map_index,
                scale_bounds=scale_bounds,
                stats=midpoint_filter_stats,
            )
            faces, _ = locator.faces_scaled(scaled_midpoints)
            overlay._assign_midpoint_faces(owners, faces)
        phase_seconds["pip_assign_sec"] = float(time.perf_counter() - pip_started)
        phase_seconds["pip_prepare_wall_sec"] = float(prepare_wall_sec)

    stream_started = time.perf_counter()
    stream_result = _stream_chain_probe_packed(
        (left_inputs, right_inputs),
        xsects_sorted,
        (vertex0_faces, vertex1_faces),
        scale_bounds=scale_bounds,
        target_start=int(args.target_start),
        target_end=int(args.target_end),
    )
    phase_seconds["stream_probe_sec"] = float(time.perf_counter() - stream_started)
    phase_seconds["total_sec"] = float(time.perf_counter() - started)

    result = {
        "schema": "rtdl.goal4806.rayjoin_output_chain_probe.v1",
        "target_range": [int(args.target_start), int(args.target_end)],
        "phase_seconds": phase_seconds,
        "lsi_timings": dict(lsi_timings),
        "midpoint_filter_stats": midpoint_filter_stats,
        "vertex_timings": {
            "map0_in_map1": dict(vertex0_timings),
            "map1_in_map0": dict(vertex1_timings),
        },
        "stream": stream_result,
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
