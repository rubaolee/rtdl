from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


class TargetCaptured(Exception):
    pass


class StreamingMismatch(Exception):
    def __init__(self, line_no: int, author: str, rtdl: str) -> None:
        super().__init__(f"streaming mismatch at line {line_no}")
        self.line_no = line_no
        self.author = author
        self.rtdl = rtdl


def install_probe(rayjoin_overlay, author_output: Path, target_chain: int, summary_state: dict[str, object]) -> None:
    author_handle = author_output.open("r", encoding="utf-8")
    line_no = 0
    chain_count = 0
    point_counter = 0
    face_ids: dict[tuple[int, int], int] = {}
    face_first_seen: dict[int, int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    recent_headers: list[dict[str, object]] = []

    def read_author_line(generated: str) -> tuple[str, bool]:
        nonlocal line_no
        line_no += 1
        expected = author_handle.readline()
        if expected != generated:
            return expected.rstrip("\n") if expected else "<eof>", False
        return expected.rstrip("\n"), True

    def create_polygon(polygon_id1: int, polygon_id2: int) -> tuple[int, tuple[int, int] | None]:
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0, None
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
        face_id = face_ids[key]
        face_first_seen.setdefault(face_id, chain_count + 1)
        return face_id, key

    def emit(output_chain, meta: dict[str, object]) -> None:
        nonlocal chain_count, point_counter
        other = int(output_chain.other_map_polygon_id)
        raw_left = int(output_chain.left_polygon_id)
        raw_right = int(output_chain.right_polygon_id)
        final_left, left_key = create_polygon(*sorted((raw_left, other)))
        final_right, right_key = create_polygon(*sorted((raw_right, other)))
        for point in output_chain.points:
            if point not in point_ids:
                point_ids[point] = point_counter
                point_counter += 1
        first_point_idx = point_ids[output_chain.points[0]]
        last_point_idx = point_ids[output_chain.points[-1]]
        chain_count += 1
        generated_header = (
            f"{chain_count} {len(output_chain.points)} {first_point_idx} {last_point_idx} "
            f"{final_left} {final_right}\n"
        )
        author_header, header_match = read_author_line(generated_header)
        record = {
            "chain": chain_count,
            "author_header": author_header,
            "generated_header": generated_header.rstrip("\n"),
            "header_match": header_match,
            "raw_left_polygon_id": raw_left,
            "raw_right_polygon_id": raw_right,
            "other_map_polygon_id": other,
            "left_key": left_key,
            "right_key": right_key,
            "final_left_polygon_id": final_left,
            "final_right_polygon_id": final_right,
            "first_point_idx": first_point_idx,
            "last_point_idx": last_point_idx,
            "points": [[float(x), float(y)] for x, y in output_chain.points],
            "meta": meta,
        }
        if chain_count >= target_chain - 4:
            recent_headers.append(record)
            if len(recent_headers) > 16:
                del recent_headers[0]
        if chain_count == target_chain or not header_match:
            summary_state["target_or_first_mismatch"] = record
            summary_state["recent_headers"] = list(recent_headers)
            summary_state["face_inverse_window"] = {
                str(face_id): {
                    "key": list(key),
                    "first_seen_chain": int(face_first_seen.get(face_id, -1)),
                }
                for key, face_id in face_ids.items()
                if face_id in {final_left, final_right, 280, 290, 294, 295}
            }
            summary_state["line_no_at_capture"] = line_no
            raise TargetCaptured()
        for x, y in output_chain.points:
            generated = f"{x:.6f} {y:.6f}\n"
            author_point, point_match = read_author_line(generated)
            if not point_match:
                raise StreamingMismatch(line_no, author_point, generated.rstrip("\n"))

    def flush(output_chain, meta: dict[str, object]) -> None:
        if not output_chain.points:
            return
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            output_chain.points = rayjoin_overlay._dedupe_consecutive_points(output_chain.points)
            emit(output_chain, meta)
        output_chain.points.clear()

    def assemble_probe(datasets, xsect_edges_sorted, point_in_polygon):
        for map_index, dataset in enumerate(datasets):
            edge_attr = "eid0" if map_index == 0 else "eid1"
            grouped: dict[int, list[object]] = {}
            for xsect in xsect_edges_sorted[map_index]:
                grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
            point_offset = 0
            edge_id = 0
            for dataset_chain_index, chain in enumerate(dataset.chains):
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
                        flush(
                            output_chain,
                            {
                                "map_index": map_index,
                                "dataset_chain_index": dataset_chain_index,
                                "edge_id": edge_id,
                                "local_point_index": local_point_index,
                                "flush_kind": "vertex_to_first_intersection",
                                "xsect_count_on_edge": len(xsects),
                            },
                        )
                        for xsect_index, (xsect, next_xsect) in enumerate(zip(xsects, xsects[1:])):
                            output_chain.other_map_polygon_id = rayjoin_overlay._midpoint_face_for_map(
                                xsect,
                                map_index,
                            )
                            output_chain.points.append((xsect.x, xsect.y))
                            output_chain.points.append((next_xsect.x, next_xsect.y))
                            flush(
                                output_chain,
                                {
                                    "map_index": map_index,
                                    "dataset_chain_index": dataset_chain_index,
                                    "edge_id": edge_id,
                                    "local_point_index": local_point_index,
                                    "flush_kind": "between_adjacent_intersections",
                                    "xsect_index": xsect_index,
                                    "xsect_count_on_edge": len(xsects),
                                    "xsect_eid0": int(getattr(xsect, "eid0")),
                                    "xsect_eid1": int(getattr(xsect, "eid1")),
                                    "next_xsect_eid0": int(getattr(next_xsect, "eid0")),
                                    "next_xsect_eid1": int(getattr(next_xsect, "eid1")),
                                },
                            )
                        output_chain.points.append((xsects[-1].x, xsects[-1].y))
                    edge_id += 1
                flush(
                    output_chain,
                    {
                        "map_index": map_index,
                        "dataset_chain_index": dataset_chain_index,
                        "edge_id": edge_id - 1,
                        "flush_kind": "tail_or_unsplit_chain",
                    },
                )
                point_offset += len(chain.points)
        return [], len(face_ids)

    def write_noop(output_chains, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("", encoding="utf-8")
        return Path(path)

    rayjoin_overlay._assemble_output_chains = assemble_probe
    rayjoin_overlay.write_output_chains = write_noop


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--target-chain", type=int, default=41230)
    args = parser.parse_args()

    import rtdsl.rayjoin_overlay as rayjoin_overlay

    summary_state: dict[str, object] = {
        "schema": "rtdl.goal4862.chain_face_assignment_probe.v1",
        "target_chain": int(args.target_chain),
    }
    install_probe(rayjoin_overlay, Path(args.author_output), int(args.target_chain), summary_state)
    start = time.time()
    try:
        rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths(
            args.left,
            args.right,
            backend="optix",
            assemble_output=True,
            output_path=Path(args.output_json).with_suffix(".placeholder.txt"),
        )
        summary_state["outcome"] = "completed_without_target_capture"
    except TargetCaptured:
        summary_state["outcome"] = "target_or_mismatch_captured"
    except StreamingMismatch as exc:
        summary_state["outcome"] = "point_line_mismatch_before_target"
        summary_state["point_line_mismatch"] = {
            "line": exc.line_no,
            "author": exc.author,
            "rtdl": exc.rtdl,
        }
    summary_state["elapsed_sec"] = time.time() - start
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary_state, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary_state, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
