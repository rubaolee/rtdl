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


SCHEMA = "rtdl.paper_reproduction.librts.goal5520_parks_europe_cardinality_gate.v1"
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
        raise ValueError(f"query path lacks range-contains cardinality: {path}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-target", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--cache-prefix", type=Path, required=True)
    parser.add_argument("--prior-100000", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--serialize-root", type=Path, required=True)
    parser.add_argument(
        "--author-binary",
        type=Path,
        default=Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query"),
    )
    parser.add_argument("--ae-root", type=Path, default=Path("/workspace/librts-ae"))
    args = parser.parse_args()

    pairs = json.loads(args.pairs.read_text(encoding="utf-8"))
    extraction = json.loads(args.extraction.read_text(encoding="utf-8"))
    extracted = {
        item["relative_path"]: item
        for item in extraction["extraction"]["selected_members"]
    }
    geometry_members = {pair["geometry"] for pair in pairs}
    if geometry_members != {"PPoPPAE/datasets/polygons/parks_Europe.wkt"}:
        raise ValueError("Goal5520 requires one parks_Europe prepared base")
    geometry_member = next(iter(geometry_members))
    geometry_path = args.base_target / geometry_member
    if _sha256(geometry_path) != extracted[geometry_member]["sha256"]:
        raise ValueError("extracted geometry SHA-256 mismatch")

    indexed, cache_metadata = load_cached_columns(
        geometry_path=geometry_path,
        cache_prefix=args.cache_prefix,
    )
    prepare_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
    prepare_sec = time.perf_counter() - prepare_start
    cases = []
    try:
        for pair in sorted(pairs, key=lambda item: _cardinality(item["query"])):
            cardinality = _cardinality(pair["query"])
            query_path = args.base_target / pair["query"]
            query_sha256 = _sha256(query_path)
            if query_sha256 != extracted[pair["query"]]["sha256"]:
                raise ValueError(f"extracted query SHA-256 mismatch: {cardinality}")
            serialize_dir = args.serialize_root / str(cardinality)
            serialize_dir.mkdir(parents=True, exist_ok=True)
            author, author_stdout, author_command = run_author_range_contains(
                author_binary=args.author_binary,
                ae_root=args.ae_root,
                geometry_path=geometry_path,
                query_path=query_path,
                serialize_dir=serialize_dir,
            )
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
                    "case_id": f"parks_Europe_range_contains_{cardinality}",
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

    prior = json.loads(args.prior_100000.read_text(encoding="utf-8"))
    if prior["case_id"] != "parks_Europe_range_contains_100000" or not prior["matched"]:
        raise ValueError("Goal5517 parks_Europe 100K checkpoint is not a match")
    if prior["input_identity"]["geometry_sha256"] != cache_metadata["source_sha256"]:
        raise ValueError("Goal5517 geometry identity differs from Goal5520")
    prior_case = {
        "case_id": prior["case_id"],
        "query_cardinality": 100000,
        "input_identity": prior["input_identity"],
        "author": prior["author"],
        "rtdl": prior["rtdl"],
        "matched": True,
        "evidence_source": "Goal5517 independent checkpoint",
    }
    all_cases = sorted(cases + [prior_case], key=lambda item: item["query_cardinality"])
    matched_count = sum(bool(case["matched"]) for case in all_cases)
    payload = {
        "schema": SCHEMA,
        "status": (
            "parks_europe_range_contains_cardinality_matrix_matched"
            if matched_count == len(all_cases)
            else "parks_europe_range_contains_cardinality_matrix_has_mismatch"
        ),
        "operation": "range_contains",
        "prepared_base": {
            "geometry_member": geometry_member,
            "geometry_sha256": cache_metadata["source_sha256"],
            "indexed_count": len(indexed),
            "cache_contract": cache_metadata["schema"],
            "prepare_index_sec": prepare_sec,
            "runtime_distinct_query_batches": len(cases),
            "matrix_distinct_query_batches": len(all_cases),
            "prior_checkpoint_case_count": len(all_cases) - len(cases),
            "same_input_replay_used": False,
        },
        "case_count": len(all_cases),
        "matched_case_count": matched_count,
        "cases": all_cases,
        "claim_boundary": {
            "exact_archive_same_input_count_evidence": True,
            "prepared_base_distinct_query_batches": True,
            "same_input_replay_claimed": False,
            "pointwise_containment_equivalence_claimed": False,
            "complete_range_contains_matrix_claimed": False,
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
    return 0 if matched_count == len(all_cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
