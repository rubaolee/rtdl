#!/usr/bin/env python3
"""Fail-closed validation of dedicated Goal5819 claim artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
RECONSTRUCTION = HISTORY / "goal5819_frozen_performance_reconstruction_20260829.json"
CLAIM = HISTORY / "goal5819_frozen_contribution_sentence.json"
AMENDMENT = HISTORY / "goal5819_frozen_contribution_sentence_amendment_a1_20260829.json"
REPORT = HISTORY / "goal5819_prepare_phase_composition_20260829.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    reconstruction = read_json(RECONSTRUCTION)
    claim = read_json(CLAIM)
    amendment = read_json(AMENDMENT)
    report = REPORT.read_text(encoding="utf-8")

    require(reconstruction["status"] ==
            "PASS__RAW_RECEIPTS_AND_EXACT_SOURCES_RECONSTRUCTED",
            "reconstruction is not PASS")
    require(reconstruction["verification"] == {
        "published_absolute_cells_exact": True,
        "published_registered_rows_and_intervals_exact": True,
        "published_direct_phase_medians_exact": True,
        "experiment_rerun_count": 0,
        "experiment_source_change_count": 0,
    }, "reconstruction verification block differs")
    cells = reconstruction["absolute_medians_and_rtdl_minus_pyoptix"]
    setup = sorted(float(row["rtdl_minus_pyoptix_ms"])
                   for row in cells
                   if row["regime"] in ("DEPLOYMENT_COLD", "PREPARE"))
    require(setup == [162.431243, 176.4883275, 218.805672, 222.5023545],
            "setup deltas differ")
    require(claim["status"] ==
            "FROZEN__GOAL5818_BRANCH_A_SELECTED_FROM_OUTCOME_KNOWN_ROUTING",
            "frozen native branch status differs")
    require(claim["selection"]["selected_branch"] == "A",
            "Goal5818-selected Branch A differs")
    authority = claim["selection"]["selection_authority"]
    require(authority["controlling_raw_result_sha256"] ==
            "8699fff641d5ef998b31507360fb05ba3b704873af13df1862bd11dad59b9fe7",
            "Goal5818 controlling raw result differs")
    require(authority["native_collision_count"] == 0 and
            authority["surviving_residual_count"] == 5 and
            authority["new_goal5818_gpu_run_count"] == 0,
            "Goal5818 Branch A counts differ")
    require([row["id"] for row in claim["native_residual_branches"]]
            == ["A", "B", "C", "D"], "branch order/coverage differs")
    selected_native = claim["selected_native_residual_sentence"]
    require(selected_native == claim["native_residual_branches"][0]["claim_template"],
            "selected Branch A wording differs from frozen template")
    require("outcome was already known" in
            claim["selection"]["outcome_known_routing_disclosure"],
            "outcome-known routing disclosure absent")
    require(amendment["status"] ==
            "CONTROLLING__PERFORMANCE_SENTENCE_NARROWED_AFTER_HOSTILE_REVIEW",
            "performance amendment is not controlling")
    require(amendment["predecessor"]["sha256"] ==
            "1f3b0bb1ecbbddd5840ad8e3fbd69b7ebe1d7a5bb65adb7c175dd904981811fb",
            "performance amendment predecessor differs")
    require(amendment["reason"]["triangle_steady_ci95"] ==
            [1.0132221860286061, 1.0264549810163792],
            "triangle steady CI differs")
    require(amendment["reason"]["both_tasks_pass_registered_noninferiority_gate"] is True,
            "steady noninferiority conclusion differs")
    require(amendment["reason"]["equality_or_zero_cost_supported"] is False,
            "zero/equality ceiling differs")
    require(amendment["native_residual_authority_amendment"] == {
        "path": "history/internal_docs/goal5818_amendment_a1_optix9_header_authority_20260829.json",
        "sha256": "1c0e87babc3bb343bd1cb1ebb7a255572eff61d23eb777e4f66b3bb22c0287d7",
        "reason": "Supersedes the predecessor's mis-versioned OptiX header scan; the executed Branch A result is unchanged.",
    }, "native residual header-authority amendment differs")
    sentence = amendment["controlling_performance_sentence"]
    require("two matched tasks" in sentence and
            "single NVIDIA RTX 4000 Ada Generation" in sentence and
            "162–223 ms" in sentence and
            "registered 1.05 noninferiority gate" in sentence and
            "−0.017020 ms" in sentence and "+0.001220 ms" in sentence,
            "controlling performance sentence lost required scope/result")
    required_forbidden = {
        "admission cost", "checking cost", "zero overhead",
        "no performance penalty", "performance-neutral",
    }
    require(required_forbidden.issubset(set(claim["forbidden_expansions"])),
            "required forbidden expansion absent")
    lowered_sentence = sentence.lower()
    combined_forbidden = set(claim["forbidden_expansions"]) | set(amendment["forbidden_interpretations"])
    require(not any(term in lowered_sentence for term in combined_forbidden),
            "controlling sentence contains forbidden expansion")
    require(claim["semantic_scan_required"] is True,
            "semantic scan is not mandatory")
    require("does **not** invoke NVRTC" in report,
            "Direct no-NVRTC finding absent")
    require("do not isolate" in report,
            "causal ceiling absent")
    print(json.dumps({
        "schema": "rtdl.goal5819.claim_artifact_validation.v1",
        "status": "PASS",
        "validated_paths": [
            str(RECONSTRUCTION.relative_to(ROOT)).replace("\\", "/"),
            str(CLAIM.relative_to(ROOT)).replace("\\", "/"),
            str(AMENDMENT.relative_to(ROOT)).replace("\\", "/"),
            str(REPORT.relative_to(ROOT)).replace("\\", "/"),
        ],
        "native_branch_selected": "A",
        "setup_deltas_ms": setup,
        "semantic_scan_required": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
