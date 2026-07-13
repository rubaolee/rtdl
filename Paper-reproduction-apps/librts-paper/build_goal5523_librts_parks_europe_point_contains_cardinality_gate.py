from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def main() -> None:
    raw = json.loads((RESULTS / "goal5523_parks_europe_point_cardinality_pod_raw.json").read_text(encoding="utf-8"))
    extraction = json.loads(
        (RESULTS / "librts_goal5523_parks_europe_point_cardinality_extraction.json").read_text(encoding="utf-8")
    )
    cache = json.loads((RESULTS / "goal5523_parks_europe_point_cache_build.json").read_text(encoding="utf-8"))
    prior = json.loads((RESULTS / "goal5482_point_contains" / "parks_Europe.json").read_text(encoding="utf-8"))
    expected = {50000: 54568, 100000: 109279, 200000: 218598, 400000: 437276, 800000: 874543}
    observed = {
        int(case["query_cardinality"]): (
            int(case["author"]["result_count"]),
            int(case["rtdl"]["result_count"]),
            bool(case["matched"]),
        )
        for case in raw["cases"]
    }
    if observed != {cardinality: (count, count, True) for cardinality, count in expected.items()}:
        raise ValueError(f"unexpected Goal5523 matrix: {observed}")
    case_100000 = next(case for case in raw["cases"] if int(case["query_cardinality"]) == 100000)
    if int(prior["author"]["result_count"]) != expected[100000]:
        raise ValueError("Goal5523 differs from prior parks_Europe author count")
    if prior["input_identity"]["query_sha256"] != case_100000["input_identity"]["query_sha256"]:
        raise ValueError("Goal5523 differs from prior parks_Europe 100K query identity")
    if extraction["extraction"]["selected_pair_count"] != 5 or extraction["extraction"]["selected_member_count"] != 6:
        raise ValueError("Goal5523 extraction must contain one geometry plus five exact queries")
    if cache["source_sha256"] != raw["prepared_base"]["geometry_sha256"]:
        raise ValueError("Goal5523 cache and raw gate geometry identities differ")
    if not (cache["row_count"] == raw["prepared_base"]["indexed_count"] == 1856318):
        raise ValueError("Goal5523 prepared base row count mismatch")

    raw["schema"] = "rtdl.paper_reproduction.librts.goal5523_parks_europe_point_cardinality_gate.v2"
    raw["coverage"] = {
        "exact_archive_point_contains_pair_count": 14,
        "matched_before_goal5523": 10,
        "new_unique_goal5523_matches": 4,
        "prior_checkpoint_cardinality": 100000,
        "matched_after_goal5523": 14,
        "remaining_not_checkpointed": 0,
        "complete_point_contains_matrix_claimed": True,
    }
    raw["evidence_accounting"] = {
        "runtime_query_cardinalities": sorted(expected),
        "all_query_files_distinct": len({case["input_identity"]["query_sha256"] for case in raw["cases"]}) == 5,
        "prior_100000_checkpoint_identity_and_count_match": True,
        "cache_is_app_owned": not bool(cache["rtdl_core_wkt_semantics"]),
    }
    if not all(
        (
            raw["evidence_accounting"]["all_query_files_distinct"],
            raw["evidence_accounting"]["cache_is_app_owned"],
            raw["matched_case_count"] == 5,
            raw["case_count"] == 5,
        )
    ):
        raise ValueError("Goal5523 final accounting gate failed")
    raw["claim_boundary"].update(
        {
            "prior_independent_checkpoint_case_count": 1,
            "new_unique_count_match_count": 4,
            "complete_point_contains_matrix_claimed": True,
            "complete_point_contains_count_matrix_only": True,
        }
    )
    output = RESULTS / "goal5523_parks_europe_point_contains_cardinality_gate.json"
    output.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(raw, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
