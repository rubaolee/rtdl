from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


class StreamingWriterMismatch(Exception):
    def __init__(self, payload: dict[str, object]) -> None:
        super().__init__(f"streaming writer mismatch at line {payload.get('line')}")
        self.payload = payload


def _json_default(value):
    return str(value)


def install_streaming_writer_compare(rayjoin_overlay, author_output: Path, summary_state: dict[str, object]) -> None:
    author_handle = author_output.open("r", encoding="utf-8")
    line_no = 0

    def compare_line(generated: str, context: dict[str, object]) -> None:
        nonlocal line_no
        line_no += 1
        expected = author_handle.readline()
        if expected != generated:
            raise StreamingWriterMismatch(
                {
                    "line": line_no,
                    "author": expected.rstrip("\n") if expected else "<eof>",
                    "rtdl": generated.rstrip("\n"),
                    "context": context,
                }
            )

    def compare_writer(datasets, xsect_edges_sorted, point_in_polygon, path):
        face_ids: dict[tuple[int, int], int] = {}
        point_ids: dict[tuple[float, float], int] = {}
        point_counter = 0
        chain_count = 0
        streamed_point_count = 0

        def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
            if polygon_id1 == 0 or polygon_id2 == 0:
                return 0
            key = (polygon_id1, polygon_id2)
            if key not in face_ids:
                face_ids[key] = len(face_ids) + 1
            return face_ids[key]

        def flush(output_chain, map_index: int, chain_index: int) -> None:
            nonlocal point_counter, chain_count, streamed_point_count
            if not output_chain.points:
                return
            if output_chain.display_points is None:
                output_chain.display_points = list(output_chain.points)
            keep = (
                output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
                or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
            )
            if keep:
                points, display_points = rayjoin_overlay._dedupe_consecutive_point_pairs(
                    output_chain.points,
                    output_chain.display_points,
                )
                other = int(output_chain.other_map_polygon_id)
                left_polygon_id = create_polygon(*sorted((int(output_chain.left_polygon_id), other)))
                right_polygon_id = create_polygon(*sorted((int(output_chain.right_polygon_id), other)))
                for point in points:
                    if point not in point_ids:
                        point_ids[point] = point_counter
                        point_counter += 1
                first_point_idx = point_ids[points[0]]
                last_point_idx = point_ids[points[-1]]
                chain_count += 1
                header = (
                    f"{chain_count} {len(points)} {first_point_idx} {last_point_idx} "
                    f"{left_polygon_id} {right_polygon_id}\n"
                )
                compare_line(
                    header,
                    {
                        "line_kind": "header",
                        "chain_no": chain_count,
                        "map_index": map_index,
                        "chain_index": chain_index,
                        "raw_left_polygon_id": int(output_chain.left_polygon_id),
                        "raw_right_polygon_id": int(output_chain.right_polygon_id),
                        "other_map_polygon_id": other,
                        "left_polygon_id": left_polygon_id,
                        "right_polygon_id": right_polygon_id,
                        "point_count": len(points),
                        "first_point_idx": first_point_idx,
                        "last_point_idx": last_point_idx,
                    },
                )
                for point_index, ((raw_x, raw_y), (display_x, display_y)) in enumerate(zip(points, display_points)):
                    compare_line(
                        f"{display_x:.6f} {display_y:.6f}\n",
                        {
                            "line_kind": "point",
                            "chain_no": chain_count,
                            "map_index": map_index,
                            "chain_index": chain_index,
                            "point_index_in_chain": point_index,
                            "raw_point": [raw_x, raw_y],
                            "display_point": [display_x, display_y],
                            "point_id": point_ids[(raw_x, raw_y)],
                        },
                    )
                    streamed_point_count += 1
            output_chain.points.clear()
            if output_chain.display_points is not None:
                output_chain.display_points.clear()

        for map_index, dataset in enumerate(datasets):
            edge_attr = "eid0" if map_index == 0 else "eid1"
            grouped: dict[int, list[object]] = {}
            for xsect in xsect_edges_sorted[map_index]:
                grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
            point_offset = 0
            edge_id = 0
            for chain_index, chain in enumerate(dataset.chains):
                output_chain = rayjoin_overlay.RayjoinOverlayOutputChain(
                    points=[],
                    display_points=[],
                    left_polygon_id=int(chain.left_face_id),
                    right_polygon_id=int(chain.right_face_id),
                )
                for local_point_index, point in enumerate(chain.points):
                    point_index = point_offset + local_point_index
                    output_chain.other_map_polygon_id = int(point_in_polygon[map_index][point_index])
                    output_chain.points.append((float(point.x), float(point.y)))
                    output_chain.display_points.append((float(point.x), float(point.y)))
                    if local_point_index == len(chain.points) - 1:
                        continue
                    xsects = grouped.get(edge_id)
                    if xsects:
                        first = xsects[0]
                        output_chain.points.append((first.x, first.y))
                        output_chain.display_points.append(
                            (
                                first.display_x if first.display_x is not None else first.x,
                                first.display_y if first.display_y is not None else first.y,
                            )
                        )
                        for xsect, next_xsect in zip(xsects, xsects[1:]):
                            flush(output_chain, map_index, chain_index)
                            output_chain.other_map_polygon_id = rayjoin_overlay._midpoint_face_for_map(
                                xsect,
                                map_index,
                            )
                            output_chain.points.append((xsect.x, xsect.y))
                            output_chain.display_points.append(
                                (
                                    xsect.display_x if xsect.display_x is not None else xsect.x,
                                    xsect.display_y if xsect.display_y is not None else xsect.y,
                                )
                            )
                            output_chain.points.append((next_xsect.x, next_xsect.y))
                            output_chain.display_points.append(
                                (
                                    next_xsect.display_x if next_xsect.display_x is not None else next_xsect.x,
                                    next_xsect.display_y if next_xsect.display_y is not None else next_xsect.y,
                                )
                            )
                        flush(output_chain, map_index, chain_index)
                        last = xsects[-1]
                        output_chain.points.append((last.x, last.y))
                        output_chain.display_points.append(
                            (
                                last.display_x if last.display_x is not None else last.x,
                                last.display_y if last.display_y is not None else last.y,
                            )
                        )
                    edge_id += 1
                flush(output_chain, map_index, chain_index)
                point_offset += len(chain.points)

        trailing = author_handle.readline()
        if trailing:
            raise StreamingWriterMismatch({"line": line_no + 1, "author": trailing.rstrip("\n"), "rtdl": "<eof>"})
        author_handle.close()
        summary_state["streamed_chain_count"] = chain_count
        summary_state["streamed_face_count"] = len(face_ids)
        summary_state["streamed_point_count"] = streamed_point_count
        summary_state["streamed_line_count"] = line_no
        return {
            "path": str(path),
            "chain_count": chain_count,
            "face_count": len(face_ids),
            "line_count": line_no,
            "point_count": streamed_point_count,
            "streaming_compare": True,
        }

    rayjoin_overlay._write_output_chains_streaming = compare_writer


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
    placeholder = output_dir / "rtdl_streaming_compare_no_output.txt"
    summary_path = output_dir / "summary.json"
    summary_state: dict[str, object] = {}

    install_streaming_writer_compare(rayjoin_overlay, Path(args.author_output), summary_state)
    start = time.perf_counter()
    try:
        result = rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths(
            args.left,
            args.right,
            backend="optix",
            assemble_output=False,
            output_path=placeholder,
        )
        outcome = {"stream_match": True, "first_diff": None, "result": result}
    except StreamingWriterMismatch as exc:
        outcome = {"stream_match": False, "first_diff": exc.payload, "result": None}
    elapsed = time.perf_counter() - start
    summary = {
        "schema": "rtdl.goal4867.block_water.streaming_writer_compare.v1",
        "elapsed_sec": elapsed,
        "left": args.left,
        "right": args.right,
        "author_output": args.author_output,
        **summary_state,
        **outcome,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=_json_default), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=_json_default))


if __name__ == "__main__":
    main()
