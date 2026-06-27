#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RERANK = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m6_barnes_hut_20260620"
    / "m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json"
)
SMOKE = ROOT / "docs" / "reports" / "goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_smoke_2026-06-16.json"
REPORT = ROOT / "docs" / "reports" / "goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_2026-06-16.md"
SOURCE = ROOT / "src" / "rtdsl" / "app_reference" / "aggregate_force_math.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SAME_BASIS_NO_GO = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.json"
)
DEFAULT_JSON_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.json"
)
DEFAULT_MD_OUT = DEFAULT_JSON_OUT.with_suffix(".md")

CONTRACT = "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1"
CANDIDATE_ROW_ID = "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def _ms(seconds: float | None) -> float | None:
    if seconds is None:
        return None
    return round(float(seconds) * 1000.0, 6)


def _route_rows(source: dict[str, Any]) -> dict[int, dict[str, dict[str, Any]]]:
    by_body: dict[int, dict[str, dict[str, Any]]] = {}
    for row in source.get("rows", []):
        by_body.setdefault(int(row["body_count"]), {})[str(row["route_id"])] = dict(row)
    return by_body


def _source_class_block() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index("class PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda")
    end = source.index("def prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda", start)
    return source[start:end]


def _large_row_summary(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for body_count, by_route in sorted(_route_rows(source).items()):
        gpu = by_route["numba_cuda_fused"]
        cpu = by_route["cpu_numba_fused"]
        optix = by_route["optix_numba_prepared_frontier"]
        gpu_seconds = float(gpu["repeat_seconds_median"])
        cpu_seconds = float(cpu["repeat_seconds_median"])
        optix_seconds = float(optix["repeat_seconds_median"])
        rows.append(
            {
                "body_count": body_count,
                "candidate_route_id": "numba_cuda_fused",
                "candidate_wall_repeat_seconds": gpu_seconds,
                "candidate_wall_repeat_ms": _ms(gpu_seconds),
                "cpu_numba_fused_wall_repeat_ms": _ms(cpu_seconds),
                "prepared_optix_numba_wall_repeat_ms": _ms(optix_seconds),
                "cpu_numba_fused_over_candidate": cpu_seconds / gpu_seconds,
                "prepared_optix_numba_over_candidate": optix_seconds / gpu_seconds,
                "contribution_row_count": int(gpu["contribution_row_count"]),
                "aggregate_contribution_row_count": int(gpu["aggregate_contribution_row_count"]),
                "exact_contribution_row_count": int(gpu["exact_contribution_row_count"]),
                "frontier_rows_materialized_on_host": gpu["frontier_rows_materialized_on_host"],
                "contribution_rows_materialized_on_host": gpu["contribution_rows_materialized_on_host"],
                "rt_cores_used": gpu["rt_cores_used"],
                "rt_core_speedup_claim_authorized": gpu["rt_core_speedup_claim_authorized"],
                "public_speedup_claim_authorized": gpu["public_speedup_claim_authorized"],
                "validation": dict(gpu.get("validation", {})),
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    source = _read_json(RERANK)
    smoke = _read_json(SMOKE)
    same_basis = _read_json(SAME_BASIS_NO_GO)
    metadata = dict(smoke["hot_run_metadata"])
    validation = dict(smoke["validation"])
    class_block = _source_class_block()
    init_text = INIT.read_text(encoding="utf-8")
    report_text = REPORT.read_text(encoding="utf-8")
    large_rows = _large_row_summary(source)
    candidate_131072 = next(row for row in large_rows if int(row["body_count"]) == 131072)
    cpu_speedups = [float(row["cpu_numba_fused_over_candidate"]) for row in large_rows]
    optix_speedups = [float(row["prepared_optix_numba_over_candidate"]) for row in large_rows]
    checks = {
        "rerank_exists": RERANK.exists(),
        "same_basis_no_go_exists": SAME_BASIS_NO_GO.exists(),
        "same_basis_no_go_status": same_basis.get("status")
        == "barnes_hut_same_basis_no_go_current_frontier_shape_not_m7",
        "smoke_exists": SMOKE.exists(),
        "report_exists": REPORT.exists(),
        "contract_matches": metadata.get("contract") == CONTRACT,
        "small_smoke_exact_cpu_reference_passed": validation.get("passed") is True,
        "small_smoke_reference_is_cpu_frontier_sum": validation.get("compared_against")
        == "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
        "source_exports_prepared_class": "PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda" in class_block,
        "source_class_block_is_app_agnostic": "Barnes-Hut" not in class_block and "barnes_hut" not in class_block,
        "init_exports_prepare_api": "prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda" in init_text,
        "init_exports_sum_api": "sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda" in init_text,
        "report_records_reusable_api": "prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda" in report_text,
        "large_rows_all_no_frontier_materialization": all(
            row["frontier_rows_materialized_on_host"] is False for row in large_rows
        ),
        "large_rows_all_no_contribution_materialization": all(
            row["contribution_rows_materialized_on_host"] is False for row in large_rows
        ),
        "large_rows_all_no_rt_core_claim": all(row["rt_core_speedup_claim_authorized"] is False for row in large_rows),
        "large_rows_all_no_public_claim": all(row["public_speedup_claim_authorized"] is False for row in large_rows),
        "large_rows_all_no_rt_cores_used": all(row["rt_cores_used"] is False for row in large_rows),
        "large_repeat_floor": int(source.get("repeat", 0)) >= 11,
        "large_warmup_floor": int(source.get("warmup", 0)) >= 2,
        "candidate_faster_than_cpu_numba_all_scales": min(cpu_speedups) > 3.0,
        "candidate_faster_than_current_optix_frontier_all_scales": min(optix_speedups) > 4.0,
        "candidate_131072_is_serious_scale": int(candidate_131072["body_count"]) == 131072
        and int(candidate_131072["contribution_row_count"]) > 60_000_000,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = "aggregate_tree_fused_partner_m7_candidate_pending_external_review" if not failed_checks else "fail"
    blockers = [
        "external_ai_review_not_done_for_candidate_row",
        "large-row validation is route parity plus checksums; independent exact-force CPU oracle is not claimed",
        "candidate is a Numba CUDA partner route, not RT-core acceleration",
        "no whole-application Barnes-Hut, paper-reproduction, automatic-backend-selection, or broad V3-over-V2 claim",
    ]
    return {
        "tool": "v3_phoenix_barnes_hut_fused_partner_m7_candidate",
        "version": "phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026_06_21",
        "status": status,
        "candidate_row_id": CANDIDATE_ROW_ID,
        "generic_capability": "aggregate_frontier",
        "refined_generic_capability": "vector_accumulation",
        "contract": CONTRACT,
        "candidate_route_id": "numba_cuda_fused",
        "candidate_partner": "numba_cuda",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "candidate_m7_contribution_if_external_review_approves": 1,
        "local_evidence_sufficient_for_external_public_row_review": not failed_checks,
        "source_packets": {
            "large_rerank": _rel(RERANK),
            "same_basis_no_go": _rel(SAME_BASIS_NO_GO),
            "small_smoke": _rel(SMOKE),
            "m53_report": _rel(REPORT),
        },
        "small_exact_smoke": {
            "passed": validation.get("passed"),
            "compared_against": validation.get("compared_against"),
            "max_abs_diff_x": validation.get("max_abs_diff_x"),
            "max_abs_diff_y": validation.get("max_abs_diff_y"),
            "metadata": {
                "contract": metadata.get("contract"),
                "frontier_rows_emitted": metadata.get("frontier_rows_emitted"),
                "frontier_rows_materialized_on_host": metadata.get("frontier_rows_materialized_on_host"),
                "contribution_rows_materialized_on_host": metadata.get("contribution_rows_materialized_on_host"),
                "native_engine_app_specific": metadata.get("native_engine_app_specific"),
                "rt_cores_used": metadata.get("rt_cores_used"),
                "rt_core_speedup_claim_authorized": metadata.get("rt_core_speedup_claim_authorized"),
                "true_zero_copy_claim_authorized": metadata.get("true_zero_copy_claim_authorized"),
            },
        },
        "large_same_basis_rows": large_rows,
        "large_same_basis_summary": {
            "min_cpu_numba_fused_over_candidate": min(cpu_speedups),
            "min_prepared_optix_numba_over_candidate": min(optix_speedups),
            "candidate_131072": candidate_131072,
        },
        "draft_row_scoped_claim_requiring_external_review": (
            "For the generic aggregate-tree fused weighted-vector partner row at 131,072 bodies, "
            "the Numba CUDA partner route completed in 45.493 ms wall-repeat median, "
            "4.082x faster than CPU/Numba fused. The 13.591x comparison against the current prepared "
            "RTDL/OptiX frontier-emission route is supporting no-go metadata only, not the primary "
            "claim. This is not an RT-core claim."
        ),
        "m7_blockers_before_external_review": blockers,
        "next_actions": [
            "Send this candidate packet to external AI review.",
            "If external review approves, add exactly one row-scoped aggregate_frontier/vector_accumulation M7 row.",
            "Keep public speedup and release flags false until that reviewed classification packet lands.",
            "Do not rewrite current prepared OptiX frontier-emission no-go into a win.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Open a narrow M7 candidate for the reusable fused Numba CUDA aggregate-tree/vector partner row, without promoting it before external review.",
            "was_i_foolish": "No. I separated the slow RT frontier-emission no-go from the fast generic partner route.",
            "foolish_actions": (
                "The foolish action would be to discard the whole aggregate family after the OptiX path failed, "
                "or to claim RT-core acceleration from a Numba CUDA partner result."
            ),
            "other_path": (
                "I could force a native OptiX redesign now, but the saved evidence shows the reusable partner "
                "route is the current performance path and fits V3's explicit-partner contract."
            ),
            "different_path_now": (
                "Use external review to decide whether this one row-scoped partner capability can close the "
                "aggregate_frontier breadth gap, while keeping release and broad claims false."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Barnes-Hut Fused Partner M7 Candidate",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet does not promote a row. It prepares one narrow aggregate-frontier/vector-accumulation",
        "candidate for external review after the same-basis no-go closed the current prepared OptiX",
        "frontier-emission shape.",
        "",
        "```text",
        f"candidate_row_id: {payload['candidate_row_id']}",
        f"contract: {payload['contract']}",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"row_scoped_public_speedup_claim_authorized: {str(payload['row_scoped_public_speedup_claim_authorized']).lower()}",
        f"rt_core_speedup_claim_authorized: {str(payload['rt_core_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"candidate_m7_contribution_if_external_review_approves: {payload['candidate_m7_contribution_if_external_review_approves']}",
        "```",
        "",
        "## Large Same-Basis Rows",
        "",
        "| Bodies | Candidate wall | CPU/Numba over candidate | Supporting no-go current OptiX frontier metadata | Contribution rows |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in payload["large_same_basis_rows"]:
        lines.append(
            "| "
            f"{int(row['body_count']):,} | "
            f"{float(row['candidate_wall_repeat_ms']):.3f} ms | "
            f"{float(row['cpu_numba_fused_over_candidate']):.3f}x | "
            f"{float(row['prepared_optix_numba_over_candidate']):.3f}x | "
            f"{int(row['contribution_row_count']):,} |"
        )
    lines.extend(
        [
            "",
            "## Draft Claim Under Review",
            "",
            payload["draft_row_scoped_claim_requiring_external_review"],
            "",
            "## Current Blockers",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["m7_blockers_before_external_review"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in payload["next_actions"])
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made it foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Phoenix V3 aggregate fused-partner M7 candidate packet.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
