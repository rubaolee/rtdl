#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-23"
SCHEMA = "rtdl.phoenix_v3.m69.rtnn_phase_shape_bridge_audit.v1"
STATUS_READY = "m69_rtnn_phase_shape_bridge_audit_ready_for_external_review_no_pod_no_release"
STATUS_FAILED = "m69_rtnn_phase_shape_bridge_audit_failed"

SCORECARD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json"
M68_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m68_next_set_a_family_selection_3ai_consensus_2026-06-23.md"
)
RTNN_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622"
    / "summary.json"
)
RTNN_APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
FRONT_DOORS = ROOT / "src" / "rtdsl" / "current_benchmark_front_doors.py"
SCALE_PROFILES = ROOT / "src" / "rtdsl" / "current_benchmark_scale_profiles.py"
ROUTE_DECISIONS = ROOT / "src" / "rtdsl" / "current_benchmark_route_decisions.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / f"phoenix_v3_m69_rtnn_phase_shape_bridge_audit_{DATE}.json"
OUT_MD = ROOT / "docs" / "reports" / f"phoenix_v3_m69_rtnn_phase_shape_bridge_audit_{DATE}.md"


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
    parser = argparse.ArgumentParser(description="Build Phoenix V3 M69 RTNN phase/shape bridge audit.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_payload() -> dict[str, Any]:
    scorecard = _read_json(SCORECARD)
    evidence = _read_json(RTNN_EVIDENCE)
    m68 = M68_CONSENSUS.read_text(encoding="utf-8")
    app_source = RTNN_APP.read_text(encoding="utf-8")
    front_source = FRONT_DOORS.read_text(encoding="utf-8")
    scale_source = SCALE_PROFILES.read_text(encoding="utf-8")
    route_source = ROUTE_DECISIONS.read_text(encoding="utf-8")
    prepared_source = PREPARED_EXECUTION.read_text(encoding="utf-8")

    rows = [_normalize_rtnn_row(row) for row in scorecard["row_classifications"] if row["app_id"] == "rtnn"]
    grouped_rows = _group_rows(rows)
    phase = _phase_attribution(evidence)
    source_surface = _source_surface(app_source, front_source, scale_source, route_source, prepared_source)
    bridge = _bridge_decision(rows, grouped_rows, phase, source_surface)
    non_authorization = {
        "release_authorized": False,
        "all_app_run_authorized": False,
        "pod_authorized": False,
        "paid_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_over_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "route_specific_rtnn_app_tuning_authorized": False,
        "runbook_authorized": False,
        "watch_row_closure_authorized": False,
    }
    checks = {
        "m68_authorizes_m69_local_audit_only": (
            "M69 may start as local-only work" in m68
            and "no POD spend" in m68
            and "no all-app benchmark run" in m68
        ),
        "rtnn_rows_present": len(rows) == 14,
        "rtnn_rows_all_ranked_summary": all(row["is_ranked_summary"] for row in rows),
        "rtnn_app_geomean_below_threshold": scorecard["scorecard"]["set_a_app_geomeans_v3_vs_v2"]["rtnn"]
        < 1.05,
        "rtnn_rows_mostly_below_threshold": bridge["row_counts"]["rows_below_1_05x"] >= 10,
        "front_door_currently_legacy_prepared_optix": source_surface[
            "front_door_uses_prepared_optix_ranked_summary"
        ],
        "productized_runner_mode_exists": source_surface["app_prepared_execution_ranked_summary_mode_exists"],
        "productized_runner_calls_generic_helper": source_surface["app_productized_mode_calls_generic_helper"],
        "prepared_helper_generic": source_surface["prepared_helper_generic_contract_present"],
        "distribution_bridge_supported": all(source_surface["distribution_support"].values()),
        "route_decision_keeps_contracts_separate": source_surface["route_decision_separates_contracts"],
        "phase_attribution_not_input_pack_only": phase["not_input_loading_packing_only"],
        "phase_attribution_hot_query_boundary_recorded": phase["hot_query_speedup_vs_legacy"] < 1.0,
        "phase_attribution_runner_after_pack_positive": phase["runner_after_input_pack_delta_sec"] > 0.0,
        "bridge_not_runbook_authorization": bridge["runbook_authorized_now"] is False,
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
            "m68_consensus": _rel(M68_CONSENSUS),
            "rtnn_evidence": _rel(RTNN_EVIDENCE),
            "rtnn_app": _rel(RTNN_APP),
            "front_doors": _rel(FRONT_DOORS),
            "scale_profiles": _rel(SCALE_PROFILES),
            "route_decisions": _rel(ROUTE_DECISIONS),
            "prepared_execution": _rel(PREPARED_EXECUTION),
        },
        "rtnn_all_app_rows": rows,
        "rtnn_shape_groups": grouped_rows,
        "phase_attribution": phase,
        "source_surface": source_surface,
        "bridge_decision": bridge,
        "checks": checks,
        "failed_checks": failed_checks,
        "summary": {
            "status": status,
            "failed_check_count": len(failed_checks),
            "rtnn_row_count": len(rows),
            "rtnn_rows_below_1_05x": bridge["row_counts"]["rows_below_1_05x"],
            "rtnn_shape_groups_below_1_05x": bridge["row_counts"]["shape_groups_below_1_05x"],
            "total_runner_wall_delta_sec": phase["total_runner_wall_delta_sec"],
            "input_load_pack_share_of_delta": phase["input_load_pack_share_of_delta"],
            "runner_after_input_pack_share_of_delta": phase["runner_after_input_pack_share_of_delta"],
            "hot_query_speedup_vs_legacy": phase["hot_query_speedup_vs_legacy"],
            "bridge_status": bridge["status"],
            "next_recommended_goal": bridge["next_recommended_goal"],
            "runbook_authorized": False,
            "pod_authorized": False,
            "all_app_authorized": False,
            "release_authorized": False,
        },
        "non_authorization": non_authorization,
        "goal_level_decision_audit": {
            "decision": (
                "Treat RTNN as bridgeable to the generic ranked-summary runner, "
                "but not yet runbook-ready until external review accepts the local "
                "phase/shape audit."
            ),
            "was_i_foolish": (
                "No. M69 splits the repeat50 wall signal by phase and refuses to "
                "convert it into a hot-query or whole-app claim."
            ),
            "foolish_actions": (
                "The foolish action would be to claim the full 1.370176x runner-wall "
                "speedup as ranked-summary execution speedup, hiding the input-packing "
                "share and the 0.988781x hot-query boundary."
            ),
            "other_path": (
                "Jump directly to a POD runbook or rewrite RTNN app code. Both are "
                "rejected because the all-app shape bridge and phase attribution must "
                "be reviewed first."
            ),
            "different_path_now": (
                "Send the local bridge audit for review. If accepted, a later goal may "
                "draft a bounded focused protocol; if rejected, return to Triangle or "
                "RTDBSCAN reserve candidates."
            ),
        },
    }


def _normalize_rtnn_row(row: dict[str, Any]) -> dict[str, Any]:
    case_id = str(row["case_id"])
    distribution = None
    point_count = None
    match = re.search(r"rtnn_(?:embree|optix)_(clustered|shell|uniform)_(\d+)_ranked_summary", case_id)
    if match:
        distribution = match.group(1)
        point_count = int(match.group(2))
    elif case_id in {"rtnn_embree_prepared_3d_ranked_summary", "rtnn_optix_prepared_3d_ranked_summary"}:
        distribution = "uniform"
        point_count = 65536
    return {
        "suite": row["suite"],
        "row_id": row["row_id"],
        "case_id": case_id,
        "comparison_group": row["comparison_group"],
        "backend": row["backend"],
        "set": row["set"],
        "v3_speedup_vs_v2": float(row["v3_speedup_vs_v2"]),
        "distribution": distribution,
        "point_count": point_count,
        "is_ranked_summary": "ranked_summary" in case_id and "ranked_summary" in row["comparison_group"],
        "below_1_05x": float(row["v3_speedup_vs_v2"]) < 1.05,
        "below_1_0x": float(row["v3_speedup_vs_v2"]) < 1.0,
    }


def _group_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = f"{row['distribution']}:{row['point_count']}:{row['comparison_group']}"
        groups[key].append(row)
    grouped = []
    for key, group_rows in sorted(groups.items()):
        speedups = [row["v3_speedup_vs_v2"] for row in group_rows]
        grouped.append(
            {
                "shape_key": key,
                "distribution": group_rows[0]["distribution"],
                "point_count": group_rows[0]["point_count"],
                "comparison_group": group_rows[0]["comparison_group"],
                "backend_count": len(group_rows),
                "geomean_v3_vs_v2": _geomean(speedups),
                "min_v3_vs_v2": min(speedups),
                "max_v3_vs_v2": max(speedups),
                "rows_below_1_05x": sum(1 for row in group_rows if row["below_1_05x"]),
                "rows": [row["case_id"] for row in group_rows],
            }
        )
    return grouped


def _phase_attribution(evidence: dict[str, Any]) -> dict[str, Any]:
    summary = evidence["summary"]
    phase_rows = summary["phase_rows"]
    runner = phase_rows["productized_prepared_execution_runner"]
    legacy = phase_rows["legacy_app_front_door_prepared_optix"]
    runner_wall = float(runner["runner_wall_sec"])
    legacy_wall = float(legacy["runner_wall_sec"])
    total_delta = legacy_wall - runner_wall
    runner_input = float(runner["input_load_pack_sec"])
    legacy_input = float(legacy["input_load_sec"]) + float(legacy["input_pack_sec"])
    input_delta = legacy_input - runner_input
    legacy_after_input = legacy_wall - legacy_input
    runner_after_input = float(runner["runner_after_input_load_pack_sec"])
    after_delta = legacy_after_input - runner_after_input
    prepare_delta = float(legacy["execution_prepare_sec"]) - float(runner["execution_prepare_sec"])
    hot_delta = float(legacy["hot_query_median_sec"]) - float(runner["hot_query_median_sec"])
    return {
        "runner_wall_sec": runner_wall,
        "legacy_runner_wall_sec": legacy_wall,
        "total_runner_wall_delta_sec": total_delta,
        "runner_input_load_pack_sec": runner_input,
        "legacy_input_load_plus_pack_sec": legacy_input,
        "input_load_pack_delta_sec": input_delta,
        "input_load_pack_share_of_delta": _safe_share(input_delta, total_delta),
        "legacy_after_input_load_pack_sec": legacy_after_input,
        "runner_after_input_pack_sec": runner_after_input,
        "runner_after_input_pack_delta_sec": after_delta,
        "runner_after_input_pack_share_of_delta": _safe_share(after_delta, total_delta),
        "legacy_execution_prepare_sec": float(legacy["execution_prepare_sec"]),
        "runner_execution_prepare_sec": float(runner["execution_prepare_sec"]),
        "execution_prepare_delta_sec": prepare_delta,
        "execution_prepare_share_of_delta": _safe_share(prepare_delta, total_delta),
        "hot_query_median_delta_sec": hot_delta,
        "hot_query_speedup_vs_legacy": summary["comparisons"]["runner_vs_legacy_hot_speedup"],
        "runner_wall_speedup_vs_legacy": summary["comparisons"]["runner_vs_legacy_runner_wall_speedup"],
        "not_input_loading_packing_only": after_delta > 0.0 and _safe_share(input_delta, total_delta) < 0.90,
        "hot_query_is_not_the_material_source": summary["comparisons"]["runner_vs_legacy_hot_speedup"] < 1.0,
        "material_signal_reading": (
            "The repeat50 runner-wall win is not hot-query speedup and is not "
            "input-loading/packing only. It is split across input packing, prepare/"
            "session reuse, and runner-after-pack phases."
        ),
    }


def _source_surface(
    app_source: str,
    front_source: str,
    scale_source: str,
    route_source: str,
    prepared_source: str,
) -> dict[str, Any]:
    route_norm = " ".join(route_source.split())
    return {
        "front_door_uses_prepared_optix_ranked_summary": (
            'row_id="rtnn_prepared_optix_ranked_summary"' in front_source
            and '"prepared_optix_ranked_summary"' in front_source
        ),
        "scale_profile_uses_prepared_optix_ranked_summary": (
            'row_id="rtnn_prepared_optix_scale_default_65536"' in scale_source
            and '"prepared_optix_ranked_summary"' in scale_source
        ),
        "app_prepared_execution_ranked_summary_mode_exists": (
            'if mode == "prepared_execution_ranked_summary"' in app_source
            and "rtnn_prepared_execution_ranked_summary_payload" in app_source
        ),
        "app_productized_mode_calls_generic_helper": (
            "rt.run_fixed_radius_ranked_summary_3d_prepared_session" in app_source
        ),
        "prepared_helper_generic_contract_present": (
            "def run_fixed_radius_ranked_summary_3d_prepared_session" in prepared_source
            and "generic_fixed_radius_ranked_summary_3d_aggregate" in prepared_source
        ),
        "prepared_execution_requires_full_batch_self_queries": (
            "prepared_execution_ranked_summary currently requires full-batch self queries" in app_source
        ),
        "distribution_support": {
            "uniform": '"uniform"' in app_source,
            "clustered": '"clustered"' in app_source,
            "shell": '"shell"' in app_source,
        },
        "route_decision_separates_contracts": (
            "preserve exact aggregate, full-batch prepared direct aggregate" in route_norm
            and "graph partner bridge" in route_norm
            and "front-door contracts" in route_norm
            and "Do not auto-select" in route_norm
        ),
    }


def _bridge_decision(
    rows: list[dict[str, Any]],
    grouped_rows: list[dict[str, Any]],
    phase: dict[str, Any],
    source_surface: dict[str, Any],
) -> dict[str, Any]:
    rows_below = sum(1 for row in rows if row["below_1_05x"])
    groups_below = sum(1 for row in grouped_rows if row["geomean_v3_vs_v2"] < 1.05)
    bridgeable = (
        rows_below >= 10
        and source_surface["app_prepared_execution_ranked_summary_mode_exists"]
        and source_surface["app_productized_mode_calls_generic_helper"]
        and phase["not_input_loading_packing_only"]
    )
    return {
        "status": "bridgeable_but_not_runbook_authorized" if bridgeable else "blocked_before_runbook",
        "row_counts": {
            "rows_total": len(rows),
            "rows_below_1_05x": rows_below,
            "rows_below_1_0x": sum(1 for row in rows if row["below_1_0x"]),
            "shape_groups_total": len(grouped_rows),
            "shape_groups_below_1_05x": groups_below,
        },
        "all_app_shape_bridge_candidate": bridgeable,
        "runbook_authorized_now": False,
        "pod_authorized_now": False,
        "all_app_authorized_now": False,
        "next_recommended_goal": (
            "M70_draft_reviewed_rtnn_focused_protocol_no_execution"
            if bridgeable
            else "select_triangle_or_rtdbscan_reserve_candidate"
        ),
        "required_before_any_later_runbook": [
            "external review accepts M69 phase/shape bridge",
            "protocol names exact frozen RTNN shapes and same-contract incumbent",
            "protocol records that repeat50 phase attribution currently comes from the uniform distribution only",
            "protocol requires per-distribution phase bounds before using clustered or shell shapes",
            "protocol carries the full-batch self-query constraint for prepared_execution_ranked_summary",
            "protocol keeps hot-query, runner-wall, prepare, and input-load/pack metrics separate",
            "protocol preserves no release/all-app/POD/public-claim boundaries until separately authorized",
        ],
        "stop_conditions": [
            "Stop if external review rejects the all-app shape bridge.",
            "Stop if the bridge requires app-specific RTNN native logic.",
            "Stop if the positive signal is only repeat50 amortization with no shape bridge.",
            "Stop if phase attribution shows only input-loading/packing consolidation and no runner-after-pack or prepare/session contribution.",
            "Stop if a later protocol extrapolates the uniform repeat50 phase split to clustered or shell without per-distribution evidence.",
            "Stop if a later protocol proposes non-self-query batches without separate code-path review.",
            "Stop if exact aggregate, graph partner bridge, and productized prepared-session contracts are mixed into one public claim.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    phase = payload["phase_attribution"]
    bridge = payload["bridge_decision"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 M69 RTNN Phase/Shape Bridge Audit",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Bottom Line",
        "",
        "M69 finds RTNN bridgeable to the generic fixed-radius ranked-summary",
        "prepared-session runner, but not runbook-authorized. The existing",
        "repeat50 evidence is not hot-query speedup and must not be described as",
        "whole-RTNN or broad V3-over-V2 performance.",
        "",
        f"- Frozen RTNN all-app rows: `{summary['rtnn_row_count']}`",
        f"- Rows below `1.05x`: `{summary['rtnn_rows_below_1_05x']}`",
        f"- Shape groups below `1.05x`: `{summary['rtnn_shape_groups_below_1_05x']}`",
        f"- Bridge status: `{summary['bridge_status']}`",
        f"- Next recommended goal: `{summary['next_recommended_goal']}`",
        "",
        "## Phase Attribution",
        "",
        f"- Total runner-wall delta: `{phase['total_runner_wall_delta_sec']:.6f}s`",
        f"- Input load/pack delta: `{phase['input_load_pack_delta_sec']:.6f}s`",
        f"- Input load/pack share: `{phase['input_load_pack_share_of_delta']:.3f}`",
        f"- Runner-after-pack delta: `{phase['runner_after_input_pack_delta_sec']:.6f}s`",
        f"- Runner-after-pack share: `{phase['runner_after_input_pack_share_of_delta']:.3f}`",
        f"- Execution-prepare delta: `{phase['execution_prepare_delta_sec']:.6f}s`",
        f"- Hot-query speedup vs legacy: `{phase['hot_query_speedup_vs_legacy']:.6f}x`",
        "",
        phase["material_signal_reading"],
        "",
        "## RTNN Shape Groups",
        "",
        "| Shape | geomean V3/V2 | min | max | rows below 1.05x |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rtnn_shape_groups"]:
        lines.append(
            f"| `{row['shape_key']}` | `{row['geomean_v3_vs_v2']:.6f}x` | "
            f"`{row['min_v3_vs_v2']:.6f}x` | `{row['max_v3_vs_v2']:.6f}x` | "
            f"`{row['rows_below_1_05x']}` |"
        )
    lines.extend(
        [
            "",
            "## Bridge Decision",
            "",
            f"- All-app shape bridge candidate: `{str(bridge['all_app_shape_bridge_candidate']).lower()}`",
            f"- Runbook authorized now: `{str(bridge['runbook_authorized_now']).lower()}`",
            f"- POD authorized now: `{str(bridge['pod_authorized_now']).lower()}`",
            f"- All-app authorized now: `{str(bridge['all_app_authorized_now']).lower()}`",
            "",
            "Required before any later runbook:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in bridge["required_before_any_later_runbook"])
    lines.extend(["", "Stop conditions:", ""])
    lines.extend(f"- {item}" for item in bridge["stop_conditions"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{name}`: `{str(ok).lower()}`" for name, ok in payload["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{len(payload['failed_checks'])}`",
            "",
            "## Non-Authorization",
            "",
            "This packet authorizes no release, no all-app run, no POD spend, no",
            "focused run, no runbook execution, no public speedup wording, no broad",
            "V3-over-V2 claim, no whole-app or paper claim, no RT-core speedup claim,",
            "no automatic partner selection, no route-specific RTNN app tuning, and",
            "no watch-row closure.",
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


def _safe_share(numerator: float, denominator: float) -> float:
    if denominator <= 0.0:
        return 0.0
    return numerator / denominator


def _geomean(values: list[float]) -> float:
    if not values:
        return 0.0
    return math.exp(sum(math.log(max(value, 1e-300)) for value in values) / len(values))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
