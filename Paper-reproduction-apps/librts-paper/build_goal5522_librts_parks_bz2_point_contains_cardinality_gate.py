from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def _paper_log_counts() -> dict[int, int]:
    denominators = json.loads(
        (RESULTS / "librts_goal5472_author_paper_log_denominators.json").read_text(encoding="utf-8")
    )
    records = [
        record
        for record in denominators["records"]
        if record["index_type"] == "rtspatial"
        and record["dataset"] == "parks.bz2.wkt.log"
        and record["category"].startswith("point-contains_queries_")
    ]
    return {
        int(record["category"].removeprefix("point-contains_queries_")): int(record["result_count"])
        for record in records
    }


def main() -> None:
    raw = json.loads((RESULTS / "goal5522_parks_bz2_point_cardinality_pod_raw.json").read_text(encoding="utf-8"))
    extraction = json.loads(
        (RESULTS / "librts_goal5522_parks_bz2_point_cardinality_extraction.json").read_text(encoding="utf-8")
    )
    cache = json.loads((RESULTS / "goal5521_parks_bz2_cache_build.json").read_text(encoding="utf-8"))
    expected = {50000: 56428, 100000: 112729, 200000: 225699, 400000: 451007, 800000: 901103}
    if _paper_log_counts() != expected:
        raise ValueError("Goal5522 expected counts differ from pinned author paper logs")
    observed = {
        int(case["query_cardinality"]): (
            int(case["author"]["result_count"]),
            int(case["rtdl"]["result_count"]),
            bool(case["matched"]),
        )
        for case in raw["cases"]
    }
    if observed != {cardinality: (count, count, True) for cardinality, count in expected.items()}:
        raise ValueError(f"unexpected Goal5522 matrix: {observed}")
    if extraction["extraction"]["selected_pair_count"] != 5:
        raise ValueError("Goal5522 extraction must contain five exact pairs")
    if extraction["extraction"]["selected_member_count"] != 6:
        raise ValueError("Goal5522 extraction must contain one geometry plus five queries")
    if extraction["extraction"]["reused_verified_member_count"] != 1:
        raise ValueError("Goal5522 must reuse exactly one verified geometry")
    if extraction["extraction"]["newly_extracted_member_count"] != 5:
        raise ValueError("Goal5522 must add exactly five point-query members")
    if cache["source_sha256"] != raw["prepared_base"]["geometry_sha256"]:
        raise ValueError("Goal5522 cache and raw gate geometry identities differ")
    if not (cache["row_count"] == raw["prepared_base"]["indexed_count"] == 11544398):
        raise ValueError("Goal5522 prepared base row count mismatch")

    raw["schema"] = "rtdl.paper_reproduction.librts.goal5522_parks_bz2_point_cardinality_gate.v2"
    raw["status"] = "parks_bz2_exact_point_contains_five_cardinality_matrix_matched"
    raw["coverage"] = {
        "exact_archive_point_contains_pair_count": 14,
        "matched_before_goal5522": 6,
        "new_unique_goal5522_matches": 4,
        "prior_checkpoint_cardinality": 100000,
        "matched_after_goal5522": 10,
        "remaining_not_checkpointed": 4,
        "complete_point_contains_matrix_claimed": False,
    }
    raw["evidence_accounting"] = {
        "runtime_query_cardinalities": sorted(expected),
        "all_query_files_distinct": len({case["input_identity"]["query_sha256"] for case in raw["cases"]}) == 5,
        "all_author_counts_match_pinned_paper_logs": all(
            int(case["author"]["result_count"]) == expected[int(case["query_cardinality"])]
            for case in raw["cases"]
        ),
        "prior_100000_checkpoint_source": "Goals5481-5484 exact point-contains matrix",
        "cache_reused_from_goal5521": True,
        "cache_is_app_owned": not bool(cache["rtdl_core_wkt_semantics"]),
    }
    if not all(
        (
            raw["evidence_accounting"]["all_query_files_distinct"],
            raw["evidence_accounting"]["all_author_counts_match_pinned_paper_logs"],
            raw["evidence_accounting"]["cache_is_app_owned"],
            raw["matched_case_count"] == 5,
            raw["case_count"] == 5,
        )
    ):
        raise ValueError("Goal5522 final accounting gate failed")
    raw["claim_boundary"].update(
        {
            "prior_independent_checkpoint_case_count": 1,
            "new_unique_count_match_count": 4,
            "complete_point_contains_matrix_claimed": False,
        }
    )
    output = RESULTS / "goal5522_parks_bz2_point_contains_cardinality_gate.json"
    output.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(raw, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
