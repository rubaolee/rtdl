from __future__ import annotations

import argparse
import json
from pathlib import Path


class TraceStop(Exception):
    pass


def _json_default(value):
    return str(value)


def _dedupe_points_with_tags(points, tags):
    if not points:
        return [], []
    out_points = [points[0]]
    out_tags = [tags[0]]
    for point, tag in zip(points[1:], tags[1:]):
        if point != out_points[-1]:
            out_points.append(point)
            out_tags.append(tag)
    return out_points, out_tags


def install_trace_assembler(rayjoin_overlay, *, chain_start: int, chain_end: int, trace: dict[str, object]) -> None:
    def assemble_trace(datasets, xsect_edges_sorted, point_in_polygon):
        face_ids: dict[tuple[int, int], int] = {}
        point_ids: dict[tuple[float, float], int] = {}
        point_counter = 0
        emitted_count = 0
        traced_chains: list[dict[str, object]] = []

        def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
            if polygon_id1 == 0 or polygon_id2 == 0:
                return 0
            key = (polygon_id1, polygon_id2)
            if key not in face_ids:
                face_ids[key] = len(face_ids) + 1
            return face_ids[key]

        def append_chain_point(output_chain, point, tag):
            output_chain["points"].append((float(point.x), float(point.y)))
            output_chain["tags"].append(tag)

        def append_xsect_point(output_chain, xsect, tag_extra):
            output_chain["points"].append((float(xsect.x), float(xsect.y)))
            output_chain["tags"].append(
                {
                    "kind": "xsect",
                    "eid0": int(xsect.eid0),
                    "eid1": int(xsect.eid1),
                    "x": float(xsect.x),
                    "y": float(xsect.y),
                    "formatted": f"{float(xsect.x):.6f} {float(xsect.y):.6f}",
                    "scaled_x": None if xsect.scaled_x is None else float(xsect.scaled_x),
                    "scaled_y": None if xsect.scaled_y is None else float(xsect.scaled_y),
                    "scaled_x_rational": xsect.scaled_x_rational,
                    "scaled_y_rational": xsect.scaled_y_rational,
                    "mid_point_polygon_id_map0": int(xsect.mid_point_polygon_id_map0),
                    "mid_point_polygon_id_map1": int(xsect.mid_point_polygon_id_map1),
                    **tag_extra,
                }
            )

        def emit(output_chain):
            nonlocal emitted_count, point_counter
            other = int(output_chain["other_map_polygon_id"])
            left_polygon_id = create_polygon(*sorted((int(output_chain["left_polygon_id"]), other)))
            right_polygon_id = create_polygon(*sorted((int(output_chain["right_polygon_id"]), other)))
            for point in output_chain["points"]:
                if point not in point_ids:
                    point_ids[point] = point_counter
                    point_counter += 1
            emitted_count += 1
            if chain_start <= emitted_count <= chain_end:
                traced_chains.append(
                    {
                        "chain_no": emitted_count,
                        "header": {
                            "point_count": len(output_chain["points"]),
                            "first_point_idx": point_ids[output_chain["points"][0]],
                            "last_point_idx": point_ids[output_chain["points"][-1]],
                            "left_polygon_id": left_polygon_id,
                            "right_polygon_id": right_polygon_id,
                            "raw_left_polygon_id": int(output_chain["left_polygon_id"]),
                            "raw_right_polygon_id": int(output_chain["right_polygon_id"]),
                            "other_map_polygon_id": other,
                        },
                        "points": [
                            {
                                "raw": [point[0], point[1]],
                                "formatted": f"{point[0]:.6f} {point[1]:.6f}",
                                "point_id": point_ids[point],
                                "tag": tag,
                            }
                            for point, tag in zip(output_chain["points"], output_chain["tags"])
                        ],
                    }
                )
            if emitted_count >= chain_end:
                trace["streamed_chain_count_at_stop"] = emitted_count
                trace["streamed_face_count_at_stop"] = len(face_ids)
                trace["streamed_point_count_at_stop"] = len(point_ids)
                trace["chains"] = traced_chains
                raise TraceStop()

        def flush(output_chain):
            if not output_chain["points"]:
                return
            keep = (
                int(output_chain["left_polygon_id"]) * int(output_chain["other_map_polygon_id"]) != 0
                or int(output_chain["right_polygon_id"]) * int(output_chain["other_map_polygon_id"]) != 0
            )
            if keep:
                output_chain["points"], output_chain["tags"] = _dedupe_points_with_tags(
                    output_chain["points"],
                    output_chain["tags"],
                )
                emit(output_chain)
            output_chain["points"].clear()
            output_chain["tags"].clear()

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
                        append_xsect_point(
                            output_chain,
                            xsects[0],
                            {"map_index": map_index, "edge_id": edge_id, "role": "first_xsect_on_edge"},
                        )
                        for xsect, next_xsect in zip(xsects, xsects[1:]):
                            flush(output_chain)
                            output_chain["other_map_polygon_id"] = rayjoin_overlay._midpoint_face_for_map(
                                xsect,
                                map_index,
                            )
                            append_xsect_point(
                                output_chain,
                                xsect,
                                {"map_index": map_index, "edge_id": edge_id, "role": "segment_start_xsect"},
                            )
                            append_xsect_point(
                                output_chain,
                                next_xsect,
                                {"map_index": map_index, "edge_id": edge_id, "role": "segment_end_xsect"},
                            )
                        flush(output_chain)
                        append_xsect_point(
                            output_chain,
                            xsects[-1],
                            {"map_index": map_index, "edge_id": edge_id, "role": "last_xsect_on_edge"},
                        )
                    edge_id += 1
                flush(output_chain)
                point_offset += len(chain.points)

        trace["streamed_chain_count_at_stop"] = emitted_count
        trace["streamed_face_count_at_stop"] = len(face_ids)
        trace["streamed_point_count_at_stop"] = len(point_ids)
        trace["chains"] = traced_chains
        return [], len(face_ids)

    rayjoin_overlay._assemble_output_chains = assemble_trace
    rayjoin_overlay.write_output_chains = lambda output_chains, path: Path(path).write_text("", encoding="utf-8")


def author_context(path: Path, start: int, end: int) -> list[dict[str, object]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if start <= line_no <= end:
                rows.append({"line": line_no, "text": line.rstrip("\n")})
            if line_no > end:
                break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--chain-start", type=int, default=340)
    parser.add_argument("--chain-end", type=int, default=360)
    parser.add_argument("--author-line-start", type=int, default=1035)
    parser.add_argument("--author-line-end", type=int, default=1060)
    args = parser.parse_args()

    import rtdsl.rayjoin_overlay as rayjoin_overlay

    trace: dict[str, object] = {
        "schema": "rtdl.goal4865.output_chain_trace.v1",
        "chain_start": args.chain_start,
        "chain_end": args.chain_end,
        "author_context": author_context(Path(args.author_output), args.author_line_start, args.author_line_end),
    }
    install_trace_assembler(rayjoin_overlay, chain_start=args.chain_start, chain_end=args.chain_end, trace=trace)
    try:
        rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths(
            args.left,
            args.right,
            backend="optix",
            assemble_output=True,
            output_path=Path(args.output).with_suffix(".placeholder.txt"),
        )
    except TraceStop:
        trace["stopped_after_requested_chain_window"] = True
    Path(args.output).write_text(json.dumps(trace, indent=2, sort_keys=True, default=_json_default), encoding="utf-8")
    print(json.dumps({k: trace.get(k) for k in ("schema", "streamed_chain_count_at_stop", "streamed_point_count_at_stop", "stopped_after_requested_chain_window")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
