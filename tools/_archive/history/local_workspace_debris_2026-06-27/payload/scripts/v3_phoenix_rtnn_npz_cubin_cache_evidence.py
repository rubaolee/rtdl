#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_npz_cubin_cache_1048576_r5_20260621"
)
COLD_DIR = EVIDENCE_ROOT / "cold_compare"
WARM_DIR = EVIDENCE_ROOT / "warm_compare"
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_npz_cubin_cache_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(before: float, after: float) -> float:
    return before / after if after else 0.0


def _phase(summary: dict[str, Any], route: str) -> dict[str, Any]:
    return summary["phase_rows"][route]


def _release_flags_false(summary: dict[str, Any]) -> bool:
    return (
        summary.get("release_authorized") is False
        and summary.get("public_speedup_claim_authorized") is False
        and summary.get("whole_app_speedup_claim_authorized") is False
        and summary.get("broad_v3_faster_than_v2_claim_authorized") is False
        and summary.get("m7_promotion_authorized") is False
    )


def _route_summary(row: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "input_load_sec": float(row.get("input_load_sec", 0.0)),
        "hot_query_median_sec": float(row.get("hot_query_median_sec", 0.0)),
        "cold_plus_query_wall_sec": float(row.get("cold_plus_query_wall_sec", 0.0)),
        "runner_wall_sec": float(row.get("runner_wall_sec", 0.0)),
        "point_column_source": row.get("point_column_source"),
        "point_column_file": row.get("point_column_file"),
    }
    if "input_pack_sec" in row:
        payload["input_pack_sec"] = float(row.get("input_pack_sec", 0.0))
    if "execution_prepare_sec" in row:
        payload["execution_prepare_sec"] = float(row.get("execution_prepare_sec", 0.0))
    if "grid_prepare_sec" in row:
        payload["grid_prepare_sec"] = float(row.get("grid_prepare_sec", 0.0))
    return payload


def build_payload() -> dict[str, Any]:
    cold = _read_json(COLD_DIR / "summary.json")
    warm = _read_json(WARM_DIR / "summary.json")
    cold_optix = _phase(cold, "optix")
    warm_optix = _phase(warm, "optix")
    warm_cupy = _phase(warm, "cupy_grid")
    material_floor = float(warm.get("material_speedup_floor", 2.0))
    warm_runner = float(warm["comparisons"]["rtdl_optix_over_cupy_grid_runner_wall_speedup"])
    warm_cold_plus = float(
        warm["comparisons"]["rtdl_optix_over_cupy_grid_cold_plus_query_speedup"]
    )
    warm_hot = float(warm["comparisons"]["rtdl_optix_over_cupy_grid_hot_speedup"])
    warm_non_hot = (
        float(warm_optix["input_load_sec"])
        + float(warm_optix.get("input_pack_sec", 0.0))
        + float(warm_optix.get("execution_prepare_sec", 0.0))
    )
    warm_hot_sec = float(warm_optix["hot_query_median_sec"])

    cache_after_warm = EVIDENCE_ROOT / "cache_after_warm.txt"
    cache_text = cache_after_warm.read_text(encoding="utf-8") if cache_after_warm.exists() else ""
    checks = {
        "cold_summary_exists": (COLD_DIR / "summary.json").exists(),
        "warm_summary_exists": (WARM_DIR / "summary.json").exists(),
        "hardware_gate_passed": _read_json(EVIDENCE_ROOT / "optix_hardware_gate.json").get("status")
        == "pass",
        "cache_file_observed": ".cubin" in cache_text,
        "cold_runner_completed": cold.get("runner_completed") is True,
        "warm_runner_completed": warm.get("runner_completed") is True,
        "warm_failed_checks_empty": warm.get("failed_checks") == [],
        "same_contract_signature_match": warm.get("parity", {}).get(
            "same_contract_signature_match"
        )
        is True,
        "integer_signature_match": warm.get("parity", {}).get("integer_signature_match") is True,
        "serious_scale": int(warm["parameters"]["point_count"]) >= 1_048_576,
        "repeat5": int(warm["parameters"]["repeat"]) == 5,
        "npz_source_recorded_on_both_routes": (
            warm_optix.get("point_column_source") == "npz"
            and warm_cupy.get("point_column_source") == "npz"
        ),
        "cache_reduces_execution_prepare_at_least_2x": _ratio(
            float(cold_optix["execution_prepare_sec"]),
            float(warm_optix["execution_prepare_sec"]),
        )
        >= 2.0,
        "cache_reduces_runner_wall_at_least_2x": _ratio(
            float(cold_optix["runner_wall_sec"]),
            float(warm_optix["runner_wall_sec"]),
        )
        >= 2.0,
        "hot_speedup_is_material": warm_hot >= material_floor,
        "runner_wall_positive_vs_cupy": warm_runner > 1.0,
        "runner_wall_below_material_floor": warm_runner < material_floor,
        "cold_plus_positive_vs_cupy": warm_cold_plus > 1.0,
        "cold_plus_below_material_floor": warm_cold_plus < material_floor,
        "release_flags_false": _release_flags_false(warm),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "rtnn_npz_cubin_cache_wall_improves_not_m7_material_floor_not_met"
    )

    return {
        "tool": "v3_phoenix_rtnn_npz_cubin_cache_evidence",
        "status": status,
        "generic_capability": "fixed_radius_neighbors_3d_npz_ingestion_plus_optix_cubin_cache",
        "candidate_scope": (
            "generic RTNN fixed-radius ranked-summary input-column ingestion plus generic "
            "OptiX CUBIN cache; RTNN is the evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": False,
        "material_speedup_floor": material_floor,
        "checks": checks,
        "failed_checks": failed_checks,
        "evidence": {
            "root": str(EVIDENCE_ROOT.relative_to(ROOT)).replace("\\", "/"),
            "cold_summary": str((COLD_DIR / "summary.json").relative_to(ROOT)).replace("\\", "/"),
            "warm_summary": str((WARM_DIR / "summary.json").relative_to(ROOT)).replace("\\", "/"),
            "source_manifest": str((EVIDENCE_ROOT / "source_manifest.sha256").relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "run_log": str((EVIDENCE_ROOT / "run.log").relative_to(ROOT)).replace("\\", "/"),
        },
        "measurements": {
            "cold_optix": _route_summary(cold_optix),
            "warm_optix": _route_summary(warm_optix),
            "warm_cupy_grid": _route_summary(warm_cupy),
        },
        "cache_reductions": {
            "execution_prepare": _ratio(
                float(cold_optix["execution_prepare_sec"]),
                float(warm_optix["execution_prepare_sec"]),
            ),
            "cold_plus_query": _ratio(
                float(cold_optix["cold_plus_query_wall_sec"]),
                float(warm_optix["cold_plus_query_wall_sec"]),
            ),
            "runner_wall": _ratio(
                float(cold_optix["runner_wall_sec"]),
                float(warm_optix["runner_wall_sec"]),
            ),
        },
        "warm_comparison_vs_cupy_grid": {
            "hot_query_speedup": warm_hot,
            "cold_plus_query_speedup": warm_cold_plus,
            "runner_wall_speedup": warm_runner,
        },
        "remaining_overhead": {
            "warm_optix_non_hot_sec": warm_non_hot,
            "warm_optix_non_hot_over_hot_query": _ratio(warm_non_hot, warm_hot_sec),
            "warm_optix_input_pack_plus_prepare_sec": float(warm_optix.get("input_pack_sec", 0.0))
            + float(warm_optix.get("execution_prepare_sec", 0.0)),
        },
        "parity": warm.get("parity"),
        "not_m7_blockers": [
            "Warm NPZ+CUBIN runner-wall speedup is 1.328x, below the 2.0x material floor.",
            "Warm NPZ+CUBIN cold-plus-query speedup is 1.247x, below the 2.0x material floor.",
            "The non-hot OptiX path is still about 42x the hot query, so prepare/pack/session overhead remains the blocker.",
            "No external Claude/Gemini review has accepted this as an M7 row.",
        ],
        "next_engine_action": (
            "Keep RTNN ranked_summary open. The next reusable work is prepared-session "
            "amortization or device-column pack reuse; do not publish RTNN wall-speedup "
            "wording from a 1.328x runner-wall result."
        ),
        "forbidden_shortcuts": [
            "Do not call 1.328x runner-wall speedup a Phoenix V3 material performance win.",
            "Do not quote the 7.784x hot-query speedup without the warm-cache and wall-time boundary.",
            "Do not promote RTNN to M7 from this packet.",
            "Do not claim whole-app, V2 comparison, or broad V3 speedup wording.",
        ],
        "goal_level_decision_audit": {
            "decision": (
                "Combine the V3 NPZ input-column path with the generic OptiX CUBIN cache "
                "on the RTX POD, but keep RTNN not M7 because material wall speed is still missing."
            ),
            "was_i_foolish": (
                "No. This tests two reusable V3 engine improvements together and still blocks "
                "promotion when the material floor is not met."
            ),
            "foolish_actions": (
                "It would be foolish to treat the hot-query result or the new 1.328x runner-wall "
                "result as a release-grade RTNN win."
            ),
            "other_path": (
                "I could have stopped after the NPZ-only rerun, but that would ignore the existing "
                "generic CUBIN cache improvement and leave the blocker diagnosis incomplete."
            ),
            "different_path_now": (
                "Work on reusable prepared-session amortization or input-pack/device-column reuse, "
                "or switch to another P0 generic engine item if RTNN remains below the floor."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    c = payload["warm_comparison_vs_cupy_grid"]
    r = payload["cache_reductions"]
    m = payload["measurements"]
    overhead = payload["remaining_overhead"]
    lines = [
        "# Phoenix V3 RTNN NPZ + CUBIN Cache Evidence",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet records a real reusable V3 improvement, not a release win: NPZ "
        "column ingestion removes the earlier input-load wall, and the generic OptiX "
        "CUBIN cache removes most repeated compile/prepare cost. The combined route "
        "is still not M7 because full wall speed is below the material floor.",
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "m7_promotion_authorized: false",
        "```",
        "",
        "## POD Result",
        "",
        f"- Warm OptiX/CuPy hot-query speedup: `{c['hot_query_speedup']:.3f}x`",
        f"- Warm OptiX/CuPy cold-plus-query speedup: `{c['cold_plus_query_speedup']:.3f}x`",
        f"- Warm OptiX/CuPy runner-wall speedup: `{c['runner_wall_speedup']:.3f}x`",
        f"- CUBIN execution-prepare reduction: `{r['execution_prepare']:.3f}x`",
        f"- CUBIN cold-plus-query reduction: `{r['cold_plus_query']:.3f}x`",
        f"- CUBIN runner-wall reduction: `{r['runner_wall']:.3f}x`",
        "",
        "## Warm Phase Rows",
        "",
        "| route | input load | pack/prepare | hot query | cold+query | runner wall |",
        "|---|---:|---:|---:|---:|---:|",
        (
            f"| RTDL OptiX | {m['warm_optix']['input_load_sec']:.6f}s | "
            f"{m['warm_optix']['input_pack_sec'] + m['warm_optix']['execution_prepare_sec']:.6f}s | "
            f"{m['warm_optix']['hot_query_median_sec']:.6f}s | "
            f"{m['warm_optix']['cold_plus_query_wall_sec']:.6f}s | "
            f"{m['warm_optix']['runner_wall_sec']:.6f}s |"
        ),
        (
            f"| CuPy grid | {m['warm_cupy_grid']['input_load_sec']:.6f}s | "
            f"{m['warm_cupy_grid']['grid_prepare_sec']:.6f}s | "
            f"{m['warm_cupy_grid']['hot_query_median_sec']:.6f}s | "
            f"{m['warm_cupy_grid']['cold_plus_query_wall_sec']:.6f}s | "
            f"{m['warm_cupy_grid']['runner_wall_sec']:.6f}s |"
        ),
        "",
        "## Not M7",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["not_m7_blockers"])
    lines.extend(
        [
            "",
            "## Remaining Blocker",
            "",
            (
                f"- Warm OptiX non-hot path: `{overhead['warm_optix_non_hot_sec']:.6f}s`, "
                f"`{overhead['warm_optix_non_hot_over_hot_query']:.3f}x` the hot query."
            ),
            (
                f"- Warm OptiX pack+prepare: "
                f"`{overhead['warm_optix_input_pack_plus_prepare_sec']:.6f}s`."
            ),
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
            f"Decision: {payload['goal_level_decision_audit']['decision']}",
            "",
            f"1. Was I foolish? {payload['goal_level_decision_audit']['was_i_foolish']}",
            (
                "2. If yes, what actions made the decision foolish? "
                f"{payload['goal_level_decision_audit']['foolish_actions']}"
            ),
            (
                "3. Was there another path that would have avoided getting stuck on that idea? "
                f"{payload['goal_level_decision_audit']['other_path']}"
            ),
            (
                "4. Can I now try a different path that actually solves the problem? "
                f"{payload['goal_level_decision_audit']['different_path_now']}"
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit Phoenix V3 RTNN NPZ+CUBIN cache POD evidence packet."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["status"] != "fail" else 2


if __name__ == "__main__":
    raise SystemExit(main())
