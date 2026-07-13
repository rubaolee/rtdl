from __future__ import annotations

import json
from pathlib import Path

from rtdsl.datasets import load_cdb
import rtdsl.rayjoin_overlay as r


LEFT = Path("/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt")
RIGHT = Path("/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt")
OUT = Path("/workspace/rtdl_goal4820_artifacts/rtdl_raw_chain_245_260.json")


def raw_chains(datasets, xsect_edges_sorted, point_in_polygon, start=245, end=260):
    out = []
    raw_index = 0
    for map_index, dataset in enumerate(datasets):
        edge_attr = "eid0" if map_index == 0 else "eid1"
        grouped = {}
        for xsect in xsect_edges_sorted[map_index]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)

        point_offset = 0
        edge_id = 0
        for chain in dataset.chains:
            output_chain = {
                "points": [],
                "left": int(chain.left_face_id),
                "right": int(chain.right_face_id),
                "other": 0,
                "map": map_index,
                "source_chain": int(chain.chain_id),
                "edge_ids": [],
            }

            def flush(reason: str) -> None:
                nonlocal raw_index
                if not output_chain["points"]:
                    return
                keep = (
                    output_chain["left"] * output_chain["other"] != 0
                    or output_chain["right"] * output_chain["other"] != 0
                )
                if keep:
                    points = []
                    for point in output_chain["points"]:
                        if not points or points[-1] != point:
                            points.append(point)
                    raw_index += 1
                    if start <= raw_index <= end:
                        out.append(
                            {
                                "raw_index": raw_index,
                                "reason": reason,
                                "map": output_chain["map"],
                                "source_chain": output_chain["source_chain"],
                                "left": output_chain["left"],
                                "right": output_chain["right"],
                                "other": output_chain["other"],
                                "point_count": len(points),
                                "points_head": points[:8],
                                "edge_ids": list(output_chain["edge_ids"]),
                            }
                        )
                output_chain["points"].clear()
                output_chain["edge_ids"].clear()

            for local_point_index, point in enumerate(chain.points):
                point_index = point_offset + local_point_index
                output_chain["other"] = int(point_in_polygon[map_index][point_index])
                output_chain["points"].append((float(point.x), float(point.y)))
                if local_point_index == len(chain.points) - 1:
                    continue
                xsects = grouped.get(edge_id)
                if xsects:
                    output_chain["points"].append((xsects[0].x, xsects[0].y))
                    output_chain["edge_ids"].append(edge_id)
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        flush("between_xsects")
                        output_chain["other"] = r._midpoint_face_for_map(xsect, map_index)
                        output_chain["points"].append((xsect.x, xsect.y))
                        output_chain["points"].append((next_xsect.x, next_xsect.y))
                        output_chain["edge_ids"].append(edge_id)
                    flush("after_xsects")
                    output_chain["points"].append((xsects[-1].x, xsects[-1].y))
                    output_chain["edge_ids"].append(edge_id)
                edge_id += 1
            flush("chain_end")
            point_offset += len(chain.points)
    return out


def main() -> None:
    left = load_cdb(LEFT)
    right = load_cdb(RIGHT)
    left_inputs = r.load_cdb_overlay_packed_inputs(LEFT)
    right_inputs = r.load_cdb_overlay_packed_inputs(RIGHT)

    rows, _ = r._run_lsi_rows(
        "optix",
        left_inputs.segments,
        right_inputs.segments,
        left,
        right,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
    )
    xsects = r._intersections_from_lsi_rows(rows)
    xsects_sorted = (
        r._sort_xsects_for_map(xsects, left_inputs.edge_starts, 0),
        r._sort_xsects_for_map(xsects, right_inputs.edge_starts, 1),
    )
    scale_bounds = r._shared_rayjoin_bounds(left_inputs, right_inputs)

    with r._prepared_point_location_pair(
        "optix",
        right_inputs.cdb_segments,
        left_inputs.cdb_segments,
        scale_bounds,
        point_counts=(int(left_inputs.point_count), int(right_inputs.point_count)),
    ) as (map0_in_map1, map1_in_map0, _):
        vertex0_faces, _ = map0_in_map1.faces(left_inputs.points, int(left_inputs.point_count))
        vertex1_faces, _ = map1_in_map0.faces(right_inputs.points, int(right_inputs.point_count))

        midpoint_stats = []
        for map_index, runner in ((0, map0_in_map1), (1, map1_in_map0)):
            midpoints, owners = r._midpoints_for_sorted_xsects(xsects_sorted[map_index], map_index)
            if midpoints:
                midpoint_points = r._packed_points_from_xy(midpoints)
                faces, _ = runner.faces(midpoint_points, len(midpoints))
                positives = r._assign_midpoint_faces(owners, faces, map_index=map_index)
            else:
                positives = 0
            midpoint_stats.append(
                {
                    "map_index": map_index,
                    "midpoints": len(midpoints),
                    "owners": len(owners),
                    "positive_faces": int(positives),
                }
            )

    payload = {
        "midpoint_stats": midpoint_stats,
        "raw": raw_chains((left, right), xsects_sorted, (vertex0_faces, vertex1_faces)),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"raw_count": len(payload["raw"]), "midpoint_stats": midpoint_stats}, sort_keys=True))


if __name__ == "__main__":
    main()
