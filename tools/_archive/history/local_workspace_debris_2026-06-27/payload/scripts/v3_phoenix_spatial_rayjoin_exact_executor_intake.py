#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXACT_EXECUTOR_SUMMARY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621"
    / "summary.json"
)
DEVICE_FILTERED_REJECTED_LOG = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621"
    / "run.log"
)
M5_TOPOLOGY_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m5_topology_20260620"
    / "m5_topology_intake_summary.json"
)
M3_GAP_ANALYSIS = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json"
)


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(text + "\n", encoding="utf-8")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(text)
    return 0 if not payload["failed_checks"] else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 Spatial RayJoin exact-executor intake packet."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT
        / "docs"
        / "rebuild"
        / "v3"
        / "phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.json",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=ROOT
        / "docs"
        / "rebuild"
        / "v3"
        / "phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.md",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_payload() -> dict[str, Any]:
    exact = _load_json(EXACT_EXECUTOR_SUMMARY)
    m5 = _load_json(M5_TOPOLOGY_INTAKE)
    gap = _load_json(M3_GAP_ANALYSIS)
    rejected_log = DEVICE_FILTERED_REJECTED_LOG.read_text(encoding="utf-8")

    summary = exact["summary"]
    m3 = summary["m3_phase_sec_medians"]
    rt_traversal = float(m3["rt_traversal_sec"])
    topology_continuation = float(m3["topology_continuation_sec"])
    prepared_query = float(summary["prepared_query_sec_median"])
    query_stream_prepare = float(m3["query_stream_prepare_sec"])
    static_scene_prepare = float(m3["static_scene_prepare_sec"])
    host_return = float(m3["host_return_or_scalar_materialization_sec"])
    device_transfer = float(m3["device_transfer_or_residency_sec"])
    continuation_over_traversal = _safe_ratio(topology_continuation, rt_traversal)
    continuation_fraction = _safe_ratio(topology_continuation, prepared_query)
    traversal_fraction = _safe_ratio(rt_traversal, prepared_query)

    m5_metrics = m5["metrics"]
    prior_author_gap = {
        "scope": "prior_100k_same_stream_author_comparison_not_direct_public_county_packet",
        "query_count": int(m5_metrics["pip_point_count"]),
        "rayjoin_rt_speedup_vs_rtdl_optix_native_traversal": float(
            m5_metrics["pip_rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"]
        ),
        "rtdl_optix_speedup_vs_rtdl_embree": float(
            m5_metrics["pip_rtdl_optix_speedup_vs_rtdl_embree"]
        ),
        "methodology_note": m5["comparison_methodology"]["timing_basis_note"],
        "direct_current_packet_comparison_authorized": False,
    }

    checks = {
        "exact_executor_packet_passed": (
            exact.get("status") == "spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7"
            and exact.get("failed_checks") == []
        ),
        "exact_executor_not_m7": (
            exact.get("m7_promotion_authorized") is False
            and exact.get("m7_qualified_release_rows_added") == 0
        ),
        "all_public_claim_flags_false": all(
            exact.get(flag) is False
            for flag in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "row_scoped_public_speedup_claim_authorized",
                "rtdl_beats_rayjoin_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "true_zero_copy_claim_authorized",
                "v4_embedding_claim_authorized",
            )
        ),
        "full_m3_table_present": bool(summary["full_m3_phase_table_complete_all_samples"]),
        "row_count_stable": bool(summary["row_count_consistent"]) and int(summary["row_count"]) == 47262,
        "query_stream_reusable_executor_residency": (
            summary["query_stream_residency"]
            == "device_resident_prepared_point_probe_columns_with_reusable_exact_executor"
        ),
        "device_filtered_rejection_recorded": "47570 != 47262" in rejected_log,
        "continuation_dominates_traversal": continuation_over_traversal is not None
        and continuation_over_traversal > 10.0,
        "author_gap_is_prior_not_direct_current_packet": (
            prior_author_gap["direct_current_packet_comparison_authorized"] is False
            and "not_direct_public_county" in prior_author_gap["scope"]
        ),
        "m3_gap_kept_not_m7": (
            gap.get("status") == "spatial_rayjoin_m3_gap_analysis_not_m7"
            and gap.get("m7_promotion_authorized") is False
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]

    return {
        "tool": "v3_phoenix_spatial_rayjoin_exact_executor_intake",
        "status": "fail" if failed_checks else "spatial_rayjoin_exact_executor_intake_not_m7",
        "generic_capability": "point_location_topology_stream",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "exact_executor_packet": {
            "source": _rel(EXACT_EXECUTOR_SUMMARY),
            "dataset": exact["dataset"],
            "gpu": exact["environment"]["nvidia_smi"],
            "count_mode": exact["count_mode"],
            "point_order_mode": exact["point_order_mode"],
            "sample_repeat": int(exact["sample_repeat"]),
            "query_repeat": int(exact["query_repeat"]),
            "warmup": int(exact["warmup"]),
            "row_count": int(summary["row_count"]),
            "failed_checks": exact["failed_checks"],
            "query_stream_residency": summary["query_stream_residency"],
            "prepared_query_sec_median": prepared_query,
            "prepared_query_total_sec_median": float(summary["prepared_query_total_sec_median"]),
            "runner_wall_sec_median": float(summary["runner_wall_sec_median"]),
        },
        "m3_bottleneck": {
            "static_scene_prepare_sec_median": static_scene_prepare,
            "query_stream_prepare_sec_median": query_stream_prepare,
            "device_transfer_or_residency_sec_median": device_transfer,
            "rt_traversal_or_candidate_emission_sec_median": rt_traversal,
            "topology_continuation_exact_refine_sec_median": topology_continuation,
            "host_return_or_scalar_materialization_sec_median": host_return,
            "topology_continuation_over_rt_traversal": continuation_over_traversal,
            "topology_continuation_fraction_of_prepared_query": continuation_fraction,
            "rt_traversal_fraction_of_prepared_query": traversal_fraction,
            "reading": (
                "The reusable executor keeps query columns resident and removes device-transfer cost, "
                "but the hot path is dominated by exact topology continuation/refinement, not RT traversal."
            ),
        },
        "rejected_device_filtered_probe": {
            "source": _rel(DEVICE_FILTERED_REJECTED_LOG),
            "status": "rejected_exact_count_mismatch",
            "exact_count": 47262,
            "device_filtered_count": 47570,
            "publishable_fast_route": False,
        },
        "prior_author_gap": prior_author_gap,
        "next_engine_actions": [
            "Move exact closed-shape membership/refinement work out of host GEOS/refine loops where a generic exact device continuation is possible.",
            "Keep the executor capacity policy explicit and fail-closed on overflow.",
            "Only compare to RayJoin author timing in a same-dataset packet with the timer basis printed beside RTDL wall and native/M3 phases.",
            "Seek external review before any Spatial RayJoin M7 wording.",
        ],
        "forbidden_shortcuts": [
            "Do not treat the public-county exact-executor packet as RayJoin-author comparison evidence.",
            "Do not publish the rejected device-filtered route.",
            "Do not call prepared point-column residency true zero-copy.",
            "Do not promote Spatial RayJoin to M7 without same-contract author-basis review.",
        ],
        "source_packets": {
            "exact_executor_summary": _rel(EXACT_EXECUTOR_SUMMARY),
            "device_filtered_rejected_log": _rel(DEVICE_FILTERED_REJECTED_LOG),
            "m5_author_gap": _rel(M5_TOPOLOGY_INTAKE),
            "m3_gap_analysis": _rel(M3_GAP_ANALYSIS),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Convert the Spatial exact-executor POD result into a not-M7 intake packet "
                "that identifies the generic topology-continuation bottleneck."
            ),
            "was_i_foolish": (
                "No. The packet prevents a fresh full-M3 POD result from being mistaken "
                "for an author comparison or public speedup row."
            ),
            "foolish_actions": (
                "The foolish action would be to quote the executor result as RTDL beating RayJoin, "
                "or to hide that exact refinement dominates the prepared query."
            ),
            "other_path": (
                "Run more Spatial app timings immediately. That could add numbers, but it would not "
                "clarify the generic engine bottleneck or release boundary."
            ),
            "different_path_now": (
                "Use the intake to drive generic exact topology-continuation work, then rerun a same-dataset "
                "author-basis packet before any M7 review."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    exact = payload["exact_executor_packet"]
    m3 = payload["m3_bottleneck"]
    author = payload["prior_author_gap"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial RayJoin Exact-Executor Intake",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This is a generic-engine intake packet for `point_location_topology_stream`.",
        "Spatial RayJoin is the evidence harness, not the product boundary.",
        "",
        "## Current POD Packet",
        "",
        f"- Source: `{exact['source']}`",
        f"- Dataset: `{exact['dataset']}`",
        f"- GPU: `{exact['gpu']}`",
        f"- Count mode: `{exact['count_mode']}`",
        f"- Repeat protocol: sample_repeat={exact['sample_repeat']}, query_repeat={exact['query_repeat']}, warmup={exact['warmup']}",
        f"- Stable exact row count: `{exact['row_count']}`",
        f"- Failed checks: `{exact['failed_checks']}`",
        f"- Query stream residency: `{exact['query_stream_residency']}`",
        "",
        "## M3 Bottleneck Reading",
        "",
        "| Phase | Median seconds |",
        "| --- | ---: |",
        f"| static scene prepare | {m3['static_scene_prepare_sec_median']} |",
        f"| query stream prepare | {m3['query_stream_prepare_sec_median']} |",
        f"| device transfer/residency | {m3['device_transfer_or_residency_sec_median']} |",
        f"| RT traversal/candidate emission | {m3['rt_traversal_or_candidate_emission_sec_median']} |",
        f"| topology continuation/exact refine | {m3['topology_continuation_exact_refine_sec_median']} |",
        f"| host return/scalar materialization | {m3['host_return_or_scalar_materialization_sec_median']} |",
        "",
        f"Topology continuation / RT traversal: `{m3['topology_continuation_over_rt_traversal']}`.",
        f"Topology continuation fraction of prepared query: `{m3['topology_continuation_fraction_of_prepared_query']}`.",
        "",
        m3["reading"],
        "",
        "## Rejected Probe",
        "",
        "The device-filtered route remains rejected:",
        "",
        f"- Source: `{payload['rejected_device_filtered_probe']['source']}`",
        f"- Device-filtered count: `{payload['rejected_device_filtered_probe']['device_filtered_count']}`",
        f"- Exact count: `{payload['rejected_device_filtered_probe']['exact_count']}`",
        "",
        "## Author Gap Boundary",
        "",
        f"- Scope: `{author['scope']}`",
        f"- Prior RayJoin author / RTDL native traversal speedup: `{author['rayjoin_rt_speedup_vs_rtdl_optix_native_traversal']}`",
        f"- Direct current-packet comparison authorized: `{str(author['direct_current_packet_comparison_authorized']).lower()}`",
        "",
        "This author gap is a carried-forward boundary from the prior M5 same-stream packet,",
        "not a direct comparison against the public-county exact-executor packet.",
        "",
        "## Claim Boundary",
        "",
        f"- `release_authorized: {str(payload['release_authorized']).lower()}`",
        f"- `public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}`",
        f"- `rtdl_beats_rayjoin_claim_authorized: {str(payload['rtdl_beats_rayjoin_claim_authorized']).lower()}`",
        f"- `true_zero_copy_claim_authorized: {str(payload['true_zero_copy_claim_authorized']).lower()}`",
        f"- `m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}`",
        f"- `m7_qualified_release_rows_added: {payload['m7_qualified_release_rows_added']}`",
        "",
        "## Next Engine Actions",
        "",
    ]
    for action in payload["next_engine_actions"]:
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Forbidden Shortcuts",
            "",
        ]
    )
    for shortcut in payload["forbidden_shortcuts"]:
        lines.append(f"- {shortcut}")
    lines.extend(
        [
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on one idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return float(numerator) / float(denominator)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
