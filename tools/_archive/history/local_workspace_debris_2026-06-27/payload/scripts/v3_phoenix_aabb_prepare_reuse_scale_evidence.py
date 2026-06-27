#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence"
SCALE_EVIDENCE_DIRS = (
    EVIDENCE_ROOT / "phoenix_v3_aabb_prepare_reuse_serious_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_prepare_reuse_65536_r50_20260621",
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
MATERIAL_WALL_SPEEDUP_FLOOR = 1.20


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _summary(path: Path) -> dict[str, Any]:
    summary_path = path / "summary.json"
    summary = _read_json(summary_path)
    summary["_evidence_dir"] = _rel(path)
    summary["_summary_path"] = _rel(summary_path)
    return summary


def _scale_row(summary: dict[str, Any]) -> dict[str, Any]:
    params = summary["parameters"]
    cmp = summary["comparisons"]
    embree = summary["phase_rows"]["embree"]
    optix = summary["phase_rows"]["optix"]
    return {
        "evidence_dir": summary["_evidence_dir"],
        "summary_path": summary["_summary_path"],
        "status": summary["status"],
        "grid_count": int(params["grid_count"]),
        "repeat": int(params["repeat"]),
        "dataset": params["dataset"],
        "failed_checks": list(summary["failed_checks"]),
        "optix_over_embree_prepare_speedup": float(cmp["optix_over_embree_prepare_speedup"]),
        "optix_over_embree_query_total_speedup": float(cmp["optix_over_embree_query_total_speedup"]),
        "optix_over_embree_collect_speedup": float(cmp["optix_over_embree_collect_speedup"]),
        "optix_over_embree_broadphase_wall_speedup": float(
            cmp["optix_over_embree_broadphase_wall_speedup"]
        ),
        "optix_over_embree_cold_plus_collect_wall_speedup": float(
            cmp["optix_over_embree_cold_plus_collect_wall_speedup"]
        ),
        "optix_over_embree_runner_wall_speedup": float(
            cmp["optix_over_embree_runner_wall_speedup"]
        ),
        "embree_prepare_sec": float(embree["prepare_aabb_index_2d_sec"]),
        "optix_prepare_sec": float(optix["prepare_aabb_index_2d_sec"]),
        "embree_query_total_sec": float(embree["emit_aabb_intersection_pair_rows_2d_total_sec"]),
        "optix_query_total_sec": float(optix["emit_aabb_intersection_pair_rows_2d_total_sec"]),
        "embree_collect_sec": float(embree["collect_k_bounded_rows_sec"]),
        "optix_collect_sec": float(optix["collect_k_bounded_rows_sec"]),
        "embree_cold_plus_collect_wall_sec": float(embree["cold_plus_collect_wall_sec"]),
        "optix_cold_plus_collect_wall_sec": float(optix["cold_plus_collect_wall_sec"]),
        "matches_cpu_reference": bool(embree["matches_cpu_reference"])
        and bool(optix["matches_cpu_reference"]),
        "complete_candidate_coverage": bool(embree["complete_candidate_coverage"])
        and bool(optix["complete_candidate_coverage"]),
    }


def build_payload() -> dict[str, Any]:
    summaries = [_summary(path) for path in SCALE_EVIDENCE_DIRS]
    rows = [_scale_row(summary) for summary in summaries]
    rows_by_scale = {row["grid_count"]: row for row in rows}
    wall_speedups = [
        row["optix_over_embree_cold_plus_collect_wall_speedup"] for row in rows
    ]
    largest = rows[-1]
    smallest = rows[0]
    hardware_gate = summaries[-1]["environment"]["hardware_gate"]

    checks = {
        "all_summaries_exist": all((path / "summary.json").exists() for path in SCALE_EVIDENCE_DIRS),
        "scales_are_32768_and_65536": set(rows_by_scale) == {32_768, 65_536},
        "all_runner_completed": all(summary.get("runner_completed") is True for summary in summaries),
        "all_backend_errors_empty": all(summary.get("run_errors") == {} for summary in summaries),
        "all_have_embree_and_optix": all(
            set(summary.get("phase_rows", {})) == {"embree", "optix"} for summary in summaries
        ),
        "all_cpu_reference_match": all(row["matches_cpu_reference"] for row in rows),
        "all_complete_candidate_coverage": all(row["complete_candidate_coverage"] for row in rows),
        "all_below_material_floor": all(speedup < MATERIAL_WALL_SPEEDUP_FLOOR for speedup in wall_speedups),
        "larger_scale_not_better": largest[
            "optix_over_embree_cold_plus_collect_wall_speedup"
        ]
        < smallest["optix_over_embree_cold_plus_collect_wall_speedup"],
        "latest_failed_material_check": "material_optix_wall_win_after_prepare_reuse"
        in largest["failed_checks"],
        "hardware_gate_pass": hardware_gate.get("status") == "pass",
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor"
    )

    return {
        "tool": "v3_phoenix_aabb_prepare_reuse_scale_evidence",
        "version": "phoenix_v3_aabb_prepare_reuse_scale_evidence_2026_06_21",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": (
            "generic aabb_index_query_2d prepared-session candidate stream; "
            "contact_manifold is only the evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": False,
        "material_wall_speedup_floor": MATERIAL_WALL_SPEEDUP_FLOOR,
        "hardware": {
            "host": "root@213.173.108.14 -p 11592",
            "gpu": hardware_gate["gpus"][0]["name"],
            "driver_version": hardware_gate["gpus"][0]["driver_version"],
            "compute_cap": hardware_gate["gpus"][0]["compute_cap"],
            "rt_hardware_gate": hardware_gate["status"],
        },
        "scale_rows": rows,
        "interpretation": (
            "The AABB prepare-reuse scale check does not reopen M7. At 32,768 "
            "AABBs, OptiX/Embree cold-plus-collect wall speedup was 1.140x, below "
            "the 1.20 floor. At 65,536 AABBs, it fell to 1.087x. Query-total "
            "speedup stayed positive but also declined, and OptiX collect became "
            "slower at 65,536. Scaling the same prepared-session shape therefore "
            "does not solve the V3 material wall requirement."
        ),
        "next_engine_action": (
            "Stop scale-shopping this row. The next valid AABB work is generic "
            "engine overhead reduction: reduce OptiX prepare cost, reduce repeated "
            "query overhead, improve collect/compaction cost, or find a separately "
            "justified contract shape before any new M7 review."
        ),
        "forbidden_shortcuts": [
            "Do not promote either 32,768 or 65,536 prepare-reuse row to M7.",
            "Do not claim V3 AABB prepare-reuse is faster from sub-floor 1.140x or 1.087x wall ratios.",
            "Do not use query-total speedup without reporting cold-plus-collect wall.",
            "Do not keep increasing scale until a ratio crosses the floor without a contract rationale.",
            "Do not claim full contact solver or broad V3-over-V2 speedup.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record the 65,536-row AABB prepare-reuse rerun as scale evidence "
                "that does not clear the M7 material floor."
            ),
            "was_i_foolish": (
                "No. The rerun tested whether a serious larger scale amortizes the "
                "prepared AABB path enough to meet the predeclared floor."
            ),
            "foolish_actions": (
                "The foolish action would be to keep shopping scales or quote "
                "query-only wins after the 65,536-row wall result got worse."
            ),
            "other_path": (
                "Skip the scale rerun and assume 32,768 was representative. That "
                "would leave a plausible but untested scale question open."
            ),
            "different_path_now": (
                "Use this no-go scale packet to drive actual generic overhead work "
                "instead of more app-specific or scale-only experiments."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 AABB Prepare-Reuse Scale Evidence",
        "",
        f"Status: `{payload['status']}`.",
        "",
        payload["interpretation"],
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Scale Rows",
        "",
        "| AABBs | Repeat | Prepare | Query total | Collect | Cold+collect wall | Runner wall |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["scale_rows"]:
        lines.append(
            f"| {row['grid_count']} | {row['repeat']} | "
            f"{row['optix_over_embree_prepare_speedup']:.3f}x | "
            f"{row['optix_over_embree_query_total_speedup']:.3f}x | "
            f"{row['optix_over_embree_collect_speedup']:.3f}x | "
            f"{row['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x | "
            f"{row['optix_over_embree_runner_wall_speedup']:.3f}x |"
        )
    lines.extend(
        [
            "",
            f"Material wall-speedup floor: `{payload['material_wall_speedup_floor']:.3f}x`.",
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
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 AABB prepare-reuse scale evidence.")
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
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "m7_rows_added": payload["m7_qualified_release_rows_added"],
                },
                sort_keys=True,
            )
        )
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return (
        0
        if payload["status"]
        == "aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
