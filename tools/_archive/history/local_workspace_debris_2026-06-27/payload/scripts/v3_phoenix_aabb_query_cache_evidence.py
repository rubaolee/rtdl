#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence"
QUERY_CACHE_EVIDENCE_DIRS = (
    EVIDENCE_ROOT / "phoenix_v3_aabb_prepare_reuse_query_cache_stats_32768_r50_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_prepare_reuse_query_cache_stats_65536_r50_20260621",
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.json"
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


def _cache_ok(stats: dict[str, Any] | None) -> bool:
    if not isinstance(stats, dict):
        return False
    return (
        int(stats.get("range_intersection_misses", -1)) == 1
        and int(stats.get("range_intersection_hits", -1)) > 1
        and int(stats.get("range_intersection_entries", -1)) == 1
    )


def _row(summary: dict[str, Any]) -> dict[str, Any]:
    params = summary["parameters"]
    cmp = summary["comparisons"]
    phase_rows = summary["phase_rows"]
    embree = phase_rows["embree"]
    optix = phase_rows["optix"]
    return {
        "evidence_dir": summary["_evidence_dir"],
        "summary_path": summary["_summary_path"],
        "status": summary["status"],
        "grid_count": int(params["grid_count"]),
        "repeat": int(params["repeat"]),
        "warmup": int(params["warmup"]),
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
        "embree_cold_plus_collect_wall_sec": float(embree["cold_plus_collect_wall_sec"]),
        "optix_cold_plus_collect_wall_sec": float(optix["cold_plus_collect_wall_sec"]),
        "embree_query_total_sec": float(embree["emit_aabb_intersection_pair_rows_2d_total_sec"]),
        "optix_query_total_sec": float(optix["emit_aabb_intersection_pair_rows_2d_total_sec"]),
        "embree_prepare_sec": float(embree["prepare_aabb_index_2d_sec"]),
        "optix_prepare_sec": float(optix["prepare_aabb_index_2d_sec"]),
        "embree_collect_sec": float(embree["collect_k_bounded_rows_sec"]),
        "optix_collect_sec": float(optix["collect_k_bounded_rows_sec"]),
        "embree_cache_stats": embree.get("prepared_query_cache_stats"),
        "optix_cache_stats": optix.get("prepared_query_cache_stats"),
        "embree_cache_observed": _cache_ok(embree.get("prepared_query_cache_stats")),
        "optix_cache_observed": _cache_ok(optix.get("prepared_query_cache_stats")),
        "matches_cpu_reference": bool(embree["matches_cpu_reference"])
        and bool(optix["matches_cpu_reference"]),
        "complete_candidate_coverage": bool(embree["complete_candidate_coverage"])
        and bool(optix["complete_candidate_coverage"]),
    }


def build_payload() -> dict[str, Any]:
    summaries = [_summary(path) for path in QUERY_CACHE_EVIDENCE_DIRS]
    rows = [_row(summary) for summary in summaries]
    wall_speedups = [
        row["optix_over_embree_cold_plus_collect_wall_speedup"] for row in rows
    ]
    query_speedups = [row["optix_over_embree_query_total_speedup"] for row in rows]
    prepare_speedups = [row["optix_over_embree_prepare_speedup"] for row in rows]
    collect_speedups = [row["optix_over_embree_collect_speedup"] for row in rows]
    largest = rows[-1]
    smallest = rows[0]
    hardware_gate = summaries[0]["environment"]["hardware_gate"]

    checks = {
        "summaries_exist": all((path / "summary.json").exists() for path in QUERY_CACHE_EVIDENCE_DIRS),
        "rows_are_32768_and_65536": {row["grid_count"] for row in rows} == {32_768, 65_536},
        "all_runner_completed": all(summary.get("runner_completed") is True for summary in summaries),
        "all_backend_errors_empty": all(summary.get("run_errors") == {} for summary in summaries),
        "all_have_embree_and_optix": all(
            set(summary.get("phase_rows", {})) == {"embree", "optix"} for summary in summaries
        ),
        "all_cpu_reference_match": all(row["matches_cpu_reference"] for row in rows),
        "all_complete_candidate_coverage": all(row["complete_candidate_coverage"] for row in rows),
        "all_cache_stats_observed": all(
            row["embree_cache_observed"] and row["optix_cache_observed"] for row in rows
        ),
        "all_query_total_positive": all(speedup > 1.0 for speedup in query_speedups),
        "all_wall_below_material_floor": all(
            speedup < MATERIAL_WALL_SPEEDUP_FLOOR for speedup in wall_speedups
        ),
        "larger_scale_not_better": largest[
            "optix_over_embree_cold_plus_collect_wall_speedup"
        ]
        < smallest["optix_over_embree_cold_plus_collect_wall_speedup"],
        "optix_prepare_slower_on_all_rows": all(speedup < 1.0 for speedup in prepare_speedups),
        "collect_not_material_win": max(collect_speedups) < 1.0,
        "hardware_gate_pass": hardware_gate.get("status") == "pass",
        "claim_flags_false": all(
            summary.get("release_authorized") is False
            and summary.get("public_speedup_claim_authorized") is False
            and summary.get("broad_v3_faster_than_v2_claim_authorized") is False
            and summary.get("m7_promotion_authorized") is False
            for summary in summaries
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "aabb_prepare_reuse_query_cache_evidence_not_m7_wall_floor_not_met"
    )

    return {
        "tool": "v3_phoenix_aabb_prepare_reuse_query_cache_evidence",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": (
            "generic aabb_index_query_2d prepared-session candidate stream; "
            "contact_manifold is only the evidence harness"
        ),
        "source_dirs": [_rel(path) for path in QUERY_CACHE_EVIDENCE_DIRS],
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_candidate_reopen_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "material_wall_speedup_floor": MATERIAL_WALL_SPEEDUP_FLOOR,
        "hardware": {
            "host": "root@213.173.108.14 -p 11592",
            "gpu": hardware_gate["gpus"][0]["name"],
            "driver_version": hardware_gate["gpus"][0]["driver_version"],
            "compute_cap": hardware_gate["gpus"][0]["compute_cap"],
            "rt_hardware_gate": hardware_gate["status"],
        },
        "observed_rows": rows,
        "blocker_summary": {
            "best_cold_plus_collect_wall_speedup": max(wall_speedups),
            "largest_cold_plus_collect_wall_speedup": largest[
                "optix_over_embree_cold_plus_collect_wall_speedup"
            ],
            "best_query_total_speedup": max(query_speedups),
            "best_prepare_speedup": max(prepare_speedups),
            "best_collect_speedup": max(collect_speedups),
            "cache_was_observed": checks["all_cache_stats_observed"],
        },
        "interpretation": (
            "The prepared-query record cache is real and generic: both serious rows show one "
            "range-intersection cache entry with one miss and 52 hits per backend. However, "
            "the material wall result still fails the V3 floor. The 32,768-row cold-plus-collect "
            "wall ratio is below 1.20x, and the 65,536-row ratio is lower again. This is a "
            "correct engine cleanup, not a V3 performance promotion."
        ),
        "next_engine_action": (
            "Keep AABB prepare-reuse in the open generic-engine queue. The next useful work is "
            "below Python query-record reuse: cache or reuse native packed query buffers, reduce "
            "OptiX prepare cost, and reduce row-output collect/compaction overhead. Do not run "
            "more scale-only AABB attempts without a new contract rationale."
        ),
        "forbidden_shortcuts": [
            "Do not promote AABB prepare-reuse to M7 from these cache-hit rows.",
            "Do not quote query-total speedup as a V3 win while cold-plus-collect wall is below 1.20x.",
            "Do not treat contact_manifold as the optimized product; it is only the evidence harness.",
            "Do not claim full contact solving, broad AABB acceleration, or broad V3-over-V2 speedup.",
            "Do not keep scale-shopping this contract without a new reviewed rationale.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record the AABB prepared-query record cache as a correct generic cleanup but "
                "not as a V3 M7 performance row."
            ),
            "was_i_foolish": (
                "No. The packet accepts the cache evidence but refuses to turn sub-floor wall "
                "speedups into a release claim."
            ),
            "foolish_actions": (
                "The foolish action would be to celebrate 1.188x as close enough, or quote "
                "query-total speedup while hiding prepare and collect costs."
            ),
            "other_path": (
                "I could keep trying larger AABB sizes. The 65,536 row already got worse, so "
                "that would be scale-shopping rather than solving the engine bottleneck."
            ),
            "different_path_now": (
                "Move the AABB route to deeper generic overhead work: native packed query "
                "buffer reuse, prepare-cost reduction, and collect/compaction improvement."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    summary = payload["blocker_summary"]
    lines = [
        "# Phoenix V3 AABB Query-Cache Evidence",
        "",
        f"Status: `{payload['status']}`",
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
        "## Observed Rows",
        "",
        "| AABBs | Repeat | Cache hits | Prepare | Query total | Collect | Cold+collect wall | Runner wall |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["observed_rows"]:
        optix_stats = row["optix_cache_stats"]
        lines.append(
            f"| {row['grid_count']} | {row['repeat']} | "
            f"{int(optix_stats['range_intersection_hits'])} | "
            f"{row['optix_over_embree_prepare_speedup']:.3f}x | "
            f"{row['optix_over_embree_query_total_speedup']:.3f}x | "
            f"{row['optix_over_embree_collect_speedup']:.3f}x | "
            f"{row['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x | "
            f"{row['optix_over_embree_runner_wall_speedup']:.3f}x |"
        )
    lines.extend(
        [
            "",
            "## Blocker Summary",
            "",
            f"- Material wall-speedup floor: `{payload['material_wall_speedup_floor']:.3f}x`",
            f"- Best cold+collect wall speedup: `{summary['best_cold_plus_collect_wall_speedup']:.3f}x`",
            f"- Largest-row cold+collect wall speedup: `{summary['largest_cold_plus_collect_wall_speedup']:.3f}x`",
            f"- Best query-total speedup: `{summary['best_query_total_speedup']:.3f}x`",
            f"- Cache observed: `{str(summary['cache_was_observed']).lower()}`",
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
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{name}`: `{str(bool(ok)).lower()}`" for name, ok in payload["checks"].items())
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
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 AABB query-cache evidence.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
