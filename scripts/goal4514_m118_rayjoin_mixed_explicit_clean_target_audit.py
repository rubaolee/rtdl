from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rayjoin_mixed_explicit_clean_target_audit.goal4514.v1"
OUT_JSON = Path("docs/reports/goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_2026-06-17.md")

AUTHOR_PACKET = Path("docs/reports/goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.json")
HUMAN_SCALE_PACKET = Path(
    "docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/"
    "human_scale_same_contract/summary.json"
)
SECTION57_OVERLAY_PACKET = Path(
    "docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/"
    "rayjoin_section57_overlay/section57_overlay_summary.json"
)
OVERLAY_ACTIVE_COUNT_PACKET = Path(
    "docs/reports/goal4430_v3_0_m33_rayjoin_overlay_active_count_same_contract_2026-06-16.json"
)
PIP_GRAPH_PACKET = Path("docs/reports/goal4451_v3_0_m55_rayjoin_pip_graph_fail_closed_2026-06-16.json")


def _read_json(root: Path, relative: Path) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _route_summary() -> dict[str, Any]:
    route = rt.explain_current_benchmark_route("spatial_rayjoin")
    return {
        "app": "spatial_rayjoin",
        "route_version": route["version"],
        "decision_kind": route["decision_kind"],
        "primary_route": route["primary_route"],
        "primitive_contract": route["primitive_contract"],
        "partner_policy": route["partner_policy"],
        "current_reader_decision": route["current_reader_decision"],
        "user_choice_guidance": route["user_choice_guidance"],
        "next_runtime_action": route["next_runtime_action"],
        "evidence_refs": list(route["evidence_refs"]),
        "pod_needed_next": bool(route["pod_needed_next"]),
        "public_speedup_claim_authorized": bool(route["public_speedup_claim_authorized"]),
        "whole_app_speedup_claim_authorized": bool(route["whole_app_speedup_claim_authorized"]),
        "broad_rt_core_claim_authorized": bool(route["broad_rt_core_claim_authorized"]),
        "automatic_partner_selection_authorized": bool(
            route["automatic_partner_selection_authorized"]
        ),
        "app_specific_native_engine_logic_allowed": bool(
            route["app_specific_native_engine_logic_allowed"]
        ),
    }


def _representative_route_matrix() -> list[dict[str, Any]]:
    return [
        {
            "contract": "PIP one-shot scalar count",
            "recommended_route": "Numba CUDA JIT scalar count",
            "rtdl_optix_vs_numba": 0.230,
            "reading": "bounded one-shot PIP favors Numba, not current RTDL/OptiX",
            "source": "Goal4039",
        },
        {
            "contract": "PIP repeated-request scalar count",
            "recommended_route": "RTDL/OptiX prepared point/closed-shape batch executor",
            "median_ms_per_request_at_100_requests": 0.145265,
            "reading": "use batch executor; do not use quarantined CUDA graph replay",
            "source": "Goal4039 and Goal4451",
        },
        {
            "contract": "LSI scalar count",
            "recommended_route": "RTDL/OptiX prepared segment-pair count",
            "rtdl_optix_vs_numba": 262.393,
            "reading": "strong RTDL/OptiX-favorable route",
            "source": "Goal4039",
        },
        {
            "contract": "Overlay active count",
            "recommended_route": "RTDL/OptiX prepared shape-pair active count",
            "rtdl_optix_vs_numba": 210.183,
            "reading": "strong RTDL/OptiX-favorable active-count route",
            "source": "Goal4039",
        },
    ]


def _author_comparison(root: Path) -> dict[str, Any]:
    packet = _read_json(root, AUTHOR_PACKET)
    rows = {
        f"{row['workload']}:{row['rtdl_backend']}": {
            "workload": row["workload"],
            "rtdl_backend": row["rtdl_backend"],
            "rayjoin_rt_query_ms": row["rayjoin_rt_query_ms"],
            "rtdl_hot_query_ms": row["rtdl_hot_query_ms"],
            "rayjoin_rt_over_rtdl": row["rayjoin_rt_over_rtdl"],
            "readout": row["readout"],
        }
        for row in packet["direct_comparison"]
    }
    return {
        "source": str(AUTHOR_PACKET),
        "status": "accepted_internal_scalar_count_only",
        "claim_boundary": packet["claim_boundary"],
        "direction_rule": "greater_than_1_means_rtdl_backend_faster_than_rayjoin_rt",
        "direct_comparison": rows,
        "interpretation": packet["interpretation"],
    }


def _human_scale_rows(root: Path) -> dict[str, Any]:
    packet = _read_json(root, HUMAN_SCALE_PACKET)
    rows = {row["app"]: row for row in packet["rows"]}
    wanted = {}
    for app in ("spatial_rayjoin_lsi", "spatial_rayjoin_pip"):
        row = rows[app]
        wanted[app] = {
            "contract": row["contract"],
            "correct": row["correct"],
            "timing_protocol": row["timing_protocol"],
            "optix_total_sec": row["optix_total_sec"],
            "embree_total_sec": row["embree_total_sec"],
            "optix_per_iter_sec": row["optix_per_iter_sec"],
            "embree_per_iter_sec": row["embree_per_iter_sec"],
            "speedup_embree_per_iter_div_optix_per_iter": row[
                "speedup_embree_per_iter_div_optix_per_iter"
            ],
            "reasonability_verdict": row["reasonability_verdict"],
            "public_wording": row["public_wording"],
            "scope": row["scope"],
        }
    return {
        "source": str(HUMAN_SCALE_PACKET),
        "rows": wanted,
        "timing_basis": packet["methodology"],
    }


def _section57_overlay(root: Path) -> dict[str, Any]:
    packet = _read_json(root, SECTION57_OVERLAY_PACKET)
    complete_rows = []
    for row in packet["rows"]:
        if not row["complete"]:
            continue
        speedup = row["rtdl_embree_total_sec"] / row["rtdl_optix_total_sec"]
        complete_rows.append(
            {
                "pair_id": row["pair_id"],
                "paper_label": row["paper_label"],
                "author_rt_process_sec": row["author_rt_process_sec"],
                "rtdl_optix_total_sec": row["rtdl_optix_total_sec"],
                "rtdl_embree_total_sec": row["rtdl_embree_total_sec"],
                "optix_vs_embree_total_speedup": speedup,
                "lsi_counts_match": row["rtdl_optix_lsi_count"] == row["rtdl_embree_lsi_count"],
            }
        )
    return {
        "source": str(SECTION57_OVERLAY_PACKET),
        "coverage": packet["coverage"],
        "complete_rows": complete_rows,
        "timing_caveat": packet["timing_caveat"],
        "full_section57_reproduction_claim_authorized": False,
    }


def _overlay_active_count(root: Path) -> dict[str, Any]:
    packet = _read_json(root, OVERLAY_ACTIVE_COUNT_PACKET)
    return {
        "source": str(OVERLAY_ACTIVE_COUNT_PACKET),
        "contract": packet["planned"]["output_contract"],
        "active_count": packet["comparison"]["active_count"],
        "active_counts_match": packet["comparison"]["active_counts_match"],
        "same_output_contract": packet["comparison"]["same_output_contract"],
        "row_materialization_avoided": packet["comparison"]["all_row_materialization_avoided"],
        "optix_speedup_by_timed_median": packet["comparison"]["embree_over_optix_timed_median"],
        "public_speedup_claim_authorized": packet["claim_boundary"][
            "public_speedup_claim_authorized"
        ],
        "full_polygon_overlay_claim_authorized": packet["claim_boundary"][
            "full_polygon_overlay_claim_authorized"
        ],
    }


def _pip_graph_status(root: Path) -> dict[str, Any]:
    packet = _read_json(root, PIP_GRAPH_PACKET)
    return {
        "source": str(PIP_GRAPH_PACKET),
        "single_count": packet["single_count"],
        "batch_counts": packet["batch_counts"],
        "executor_counts": packet["executor_counts"],
        "unvalidated_graph_status": packet["unvalidated_graph_status"],
        "validated_graph_status": packet["validated_graph_status"],
        "recommended_repeated_pip_path": "prepared point/closed-shape batch executor",
        "graph_replay_current_path": False,
        "claim_boundary": packet["claim_boundary"],
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    route = _route_summary()
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4514 / V3 M118",
        "app": "spatial_rayjoin",
        "route": route,
        "representative_route_matrix": _representative_route_matrix(),
        "author_comparison": _author_comparison(root),
        "human_scale_optix_vs_embree": _human_scale_rows(root),
        "section57_overlay": _section57_overlay(root),
        "overlay_active_count_same_contract": _overlay_active_count(root),
        "pip_graph_status": _pip_graph_status(root),
        "m113_applicability": {
            "current_route_should_use_m113": False,
            "reason": (
                "Spatial RayJoin uses explicit prepared PIP batch execution and "
                "prepared scalar/active-count primitives. The unsafe PIP CUDA graph "
                "replay path is quarantined after Goal4451, and M113 prepared graph "
                "chunk execution is not the current promoted RayJoin route."
            ),
        },
        "readiness": {
            "internal_v3_mixed_explicit_target_closed": True,
            "full_rayjoin_paper_reproduction_claim_authorized": False,
            "full_section57_8_of_8_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Spatial RayJoin is closed as a V3 mixed-explicit clean target, not as "
            "a primitive-only or public-speedup app. Use Numba for bounded PIP "
            "one-shot, RTDL/OptiX prepared batch execution for repeated PIP, and "
            "RTDL/OptiX prepared scalar/active-count primitives for LSI and overlay "
            "active count. The authors-code comparison remains scalar-count-only: "
            "RTDL/OptiX wins LSI, RayJoin RT wins PIP, and full RayJoin paper "
            "reproduction plus Section 5.7 8/8 overlay wording remain blocked."
        ),
    }
    return packet


def write_report(packet: dict[str, Any], path: Path) -> None:
    route = packet["route"]
    lines = [
        "# Goal4514 / V3 M118 RayJoin Mixed-Explicit Clean-Target Audit",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Current Route",
        "",
        f"- Decision: `{route['decision_kind']}`.",
        f"- Partner policy: `{route['partner_policy']}`.",
        f"- Primitive contract: `{route['primitive_contract']}`.",
        f"- Reader decision: {route['current_reader_decision']}",
        f"- User guidance: {route['user_choice_guidance']}",
        f"- M113 reading: {packet['m113_applicability']['reason']}",
        "",
        "## Recommended Route Matrix",
        "",
        "| Contract | Recommended route | Key evidence | Reading |",
        "| --- | --- | ---: | --- |",
    ]
    for row in packet["representative_route_matrix"]:
        if "rtdl_optix_vs_numba" in row:
            metric = f"{row['rtdl_optix_vs_numba']}x RTDL/OptiX vs Numba"
        else:
            metric = f"{row['median_ms_per_request_at_100_requests']} ms/request"
        lines.append(
            f"| {row['contract']} | {row['recommended_route']} | {metric} | {row['reading']} |"
        )

    author_rows = packet["author_comparison"]["direct_comparison"]
    lines.extend(
        [
            "",
            "## Authors-Code Scalar-Count Comparison",
            "",
            "| Workload/backend | RayJoin RT query ms | RTDL hot query ms | RayJoin RT / RTDL | Readout |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for key in ("lsi:optix", "lsi:embree", "pip:optix", "pip:embree"):
        row = author_rows[key]
        lines.append(
            f"| {key} | {row['rayjoin_rt_query_ms']} | {row['rtdl_hot_query_ms']} | "
            f"{row['rayjoin_rt_over_rtdl']}x | {row['readout']} |"
        )

    human_rows = packet["human_scale_optix_vs_embree"]["rows"]
    lines.extend(
        [
            "",
            "## RTDL OptiX vs RTDL Embree",
            "",
            "| Row | Contract | Speedup | Reading |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for key in ("spatial_rayjoin_lsi", "spatial_rayjoin_pip"):
        row = human_rows[key]
        lines.append(
            f"| {key} | {row['contract']} | "
            f"{row['speedup_embree_per_iter_div_optix_per_iter']:.2f}x | "
            f"{row['public_wording']} |"
        )

    overlay = packet["section57_overlay"]
    lines.extend(
        [
            "",
            "## Section 5.7 Overlay Boundary",
            "",
            f"- Complete overlay pairs: {overlay['coverage']['overlay_pairs_complete']}/"
            f"{overlay['coverage']['overlay_pairs_total']}.",
            f"- Incomplete overlay pairs: {overlay['coverage']['overlay_pairs_incomplete']}/"
            f"{overlay['coverage']['overlay_pairs_total']}.",
            f"- Timing caveat: {overlay['timing_caveat']}",
            "",
            "| Pair | RTDL OptiX total sec | RTDL Embree total sec | OptiX-vs-Embree | Count match |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in overlay["complete_rows"]:
        lines.append(
            f"| {row['paper_label']} | {row['rtdl_optix_total_sec']:.4f} | "
            f"{row['rtdl_embree_total_sec']:.4f} | "
            f"{row['optix_vs_embree_total_speedup']:.2f}x | {row['lsi_counts_match']} |"
        )

    active = packet["overlay_active_count_same_contract"]
    graph = packet["pip_graph_status"]
    lines.extend(
        [
            "",
            "## Cleanup Decisions",
            "",
            f"- Overlay active-count same-contract row: active count {active['active_count']}, "
            f"counts match `{active['active_counts_match']}`, row materialization avoided "
            f"`{active['row_materialization_avoided']}`.",
            f"- PIP graph replay: unvalidated `{graph['unvalidated_graph_status']}`, "
            f"validated `{graph['validated_graph_status']}`; use the batch executor.",
            "- No public speedup, full RayJoin reproduction, whole-app, automatic partner, "
            "or app-specific native-engine claim is authorized by this packet.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["readiness"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
