from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rtdsl.datasets import load_cdb
from rtdsl import rayjoin_overlay as overlay


def _stream_full_chain_probe(
    datasets,
    xsect_edges_sorted,
    point_in_polygon,
    *,
    target_start: int,
    target_end: int,
    target_indices: set[int] | None = None,
):
    records = []
    face_ids: dict[tuple[int, int], int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    point_counter = 0
    output_index = 0

    class Chain:
        def __init__(self, left: int = 0, right: int = 0):
            self.points = []
            self.left_polygon_id = int(left)
            self.right_polygon_id = int(right)
            self.other_map_polygon_id = 0
            self.debug = {}

    def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
        return face_ids[key]

    def flush(output_chain: Chain):
        nonlocal output_index, point_counter
        if not output_chain.points:
            return False
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            raw_points = list(output_chain.points)
            points = overlay._dedupe_consecutive_points(raw_points)
            raw_left = int(output_chain.left_polygon_id)
            raw_right = int(output_chain.right_polygon_id)
            raw_other = int(output_chain.other_map_polygon_id)
            mapped_left = create_polygon(*sorted((raw_left, raw_other)))
            mapped_right = create_polygon(*sorted((raw_right, raw_other)))
            for point in points:
                if point not in point_ids:
                    point_ids[point] = point_counter
                    point_counter += 1
            output_index += 1
            capture = (
                output_index in target_indices
                if target_indices is not None
                else target_start <= output_index <= target_end
            )
            if capture:
                records.append(
                    {
                        "output_index": int(output_index),
                        "point_count": int(len(points)),
                        "first_point_idx": int(point_ids[points[0]]),
                        "last_point_idx": int(point_ids[points[-1]]),
                        "raw_left": raw_left,
                        "raw_right": raw_right,
                        "raw_other": raw_other,
                        "mapped_left": int(mapped_left),
                        "mapped_right": int(mapped_right),
                        "raw_points": [[float(x), float(y)] for x, y in raw_points],
                        "points": [[float(x), float(y)] for x, y in points],
                        "debug": dict(output_chain.debug),
                    }
                )
        output_chain.points.clear()
        return output_index >= target_end

    stop = False
    for map_index, dataset in enumerate(datasets):
        edge_attr = "eid0" if map_index == 0 else "eid1"
        grouped: dict[int, list[overlay.RayjoinOverlayIntersection]] = {}
        for xsect in xsect_edges_sorted[map_index]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)

        point_offset = 0
        edge_id = 0
        for chain_index, chain in enumerate(dataset.chains):
            output_chain = Chain(int(chain.left_face_id), int(chain.right_face_id))
            for local_point_index, point in enumerate(chain.points):
                point_index = point_offset + local_point_index
                output_chain.other_map_polygon_id = int(point_in_polygon[map_index][point_index])
                output_chain.debug = {
                    "map_index": int(map_index),
                    "chain_index": int(chain_index),
                    "edge_id": int(edge_id),
                    "local_point_index": int(local_point_index),
                    "kind": "chain_point",
                }
                output_chain.points.append((float(point.x), float(point.y)))
                if local_point_index == len(chain.points) - 1:
                    continue
                xsects = grouped.get(edge_id)
                if xsects:
                    output_chain.debug = {
                        "map_index": int(map_index),
                        "chain_index": int(chain_index),
                        "edge_id": int(edge_id),
                        "kind": "segment_start_to_first_xsect_or_endpoint",
                        "first_xsect_eid0": int(xsects[0].eid0),
                        "first_xsect_eid1": int(xsects[0].eid1),
                    }
                    output_chain.points.append((xsects[0].x, xsects[0].y))
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        output_chain.debug = {
                            "map_index": int(map_index),
                            "chain_index": int(chain_index),
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
                            "chain_index": int(chain_index),
                            "edge_id": int(edge_id),
                            "kind": "between_xsects",
                            "left_xsect_eid0": int(xsect.eid0),
                            "left_xsect_eid1": int(xsect.eid1),
                            "right_xsect_eid0": int(next_xsect.eid0),
                            "right_xsect_eid1": int(next_xsect.eid1),
                            "mid_point_polygon_id": int(xsect.mid_point_polygon_id),
                        }
                        output_chain.points.append((xsect.x, xsect.y))
                        output_chain.points.append((next_xsect.x, next_xsect.y))
                    if stop:
                        break
                    stop = flush(output_chain)
                    if stop:
                        break
                    output_chain.debug = {
                        "map_index": int(map_index),
                        "chain_index": int(chain_index),
                        "edge_id": int(edge_id),
                        "kind": "last_xsect_to_next_chain_point",
                        "last_xsect_eid0": int(xsects[-1].eid0),
                        "last_xsect_eid1": int(xsects[-1].eid1),
                    }
                    output_chain.points.append((xsects[-1].x, xsects[-1].y))
                edge_id += 1
                if stop:
                    break
            if stop:
                break
            stop = flush(output_chain)
            point_offset += len(chain.points)
        if stop:
            break
    return {"records": records, "face_count_at_stop": int(len(face_ids))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-cdb", required=True)
    parser.add_argument("--right-cdb", required=True)
    parser.add_argument("--target-start", type=int, required=True)
    parser.add_argument("--target-end", type=int, required=True)
    parser.add_argument(
        "--target-indices",
        default="",
        help="Optional comma-separated output indices to capture while streaming until --target-end.",
    )
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()
    target_indices = None
    if args.target_indices.strip():
        target_indices = {int(item) for item in args.target_indices.split(",") if item.strip()}

    started = time.perf_counter()
    left = load_cdb(args.left_cdb)
    right = load_cdb(args.right_cdb)
    left_inputs = overlay._packed_overlay_inputs(left)
    right_inputs = overlay._packed_overlay_inputs(right)
    scale_bounds = overlay._shared_rayjoin_bounds(left_inputs, right_inputs)

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
    xsects = overlay._intersections_from_lsi_rows(lsi_rows)
    xsects_sorted = (
        overlay._sort_xsects_for_map(xsects, left_inputs.edge_starts, 0, scale_bounds=scale_bounds),
        overlay._sort_xsects_for_map(xsects, right_inputs.edge_starts, 1, scale_bounds=scale_bounds),
    )

    midpoint_filter_stats = {"map0_nonfinite_midpoints_dropped": 0, "map1_nonfinite_midpoints_dropped": 0}
    with overlay._prepared_point_location_pair(
        "optix",
        right_inputs.cdb_segments,
        left_inputs.cdb_segments,
        scale_bounds,
        point_counts=(int(left_inputs.points.count), int(right_inputs.points.count)),
    ) as (map0_in_map1, map1_in_map0, prepare_wall_sec):
        vertex0_faces, vertex0_timings = map0_in_map1.faces(left_inputs.points, int(left_inputs.points.count))
        vertex1_faces, vertex1_timings = map1_in_map0.faces(right_inputs.points, int(right_inputs.points.count))
        for map_index, locator, base_cdb in (
            (0, map0_in_map1, right_inputs.cdb_segments),
            (1, map1_in_map0, left_inputs.cdb_segments),
        ):
            midpoints, owners, scaled_midpoints = overlay._midpoints_for_sorted_xsects(
                xsects_sorted[map_index],
                map_index,
                scale_bounds=scale_bounds,
                stats=midpoint_filter_stats,
            )
            faces, _ = locator.faces_scaled(scaled_midpoints)
            overlay._assign_midpoint_faces(owners, faces)

    stream = _stream_full_chain_probe(
        (left, right),
        xsects_sorted,
        (vertex0_faces, vertex1_faces),
        target_start=int(args.target_start),
        target_end=int(args.target_end),
        target_indices=target_indices,
    )
    result = {
        "schema": "rtdl.goal4806.rayjoin_output_chain_full_probe.v1",
        "target_range": [int(args.target_start), int(args.target_end)],
        "phase_seconds": {"total_sec": float(time.perf_counter() - started), "pip_prepare_wall_sec": float(prepare_wall_sec)},
        "lsi_timings": dict(lsi_timings),
        "midpoint_filter_stats": midpoint_filter_stats,
        "vertex_timings": {"map0_in_map1": dict(vertex0_timings), "map1_in_map0": dict(vertex1_timings)},
        "stream": stream,
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
