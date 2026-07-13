from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import rtdsl as rt

from run_exact_point_contains_count_gate import (
    _sha256,
    load_geometry_mbrs,
    load_point_queries,
    run_author,
    validate_exact_input_evidence,
)


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
    author, author_stdout, author_command = run_author(
        author_binary=author_binary,
        ae_root=ae_root,
        geometry_path=geometry_path,
        query_path=query_path,
        serialize_dir=serialize_dir,
    )
    load_start = time.perf_counter()
    boxes = load_geometry_mbrs(geometry_path)
    points = load_point_queries(query_path)
    rtdl_load_sec = time.perf_counter() - load_start
    if len(boxes) != author["geometry_count"] or len(points) != author["query_count"]:
        raise RuntimeError("author and RTDL WKT row counts differ before execution")
    route_start = time.perf_counter()
    rtdl = rt.query_aabb_index_2d(
        boxes,
        point_queries=points,
        operation="point_contains",
        backend="optix",
    )
    rtdl_route_sec = time.perf_counter() - route_start
    result_count = int(rtdl["counts"]["point_contains"])
    matched = result_count == int(author["result_count"])
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_point_contains_count_only.v1",
        "status": (
            "exact_input_point_contains_count_matched"
            if matched
            else "exact_input_point_contains_count_mismatch"
        ),
        "matched": matched,
        "input_identity": {
            "verified_extraction_root": str(extraction_root),
            "same_files_passed_to_author_and_rtdl": True,
            "geometry_path": str(geometry_path),
            "geometry_size_bytes": geometry_path.stat().st_size,
            "geometry_sha256": _sha256(geometry_path),
            "query_path": str(query_path),
            "query_size_bytes": query_path.stat().st_size,
            "query_sha256": _sha256(query_path),
        },
        "author": {
            **author,
            "command": author_command,
            "stdout": author_stdout,
            "pair_rows_exposed": False,
        },
        "rtdl": {
            "public_api": "query_aabb_index_2d",
            "operation": "point_contains",
            "count_only": True,
            "row_output_requested": False,
            "backend": rtdl["backend"],
            "result_count": result_count,
            "load_wkt_sec": rtdl_load_sec,
            "route_wall_sec": rtdl_route_sec,
            "primitive_query_sec": rtdl["run_phases"]["query_aabb_index_2d_sec"],
            "rt_core_accelerated": rtdl["rt_core_accelerated"],
            "native_engine_customization": rtdl["native_engine_customization"],
        },
        "claim_boundary": {
            "exact_archive_and_extracted_input_identity_used": True,
            "same_input_result_count_agreement": matched,
            "pointwise_containment_equivalence_claimed": False,
            "relation_level_evidence_reference": "Paper-reproduction-apps/librts-paper/results/librts_goal5467_representative_same_input_pip.json",
            "author_pair_relation_agreement_claimed": False,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
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
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
