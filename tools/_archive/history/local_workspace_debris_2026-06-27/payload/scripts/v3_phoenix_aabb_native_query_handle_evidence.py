#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence"
NATIVE_HANDLE_EVIDENCE_DIRS = (
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_32768_r50_20260621",
    EVIDENCE_ROOT / "phoenix_v3_aabb_native_query_handle_65536_r50_20260621",
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json"
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
        "optix_native_cache_observed": _native_cache_ok(optix.get("prepared_query_cache_stats")),
        "matches_cpu_reference": bool(embree["matches_cpu_reference"])
        and bool(optix["matches_cpu_reference"]),
        "complete_candidate_coverage": bool(embree["complete_candidate_coverage"])
        and bool(optix["complete_candidate_coverage"]),
    }


def build_payload() -> dict[str, Any]:
    summaries = [_summary(path) for path in NATIVE_HANDLE_EVIDENCE_DIRS]
    rows = [_row(summary) for summary in summaries]
    wall_speedups = [
        row["optix_over_embree_cold_plus_collect_wall_speedup"] for row in rows
    ]
    runner_speedups = [row["optix_over_embree_runner_wall_speedup"] for row in rows]
    query_speedups = [row["optix_over_embree_query_total_speedup"] for row in rows]
    hardware_gate = summaries[0]["environment"]["hardware_gate"]

    checks = {
        "summaries_exist": all((path / "summary.json").exists() for path in NATIVE_HANDLE_EVIDENCE_DIRS),
        "rows_are_32768_and_65536": {row["grid_count"] for row in rows} == {32_768, 65_536},
        "all_runner_completed": all(summary.get("runner_completed") is True for summary in summaries),
        "all_backend_errors_empty": all(summary.get("run_errors") == {} for summary in summaries),
        "all_have_embree_and_optix": all(
            set(summary.get("phase_rows", {})) == {"embree", "optix"} for summary in summaries
        ),
        "all_cpu_reference_match": all(row["matches_cpu_reference"] for row in rows),
        "all_complete_candidate_coverage": all(row["complete_candidate_coverage"] for row in rows),
        "all_optix_native_cache_stats_observed": all(row["optix_native_cache_observed"] for row in rows),
        "all_query_total_positive": all(speedup > 1.0 for speedup in query_speedups),
        "all_runner_wall_positive": all(speedup > 1.0 for speedup in runner_speedups),
        "all_wall_clear_material_floor": all(
            speedup >= MATERIAL_WALL_SPEEDUP_FLOOR for speedup in wall_speedups
        ),
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
        else "aabb_native_query_handle_m7_candidate_pending_external_review"
    )

    return {
        "tool": "v3_phoenix_aabb_native_query_handle_evidence",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": (
            "generic AABB_INDEX_QUERY_2D prepared-session candidate stream; "
            "contact_manifold is only the evidence harness"
        ),
        "native_generic_change": (
            "OptiX range_intersection_rows now reuses prepared native box-query handles "
            "through rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows_packed_queries"
        ),
        "source_dirs": [_rel(path) for path in NATIVE_HANDLE_EVIDENCE_DIRS],
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_candidate_reopen_authorized": status != "fail",
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
        "candidate_summary": {
            "best_cold_plus_collect_wall_speedup": max(wall_speedups),
            "largest_cold_plus_collect_wall_speedup": rows[-1][
                "optix_over_embree_cold_plus_collect_wall_speedup"
            ],
            "best_query_total_speedup": max(query_speedups),
            "best_runner_wall_speedup": max(runner_speedups),
            "native_query_handle_cache_observed": checks[
                "all_optix_native_cache_stats_observed"
            ],
        },
        "interpretation": (
            "The native prepared-query handle path changes AABB from useful cleanup "
            "to a real V3 performance candidate. On the RTX 4000 Ada pod, both "
            "serious rows clear the 1.20x cold-plus-collect floor against Embree "
            "under the same generic AABB candidate-stream contract. This still "
            "does not authorize release wording or M7 promotion until external "
            "review and Codex consensus close."
        ),
        "next_engine_action": (
            "Send this packet for external review. If accepted, update the Phoenix "
            "M7 row classification with an AABB native-query-handle row. Keep "
            "public copy row-scoped: generic AABB candidate streaming only, not "
            "full contact solving and not broad V3-over-V2 speedup."
        ),
        "forbidden_shortcuts": [
            "Do not call this a whole Contact Manifold solver speedup.",
            "Do not call this broad V3-over-V2 proof.",
            "Do not publish it before external review and Codex consensus.",
            "Do not hide the remaining prepare/collect phase costs.",
            "Do not generalize from AABB candidate streaming to every benchmark app.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record native prepared-query handle reuse as an M7 candidate "
                "pending external review, not as an already promoted V3 row."
            ),
            "was_i_foolish": (
                "No. This uses the predeclared serious scale, material wall floor, "
                "same hardware, and keeps release/M7 flags false before review."
            ),
            "foolish_actions": (
                "The foolish action would be to treat one 32k result as final, "
                "omit the 65k rerun, or promote a contact-specific story instead "
                "of the generic AABB contract."
            ),
            "other_path": (
                "I could have moved to a different app after the old no-go result, "
                "but the evidence pointed to native query lifetime as the actual "
                "generic bottleneck."
            ),
            "different_path_now": (
                "Continue through external review and M7 classification, then use "
                "the same pattern on the remaining generic-engine queue rather than "
                "hand-tuning app code."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 AABB Native Query-Handle Evidence",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This packet evaluates a generic engine change: OptiX AABB "
        "`range_intersection_rows` reuses prepared native box-query handles. "
        "The Contact Manifold fixture is only the evidence harness.",
        "",
        "## Candidate Summary",
        "",
        f"- Material wall-speedup floor: `{payload['material_wall_speedup_floor']:.2f}x`.",
        f"- Best cold-plus-collect wall speedup: "
        f"`{payload['candidate_summary']['best_cold_plus_collect_wall_speedup']:.3f}x`.",
        f"- Largest-scale cold-plus-collect wall speedup: "
        f"`{payload['candidate_summary']['largest_cold_plus_collect_wall_speedup']:.3f}x`.",
        f"- Best query-total speedup: "
        f"`{payload['candidate_summary']['best_query_total_speedup']:.3f}x`.",
        f"- Native query-handle cache observed: "
        f"`{payload['candidate_summary']['native_query_handle_cache_observed']}`.",
        "",
        "## Rows",
        "",
        "| grid_count | repeat | OptiX/Embree cold+collect | OptiX/Embree query total | OptiX native cache | CPU reference |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["observed_rows"]:
        lines.append(
            "| "
            f"{row['grid_count']} | "
            f"{row['repeat']} | "
            f"{row['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x | "
            f"{row['optix_over_embree_query_total_speedup']:.3f}x | "
            f"{row['optix_cache_stats']} | "
            f"{row['matches_cpu_reference']} |"
        )
    lines += [
        "",
        "## Boundaries",
        "",
        "- Release authorized: `False`.",
        "- Public speedup claim authorized: `False`.",
        "- Broad V3-over-V2 claim authorized: `False`.",
        "- M7 promotion authorized: `False` until external review and Codex consensus close.",
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "## Next Action",
        "",
        payload["next_engine_action"],
        "",
        "## Goal-Level Decision Audit",
        "",
    ]
    audit = payload["goal_level_decision_audit"]
    for key in (
        "decision",
        "was_i_foolish",
        "foolish_actions",
        "other_path",
        "different_path_now",
    ):
        lines.append(f"- `{key}`: {audit[key]}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    parser.add_argument("--md", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
