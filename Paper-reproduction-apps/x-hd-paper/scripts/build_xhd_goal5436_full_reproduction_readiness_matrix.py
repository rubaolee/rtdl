#!/usr/bin/env python3
"""Build the Goal5436 X-HD full-reproduction readiness matrix.

This is a status/governance artifact for the active objective:
Python/RTDL/partner should eventually reproduce the author C++/CUDA/OptiX X-HD
implementation at the same functional level and with a fair performance
matrix.

The matrix deliberately separates:
  - current Level-B representative scalar evidence,
  - exact input / exact-equivalence readiness,
  - functional completeness,
  - denominator-aligned performance readiness,
  - POD readiness.

It does not run POD, author code, RTDL routes, or external requests.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"

GOAL5428 = RESULTS / "xhd_goal5428_level_b_matrix_with_water_bg_full_public.json"
GOAL5429 = RESULTS / "xhd_goal5429_exact_input_or_equivalence_decision_refresh.json"
GOAL5434 = RESULTS / "xhd_goal5434_water_bg_external_action_packet.json"
GOAL5435 = RESULTS / "xhd_goal5435_external_response_inbox_gate.json"
GOAL5345 = RESULTS / "xhd_goal5345_exact_reproduction_readiness.json"
OUT = RESULTS / "xhd_goal5436_full_reproduction_readiness_matrix.json"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    level_b = _load(GOAL5428)
    exact_decision = _load(GOAL5429)
    action_packet = _load(GOAL5434)
    inbox = _load(GOAL5435)
    pod_readiness = _load(GOAL5345)

    coverage = level_b["coverage"]
    exact_blocker = exact_decision["full_reproduction_decision"]["full_reproduction_next_blocker"]
    response_count = int(inbox["response_count"])
    positive_count = int(inbox["positive_classifier_outcome_count"])
    pod_allowed = bool(pod_readiness["pod_execution_allowed_now"]) or bool(inbox["pod_usage"]["expected_next"])

    exact_or_equivalence_ready = (
        bool(action_packet["claim_boundary"].get("external_artifacts_acquired"))
        or bool(action_packet["claim_boundary"].get("exact_equivalence_accepted"))
        or positive_count > 0
    )

    requirements = {
        "level_b_representative_scalar_evidence": {
            "satisfied": bool(level_b["matched"]) and int(coverage["total_case_count"]) >= 1,
            "evidence": _rel(GOAL5428),
            "scope": "6 Level-B cases / 9 route results; scalar correctness only, not exact paper input.",
        },
        "exact_inputs_or_accepted_exact_equivalence": {
            "satisfied": exact_or_equivalence_ready,
            "evidence": [_rel(GOAL5429), _rel(GOAL5435)],
            "missing": [
                "author input files or hashes",
                "byte-identical regeneration proof",
                "inspectable ACM supplement contents with relevant inputs",
                "explicit external exact-equivalence acceptance",
            ],
        },
        "same_input_author_rtdl_gate_on_exact_or_accepted_inputs": {
            "satisfied": False,
            "evidence": _rel(GOAL5345),
            "reason": "No exact/accepted input artifact is command-ready; POD same-input gate is not open.",
        },
        "full_functional_parity_with_author_visible_behavior": {
            "satisfied": False,
            "evidence": _rel(GOAL5429),
            "reason": (
                "Current evidence is scalar Level-B correctness. Full paper figures, exact input identity, "
                "and author RT-core algorithm equivalence remain unclaimed."
            ),
        },
        "denominator_aligned_performance_matrix": {
            "satisfied": False,
            "evidence": _rel(GOAL5428),
            "reason": "Author internal AvgTime/process wall and RTDL route/total remain separate denominators.",
        },
        "pod_execution_ready_for_next_gate": {
            "satisfied": pod_allowed,
            "evidence": [_rel(GOAL5435), _rel(GOAL5345)],
            "reason": "POD is expected only after a positive classifier outcome or command-ready exact artifact packet.",
        },
    }

    complete = all(row["satisfied"] for row in requirements.values())
    if complete:
        status = "full_xhd_reproduction_ready_for_completion_audit"
        next_action = "run completion audit and external review before claiming full reproduction"
    elif positive_count > 0:
        status = "full_xhd_reproduction_not_ready__positive_response_requires_strict_review"
        next_action = "strictly_review_classifier_output_then_open_separate_next_gate_if_approved"
    elif response_count == 0:
        status = "full_xhd_reproduction_not_ready__await_external_response_or_artifact"
        next_action = "send_or_review_action_packet_and_wait_for_classified_external_response"
    else:
        status = "full_xhd_reproduction_not_ready__responses_fail_closed_keep_level_b"
        next_action = "record response outcome and keep Level-B until stronger evidence arrives"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5436.full_reproduction_readiness_matrix.v1",
        "goal": "Goal5436",
        "date": "2026-07-10",
        "status": status,
        "full_xhd_paper_reproduction_ready": complete,
        "requirements": requirements,
        "current_level_b_summary": {
            "matched": bool(level_b["matched"]),
            "case_count": int(coverage["total_case_count"]),
            "route_result_count": int(coverage["total_route_result_count"]),
            "graphics_case_count": int(coverage["graphics_case_count"]),
            "bounded_geo_case_count": int(coverage["bounded_geo_case_count"]),
            "full_public_geo_case_count": int(coverage["full_public_geo_case_count"]),
            "strongest_exact_equivalence_candidate": exact_decision["current_best_exact_equivalence_candidate"]["row_id"],
            "strongest_candidate_evidence_level": exact_decision["current_best_exact_equivalence_candidate"]["evidence_level"],
        },
        "current_blocker": {
            "kind": exact_blocker,
            "route_micro_optimization_is_next": bool(
                exact_decision["full_reproduction_decision"]["more_route_performance_work_is_next"]
            ),
            "route_micro_optimization_authorized": bool(
                exact_decision["full_reproduction_decision"]["route_micro_optimization_authorized"]
            ),
            "explicit_lb_authorized": bool(exact_decision["full_reproduction_decision"]["explicit_lb_authorized"]),
        },
        "external_state": {
            "action_packet_status": action_packet["status"],
            "inbox_status": inbox["status"],
            "response_count": response_count,
            "positive_classifier_outcome_count": positive_count,
            "pod_execution_allowed_now": pod_allowed,
            "exact_reproduction_pod_readiness": pod_readiness["classification"],
        },
        "next_action": next_action,
        "claim_boundary": {
            "readiness_matrix_claimed": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "pod_usage": {
            "used": False,
            "expected_next": pod_allowed,
            "reason": "POD remains gated by exact/accepted input evidence and strict review of classifier output.",
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "full-reproduction readiness matrix / external-response governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: readiness governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming full X-HD paper reproduction from Level-B scalar evidence",
            "claiming exact paper dataset reproduction without file/hash, regeneration, artifact, or accepted exact-equivalence evidence",
            "claiming Figure 5 reproduction from the Level-B matrix",
            "claiming author-vs-RTDL performance ratio without denominator alignment",
            "reopening route micro-optimization as paper-reproduction progress",
            "reopening explicit -lb or row-identity work",
            "running POD before a positive classified response or command-ready exact artifact packet",
        ],
        "source_artifacts": {
            "goal5428": _rel(GOAL5428),
            "goal5429": _rel(GOAL5429),
            "goal5434": _rel(GOAL5434),
            "goal5435": _rel(GOAL5435),
            "goal5345": _rel(GOAL5345),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "full_xhd_paper_reproduction_ready": payload["full_xhd_paper_reproduction_ready"],
                "next_action": payload["next_action"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
