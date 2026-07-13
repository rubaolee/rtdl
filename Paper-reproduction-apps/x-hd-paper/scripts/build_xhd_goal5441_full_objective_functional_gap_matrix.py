#!/usr/bin/env python3
"""Build the Goal5441 X-HD full-objective functional gap matrix.

This matrix maps the user's full objective ("same functionality as the author
C++/CUDA/OptiX implementation, comprehensive performance evaluation, same user
experience except language") against current evidence.

It does not run POD, run author code, run RTDL routes, or upgrade claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
HISTORY = ROOT / "history" / "internal_docs"
OUT = RESULTS / "xhd_goal5441_full_objective_functional_gap_matrix.json"


SOURCES = {
    "readiness": RESULTS / "xhd_goal5436_full_reproduction_readiness_matrix.json",
    "level_b_matrix": RESULTS / "xhd_goal5428_level_b_matrix_with_water_bg_full_public.json",
    "coverage_gap": RESULTS / "xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json",
    "figure5_denominator": RESULTS / "xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json",
    "figure7": RESULTS / "xhd_goal5292_figure7_load_balance_audit_2026-07-09.json",
    "figure8": RESULTS / "xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json",
    "figure9": RESULTS / "xhd_goal5287_figure9_disposition_2026-07-09.json",
    "figure10": RESULTS / "xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json",
    "figure11": RESULTS / "xhd_goal5283_figure11_disposition_2026-07-09.json",
    "external_chain": RESULTS / "xhd_goal5440_external_evidence_chain_review_packet.json",
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def _load_sources() -> dict[str, dict[str, Any]]:
    return {name: _load_json(path) for name, path in SOURCES.items()}


def _row(
    requirement: str,
    current_status: str,
    achieved: bool,
    evidence: list[str],
    gap: str,
    next_gate: str,
) -> dict[str, Any]:
    return {
        "requirement": requirement,
        "current_status": current_status,
        "achieved": achieved,
        "evidence": evidence,
        "gap": gap,
        "next_gate": next_gate,
    }


def build_payload() -> dict[str, Any]:
    data = _load_sources()
    readiness = data["readiness"]
    level_b = data["level_b_matrix"]
    coverage = data["coverage_gap"]
    fig5 = data["figure5_denominator"]
    fig7 = data["figure7"]
    fig8 = data["figure8"]
    fig9 = data["figure9"]
    fig10 = data["figure10"]
    fig11 = data["figure11"]
    external = data["external_chain"]

    rows = [
        _row(
            "Same directed Hausdorff scalar value on bounded / representative inputs",
            "substantially achieved for current Level-B matrix",
            bool(level_b.get("matched") is True),
            [_rel(SOURCES["level_b_matrix"])],
            "Level-B scalar correctness is not exact paper input reproduction.",
            "Keep as Level-B evidence; do not promote without exact/accepted input evidence.",
        ),
        _row(
            "Exact paper input identity across paper workloads",
            "not achieved",
            False,
            [_rel(SOURCES["readiness"]), _rel(SOURCES["external_chain"])],
            "Missing author input files/hashes, byte-identical regeneration proof, inspectable ACM artifact, or accepted exact-equivalence decision.",
            "Send selected external requests, record receipts, classify any response, then open a strict next gate.",
        ),
        _row(
            "Same visible CLI/user entrypoint behavior",
            "partial",
            False,
            [_rel(SOURCES["coverage_gap"])],
            "RTDL has hd_exec-compatible wrappers for several Level-B cases, but not full paper dataset/figure coverage.",
            "After exact/accepted inputs, run same-input author/RTDL gates through the app entrypoint.",
        ),
        _row(
            "Per-source exact witness output when requested",
            "partial",
            False,
            [_rel(SOURCES["level_b_matrix"]), _rel(SOURCES["coverage_gap"])],
            "Exact-witness routes preserve witnesses; fast-scalar early-break routes may have approximate per-source witnesses and can only claim scalar max-nearest correctness.",
            "Keep exact-witness and fast-scalar claims separate in every matrix.",
        ),
        _row(
            "Author RT-core algorithm equivalence",
            "not claimed",
            False,
            [_rel(SOURCES["readiness"]), _rel(SOURCES["coverage_gap"])],
            "Current RTDL route uses generic exact/reference and generic cell-MBR/partner machinery, not a proof of author RT-core internal algorithm equivalence.",
            "Only claim algorithm equivalence after a separately reviewed phase/counter/behavior mapping.",
        ),
        _row(
            "Figure 5 full performance matrix",
            "not reproduced",
            False,
            [_rel(SOURCES["figure5_denominator"]), _rel(SOURCES["level_b_matrix"])],
            "Figure 5 author logs exist, but exact inputs, BraTS/full geo RTDL gates, and same-denominator timing are missing.",
            "Acquire exact/accepted inputs and build same-denominator matrix before any ratio.",
        ),
        _row(
            "Figure 6 pruning effectiveness",
            "not reproduced",
            False,
            [_rel(SOURCES["coverage_gap"])],
            "Phase/counter mapping for pruning variants and exact/accepted inputs are insufficient for a paper claim.",
            "Do not prioritize unless exact input state changes or a reviewed phase-mapping goal is opened.",
        ),
        _row(
            "Figure 7 load-balance / heavy-cell offload",
            "not reproduced; current implementation-artifact line stopped",
            False,
            [_rel(SOURCES["figure7"])],
            "Checked-in lb_comparison logs are absent; run_all has LB=256 only; explicit row-identity parity line is fail-closed.",
            "Reopen only with author lb=0/lb=256 matrix or external review, plus G-1 stop-loss gate.",
        ),
        _row(
            "Figure 8 radius-growing strategy",
            "not reproduced",
            False,
            [_rel(SOURCES["figure8"])],
            "Author scripts exist but checked-in tune_radius numeric logs are absent.",
            "Do not start RTDL comparison until an author add/double/adaptive numeric matrix exists.",
        ),
        _row(
            "Figure 9 adaptive grid sizing",
            "closed: author denominator missing",
            False,
            [_rel(SOURCES["figure9"])],
            "Plot expects four variants but current logs provide two; checked-in PDF is not a reproducible denominator.",
            "Reopen only with missing variants or externally reviewed mapping.",
        ),
        _row(
            "Figure 10 scalability / overlap sensitivity",
            "not reproduced",
            False,
            [_rel(SOURCES["figure10"])],
            "Checked-in scalability logs are absent and run_all lacks scale/overlap labels.",
            "Do not start RTDL comparison until author scalability matrix exists.",
        ),
        _row(
            "Figure 11 memory footprint",
            "closed: denominator not aligned",
            False,
            [_rel(SOURCES["figure11"])],
            "RTDL queue-byte accounting does not match author WL / WL Heavy Peak denominator, and exact inputs are unavailable.",
            "Reopen only with denominator-aligned generic native worklist or external review accepting a different memory question.",
        ),
        _row(
            "Comprehensive performance evaluation",
            "not achieved",
            False,
            [_rel(SOURCES["figure5_denominator"]), _rel(SOURCES["readiness"])],
            "No full paper exact-input matrix and no same-denominator author/RTDL performance ratio are authorized.",
            "After exact/accepted inputs, run author internal time, author process wall, RTDL route wall, RTDL process wall, load time, and cold/warm labels side-by-side.",
        ),
        _row(
            "Same user experience except language",
            "not achieved",
            False,
            [_rel(SOURCES["readiness"]), _rel(SOURCES["external_chain"])],
            "The user-facing app cannot yet be honestly described as equivalent because exact input coverage, figure coverage, and performance denominators remain incomplete.",
            "Treat as final acceptance only after exact/full functional and performance gates pass.",
        ),
    ]

    achieved_count = sum(1 for row in rows if row["achieved"])
    partial_count = sum(1 for row in rows if row["current_status"] == "partial")
    not_achieved_count = len(rows) - achieved_count

    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5441.full_objective_functional_gap_matrix.v1",
        "goal": "Goal5441",
        "date": "2026-07-10",
        "status": "full_objective_functional_gap_matrix_ready__full_objective_incomplete",
        "objective": "Python/RTDL/partner X-HD implementation should match author C++/CUDA/OptiX functionality and provide comprehensive performance evaluation; user experience should differ only by language.",
        "summary": {
            "requirement_count": len(rows),
            "achieved_count": achieved_count,
            "partial_count": partial_count,
            "not_achieved_count": not_achieved_count,
            "full_objective_complete": False,
            "current_strongest_success": "Level-B scalar HDResult correctness across 6 cases / 9 route results.",
            "current_primary_blocker": "exact input artifacts or accepted exact-equivalence evidence",
            "current_secondary_blockers": [
                "full figure coverage",
                "author RT-core algorithm/phase equivalence",
                "same-denominator performance matrix",
                "exact-vs-fast-scalar witness claim separation",
            ],
        },
        "requirements": rows,
        "source_artifacts": {name: _rel(path) for name, path in SOURCES.items()},
        "external_state": {
            "ready_external_request_count": external.get("summary", {}).get("ready_external_request_count"),
            "sent_receipt_count": external.get("summary", {}).get("sent_receipt_count"),
            "external_response_count": external.get("summary", {}).get("external_response_count"),
            "planned_gate_count": external.get("summary", {}).get("planned_gate_count"),
            "pod_expected_next": external.get("summary", {}).get("pod_expected_next"),
        },
        "next_action": "external_evidence_chain_review_then_owner_send_selected_requests_or_record_responses",
        "claim_boundary": {
            "functional_gap_matrix_claimed": True,
            "bounded_level_b_scalar_evidence_claimed": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "figure6_reproduction_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure8_reproduction_claimed": False,
            "figure9_reproduction_claimed": False,
            "figure10_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "full-objective functional gap matrix / release-governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: objective audit/governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming full X-HD paper reproduction from Level-B scalar evidence",
            "claiming user-experience equivalence before exact/full function and performance gates",
            "claiming any Figure 5-11 reproduction from this matrix",
            "claiming author-vs-RTDL performance ratio",
            "claiming author RT-core algorithm equivalence",
            "running POD or route work from this matrix",
            "reopening explicit -lb or route micro-optimization while exact input evidence is absent",
        ],
    }
    return payload


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "requirement_count": payload["summary"]["requirement_count"],
                "achieved_count": payload["summary"]["achieved_count"],
                "full_objective_complete": payload["summary"]["full_objective_complete"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
