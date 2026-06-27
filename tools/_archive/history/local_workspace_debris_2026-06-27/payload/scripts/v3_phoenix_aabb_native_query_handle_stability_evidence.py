#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs/rebuild/v3/evidence"
STABILITY_DIRS = (
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_stability_32768_s01_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_stability_32768_s02_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_stability_32768_s03_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_stability_65536_s01_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_stability_65536_s02_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_stability_65536_s03_20260621",
)
OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json"
OUT_MD = OUT_JSON.with_suffix(".md")
MATERIAL_WALL_SPEEDUP_FLOOR = 1.20


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _native_cache_ok(stats: dict[str, Any] | None) -> bool:
    if not isinstance(stats, dict):
        return False
    return (
        int(stats.get("native_range_intersection_misses", -1)) == 1
        and int(stats.get("native_range_intersection_hits", -1)) > 1
        and int(stats.get("native_range_intersection_entries", -1)) == 1
        and int(stats.get("range_intersection_misses", -1)) == 1
        and int(stats.get("range_intersection_hits", -1)) > 1
        and int(stats.get("range_intersection_entries", -1)) == 1
    )


def _sample_id(path: Path) -> str:
    return path.name.replace("phoenix_v3_aabb_native_query_handle_stability_", "")


def _row(path: Path) -> dict[str, Any]:
    summary_path = path / "summary.json"
    summary = _load_json(summary_path)
    optix = summary["phase_rows"]["optix"]
    embree = summary["phase_rows"]["embree"]
    comparisons = summary["comparisons"]
    params = summary["parameters"]
    return {
        "sample_id": _sample_id(path),
        "evidence_dir": _rel(path),
        "summary_path": _rel(summary_path),
        "status": summary["status"],
        "grid_count": int(params["grid_count"]),
        "repeat": int(params["repeat"]),
        "warmup": int(params["warmup"]),
        "runner_completed": bool(summary["runner_completed"]),
        "run_errors": dict(summary.get("run_errors", {})),
        "matches_cpu_reference": bool(optix["matches_cpu_reference"]) and bool(embree["matches_cpu_reference"]),
        "complete_candidate_coverage": bool(optix["complete_candidate_coverage"])
        and bool(embree["complete_candidate_coverage"]),
        "optix_native_cache_observed": _native_cache_ok(optix.get("prepared_query_cache_stats")),
        "optix_over_embree_cold_plus_collect_wall_speedup": float(
            comparisons["optix_over_embree_cold_plus_collect_wall_speedup"]
        ),
        "optix_over_embree_query_total_speedup": float(
            comparisons["optix_over_embree_query_total_speedup"]
        ),
        "optix_over_embree_runner_wall_speedup": float(
            comparisons["optix_over_embree_runner_wall_speedup"]
        ),
        "embree_cold_plus_collect_wall_sec": float(embree["cold_plus_collect_wall_sec"]),
        "optix_cold_plus_collect_wall_sec": float(optix["cold_plus_collect_wall_sec"]),
    }


def _group_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_scale: dict[str, dict[str, Any]] = {}
    for grid_count in sorted({int(row["grid_count"]) for row in rows}):
        scale_rows = [row for row in rows if int(row["grid_count"]) == grid_count]
        wall = [float(row["optix_over_embree_cold_plus_collect_wall_speedup"]) for row in scale_rows]
        runner = [float(row["optix_over_embree_runner_wall_speedup"]) for row in scale_rows]
        by_scale[str(grid_count)] = {
            "sample_count": len(scale_rows),
            "cold_plus_collect_wall_speedups": wall,
            "weakest_cold_plus_collect_wall_speedup": min(wall),
            "mean_cold_plus_collect_wall_speedup": mean(wall),
            "weakest_runner_wall_speedup": min(runner),
            "mean_runner_wall_speedup": mean(runner),
        }
    return by_scale


def build_payload() -> dict[str, Any]:
    rows = [_row(path) for path in STABILITY_DIRS]
    grouped = _group_summary(rows)
    wall_speedups = [float(row["optix_over_embree_cold_plus_collect_wall_speedup"]) for row in rows]
    checks = {
        "all_summaries_exist": all((path / "summary.json").exists() for path in STABILITY_DIRS),
        "six_fresh_runs_present": len(rows) == 6,
        "three_runs_per_scale": all(item["sample_count"] == 3 for item in grouped.values())
        and set(grouped) == {"32768", "65536"},
        "all_runner_completed": all(row["runner_completed"] for row in rows),
        "all_backend_errors_empty": all(row["run_errors"] == {} for row in rows),
        "all_matches_cpu_reference": all(row["matches_cpu_reference"] for row in rows),
        "all_complete_candidate_coverage": all(row["complete_candidate_coverage"] for row in rows),
        "all_optix_native_cache_observed": all(row["optix_native_cache_observed"] for row in rows),
        "all_cold_plus_collect_wall_clear_floor": all(
            speedup >= MATERIAL_WALL_SPEEDUP_FLOOR for speedup in wall_speedups
        ),
        "all_runner_wall_positive": all(float(row["optix_over_embree_runner_wall_speedup"]) > 1.0 for row in rows),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = "aabb_native_query_handle_stability_pass_not_m7" if not failed_checks else "aabb_native_query_handle_stability_fail_not_m7"
    return {
        "tool": "v3_phoenix_aabb_native_query_handle_stability_evidence",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": "generic AABB_INDEX_QUERY_2D native query-handle fresh-run stability",
        "source_dirs": [_rel(path) for path in STABILITY_DIRS],
        "material_wall_speedup_floor": MATERIAL_WALL_SPEEDUP_FLOOR,
        "fresh_run_stability_closes_blocker": status == "aabb_native_query_handle_stability_pass_not_m7",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "observed_rows": rows,
        "by_scale": grouped,
        "stability_summary": {
            "sample_count": len(rows),
            "weakest_cold_plus_collect_wall_speedup": min(wall_speedups),
            "mean_cold_plus_collect_wall_speedup": mean(wall_speedups),
            "best_cold_plus_collect_wall_speedup": max(wall_speedups),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "interpretation": (
            "Six fresh POD runs across 32,768 and 65,536 AABBs preserve the material "
            "cold-plus-collect wall win for the generic AABB candidate-stream route. "
            "This closes the fresh-run stability blocker only; it does not authorize M7 "
            "promotion or any public/broad speedup wording."
        ),
        "goal_level_decision_audit": {
            "decision": (
                "Add fresh-run AABB native-query-handle stability evidence instead of relying "
                "on repeat timing inside one benchmark process."
            ),
            "was_i_foolish": (
                "No. Huygens specifically called for run-to-run stability, and this packet "
                "answers that blocker directly."
            ),
            "foolish_actions": (
                "The foolish action would be to treat repeat=50 inside one process as fresh-run "
                "stability or to use the stability packet as M7 approval."
            ),
            "other_path": (
                "I could have requested review immediately after raw oracle closure. That would "
                "leave a known Huygens blocker unresolved."
            ),
            "different_path_now": (
                "Use this packet to close only the stability blocker, then keep external review "
                "and stable row materialization as the remaining gates."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["stability_summary"]
    lines = [
        "# Phoenix V3 AABB Native Query-Handle Stability Evidence",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This packet checks fresh-run stability for the generic AABB",
        "`range_intersection_rows` native query-handle route. It is not release",
        "authorization and not a broad speedup claim.",
        "",
        "## Summary",
        "",
        f"- Fresh runs: `{summary['sample_count']}`",
        f"- Material wall-speedup floor: `{payload['material_wall_speedup_floor']:.2f}x`",
        f"- Weakest cold-plus-collect wall speedup: `{summary['weakest_cold_plus_collect_wall_speedup']:.3f}x`",
        f"- Mean cold-plus-collect wall speedup: `{summary['mean_cold_plus_collect_wall_speedup']:.3f}x`",
        f"- Best cold-plus-collect wall speedup: `{summary['best_cold_plus_collect_wall_speedup']:.3f}x`",
        "",
        "## By Scale",
        "",
        "| grid_count | samples | weakest cold+collect | mean cold+collect | weakest runner wall |",
        "|---:|---:|---:|---:|---:|",
    ]
    for grid_count, item in payload["by_scale"].items():
        lines.append(
            "| "
            f"{grid_count} | "
            f"{item['sample_count']} | "
            f"{item['weakest_cold_plus_collect_wall_speedup']:.3f}x | "
            f"{item['mean_cold_plus_collect_wall_speedup']:.3f}x | "
            f"{item['weakest_runner_wall_speedup']:.3f}x |"
        )
    lines.extend(["", "## Samples", "", "| sample | grid_count | cold+collect | runner wall | oracle | native cache |", "|---|---:|---:|---:|---|---|"])
    for row in payload["observed_rows"]:
        lines.append(
            "| "
            f"{row['sample_id']} | "
            f"{row['grid_count']} | "
            f"{row['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x | "
            f"{row['optix_over_embree_runner_wall_speedup']:.3f}x | "
            f"{str(bool(row['matches_cpu_reference'])).lower()} | "
            f"{str(bool(row['optix_native_cache_observed'])).lower()} |"
        )
    lines.extend(["", "## Checks", ""])
    for name, passed in payload["checks"].items():
        lines.append(f"- `{name}`: `{str(bool(passed)).lower()}`")
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            f"Failed checks: `{payload['failed_checks']}`",
            "",
            "## Boundaries",
            "",
            "- Release authorized: `false`",
            "- Public speedup claim authorized: `false`",
            "- Broad V3-over-V2 claim authorized: `false`",
            "- M7 promotion authorized: `false`",
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phoenix V3 AABB fresh-run stability evidence.")
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
    print(json.dumps(payload if args.pretty else {"status": payload["status"], "failed_checks": payload["failed_checks"]}, indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
