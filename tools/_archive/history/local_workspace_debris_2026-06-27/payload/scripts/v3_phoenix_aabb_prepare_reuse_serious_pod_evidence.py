#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_aabb_prepare_reuse_serious_20260621"
)
SUMMARY = EVIDENCE_DIR / "summary.json"
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    summary = _read_json(SUMMARY)
    comparisons = summary["comparisons"]
    phase_rows = summary["phase_rows"]
    environment = summary["environment"]
    hardware_gate = environment["hardware_gate"]
    material_floor = float(summary["material_wall_speedup_floor"])
    cold_speedup = float(comparisons["optix_over_embree_cold_plus_collect_wall_speedup"])
    broadphase_speedup = float(comparisons["optix_over_embree_broadphase_wall_speedup"])
    query_total_speedup = float(comparisons["optix_over_embree_query_total_speedup"])
    prepare_speedup = float(comparisons["optix_over_embree_prepare_speedup"])

    checks = {
        "summary_exists": SUMMARY.exists(),
        "runner_completed": summary.get("runner_completed") is True,
        "runner_status_not_m7": summary.get("status") == "aabb_prepare_reuse_pod_evidence_collected_not_m7",
        "serious_fixture_scale": summary["checks"].get("serious_fixture_scale") is True,
        "has_32768_indexed_aabbs": summary["checks"].get("has_32768_indexed_aabbs") is True,
        "has_32768_query_aabbs": summary["checks"].get("has_32768_query_aabbs") is True,
        "embree_and_optix_present": summary["checks"].get("embree_and_optix_present") is True,
        "no_backend_errors": summary["checks"].get("runner_completed_without_backend_errors") is True,
        "all_payloads_match_cpu_reference": summary["checks"].get("all_payloads_match_cpu_reference") is True,
        "all_payloads_complete_candidate_coverage": summary["checks"].get(
            "all_payloads_complete_candidate_coverage"
        )
        is True,
        "all_payloads_observed_reuse": summary["checks"].get("all_payloads_observed_reuse") is True,
        "phase_table_has_prepare_query_collect_wall": summary["checks"].get(
            "phase_table_has_prepare_query_collect_wall"
        )
        is True,
        "rt_hardware_gate_passed": hardware_gate.get("status") == "pass",
        "material_wall_speedup_below_floor": cold_speedup < material_floor,
        "material_wall_speedup_positive_but_low_margin": 1.0 < cold_speedup < material_floor,
        "runner_blocks_m7": summary.get("m7_reopen_candidate_pending_2ai_review") is False,
        "release_flags_false": summary.get("release_authorized") is False
        and summary.get("public_speedup_claim_authorized") is False
        and summary.get("whole_app_speedup_claim_authorized") is False
        and summary.get("m7_promotion_authorized") is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin"

    return {
        "tool": "v3_phoenix_aabb_prepare_reuse_serious_pod_evidence",
        "version": "phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026_06_21",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": False,
        "evidence_dir": _rel(EVIDENCE_DIR),
        "source_summary": _rel(SUMMARY),
        "hardware": {
            "host": "root@213.173.108.14 -p 11592",
            "gpu": hardware_gate["gpus"][0]["name"],
            "driver_version": hardware_gate["gpus"][0]["driver_version"],
            "compute_cap": hardware_gate["gpus"][0]["compute_cap"],
            "rt_hardware_gate": hardware_gate["status"],
        },
        "parameters": summary["parameters"],
        "phase_rows": {
            backend: {
                "prepare_aabb_index_2d_sec": row["prepare_aabb_index_2d_sec"],
                "emit_aabb_intersection_pair_rows_2d_total_sec": row[
                    "emit_aabb_intersection_pair_rows_2d_total_sec"
                ],
                "emit_aabb_intersection_pair_rows_2d_median_sec": row[
                    "emit_aabb_intersection_pair_rows_2d_median_sec"
                ],
                "collect_k_bounded_rows_sec": row["collect_k_bounded_rows_sec"],
                "generic_aabb_broadphase_wall_sec": row["generic_aabb_broadphase_wall_sec"],
                "cold_plus_collect_wall_sec": row["cold_plus_collect_wall_sec"],
                "runner_wall_sec": row["runner_wall_sec"],
                "matches_cpu_reference": row["matches_cpu_reference"],
                "complete_candidate_coverage": row["complete_candidate_coverage"],
                "valid_rows": row["valid_rows"],
            }
            for backend, row in phase_rows.items()
        },
        "comparisons": {
            "optix_over_embree_prepare_speedup": prepare_speedup,
            "optix_over_embree_query_total_speedup": query_total_speedup,
            "optix_over_embree_query_median_speedup": comparisons[
                "optix_over_embree_query_median_speedup"
            ],
            "optix_over_embree_collect_speedup": comparisons["optix_over_embree_collect_speedup"],
            "optix_over_embree_broadphase_wall_speedup": broadphase_speedup,
            "optix_over_embree_cold_plus_collect_wall_speedup": cold_speedup,
            "optix_over_embree_runner_wall_speedup": comparisons[
                "optix_over_embree_runner_wall_speedup"
            ],
            "material_wall_speedup_floor": material_floor,
        },
        "interpretation": (
            "This serious RTX run is useful V3 engine evidence but not an M7 reopen "
            "candidate. Reusing the prepared AABB path moves the wall comparison from "
            "the earlier contact regression into a positive 1.140x cold-plus-collect "
            "wall result, but it is below the runner's 1.20 material-speedup floor. "
            "OptiX query work improves, while OptiX prepare is still slower than Embree."
        ),
        "next_engine_action": (
            "Keep AABB prepare-reuse in the Phoenix queue. The next valid work is "
            "generic engine tuning that either reduces OptiX prepare/query overhead or "
            "finds a reviewer-approved workload shape where repeated prepared reuse "
            "clears the material wall-speedup floor without app-specific native logic."
        ),
        "forbidden_shortcuts": [
            "Do not promote this row to M7.",
            "Do not claim V3 AABB is faster from a 1.140x low-margin wall result.",
            "Do not quote the 1.178x query-total speedup as a release claim.",
            "Do not claim full contact solver speedup or broad V3-over-V2 speedup.",
            "Do not treat this as 2-AI reviewed evidence.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Record the serious AABB prepare-reuse RTX run as useful not-M7 evidence.",
            "was_i_foolish": (
                "No. The run used serious scale, RTX hardware, both backends, parity, "
                "phase accounting, and the predeclared material-speedup floor."
            ),
            "foolish_actions": (
                "The foolish action would be to round 1.140x up into a V3 win, quote "
                "query-only numbers, or ignore that OptiX prepare remains slower."
            ),
            "other_path": (
                "Skip the run and keep the runner as a plan. That would preserve a clean "
                "story but would not answer whether prepare reuse materially fixes AABB."
            ),
            "different_path_now": (
                "Use this low-margin evidence to drive engine-level overhead work or "
                "another reviewer-approved prepared-reuse shape before any M7 review."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 AABB Prepare-Reuse Serious RTX Evidence",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet records a serious RTX run for the generic",
        "`aabb_candidate_stream` prepare-reuse queue item. It does not promote a",
        "new M7 row.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Hardware And Scale",
        "",
        f"- Host: `{payload['hardware']['host']}`",
        f"- GPU: `{payload['hardware']['gpu']}`",
        f"- Driver: `{payload['hardware']['driver_version']}`",
        f"- Compute capability: `{payload['hardware']['compute_cap']}`",
        f"- RT hardware gate: `{payload['hardware']['rt_hardware_gate']}`",
        f"- Dataset: `{payload['parameters']['dataset']}`",
        f"- Indexed AABBs: `{payload['parameters']['indexed_aabb_count']}`",
        f"- Query AABBs: `{payload['parameters']['query_aabb_count']}`",
        f"- Warmup/repeat: `{payload['parameters']['warmup']}` / `{payload['parameters']['repeat']}`",
        "",
        "## Phase Table",
        "",
        "| Backend | Prepare s | Query total s | Collect s | Broadphase wall s | Cold+collect wall s |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for backend in ("embree", "optix"):
        row = payload["phase_rows"][backend]
        lines.append(
            f"| `{backend}` | {row['prepare_aabb_index_2d_sec']:.6f} | "
            f"{row['emit_aabb_intersection_pair_rows_2d_total_sec']:.6f} | "
            f"{row['collect_k_bounded_rows_sec']:.6f} | "
            f"{row['generic_aabb_broadphase_wall_sec']:.6f} | "
            f"{row['cold_plus_collect_wall_sec']:.6f} |"
        )
    cmp = payload["comparisons"]
    lines.extend(
        [
            "",
            "## Ratios",
            "",
            f"- OptiX / Embree prepare speedup: `{cmp['optix_over_embree_prepare_speedup']:.3f}x`",
            f"- OptiX / Embree query-total speedup: `{cmp['optix_over_embree_query_total_speedup']:.3f}x`",
            f"- OptiX / Embree broadphase-wall speedup: `{cmp['optix_over_embree_broadphase_wall_speedup']:.3f}x`",
            f"- OptiX / Embree cold-plus-collect wall speedup: `{cmp['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x`",
            f"- Material wall-speedup floor: `{cmp['material_wall_speedup_floor']:.3f}x`",
            "",
            payload["interpretation"],
            "",
            "## Next Engine Action",
            "",
            payload["next_engine_action"],
            "",
            "## Forbidden Shortcuts",
            "",
        ]
    )
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
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 AABB serious RTX evidence packet.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


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
        print(json.dumps({"status": payload["status"], "m7_rows_added": 0}, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0 if payload["status"] == "aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin" else 2


if __name__ == "__main__":
    raise SystemExit(main())
