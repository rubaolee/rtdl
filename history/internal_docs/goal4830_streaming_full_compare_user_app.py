from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


class StreamingMismatch(Exception):
    def __init__(self, line_no: int, author: str, rtdl: str) -> None:
        super().__init__(f"streaming mismatch at line {line_no}")
        self.line_no = line_no
        self.author = author
        self.rtdl = rtdl


class StreamedChains:
    def __init__(self) -> None:
        self.count = 0

    def __len__(self) -> int:
        return self.count


def install_streaming_comparer(rayjoin_overlay, author_output: Path, summary_state: dict[str, object]) -> None:
    author_handle = author_output.open("r", encoding="utf-8")
    line_no = 0

    def compare_line(generated: str) -> None:
        nonlocal line_no
        line_no += 1
        expected = author_handle.readline()
        if expected != generated:
            raise StreamingMismatch(line_no, expected.rstrip("\n") if expected else "<eof>", generated.rstrip("\n"))

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

        def emit(output_chain) -> None:
            nonlocal point_counter
            other = int(output_chain.other_map_polygon_id)
            left_polygon_id = create_polygon(*sorted((int(output_chain.left_polygon_id), other)))
            right_polygon_id = create_polygon(*sorted((int(output_chain.right_polygon_id), other)))
            for point in output_chain.points:
                if point not in point_ids:
                    point_ids[point] = point_counter
                    point_counter += 1
            first_point_idx = point_ids[output_chain.points[0]]
            last_point_idx = point_ids[output_chain.points[-1]]
            chains.count += 1
            compare_line(
                f"{chains.count} {len(output_chain.points)} {first_point_idx} {last_point_idx} "
                f"{left_polygon_id} {right_polygon_id}\n"
            )
            for x, y in output_chain.points:
                compare_line(f"{x:.6f} {y:.6f}\n")

        def flush(output_chain) -> None:
            if not output_chain.points:
                return
            keep = (
                output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
                or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
            )
            if keep:
                output_chain.points = rayjoin_overlay._dedupe_consecutive_points(output_chain.points)
                emit(output_chain)
            output_chain.points.clear()

        for map_index, dataset in enumerate(datasets):
            edge_attr = "eid0" if map_index == 0 else "eid1"
            grouped: dict[int, list[object]] = {}
            for xsect in xsect_edges_sorted[map_index]:
                grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
            point_offset = 0
            edge_id = 0
            for chain in dataset.chains:
                output_chain = rayjoin_overlay.RayjoinOverlayOutputChain(
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
                        for xsect, next_xsect in zip(xsects, xsects[1:]):
                            flush(output_chain)
                            output_chain.other_map_polygon_id = rayjoin_overlay._midpoint_face_for_map(
                                xsect,
                                map_index,
                            )
                            output_chain.points.append((xsect.x, xsect.y))
                            output_chain.points.append((next_xsect.x, next_xsect.y))
                        flush(output_chain)
                        output_chain.points.append((xsects[-1].x, xsects[-1].y))
                    edge_id += 1
                flush(output_chain)
                point_offset += len(chain.points)

        trailing = author_handle.readline()
        if trailing:
            raise StreamingMismatch(line_no + 1, trailing.rstrip("\n"), "<eof>")
        author_handle.close()
        summary_state["streamed_chain_count"] = chains.count
        summary_state["streamed_face_count"] = len(face_ids)
        summary_state["streamed_point_count"] = len(point_ids)
        summary_state["streamed_line_count"] = line_no
        return chains, len(face_ids)

    def write_noop(output_chains, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("", encoding="utf-8")
        return Path(path)

    rayjoin_overlay._assemble_output_chains = assemble_stream
    rayjoin_overlay.write_output_chains = write_noop


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
    placeholder = output_dir / "rtdl_stream_compare_placeholder.txt"
    summary_path = output_dir / "summary.json"
    summary_state: dict[str, object] = {}

    install_streaming_comparer(rayjoin_overlay, Path(args.author_output), summary_state)
    start = time.time()
    try:
        result = rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths(
            args.left,
            args.right,
            backend="optix",
            assemble_output=True,
            output_path=placeholder,
        )
        outcome = {
            "stream_match": True,
            "first_diff": None,
            "result": result,
        }
    except StreamingMismatch as exc:
        outcome = {
            "stream_match": False,
            "first_diff": {
                "line": exc.line_no,
                "author": exc.author,
                "rtdl": exc.rtdl,
            },
            "result": None,
        }
    elapsed = time.time() - start
    summary = {
        "schema": "rtdl.goal4830.streaming_compare.v1",
        "elapsed_sec": elapsed,
        **summary_state,
        **outcome,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
