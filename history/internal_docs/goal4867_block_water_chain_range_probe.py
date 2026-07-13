from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from goal4867_block_water_packed_streaming_compare import PackedTwoPointDatasetView


class ChainRangeFound(Exception):
    def __init__(self, payload: dict[str, object]) -> None:
        super().__init__("chain range found")
        self.payload = payload


def _json_default(value):
    return str(value)


def install_chain_range_probe(rayjoin_overlay, *, start_chain_no: int, end_chain_no: int) -> None:
    def probe_writer(datasets, xsect_edges_sorted, point_in_polygon, path):
        chain_count = 0
        records: list[dict[str, object]] = []

        def flush(output_chain: dict[str, object], map_index: int, chain_index: int) -> None:
            nonlocal chain_count, records
            points = output_chain["points"]
            if not points:
                return
            keep = (
                int(output_chain["left_polygon_id"]) * int(output_chain["other_map_polygon_id"]) != 0
                or int(output_chain["right_polygon_id"]) * int(output_chain["other_map_polygon_id"]) != 0
            )
            if keep:
                points2, display_points2, tags2 = _dedupe_with_tags(
                    output_chain["points"],
                    output_chain["display_points"],
                    output_chain["tags"],
                )
                chain_count += 1
                if start_chain_no <= chain_count <= end_chain_no:
                    records.append(
                        {
                            "chain_no": chain_count,
                            "map_index": map_index,
                            "chain_index": chain_index,
                            "raw_left_polygon_id": int(output_chain["left_polygon_id"]),
                            "raw_right_polygon_id": int(output_chain["right_polygon_id"]),
                            "other_map_polygon_id": int(output_chain["other_map_polygon_id"]),
                            "point_count": len(points2),
                            "points": [[float(x), float(y)] for x, y in points2],
                            "display_points": [[float(x), float(y)] for x, y in display_points2],
                            "tags": tags2,
                        }
                    )
                if chain_count >= end_chain_no:
                    raise ChainRangeFound(
                        {
                            "start_chain_no": start_chain_no,
                            "end_chain_no": end_chain_no,
                            "records": records,
                            "emitted_chain_count_at_stop": chain_count,
                        }
                    )
            output_chain["points"].clear()
            output_chain["display_points"].clear()
            output_chain["tags"].clear()

        def append_chain_point(output_chain: dict[str, object], point, tag: dict[str, object]) -> None:
            output_chain["points"].append((float(point.x), float(point.y)))
            output_chain["display_points"].append((float(point.x), float(point.y)))
            output_chain["tags"].append(tag)

        def append_xsect(output_chain: dict[str, object], xsect, tag: dict[str, object]) -> None:
            output_chain["points"].append((float(xsect.x), float(xsect.y)))
            output_chain["display_points"].append(
                (
                    float(xsect.display_x if xsect.display_x is not None else xsect.x),
                    float(xsect.display_y if xsect.display_y is not None else xsect.y),
                )
            )
            output_chain["tags"].append(
                {
                    **tag,
                    "kind": "xsect",
                    "eid0": int(xsect.eid0),
                    "eid1": int(xsect.eid1),
                    "x": float(xsect.x),
                    "y": float(xsect.y),
                    "display_x": None if xsect.display_x is None else float(xsect.display_x),
                    "display_y": None if xsect.display_y is None else float(xsect.display_y),
                    "scaled_x": None if xsect.scaled_x is None else float(xsect.scaled_x),
                    "scaled_y": None if xsect.scaled_y is None else float(xsect.scaled_y),
                    "scaled_x_rational": xsect.scaled_x_rational,
                    "scaled_y_rational": xsect.scaled_y_rational,
                    "mid_point_polygon_id_map0": int(xsect.mid_point_polygon_id_map0),
                    "mid_point_polygon_id_map1": int(xsect.mid_point_polygon_id_map1),
                }
            )

        for map_index, dataset in enumerate(datasets):
            edge_attr = "eid0" if map_index == 0 else "eid1"
            grouped: dict[int, list[object]] = {}
            for xsect in xsect_edges_sorted[map_index]:
                grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
            point_offset = 0
            edge_id = 0
            for chain_index, chain in enumerate(dataset.chains):
                output_chain = {
                    "points": [],
                    "display_points": [],
                    "tags": [],
                    "left_polygon_id": int(chain.left_face_id),
                    "right_polygon_id": int(chain.right_face_id),
                    "other_map_polygon_id": 0,
                }
                for local_point_index, point in enumerate(chain.points):
                    point_index = point_offset + local_point_index
                    output_chain["other_map_polygon_id"] = int(point_in_polygon[map_index][point_index])
                    append_chain_point(
                        output_chain,
                        point,
                        {
                            "kind": "chain_point",
                            "map_index": map_index,
                            "chain_index": chain_index,
                            "local_point_index": local_point_index,
                            "global_point_index": point_index,
                            "edge_id_before_point": edge_id,
                            "pip_face": int(point_in_polygon[map_index][point_index]),
                        },
                    )
                    if local_point_index == len(chain.points) - 1:
                        continue
                    xsects = grouped.get(edge_id)
                    if xsects:
                        append_xsect(output_chain, xsects[0], {"map_index": map_index, "edge_id": edge_id, "role": "first_xsect_on_edge"})
                        for xsect, next_xsect in zip(xsects, xsects[1:]):
                            flush(output_chain, map_index, chain_index)
                            output_chain["other_map_polygon_id"] = rayjoin_overlay._midpoint_face_for_map(xsect, map_index)
                            append_xsect(output_chain, xsect, {"map_index": map_index, "edge_id": edge_id, "role": "segment_start_xsect"})
                            append_xsect(output_chain, next_xsect, {"map_index": map_index, "edge_id": edge_id, "role": "segment_end_xsect"})
                        flush(output_chain, map_index, chain_index)
                        append_xsect(output_chain, xsects[-1], {"map_index": map_index, "edge_id": edge_id, "role": "last_xsect_on_edge"})
                    edge_id += 1
                flush(output_chain, map_index, chain_index)
                point_offset += len(chain.points)

        raise RuntimeError(
            f"chain range {start_chain_no}..{end_chain_no} not reached; emitted {chain_count} chains"
        )

    rayjoin_overlay._write_output_chains_streaming = probe_writer


def _dedupe_with_tags(points, display_points, tags):
    if not points:
        return [], [], []
    out_points = [points[0]]
    out_display = [display_points[0]]
    out_tags = [tags[0]]
    for point, display, tag in zip(points[1:], display_points[1:], tags[1:]):
        if point != out_points[-1]:
            out_points.append(point)
            out_display.append(display)
            out_tags.append(tag)
    return out_points, out_display, out_tags


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--start-chain-no", type=int, required=True)
    parser.add_argument("--end-chain-no", type=int, required=True)
    args = parser.parse_args()
    if args.start_chain_no <= 0 or args.end_chain_no < args.start_chain_no:
        raise SystemExit("--start-chain-no must be positive and <= --end-chain-no")

    import rtdsl.rayjoin_overlay as rayjoin_overlay

    load_start = time.perf_counter()
    left_inputs = rayjoin_overlay.load_cdb_overlay_packed_inputs(args.left)
    right_inputs = rayjoin_overlay.load_cdb_overlay_packed_inputs(args.right)
    load_sec = time.perf_counter() - load_start
    install_chain_range_probe(
        rayjoin_overlay,
        start_chain_no=args.start_chain_no,
        end_chain_no=args.end_chain_no,
    )
    start = time.perf_counter()
    try:
        rayjoin_overlay._run_rayjoin_overlay_packed(
            left_inputs,
            right_inputs,
            backend="optix",
            assemble_output=False,
            output_path=Path(args.output).with_suffix(".placeholder.txt"),
            left=PackedTwoPointDatasetView(left_inputs),
            right=PackedTwoPointDatasetView(right_inputs),
            input_phase_name="load_cached_packed_inputs_sec",
            input_phase_sec=load_sec,
            total_start=start,
        )
    except ChainRangeFound as found:
        payload = {
            "schema": "rtdl.goal4867.block_water.chain_range_probe.v1",
            "elapsed_sec": time.perf_counter() - start,
            "load_cached_packed_inputs_sec": load_sec,
            "left": args.left,
            "right": args.right,
            "range": found.payload,
        }
        Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True, default=_json_default), encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True, default=_json_default))
        return
    raise RuntimeError("target chain probe did not stop")


if __name__ == "__main__":
    main()
