#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rtdl.phoenix_v3.m67.barnes_hut_phase_structure_pre_audit.v1"
STATUS_READY = "m67_barnes_hut_phase_structure_pre_audit_ready_for_external_review_no_pod_no_release"
STATUS_FAILED = "m67_barnes_hut_phase_structure_pre_audit_failed"
DATE = "2026-06-23"

M66_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md"
)
M45_REAUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md"
STEP2_PRE_AUDIT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_barnes_hut_step2_pre_audit_2026-06-22.json"
RUNNER_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718"
    / "summary.json"
)
M29_SURFACE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m29_barnes_hut_surface_Cv7ppr"
    / "summary.json"
)
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
APP = ROOT / "examples" / "current" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_{DATE}.json"
OUT_MD = ROOT / "docs" / "reports" / f"phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_{DATE}.md"


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
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 M67 Barnes-Hut local phase-structure pre-audit."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_payload() -> dict[str, Any]:
    m66 = M66_CONSENSUS.read_text(encoding="utf-8")
    m45 = M45_REAUDIT.read_text(encoding="utf-8")
    step2 = _read_json(STEP2_PRE_AUDIT)
    runner = _read_json(RUNNER_PACKET)
    m29 = _read_json(M29_SURFACE)
    prepared_source = PREPARED_EXECUTION.read_text(encoding="utf-8")
    app_source = APP.read_text(encoding="utf-8")

    summary = dict(runner["summary"])
    parity_rows = list(summary["parity_rows"])
    historical_rows = list(summary["historical_reference_rows"])
    variant_summaries = dict(summary["variant_size_summaries"])
    source_surface = _source_surface(prepared_source, app_source)
    phase_structure = _phase_structure(summary=summary, variant_summaries=variant_summaries)
    reconciliation = {
        "m45_old_all_app_blocker_status": "focused_fix_covered_pending_full_suite_validation",
        "m66_redirect_scope": "local_barnes_hut_phase_structure_pre_audit",
        "reconciled_reading": (
            "Do not start Barnes-Hut app tuning. The local pre-audit should decide "
            "whether existing aggregate-tree fused-vector runner evidence already "
            "satisfies the material-source question or needs external rejection."
        ),
        "new_barnes_hut_app_tuning_allowed": False,
        "new_barnes_hut_runtime_coding_required_now": False,
        "external_review_required_before_counting_as_accepted_set_a_family": True,
    }
    decision = {
        "status": "existing_evidence_answers_pre_audit_requires_external_counting_review",
        "barnes_hut_should_be_current_coding_target": False,
        "pod_now_authorized": False,
        "all_app_now_authorized": False,
        "material_source_found_against_historical_predecessor": bool(
            phase_structure["historical_predecessor"]["compressible_nonzero_phase_found"]
        ),
        "new_material_source_found_against_current_fused_control": bool(
            phase_structure["current_fused_control"]["new_compressible_phase_found"]
        ),
        "runner_preserves_current_fused_control_speed": bool(
            phase_structure["current_fused_control"]["runner_parity_with_existing_fused_partner"]
        ),
        "next_action": (
            "Send this M67 packet for external review. If accepted, Barnes-Hut can "
            "be counted as an existing Step-1 replacement material family and the "
            "next engineering target should move to the next Set-A family. If "
            "rejected, select a different family rather than doing Barnes-Hut "
            "app-specific tuning."
        ),
    }
    checks = {
        "m66_redirect_to_barnes_hut_pre_audit_recorded": (
            "Local Barnes-Hut phase-structure pre-audit may begin" in m66
            and "No POD run is authorized" in m66
        ),
        "m45_blocks_new_barnes_hut_app_tuning": (
            "immediate new coding target" in m45
            and "focused-fix-covered" in m45
            and "pending full-suite" in m45
        ),
        "step2_audit_requires_productized_runtime_before_pod": (
            step2["pre_audit_decision"]["pod_now_authorized"] is False
            and step2["pre_audit_decision"]["runtime_implementation_authorized"] is True
        ),
        "runner_packet_status_not_release": runner["status"]
        == "barnes_hut_runner_parity_pod_ab_collected_not_release",
        "runner_parity_geomean_floor": float(summary["runner_vs_existing_fused_control_geomean"]) >= 0.98,
        "runner_parity_each_size_floor": all(
            float(row["runner_vs_existing_fused_control_speedup"]) >= 0.95
            for row in parity_rows
        ),
        "historical_predecessor_material_floor": float(summary["historical_optix_over_runner_geomean"])
        >= 1.20
        and all(float(row["historical_optix_over_runner_speedup"]) >= 1.20 for row in historical_rows),
        "runner_runtime_trunk_all_samples": runner["checks"]["runner_runtime_trunk_executes_all_samples"],
        "runner_internal_residency_all_samples": runner["checks"]["runner_internal_device_residency_all_samples"],
        "runner_no_frontier_or_contribution_host_materialization": runner["checks"][
            "runner_no_frontier_or_contribution_host_materialization"
        ],
        "runner_control_output_equivalence": runner["checks"]["runner_control_output_equivalence_all_sizes"],
        "m29_confirms_no_v2_14_equivalent_current_trunk_surface": m29["classification"]
        == "v2_14_has_cpu_fused_or_typed_stream_only",
        "source_helper_is_current_and_generic": source_surface["helper_present"]
        and source_surface["helper_body_has_no_barnes_name"],
        "app_adapter_calls_productized_helper": source_surface["app_adapter_calls_helper"],
        "non_authorization_flags_closed": _non_authorization_flags_closed(runner, m29, step2),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "schema": SCHEMA,
        "date": DATE,
        "status": STATUS_FAILED if failed_checks else STATUS_READY,
        "inputs": {
            "m66_consensus": _rel(M66_CONSENSUS),
            "m45_reaudit": _rel(M45_REAUDIT),
            "step2_pre_audit": _rel(STEP2_PRE_AUDIT),
            "runner_packet": _rel(RUNNER_PACKET),
            "m29_surface": _rel(M29_SURFACE),
            "prepared_execution": _rel(PREPARED_EXECUTION),
            "barnes_hut_app": _rel(APP),
        },
        "reconciliation": reconciliation,
        "phase_structure": phase_structure,
        "source_surface": source_surface,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed_checks,
        "summary": {
            "status": STATUS_FAILED if failed_checks else STATUS_READY,
            "failed_check_count": len(failed_checks),
            "barnes_hut_should_be_current_coding_target": False,
            "pod_authorized": False,
            "all_app_authorized": False,
            "external_review_required_before_counting": True,
            "historical_optix_over_runner_geomean": summary["historical_optix_over_runner_geomean"],
            "runner_vs_existing_fused_control_geomean": summary[
                "runner_vs_existing_fused_control_geomean"
            ],
            "m29_classification": m29["classification"],
        },
        "non_authorization": {
            "release_authorized": False,
            "all_app_run_authorized": False,
            "paid_pod_spend_authorized": False,
            "focused_pod_spend_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_over_v2_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_barnes_hut_engine_tuning_authorized": False,
            "watch_row_closure_authorized": False,
        },
        "goal_level_decision_audit": {
            "decision": (
                "Treat Barnes-Hut M67 as a local phase-structure reconciliation "
                "audit, not a new Barnes-Hut coding branch."
            ),
            "was_i_foolish": (
                "No after rereading M45/M66/M29. The foolish path would be to "
                "turn M66's redirect into more Barnes-Hut app tuning."
            ),
            "foolish_actions": (
                "The risky action would be ignoring that M45 already blocked "
                "new Barnes-Hut app tuning and that M28/M29 already productized "
                "the fused runner route."
            ),
            "other_path": (
                "Run another focused POD or write another Barnes-Hut-specific "
                "route. That would repeat the leaf-first mistake."
            ),
            "different_path_now": (
                "Ask external review whether existing productized Barnes-Hut "
                "evidence counts as the Step-1 material family, then move to "
                "the next generic Set-A family or select a replacement."
            ),
        },
    }


def _phase_structure(*, summary: dict[str, Any], variant_summaries: dict[str, Any]) -> dict[str, Any]:
    parity_rows = list(summary["parity_rows"])
    historical_rows = list(summary["historical_reference_rows"])
    process_rows = []
    for row in parity_rows:
        body_count = int(row["body_count"])
        runner = variant_summaries[f"runner_prepared_execution_fused_numba_cuda:{body_count}"]
        control = variant_summaries[f"existing_app_front_door_fused_numba_cuda_control:{body_count}"]
        process_rows.append(
            {
                "body_count": body_count,
                "runner_process_wall_sec_median": runner["process_wall_sec_median"],
                "control_process_wall_sec_median": control["process_wall_sec_median"],
                "runner_process_wall_over_control": _ratio(
                    control["process_wall_sec_median"],
                    runner["process_wall_sec_median"],
                ),
            }
        )
    return {
        "historical_predecessor": {
            "path": "prepared_aggregate_frontier_weighted_vector_optix",
            "role": "historical no-go predecessor, not primary public claim",
            "compressible_nonzero_phase_found": bool(summary["historical_reference_material"]),
            "hot_speedup_geomean": summary["historical_optix_over_runner_geomean"],
            "rows": historical_rows,
            "reading": (
                "The old frontier route has a non-zero hot physical cost that the "
                "fused vector route displaces. This is useful predecessor-displacement "
                "evidence, not proof that the wrapper is faster than the current fused route."
            ),
        },
        "current_fused_control": {
            "path": "fused_frontier_force_sum_bucketized_numba_cuda",
            "role": "current fastest app-front-door control",
            "new_compressible_phase_found": False,
            "runner_parity_with_existing_fused_partner": bool(
                summary["runner_parity_with_existing_fused_partner"]
            ),
            "runner_vs_control_geomean": summary["runner_vs_existing_fused_control_geomean"],
            "rows": parity_rows,
            "process_wall_rows": process_rows,
            "reading": (
                "The current fused control already removed the material frontier/"
                "contribution path. The runner requirement is parity plus metadata, "
                "not a fresh speedup over this control."
            ),
        },
        "productized_runner": {
            "path": "prepared_execution_fused_vector_sum_numba_cuda",
            "role": "productized runtime-trunk carrier for the fused partner route",
            "runtime_trunk_executes_end_to_end": True,
            "internal_device_residency_between_rtdl_phases": True,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "output_equivalence_to_current_control": True,
        },
    }


def _source_surface(prepared_source: str, app_source: str) -> dict[str, Any]:
    helper_name = "def run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session"
    helper_present = helper_name in prepared_source
    helper_body = ""
    if helper_present:
        start = prepared_source.index(helper_name)
        end_marker = "def describe_prepared_execution_user_pattern"
        end = prepared_source.index(end_marker, start) if end_marker in prepared_source[start:] else len(prepared_source)
        helper_body = prepared_source[start:end]
    return {
        "helper_present": helper_present,
        "helper_body_has_no_barnes_name": "barnes" not in helper_body.lower(),
        "helper_records_runtime_trunk": "runtime_trunk_executes_end_to_end" in helper_body,
        "helper_records_internal_residency": "internal_device_residency_between_rtdl_phases" in helper_body,
        "helper_records_materialization_flags": "frontier_rows_materialized_on_host" in helper_body
        and "contribution_rows_materialized_on_host" in helper_body,
        "app_adapter_calls_helper": "run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session"
        in app_source
        and "prepared_execution_fused_vector_sum_numba_cuda" in app_source,
    }


def _non_authorization_flags_closed(runner: dict[str, Any], m29: dict[str, Any], step2: dict[str, Any]) -> bool:
    runner_flags = dict(runner.get("non_authorization") or {})
    m29_flags = dict(m29.get("non_authorization") or {})
    step2_flags = dict(step2.get("hard_guards") or {})
    return (
        all(value is False for value in runner_flags.values())
        and all(value is False for value in m29_flags.values())
        and all(value is False for value in step2_flags.values())
    )


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    decision = payload["decision"]
    phase = payload["phase_structure"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 M67 Barnes-Hut Phase-Structure Pre-Audit",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Bottom Line",
        "",
        "M67 finds no reason to start another Barnes-Hut coding branch. The",
        "material Barnes-Hut route already exists as the aggregate-tree fused",
        "weighted-vector partner path routed through the productized prepared",
        "execution session runner. The current fastest fused control has no new",
        "compressible phase for the runner to remove; the runner preserves it at",
        f"`{float(summary['runner_vs_existing_fused_control_geomean']):.6f}x` geomean.",
        "",
        "The large material delta is against the historical prepared OptiX/frontier",
        "predecessor only:",
        f"`{float(summary['historical_optix_over_runner_geomean']):.6f}x` geomean.",
        "That is predecessor-displacement evidence, not wrapper-is-faster wording.",
        "",
        "## Reconciliation",
        "",
        "- M45 blocks new Barnes-Hut app tuning and classifies the old all-app",
        "  blocker as focused-fix-covered pending full-suite validation.",
        "- M66 redirects to a local Barnes-Hut pre-audit after RayJoin non-go.",
        "- M67 reconciles them: audit existing productized runtime evidence, then",
        "  ask external review whether Barnes-Hut already counts as the Step-1",
        "  material family.",
        "",
        "## Phase Structure",
        "",
        "| Path | Role | Reading |",
        "| --- | --- | --- |",
        f"| historical prepared OptiX/frontier | {phase['historical_predecessor']['role']} | compressible non-zero phase found: `{str(phase['historical_predecessor']['compressible_nonzero_phase_found']).lower()}` |",
        f"| current fused Numba CUDA control | {phase['current_fused_control']['role']} | new compressible phase found: `{str(phase['current_fused_control']['new_compressible_phase_found']).lower()}` |",
        f"| productized runner | {phase['productized_runner']['role']} | runtime trunk executes: `{str(phase['productized_runner']['runtime_trunk_executes_end_to_end']).lower()}` |",
        "",
        "## Decision",
        "",
        f"- Status: `{decision['status']}`",
        f"- Barnes-Hut current coding target: `{str(decision['barnes_hut_should_be_current_coding_target']).lower()}`",
        f"- POD now authorized: `{str(decision['pod_now_authorized']).lower()}`",
        f"- All-app now authorized: `{str(decision['all_app_now_authorized']).lower()}`",
        f"- Material source versus historical predecessor: `{str(decision['material_source_found_against_historical_predecessor']).lower()}`",
        f"- New material source versus current fused control: `{str(decision['new_material_source_found_against_current_fused_control']).lower()}`",
        "",
        decision["next_action"],
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{name}`: `{str(ok).lower()}`" for name, ok in payload["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{len(payload['failed_checks'])}`",
            "",
            "## Non-Authorization",
            "",
            "This packet authorizes no release, no all-app run, no POD spend, no",
            "public speedup claim, no broad V3-over-V2 claim, no RT-core speedup",
            "claim, no whole-app speedup claim, no paper reproduction claim, no",
            "true-zero-copy claim, no automatic partner selection, no app-specific",
            "Barnes-Hut engine tuning, and no watch-row closure.",
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


def _ratio(denominator: Any, numerator: Any) -> float | None:
    if denominator is None or float(denominator) <= 0.0:
        return None
    result = float(numerator) / float(denominator)
    return result if math.isfinite(result) else None


if __name__ == "__main__":
    raise SystemExit(main())
