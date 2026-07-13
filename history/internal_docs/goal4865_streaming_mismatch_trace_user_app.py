from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


class StreamingMismatch(Exception):
    def __init__(self, payload: dict[str, object]) -> None:
        super().__init__(f"streaming mismatch at line {payload.get('line')}")
        self.payload = payload


class StreamedChains:
    def __init__(self) -> None:
        self.count = 0

    def __len__(self) -> int:
        return self.count


def _json_default(value):
    return str(value)


def _dedupe_points_with_display_and_tags(points, display_points, tags):
    if not points:
        return [], [], []
    out_points = [points[0]]
    out_display_points = [display_points[0]]
    out_tags = [tags[0]]
    for point, display_point, tag in zip(points[1:], display_points[1:], tags[1:]):
        if point != out_points[-1]:
            out_points.append(point)
            out_display_points.append(display_point)
            out_tags.append(tag)
    return out_points, out_display_points, out_tags


def install_streaming_mismatch_tracer(rayjoin_overlay, author_output: Path, summary_state: dict[str, object]) -> None:
    author_handle = author_output.open("r", encoding="utf-8")
    line_no = 0

    def compare_line(generated: str, context: dict[str, object]) -> None:
        nonlocal line_no
        line_no += 1
        expected = author_handle.readline()
        if expected != generated:
            raise StreamingMismatch(
                {
                    "line": line_no,
                    "author": expected.rstrip("\n") if expected else "<eof>",
                    "rtdl": generated.rstrip("\n"),
                    "context": context,
                }
            )

    def assemble_stream(datasets, xsect_edges_sorted, point_in_polygon):
        chains = StreamedChains()
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

        def append_chain_point(output_chain, point, tag):
            output_chain["points"].append((float(point.x), float(point.y)))
            output_chain["display_points"].append((float(point.x), float(point.y)))
            output_chain["tags"].append(tag)

        def append_xsect_point(output_chain, xsect, tag_extra):
            output_chain["points"].append((float(xsect.x), float(xsect.y)))
            display_point = (
                float(xsect.display_x if xsect.display_x is not None else xsect.x),
                float(xsect.display_y if xsect.display_y is not None else xsect.y),
            )
            output_chain["display_points"].append(
                (float(display_point[0]), float(display_point[1]))
            )
            output_chain["tags"].append(
                {
                    "kind": "xsect",
                    "eid0": int(xsect.eid0),
                    "eid1": int(xsect.eid1),
                    "x": float(xsect.x),
                    "y": float(xsect.y),
                    "formatted": (
                        f"{float(xsect.x):.6f} "
                        f"{float(xsect.y):.6f}"
                    ),
                    "scaled_x": None if xsect.scaled_x is None else float(xsect.scaled_x),
                    "scaled_y": None if xsect.scaled_y is None else float(xsect.scaled_y),
                    "scaled_x_rational": xsect.scaled_x_rational,
                    "scaled_y_rational": xsect.scaled_y_rational,
                    "mid_point_polygon_id_map0": int(xsect.mid_point_polygon_id_map0),
                    "mid_point_polygon_id_map1": int(xsect.mid_point_polygon_id_map1),
                    **tag_extra,
                }
            )

        def emit(output_chain) -> None:
            nonlocal point_counter
            other = int(output_chain["other_map_polygon_id"])
            left_polygon_id = create_polygon(*sorted((int(output_chain["left_polygon_id"]), other)))
            right_polygon_id = create_polygon(*sorted((int(output_chain["right_polygon_id"]), other)))
            for point in output_chain["points"]:
                if point not in point_ids:
                    point_ids[point] = point_counter
                    point_counter += 1
            first_point_idx = point_ids[output_chain["points"][0]]
            last_point_idx = point_ids[output_chain["points"][-1]]
            chains.count += 1
            header_context = {
                "line_kind": "header",
                "chain_no": chains.count,
                "raw_left_polygon_id": int(output_chain["left_polygon_id"]),
                "raw_right_polygon_id": int(output_chain["right_polygon_id"]),
                "other_map_polygon_id": other,
                "left_polygon_id": left_polygon_id,
                "right_polygon_id": right_polygon_id,
                "point_count": len(output_chain["points"]),
                "first_point_idx": first_point_idx,
                "last_point_idx": last_point_idx,
            }
            compare_line(
                f"{chains.count} {len(output_chain['points'])} {first_point_idx} {last_point_idx} "
                f"{left_polygon_id} {right_polygon_id}\n",
                header_context,
            )
            for point_index, (point, display_point, tag) in enumerate(
                zip(output_chain["points"], output_chain["display_points"], output_chain["tags"])
            ):
                compare_line(
                    (
                        f"{display_point[0]:.6f} "
                        f"{display_point[1]:.6f}\n"
                    ),
                    {
                        "line_kind": "point",
                        "chain_no": chains.count,
                        "point_index_in_chain": point_index,
                        "raw_point": [point[0], point[1]],
                        "display_point": [display_point[0], display_point[1]],
                        "formatted": (
                            f"{display_point[0]:.6f} "
                            f"{display_point[1]:.6f}"
                        ),
                        "point_id": point_ids[point],
                        "chain_header": header_context,
                        "tag": tag,
                    },
                )

        def flush(output_chain) -> None:
            if not output_chain["points"]:
                return
            keep = (
                int(output_chain["left_polygon_id"]) * int(output_chain["other_map_polygon_id"]) != 0
                or int(output_chain["right_polygon_id"]) * int(output_chain["other_map_polygon_id"]) != 0
            )
            if keep:
                (
                    output_chain["points"],
                    output_chain["display_points"],
                    output_chain["tags"],
                ) = _dedupe_points_with_display_and_tags(
                    output_chain["points"],
                    output_chain["display_points"],
                    output_chain["tags"],
                )
                emit(output_chain)
            output_chain["points"].clear()
            output_chain["display_points"].clear()
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

        trailing = author_handle.readline()
        if trailing:
            raise StreamingMismatch({"line": line_no + 1, "author": trailing.rstrip("\n"), "rtdl": "<eof>"})
        author_handle.close()
        summary_state["streamed_chain_count"] = chains.count
        summary_state["streamed_face_count"] = len(face_ids)
        summary_state["streamed_point_count"] = len(point_ids)
        summary_state["streamed_line_count"] = line_no
        return chains, len(face_ids)

    rayjoin_overlay._assemble_output_chains = assemble_stream
    rayjoin_overlay.write_output_chains = lambda output_chains, path: Path(path).write_text("", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    import rtdsl.rayjoin_overlay as rayjoin_overlay

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.json"
    placeholder = output_dir / "placeholder.txt"
    summary_state: dict[str, object] = {}

    install_streaming_mismatch_tracer(rayjoin_overlay, Path(args.author_output), summary_state)
    start = time.time()
    try:
        result = rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths(
            args.left,
            args.right,
            backend="optix",
            assemble_output=True,
            output_path=placeholder,
        )
        outcome = {"stream_match": True, "first_diff": None, "result": result}
    except StreamingMismatch as exc:
        outcome = {"stream_match": False, "first_diff": exc.payload, "result": None}
    summary = {
        "schema": "rtdl.goal4865.streaming_mismatch_trace.v1",
        "elapsed_sec": time.time() - start,
        **summary_state,
        **outcome,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=_json_default), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=_json_default))


if __name__ == "__main__":
    main()
