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
    extraction_path = RESULTS / "librts_goal5509_range_intersects_batch_extraction.json"
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    case_paths = {
        "parks_Europe_select_0.0001_10000": RESULTS / "goal5509_parks_Europe_select0001_10000.json",
        "dtl_cnty_select_0.0001_10000": RESULTS / "goal5509_dtl_cnty_select0001_10000.json",
        "lakes_bz2_select_0.0001_10000": None,
        "USACensusBlockGroupBoundaries_select_0.0001_10000": RESULTS / "goal5509_USACensusBlockGroupBoundaries_select0001_10000.json",
        "USADetailedWaterBodies_select_0.0001_10000": RESULTS / "goal5509_USADetailedWaterBodies_select0001_10000.json",
        "parks_bz2_select_0.0001_10000": None,
    }
    cases = []
    for case_id, path in case_paths.items():
        if path is None:
            cases.append(
                {
                    "case_id": case_id,
                    "status": "not_checkpointed_after_batch_resource_termination",
                    "matched": False,
                    "result_available": False,
                    "interpretation": "unresolved_capacity_or_process-lifetime status; not a semantic mismatch",
                }
            )
        else:
            cases.append(json.loads(path.read_text(encoding="utf-8")))
    matched = [case for case in cases if case.get("matched") is True]
    unresolved = [case for case in cases if not case.get("result_available", True)]
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5509_exact_range_intersects_next_batch.v1",
        "status": (
            "exact_input_range_intersects_next_batch_completed_with_all_cases"
            if len(cases) == 6 and len(matched) == 6
            else "exact_input_range_intersects_next_batch_completed_bounded"
        ),
        "operation": "range_intersects",
        "query_family": "range-intersects_select_0.0001_queries_10000",
        "archive_extraction": {
            "result_path": str(extraction_path.relative_to(ROOT)).replace("\\", "/"),
            "selected_pair_count": extraction["extraction"]["selected_pair_count"],
            "selected_member_count": extraction["extraction"]["selected_member_count"],
            "verified_md5": extraction["archive"]["verified_md5"],
        },
        "case_count": len(cases),
        "matched_case_count": len(matched),
        "unresolved_case_count": len(unresolved),
        "cases": cases,
        "coverage": {
            "exact_range_intersects_archive_pair_count": 42,
            "previously_attempted_case_count": 6,
            "this_batch_case_count": len(cases),
            "this_batch_checkpointed_case_count": len(cases) - len(unresolved),
            "cumulative_attempted_case_count": 6 + len(cases) - len(unresolved),
            "remaining_unattempted_case_count": 42 - (6 + len(cases) - len(unresolved)),
        },
        "claim_boundary": {
            "same_input_count_level_evidence_only": True,
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "author_oom_resolved_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "device_zero_copy_claimed": False,
            "embree_in_scope": False,
        },
        "evidence_integrity": {
            "same_files_passed_to_author_and_rtdl": all(
                bool(case.get("input_identity", {}).get("same_files_passed_to_author_and_rtdl"))
                for case in cases
                if case.get("matched") is True
            ),
            "checkpoint_case_sha256": {
                case_id: _sha256(path)
                for case_id, path in case_paths.items()
                if path is not None
            },
        },
    }
    output = RESULTS / "goal5509_exact_range_intersects_next_batch_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
