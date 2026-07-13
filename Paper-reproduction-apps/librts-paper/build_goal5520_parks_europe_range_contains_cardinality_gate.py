from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def main() -> None:
    raw = json.loads((RESULTS / "goal5520_parks_europe_cardinality_pod_raw.json").read_text(encoding="utf-8"))
    extraction = json.loads(
        (RESULTS / "librts_goal5520_parks_europe_cardinality_extraction.json").read_text(encoding="utf-8")
    )
    cache = json.loads((RESULTS / "goal5520_parks_europe_cache_build.json").read_text(encoding="utf-8"))
    expected = {
        50000: 52245,
        100000: 104426,
        200000: 208918,
        400000: 417968,
        800000: 835864,
    }
    observed = {
        int(case["query_cardinality"]): (
            int(case["author"]["result_count"]),
            int(case["rtdl"]["result_count"]),
            bool(case["matched"]),
        )
        for case in raw["cases"]
    }
    if observed != {cardinality: (count, count, True) for cardinality, count in expected.items()}:
        raise ValueError(f"unexpected Goal5520 matrix: {observed}")
    if extraction["extraction"]["selected_pair_count"] != 4:
        raise ValueError("Goal5520 extraction must contain four new query pairs")
    if extraction["extraction"]["selected_member_count"] != 5:
        raise ValueError("Goal5520 extraction must contain one geometry plus four queries")
    if cache["source_sha256"] != raw["prepared_base"]["geometry_sha256"]:
        raise ValueError("Goal5520 cache and raw gate geometry identities differ")
    if not (cache["row_count"] == raw["prepared_base"]["indexed_count"] == 1856318):
        raise ValueError("Goal5520 prepared base row count mismatch")

    raw["schema"] = "rtdl.paper_reproduction.librts.goal5520_parks_europe_cardinality_gate.v2"
    raw["status"] = "parks_europe_exact_range_contains_five_cardinality_matrix_matched"
    raw["prepared_base"].pop("distinct_query_batches", None)
    raw["prepared_base"].update(
        {
            "runtime_distinct_query_batches": 4,
            "matrix_distinct_query_batches": 5,
            "prior_checkpoint_case_count": 1,
            "prior_checkpoint_cardinality": 100000,
            "same_input_replay_used": False,
        }
    )
    raw["coverage"] = {
        "exact_archive_range_contains_pair_count": 14,
        "matched_before_goal5520": 5,
        "new_goal5520_matches": 4,
        "matched_after_goal5520": 9,
        "remaining_not_checkpointed": 5,
        "complete_range_contains_matrix_claimed": False,
    }
    raw["evidence_accounting"] = {
        "runtime_new_query_cardinalities": [50000, 200000, 400000, 800000],
        "prior_goal5517_checkpoint_cardinality": 100000,
        "all_query_files_distinct": len({case["input_identity"]["query_sha256"] for case in raw["cases"]}) == 5,
        "extraction_selected_member_count": extraction["extraction"]["selected_member_count"],
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
        raise ValueError("Goal5520 final accounting gate failed")
    raw["claim_boundary"].update(
        {
            "prepared_base_runtime_case_count": 4,
            "prior_independent_checkpoint_case_count": 1,
            "complete_range_contains_matrix_claimed": False,
        }
    )
    output = RESULTS / "goal5520_parks_europe_range_contains_cardinality_gate.json"
    output.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(raw, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
