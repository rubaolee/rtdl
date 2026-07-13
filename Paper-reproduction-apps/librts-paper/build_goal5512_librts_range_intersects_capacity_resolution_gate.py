from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src" / "rtdsl").is_dir()
)
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parks = json.loads(
        (RESULTS / "goal5512_parks_bz2_select0001_10000.json").read_text(
            encoding="utf-8"
        )
    )
    lakes = json.loads(
        (RESULTS / "goal5512_lakes_bz2_select0001_10000.json").read_text(
            encoding="utf-8"
        )
    )
    if parks["status"] != "author_capacity_failure":
        raise ValueError("parks case must remain an author capacity failure")
    if lakes["case_id"] != "lakes_bz2_select_0.0001_10000":
        raise ValueError("lakes retry must be normalized to the canonical case id")
    if not lakes.get("matched"):
        raise ValueError("lakes retry did not produce a count match")
    if parks["claim_boundary"]["semantic_mismatch_claimed"]:
        raise ValueError("capacity failure cannot be classified as semantic mismatch")

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5512_range_intersects_capacity_resolution.v1",
        "status": "goal5509_large_cases_resolved_one_author_capacity_failure_one_count_match",
        "operation": "range_intersects",
        "query_family": "range-intersects_select_0.0001_queries_10000",
        "cases": [parks, lakes],
        "case_count": 2,
        "matched_case_count": 1,
        "author_capacity_failure_case_count": 1,
        "unresolved_case_count": 0,
        "coverage": {
            "exact_range_intersects_archive_pair_count": 42,
            "goal5509_large_case_states_resolved": True,
            "complete_range_intersects_matrix_claimed": False,
            "remaining_exact_archive_pairs_not_attempted": True,
        },
        "claim_boundary": {
            "count_match_only_for_lakes": True,
            "parks_author_capacity_failure_only": True,
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "author_performance_parity_claimed": False,
            "device_zero_copy_claimed": False,
            "embree_in_scope": False,
        },
        "evidence_integrity": {
            "lakes_checkpoint_sha256": _sha256(
                RESULTS / "goal5512_lakes_bz2_select0001_10000.json"
            ),
            "parks_failure_record_sha256": _sha256(
                RESULTS / "goal5512_parks_bz2_select0001_10000.json"
            ),
        },
    }
    output = RESULTS / "goal5512_range_intersects_capacity_resolution_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
