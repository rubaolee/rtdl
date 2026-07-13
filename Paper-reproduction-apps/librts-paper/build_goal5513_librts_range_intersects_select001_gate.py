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
        (DATA / "goal5513_range_intersects_select001_exact_batch.json").read_text(
            encoding="utf-8"
        )
    )
    results = []
    for case in cases:
        result_path = RESULTS / f"goal5513_{case['case_id']}.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("case_id") != case["case_id"] or not result.get("matched"):
            raise ValueError(f"case failed: {case['case_id']}")
        if not result["input_identity"]["same_files_passed_to_author_and_rtdl"]:
            raise ValueError(f"same-input flag missing: {case['case_id']}")
        results.append(result)

    extraction_path = RESULTS / "librts_goal5513_range_intersects_batch_extraction.json"
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    selected = {
        item["relative_path"]: item
        for item in extraction["extraction"]["selected_members"]
    }
    input_identity = {}
    for result in results:
        identity = result["input_identity"]
        for path_key, hash_key in (("geometry_path", "geometry_sha256"), ("query_path", "query_sha256")):
            relative = identity[path_key].split("/goal5500-range-intersects/", 1)[1]
            if selected.get(relative, {}).get("sha256") != identity[hash_key]:
                raise ValueError(f"extraction hash mismatch: {relative}")
        input_identity[result["case_id"]] = {
            "geometry_sha256": identity["geometry_sha256"],
            "query_sha256": identity["query_sha256"],
            "same_files_passed_to_author_and_rtdl": True,
        }

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5513_exact_range_intersects_select001.v1",
        "status": "exact_input_range_intersects_select001_completed_bounded",
        "operation": "range_intersects",
        "query_family": "range-intersects_select_0.01_queries_10000",
        "archive_extraction": {
            "result_path": str(extraction_path.relative_to(ROOT)).replace("\\", "/"),
            "selected_pair_count": extraction["extraction"]["selected_pair_count"],
            "selected_member_count": extraction["extraction"]["selected_member_count"],
            "verified_md5": extraction["archive"]["verified_md5"],
        },
        "case_count": len(results),
        "matched_case_count": len(results),
        "cases": results,
        "coverage": {
            "exact_range_intersects_archive_pair_count": 42,
            "this_query_family_case_count": len(results),
            "this_query_family_checkpointed_case_count": len(results),
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
            "same_files_passed_to_author_and_rtdl": True,
            "input_identity": input_identity,
            "checkpoint_case_sha256": {
                case["case_id"]: _sha256(RESULTS / f"goal5513_{case['case_id']}.json")
                for case in cases
            },
        },
    }
    output = RESULTS / "goal5513_exact_range_intersects_select001_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
