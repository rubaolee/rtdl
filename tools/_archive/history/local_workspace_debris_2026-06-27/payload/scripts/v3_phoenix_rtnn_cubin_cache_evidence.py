#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "rtnn_cubin_cache_20260621"
COLD_DIR = EVIDENCE_ROOT / "cold_optix"
WARM_DIR = EVIDENCE_ROOT / "warm_compare_venv"
CACHE_DIR = EVIDENCE_ROOT / "cache"
SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_optix_cubin_cache_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _ratio(before: float, after: float) -> float:
    return before / after if after else 0.0


def _phase(summary: dict[str, Any], route: str) -> dict[str, Any]:
    return summary["phase_rows"][route]


def build_payload() -> dict[str, Any]:
    cold = _read_json(COLD_DIR / "summary.json")
    warm = _read_json(WARM_DIR / "summary.json")
    cold_optix = _phase(cold, "optix")
    warm_optix = _phase(warm, "optix")
    warm_cupy = _phase(warm, "cupy_grid")
    cache_files = sorted(path for path in CACHE_DIR.glob("*.cubin") if path.is_file())
    source_text = SOURCE.read_text(encoding="utf-8")
    prelude_text = PRELUDE.read_text(encoding="utf-8")

    prepare_reduction = _ratio(
        float(cold_optix["execution_prepare_sec"]),
        float(warm_optix["execution_prepare_sec"]),
    )
    cold_plus_query_reduction = _ratio(
        float(cold_optix["cold_plus_query_wall_sec"]),
        float(warm_optix["cold_plus_query_wall_sec"]),
    )
    runner_wall_reduction = _ratio(
        float(cold_optix["runner_wall_sec"]),
        float(warm_optix["runner_wall_sec"]),
    )
    material_floor = float(warm["material_speedup_floor"])
    warm_runner_vs_cupy = float(warm["comparisons"]["rtdl_optix_over_cupy_grid_runner_wall_speedup"])
    warm_cold_plus_vs_cupy = float(
        warm["comparisons"]["rtdl_optix_over_cupy_grid_cold_plus_query_speedup"]
    )

    checks = {
        "cold_summary_exists": (COLD_DIR / "summary.json").exists(),
        "warm_summary_exists": (WARM_DIR / "summary.json").exists(),
        "cache_file_exists": bool(cache_files),
        "cache_env_controls_in_source": (
            "RTDL_OPTIX_CUBIN_CACHE_DIR" in source_text
            and "RTDL_OPTIX_DISABLE_CUBIN_CACHE" in source_text
        ),
        "prelude_documents_cross_process_cache": "content-addressed disk cache" in prelude_text,
        "warm_runner_completed": warm.get("runner_completed") is True,
        "warm_failed_checks_empty": warm.get("failed_checks") == [],
        "warm_same_contract_signature_match": warm.get("parity", {}).get(
            "same_contract_signature_match"
        )
        is True,
        "integer_signature_match": warm.get("parity", {}).get("integer_signature_match") is True,
        "serious_scale": int(warm["parameters"]["point_count"]) >= 1_048_576,
        "repeat5": int(warm["parameters"]["repeat"]) == 5,
        "prepare_reduced_at_least_2x": prepare_reduction >= 2.0,
        "cold_plus_query_reduced_at_least_1_5x": cold_plus_query_reduction >= 1.5,
        "runner_wall_reduced_at_least_1_5x": runner_wall_reduction >= 1.5,
        "hot_speedup_still_material": float(
            warm["comparisons"]["rtdl_optix_over_cupy_grid_hot_speedup"]
        )
        >= material_floor,
        "warm_runner_positive_vs_cupy": warm_runner_vs_cupy > 1.0,
        "warm_runner_below_material_floor": warm_runner_vs_cupy < material_floor,
        "warm_cold_plus_query_still_loses": warm_cold_plus_vs_cupy < 1.0,
        "release_flags_false": warm.get("release_authorized") is False
        and warm.get("public_speedup_claim_authorized") is False
        and warm.get("whole_app_speedup_claim_authorized") is False
        and warm.get("broad_v3_faster_than_v2_claim_authorized") is False
        and warm.get("m7_promotion_authorized") is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "rtnn_optix_cubin_cache_reduces_prepare_not_m7_wall_floor_not_met"
    )

    return {
        "tool": "v3_phoenix_rtnn_cubin_cache_evidence",
        "status": status,
        "generic_capability": "optix_cubin_cache_for_ranked_summary_prepare_path",
        "candidate_scope": (
            "generic OptiX CUBIN content-addressed disk cache; RTNN ranked_summary is the "
            "serious evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": False,
        "cache_controls": {
            "cache_dir_env": "RTDL_OPTIX_CUBIN_CACHE_DIR",
            "disable_env": "RTDL_OPTIX_DISABLE_CUBIN_CACHE",
            "cache_files": [_rel(path) for path in cache_files],
            "cache_bytes": sum(path.stat().st_size for path in cache_files),
        },
        "evidence": {
            "cold_optix": _rel(COLD_DIR),
            "warm_compare": _rel(WARM_DIR),
            "cold_summary": _rel(COLD_DIR / "summary.json"),
            "warm_summary": _rel(WARM_DIR / "summary.json"),
        },
        "hardware": warm["environment"]["hardware_gate"]["gpus"][0],
        "cold_optix": {
            "execution_prepare_sec": cold_optix["execution_prepare_sec"],
            "cold_plus_query_wall_sec": cold_optix["cold_plus_query_wall_sec"],
            "runner_wall_sec": cold_optix["runner_wall_sec"],
            "hot_query_median_sec": cold_optix["hot_query_median_sec"],
        },
        "warm_optix": {
            "execution_prepare_sec": warm_optix["execution_prepare_sec"],
            "cold_plus_query_wall_sec": warm_optix["cold_plus_query_wall_sec"],
            "runner_wall_sec": warm_optix["runner_wall_sec"],
            "hot_query_median_sec": warm_optix["hot_query_median_sec"],
            "input_pack_sec": warm_optix["input_pack_sec"],
        },
        "warm_cupy_grid": {
            "grid_prepare_sec": warm_cupy["grid_prepare_sec"],
            "cold_plus_query_wall_sec": warm_cupy["cold_plus_query_wall_sec"],
            "runner_wall_sec": warm_cupy["runner_wall_sec"],
            "hot_query_median_sec": warm_cupy["hot_query_median_sec"],
        },
        "improvement_vs_cold_optix": {
            "execution_prepare_reduction": prepare_reduction,
            "cold_plus_query_reduction": cold_plus_query_reduction,
            "runner_wall_reduction": runner_wall_reduction,
        },
        "warm_comparison_vs_cupy_grid": warm["comparisons"],
        "parity": warm["parity"],
        "not_m7_blockers": [
            "Warm-cache OptiX/CuPy runner-wall speedup is positive but only 1.098x, below the 2.0x material floor.",
            "Warm-cache OptiX/CuPy cold-plus-query speedup is 0.794x, so cold-plus-query still loses.",
            "Input load and OptiX input_pack remain large; the cache only addresses CUBIN compilation/module preparation.",
            "No external Claude/Gemini review has accepted this candidate.",
            "This does not authorize RTNN whole-app, V2 comparison, or broad V3 speedup wording.",
        ],
        "interpretation": (
            "The content-addressed CUBIN cache is a real generic OptiX backend improvement: "
            "on the RTX 4000 Ada POD it reduced RTNN evidence-harness execution_prepare "
            "from 3.337s to 0.564s (5.914x), cold-plus-query from 5.418s to 2.635s "
            "(2.056x), and runner wall from 6.122s to 3.431s (1.785x). It does not "
            "make the RTNN row M7. Warm-cache OptiX still loses cold-plus-query to CuPy "
            "at 0.794x and clears runner wall by only 1.098x, below the material floor."
        ),
        "next_engine_action": (
            "Keep RTNN ranked_summary open. The next reusable work is input-pack/device-column "
            "reuse or persistent prepared-session amortization; do not tune RTNN-specific logic "
            "or publish the hot-query win as an end-to-end result."
        ),
        "forbidden_shortcuts": [
            "Do not call 1.098x runner-wall speedup a Phoenix V3 performance win.",
            "Do not quote the 7.740x hot-query speedup without the warm-cache and prepared-query boundary.",
            "Do not claim CUBIN cache solves RTNN wall time.",
            "Do not promote this row to M7 without external review and a material wall-speedup result.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record the generic OptiX CUBIN cache as a real blocker reduction, but keep "
                "RTNN ranked_summary out of M7 because material wall speed is still missing."
            ),
            "was_i_foolish": (
                "No. The decision separates a reusable backend improvement from a release claim."
            ),
            "foolish_actions": (
                "It would be foolish to treat the 7.740x hot-query result or the 1.098x "
                "runner-wall result as a V3 win while cold-plus-query still loses."
            ),
            "other_path": (
                "I could have tuned RTNN-specific code or polished docs. That would not have "
                "attacked the measured generic OptiX startup blocker."
            ),
            "different_path_now": (
                "Use the cache result as a stepping stone and work on reusable input-pack or "
                "prepared-session amortization before asking for M7 review."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 RTNN OptiX CUBIN Cache Evidence",
        "",
        f"Status: `{payload['status']}`.",
        "",
        payload["interpretation"],
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"whole_app_speedup_claim_authorized: {str(payload['whole_app_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Cache Controls",
        "",
        f"- Cache dir env: `{payload['cache_controls']['cache_dir_env']}`",
        f"- Disable env: `{payload['cache_controls']['disable_env']}`",
        f"- Cache bytes captured: `{payload['cache_controls']['cache_bytes']}`",
        "",
        "## POD Result",
        "",
        f"- GPU: `{payload['hardware']['name']}`",
        f"- Cold OptiX execution prepare: `{payload['cold_optix']['execution_prepare_sec']:.3f}s`",
        f"- Warm OptiX execution prepare: `{payload['warm_optix']['execution_prepare_sec']:.3f}s`",
        f"- Prepare reduction: `{payload['improvement_vs_cold_optix']['execution_prepare_reduction']:.3f}x`",
        f"- Cold-plus-query reduction: `{payload['improvement_vs_cold_optix']['cold_plus_query_reduction']:.3f}x`",
        f"- Runner-wall reduction: `{payload['improvement_vs_cold_optix']['runner_wall_reduction']:.3f}x`",
        f"- Warm OptiX/CuPy hot-query speedup: `{payload['warm_comparison_vs_cupy_grid']['rtdl_optix_over_cupy_grid_hot_speedup']:.3f}x`",
        f"- Warm OptiX/CuPy cold-plus-query speedup: `{payload['warm_comparison_vs_cupy_grid']['rtdl_optix_over_cupy_grid_cold_plus_query_speedup']:.3f}x`",
        f"- Warm OptiX/CuPy runner-wall speedup: `{payload['warm_comparison_vs_cupy_grid']['rtdl_optix_over_cupy_grid_runner_wall_speedup']:.3f}x`",
        "",
        "## Not-M7 Blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["not_m7_blockers"])
    lines.extend(
        [
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
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 RTNN OptiX CUBIN cache evidence.")
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
                    "prepare_reduction": payload["improvement_vs_cold_optix"][
                        "execution_prepare_reduction"
                    ],
                    "runner_wall_speedup": payload["warm_comparison_vs_cupy_grid"][
                        "rtdl_optix_over_cupy_grid_runner_wall_speedup"
                    ],
                },
                sort_keys=True,
            )
        )
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return (
        0
        if payload["status"]
        == "rtnn_optix_cubin_cache_reduces_prepare_not_m7_wall_floor_not_met"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
