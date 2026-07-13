from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.datasets import load_cdb
from rtdsl.rayjoin_overlay import EXTERIOR_FACE_ID
from rtdsl.rayjoin_overlay import RayjoinOverlayOutputChain
from rtdsl.rayjoin_overlay import _assign_midpoint_faces
from rtdsl.rayjoin_overlay import _dedupe_consecutive_points
from rtdsl.rayjoin_overlay import _intersections_from_lsi_rows
from rtdsl.rayjoin_overlay import _midpoint_face_for_map
from rtdsl.rayjoin_overlay import _midpoints_for_sorted_xsects
from rtdsl.rayjoin_overlay import _packed_overlay_inputs
from rtdsl.rayjoin_overlay import _prepared_point_location_pair
from rtdsl.rayjoin_overlay import _run_lsi_rows
from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
from rtdsl.rayjoin_overlay import _sort_xsects_for_map


def _prefix_chains(datasets, xsect_edges_sorted, point_in_polygon, max_chains: int):
    output_chains: list[RayjoinOverlayOutputChain] = []
    chain_events: list[list[dict[str, object]]] = []
    current_events: list[dict[str, object]] = []

    def flush(output_chain: RayjoinOverlayOutputChain) -> bool:
        nonlocal current_events
        if not output_chain.points:
            current_events = []
            return False
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            output_chain.points = _dedupe_consecutive_points(output_chain.points)
            output_chains.append(
                RayjoinOverlayOutputChain(
                    points=list(output_chain.points),
                    left_polygon_id=output_chain.left_polygon_id,
                    right_polygon_id=output_chain.right_polygon_id,
                    other_map_polygon_id=output_chain.other_map_polygon_id,
                )
            )
            chain_events.append(list(current_events))
        output_chain.points.clear()
        current_events = []
        return len(output_chains) >= max_chains

    for map_index, dataset in enumerate(datasets):
        edge_attr = "eid0" if map_index == 0 else "eid1"
        grouped = {}
        for xsect in xsect_edges_sorted[map_index]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
        point_offset = 0
        edge_id = 0
        for chain in dataset.chains:
            output_chain = RayjoinOverlayOutputChain(
                points=[],
                left_polygon_id=int(chain.left_face_id),
                right_polygon_id=int(chain.right_face_id),
            )
            for local_point_index, point in enumerate(chain.points):
                point_index = point_offset + local_point_index
                output_chain.other_map_polygon_id = int(point_in_polygon[map_index][point_index])
                output_chain.points.append((float(point.x), float(point.y)))
                if local_point_index == len(chain.points) - 1:
                    continue
                xsects = grouped.get(edge_id)
                if xsects:
                    output_chain.points.append((xsects[0].x, xsects[0].y))
                    current_events.append(
                        {
                            "kind": "first_xsect",
                            "eid0": int(xsects[0].eid0),
                            "eid1": int(xsects[0].eid1),
                            "x": repr(float(xsects[0].x)),
                            "y": repr(float(xsects[0].y)),
                            "scaled_x": None if xsects[0].scaled_x is None else repr(float(xsects[0].scaled_x)),
                            "scaled_y": None if xsects[0].scaled_y is None else repr(float(xsects[0].scaled_y)),
                        }
                    )
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        if flush(output_chain):
                            return output_chains, chain_events
                        output_chain.other_map_polygon_id = _midpoint_face_for_map(xsect, map_index)
                        current_events.append(
                            {
                                "kind": "midpoint_span",
                                "owner_eid0": int(xsect.eid0),
                                "owner_eid1": int(xsect.eid1),
                                "next_eid0": int(next_xsect.eid0),
                                "next_eid1": int(next_xsect.eid1),
                                "owner_face": int(output_chain.other_map_polygon_id),
                                "owner_x": repr(float(xsect.x)),
                                "owner_y": repr(float(xsect.y)),
                                "owner_scaled_x": None if xsect.scaled_x is None else repr(float(xsect.scaled_x)),
                                "owner_scaled_y": None if xsect.scaled_y is None else repr(float(xsect.scaled_y)),
                                "next_x": repr(float(next_xsect.x)),
                                "next_y": repr(float(next_xsect.y)),
                                "next_scaled_x": None if next_xsect.scaled_x is None else repr(float(next_xsect.scaled_x)),
                                "next_scaled_y": None if next_xsect.scaled_y is None else repr(float(next_xsect.scaled_y)),
                            }
                        )
                        output_chain.points.append((xsect.x, xsect.y))
                        output_chain.points.append((next_xsect.x, next_xsect.y))
                    if flush(output_chain):
                        return output_chains, chain_events
                    output_chain.points.append((xsects[-1].x, xsects[-1].y))
                    current_events.append(
                        {
                            "kind": "last_xsect",
                            "eid0": int(xsects[-1].eid0),
                            "eid1": int(xsects[-1].eid1),
                            "x": repr(float(xsects[-1].x)),
                            "y": repr(float(xsects[-1].y)),
                            "scaled_x": None if xsects[-1].scaled_x is None else repr(float(xsects[-1].scaled_x)),
                            "scaled_y": None if xsects[-1].scaled_y is None else repr(float(xsects[-1].scaled_y)),
                        }
                    )
                edge_id += 1
            if flush(output_chain):
                return output_chains, chain_events
            point_offset += len(chain.points)
    return output_chains, chain_events


def _finalize_prefix(output_chains):
    face_ids: dict[tuple[int, int], int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    point_counter = 0

    def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
        return face_ids[key]

    for chain in output_chains:
        other = int(chain.other_map_polygon_id)
        chain.left_polygon_id = create_polygon(*sorted((int(chain.left_polygon_id), other)))
        chain.right_polygon_id = create_polygon(*sorted((int(chain.right_polygon_id), other)))
        for point in chain.points:
            if point not in point_ids:
                point_ids[point] = point_counter
                point_counter += 1
        chain.first_point_idx = point_ids[chain.points[0]]
        chain.last_point_idx = point_ids[chain.points[-1]]
    return len(face_ids)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--max-chains", type=int, default=12)
    args = parser.parse_args()

    timings = {}
    start = time.perf_counter()
    print("LOAD_CDB_START", flush=True)
    left = load_cdb(args.left)
    right = load_cdb(args.right)
    timings["load_cdb_sec"] = time.perf_counter() - start
    print("LOAD_CDB_DONE", timings["load_cdb_sec"], flush=True)

    pack_start = time.perf_counter()
    print("PACK_START", flush=True)
    left_inputs = _packed_overlay_inputs(left)
    right_inputs = _packed_overlay_inputs(right)
    timings["pack_inputs_sec"] = time.perf_counter() - pack_start
    print("PACK_DONE", timings["pack_inputs_sec"], flush=True)
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)

    lsi_start = time.perf_counter()
    print("LSI_START", flush=True)
    lsi_rows, lsi_timings = _run_lsi_rows(
        "optix",
        left_inputs.segments,
        right_inputs.segments,
        left,
        right,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
        scale_bounds=scale_bounds,
    )
    timings["lsi_rows_sec"] = time.perf_counter() - lsi_start
    print("LSI_DONE", len(lsi_rows), timings["lsi_rows_sec"], flush=True)

    sort_start = time.perf_counter()
    print("SORT_START", flush=True)
    xsects = _intersections_from_lsi_rows(lsi_rows)
    edge_starts = (left_inputs.edge_starts, right_inputs.edge_starts)
    xsects_sorted = (
        _sort_xsects_for_map(xsects, edge_starts[0], 0, scale_bounds=scale_bounds),
        _sort_xsects_for_map(xsects, edge_starts[1], 1, scale_bounds=scale_bounds),
    )
    timings["materialize_sort_sec"] = time.perf_counter() - sort_start
    print("SORT_DONE", timings["materialize_sort_sec"], flush=True)

    midpoint_filter_stats = {"map0_nonfinite_midpoints_dropped": 0, "map1_nonfinite_midpoints_dropped": 0}
    point_faces = [None, None]
    midpoint_counts = [0, 0]
    midpoint_positive_counts = [0, 0]
    pip_start = time.perf_counter()
    print("PIP_START", flush=True)
    with _prepared_point_location_pair(
        "optix",
        right_inputs.cdb_segments,
        left_inputs.cdb_segments,
        scale_bounds,
        point_counts=(int(left_inputs.points.count), int(right_inputs.points.count)),
    ) as (left_in_right_runner, right_in_left_runner, prepare_wall_sec):
        point_faces[0], _ = left_in_right_runner.faces(left_inputs.points, int(left_inputs.points.count))
        point_faces[1], _ = right_in_left_runner.faces(right_inputs.points, int(right_inputs.points.count))
        for map_index, runner in enumerate((left_in_right_runner, right_in_left_runner)):
            midpoints, owners = _midpoints_for_sorted_xsects(
                xsects_sorted[map_index],
                map_index,
                stats=midpoint_filter_stats,
                scale_bounds=scale_bounds,
            )
            midpoint_counts[map_index] = len(midpoints)
            if midpoints:
                packed_midpoints = __import__("rtdsl.rayjoin_overlay", fromlist=["_packed_points_from_arrays"])
                pack_fn = packed_midpoints._packed_points_from_arrays
                import numpy as np

                mid_x = np.asarray([point[0] for point in midpoints], dtype=np.float64)
                mid_y = np.asarray([point[1] for point in midpoints], dtype=np.float64)
                faces, _ = runner.faces(pack_fn(mid_x, mid_y), len(midpoints))
            else:
                faces = []
            midpoint_positive_counts[map_index] = _assign_midpoint_faces(owners, faces, map_index)
    timings["pip_sec"] = time.perf_counter() - pip_start
    timings["pip_prepare_wall_sec"] = prepare_wall_sec
    print("PIP_DONE", timings["pip_sec"], flush=True)

    prefix_start = time.perf_counter()
    print("PREFIX_START", flush=True)
    prefix, chain_events = _prefix_chains((left, right), xsects_sorted, (point_faces[0], point_faces[1]), args.max_chains)
    pre_finalize = [
        {
            "id": index,
            "point_count": len(chain.points),
            "left_polygon_id": int(chain.left_polygon_id),
            "right_polygon_id": int(chain.right_polygon_id),
            "other_map_polygon_id": int(chain.other_map_polygon_id),
            "points": [f"{x:.6f} {y:.6f}" for x, y in chain.points],
            "raw_points": [[repr(float(x)), repr(float(y))] for x, y in chain.points],
        }
        for index, chain in enumerate(prefix, start=1)
    ]
    face_count_prefix = _finalize_prefix(prefix)
    timings["prefix_assembly_sec"] = time.perf_counter() - prefix_start
    print("PREFIX_DONE", timings["prefix_assembly_sec"], flush=True)

    payload = {
        "scale_bounds": scale_bounds,
        "lsi_count": int(len(lsi_rows)),
        "lsi_timings": lsi_timings,
        "midpoint_filter_stats": midpoint_filter_stats,
        "midpoint_counts": midpoint_counts,
        "midpoint_positive_counts": midpoint_positive_counts,
        "face_count_prefix": face_count_prefix,
        "pre_finalize_chains": pre_finalize,
        "chain_events": chain_events,
        "timings": timings,
        "chains": [
            {
                "id": index,
                "point_count": len(chain.points),
                "first": int(chain.first_point_idx),
                "last": int(chain.last_point_idx),
                "left": int(chain.left_polygon_id),
                "right": int(chain.right_polygon_id),
                "points": [f"{x:.6f} {y:.6f}" for x, y in chain.points],
                "raw_points": [[repr(float(x)), repr(float(y))] for x, y in chain.points],
            }
            for index, chain in enumerate(prefix, start=1)
        ],
    }
    out = Path(args.output_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
