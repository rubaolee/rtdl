#!/usr/bin/env python3
"""Section 5.3 PIP count through the directed point-location RTDL front door.

This runner intentionally avoids the bundled RayJoin overlay helper.  It uses
the released directed-segment point-location primitive and a user-side streaming
CDB adapter so large Section 5.3 inputs do not require loading both maps as
Python object graphs at once.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

from rtdsl import prepare_planar_map_point_location_2d_optix
from rtdsl.optix_runtime import pack_points
from rtdsl.embree_runtime import PackedRayjoinCdbSegments
from rtdsl.embree_runtime import _RtdlRayjoinCdbSegment


@dataclass(frozen=True)
class CdbStats:
    path: str
    chain_count: int
    point_count: int
    segment_count: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float


def _timed(func):
    start = time.perf_counter()
    value = func()
    return value, time.perf_counter() - start


def _log(message: str) -> None:
    print(f"[goal4855-section53] {message}", file=sys.stderr, flush=True)


def _parse_header(line: str, *, line_no: int) -> tuple[int, int, int, int, int, int]:
    fields = line.split()
    if len(fields) != 6:
        raise ValueError(f"invalid CDB header at line {line_no}: {line.rstrip()!r}")
    return tuple(int(value) for value in fields)  # type: ignore[return-value]


def _stream_cdb_chains(path: Path) -> Iterator[tuple[tuple[int, int, int, int, int, int], list[tuple[float, float]]]]:
    with path.open("r", encoding="utf-8") as handle:
        line_no = 0
        while True:
            line = handle.readline()
            line_no += 1
            while line and not line.strip():
                line = handle.readline()
                line_no += 1
            if not line:
                break
            header = _parse_header(line, line_no=line_no)
            _, point_count, _, _, _, _ = header
            points: list[tuple[float, float]] = []
            for _ in range(point_count):
                point_line = handle.readline()
                line_no += 1
                if not point_line:
                    raise ValueError(f"unexpected EOF while reading CDB chain at line {line_no}")
                point_fields = point_line.split()
                if len(point_fields) != 2:
                    raise ValueError(f"invalid CDB point at line {line_no}: {point_line.rstrip()!r}")
                points.append((float(point_fields[0]), float(point_fields[1])))
            yield header, points


def _scan_cdb(path: Path) -> CdbStats:
    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")
    chain_count = 0
    point_count_total = 0
    segment_count = 0
    for _, points in _stream_cdb_chains(path):
        chain_count += 1
        point_count_total += len(points)
        segment_count += max(0, len(points) - 1)
        for x, y in points:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    if point_count_total == 0:
        raise ValueError(f"CDB input has no points: {path}")
    return CdbStats(
        path=str(path),
        chain_count=chain_count,
        point_count=point_count_total,
        segment_count=segment_count,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
    )


def _shared_bounds(left: CdbStats, right: CdbStats) -> tuple[float, float, float, float]:
    return (
        min(left.min_x, right.min_x),
        max(left.max_x, right.max_x),
        min(left.min_y, right.min_y),
        max(left.max_y, right.max_y),
    )


def _rayjoin_cdb_segment_dtype() -> np.dtype:
    dtype = np.dtype(
        [
            ("id", np.uint32),
            ("x0", np.float64),
            ("y0", np.float64),
            ("x1", np.float64),
            ("y1", np.float64),
            ("left_face_id", np.uint32),
            ("right_face_id", np.uint32),
        ],
        align=True,
    )
    if dtype.itemsize != ctypes.sizeof(_RtdlRayjoinCdbSegment):
        raise RuntimeError(
            "NumPy structured segment layout does not match the RTDL packed C ABI layout"
        )
    return dtype


def _pack_base_segments_stream(path: Path, expected_segments: int) -> PackedRayjoinCdbSegments:
    dtype = _rayjoin_cdb_segment_dtype()
    owner = np.empty(expected_segments, dtype=dtype)
    index = 0
    next_id = 1
    for header, points in _stream_cdb_chains(path):
        _, _, _, _, left_face_id, right_face_id = header
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            owner[index] = (
                np.uint32(next_id),
                float(x0),
                float(y0),
                float(x1),
                float(y1),
                np.uint32(left_face_id),
                np.uint32(right_face_id),
            )
            index += 1
            next_id += 1
    if index != expected_segments:
        raise RuntimeError(f"segment count changed while packing {path}: {index} != {expected_segments}")
    records = (_RtdlRayjoinCdbSegment * expected_segments).from_buffer(owner)
    return PackedRayjoinCdbSegments(records=records, count=expected_segments, owner=owner)


def _iter_query_point_chunks(path: Path, *, chunk_size: int):
    ids = np.empty(chunk_size, dtype=np.uint32)
    xs = np.empty(chunk_size, dtype=np.float64)
    ys = np.empty(chunk_size, dtype=np.float64)
    count = 0
    next_id = 1
    for _, points in _stream_cdb_chains(path):
        for x, y in points:
            ids[count] = np.uint32(next_id)
            xs[count] = float(x)
            ys[count] = float(y)
            count += 1
            next_id += 1
            if count == chunk_size:
                packed, pack_sec = _timed(
                    lambda: pack_points(
                        ids=ids[:count],
                        x=xs[:count],
                        y=ys[:count],
                        dimension=2,
                    )
                )
                yield int(next_id - count), packed, pack_sec
                count = 0
    if count:
        packed, pack_sec = _timed(
            lambda: pack_points(
                ids=ids[:count],
                x=xs[:count],
                y=ys[:count],
                dimension=2,
            )
        )
        yield int(next_id - count), packed, pack_sec


def _reject_bundled_helper_import() -> None:
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("rtdsl.rayjoin_overlay was imported; this script must use the primitive front door")


def _count_section53_direction(
    *,
    poly1: Path,
    poly2: Path,
    poly1_stats: CdbStats,
    poly2_stats: CdbStats,
    scale_bounds: tuple[float, float, float, float],
    chunk_size: int,
):
    _log(f"pack base segments from {poly1} ({poly1_stats.segment_count} segments)")
    packed_base, pack_base_sec = _timed(lambda: _pack_base_segments_stream(poly1, poly1_stats.segment_count))
    _log(f"prepare directed point-location primitive ({poly1_stats.segment_count} base segments)")
    prepare_start = time.perf_counter()
    chunks = []
    total_count = 0
    total_chunk_pack_sec = 0.0
    total_count_sec = 0.0
    total_native_traversal_sec = 0.0
    with prepare_planar_map_point_location_2d_optix(
        packed_base,
        query_map_id=1,
        scale_bounds=scale_bounds,
    ) as locator:
        prepare_sec = time.perf_counter() - prepare_start
        for chunk_index, (first_point_id, packed_points, pack_sec) in enumerate(
            _iter_query_point_chunks(poly2, chunk_size=chunk_size),
            start=1,
        ):
            total_chunk_pack_sec += pack_sec
            _log(
                "count chunk "
                f"{chunk_index}: first_point_id={first_point_id} "
                f"points={packed_points.count}"
            )
            chunk_start = time.perf_counter()
            count, count_sec = _timed(lambda: locator.count_positive_faces(packed_points))
            chunk_elapsed = time.perf_counter() - chunk_start
            phase_timings = locator.last_phase_timings()
            traversal_sec = float(phase_timings.get("traversal", 0.0))
            total_native_traversal_sec += traversal_sec
            total_count_sec += count_sec
            total_count += int(count)
            _log(
                "chunk "
                f"{chunk_index} done: positives={count} "
                f"count_wall={count_sec:.6f}s native_traversal={traversal_sec:.6f}s"
            )
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "first_point_id": int(first_point_id),
                    "point_count": int(packed_points.count),
                    "positive_face_count": int(count),
                    "pack_points_sec": pack_sec,
                    "count_wall_sec": count_sec,
                    "chunk_elapsed_sec": chunk_elapsed,
                    "native_phase_timings": phase_timings,
                }
            )
    _reject_bundled_helper_import()
    return {
        "base_dataset": str(poly1),
        "query_dataset": str(poly2),
        "query_map_id": 1,
        "base_segments": int(poly1_stats.segment_count),
        "query_points": int(poly2_stats.point_count),
        "positive_face_count": int(total_count),
        "api_parameters": {
            "query_map_id": 1,
            "scale_bounds": tuple(float(value) for value in scale_bounds),
        },
        "chunk_size": int(chunk_size),
        "chunk_count": len(chunks),
        "chunks": chunks,
        "timings_sec": {
            "pack_base_segments_stream": pack_base_sec,
            "prepare": prepare_sec,
            "pack_query_points_stream": total_chunk_pack_sec,
            "count_total_wall": total_count_sec,
            "native_traversal_total": total_native_traversal_sec,
            "total_direction_observed": pack_base_sec + prepare_sec + total_count_sec,
        },
    }


def _run_author(author_exec: str | None, poly1: str, poly2: str, output_dir: Path, label: str):
    if not author_exec:
        return None
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / f"{label}.authorpatch.stdout"
    stderr_path = output_dir / f"{label}.authorpatch.stderr"
    cmd = [
        author_exec,
        "-poly1",
        poly1,
        "-poly2",
        poly2,
        "-serialize=/dev/shm",
        "-grid_size=15000",
        "-mode=rt",
        "-v=1",
        "-fau",
        "-xsect_factor",
        "0.1",
        "-enlarge=3.5",
        "-check=false",
        "-warmup=0",
        "-repeat=1",
        "-query=pip",
    ]
    _log(f"run AuthorPatch baseline for {label}")
    start = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, stdout=out, stderr=err, text=True)
    elapsed = time.perf_counter() - start
    return {
        "command": cmd,
        "returncode": int(proc.returncode),
        "elapsed_sec": elapsed,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_tail": "\n".join(stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()[-80:]),
        "stderr_tail": "\n".join(stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()[-80:]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poly1", required=True)
    parser.add_argument("--poly2", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--author-exec", default=None)
    parser.add_argument("--author-output-dir", default=None)
    parser.add_argument("--chunk-size", type=int, default=500_000)
    args = parser.parse_args()

    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be positive")

    _reject_bundled_helper_import()
    poly1 = Path(args.poly1)
    poly2 = Path(args.poly2)
    _log(f"scan poly1 stats: {poly1}")
    poly1_stats, scan_poly1_sec = _timed(lambda: _scan_cdb(poly1))
    _log(f"scan poly2 stats: {poly2}")
    poly2_stats, scan_poly2_sec = _timed(lambda: _scan_cdb(poly2))
    _log(
        "stats ready: "
        f"poly1 points={poly1_stats.point_count} segments={poly1_stats.segment_count}; "
        f"poly2 points={poly2_stats.point_count} segments={poly2_stats.segment_count}"
    )
    scale_bounds = _shared_bounds(poly1_stats, poly2_stats)

    direction = _count_section53_direction(
        poly1=poly1,
        poly2=poly2,
        poly1_stats=poly1_stats,
        poly2_stats=poly2_stats,
        scale_bounds=scale_bounds,
        chunk_size=args.chunk_size,
    )
    author = _run_author(
        args.author_exec,
        str(poly1),
        str(poly2),
        Path(args.author_output_dir) if args.author_output_dir else Path(args.output).parent,
        args.label,
    )

    summary = {
        "schema": "rtdl.goal4855.section53_pip_streaming_front_door.v2",
        "label": args.label,
        "poly1": str(poly1),
        "poly2": str(poly2),
        "paper_section": "5.3 PIP Performance",
        "section53_direction_contract": "query_exec -query=pip probes poly2/map1 vertices against poly1/map0",
        "authorpatch_command_shape": "query_exec -query=pip -mode=rt -grid_size=15000 -xsect_factor 0.1 -enlarge=3.5",
        "rtdl_public_api": "prepare_planar_map_point_location_2d_optix",
        "streaming_adapter": "user-side CDB streaming packer for large public inputs",
        "scale_bounds": list(scale_bounds),
        "input_stats": {
            "poly1": poly1_stats.__dict__,
            "poly2": poly2_stats.__dict__,
            "scan_timings_sec": {"poly1": scan_poly1_sec, "poly2": scan_poly2_sec},
        },
        "direction_mode": "section53_poly2_in_poly1",
        "directions": {"section53_poly2_vertices_in_poly1": direction},
        "section53_positive_faces": int(direction["positive_face_count"]),
        "authorpatch": author,
        "claim_boundary": {
            "section53_pip_count_only": True,
            "directed_point_location_public_primitive_used": True,
            "streaming_packer_uses_internal_layout_for_memory_safety": True,
            "bundled_rayjoin_helper_used": False,
            "section57_overlay_claim": False,
            "all_eight_exact_paper_pairs_claim": False,
            "broad_speedup_claim": False,
        },
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if author is None or author["returncode"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
