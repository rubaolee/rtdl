from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    base = json.loads((RESULTS / "goal5513_exact_range_intersects_select001_gate.json").read_text(encoding="utf-8"))
    lakes = json.loads((RESULTS / "goal5514_lakes_bz2_select_0.01_10000.json").read_text(encoding="utf-8"))
    parks = json.loads((RESULTS / "goal5514_parks_bz2_select001_10000.json").read_text(encoding="utf-8"))
    if not lakes.get("matched") or parks["status"] != "author_capacity_failure":
        raise ValueError("large-case statuses are not the expected match/failure pair")
    if parks["claim_boundary"]["semantic_mismatch_claimed"]:
        raise ValueError("parks capacity failure cannot be a semantic mismatch")
    cases = base["cases"] + [lakes, parks]
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5514_exact_range_intersects_select001_resolution.v1",
        "status": "exact_input_range_intersects_select001_six_geometry_states_resolved",
        "operation": "range_intersects",
        "query_family": "range-intersects_select_0.01_queries_10000",
        "cases": cases,
        "case_count": 6,
        "matched_case_count": 5,
        "author_capacity_failure_case_count": 1,
        "unresolved_case_count": 0,
        "coverage": {
            "exact_range_intersects_archive_pair_count": 42,
            "query_family_geometry_count": 6,
            "query_family_states_resolved": True,
            "complete_range_intersects_matrix_claimed": False,
            "remaining_exact_archive_pairs_not_attempted": True,
        },
        "claim_boundary": {
            "count_match_cases_only": True,
            "author_capacity_failure_not_semantic_mismatch": True,
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "device_zero_copy_claimed": False,
            "author_performance_parity_claimed": False,
            "embree_in_scope": False,
        },
        "evidence_integrity": {
            "goal5513_gate_sha256": _sha256(RESULTS / "goal5513_exact_range_intersects_select001_gate.json"),
            "lakes_checkpoint_sha256": _sha256(RESULTS / "goal5514_lakes_bz2_select_0.01_10000.json"),
            "parks_failure_record_sha256": _sha256(RESULTS / "goal5514_parks_bz2_select001_10000.json"),
        },
    }
    output = RESULTS / "goal5514_exact_range_intersects_select001_resolution_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
