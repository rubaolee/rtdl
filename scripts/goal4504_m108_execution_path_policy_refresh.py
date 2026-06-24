from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.execution_path_policy_refresh.goal4504.v1"
OUT_JSON = Path("docs/reports/goal4504_v3_0_m108_execution_path_policy_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4504_v3_0_m108_execution_path_policy_refresh_2026-06-17.md")


def _plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "backend": plan["backend"],
        "requires_partner_continuation": plan["requires_partner_continuation"],
        "query_count": plan["query_count"],
        "query_batch_size": plan["query_batch_size"],
        "selected_path": plan["selected_path"],
        "recommended_result_mode": plan["recommended_result_mode"],
        "evidence_goal": plan["evidence_goal"],
        "large_aggregate_only_full_batch_direct_preferred": plan[
            "large_aggregate_only_full_batch_direct_preferred"
        ],
        "direct_native_graph_preferred_when_no_partner_continuation": plan[
            "direct_native_graph_preferred_when_no_partner_continuation"
        ],
        "same_stream_required_for_partner_continuation": plan[
            "same_stream_required_for_partner_continuation"
        ],
        "hidden_auto_dispatch_allowed": plan["hidden_auto_dispatch_allowed"],
        "public_speedup_claim_authorized": plan["public_speedup_claim_authorized"],
        "warnings": plan["warnings"],
        "reasons": plan["reasons"],
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    del root
    scenarios = {
        "unknown_or_small_aggregate_only": rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=False
        ),
        "large_aggregate_only_kitti_1m": rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=False,
            query_count=1_000_000,
            query_batch_size=1_000_000,
        ),
        "large_partner_continuation": rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=True,
            query_count=1_000_000,
            query_batch_size=65_536,
        ),
        "embree_backend": rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=False,
            backend="embree",
            query_count=1_000_000,
        ),
    }
    validation = rt.validate_v2_5_execution_path_policy()
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4504 / V3 M108",
        "policy_version": rt.V2_5_EXECUTION_PATH_POLICY_VERSION,
        "operation": "fixed_radius_ranked_summary_aggregate_3d",
        "graph_query_count_cap": rt.V2_5_FIXED_RADIUS_AGGREGATE_GRAPH_QUERY_COUNT_CAP,
        "graph_query_count_boundary": rt.V2_5_FIXED_RADIUS_AGGREGATE_GRAPH_QUERY_COUNT_BOUNDARY,
        "large_direct_query_count_floor": rt.V2_5_FIXED_RADIUS_AGGREGATE_LARGE_DIRECT_QUERY_COUNT_FLOOR,
        "result_modes": {
            "direct_graph": rt.V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE,
            "full_batch_direct": rt.V2_5_FIXED_RADIUS_AGGREGATE_FULL_BATCH_DIRECT_MODE,
            "same_stream_cupy": rt.V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE,
        },
        "validation": validation,
        "scenario_matrix": {
            key: _plan_summary(plan) for key, plan in scenarios.items()
        },
        "evidence_refs": (
            "Goal2841",
            "Goal4502",
            "docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.json",
        ),
        "claim_boundary": {
            "policy_is_explain_only": True,
            "explicit_result_mode_required": True,
            "hidden_auto_dispatch_allowed": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "release_readiness_authorized": False,
        },
        "conclusion": (
            "The fixed-radius aggregate execution-path policy is now size-aware. "
            "Unknown or small aggregate-only OptiX work keeps the Goal2841 direct graph "
            "recommendation; Phoenix removes the fixed 65,536-query native graph cap, "
            "but explicit large aggregate-only work still uses the measured Goal4502/Phoenix "
            "full-batch prepared direct aggregate recommendation until graph replay has "
            "material large-workload evidence; partner continuations keep the same-stream "
            "graph/device-partial route with an explicit large-workload evidence warning."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    rows = []
    for name, plan in packet["scenario_matrix"].items():
        warnings = "; ".join(plan["warnings"]) if plan["warnings"] else "none"
        rows.append(
            "| {name} | {selected} | `{mode}` | {evidence} | {warnings} |".format(
                name=name,
                selected=plan["selected_path"],
                mode=plan["recommended_result_mode"],
                evidence=plan["evidence_goal"],
                warnings=warnings,
            )
        )
    lines = [
        "# Goal4504 / V3 M108 Execution-Path Policy Refresh",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Scenario Matrix",
        "",
        "| Scenario | Selected path | Recommended result mode | Evidence | Warning |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
        "## Boundary",
        "",
        "- This is explain-only policy, not hidden runtime dispatch.",
        "- Users and benchmark apps still choose explicit result modes.",
        "- Public speedup wording and release-readiness wording remain blocked by this packet.",
        "- Goal4502 supersedes Goal2841 only for explicit large aggregate-only batches; it does not replace the same-stream partner-continuation route.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["validation"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
