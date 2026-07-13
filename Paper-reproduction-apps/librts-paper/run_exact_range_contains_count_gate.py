from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import rtdsl as rt

from run_exact_point_contains_count_gate import (
    _sha256,
    load_geometry_mbr_columns,
    parse_author_output,
    validate_exact_input_evidence,
)


def run_author_range_contains(
    *,
    author_binary: Path,
    ae_root: Path,
    geometry_path: Path,
    query_path: Path,
    serialize_dir: Path,
) -> tuple[dict[str, object], str, list[str]]:
    command = [
        str(author_binary),
        "-geom",
        str(geometry_path),
        "-query",
        str(query_path),
        "-serialize",
        str(serialize_dir),
        "-query_type",
        "range-contains",
        "-index_type",
        "rtspatial",
        "-load_factor",
        "0.0001",
    ]
    environment = os.environ.copy()
    deps_lib = str(ae_root / "deps" / "lib")
    environment["LD_LIBRARY_PATH"] = deps_lib + (
        ":" + environment["LD_LIBRARY_PATH"] if environment.get("LD_LIBRARY_PATH") else ""
    )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"author range-contains failed with exit {completed.returncode}: "
            f"{completed.stderr[-2000:]}"
        )
    return parse_author_output(completed.stdout), completed.stdout, command


def run_gate(
    *,
    author_binary: Path,
    ae_root: Path,
    geometry_path: Path,
    query_path: Path,
    serialize_dir: Path,
    archive_result: dict[str, object],
    extraction_result: dict[str, object],
) -> dict[str, object]:
    extraction_root = validate_exact_input_evidence(
        archive_result=archive_result,
        extraction_result=extraction_result,
        geometry_path=geometry_path,
        query_path=query_path,
    )
    author, author_stdout, author_command = run_author_range_contains(
        author_binary=author_binary,
        ae_root=ae_root,
        geometry_path=geometry_path,
        query_path=query_path,
        serialize_dir=serialize_dir,
    )
    load_start = time.perf_counter()
    boxes = load_geometry_mbr_columns(geometry_path)
    queries = load_geometry_mbr_columns(query_path)
    load_sec = time.perf_counter() - load_start
    if len(boxes) != author["geometry_count"] or len(queries) != author["query_count"]:
        raise RuntimeError("author and RTDL WKT row counts differ before execution")
    prepare_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d_columns(boxes, backend="optix")
    prepare_sec = time.perf_counter() - prepare_start
    try:
        query_start = time.perf_counter()
        rtdl = prepared.count(box_queries=queries, operation="range_contains")
        query_wall_sec = time.perf_counter() - query_start
    finally:
        prepared.close()
    result_count = int(rtdl["counts"]["range_contains"])
    matched = result_count == int(author["result_count"])
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_range_contains_count_gate.v1",
        "status": "exact_input_range_contains_count_matched" if matched else "exact_input_range_contains_count_mismatch",
        "matched": matched,
        "input_identity": {
            "verified_extraction_root": str(extraction_root),
            "same_files_passed_to_author_and_rtdl": True,
            "geometry_path": str(geometry_path),
            "geometry_sha256": _sha256(geometry_path),
            "query_path": str(query_path),
            "query_sha256": _sha256(query_path),
        },
        "author": {
            **author,
            "command": author_command,
            "stdout": author_stdout,
            "pair_rows_exposed": False,
            "query_metric": "internal Query Time; index Loading Time excluded",
        },
        "rtdl": {
            "public_api": "Aabb2DColumns + prepare_aabb_index_2d_columns + prepared.count",
            "operation": "range_contains",
            "backend": rtdl["backend"],
            "result_count": result_count,
            "row_output_requested": False,
            "input_contract": "generic_host_aabb_2d_columns",
            "load_wkt_sec": load_sec,
            "prepare_index_sec": prepare_sec,
            "prepared_query_wall_sec": query_wall_sec,
            "primitive_query_sec": rtdl["run_phases"]["query_aabb_index_2d_sec"],
            "rt_core_accelerated": rtdl["rt_core_accelerated"],
            "native_engine_customization": rtdl["native_engine_customization"],
        },
        "phase_boundary": {
            "author_query_excludes_loading": True,
            "rtdl_prepared_query_excludes_wkt_load_and_index_prepare": True,
            "performance_ratio_authorized": False,
        },
        "claim_boundary": {
            "exact_archive_and_extracted_input_identity_used": True,
            "same_input_result_count_agreement": matched,
            "pointwise_containment_equivalence_claimed": False,
            "generic_columnar_frontdoor_used": True,
            "device_zero_copy_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--serialize-dir", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--extraction-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.serialize_dir.mkdir(parents=True, exist_ok=True)
    payload = run_gate(
        author_binary=args.author_binary.resolve(),
        ae_root=args.ae_root.resolve(),
        geometry_path=args.geometry.resolve(),
        query_path=args.query.resolve(),
        serialize_dir=args.serialize_dir.resolve(),
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction_result=json.loads(args.extraction_result.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
