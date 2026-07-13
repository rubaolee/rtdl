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
DATA = APP / "data"
RESULTS = APP / "results"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    cases = json.loads(
        (DATA / "goal5511_range_intersects_select0001_exact_batch.json").read_text(
            encoding="utf-8"
        )
    )
    case_results = []
    for case in cases:
        result_path = RESULTS / f"goal5511_{case['case_id']}.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("case_id") != case["case_id"]:
            raise ValueError(f"case id mismatch: {result_path}")
        if not result.get("matched"):
            raise ValueError(f"case is not matched: {case['case_id']}")
        if not result.get("claim_boundary", {}).get("same_input_result_count_agreement"):
            raise ValueError(f"same-input flag missing: {case['case_id']}")
        case_results.append(result)

    extraction_path = RESULTS / "librts_goal5511_range_intersects_batch_extraction.json"
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    selected_members = {
        item["relative_path"]: item
        for item in extraction["extraction"]["selected_members"]
    }
    input_identity = {}
    for case in case_results:
        identity = case["input_identity"]
        for key in ("geometry_path", "query_path"):
            relative = identity[key].split("/goal5500-range-intersects/", 1)[1]
            record = selected_members.get(relative)
            if record is None:
                raise ValueError(f"missing archive extraction record: {relative}")
            if record["sha256"] != identity[key.replace("_path", "_sha256")]:
                raise ValueError(f"extraction hash mismatch: {relative}")
        input_identity[case["case_id"]] = {
            "geometry_sha256": identity["geometry_sha256"],
            "query_sha256": identity["query_sha256"],
            "same_files_passed_to_author_and_rtdl": identity[
                "same_files_passed_to_author_and_rtdl"
            ],
        }

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5511_exact_range_intersects_select0001.v1",
        "status": "exact_input_range_intersects_select0001_completed_bounded",
        "operation": "range_intersects",
        "query_family": "range-intersects_select_0.001_queries_10000",
        "archive_extraction": {
            "result_path": str(extraction_path.relative_to(ROOT)).replace("\\", "/"),
            "selected_pair_count": extraction["extraction"]["selected_pair_count"],
            "selected_member_count": extraction["extraction"]["selected_member_count"],
            "verified_md5": extraction["archive"]["verified_md5"],
        },
        "case_count": len(case_results),
        "matched_case_count": len(case_results),
        "cases": case_results,
        "coverage": {
            "exact_range_intersects_archive_pair_count": 42,
            "this_query_family_case_count": len(case_results),
            "this_query_family_checkpointed_case_count": len(case_results),
            "complete_range_intersects_matrix_claimed": False,
            "remaining_exact_archive_pairs_not_attempted": True,
        },
        "claim_boundary": {
            "same_input_count_level_evidence_only": True,
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "device_zero_copy_claimed": False,
            "author_performance_parity_claimed": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "embree_in_scope": False,
        },
        "evidence_integrity": {
            "same_files_passed_to_author_and_rtdl": all(
                bool(item["same_files_passed_to_author_and_rtdl"])
                for item in input_identity.values()
            ),
            "input_identity": input_identity,
            "checkpoint_case_sha256": {
                case["case_id"]: _sha256(RESULTS / f"goal5511_{case['case_id']}.json")
                for case in cases
            },
        },
    }
    output = RESULTS / "goal5511_exact_range_intersects_select0001_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
