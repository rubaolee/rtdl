from __future__ import annotations

import argparse
import struct
from pathlib import Path


CHECKSUM = 0xABCDABCD


def restore_pgraph_cache_to_cdb(cache_path: Path, output_path: Path, *, flush_every: int = 1_000_000) -> dict[str, int]:
    """Restore a RayJoin serialized PlanarGraph cache to text CDB.

    This is an internal recovery tool for Goal4851. It mirrors RayJoin's
    `serialize_pgraph` layout in `src/map/planar_graph.h`:

    checksum, n_chains, n_row_index, n_points
    chains: int64 id, first, last, left_face, right_face
    row_index: uint32[n_row_index]
    points: double x/y[n_points]
    bbox: four doubles
    checksum
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("rb") as inp:
        checksum, n_chains, n_row_index, n_points = struct.unpack("<QQQQ", inp.read(32))
        if checksum != CHECKSUM:
            raise ValueError(f"unexpected leading checksum {checksum:#x} in {cache_path}")

        chains_raw = inp.read(n_chains * 5 * 8)
        row_index_raw = inp.read(n_row_index * 4)
        points_offset = inp.tell()

        chain_struct = struct.Struct("<qqqqq")
        row_index_struct = struct.Struct("<I")
        point_struct = struct.Struct("<dd")

        with output_path.open("w", encoding="utf-8", newline="\n") as out:
            for chain_idx in range(n_chains):
                chain_offset = chain_idx * 5 * 8
                chain_id, first_point_id, last_point_id, left_face_id, right_face_id = chain_struct.unpack_from(
                    chains_raw,
                    chain_offset,
                )
                start = row_index_struct.unpack_from(row_index_raw, chain_idx * 4)[0]
                end = row_index_struct.unpack_from(row_index_raw, (chain_idx + 1) * 4)[0]
                point_count = end - start
                out.write(
                    f"{chain_id} {point_count} {first_point_id} {last_point_id} "
                    f"{left_face_id} {right_face_id}\n"
                )
                inp.seek(points_offset + start * 16)
                for _ in range(point_count):
                    x, y = point_struct.unpack(inp.read(16))
                    out.write(f"{x:.10e} {y:.10e}\n")
                if flush_every > 0 and chain_idx and chain_idx % flush_every == 0:
                    out.flush()

        inp.seek(points_offset + n_points * 16)
        min_x, min_y, max_x, max_y = struct.unpack("<dddd", inp.read(32))
        trailing_checksum = struct.unpack("<Q", inp.read(8))[0]
        if trailing_checksum != CHECKSUM:
            raise ValueError(f"unexpected trailing checksum {trailing_checksum:#x} in {cache_path}")

    return {
        "chains": int(n_chains),
        "row_index": int(n_row_index),
        "points": int(n_points),
        "segments": int(n_points - n_chains),
        "min_x": float(min_x),
        "min_y": float(min_y),
        "max_x": float(max_x),
        "max_y": float(max_y),
        "bytes": int(output_path.stat().st_size),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    stats = restore_pgraph_cache_to_cdb(args.cache, args.output)
    for key, value in stats.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
