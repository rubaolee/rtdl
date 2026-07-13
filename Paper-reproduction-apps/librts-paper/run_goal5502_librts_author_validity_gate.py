from __future__ import annotations

import argparse
import json
from pathlib import Path


SCHEMA = "rtdl.paper_reproduction.librts.goal5502_author_validity_gate.v1"


def classify_case(case: dict[str, object]) -> dict[str, object]:
    matches = case.get("diagnostic_matches")
    if not isinstance(matches, dict):
        return {
            "case_id": case.get("case_id"),
            "classification": "unresolved_missing_oracle_evidence",
            "decision": "collect_independent_or_contract_evidence",
            "author_matches_selected_generic_contract": False,
            "rtdl_matches_selected_generic_contract": False,
        }

    author_match = bool(matches.get("author_equals_cpu_float32", False))
    rtdl_match = bool(matches.get("rtdl_equals_cpu_float32", False))
    if author_match and rtdl_match:
        classification = "author_and_rtdl_match_selected_generic_contract"
        decision = "no_semantic_fix_required_for_this_case"
    elif author_match and not rtdl_match:
        classification = "author_matches_contract_rtdl_diverges"
        decision = "fix_rtdl_before_author_reproduction_claim"
    elif not author_match and rtdl_match:
        classification = "rtdl_matches_contract_author_diverges"
        decision = "preserve_generic_rtdl_do_not_copy_author_divergence"
    else:
        classification = "both_diverge_or_contract_unresolved"
        decision = "collect_pair_rows_or_contract_evidence"

    return {
        "case_id": case.get("case_id"),
        "classification": classification,
        "decision": decision,
        "author_matches_selected_generic_contract": author_match,
        "rtdl_matches_selected_generic_contract": rtdl_match,
        "author_result_count": case.get("author", {}).get("result_count")
        if isinstance(case.get("author"), dict)
        else None,
        "rtdl_count": case.get("rtdl_count"),
        "cpu_float32_count": case.get("cpu_oracle", {}).get("float32_overlap_count")
        if isinstance(case.get("cpu_oracle"), dict)
        else None,
        "sample_geometry_count": case.get("sample_geometry_count"),
        "sample_query_count": case.get("sample_query_count"),
        "scope": "same_source_prefix_only",
    }


def load_cases(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"no cases in diagnostic artifact: {path}")
    return [case for case in cases if isinstance(case, dict)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostic", type=Path, action="append", required=True)
    parser.add_argument("--capacity", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases: list[dict[str, object]] = []
    sources: list[str] = []
    for path in [*args.diagnostic, *args.capacity]:
        cases.extend(load_cases(path))
        sources.append(str(path))
    classifications = [classify_case(case) for case in cases]
    payload = {
        "schema": SCHEMA,
        "status": "author_validity_gate_completed",
        "policy": {
            "selected_generic_contract": "inclusive_aabb_intersects_float32",
            "independent_oracle": "Goal5501 CPU float32 AABB overlap count",
            "author_wrong_is_not_inferred_from_count_difference": True,
            "rtdl_must_match_oracle_before_author_reproduction_claim": True,
            "author_divergence_does_not_justify_author_specific_core_behavior": True,
            "full_input_adjudication": False,
        },
        "source_artifacts": sources,
        "case_count": len(classifications),
        "classifications": classifications,
        "summary": {
            "both_match_count": sum(
                c["classification"]
                == "author_and_rtdl_match_selected_generic_contract"
                for c in classifications
            ),
            "author_matches_rtdl_diverges_count": sum(
                c["classification"] == "author_matches_contract_rtdl_diverges"
                for c in classifications
            ),
            "rtdl_matches_author_diverges_count": sum(
                c["classification"] == "rtdl_matches_contract_author_diverges"
                for c in classifications
            ),
            "unresolved_count": sum(
                c["classification"]
                in {
                    "both_diverge_or_contract_unresolved",
                    "unresolved_missing_oracle_evidence",
                }
                for c in classifications
            ),
        },
        "claim_boundary": {
            "author_validity_proven_for_full_inputs": False,
            "rtdl_full_input_fix_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "full_range_intersects_matrix_claimed": False,
            "performance_ratio_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
