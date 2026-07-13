from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np
import rtdsl as rt

from run_exact_point_contains_count_gate import load_geometry_mbr_columns
from run_exact_range_intersects_count_gate import parse_author_range_intersects_output


TARGET_GEOMETRIES = {"parks_Europe.wkt", "lakes.bz2.wkt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prefix_lines(source: Path, target: Path, limit: int) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with source.open("rb") as input_stream, target.open("wb") as output_stream:
        for raw_line in input_stream:
            if not raw_line.strip():
                continue
            output_stream.write(raw_line)
            count += 1
            if count >= limit:
                break
    if count == 0:
        raise ValueError(f"empty WKT prefix: {source}")
    return count


def cpu_overlap_count(boxes, queries, *, cast_float32: bool, pad: float = 0.0) -> int:
    min_x = np.asarray(boxes.min_x, dtype=np.float32 if cast_float32 else np.float64)
    min_y = np.asarray(boxes.min_y, dtype=np.float32 if cast_float32 else np.float64)
    max_x = np.asarray(boxes.max_x, dtype=np.float32 if cast_float32 else np.float64)
    max_y = np.asarray(boxes.max_y, dtype=np.float32 if cast_float32 else np.float64)
    q_min_x = np.asarray(queries.min_x, dtype=min_x.dtype)
    q_min_y = np.asarray(queries.min_y, dtype=min_y.dtype)
    q_max_x = np.asarray(queries.max_x, dtype=max_x.dtype)
    q_max_y = np.asarray(queries.max_y, dtype=max_y.dtype)
    if pad:
        min_x = min_x - pad
        min_y = min_y - pad
        max_x = max_x + pad
        max_y = max_y + pad
    total = 0
    for start in range(0, len(q_min_x), 64):
        stop = min(start + 64, len(q_min_x))
        total += int(
            np.count_nonzero(
                (min_x[None, :] <= q_max_x[start:stop, None])
                & (max_x[None, :] >= q_min_x[start:stop, None])
                & (min_y[None, :] <= q_max_y[start:stop, None])
                & (max_y[None, :] >= q_min_y[start:stop, None])
            )
        )
    return total


def run_author(
    *,
    author_binary: Path,
    ae_root: Path,
    geometry: Path,
    query: Path,
    serialize_dir: Path,
) -> dict[str, object]:
    serialize_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(author_binary),
        "-geom", str(geometry),
        "-query", str(query),
        "-serialize", str(serialize_dir),
        "-query_type", "range-intersects",
        "-index_type", "rtspatial",
        "-load_factor", "1",
    ]
    environment = dict(os.environ)
    deps_lib = str(ae_root / "deps" / "lib")
    environment["LD_LIBRARY_PATH"] = deps_lib + (
        ":" + environment["LD_LIBRARY_PATH"]
        if environment.get("LD_LIBRARY_PATH")
        else ""
    )
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    wall = time.perf_counter() - started
    if completed.returncode != 0:
        return {
            "status": "author_execution_failed",
            "returncode": completed.returncode,
            "error": completed.stderr[-4000:],
            "command": command,
            "wall_sec": wall,
        }
    parsed = parse_author_range_intersects_output(completed.stdout)
    return {
        "status": "author_matched_contract",
        **parsed,
        "command": command,
        "wall_sec": wall,
        "stdout": completed.stdout,
    }


def run_case(
    *,
    case: dict[str, object],
    author_binary: Path,
    ae_root: Path,
    output_root: Path,
    geometry_lines: int,
    query_lines: int,
) -> dict[str, object]:
    geometry = Path(str(case["geometry"]))
    query = Path(str(case["query"]))
    case_id = str(case.get("case_id", geometry.name))
    case_root = output_root / case_id
    sample_geometry = case_root / "geometry_prefix.wkt"
    sample_query = case_root / "query_prefix.wkt"
    geometry_count = prefix_lines(geometry, sample_geometry, geometry_lines)
    query_count = prefix_lines(query, sample_query, query_lines)

    author = run_author(
        author_binary=author_binary,
        ae_root=ae_root,
        geometry=sample_geometry,
        query=sample_query,
        serialize_dir=case_root / "serialize",
    )
    boxes = load_geometry_mbr_columns(sample_geometry)
    queries = load_geometry_mbr_columns(sample_query)
    if len(boxes) != geometry_count or len(queries) != query_count:
        raise RuntimeError("prefix parser counts differ from source-line counts")

    cpu64 = cpu_overlap_count(boxes, queries, cast_float32=False)
    cpu32 = cpu_overlap_count(boxes, queries, cast_float32=True)
    cpu32_pad = cpu_overlap_count(boxes, queries, cast_float32=True, pad=1.0e-6)
    prepared = rt.prepare_aabb_index_2d_columns(boxes, backend="optix")
    try:
        query_started = time.perf_counter()
        rtdl_count = int(
            prepared.count(box_queries=queries, operation="range_intersects")["counts"]["range_intersects"]
        )
        rtdl_query_sec = time.perf_counter() - query_started
    finally:
        prepared.close()
    return {
        "case_id": case_id,
        "source_geometry": str(geometry),
        "source_query": str(query),
        "source_geometry_sha256": sha256(geometry),
        "source_query_sha256": sha256(query),
        "sample_geometry": str(sample_geometry),
        "sample_query": str(sample_query),
        "sample_geometry_sha256": sha256(sample_geometry),
        "sample_query_sha256": sha256(sample_query),
        "sample_geometry_count": geometry_count,
        "sample_query_count": query_count,
        "author": author,
        "rtdl_count": rtdl_count,
        "rtdl_query_sec": rtdl_query_sec,
        "cpu_oracle": {
            "float64_exact_overlap_count": cpu64,
            "float32_overlap_count": cpu32,
            "float32_index_pad_1e-6_overlap_count": cpu32_pad,
        },
        "diagnostic_matches": {
            "rtdl_equals_author": author.get("result_count") == rtdl_count,
            "rtdl_equals_cpu_float64": rtdl_count == cpu64,
            "rtdl_equals_cpu_float32": rtdl_count == cpu32,
            "rtdl_equals_cpu_float32_pad": rtdl_count == cpu32_pad,
            "author_equals_cpu_float64": author.get("result_count") == cpu64,
            "author_equals_cpu_float32": author.get("result_count") == cpu32,
        },
        "claim_boundary": {
            "full_input_equivalence_claimed": False,
            "root_cause_declared": False,
            "performance_ratio_authorized": False,
            "complete_range_intersects_matrix_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--geometry-lines", type=int, default=100_000)
    parser.add_argument("--query-lines", type=int, default=10_000)
    parser.add_argument(
        "--geometry-name",
        action="append",
        dest="geometry_names",
        help="optional geometry filename filter; defaults to the two known mismatch cases",
    )
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    selected_names = set(args.geometry_names or TARGET_GEOMETRIES)
    selected = [
        case for case in cases
        if Path(str(case["geometry"])).name in selected_names
    ]
    if not selected:
        raise ValueError("diagnostic geometry filter selected no cases")
    results = []
    for case in selected:
        results.append(
            run_case(
                case=case,
                author_binary=args.author_binary.resolve(),
                ae_root=args.ae_root.resolve(),
                output_root=args.output_root.resolve(),
                geometry_lines=args.geometry_lines,
                query_lines=args.query_lines,
            )
        )
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5501_range_intersects_mismatch_diagnostic.v1",
        "status": "diagnostic_completed",
        "sample_policy": {
            "geometry_lines": args.geometry_lines,
            "query_lines": args.query_lines,
            "same_source_prefix_for_author_rtdl_oracles": True,
        },
        "cases": results,
        "claim_boundary": {
            "root_cause_declared": False,
            "full_input_equivalence_claimed": False,
            "complete_range_intersects_matrix_claimed": False,
            "performance_ratio_authorized": False,
            "parks_bz2_oom_resolved": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
