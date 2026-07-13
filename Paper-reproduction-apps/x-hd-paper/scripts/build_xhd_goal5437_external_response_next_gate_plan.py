#!/usr/bin/env python3
"""Build the Goal5437 next-gate plan from Goal5435 inbox output.

The plan translates classified external response outcomes into explicit
follow-up gate labels. It does not run the gates. This keeps a positive author,
ACM, or reviewer response from being used as an informal permission slip.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"

INBOX = RESULTS / "xhd_goal5435_external_response_inbox_gate.json"
READINESS = RESULTS / "xhd_goal5436_full_reproduction_readiness_matrix.json"
OUT = RESULTS / "xhd_goal5437_external_response_next_gate_plan.json"


NEXT_GATE_BY_CLASSIFICATION: dict[str, dict[str, Any]] = {
    "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim": {
        "gate_label": "same_input_author_rtdl_gate_on_current_public_wkt_hash_matched",
        "requires_pod": True,
        "requires_strict_review_before_execution": True,
        "allowed_claim_after_gate_passes": "same-input value/witness gate on hash-matched current public WKT; exact wording still requires review",
        "forbidden_direct_claims": [
            "exact paper dataset reproduction",
            "Figure 5 reproduction",
            "full X-HD paper reproduction",
            "author-vs-RTDL performance ratio",
        ],
    },
    "author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate": {
        "gate_label": "extract_author_archive_hash_then_same_input_gate",
        "requires_pod": True,
        "requires_strict_review_before_execution": True,
        "allowed_claim_after_gate_passes": "same-input gate on extracted author-provided files; exact wording depends on archive provenance review",
        "forbidden_direct_claims": [
            "exact paper dataset reproduction before archive/hash review",
            "Figure 5 reproduction before denominator-aligned matrix",
            "full X-HD paper reproduction",
            "performance ratio",
        ],
    },
    "byte_identical_regeneration_available__run_regeneration_then_hash_gate": {
        "gate_label": "run_regeneration_hash_gate_then_same_input_gate",
        "requires_pod": True,
        "requires_strict_review_before_execution": True,
        "allowed_claim_after_gate_passes": "byte-identical regeneration candidate if hashes match and same-input gate passes",
        "forbidden_direct_claims": [
            "exact paper dataset reproduction before regenerated hashes match",
            "full X-HD paper reproduction before functional/performance gates",
            "performance ratio",
        ],
    },
    "acm_supplement_contains_possible_provenance__map_before_route": {
        "gate_label": "map_acm_supplement_artifacts_to_workloads_before_any_route",
        "requires_pod": False,
        "requires_strict_review_before_execution": True,
        "allowed_claim_after_gate_passes": "artifact/workload mapping readiness only",
        "forbidden_direct_claims": [
            "same-input correctness",
            "exact paper dataset reproduction",
            "Figure 5 reproduction",
            "full X-HD paper reproduction",
            "performance ratio",
        ],
    },
    "exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix": {
        "gate_label": "bounded_public_reconstruction_accepted_claim_matrix",
        "requires_pod": True,
        "requires_strict_review_before_execution": True,
        "allowed_claim_after_gate_passes": "externally accepted bounded public-reconstruction matrix using the accepted claim name",
        "forbidden_direct_claims": [
            "byte-identical exact input",
            "unqualified exact paper dataset reproduction",
            "full X-HD paper reproduction",
            "performance ratio unless denominator-aligned",
        ],
    },
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def build_plan(inbox_path: Path = INBOX, readiness_path: Path = READINESS) -> dict[str, Any]:
    inbox = _load(inbox_path)
    readiness = _load(readiness_path)
    classified = inbox.get("classified_responses", [])
    if not isinstance(classified, list):
        classified = []

    planned_gates: list[dict[str, Any]] = []
    fail_closed_responses: list[dict[str, Any]] = []

    for row in classified:
        classification = row.get("classification")
        if classification in NEXT_GATE_BY_CLASSIFICATION:
            plan = dict(NEXT_GATE_BY_CLASSIFICATION[classification])
            plan.update(
                {
                    "source_response_path": row.get("path"),
                    "source_classification": classification,
                    "classifier_recommended_next_action": row.get("recommended_next_action"),
                    "execution_status": "not_executed__requires_strict_review",
                }
            )
            planned_gates.append(plan)
        else:
            fail_closed_responses.append(
                {
                    "source_response_path": row.get("path"),
                    "source_classification": classification,
                    "classifier_recommended_next_action": row.get("recommended_next_action"),
                    "status": "fail_closed_or_manual_review_keep_level_b",
                }
            )

    if planned_gates:
        status = "external_response_next_gate_plan_ready__strict_review_required_before_execution"
        next_action = "strictly_review_planned_gates_then_execute_at_most_one_separate_gate"
    elif int(inbox.get("response_count", 0)) == 0:
        status = "external_response_next_gate_plan_empty__await_response"
        next_action = "wait_for_external_response_or_send_owner_reviewed_action_packet"
    else:
        status = "external_response_next_gate_plan_all_fail_closed__keep_level_b"
        next_action = "record_fail_closed_responses_and_keep_level_b"

    pod_expected = any(bool(row["requires_pod"]) for row in planned_gates)

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5437.external_response_next_gate_plan.v1",
        "goal": "Goal5437",
        "date": "2026-07-10",
        "status": status,
        "inbox_status": inbox.get("status"),
        "readiness_status": readiness.get("status"),
        "response_count": int(inbox.get("response_count", 0)),
        "planned_gate_count": len(planned_gates),
        "fail_closed_response_count": len(fail_closed_responses),
        "planned_gates": planned_gates,
        "fail_closed_responses": fail_closed_responses,
        "next_action": next_action,
        "pod_usage": {
            "used": False,
            "expected_next": pod_expected,
            "reason": "POD is expected only for a planned gate after strict review; this planner never runs POD.",
        },
        "claim_boundary": {
            "next_gate_plan_claimed": True,
            "planned_gate_executed": False,
            "request_sent_claimed": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external response next-gate planner / provenance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: next-gate governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "executing planned gates inside the planner",
            "running POD before strict review of a planned gate",
            "claiming exact/full reproduction from a planned gate label",
            "claiming exact-equivalence accepted before the accepted-matrix gate passes",
            "claiming author-vs-RTDL performance ratio from a next-gate plan",
            "reopening explicit -lb or route micro-optimization work from a next-gate plan",
        ],
        "source_artifacts": {
            "goal5435": _rel(inbox_path),
            "goal5436": _rel(readiness_path),
        },
    }


def main() -> int:
    payload = build_plan()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "planned_gate_count": payload["planned_gate_count"],
                "pod_expected_next": payload["pod_usage"]["expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
