#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_m112_reconciliation_packet_2026-06-21.json"
OUT_MD = OUT_JSON.with_suffix(".md")

RTNN_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_ranked_summary_20260620"
    / "rtnn_ranked_summary_intake_summary.json"
)
WALL_BOUNDARY = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.json"
M104 = ROOT / "docs" / "reports" / "goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.json"
M106 = ROOT / "docs" / "reports" / "goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.json"
M111 = ROOT / "docs" / "reports" / "goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.json"
M112 = ROOT / "docs" / "reports" / "goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the Phoenix V3 RTNN M112 reconciliation packet."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    args = parser.parse_args()

    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "m7_qualified_release_rows": payload["m7_qualified_release_rows"],
                "existing_evidence_promotable_now": payload["existing_evidence_promotable_now"],
                "next_engine_queue_effect": payload["next_engine_queue_effect"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0


def build_payload() -> dict[str, Any]:
    intake = _read_json(RTNN_INTAKE)
    wall = _read_json(WALL_BOUNDARY)
    m104 = _read_json(M104)
    m106 = _read_json(M106)
    m111 = _read_json(M111)
    m112 = _read_json(M112)

    m106_best = m106["rtdl"]["optix_full_batch_direct_aggregate"]
    m106_embree = m106["rtdl"]["m104_generic_embree"]
    m106_generic_optix = m106["rtdl"]["m104_generic_optix"]
    current_wall_ratios = {
        row["distribution"]: float(row["wall_optix_over_embree"])
        for row in wall["rows"]
    }
    hot_ratios = {
        row["distribution"]: float(row["hot_optix_over_embree"])
        for row in wall["rows"]
    }
    partner_rows = {
        row["distribution"]: {
            "chunk_count": int(row["chunk_count"]),
            "cupy_hot_device_run_seconds_median_sum": float(
                row["cupy_hot_device_run_seconds_median_sum"]
            ),
            "numba_hot_device_run_seconds_median_sum": float(
                row["numba_hot_device_run_seconds_median_sum"]
            ),
            "signature_match": bool(row["signature_match"]),
            "hot_no_hidden_column_copy_ready": bool(row["hot_no_hidden_column_copy_ready"]),
        }
        for row in m111["rows"]
    }

    blocking_reasons = [
        "current_65k_raw_summary_wall_timing_regresses",
        "m104_exact_float64_has_tie_sensitive_kth_checksum_mismatch",
        "m106_fastest_full_batch_route_is_float32_and_exact_false",
        "author_same_input_comparison_is_not_same_output_contract",
        "m110_m111_partner_continuation_has_no_same_contract_speed_baseline",
        "paper_dataset_reproduction_not_authorized",
        "fresh_phoenix_m7_review_not_done_for_any_rtnn_row",
    ]
    checks = {
        "intake_not_m7": intake["comparison"]["m7_qualified"] is False,
        "wall_boundary_not_m7": wall["m7_promotion_authorized"] is False,
        "all_current_wall_ratios_below_one": all(value < 1.0 for value in current_wall_ratios.values()),
        "m104_optix_over_embree_material": float(m104["summary"]["optix_over_embree_speedup"]) > 10.0,
        "m104_strict_signature_false": m104["results"]["strict_signature_match"] is False,
        "m104_tie_stable_true": m104["results"]["tie_stable_signature_match"] is True,
        "m106_best_query_material": float(m106_best["median_query_sec"]) < 0.2,
        "m106_best_exact_false": m106_best["contract"]["exact"] is False,
        "m106_author_same_output_false": m106["claim_boundary"]["same_output_contract_author_vs_rtdl"] is False,
        "m111_partner_matrix_no_public_speed": m111["claim_boundary"]["public_speedup_claim_authorized"] is False,
        "m112_public_rt_core_speedup_false": m112["readiness"]["public_rt_core_speedup_claim_ready"] is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]

    return {
        "version": "phoenix_v3_rtnn_m112_reconciliation_2026_06_21",
        "status": "rtnn_m112_reconciled_no_m7_promotion",
        "generic_capability": "ranked_summary",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows": 0,
        "existing_evidence_promotable_now": False,
        "source_packets": {
            "current_intake": _rel(RTNN_INTAKE),
            "current_wall_boundary": _rel(WALL_BOUNDARY),
            "m104_same_input_rtdl_gate": _rel(M104),
            "m106_full_batch_route_refresh": _rel(M106),
            "m111_chunked_distribution_matrix": _rel(M111),
            "m112_clean_target_closeout": _rel(M112),
        },
        "current_65k_raw_summary_boundary": {
            "status": wall["status"],
            "hot_optix_over_embree": hot_ratios,
            "wall_optix_over_embree": current_wall_ratios,
            "all_hot_optix_faster": bool(intake["comparison"]["all_hot_optix_faster_than_embree"]),
            "all_wall_optix_slower": bool(intake["comparison"]["all_wall_optix_slower_than_embree"]),
            "reading": (
                "The small synthetic raw-row ladder is useful boundary evidence: OptiX wins "
                "the isolated hot metric, but wall timing loses for every distribution."
            ),
        },
        "m104_exact_float64_same_input_gate": {
            "dataset": m104["input"]["csv_export"]["paper_label"],
            "point_count": int(m104["input"]["csv_export"]["point_count"]),
            "radius": float(m104["contract"]["radius"]),
            "k_max": int(m104["contract"]["k_max"]),
            "precision": m104["contract"]["precision"],
            "result_mode": m104["contract"]["result_mode"],
            "optix_median_sec": float(m104["results"]["optix"]["payload"]["elapsed_median_sec"]),
            "embree_median_sec": float(m104["results"]["embree"]["payload"]["elapsed_median_sec"]),
            "optix_over_embree_speedup": float(m104["summary"]["optix_over_embree_speedup"]),
            "strict_signature_match": bool(m104["results"]["strict_signature_match"]),
            "tie_stable_signature_match": bool(m104["results"]["tie_stable_signature_match"]),
            "signature_delta": m104["results"]["signature_delta_optix_minus_embree"],
            "m7_reading": (
                "Material same-input RTDL OptiX-vs-Embree evidence, but not M7 until "
                "the tie-sensitive kth checksum policy is reviewed or repaired."
            ),
        },
        "m106_full_batch_aggregate_route": {
            "result_mode": m106_best["result_mode"],
            "precision": m106_best["contract"]["precision"],
            "exact": bool(m106_best["contract"]["exact"]),
            "query_batch_size": int(m106_best["query_batch_size"]),
            "median_query_sec": float(m106_best["median_query_sec"]),
            "cold_load_pack_prepare_query_sec": float(m106_best["cold_load_pack_prepare_query_sec"]),
            "vs_m104_generic_optix_speedup": float(m106["comparisons"]["rtdl_full_batch_over_m104_generic_optix_query"]),
            "vs_m104_embree_speedup": float(m106["comparisons"]["rtdl_full_batch_over_m104_embree_query"]),
            "vs_author_total_search_speedup": float(m106["comparisons"]["rtdl_full_batch_query_over_author_total_search"]),
            "author_compute_over_rtdl_speedup": float(m106["comparisons"]["author_compute_over_rtdl_full_batch_query"]),
            "same_output_contract_author_vs_rtdl": bool(
                m106["claim_boundary"]["same_output_contract_author_vs_rtdl"]
            ),
            "m7_reading": (
                "This is the strongest RTDL aggregate route, but it is float32, exact=false, "
                "and not a same-output author comparison."
            ),
        },
        "m111_partner_continuation": {
            "mode": m111["mode"],
            "rows": partner_rows,
            "all_signature_match": bool(m111["matrix_summary"]["all_signature_match"]),
            "all_hot_no_hidden_column_copy_ready": bool(
                m111["matrix_summary"]["all_hot_no_hidden_column_copy_ready"]
            ),
            "m7_reading": (
                "Real large same-stream partner-continuation runtime evidence, but not an "
                "aggregate-only same-contract speed row."
            ),
        },
        "m112_reconciliation": {
            "internal_clean_target_closed": bool(m112["readiness"]["internal_clean_target_closed"]),
            "public_rt_core_speedup_claim_ready": bool(
                m112["readiness"]["public_rt_core_speedup_claim_ready"]
            ),
            "same_output_author_comparison_ready": bool(
                m112["readiness"]["same_output_author_comparison_ready"]
            ),
            "rtnn_has_real_generic_engine_progress": True,
            "rtnn_has_phoenix_m7_row_now": False,
            "why": (
                "M112 shows the ranked_summary engine has strong large-route progress, but "
                "the current Phoenix M7 bar requires exact row-scoped public wording, strict "
                "or explicitly reviewed parity, and 2-AI review for the exact row."
            ),
        },
        "blocking_reasons": blocking_reasons,
        "next_m7_paths": [
            {
                "id": "rtnn_kitti_exact_tie_stable_aggregate_review",
                "required_evidence": (
                    "Rebuild or rerun the exact float64 same-input aggregate gate with a reviewed "
                    "tie-stable equivalence policy, or repair the kth checksum mismatch."
                ),
                "can_use_existing_evidence_directly": False,
            },
            {
                "id": "rtnn_full_batch_float32_same_contract_m7_rerun",
                "required_evidence": (
                    "Run a focused same-contract float32 aggregate packet with CPU/reference parity, "
                    "phase/wall timing, source manifest, and 2-AI review."
                ),
                "can_use_existing_evidence_directly": False,
            },
        ],
        "next_engine_queue_effect": (
            "Keep `rtnn_ranked_summary_wall_path` open, but refine it: old M112 evidence proves "
            "a large aggregate route exists, while M7 still needs tie/parity or float32 same-contract repair."
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Reconcile RTNN M112 clean-target evidence with the Phoenix M7 bar without promoting RTNN.",
            "was_i_foolish": "No. This prevents both under-reading M112 and overclaiming it as V3 release evidence.",
            "foolish_actions": (
                "It would be foolish to use the M106 787.53x-vs-Embree figure as a public RTNN row "
                "while ignoring float32/exact=false and same-output-contract blockers."
            ),
            "other_path": (
                "Declare RTNN solved from M112 or leave the wall-time regression packet alone. "
                "Either path loses key evidence."
            ),
            "different_path_now": (
                "Keep RTNN in the engine queue with a narrower next action: exact tie-stable aggregate "
                "review or float32 same-contract rerun."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    current = payload["current_65k_raw_summary_boundary"]
    m104 = payload["m104_exact_float64_same_input_gate"]
    m106 = payload["m106_full_batch_aggregate_route"]
    m111 = payload["m111_partner_continuation"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 RTNN M112 Reconciliation Packet",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet reconciles the earlier M104-M112 RTNN clean-target work with",
        "the stricter Phoenix V3 M7 release bar. It is not release authorization",
        "and it promotes zero RTNN rows.",
        "",
        "## Bottom Line",
        "",
        "RTNN has real generic ranked_summary engine progress, but no Phoenix M7",
        "row is promoted from the current evidence. The small 65k raw-row ladder",
        "has wall-time regression; the large KITTI aggregate route is strong but",
        "blocked by tie/parity and precision/output-contract boundaries.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"Phoenix M7-qualified release rows from this packet: {payload['m7_qualified_release_rows']}",
        "```",
        "",
        "## Evidence Reconciliation",
        "",
        "| Evidence | Strong fact | Blocking fact | Reading |",
        "| --- | --- | --- | --- |",
        (
            "| Current 65k raw summary | Hot OptiX/Embree: "
            f"clustered {current['hot_optix_over_embree']['clustered']:.3f}x, "
            f"shell {current['hot_optix_over_embree']['shell']:.3f}x, "
            f"uniform {current['hot_optix_over_embree']['uniform']:.3f}x | "
            "Wall ratios are all below 1.0 | Boundary evidence only. |"
        ),
        (
            "| M104 exact float64 KITTI same-input gate | "
            f"OptiX/Embree {m104['optix_over_embree_speedup']:.3f}x on 1,000,000 points | "
            "strict kth checksum mismatch; tie-stable only | Candidate needs tie policy review or repair. |"
        ),
        (
            "| M106 full-batch aggregate | "
            f"{m106['median_query_sec']:.6f}s hot query; "
            f"{m106['vs_m104_embree_speedup']:.3f}x vs M104 Embree | "
            "float32, exact=false, not same-output with author RTNN | Strong engine route, not M7 today. |"
        ),
        (
            "| M111 partner continuation | "
            f"uniform CuPy {m111['rows']['uniform']['cupy_hot_device_run_seconds_median_sum']:.6f}s; "
            f"clustered CuPy {m111['rows']['clustered']['cupy_hot_device_run_seconds_median_sum']:.6f}s | "
            "no same-contract speed baseline | Runtime evidence, not public speed row. |"
        ),
        "",
        "## Why No M7 Promotion",
        "",
    ]
    for reason in payload["blocking_reasons"]:
        lines.append(f"- `{reason}`")
    lines.extend(
        [
            "",
            "## Next M7 Paths",
            "",
        ]
    )
    for path in payload["next_m7_paths"]:
        lines.extend(
            [
                f"### {path['id']}",
                "",
                path["required_evidence"],
                "",
                f"`can_use_existing_evidence_directly: {str(path['can_use_existing_evidence_directly']).lower()}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Queue Effect",
            "",
            payload["next_engine_queue_effect"],
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
