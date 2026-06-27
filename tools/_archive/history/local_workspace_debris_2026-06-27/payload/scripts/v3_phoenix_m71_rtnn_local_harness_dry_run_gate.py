#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-23"
SCHEMA = "rtdl.phoenix_v3.m71.rtnn_local_harness_dry_run_gate.v1"
STATUS_READY = "m71_rtnn_local_harness_dry_run_gate_ready_no_execution_no_pod"
STATUS_FAILED = "m71_rtnn_local_harness_dry_run_gate_failed"

M70_PACKET = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m70_rtnn_focused_protocol_{DATE}.json"
M70_PROVISIONAL = (
    ROOT
    / "docs"
    / "reviews"
    / f"codex_antigravity_phoenix_v3_m70_provisional_2ai_consensus_pending_claude_{DATE}.md"
)
M70_STATUS = ROOT / "docs" / "reports" / f"phoenix_v3_m70_status_pending_claude_backfill_{DATE}.md"
RTNN_APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"

OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m71_rtnn_local_harness_dry_run_gate_{DATE}.json"
OUT_MD = ROOT / "docs" / "reports" / f"phoenix_v3_m71_rtnn_local_harness_dry_run_gate_{DATE}.md"
OUT_CALL = ROOT / "docs" / "reviews" / f"call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_{DATE}.md"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    for path in (args.json_out, args.md_out, args.call_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    args.call_out.write_text(render_call_for_review(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phoenix V3 M71 RTNN local harness dry-run gate.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--call-out", type=Path, default=OUT_CALL)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_payload() -> dict[str, Any]:
    m70 = _read_json(M70_PACKET)
    provisional = M70_PROVISIONAL.read_text(encoding="utf-8")
    pending_status = M70_STATUS.read_text(encoding="utf-8")
    app_source = RTNN_APP.read_text(encoding="utf-8")
    prepared_source = PREPARED_EXECUTION.read_text(encoding="utf-8")

    required_timing_fields = [
        "input_load",
        "input_pack",
        "input_load_pack",
        "runner_after_input_load_pack",
        "hot_query_median",
        "runner_wall",
        "runner_measured_total",
        "runner_measured_median",
    ]
    required_metadata_fields = [
        "prepared_execution_session_runner_used",
        "productized_execution_path",
        "runtime_trunk_executes_end_to_end",
        "material_probe_candidate",
        "release_authorized",
        "public_speedup_claim_authorized",
        "broad_v3_faster_than_v2_claim_authorized",
        "signature_match_status",
    ]
    source_surface = _source_surface(app_source, prepared_source, required_timing_fields, required_metadata_fields)
    dry_run_plan = _dry_run_plan(m70["frozen_shapes"], required_timing_fields, required_metadata_fields)
    non_authorization = {
        "release_authorized": False,
        "all_app_run_authorized": False,
        "pod_authorized": False,
        "paid_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "runbook_execution_authorized": False,
        "benchmark_execution_authorized": False,
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
    checks = {
        "m70_provisional_allows_m71_local_only": (
            "M71 local RTNN harness design/dry-run gate" in provisional
            and "no execution, no POD, no runbook" in provisional
        ),
        "m70_not_goal_complete": "M70 is not 3AI-complete" in " ".join(pending_status.split()),
        "m70_packet_no_execution": m70["protocol_scope"]["execution_authorized_now"] is False,
        "dry_run_only": all(item["dry_run_only"] for item in dry_run_plan),
        "all_7_shape_groups_planned": len(dry_run_plan) == 7,
        "all_14_rows_planned": sum(len(item["rows"]) for item in dry_run_plan) == 14,
        "source_productized_mode_present": source_surface["productized_mode_present"],
        "source_generic_helper_call_present": source_surface["generic_helper_call_present"],
        "source_full_batch_constraint_present": source_surface["full_batch_self_query_constraint_present"],
        "source_timing_fields_present": source_surface["required_timing_fields_present"],
        "source_metadata_fields_present": source_surface["required_metadata_fields_present"],
        "source_no_route_specific_tuning_marker": source_surface["no_route_specific_tuning_marker_present"],
        "no_command_templates": source_surface["no_command_templates"] and all(
            item["command_present"] is False for item in dry_run_plan
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
            "m70_packet": _rel(M70_PACKET),
            "m70_provisional_consensus": _rel(M70_PROVISIONAL),
            "m70_pending_status": _rel(M70_STATUS),
            "rtnn_app": _rel(RTNN_APP),
            "prepared_execution": _rel(PREPARED_EXECUTION),
        },
        "scope": {
            "dry_run_gate_only": True,
            "benchmark_execution_authorized": False,
            "runbook_authorized": False,
            "pod_authorized": False,
            "all_app_authorized": False,
            "release_authorized": False,
            "commands_generated": False,
            "authorization_token_present": False,
        },
        "source_surface": source_surface,
        "dry_run_plan": dry_run_plan,
        "required_timing_fields": required_timing_fields,
        "required_metadata_fields": required_metadata_fields,
        "fail_closed_conditions": [
            "fail if query_batch_size differs from point_count",
            "fail if productized mode is not prepared_execution_ranked_summary",
            "fail if helper call is not run_fixed_radius_ranked_summary_3d_prepared_session",
            "fail if any required timing field is missing",
            "fail if signature_match_status is missing",
            "fail if runtime_trunk_executes_end_to_end is missing or false in future measured output",
            "fail if commands or authorization tokens are introduced into this dry-run gate",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "non_authorization": non_authorization,
        "summary": {
            "status": status,
            "failed_check_count": len(failed_checks),
            "shape_group_count": len(dry_run_plan),
            "row_count": sum(len(item["rows"]) for item in dry_run_plan),
            "dry_run_only": True,
            "benchmark_execution_authorized": False,
            "pod_authorized": False,
            "release_authorized": False,
            "telemetry_contract_ready": source_surface["required_timing_fields_present"]
            and source_surface["required_metadata_fields_present"],
        },
        "goal_level_decision_audit": {
            "decision": "continue from M70 provisional acceptance to a local RTNN harness dry-run gate without execution",
            "was_i_foolish": "No. M71 validates schema and telemetry readiness only and remains non-executing.",
            "foolish_actions": "It would be foolish to turn a dry-run gate into a live benchmark or to ignore missing telemetry fields.",
            "other_path": "Wait for Claude before doing any local work. That protects 3AI completion but leaves useful no-execution validation undone.",
            "different_path_now": "Use M71 to validate source-surface routing, exact shape plans, telemetry fields, and fail-closed boundaries while keeping M70 pending Claude backfill.",
        },
    }


def _source_surface(
    app_source: str,
    prepared_source: str,
    required_timing_fields: list[str],
    required_metadata_fields: list[str],
) -> dict[str, Any]:
    timing_present = {field: f'"{field}"' in app_source for field in required_timing_fields}
    metadata_present = {field: field in app_source for field in required_metadata_fields}
    metadata_fields_present = [field for field, present in metadata_present.items() if present]
    metadata_fields_missing = [field for field, present in metadata_present.items() if not present]
    return {
        "productized_mode_present": (
            'if mode == "prepared_execution_ranked_summary"' in app_source
            and "rtnn_prepared_execution_ranked_summary_payload" in app_source
        ),
        "generic_helper_call_present": "rt.run_fixed_radius_ranked_summary_3d_prepared_session" in app_source,
        "generic_helper_defined": "def run_fixed_radius_ranked_summary_3d_prepared_session" in prepared_source,
        "full_batch_self_query_constraint_present": (
            "prepared_execution_ranked_summary currently requires full-batch self queries" in app_source
        ),
        "telemetry_split_helper_present": "_load_rtnn_csv_xyz_records" in app_source,
        "timing_fields": timing_present,
        "metadata_fields_present": metadata_fields_present,
        "metadata_fields_missing": metadata_fields_missing,
        "required_timing_fields_present": all(timing_present.values()),
        "required_metadata_fields_present": all(metadata_present.values()),
        "no_route_specific_tuning_marker_present": '"native_engine_customization": False' in app_source,
        "no_command_templates": "command_template" not in app_source,
    }


def _dry_run_plan(
    frozen_shapes: list[dict[str, Any]],
    required_timing_fields: list[str],
    required_metadata_fields: list[str],
) -> list[dict[str, Any]]:
    plan = []
    for shape in frozen_shapes:
        rows = []
        for row in shape["rows"]:
            rows.append(
                {
                    "backend": row["backend"],
                    "case_id": row["case_id"],
                    "same_contract_incumbent": row["same_contract_incumbent"]["incumbent_id"],
                    "would_validate_signature": True,
                    "would_validate_phase_fields": True,
                }
            )
        plan.append(
            {
                "shape_key": shape["shape_key"],
                "distribution": shape["distribution"],
                "point_count": shape["point_count"],
                "query_batch_size": shape["query_batch_size"],
                "query_role": shape["query_role"],
                "dry_run_only": True,
                "command_present": False,
                "rows": rows,
                "required_timing_fields": required_timing_fields,
                "required_metadata_fields": required_metadata_fields,
                "fail_if_query_batch_size_differs_from_point_count": True,
                "per_distribution_phase_bound_required": shape["per_distribution_phase_bound_required"],
            }
        )
    return plan


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 M71 RTNN Local Harness Dry-Run Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Bottom Line",
        "",
        "M71 is a local dry-run gate only. It validates the RTNN focused harness",
        "schema, exact shape plan, source-surface routing, telemetry fields, and",
        "fail-closed boundaries without executing benchmarks.",
        "",
        "## Summary",
        "",
        f"- Shape groups planned: `{payload['summary']['shape_group_count']}`",
        f"- Rows planned: `{payload['summary']['row_count']}`",
        f"- Telemetry contract ready: `{str(payload['summary']['telemetry_contract_ready']).lower()}`",
        f"- Benchmark execution authorized: `{str(payload['summary']['benchmark_execution_authorized']).lower()}`",
        f"- POD authorized: `{str(payload['summary']['pod_authorized']).lower()}`",
        f"- Release authorized: `{str(payload['summary']['release_authorized']).lower()}`",
        "",
        "## Required Timing Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in payload["required_timing_fields"])
    lines.extend(["", "## Required Metadata Fields", ""])
    lines.extend(f"- `{field}`" for field in payload["required_metadata_fields"])
    lines.extend(
        [
            "",
            "## Dry-Run Shape Plan",
            "",
            "| Shape | distribution | points | rows | phase bound |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for shape in payload["dry_run_plan"]:
        lines.append(
            f"| `{shape['shape_key']}` | `{shape['distribution']}` | `{shape['point_count']}` | "
            f"`{len(shape['rows'])}` | `{str(shape['per_distribution_phase_bound_required']).lower()}` |"
        )
    lines.extend(["", "## Fail-Closed Conditions", ""])
    lines.extend(f"- {item}" for item in payload["fail_closed_conditions"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{name}`: `{str(ok).lower()}`" for name, ok in payload["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{len(payload['failed_checks'])}`",
            "",
            "## Non-Authorization",
            "",
            "This dry-run gate authorizes no V3 release, no all-app benchmark run, no",
            "POD spend, no paid POD spend, no focused POD spend, no runbook execution,",
            "no benchmark execution, no public speedup wording, no broad V3-over-V2",
            "claim, no whole-app speedup claim, no paper reproduction claim, no RT-core",
            "speedup claim, no automatic partner selection, no route-specific RTNN app",
            "tuning, no V4 work, no embedding, no C ABI, no true-zero-copy claim, and",
            "no watch-row closure.",
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
    return "\n".join(
        [
            "# Call For Review: Phoenix V3 M71 RTNN Local Harness Dry-Run Gate",
            "",
            f"Date: {DATE}",
            "",
            "Status: `request_m71_local_dry_run_gate_review_no_execution_no_pod`",
            "",
            "Please review M71 as a local dry-run gate only. It does not execute",
            "benchmarks and does not authorize POD.",
            "",
            "## Files To Review",
            "",
            f"- `{_rel(OUT_JSON)}`",
            f"- `{_rel(OUT_MD)}`",
            "- `tests/v3_phoenix_m71_rtnn_local_harness_dry_run_gate_test.py`",
            "- `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`",
            "",
            "## Specific Questions",
            "",
            "1. Does M71 remain dry-run only with no execution path?",
            "2. Does the telemetry-only RTNN app change correctly expose input_load, input_pack, input_load_pack, runner_after_input_load_pack, hot_query_median, and signature_match_status?",
            "3. Does the dry-run plan cover all 7 M70 shape groups and 14 rows?",
            "4. Are source-surface route checks sufficient before any future harness execution is discussed?",
            "5. Are non-authorization boundaries preserved?",
            "",
            "## Acceptable Verdict Labels",
            "",
            "- `accept_m71_local_dry_run_gate_continue_no_execution_no_pod`",
            "- `revise_m71_dry_run_gate_before_any_harness_work`",
            "- `reject_m71_dry_run_gate_oversteps_no_execution_boundary`",
            "",
            "## Explicit Non-Authorization Block",
            "",
            "No matter the verdict, this review carries: no V3 release, no all-app",
            "benchmark run, no POD spend, no paid POD spend, no focused POD spend, no",
            "runbook execution, no benchmark execution, no public speedup wording, no",
            "broad V3-over-V2 wording, no whole-app speedup wording, no paper",
            "reproduction wording, no RT-core speedup wording, no automatic partner",
            "selection, no route-specific RTNN app tuning, no V4 work, no embedding,",
            "no C ABI, no true-zero-copy claim, and no watch-row closure.",
            "",
        ]
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("/", "\\")


if __name__ == "__main__":
    raise SystemExit(main())
