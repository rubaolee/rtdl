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
        and record["category"].startswith("range-contains_queries_")
    ]
    counts = {
        int(record["category"].removeprefix("range-contains_queries_")): int(record["result_count"])
        for record in records
    }
    if len(counts) != len(records):
        raise ValueError("duplicate parks.bz2 range-contains paper-log cardinality")
    return counts


def main() -> None:
    raw = json.loads(
        (RESULTS / "goal5521_parks_bz2_cardinality_pod_raw.json").read_text(encoding="utf-8")
    )
    extraction = json.loads(
        (RESULTS / "librts_goal5521_parks_bz2_cardinality_extraction.json").read_text(encoding="utf-8")
    )
    precheck = json.loads(
        (RESULTS / "goal5521_parks_bz2_author_capacity_precheck.json").read_text(encoding="utf-8")
    )
    cache = json.loads((RESULTS / "goal5521_parks_bz2_cache_build.json").read_text(encoding="utf-8"))
    expected = {
        50000: 52849,
        100000: 105826,
        200000: 211714,
        400000: 423396,
        800000: 846860,
    }
    if _paper_log_counts() != expected:
        raise ValueError("Goal5521 expected counts differ from pinned author paper logs")
    observed = {
        int(case["query_cardinality"]): (
            int(case["author"]["result_count"]),
            int(case["rtdl"]["result_count"]),
            bool(case["matched"]),
        )
        for case in raw["cases"]
    }
    if observed != {cardinality: (count, count, True) for cardinality, count in expected.items()}:
        raise ValueError(f"unexpected Goal5521 matrix: {observed}")
    if precheck["status"] != "parks_bz2_author_50000_completed":
        raise ValueError("Goal5521 author capacity precheck did not complete")
    if not precheck["decision"]["authorize_rtdl_cache_and_matrix"]:
        raise ValueError("Goal5521 author precheck did not authorize the matrix")
    if extraction["extraction"]["selected_pair_count"] != 5:
        raise ValueError("Goal5521 extraction must contain five exact pairs")
    if extraction["extraction"]["selected_member_count"] != 6:
        raise ValueError("Goal5521 extraction must contain one geometry plus five queries")
    if cache["source_sha256"] != raw["prepared_base"]["geometry_sha256"]:
        raise ValueError("Goal5521 cache and raw gate geometry identities differ")
    if not (cache["row_count"] == raw["prepared_base"]["indexed_count"] == 11544398):
        raise ValueError("Goal5521 prepared base row count mismatch")

    raw["schema"] = "rtdl.paper_reproduction.librts.goal5521_parks_bz2_cardinality_gate.v2"
    raw["status"] = "parks_bz2_exact_range_contains_five_cardinality_matrix_matched"
    raw["coverage"] = {
        "exact_archive_range_contains_pair_count": 14,
        "matched_before_goal5521": 9,
        "new_goal5521_matches": 5,
        "matched_after_goal5521": 14,
        "remaining_not_checkpointed": 0,
        "complete_range_contains_matrix_claimed": True,
    }
    raw["evidence_accounting"] = {
        "runtime_query_cardinalities": sorted(expected),
        "all_query_files_distinct": len({case["input_identity"]["query_sha256"] for case in raw["cases"]}) == 5,
        "all_author_counts_match_pinned_paper_logs": all(
            int(case["author"]["result_count"]) == expected[int(case["query_cardinality"])]
            for case in raw["cases"]
        ),
        "extraction_selected_member_count": extraction["extraction"]["selected_member_count"],
        "author_capacity_precheck_completed": True,
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
        raise ValueError("Goal5521 final accounting gate failed")
    raw["claim_boundary"].update(
        {
            "complete_range_contains_matrix_claimed": True,
            "complete_range_contains_count_matrix_only": True,
            "pointwise_containment_equivalence_claimed": False,
        }
    )
    output = RESULTS / "goal5521_parks_bz2_range_contains_cardinality_gate.json"
    output.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(raw, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
