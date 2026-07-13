from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
DATA = APP / "data"
RESULTS = APP / "results"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _case_name(geometry: str) -> str:
    return Path(geometry).name.removesuffix(".wkt") + "_range_contains_100000"


def main() -> None:
    pairs = json.loads((DATA / "goal5517_range_contains_exact_batch.json").read_text(encoding="utf-8"))
    extraction_path = RESULTS / "librts_goal5517_range_contains_batch_extraction.json"
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    selected = {item["relative_path"]: item for item in extraction["extraction"]["selected_members"]}
    results = []
    input_identity = {}
    checkpoint_hashes = {}
    for pair in pairs:
        case = _case_name(pair["geometry"])
        result_path = RESULTS / f"goal5517_{case}.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("case_id") != case or not result.get("matched"):
            raise ValueError(f"case failed: {case}")
        identity = result["input_identity"]
        for member_key, hash_key in (("geometry", "geometry_sha256"), ("query", "query_sha256")):
            member = pair[member_key]
            if selected.get(member, {}).get("sha256") != identity[hash_key]:
                raise ValueError(f"extraction hash mismatch: {member}")
        if not identity["same_files_passed_to_author_and_rtdl"]:
            raise ValueError(f"same-input flag missing: {case}")
        results.append(result)
        input_identity[case] = {
            "geometry_sha256": identity["geometry_sha256"],
            "query_sha256": identity["query_sha256"],
            "same_files_passed_to_author_and_rtdl": True,
        }
        checkpoint_hashes[case] = _sha256(result_path)

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5517_exact_range_contains_batch.v1",
        "status": "exact_input_range_contains_four_case_batch_matched",
        "operation": "range_contains",
        "query_family": "range-contains_queries_100000",
        "case_count": len(results),
        "matched_case_count": len(results),
        "cases": results,
        "archive_extraction": {
            "result_path": str(extraction_path.relative_to(ROOT)).replace("\\", "/"),
            "selected_pair_count": extraction["extraction"]["selected_pair_count"],
            "selected_member_count": extraction["extraction"]["selected_member_count"],
            "verified_md5": extraction["archive"]["verified_md5"],
            "workspace_quota_fallback": "extracted under /tmp after /workspace quota failure",
        },
        "coverage": {
            "exact_range_contains_archive_pair_count": 14,
            "this_batch_checkpointed_case_count": len(results),
            "complete_range_contains_matrix_claimed": False,
            "remaining_exact_archive_pairs_not_attempted": True,
        },
        "claim_boundary": {
            "same_input_count_level_evidence_only": True,
            "complete_range_contains_matrix_claimed": False,
            "pointwise_containment_equivalence_claimed": False,
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
            "checkpoint_case_sha256": checkpoint_hashes,
        },
    }
    output = RESULTS / "goal5517_exact_range_contains_batch_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
