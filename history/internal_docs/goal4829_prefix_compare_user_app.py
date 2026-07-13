from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


class PrefixDone(Exception):
    pass


def _read_prefix_lines(path: Path, chain_count: int) -> list[str]:
    lines: list[str] = []
    chains_seen = 0
    with path.open("r", encoding="utf-8") as handle:
        while chains_seen < chain_count:
            header = handle.readline()
            if not header:
                break
            lines.append(header)
            fields = header.split()
            if len(fields) < 2:
                raise ValueError(f"bad output-chain header in {path}: {header!r}")
            point_count = int(fields[1])
            for _ in range(point_count):
                point_line = handle.readline()
                if not point_line:
                    raise ValueError(f"unexpected EOF in {path}")
                lines.append(point_line)
            chains_seen += 1
    return lines


def install_prefix_assembler(rayjoin_overlay, max_chains: int) -> None:
    def assemble_prefix(datasets, xsect_edges_sorted, point_in_polygon):
        output_chains = []

        def flush(output_chain):
            if not output_chain.points:
                return
            keep = (
                output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
                or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
            )
            if keep:
                output_chain.points = rayjoin_overlay._dedupe_consecutive_points(output_chain.points)
                output_chains.append(
                    rayjoin_overlay.RayjoinOverlayOutputChain(
                        points=list(output_chain.points),
                        left_polygon_id=output_chain.left_polygon_id,
                        right_polygon_id=output_chain.right_polygon_id,
                        other_map_polygon_id=output_chain.other_map_polygon_id,
                    )
                )
                if len(output_chains) >= max_chains:
                    raise PrefixDone
            output_chain.points.clear()

        try:
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
        except PrefixDone:
            pass

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

        return output_chains, len(face_ids)

    rayjoin_overlay._assemble_output_chains = assemble_prefix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-chains", type=int, default=20)
    args = parser.parse_args()

    import rtdsl.rayjoin_overlay as rayjoin_overlay

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rtdl_prefix = output_dir / f"rtdl_prefix_{args.max_chains}.txt"
    summary_path = output_dir / "summary.json"

    install_prefix_assembler(rayjoin_overlay, args.max_chains)
    start = time.time()
    result = rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths(
        args.left,
        args.right,
        backend="optix",
        assemble_output=True,
        output_path=rtdl_prefix,
    )
    elapsed = time.time() - start

    author_lines = _read_prefix_lines(Path(args.author_output), args.max_chains)
    rtdl_lines = _read_prefix_lines(rtdl_prefix, args.max_chains)
    first_diff = None
    for line_no, (author_line, rtdl_line) in enumerate(zip(author_lines, rtdl_lines), start=1):
        if author_line != rtdl_line:
            first_diff = {
                "line": line_no,
                "author": author_line.rstrip("\n"),
                "rtdl": rtdl_line.rstrip("\n"),
            }
            break
    if first_diff is None and len(author_lines) != len(rtdl_lines):
        first_diff = {
            "line": min(len(author_lines), len(rtdl_lines)) + 1,
            "author": "<eof>" if len(author_lines) < len(rtdl_lines) else "<extra>",
            "rtdl": "<eof>" if len(rtdl_lines) < len(author_lines) else "<extra>",
        }

    summary = {
        "schema": "rtdl.goal4829.prefix_compare.v1",
        "max_chains": args.max_chains,
        "elapsed_sec": elapsed,
        "prefix_match": first_diff is None,
        "first_diff": first_diff,
        "rtdl_prefix_path": str(rtdl_prefix),
        "rtdl_prefix_bytes": rtdl_prefix.stat().st_size,
        "result": result,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
