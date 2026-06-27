#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-23"
SCHEMA = "rtdl.phoenix_v3.m68.next_set_a_family_selection.v1"
STATUS_READY = "m68_next_set_a_family_selection_ready_for_external_review_no_pod_no_release"
STATUS_FAILED = "m68_next_set_a_family_selection_failed"

SCORECARD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json"
CLASSIFICATION = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_classification_2026-06-22.json"
M66_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md"
)
M67_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_3ai_consensus_2026-06-23.md"
)
M35_GAP_LEDGER = ROOT / "docs" / "reports" / "phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md"
M40_COMPONENT_UNION = ROOT / "docs" / "reports" / "phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md"
M43_GROUPED_REDUCTION = ROOT / "docs" / "reports" / "phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md"
M44_SCORECARD = ROOT / "docs" / "reports" / "phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md"
RTNN_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622"
    / "summary.json"
)
RTNN_REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_prepared_execution_runner_repeat50_pod_evidence_2026-06-22.md"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m68_next_set_a_family_selection_{DATE}.json"
OUT_MD = ROOT / "docs" / "reports" / f"phoenix_v3_m68_next_set_a_family_selection_{DATE}.md"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 M68 next generic Set-A family selection packet."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_payload() -> dict[str, Any]:
    scorecard = _read_json(SCORECARD)
    classification = _read_json(CLASSIFICATION)
    rtnn_evidence = _read_json(RTNN_EVIDENCE)
    prepared_source = PREPARED_EXECUTION.read_text(encoding="utf-8")
    m66 = M66_CONSENSUS.read_text(encoding="utf-8")
    m67 = M67_CONSENSUS.read_text(encoding="utf-8")
    m35 = M35_GAP_LEDGER.read_text(encoding="utf-8")
    m40 = M40_COMPONENT_UNION.read_text(encoding="utf-8")
    m43 = M43_GROUPED_REDUCTION.read_text(encoding="utf-8")
    m44 = M44_SCORECARD.read_text(encoding="utf-8")

    score = scorecard["scorecard"]
    app_geomeans = dict(score["set_a_app_geomeans_v3_vs_v2"])
    selected = _selected_rtnn(app_geomeans, rtnn_evidence, prepared_source)
    candidates = _candidate_table(app_geomeans)
    next_work = {
        "goal_id": "M69",
        "work_item": "local_rtnn_ranked_summary_phase_shape_bridge_audit",
        "scope": (
            "No-POD local audit mapping the existing fixed-radius ranked-summary "
            "prepared-session runner evidence to the frozen RTNN all-app shapes."
        ),
        "must_answer": [
            "Which all-app RTNN rows remain below the 1.05x Set-A app-win threshold?",
            "Do those rows share the generic fixed_radius_ranked_summary_3d prepared-session surface?",
            "Is the repeat50 material signal broad enough to justify a later focused runbook?",
            "Which phase is actually compressible: prepare, input packing, ranked-summary aggregate, or runner process wall?",
            "How much of the runner-wall delta is input-loading/packing consolidation rather than ranked-summary execution compression?",
            "Does the next change belong in a generic ranked-summary runner/phase bridge rather than app code?",
        ],
        "stop_conditions": [
            "If the only positive signal is repeat50 amortization with no all-app shape bridge, stop.",
            "If runner-wall improvement is attributable entirely to input-loading/packing consolidation with no ranked-summary phase compression, stop before any runbook.",
            "If the route requires app-specific RTNN shortcuts, stop.",
            "If source inspection shows no current productized ranked-summary helper, stop.",
            "If M69 cannot define same-contract focused evidence before POD, stop.",
        ],
        "pod_authorized": False,
        "all_app_authorized": False,
    }
    non_authorization = {
        "release_authorized": False,
        "pod_authorized": False,
        "all_app_run_authorized": False,
        "paid_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_over_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "route_specific_rtnn_app_tuning_authorized": False,
        "watch_row_closure_authorized": False,
    }
    checks = {
        "scorecard_blocks_release": scorecard["release_authorized"] is False
        and scorecard["release_candidate_under_two_number_bar"] is False,
        "scorecard_blocks_all_app_pod_spend": scorecard["all_app_pod_spend_authorized"] is False,
        "classification_frozen": classification["classification_frozen_before_next_full_paired_run"] is True,
        "m66_blocks_repeat_topology_stream_pod": (
            "rejected" in m66.lower() and "No POD" in m66
        ),
        "m67_accepts_barnes_hut_as_existing_material_family": (
            "accept_m67_count_barnes_hut_as_existing_step1_material_family_no_pod_no_release"
            in m67
        ),
        "m35_blocks_rtdbscan_and_rayjoin_as_immediate_material_targets": (
            "RTDBSCAN component signature | Structural ready, not material" in m35
            and "RayJoin point-location topology stream | Structural ready, not material" in m35
        ),
        "m40_component_union_already_has_focused_probe": (
            "Productized runner vs Embree, hot query" in m40
            and "1.221027x" in m40
            and "component_union_phase_accounting_visible" in m40
        ),
        "m43_grouped_reduction_already_closed_bounded_step2": (
            "3.454249350723889x" in m43
            and "bounded Step-2 technical closure" in m44
            and "15.409128x" in m44
        ),
        "selected_family_is_set_a": classification["app_classification"]["rtnn"]["set"] == "A",
        "selected_family_below_app_win_threshold": app_geomeans["rtnn"] < 1.05,
        "selected_family_not_severe_regression": app_geomeans["rtnn"] >= 0.90,
        "selected_has_productized_helper": selected["source_surface"]["helper_present"],
        "selected_helper_has_generic_contract": selected["source_surface"]["helper_generic_contract_present"],
        "selected_evidence_runtime_trunk_executes": selected["evidence"]["runtime_trunk_executes_end_to_end"] is True,
        "selected_evidence_internal_residency": selected["evidence"]["internal_device_residency_between_rtdl_phases"] is True,
        "selected_evidence_repeat50_wall_material_signal": selected["evidence"][
            "runner_vs_legacy_runner_wall_speedup"
        ]
        >= 1.20,
        "selected_evidence_hot_query_boundary_recorded": selected["evidence"]["runner_vs_legacy_hot_speedup"]
        < 1.0,
        "all_non_authorization_flags_false": all(value is False for value in non_authorization.values()),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = STATUS_FAILED if failed_checks else STATUS_READY
    return {
        "schema": SCHEMA,
        "date": DATE,
        "status": status,
        "inputs": {
            "scorecard": _rel(SCORECARD),
            "classification": _rel(CLASSIFICATION),
            "m66_consensus": _rel(M66_CONSENSUS),
            "m67_consensus": _rel(M67_CONSENSUS),
            "m35_gap_ledger": _rel(M35_GAP_LEDGER),
            "m40_component_union": _rel(M40_COMPONENT_UNION),
            "m43_grouped_reduction": _rel(M43_GROUPED_REDUCTION),
            "m44_scorecard": _rel(M44_SCORECARD),
            "rtnn_evidence": _rel(RTNN_EVIDENCE),
            "rtnn_report": _rel(RTNN_REPORT),
            "prepared_execution": _rel(PREPARED_EXECUTION),
        },
        "candidate_policy": {
            "selection_unit": "generic runtime family, not benchmark app ownership",
            "must_be_set_a": True,
            "must_not_repeat_recent_non_go": True,
            "must_have_or_require_productized_prepared_session_runner": True,
            "must_start_local_no_pod": True,
            "must_preserve_non_authorization": True,
        },
        "candidates": candidates,
        "selected_family": selected,
        "next_work": next_work,
        "checks": checks,
        "failed_checks": failed_checks,
        "summary": {
            "status": status,
            "failed_check_count": len(failed_checks),
            "selected_family_id": selected["family_id"],
            "selected_pressure_app": selected["pressure_app"],
            "selected_next_goal": next_work["goal_id"],
            "rtnn_set_a_app_geomean": app_geomeans["rtnn"],
            "rtnn_runner_vs_legacy_runner_wall_speedup": selected["evidence"][
                "runner_vs_legacy_runner_wall_speedup"
            ],
            "rtnn_runner_vs_legacy_hot_speedup": selected["evidence"]["runner_vs_legacy_hot_speedup"],
            "pod_authorized": False,
            "all_app_authorized": False,
            "release_authorized": False,
        },
        "non_authorization": non_authorization,
        "goal_level_decision_audit": {
            "decision": (
                "Select RTNN fixed-radius ranked-summary as the next generic Set-A "
                "family for local no-POD phase/shape bridge audit."
            ),
            "was_i_foolish": (
                "No. The decision explicitly rejects Barnes-Hut repetition, RayJoin "
                "rerun, LibRTS Set-B drift, and app-specific RTNN shortcuts."
            ),
            "foolish_actions": (
                "The foolish action would be to quote the repeat50 wall speedup as a "
                "broad RTNN or V3 claim, or to skip the all-app shape bridge."
            ),
            "other_path": (
                "Pick Triangle, RTDBSCAN, Hausdorff, or Spatial immediately. Those "
                "remain valid later, but each is either already accepted, recently "
                "non-go, already above the app-win threshold, or still tied to a "
                "known continuation bottleneck."
            ),
            "different_path_now": (
                "Use M69 to perform a local ranked-summary phase/shape bridge audit "
                "first, then seek review before any runbook or POD request."
            ),
        },
    }


def _selected_rtnn(
    app_geomeans: dict[str, float], rtnn_evidence: dict[str, Any], prepared_source: str
) -> dict[str, Any]:
    summary = rtnn_evidence["summary"]
    comparisons = summary["comparisons"]
    runner = summary["phase_rows"]["productized_prepared_execution_runner"]
    legacy = summary["phase_rows"]["legacy_app_front_door_prepared_optix"]
    legacy_input_load_pack_sec = float(legacy["input_load_sec"]) + float(legacy["input_pack_sec"])
    helper_name = "def run_fixed_radius_ranked_summary_3d_prepared_session"
    helper_present = helper_name in prepared_source
    helper_body = ""
    if helper_present:
        start = prepared_source.index(helper_name)
        end_marker = "def run_fixed_radius_count_threshold_3d_self_query_prepared_session"
        end = prepared_source.index(end_marker, start) if end_marker in prepared_source[start:] else len(prepared_source)
        helper_body = prepared_source[start:end]
    return {
        "family_id": "fixed_radius_ranked_summary_3d_prepared_session",
        "pressure_app": "rtnn",
        "selection_verdict": "select_for_m69_local_phase_shape_bridge_audit_no_pod_no_release",
        "why_selected": [
            "It is a frozen Set-A architecture-bearing app still below the 1.05x app-win threshold.",
            "It already has a productized prepared-session runner surface.",
            "Existing same-RT-hardware evidence shows a material runner-wall signal at repeat50.",
            "The hot-query boundary is explicit, so M69 can avoid overclaiming.",
            "The next step can be a local phase/shape bridge audit before any POD request.",
        ],
        "set_a_app_geomean_v3_vs_v2": app_geomeans["rtnn"],
        "scorecard_need": "turn an existing focused runner signal into an auditable bridge to frozen RTNN all-app shapes, or reject it as too narrow",
        "evidence": {
            "status": rtnn_evidence["status"],
            "point_count": summary["point_count"],
            "repeat": summary["repeat"],
            "runtime_trunk_executes_end_to_end": runner["runtime_trunk_executes_end_to_end"],
            "internal_device_residency_between_rtdl_phases": runner[
                "internal_device_residency_between_rtdl_phases"
            ],
            "runner_vs_legacy_hot_speedup": comparisons["runner_vs_legacy_hot_speedup"],
            "runner_vs_legacy_cold_plus_query_speedup": comparisons[
                "runner_vs_legacy_cold_plus_query_speedup"
            ],
            "runner_vs_legacy_runner_wall_speedup": comparisons["runner_vs_legacy_runner_wall_speedup"],
            "runner_input_load_pack_sec": runner["input_load_pack_sec"],
            "legacy_input_load_plus_pack_sec": legacy_input_load_pack_sec,
            "input_load_pack_consolidation_sec": legacy_input_load_pack_sec
            - float(runner["input_load_pack_sec"]),
            "runner_after_input_load_pack_sec": runner["runner_after_input_load_pack_sec"],
            "signature_match_runner_vs_legacy": summary["parity"]["runner_vs_legacy_signature_match"],
            "signature_match_runner_vs_cupy": summary["parity"]["runner_vs_cupy_signature_match"],
        },
        "source_surface": {
            "helper_present": helper_present,
            "helper_generic_contract_present": "generic_fixed_radius_ranked_summary_3d_aggregate"
            in helper_body,
            "runtime_trunk_family_present": "fixed_radius_ranked_summary_3d_prepared_query_aggregate"
            in helper_body,
            "continuation_contract_present": "fixed_radius_ranked_summary_aggregate_3d"
            in helper_body,
            "materialization_flag_present": "ranked_summary_rows_materialized_on_host" in helper_body,
            "helper_body_has_no_rtnn_name": "rtnn" not in helper_body.lower(),
        },
    }


def _candidate_table(app_geomeans: dict[str, float]) -> list[dict[str, Any]]:
    return [
        {
            "family": "barnes_hut_aggregate_tree_fused_vector_sum",
            "pressure_app": "barnes_hut",
            "set_a_app_geomean": app_geomeans["barnes_hut"],
            "rank": "excluded_currently",
            "reason": "M67 3-AI counted it internally as an existing material family and blocked more Barnes-Hut-specific work.",
        },
        {
            "family": "spatial_rayjoin_topology_stream",
            "pressure_app": "spatial_rayjoin",
            "set_a_app_geomean": app_geomeans["spatial_rayjoin"],
            "rank": "excluded_currently",
            "reason": "M66 rejected a repeat topology-stream run because the current route removes no new physical work.",
        },
        {
            "family": "fixed_radius_ranked_summary_3d_prepared_session",
            "pressure_app": "rtnn",
            "set_a_app_geomean": app_geomeans["rtnn"],
            "rank": "selected",
            "reason": "Generic ranked-summary surface exists, all-app app-win is still below target, and local bridge audit can test scope before POD.",
        },
        {
            "family": "triangle_prepared_graph_chunk_execution",
            "pressure_app": "triangle_counting",
            "set_a_app_geomean": app_geomeans["triangle_counting"],
            "rank": "reserve_candidate",
            "reason": "M19 already accepted a strict focused probe; useful if RTNN bridge fails, but not the cleanest next no-POD bridge.",
        },
        {
            "family": "rt_dbscan_component_union",
            "pressure_app": "rt_dbscan",
            "set_a_app_geomean": app_geomeans["rt_dbscan"],
            "rank": "reserve_candidate",
            "reason": "M40 gives component-union evidence, but M35 says the incumbent comparison is still bottlenecked by grouped-union work.",
        },
        {
            "family": "hausdorff_threshold_summary",
            "pressure_app": "hausdorff_xhd",
            "set_a_app_geomean": app_geomeans["hausdorff_xhd"],
            "rank": "defer",
            "reason": "Already the only Set-A app above 1.05x in the frozen scorecard; less urgent for the next app-win bridge.",
        },
    ]


def render_markdown(payload: dict[str, Any]) -> str:
    selected = payload["selected_family"]
    summary = payload["summary"]
    next_work = payload["next_work"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 M68 Next Set-A Family Selection",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Bottom Line",
        "",
        "M68 selects RTNN fixed-radius ranked-summary as the next generic Set-A",
        "family for local, no-POD phase/shape bridge audit. This is not a",
        "benchmark-app tuning decision. The selected mechanism is the generic",
        "`fixed_radius_ranked_summary_3d_prepared_session` runner surface.",
        "",
        "The reason is disciplined: Barnes-Hut is already counted internally by",
        "M67, Spatial/RayJoin is non-go under M66, LibRTS is Set-B control work,",
        "Hausdorff is already above the app-win threshold, and RTNN has both an",
        "existing productized runner and a frozen all-app app-win gap.",
        "",
        "## Selected Family",
        "",
        f"- Family: `{selected['family_id']}`",
        f"- Pressure app: `{selected['pressure_app']}`",
        f"- Verdict: `{selected['selection_verdict']}`",
        f"- Frozen Set-A app geomean: `{float(summary['rtnn_set_a_app_geomean']):.6f}x`",
        f"- Existing runner vs legacy runner-wall: `{float(summary['rtnn_runner_vs_legacy_runner_wall_speedup']):.6f}x`",
        f"- Existing runner vs legacy hot-query boundary: `{float(summary['rtnn_runner_vs_legacy_hot_speedup']):.6f}x`",
        f"- Input load/pack consolidation in existing evidence: `{float(selected['evidence']['input_load_pack_consolidation_sec']):.6f}s`",
        f"- Runner after input load/pack: `{float(selected['evidence']['runner_after_input_load_pack_sec']):.6f}s`",
        "",
        "The hot-query boundary is part of the selection. M69 must not turn the",
        "repeat50 wall signal into a single-shot or whole-RTNN claim. It must",
        "also separate input-packing/loading consolidation from ranked-summary",
        "execution compression before any later runbook is considered.",
        "",
        "## Candidate Table",
        "",
        "| Family | Pressure app | Rank | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for candidate in payload["candidates"]:
        lines.append(
            f"| `{candidate['family']}` | `{candidate['pressure_app']}` | `{candidate['rank']}` | {candidate['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Next Work",
            "",
            f"- Goal: `{next_work['goal_id']}`",
            f"- Work item: `{next_work['work_item']}`",
            f"- Scope: {next_work['scope']}",
            f"- POD authorized: `{str(next_work['pod_authorized']).lower()}`",
            f"- All-app authorized: `{str(next_work['all_app_authorized']).lower()}`",
            "",
            "M69 must answer:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in next_work["must_answer"])
    lines.extend(
        [
            "",
            "Stop conditions:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in next_work["stop_conditions"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    lines.extend(f"- `{name}`: `{str(ok).lower()}`" for name, ok in payload["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{len(payload['failed_checks'])}`",
            "",
            "## Non-Authorization",
            "",
            "This packet authorizes no release, no all-app run, no POD spend, no",
            "focused run, no public speedup wording, no broad V3-over-V2 claim, no",
            "whole-app or paper claim, no RT-core speedup claim, no automatic partner",
            "selection, no route-specific RTNN app tuning, and no watch-row closure.",
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path that actually solves the problem? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
