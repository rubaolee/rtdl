#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SERIOUS_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.json"
)
SCALE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.json"
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _ratio_rows(scale: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in scale["scale_rows"]:
        rows.append(
            {
                "grid_count": row["grid_count"],
                "repeat": row["repeat"],
                "prepare_speedup": row["optix_over_embree_prepare_speedup"],
                "query_total_speedup": row["optix_over_embree_query_total_speedup"],
                "collect_speedup": row["optix_over_embree_collect_speedup"],
                "cold_plus_collect_wall_speedup": row[
                    "optix_over_embree_cold_plus_collect_wall_speedup"
                ],
                "runner_wall_speedup": row["optix_over_embree_runner_wall_speedup"],
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    serious = _read_json(SERIOUS_EVIDENCE)
    scale = _read_json(SCALE_EVIDENCE)
    rows = _ratio_rows(scale)
    wall_floor = float(scale["material_wall_speedup_floor"])
    wall_speedups = [float(row["cold_plus_collect_wall_speedup"]) for row in rows]
    prepare_speedups = [float(row["prepare_speedup"]) for row in rows]
    query_total_speedups = [float(row["query_total_speedup"]) for row in rows]
    collect_speedups = [float(row["collect_speedup"]) for row in rows]

    required_blockers = [
        "optix_prepare_slower_than_embree",
        "material_wall_floor_not_met",
        "larger_scale_not_better",
        "query_only_claim_forbidden",
        "collect_not_material_win",
        "external_m7_review_missing_for_new_row",
        "generic_overhead_reduction_required",
        "same_contract_public_wording_review_missing",
    ]

    checks = {
        "serious_evidence_exists": SERIOUS_EVIDENCE.exists(),
        "scale_evidence_exists": SCALE_EVIDENCE.exists(),
        "serious_evidence_not_m7": (
            serious.get("status") == "aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin"
            and serious.get("m7_promotion_authorized") is False
            and serious.get("m7_qualified_release_rows_added") == 0
        ),
        "scale_evidence_not_m7": (
            scale.get("status") == "aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor"
            and scale.get("m7_promotion_authorized") is False
            and scale.get("m7_qualified_release_rows_added") == 0
        ),
        "rows_cover_32768_and_65536": {row["grid_count"] for row in rows} == {32_768, 65_536},
        "all_wall_speedups_below_material_floor": all(speedup < wall_floor for speedup in wall_speedups),
        "larger_scale_not_better": scale.get("checks", {}).get("larger_scale_not_better") is True,
        "optix_prepare_slower_on_all_rows": all(speedup < 1.0 for speedup in prepare_speedups),
        "query_total_positive_but_not_promotable": (
            all(speedup > 1.0 for speedup in query_total_speedups)
            and max(wall_speedups) < wall_floor
        ),
        "collect_is_not_material_win": max(collect_speedups) < 1.01,
        "scale_shopping_already_blocked": "Stop scale-shopping" in scale.get("next_engine_action", ""),
        "claim_flags_false": (
            serious.get("release_authorized") is False
            and serious.get("public_speedup_claim_authorized") is False
            and serious.get("broad_v3_faster_than_v2_claim_authorized") is False
            and scale.get("release_authorized") is False
            and scale.get("public_speedup_claim_authorized") is False
            and scale.get("broad_v3_faster_than_v2_claim_authorized") is False
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "aabb_prepare_reuse_overhead_gate_blocked_not_m7"

    return {
        "tool": "v3_phoenix_aabb_prepare_reuse_overhead_gate",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": scale["candidate_scope"],
        "source_packets": {
            "serious_evidence": _rel(SERIOUS_EVIDENCE),
            "scale_evidence": _rel(SCALE_EVIDENCE),
        },
        "m7_candidate_reopen_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "full_contact_solver_claim_authorized": False,
        "material_wall_speedup_floor": wall_floor,
        "observed_ratios": rows,
        "blocker_summary": {
            "best_cold_plus_collect_wall_speedup": max(wall_speedups),
            "latest_cold_plus_collect_wall_speedup": rows[-1]["cold_plus_collect_wall_speedup"],
            "best_query_total_speedup": max(query_total_speedups),
            "best_prepare_speedup": max(prepare_speedups),
            "best_collect_speedup": max(collect_speedups),
        },
        "required_blockers_before_m7": required_blockers,
        "interpretation": (
            "AABB prepare-reuse is a useful V3 engine target, but the current evidence is "
            "blocked. The 32,768 row was only 1.140x cold-plus-collect wall versus Embree, "
            "below the 1.20 material floor; the 65,536 rerun fell to 1.087x. OptiX prepare "
            "is slower on both rows, query-total wins are not valid public claims without "
            "wall clearance, and collect is neutral or slower. This is not a V3 performance win yet."
        ),
        "next_engine_action": (
            "Do generic AABB overhead work before any new M7 attempt: reduce OptiX prepare cost, "
            "reduce repeated query overhead, improve collect/compaction cost, or propose a "
            "separately justified prepared-session contract that clears the wall floor without "
            "contact-specific native logic."
        ),
        "forbidden_shortcuts": [
            "Do not promote AABB prepare-reuse to M7 from 1.140x or 1.087x wall evidence.",
            "Do not quote query-total speedup as a V3 win while cold-plus-collect wall is below 1.20x.",
            "Do not keep scale-shopping this contract without a new reviewer-approved rationale.",
            "Do not claim full contact solving, broad AABB-index acceleration, or broad V3-over-V2 speedup.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Add a hard overhead gate for AABB prepare-reuse instead of treating sub-floor ratios as V3 progress.",
            "was_i_foolish": (
                "No. This gate prevents a low-margin 1.140x row and a worse 1.087x scale row from being "
                "mistaken for a major V3 optimization."
            ),
            "foolish_actions": (
                "The foolish action would be to promote query-only wins, keep increasing scale until a "
                "ratio looks good, or call this full contact/AABB acceleration."
            ),
            "other_path": (
                "I could have moved straight to code tuning. That might be useful, but without this gate "
                "the current evidence would remain easy to misread."
            ),
            "different_path_now": (
                "Use the gate as the work order for real generic overhead reduction: prepare, query, and "
                "collect/compaction must improve before AABB can reopen M7."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    summary = payload["blocker_summary"]
    lines = [
        "# Phoenix V3 AABB Prepare-Reuse Overhead Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["interpretation"],
        "",
        "## Verdict",
        "",
        f"- M7 candidate reopen authorized: `{str(payload['m7_candidate_reopen_authorized']).lower()}`",
        f"- M7 promotion authorized: `{str(payload['m7_promotion_authorized']).lower()}`",
        f"- Release authorized: `{str(payload['release_authorized']).lower()}`",
        f"- Public speedup claim authorized: `{str(payload['public_speedup_claim_authorized']).lower()}`",
        f"- Material wall-speedup floor: `{payload['material_wall_speedup_floor']:.3f}x`",
        "",
        "## Observed Ratios",
        "",
        "| AABBs | Repeat | Prepare | Query total | Collect | Cold+collect wall | Runner wall |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["observed_ratios"]:
        lines.append(
            f"| {row['grid_count']} | {row['repeat']} | "
            f"{row['prepare_speedup']:.3f}x | "
            f"{row['query_total_speedup']:.3f}x | "
            f"{row['collect_speedup']:.3f}x | "
            f"{row['cold_plus_collect_wall_speedup']:.3f}x | "
            f"{row['runner_wall_speedup']:.3f}x |"
        )
    lines.extend(
        [
            "",
            "## Blocker Summary",
            "",
            f"- Best cold+collect wall speedup: `{summary['best_cold_plus_collect_wall_speedup']:.3f}x`",
            f"- Latest cold+collect wall speedup: `{summary['latest_cold_plus_collect_wall_speedup']:.3f}x`",
            f"- Best query-total speedup: `{summary['best_query_total_speedup']:.3f}x`",
            f"- Best prepare speedup: `{summary['best_prepare_speedup']:.3f}x`",
            f"- Best collect speedup: `{summary['best_collect_speedup']:.3f}x`",
            "",
            "## Required Blockers Before M7",
            "",
        ]
    )
    lines.extend(f"- `{blocker}`" for blocker in payload["required_blockers_before_m7"])
    lines.extend(["", "## Next Engine Action", "", payload["next_engine_action"], ""])
    lines.extend(["## Forbidden Shortcuts", ""])
    lines.extend(f"- {shortcut}" for shortcut in payload["forbidden_shortcuts"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{name}`: `{str(bool(passed)).lower()}`" for name, passed in payload["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{payload['failed_checks']}`",
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
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 AABB prepare-reuse overhead gate.")
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": payload["failed_checks"],
                "m7_rows_added": payload["m7_qualified_release_rows_added"],
            },
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0 if payload["status"] == "aabb_prepare_reuse_overhead_gate_blocked_not_m7" else 2


if __name__ == "__main__":
    raise SystemExit(main())
