#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.v3_0_topology_stream_accounting import (  # noqa: E402
    TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
    TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT,
    TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
    build_topology_stream_phase_accounting,
    compare_author_timer_to_topology_stream,
    compare_topology_stream_accounting,
)


OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
FEASIBILITY = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.json"
M5_DIR = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_m5_topology_20260620"
PIP_SUMMARY = M5_DIR / "m5_pip_point_location_parity_filtered_100k" / "summary.json"
OVERLAY_SUMMARY = M5_DIR / "m5_overlay_active_count_same_contract.json"


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0 if payload["status"] == "spatial_rayjoin_topology_stream_contract_candidate_not_m7" else 2


def build_payload() -> dict[str, Any]:
    feasibility = _read_json(FEASIBILITY)
    pip = _read_json(PIP_SUMMARY)
    overlay = _read_json(OVERLAY_SUMMARY)
    optix_row = pip["rtdl"]["optix"]
    embree_row = pip["rtdl"]["embree"]
    pip_query_count = int(pip["protocol"]["point_count"])
    pip_output_contract = "rayjoin_cdb_point_location_positive_face_count"
    optix_accounting = build_topology_stream_phase_accounting(
        backend="optix",
        output_contract=pip_output_contract,
        query_count=pip_query_count,
        wall_sec=float(optix_row["hot_median_sec"]),
        native_traversal_sec=float(optix_row["native_traversal_median_sec"]),
        repeat=int(optix_row["repeats"]),
        warmup=int(pip["protocol"]["rtdl_warmups"]),
        timer_basis="Python time.perf_counter around prepared.count_positive_faces",
    )
    embree_accounting = build_topology_stream_phase_accounting(
        backend="embree",
        output_contract=pip_output_contract,
        query_count=pip_query_count,
        wall_sec=float(embree_row["hot_median_sec"]),
        native_traversal_sec=float(embree_row["native_traversal_median_sec"]),
        repeat=int(embree_row["repeats"]),
        warmup=int(pip["protocol"]["rtdl_warmups"]),
        timer_basis="Python time.perf_counter around prepared.count_positive_faces",
    )
    pip_comparison = compare_topology_stream_accounting(
        baseline=embree_accounting,
        candidate=optix_accounting,
    )
    author_gap = compare_author_timer_to_topology_stream(
        author_label="RayJoin author query_exec",
        author_query_sec=float(pip["rayjoin_rt"]["query_ms"]) / 1000.0,
        rtdl_accounting=optix_accounting,
        author_timer_basis="query_exec stdout Timing breakdown: Query",
    )
    overlay_rows = {row["backend"]: row for row in overlay["rows"]}
    overlay_optix = overlay_rows["optix"]
    overlay_embree = overlay_rows["embree"]
    overlay_output_contract = str(overlay_optix["output_contract"])
    overlay_optix_accounting = build_topology_stream_phase_accounting(
        backend="optix",
        output_contract=overlay_output_contract,
        query_count=int(overlay["case_shape"]["left_shape_count"]) * int(overlay["case_shape"]["right_shape_count"]),
        wall_sec=float(overlay_optix["timed_median_sec"]),
        native_traversal_sec=float(overlay_optix["native_traversal_median_sec"]),
        repeat=int(overlay_optix["repeat"]),
        warmup=int(overlay_optix["warmup"]),
        timer_basis="Python time.perf_counter around active-count executor.run",
    )
    overlay_embree_accounting = build_topology_stream_phase_accounting(
        backend="embree",
        output_contract=overlay_output_contract,
        query_count=int(overlay["case_shape"]["left_shape_count"]) * int(overlay["case_shape"]["right_shape_count"]),
        wall_sec=float(overlay_embree["timed_median_sec"]),
        native_traversal_sec=float(overlay_embree["native_traversal_median_sec"]),
        repeat=int(overlay_embree["repeat"]),
        warmup=int(overlay_embree["warmup"]),
        timer_basis="Python time.perf_counter around active count",
    )
    overlay_comparison = compare_topology_stream_accounting(
        baseline=overlay_embree_accounting,
        candidate=overlay_optix_accounting,
    )
    checks = {
        "feasibility_keeps_no_m7": feasibility.get("phoenix_m7_qualified_release_rows") == 0,
        "feasibility_blocks_rtdl_beats_rayjoin": feasibility.get("rtdl_beats_rayjoin_claim_authorized") is False,
        "pip_contract_has_exact_parity": int(pip["correctness_sample"]["mismatch_count_first_10_materialized"]) == 0,
        "pip_author_is_faster_than_rtdl_optix_wall": author_gap["author_speedup_vs_rtdl_wall"] > 1.0,
        "pip_rtdl_optix_wall_beats_rtdl_embree": pip_comparison["candidate_over_baseline_wall_speedup"] > 1.0,
        "pip_visible_overhead_is_material": (
            optix_accounting["visible_non_traversal_overhead_fraction_of_wall"] is not None
            and optix_accounting["visible_non_traversal_overhead_fraction_of_wall"] > 0.25
        ),
        "overlay_active_count_same_contract": overlay["comparison"]["same_output_contract"] is True,
        "overlay_not_full_polygon_overlay": (
            overlay["claim_boundary"]["full_polygon_overlay_claim_authorized"] is False
        ),
        "prepared_topology_stream_contracts_named": (
            TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT == "topology_stream_m3_phase_table_v1"
            and TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT == "topology_stream_prepared_handle_v1"
        ),
        "all_release_flags_false": all(
            item.get("release_authorized") is False
            and item.get("public_speedup_claim_authorized") is False
            and item.get("m7_promotion_authorized") is False
            for item in (
                optix_accounting,
                embree_accounting,
                overlay_optix_accounting,
                overlay_embree_accounting,
            )
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "spatial_rayjoin_topology_stream_contract_candidate_not_m7"
    return {
        "tool": "v3_phoenix_spatial_rayjoin_topology_stream_contract",
        "version": "phoenix_v3_spatial_rayjoin_topology_stream_contract_2026_06_21",
        "status": status,
        "generic_capability": "point_location_topology_stream",
        "phase_accounting_contract": TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT,
        "m3_phase_table_contract": TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
        "prepared_handle_contract": TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
        "prepared_handle_interface_status": "local_payload_interface_added_not_pod_performance_closed",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "source_packets": {
            "spatial_rayjoin_m7_feasibility": _rel(FEASIBILITY),
            "m5_pip_summary": _rel(PIP_SUMMARY),
            "m5_overlay_summary": _rel(OVERLAY_SUMMARY),
        },
        "pip_point_location": {
            "contract": pip_output_contract,
            "query_points": pip_query_count,
            "parity_filter_rejected_count": int(pip["parity_filter"]["rejected_count"]),
            "exact_mismatch_count": int(pip["correctness_sample"]["mismatch_count_first_10_materialized"]),
            "optix_accounting": optix_accounting,
            "embree_accounting": embree_accounting,
            "rtdl_optix_vs_embree": pip_comparison,
            "author_gap": author_gap,
            "reading": (
                "RTDL OptiX beats RTDL Embree on the same point-location topology "
                "contract, but RayJoin author RT remains faster and RTDL OptiX still "
                "has material visible non-traversal overhead."
            ),
        },
        "overlay_active_count": {
            "contract": overlay_output_contract,
            "left_shape_count": int(overlay["case_shape"]["left_shape_count"]),
            "right_shape_count": int(overlay["case_shape"]["right_shape_count"]),
            "active_count": int(overlay["comparison"]["active_count"]),
            "optix_accounting": overlay_optix_accounting,
            "embree_accounting": overlay_embree_accounting,
            "rtdl_optix_vs_embree": overlay_comparison,
            "reading": (
                "Overlay active-count is strong internal same-contract topology evidence, "
                "but it is not full polygon overlay and has no author-paper comparison."
            ),
        },
        "m7_blockers_preserved": [
            "rayjoin_author_rt_faster_than_rtdl_optix",
            "mixed_timing_basis_requires_public_methodology_review",
            "m3_phase_table_gap_for_pip_before_public_row",
            "not_full_rayjoin_paper_reproduction",
            "not_full_polygon_overlay_or_materialization",
            "no_future_public_row_2ai_consensus_for_spatial_rayjoin_m7_promotion",
        ],
        "future_public_row_requirements": [
            "Choose one named user contract, not the whole Spatial RayJoin app.",
            "Use one exact dataset path plus a saved query stream with parity-filter provenance.",
            "Report RTDL OptiX and RTDL Embree same-contract wall and native traversal timing.",
            "Use the topology_stream_prepared_handle_v1 payload metadata and topology_stream_m3_phase_table_v1 table emitted by the prepared OptiX route.",
            "When RayJoin author timing is cited, report the author timer basis beside RTDL wall and native traversal basis.",
            "Replace the current partial wall/native accounting with a full M3 phase table: static scene prepare, query stream prepare, device transfer or residency, RT traversal, topology continuation, and host return or scalar materialization.",
            "Keep paper, full overlay, RTDL-beats-RayJoin, and broad V3-over-V2 wording false unless separately proven.",
            "Obtain fresh external public-row review plus Codex consensus before any Spatial RayJoin M7 promotion.",
        ],
        "forbidden_shortcuts": [
            "Do not promote the 1.920x RTDL OptiX/Embree wall ratio without author and M3 phase context.",
            "Do not invert the 5.728x RayJoin-author-over-RTDL-OptiX gap into an RTDL win.",
            "Do not publish the 499x overlay active-count row as full polygon overlay.",
            "Do not mix the tiny 0.034x route-health row with authored hot-route rows without contract labels.",
        ],
        "summary": {
            "m7_rows_added": 0,
            "pip_rtdl_optix_wall_speedup_vs_embree": pip_comparison[
                "candidate_over_baseline_wall_speedup"
            ],
            "pip_rtdl_optix_visible_overhead_fraction": optix_accounting[
                "visible_non_traversal_overhead_fraction_of_wall"
            ],
            "rayjoin_author_speedup_vs_rtdl_optix_wall": author_gap[
                "author_speedup_vs_rtdl_wall"
            ],
            "overlay_active_count_optix_wall_speedup_vs_embree": overlay_comparison[
                "candidate_over_baseline_wall_speedup"
            ],
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Add topology-stream phase accounting for Spatial RayJoin without promoting a row.",
            "was_i_foolish": "No. This exposes the RTDL overhead and author timing gap instead of hiding them behind a same-contract OptiX/Embree win.",
            "foolish_actions": (
                "It would be foolish to quote the 1.920x PIP wall win or 499x overlay active-count win "
                "without also showing that RayJoin author RT is faster and that PIP lacks a full M3 phase table."
            ),
            "other_path": (
                "Tune RayJoin-specific code immediately. That might improve one benchmark, but it would not give "
                "Phoenix a reusable topology-stream accounting contract."
            ),
            "different_path_now": (
                "Use this contract to drive the next public-row runner: reduce visible non-traversal overhead, "
                "collect full M3 phases, and keep author/paper wording blocked until reviewed."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    pip = payload["pip_point_location"]
    overlay = payload["overlay_active_count"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial RayJoin Topology-Stream Contract",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet advances the Spatial RayJoin queue item by making the",
        "`point_location_topology_stream` phase-accounting contract explicit.",
        "It does not promote a new M7 row.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"rtdl_beats_rayjoin_claim_authorized: {str(payload['rtdl_beats_rayjoin_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "Current local prepared OptiX payload interface:",
        "",
        f"- M3 table contract: `{payload['m3_phase_table_contract']}`",
        f"- Prepared handle contract: `{payload['prepared_handle_contract']}`",
        f"- Interface status: `{payload['prepared_handle_interface_status']}`",
        "- This is not POD performance closure and not a public Spatial RayJoin win.",
        "",
        "## PIP Point-Location Accounting",
        "",
        f"- Contract: `{pip['contract']}`",
        f"- Query points: `{pip['query_points']}`",
        f"- Exact mismatches: `{pip['exact_mismatch_count']}`",
        f"- RTDL OptiX / RTDL Embree wall speedup: `{pip['rtdl_optix_vs_embree']['candidate_over_baseline_wall_speedup']:.3f}x`",
        f"- RTDL OptiX visible non-traversal overhead fraction: `{pip['optix_accounting']['visible_non_traversal_overhead_fraction_of_wall']:.3f}`",
        f"- RayJoin author / RTDL OptiX wall speedup: `{pip['author_gap']['author_speedup_vs_rtdl_wall']:.3f}x`",
        f"- RayJoin author / RTDL OptiX native traversal speedup: `{pip['author_gap']['author_speedup_vs_rtdl_native_traversal']:.3f}x`",
        "",
        pip["reading"],
        "",
        "## Overlay Active-Count Accounting",
        "",
        f"- Contract: `{overlay['contract']}`",
        f"- Left/right shapes: `{overlay['left_shape_count']}` / `{overlay['right_shape_count']}`",
        f"- Active count: `{overlay['active_count']}`",
        f"- RTDL OptiX / RTDL Embree wall speedup: `{overlay['rtdl_optix_vs_embree']['candidate_over_baseline_wall_speedup']:.3f}x`",
        "",
        overlay["reading"],
        "",
        "## Preserved M7 Blockers",
        "",
    ]
    lines.extend(f"- `{item}`" for item in payload["m7_blockers_preserved"])
    lines.extend(["", "## Future Public-Row Requirements", ""])
    lines.extend(f"- {item}" for item in payload["future_public_row_requirements"])
    lines.extend(["", "## Forbidden Shortcuts", ""])
    lines.extend(f"- {item}" for item in payload["forbidden_shortcuts"])
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on that idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit Phoenix V3 Spatial RayJoin topology-stream accounting contract."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
