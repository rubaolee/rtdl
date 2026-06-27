#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence"
MAIN_EVIDENCE_DIR = EVIDENCE_ROOT / "rtnn_full_batch_float32_same_contract_1048576_r5_20260621"
SUPPLEMENTAL_EVIDENCE_DIRS = (
    EVIDENCE_ROOT / "rtnn_full_batch_float32_same_contract_262144_r3_20260621",
    EVIDENCE_ROOT / "rtnn_full_batch_float32_same_contract_1048576_r3_20260621",
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_summary(evidence_dir: Path) -> dict[str, Any]:
    summary_path = evidence_dir / "summary.json"
    summary = _read_json(summary_path)
    summary["_evidence_dir"] = _rel(evidence_dir)
    summary["_summary_path"] = _rel(summary_path)
    return summary


def _scale_row(summary: dict[str, Any]) -> dict[str, Any]:
    params = summary["parameters"]
    comparisons = summary["comparisons"]
    optix = summary["phase_rows"]["optix"]
    cupy = summary["phase_rows"]["cupy_grid"]
    parity = summary["parity"]
    return {
        "evidence_dir": summary["_evidence_dir"],
        "point_count": int(params["point_count"]),
        "repeat": int(params["repeat"]),
        "distribution": params["distribution"],
        "radius": float(params["radius"]),
        "k_max": int(params["k_max"]),
        "same_contract_signature_match": bool(parity["same_contract_signature_match"]),
        "sum_distance_relative_error": float(parity["sum_distance_relative_error"]),
        "optix_hot_query_median_sec": float(optix["hot_query_median_sec"]),
        "cupy_grid_hot_query_median_sec": float(cupy["hot_query_median_sec"]),
        "optix_cold_plus_query_wall_sec": float(optix["cold_plus_query_wall_sec"]),
        "cupy_grid_cold_plus_query_wall_sec": float(cupy["cold_plus_query_wall_sec"]),
        "optix_runner_wall_sec": float(optix["runner_wall_sec"]),
        "cupy_grid_runner_wall_sec": float(cupy["runner_wall_sec"]),
        "hot_speedup_optix_over_cupy_grid": float(
            comparisons["rtdl_optix_over_cupy_grid_hot_speedup"]
        ),
        "cold_plus_query_speedup_optix_over_cupy_grid": float(
            comparisons["rtdl_optix_over_cupy_grid_cold_plus_query_speedup"]
        ),
        "runner_wall_speedup_optix_over_cupy_grid": float(
            comparisons["rtdl_optix_over_cupy_grid_runner_wall_speedup"]
        ),
    }


def build_payload() -> dict[str, Any]:
    main = _load_summary(MAIN_EVIDENCE_DIR)
    supplemental = [_load_summary(path) for path in SUPPLEMENTAL_EVIDENCE_DIRS]
    scale_rows = [_scale_row(row) for row in [*supplemental, main]]
    main_row = _scale_row(main)
    env = main["environment"]
    hardware_gate = env["hardware_gate"]
    material_floor = float(main["material_speedup_floor"])

    checks = {
        "main_summary_exists": (MAIN_EVIDENCE_DIR / "summary.json").exists(),
        "supplemental_summaries_exist": all(
            (path / "summary.json").exists() for path in SUPPLEMENTAL_EVIDENCE_DIRS
        ),
        "runner_status_pending_2ai_not_m7": main.get("status")
        == "rtnn_full_batch_float32_same_contract_pod_evidence_pending_2ai_not_m7",
        "runner_completed": main.get("runner_completed") is True,
        "failed_checks_empty": main.get("failed_checks") == [],
        "serious_scale_1m": int(main["parameters"]["point_count"]) >= 1_048_576,
        "repeat5_main": int(main["parameters"]["repeat"]) == 5,
        "hardware_gate_pass": hardware_gate.get("status") == "pass",
        "same_contract_signature_match": main["parity"].get("same_contract_signature_match")
        is True,
        "integer_signature_match": main["parity"].get("integer_signature_match") is True,
        "sum_distance_within_tolerance": float(main["parity"]["sum_distance_relative_error"])
        <= float(main["parity"]["sum_distance_relative_tolerance"]),
        "hot_speedup_material": main_row["hot_speedup_optix_over_cupy_grid"] >= material_floor,
        "cold_plus_query_wall_regresses": main_row[
            "cold_plus_query_speedup_optix_over_cupy_grid"
        ]
        < 1.0,
        "runner_wall_regresses": main_row["runner_wall_speedup_optix_over_cupy_grid"] < 1.0,
        "release_flags_false": main.get("release_authorized") is False
        and main.get("public_speedup_claim_authorized") is False
        and main.get("whole_app_speedup_claim_authorized") is False
        and main.get("broad_v3_faster_than_v2_claim_authorized") is False
        and main.get("m7_promotion_authorized") is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7"
    )

    return {
        "tool": "v3_phoenix_rtnn_full_batch_float32_pod_evidence",
        "version": "phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026_06_21",
        "status": status,
        "generic_capability": "ranked_summary",
        "candidate_scope": (
            "generic fixed_radius_neighbors_3d ranked_summary full-batch float32 aggregate; "
            "RTNN is only the evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": status != "fail",
        "m7_reopen_candidate_scope": (
            "prepared hot-query only, after data is loaded, packed, and the OptiX plan is prepared"
        ),
        "not_m7_blockers": [
            "No external Claude/Gemini review has accepted the exact row.",
            "OptiX loses the cold-plus-query wall comparison to the same-contract CuPy grid reference.",
            "OptiX loses runner wall time to the same-contract CuPy grid reference.",
            "The RTDL route is float32 and exact=false, while the CuPy grid reference is exact.",
            "The row does not authorize RTNN whole-app, paper reproduction, V2 comparison, or universal NN claims.",
        ],
        "evidence": {
            "main": main["_evidence_dir"],
            "main_summary": main["_summary_path"],
            "supplemental": [row["_evidence_dir"] for row in supplemental],
        },
        "hardware": {
            "host": "root@213.173.108.14 -p 11592",
            "gpu": hardware_gate["gpus"][0]["name"],
            "driver_version": hardware_gate["gpus"][0]["driver_version"],
            "compute_cap": hardware_gate["gpus"][0]["compute_cap"],
            "rt_hardware_gate": hardware_gate["status"],
            "rtdl_optix_library": env["env"]["RTDL_OPTIX_LIBRARY"],
        },
        "main_row": main_row,
        "scale_rows": scale_rows,
        "parity": {
            "same_contract_signature_match": main["parity"]["same_contract_signature_match"],
            "integer_signature_match": main["parity"]["integer_signature_match"],
            "sum_distance_relative_error": main["parity"]["sum_distance_relative_error"],
            "sum_distance_relative_tolerance": main["parity"]["sum_distance_relative_tolerance"],
            "delta_optix_minus_cupy_grid": main["parity"]["delta_optix_minus_cupy_grid"],
        },
        "phase_rows": {
            "optix": main["phase_rows"]["optix"],
            "cupy_grid": main["phase_rows"]["cupy_grid"],
        },
        "interpretation": (
            "The 1,048,576-point repeat5 run is strong evidence that the prepared RTDL "
            "OptiX ranked_summary aggregate has a reusable hot-query advantage over a "
            "same-contract CuPy CUDA-core grid reference: 7.790x on the median hot query "
            "with matching integer signatures and a 1.21e-10 relative sum-distance error. "
            "It is not an end-to-end RTNN win. OptiX still loses cold-plus-query wall "
            "time at 0.393x and runner wall time at 0.627x because load, pack, and "
            "OptiX execution preparation dominate. This may be reviewed only as a "
            "prepared-hot-query candidate; wall/end-to-end wording remains blocked."
        ),
        "next_engine_action": (
            "Keep RTNN ranked_summary open. The next valid engine work is to reduce or "
            "amortize OptiX pack/prepare overhead, add a stricter exact/tie-stable path, "
            "or seek external review for a narrowly worded prepared-hot-query row."
        ),
        "forbidden_shortcuts": [
            "Do not call this RTNN M7 without external review and Codex consensus.",
            "Do not claim RTDL beats CuPy grid end-to-end or wall-clock on this row.",
            "Do not claim V3 solves nearest-neighbor workloads in general.",
            "Do not quote the 7.790x hot-query speedup without saying prepared-hot-query only.",
            "Do not reuse the old M106 787x-vs-Embree figure as public evidence.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Classify the fresh RTNN full-batch float32 same-contract RTX run as a "
                "prepared-hot-query candidate, not as an M7 or end-to-end win."
            ),
            "was_i_foolish": (
                "No. The classification keeps the substantial hot-query improvement and "
                "the wall-time regression visible at the same time."
            ),
            "foolish_actions": (
                "The foolish action would be to market the 7.790x hot-query number while "
                "hiding the 0.393x cold-plus-query and 0.627x runner-wall regressions."
            ),
            "other_path": (
                "Reject RTNN entirely because wall time loses, or promote it entirely "
                "because hot time wins. Either path would erase important evidence."
            ),
            "different_path_now": (
                "Treat the row as a narrow candidate and direct engine work toward "
                "pack/prepare amortization or exact/tie-stable parity before promotion."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    main = payload["main_row"]
    lines = [
        "# Phoenix V3 RTNN Full-Batch Float32 Same-Contract RTX Evidence",
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
        "## Hardware",
        "",
        f"- Host: `{payload['hardware']['host']}`",
        f"- GPU: `{payload['hardware']['gpu']}`",
        f"- Driver: `{payload['hardware']['driver_version']}`",
        f"- Compute capability: `{payload['hardware']['compute_cap']}`",
        f"- RT hardware gate: `{payload['hardware']['rt_hardware_gate']}`",
        f"- OptiX library: `{payload['hardware']['rtdl_optix_library']}`",
        "",
        "## Main Row",
        "",
        f"- Evidence: `{payload['evidence']['main']}`",
        f"- Points/repeat: `{main['point_count']}` / `{main['repeat']}`",
        f"- Same-contract signature match: `{str(main['same_contract_signature_match']).lower()}`",
        f"- Sum-distance relative error: `{main['sum_distance_relative_error']:.3e}`",
        f"- OptiX/CuPy hot-query speedup: `{main['hot_speedup_optix_over_cupy_grid']:.3f}x`",
        f"- OptiX/CuPy cold-plus-query speedup: `{main['cold_plus_query_speedup_optix_over_cupy_grid']:.3f}x`",
        f"- OptiX/CuPy runner-wall speedup: `{main['runner_wall_speedup_optix_over_cupy_grid']:.3f}x`",
        "",
        "## Scale Rows",
        "",
        "| Points | Repeat | Hot speedup | Cold+query speedup | Runner wall speedup | Parity |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in payload["scale_rows"]:
        lines.append(
            f"| {row['point_count']} | {row['repeat']} | "
            f"{row['hot_speedup_optix_over_cupy_grid']:.3f}x | "
            f"{row['cold_plus_query_speedup_optix_over_cupy_grid']:.3f}x | "
            f"{row['runner_wall_speedup_optix_over_cupy_grid']:.3f}x | "
            f"{str(row['same_contract_signature_match']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Not-M7 Blockers",
            "",
        ]
    )
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
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 RTNN same-contract RTX evidence packet.")
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
                    "hot_speedup": payload["main_row"]["hot_speedup_optix_over_cupy_grid"],
                    "runner_wall_speedup": payload["main_row"][
                        "runner_wall_speedup_optix_over_cupy_grid"
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
        == "rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
