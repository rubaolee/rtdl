from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import rtdsl as rt

from build_exact_aabb_column_cache import load_cached_columns
from run_exact_point_contains_count_gate import (
    _sha256,
    load_geometry_mbr_columns,
    load_geometry_mbr_columns_fast,
    load_point_queries,
    run_author,
    validate_exact_input_evidence,
)


def run_repeat(
    *,
    author_binary: Path,
    ae_root: Path,
    geometry_path: Path,
    query_path: Path,
    serialize_dir: Path,
    archive_result: dict[str, object],
    extraction_result: dict[str, object],
    repeat: int,
    loader: str = "regex",
    cache_prefix: Path | None = None,
    author_result: dict[str, object] | None = None,
) -> dict[str, object]:
    if repeat < 2:
        raise ValueError("repeat must be at least 2 to measure same-process reuse")
    extraction_root = validate_exact_input_evidence(
        archive_result=archive_result,
        extraction_result=extraction_result,
        geometry_path=geometry_path,
        query_path=query_path,
    )
    if author_result is None:
        author, author_stdout, author_command = run_author(
            author_binary=author_binary,
            ae_root=ae_root,
            geometry_path=geometry_path,
            query_path=query_path,
            serialize_dir=serialize_dir,
        )
    else:
        identity = author_result.get("input_identity", {})
        if identity.get("geometry_sha256") != _sha256(geometry_path):
            raise ValueError("reused author evidence geometry hash does not match")
        if identity.get("query_sha256") != _sha256(query_path):
            raise ValueError("reused author evidence query hash does not match")
        author = dict(author_result["author"])
        author_stdout = "reused exact-input author evidence"
        author_command = ["reused_author_result_json"]

    if loader not in {"regex", "numpy", "cache"}:
        raise ValueError("loader must be regex, numpy, or cache")
    if loader == "cache":
        if cache_prefix is None:
            raise ValueError("cache loader requires cache_prefix")
        load_start = time.perf_counter()
        boxes, cache_metadata = load_cached_columns(
            geometry_path=geometry_path,
            cache_prefix=cache_prefix,
        )
        load_sec = time.perf_counter() - load_start
    else:
        geometry_loader = load_geometry_mbr_columns if loader == "regex" else load_geometry_mbr_columns_fast
        cache_metadata = None
        load_start = time.perf_counter()
        boxes = geometry_loader(geometry_path)
        load_sec = time.perf_counter() - load_start
    points = load_point_queries(query_path)
    load_sec = time.perf_counter() - load_start
    if len(boxes) != author["geometry_count"] or len(points) != author["query_count"]:
        raise RuntimeError("author and RTDL WKT row counts differ before execution")

    prepare_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d_columns(boxes, backend="optix")
    prepare_sec = time.perf_counter() - prepare_start
    queries: list[dict[str, object]] = []
    try:
        for index in range(repeat):
            query_start = time.perf_counter()
            result = prepared.count(point_queries=points, operation="point_contains")
            wall_sec = time.perf_counter() - query_start
            result_count = int(result["counts"]["point_contains"])
            queries.append(
                {
                    "iteration": index + 1,
                    "result_count": result_count,
                    "matched_author_count": result_count == int(author["result_count"]),
                    "prepared_query_wall_sec": wall_sec,
                    "primitive_query_sec": result["run_phases"]["query_aabb_index_2d_sec"],
                    "backend": result["backend"],
                    "rt_core_accelerated": result["rt_core_accelerated"],
                }
            )
    finally:
        prepared.close()

    if not all(item["matched_author_count"] for item in queries):
        raise RuntimeError("same-process repeated query did not preserve author count")
    query_wall = [float(item["prepared_query_wall_sec"]) for item in queries]
    primitive = [float(item["primitive_query_sec"]) for item in queries]
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_point_contains_prepared_phase_columns_repeat.v1",
        "status": "exact_input_point_contains_prepared_phase_columns_repeat_matched",
        "matched": True,
        "repeat": repeat,
        "geometry_loader": loader,
        "cache_metadata": cache_metadata,
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
            "operation": "point_contains",
            "input_contract": "generic_host_aabb_2d_columns",
            "load_wkt_sec": load_sec,
            "prepare_index_sec": prepare_sec,
            "queries": queries,
            "query_wall_summary": {
                "first_sec": query_wall[0],
                "subsequent_median_sec": statistics.median(query_wall[1:]),
                "all_median_sec": statistics.median(query_wall),
            },
            "primitive_query_summary": {
                "first_sec": primitive[0],
                "subsequent_median_sec": statistics.median(primitive[1:]),
                "all_median_sec": statistics.median(primitive),
            },
        },
        "phase_boundary": {
            "same_process_reuse_only": True,
            "author_query_excludes_loading": True,
            "rtdl_repeated_queries_exclude_wkt_load_and_index_prepare": True,
            "performance_ratio_authorized": False,
        },
        "claim_boundary": {
            "exact_archive_and_extracted_input_identity_used": True,
            "same_input_result_count_agreement": True,
            "pointwise_containment_equivalence_claimed": False,
            "generic_columnar_frontdoor_used": True,
            "same_process_reuse_diagnostic": True,
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
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--loader", choices=("regex", "numpy", "cache"), default="regex")
    parser.add_argument("--cache-prefix", type=Path)
    parser.add_argument("--author-result-json", type=Path)
    args = parser.parse_args()
    args.serialize_dir.mkdir(parents=True, exist_ok=True)
    payload = run_repeat(
        author_binary=args.author_binary.resolve(),
        ae_root=args.ae_root.resolve(),
        geometry_path=args.geometry.resolve(),
        query_path=args.query.resolve(),
        serialize_dir=args.serialize_dir.resolve(),
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction_result=json.loads(args.extraction_result.read_text(encoding="utf-8")),
        repeat=args.repeat,
        loader=args.loader,
        cache_prefix=args.cache_prefix.resolve() if args.cache_prefix else None,
        author_result=(
            json.loads(args.author_result_json.read_text(encoding="utf-8"))
            if args.author_result_json
            else None
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
