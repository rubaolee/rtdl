from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

import rtdsl as rt

from build_exact_aabb_column_cache import load_cached_columns
from run_exact_point_contains_count_gate import load_geometry_mbr_columns
from run_exact_range_contains_count_gate import run_author_range_contains


CARDINALITY_RE = re.compile(r"range-contains_queries_(\d+)")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cardinality(path: str) -> int:
    match = CARDINALITY_RE.search(path)
    if match is None:
        raise ValueError(f"query path lacks cardinality: {path}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-target", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--cache-prefix", type=Path, required=True)
    parser.add_argument("--precheck", type=Path, required=True)
    parser.add_argument("--shared-serialize-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--author-binary",
        type=Path,
        default=Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query"),
    )
    parser.add_argument("--ae-root", type=Path, default=Path("/workspace/librts-ae"))
    args = parser.parse_args()

    pairs = json.loads(args.pairs.read_text(encoding="utf-8"))
    extraction = json.loads(args.extraction.read_text(encoding="utf-8"))
    members = {item["relative_path"]: item for item in extraction["extraction"]["selected_members"]}
    geometry_member = "PPoPPAE/datasets/polygons/parks.bz2.wkt"
    if {pair["geometry"] for pair in pairs} != {geometry_member}:
        raise ValueError("Goal5521 requires one parks.bz2 prepared base")
    geometry_path = args.base_target / geometry_member
    if _sha256(geometry_path) != members[geometry_member]["sha256"]:
        raise ValueError("parks.bz2 geometry SHA-256 mismatch")

    precheck = json.loads(args.precheck.read_text(encoding="utf-8"))
    if precheck["status"] != "parks_bz2_author_50000_completed":
        raise ValueError("Goal5521 matrix requires a successful author 50K precheck")
    if not precheck["decision"]["authorize_rtdl_cache_and_matrix"]:
        raise ValueError("Goal5521 precheck did not authorize the matrix")

    indexed, cache_metadata = load_cached_columns(
        geometry_path=geometry_path,
        cache_prefix=args.cache_prefix,
    )
    prepare_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
    prepare_sec = time.perf_counter() - prepare_start
    args.shared_serialize_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    try:
        for pair in sorted(pairs, key=lambda item: _cardinality(item["query"])):
            cardinality = _cardinality(pair["query"])
            query_path = args.base_target / pair["query"]
            query_sha256 = _sha256(query_path)
            if query_sha256 != members[pair["query"]]["sha256"]:
                raise ValueError(f"query SHA-256 mismatch: {cardinality}")
            if cardinality == 50000:
                author = precheck["author"]
                author_stdout = precheck["stdout"]
                author_command = precheck["command"]
                author_evidence_source = "Goal5521 capacity precheck"
            else:
                author, author_stdout, author_command = run_author_range_contains(
                    author_binary=args.author_binary,
                    ae_root=args.ae_root,
                    geometry_path=geometry_path,
                    query_path=query_path,
                    serialize_dir=args.shared_serialize_dir,
                )
                author_evidence_source = "Goal5521 shared prepared-base follow-up"
            query_load_start = time.perf_counter()
            queries = load_geometry_mbr_columns(query_path)
            query_load_sec = time.perf_counter() - query_load_start
            if len(queries) != cardinality or int(author["query_count"]) != cardinality:
                raise ValueError(f"query cardinality mismatch: {cardinality}")
            query_start = time.perf_counter()
            rtdl = prepared.count(box_queries=queries, operation="range_contains")
            query_sec = time.perf_counter() - query_start
            rtdl_count = int(rtdl["counts"]["range_contains"])
            author_count = int(author["result_count"])
            cases.append(
                {
                    "case_id": f"parks_bz2_range_contains_{cardinality}",
                    "query_cardinality": cardinality,
                    "input_identity": {
                        "geometry_sha256": cache_metadata["source_sha256"],
                        "query_sha256": query_sha256,
                        "same_files_passed_to_author_and_rtdl": True,
                    },
                    "author": {
                        **author,
                        "command": author_command,
                        "stdout": author_stdout,
                        "evidence_source": author_evidence_source,
                    },
                    "rtdl": {
                        "result_count": rtdl_count,
                        "query_load_sec": query_load_sec,
                        "prepared_query_wall_sec": query_sec,
                        "primitive_query_sec": rtdl["run_phases"]["query_aabb_index_2d_sec"],
                    },
                    "matched": author_count == rtdl_count,
                }
            )
    finally:
        prepared.close()

    matched_count = sum(bool(case["matched"]) for case in cases)
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5521_parks_bz2_cardinality_gate.v1",
        "status": (
            "parks_bz2_exact_range_contains_five_cardinality_matrix_matched"
            if matched_count == len(cases)
            else "parks_bz2_exact_range_contains_cardinality_matrix_has_mismatch"
        ),
        "operation": "range_contains",
        "prepared_base": {
            "geometry_member": geometry_member,
            "geometry_sha256": cache_metadata["source_sha256"],
            "indexed_count": len(indexed),
            "cache_contract": cache_metadata["schema"],
            "prepare_index_sec": prepare_sec,
            "runtime_distinct_query_batches": len(cases),
            "shared_author_serialization_base": True,
            "same_input_replay_used": False,
        },
        "case_count": len(cases),
        "matched_case_count": matched_count,
        "cases": cases,
        "claim_boundary": {
            "exact_archive_same_input_count_evidence": True,
            "prepared_base_distinct_query_batches": True,
            "same_input_replay_claimed": False,
            "pointwise_containment_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure_reproduction_claimed": False,
            "complete_paper_reproduction_claimed": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if matched_count == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
