#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-23"
SCHEMA = "rtdl.phoenix_v3.m70.rtnn_focused_protocol.v1"
STATUS_READY = "m70_rtnn_focused_protocol_draft_ready_for_review_no_execution_no_pod_no_release"
STATUS_FAILED = "m70_rtnn_focused_protocol_draft_failed"

M69_PACKET = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m69_rtnn_phase_shape_bridge_audit_{DATE}.json"
M69_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / f"codex_claude_antigravity_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_3ai_consensus_{DATE}.md"
)
CLAUDE_M69 = (
    ROOT
    / "docs"
    / "reviews"
    / f"claude_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_recorded_review_{DATE}.md"
)
ANTIGRAVITY_M69 = (
    ROOT
    / "docs"
    / "reviews"
    / f"antigravity_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_review_{DATE}.md"
)
M69_AUDIT = ROOT / "docs" / "reports" / f"phoenix_v3_m69_goal_completion_audit_{DATE}.md"
RTNN_APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"

OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m70_rtnn_focused_protocol_{DATE}.json"
OUT_PACKET_MD = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m70_rtnn_focused_protocol_{DATE}.md"
OUT_REPORT_MD = ROOT / "docs" / "reports" / f"phoenix_v3_m70_rtnn_focused_protocol_{DATE}.md"
OUT_CALL = ROOT / "docs" / "reviews" / f"call_for_review_phoenix_v3_m70_rtnn_focused_protocol_{DATE}.md"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    for path in (args.json_out, args.packet_md_out, args.report_md_out, args.call_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render_markdown(payload)
    args.packet_md_out.write_text(rendered, encoding="utf-8")
    args.report_md_out.write_text(rendered, encoding="utf-8")
    args.call_out.write_text(render_call_for_review(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phoenix V3 M70 RTNN focused protocol draft.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--packet-md-out", type=Path, default=OUT_PACKET_MD)
    parser.add_argument("--report-md-out", type=Path, default=OUT_REPORT_MD)
    parser.add_argument("--call-out", type=Path, default=OUT_CALL)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_payload() -> dict[str, Any]:
    m69 = _read_json(M69_PACKET)
    m69_consensus = M69_CONSENSUS.read_text(encoding="utf-8")
    claude = CLAUDE_M69.read_text(encoding="utf-8")
    antigravity = ANTIGRAVITY_M69.read_text(encoding="utf-8")
    audit = M69_AUDIT.read_text(encoding="utf-8")
    rtnn_app = RTNN_APP.read_text(encoding="utf-8")
    prepared_execution = PREPARED_EXECUTION.read_text(encoding="utf-8")

    protocol_shapes = _protocol_shapes(m69["rtnn_shape_groups"], m69["rtnn_all_app_rows"])
    non_authorization = {
        "release_authorized": False,
        "all_app_run_authorized": False,
        "pod_authorized": False,
        "paid_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "runbook_execution_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_over_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v4_work_authorized": False,
        "embedding_authorized": False,
        "c_abi_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "route_specific_rtnn_app_tuning_authorized": False,
        "watch_row_closure_authorized": False,
    }
    phase_metrics = _phase_metrics(m69["phase_attribution"])
    stop_conditions = [
        "Stop if a future harness lacks a reviewed local dry-run gate.",
        "Stop if any frozen RTNN shape lacks an exact same-contract incumbent row.",
        "Stop if clustered or shell rows reuse the uniform repeat50 phase split without per-distribution measurement.",
        "Stop if non-self-query batches are proposed without separate code-path review.",
        "Stop if input-loading/packing, prepare, runner-after-pack, hot-query, and runner-wall metrics are merged.",
        "Stop if exact aggregate, productized prepared-session runner, graph partner bridge, raw rows, or paper diagnostic rows are merged into one claim.",
        "Stop if the result is only input-loading/packing consolidation or repeat50 amortization with no runner-after-pack contribution.",
        "Stop if productized runner metadata does not show prepared_execution_session_runner and runtime_trunk_executes_end_to_end=true.",
        "Stop if any public, release, all-app, POD, V4, embedding, C ABI, true-zero-copy, route-specific tuning, or watch-row closure wording appears.",
    ]
    future_harness_requirements = {
        "status": "requirements_only_no_execution",
        "commands_present": False,
        "authorization_token_present": False,
        "exact_shape_count": len(protocol_shapes),
        "required_distributions": ["uniform", "clustered", "shell"],
        "required_phase_metrics": phase_metrics["required_metric_names"],
        "required_metadata": [
            "mode=prepared_execution_ranked_summary",
            "productized_execution_path=prepared_execution_session_runner",
            "runtime_trunk_executes_end_to_end=true",
            "prepared_execution_session_runner_used=true",
            "material_probe_candidate recorded without public claim",
            "release_authorized=false",
            "public_speedup_claim_authorized=false",
            "automatic_partner_selection_authorized=false",
        ],
        "future_material_candidate_bar_if_separately_authorized": {
            "runner_wall_speedup_vs_same_contract_incumbent": ">=1.20x",
            "runner_after_input_pack_speedup_vs_same_contract_incumbent": ">=1.20x or explicitly explained",
            "hot_query_speedup_vs_same_contract_incumbent": ">=0.98x; no material claim if hot query regresses materially",
            "input_load_pack_share_guard": "input-loading/packing cannot be the sole source of a positive result",
            "distribution_scope": "uniform, clustered, and shell must each have their own phase rows before clustered/shell claims",
        },
    }
    checks = {
        "m69_3ai_accepts_protocol_draft_only": (
            "accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release" in m69_consensus
            and "M70 may draft a focused protocol only" in m69_consensus
        ),
        "claude_carry_forward_present": (
            "uniform-distribution only" in claude
            and "full-batch self-queries" in claude
            and "0.988781x" in claude
        ),
        "antigravity_carry_forward_present": (
            "Proceed to M70 protocol drafting only" in antigravity
            and "0.988781x" in antigravity
            and "Full-Batch Self-Query Constraint" in antigravity
        ),
        "m69_audit_complete": (
            "m69_goal_complete_3ai_accept_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release"
            in audit
        ),
        "all_14_rows_named": sum(len(shape["rows"]) for shape in protocol_shapes) == 14,
        "all_7_shape_groups_named": len(protocol_shapes) == 7,
        "all_rows_have_same_contract_incumbents": all(
            row.get("same_contract_incumbent") for shape in protocol_shapes for row in shape["rows"]
        ),
        "distribution_bounds_required": set(shape["distribution"] for shape in protocol_shapes)
        == {"uniform", "clustered", "shell"},
        "full_batch_self_query_constraint_source_present": (
            "prepared_execution_ranked_summary currently requires full-batch self queries" in rtnn_app
        ),
        "generic_helper_present": "def run_fixed_radius_ranked_summary_3d_prepared_session" in prepared_execution,
        "phase_metrics_separated": len(phase_metrics["required_metric_names"]) >= 8,
        "no_commands_or_authorization_token": (
            future_harness_requirements["commands_present"] is False
            and future_harness_requirements["authorization_token_present"] is False
        ),
        "all_non_authorization_flags_false": all(value is False for value in non_authorization.values()),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = STATUS_FAILED if failed_checks else STATUS_READY
    return {
        "schema": SCHEMA,
        "date": DATE,
        "status": status,
        "inputs": {
            "m69_packet": _rel(M69_PACKET),
            "m69_consensus": _rel(M69_CONSENSUS),
            "claude_m69_review": _rel(CLAUDE_M69),
            "antigravity_m69_review": _rel(ANTIGRAVITY_M69),
            "m69_completion_audit": _rel(M69_AUDIT),
            "rtnn_app": _rel(RTNN_APP),
            "prepared_execution": _rel(PREPARED_EXECUTION),
        },
        "source_verdicts": {
            "m69_3ai": "accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release",
            "m70_scope": "protocol_draft_only_no_execution",
        },
        "protocol_scope": {
            "protocol_type": "review_packet_only",
            "execution_authorized_now": False,
            "runbook_authorized_now": False,
            "pod_authorized_now": False,
            "all_app_authorized_now": False,
            "release_authorized_now": False,
            "next_step_if_accepted": "M71_local_rtnn_harness_design_or_dry_run_gate_no_pod",
        },
        "selected_family": {
            "family_id": "fixed_radius_ranked_summary_3d_prepared_session",
            "pressure_app": "rtnn",
            "productized_app_mode": "prepared_execution_ranked_summary",
            "current_front_door_mode": "prepared_optix_ranked_summary",
            "generic_helper": "run_fixed_radius_ranked_summary_3d_prepared_session",
            "contract": "generic prepared 3-D fixed-radius bounded ranked-summary aggregate",
            "full_batch_self_query_required": True,
            "automatic_partner_selection_authorized": False,
            "route_specific_rtnn_app_tuning_authorized": False,
        },
        "m69_carry_forward": [
            "repeat50 phase attribution is uniform-distribution evidence only",
            "per-distribution phase bounds are required before clustered or shell protocol use",
            "prepared_execution_ranked_summary currently requires full-batch self-queries",
            "exact frozen RTNN shapes and same-contract incumbents must be named",
            "0.988781x hot-query boundary must remain visible",
            "exact aggregate, productized prepared-session runner, graph partner bridge, and diagnostic rows must not be merged",
        ],
        "frozen_shapes": protocol_shapes,
        "phase_metric_contract": phase_metrics,
        "future_harness_requirements": future_harness_requirements,
        "stop_conditions": stop_conditions,
        "review_request_verdicts": [
            "accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod",
            "accept_m70_protocol_shape_but_revise_before_harness",
            "blocked_m70_missing_same_contract_or_phase_boundaries",
            "reject_m70_protocol_repeats_leaf_first_or_overclaims",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "non_authorization": non_authorization,
        "summary": {
            "status": status,
            "failed_check_count": len(failed_checks),
            "shape_group_count": len(protocol_shapes),
            "row_count": sum(len(shape["rows"]) for shape in protocol_shapes),
            "execution_authorized": False,
            "pod_authorized": False,
            "all_app_authorized": False,
            "release_authorized": False,
            "next_step_if_accepted": "M71_local_rtnn_harness_design_or_dry_run_gate_no_pod",
        },
        "goal_level_decision_audit": {
            "decision": "draft a focused RTNN protocol without execution after M69 accepted RTNN as bridgeable but not runbook-ready",
            "was_i_foolish": "No. M70 preserves M69's no-execution boundary and turns the review debt into explicit protocol gates.",
            "foolish_actions": "It would be foolish to use M69's repeat50 runner-wall signal as execution authorization or to hide the 0.988781x hot-query boundary.",
            "other_path": "Jump directly to POD or tune RTNN app routes. That repeats leaf-first work and ignores the frozen all-app gap.",
            "different_path_now": "Freeze exact shapes, same-contract incumbents, per-distribution requirements, separated phase metrics, and fail-closed stop conditions for external review.",
        },
    }


def _protocol_shapes(shape_groups: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_group: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = f"{row['distribution']}:{row['point_count']}:{row['comparison_group']}"
        rows_by_group.setdefault(key, []).append(row)

    protocol_shapes = []
    for shape in shape_groups:
        shape_rows = []
        for row in sorted(rows_by_group[shape["shape_key"]], key=lambda item: item["backend"]):
            shape_rows.append(
                {
                    "backend": row["backend"],
                    "case_id": row["case_id"],
                    "row_id": row["row_id"],
                    "frozen_v3_speedup_vs_v2": row["v3_speedup_vs_v2"],
                    "below_1_05x": row["below_1_05x"],
                    "same_contract_incumbent": _same_contract_incumbent(row),
                }
            )
        protocol_shapes.append(
            {
                "shape_key": shape["shape_key"],
                "distribution": shape["distribution"],
                "point_count": shape["point_count"],
                "comparison_group": shape["comparison_group"],
                "query_batch_size": shape["point_count"],
                "query_role": "full_batch_self_query",
                "ranked_summary_contract": "prepared 3-D fixed-radius bounded ranked-summary aggregate",
                "geomean_v3_vs_v2": shape["geomean_v3_vs_v2"],
                "rows_below_1_05x": shape["rows_below_1_05x"],
                "rows": shape_rows,
                "per_distribution_phase_bound_required": shape["distribution"] in {"clustered", "shell"},
            }
        )
    return protocol_shapes


def _same_contract_incumbent(row: dict[str, Any]) -> dict[str, Any]:
    terms = [
        "same point_count",
        "same distribution",
        "same generated points or frozen point file",
        "same radius and k from the frozen RTNN row config",
        "query_batch_size equals point_count",
        "ranked-summary aggregate output contract",
        "signature or aggregate checks must match before timing is interpreted",
    ]
    if row["backend"] == "optix":
        return {
            "incumbent_id": "legacy_app_front_door_prepared_optix_ranked_summary",
            "mode": "prepared_optix_ranked_summary",
            "backend": "optix",
            "result_mode": "ranked-summary-aggregate-prepared-query-batch-float32",
            "same_contract_terms": terms,
        }
    return {
        "incumbent_id": "frozen_v2_14_embree_ranked_summary_row",
        "mode": "same-contract embree fixed-radius ranked-summary aggregate incumbent",
        "backend": "embree",
        "result_mode": "ranked-summary aggregate",
        "same_contract_terms": terms,
        "new_current_route_execution_requires_review": True,
    }


def _phase_metrics(phase: dict[str, Any]) -> dict[str, Any]:
    required = [
        "input_load_sec",
        "input_pack_sec",
        "input_load_pack_sec",
        "execution_prepare_sec",
        "runner_after_input_load_pack_sec",
        "hot_query_median_sec",
        "runner_wall_sec",
        "measured_total_sec",
        "measured_median_sec",
        "signature_match_status",
    ]
    return {
        "required_metric_names": required,
        "must_keep_separate": True,
        "m69_uniform_repeat50_reference": {
            "total_runner_wall_delta_sec": phase["total_runner_wall_delta_sec"],
            "input_load_pack_share_of_delta": phase["input_load_pack_share_of_delta"],
            "runner_after_input_pack_share_of_delta": phase["runner_after_input_pack_share_of_delta"],
            "execution_prepare_delta_sec": phase["execution_prepare_delta_sec"],
            "hot_query_speedup_vs_legacy": phase["hot_query_speedup_vs_legacy"],
            "scope": "uniform-distribution repeat50 reference only",
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 M70 RTNN Focused Protocol Draft",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Bottom Line",
        "",
        "M70 is a no-execution focused protocol draft. It names the exact frozen",
        "RTNN ranked-summary shapes, their same-contract incumbents, the phase",
        "metrics that must remain separated, and the stop conditions for any later",
        "harness. It authorizes no runbook, no POD, no all-app run, no release, and",
        "no public performance claim.",
        "",
        "## Scope",
        "",
        f"- Family: `{payload['selected_family']['family_id']}`",
        f"- Productized app mode: `{payload['selected_family']['productized_app_mode']}`",
        f"- Current front door: `{payload['selected_family']['current_front_door_mode']}`",
        f"- Shape groups: `{payload['summary']['shape_group_count']}`",
        f"- Frozen RTNN rows: `{payload['summary']['row_count']}`",
        f"- Next step if accepted: `{payload['summary']['next_step_if_accepted']}`",
        "",
        "## M69 Carry-Forward",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["m69_carry_forward"])
    lines.extend(
        [
            "",
            "## Frozen Shapes",
            "",
            "| Shape | distribution | points | geomean V3/V2 | rows | phase bound |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for shape in payload["frozen_shapes"]:
        lines.append(
            f"| `{shape['shape_key']}` | `{shape['distribution']}` | `{shape['point_count']}` | "
            f"`{shape['geomean_v3_vs_v2']:.6f}x` | `{len(shape['rows'])}` | "
            f"`{str(shape['per_distribution_phase_bound_required']).lower()}` |"
        )
    lines.extend(["", "## Same-Contract Incumbents", ""])
    for shape in payload["frozen_shapes"]:
        lines.append(f"- `{shape['shape_key']}`")
        for row in shape["rows"]:
            incumbent = row["same_contract_incumbent"]
            lines.append(
                f"  - `{row['case_id']}` -> `{incumbent['incumbent_id']}` "
                f"({incumbent['mode']})"
            )
    lines.extend(
        [
            "",
            "## Phase Metric Contract",
            "",
            "These metrics must remain separate:",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in payload["phase_metric_contract"]["required_metric_names"])
    ref = payload["phase_metric_contract"]["m69_uniform_repeat50_reference"]
    lines.extend(
        [
            "",
            "M69 reference, uniform-distribution repeat50 only:",
            "",
            f"- Total runner-wall delta: `{ref['total_runner_wall_delta_sec']:.6f}s`",
            f"- Input load/pack share: `{ref['input_load_pack_share_of_delta']:.3f}`",
            f"- Runner-after-pack share: `{ref['runner_after_input_pack_share_of_delta']:.3f}`",
            f"- Execution-prepare delta: `{ref['execution_prepare_delta_sec']:.6f}s`",
            f"- Hot-query speedup vs legacy: `{ref['hot_query_speedup_vs_legacy']:.6f}x`",
            "",
            "## Future Harness Requirements",
            "",
            f"- Status: `{payload['future_harness_requirements']['status']}`",
            f"- Commands present: `{str(payload['future_harness_requirements']['commands_present']).lower()}`",
            f"- Authorization token present: `{str(payload['future_harness_requirements']['authorization_token_present']).lower()}`",
            "",
            "## Stop Conditions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["stop_conditions"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{name}`: `{str(ok).lower()}`" for name, ok in payload["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{len(payload['failed_checks'])}`",
            "",
            "## Non-Authorization",
            "",
            "This protocol draft authorizes no V3 release, no all-app benchmark run, no",
            "POD spend, no paid POD spend, no focused POD spend, no runbook execution,",
            "no public speedup wording, no broad V3-over-V2 claim, no whole-app",
            "speedup claim, no paper reproduction claim, no RT-core speedup claim, no",
            "V4 work, no embedding, no C ABI, no true-zero-copy claim, no automatic",
            "partner selection, no route-specific RTNN app tuning, and no watch-row",
            "closure.",
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}.",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path that actually solves the problem? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_call_for_review(payload: dict[str, Any]) -> str:
    lines = [
        "# Call For Review: Phoenix V3 M70 RTNN Focused Protocol Draft",
        "",
        f"Date: {DATE}",
        "",
        "Status: `request_m70_rtnn_focused_protocol_review_no_execution_no_pod`",
        "",
        "Please critically review the M70 protocol draft only. It must not authorize",
        "execution unless a later, separate consensus explicitly does so.",
        "",
        "## Files To Review",
        "",
        f"- `{_rel(OUT_JSON)}`",
        f"- `{_rel(OUT_PACKET_MD)}`",
        f"- `{_rel(OUT_REPORT_MD)}`",
        "- `tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py`",
        "",
        "## Specific Questions",
        "",
        "1. Does M70 name all exact frozen RTNN shapes and same-contract incumbents?",
        "2. Does it correctly carry the M69 boundary that repeat50 phase evidence is uniform-distribution only?",
        "3. Does it require per-distribution phase bounds before clustered or shell shapes are used?",
        "4. Does it preserve the full-batch self-query constraint?",
        "5. Are hot-query, runner-wall, prepare, and input-loading/packing metrics separated strongly enough?",
        "6. Are the stop conditions enough to prevent RTNN app tuning, repeat50 overclaiming, and contract mixing?",
        "7. Is M71 local harness design/dry-run gate the right next step, with no POD and no runbook execution?",
        "8. Are any non-authorization boundaries weakened?",
        "",
        "## Acceptable Verdict Labels",
        "",
    ]
    lines.extend(f"- `{verdict}`" for verdict in payload["review_request_verdicts"])
    lines.extend(
        [
            "",
            "If you choose revision/block/reject, list the exact required changes.",
            "",
            "## Explicit Non-Authorization Block",
            "",
            "No matter the verdict, this review carries: no V3 release, no all-app",
            "benchmark run, no POD spend, no paid POD spend, no focused POD spend,",
            "no runbook execution, no public speedup wording, no broad V3-over-V2",
            "wording, no whole-app speedup wording, no paper reproduction wording,",
            "no RT-core speedup wording, no V4 work, no embedding, no C ABI, no",
            "true-zero-copy claim, no automatic partner selection, no route-specific",
            "RTNN app tuning, and no watch-row closure.",
            "",
            "## Goal-Level Decision Audit",
            "",
            "Decision: seek external review for an RTNN focused protocol draft before",
            "any harness execution or POD request.",
            "",
            "1. Was I foolish?",
            "",
            "   No.",
            "",
            "2. If yes, what actions made the decision foolish?",
            "",
            "   It would be foolish to treat M69's repeat50 runner-wall signal as",
            "   permission to execute or claim performance.",
            "",
            "3. Was there another path?",
            "",
            "   Yes. Run a focused RTNN benchmark immediately. That skips the exact",
            "   shape/incumbent/phase-boundary review M69 required.",
            "",
            "4. Can I now try a different path that actually solves the problem?",
            "",
            "   Yes. Freeze the protocol, get review, and only then build a local harness",
            "   gate if reviewers accept it.",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("/", "\\")


if __name__ == "__main__":
    raise SystemExit(main())
