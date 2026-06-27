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
    / "phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621"
)
CACHE_FILL_DIR = EVIDENCE_ROOT / "cache_fill"
REPEAT50_DIR = EVIDENCE_ROOT / "repeat50_compare"
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _phase(summary: dict[str, Any], route: str) -> dict[str, Any]:
    return summary["phase_rows"][route]


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


def _release_flags_false(summary: dict[str, Any]) -> bool:
    return (
        summary.get("release_authorized") is False
        and summary.get("public_speedup_claim_authorized") is False
        and summary.get("whole_app_speedup_claim_authorized") is False
        and summary.get("broad_v3_faster_than_v2_claim_authorized") is False
        and summary.get("m7_promotion_authorized") is False
    )


def build_payload() -> dict[str, Any]:
    cache_fill = _read_json(CACHE_FILL_DIR / "summary.json")
    repeat50 = _read_json(REPEAT50_DIR / "summary.json")
    optix = _phase(repeat50, "optix")
    cupy = _phase(repeat50, "cupy_grid")
    material_floor = float(repeat50.get("material_speedup_floor", 2.0))
    comparisons = repeat50["comparisons"]
    runner_speedup = float(comparisons["rtdl_optix_over_cupy_grid_runner_wall_speedup"])
    cold_plus_speedup = float(
        comparisons["rtdl_optix_over_cupy_grid_cold_plus_query_speedup"]
    )
    hot_speedup = float(comparisons["rtdl_optix_over_cupy_grid_hot_speedup"])
    repeat = int(repeat50["parameters"]["repeat"])
    point_count = int(repeat50["parameters"]["point_count"])
    candidate_row_id = (
        "rtnn_prepared_ranked_summary_npz_cubin_repeat50_"
        "1048576_points_k50_radius_0_02"
    )
    cache_after_fill = EVIDENCE_ROOT / "cache_after_fill.txt"
    cache_text = cache_after_fill.read_text(encoding="utf-8") if cache_after_fill.exists() else ""

    checks = {
        "cache_fill_summary_exists": (CACHE_FILL_DIR / "summary.json").exists(),
        "repeat50_summary_exists": (REPEAT50_DIR / "summary.json").exists(),
        "hardware_gate_passed": _read_json(EVIDENCE_ROOT / "optix_hardware_gate.json").get(
            "status"
        )
        == "pass",
        "cubin_cache_file_observed": ".cubin" in cache_text,
        "cache_fill_completed": cache_fill.get("runner_completed") is True,
        "repeat50_completed": repeat50.get("runner_completed") is True,
        "repeat50_failed_checks_empty": repeat50.get("failed_checks") == [],
        "same_contract_signature_match": repeat50.get("parity", {}).get(
            "same_contract_signature_match"
        )
        is True,
        "integer_signature_match": repeat50.get("parity", {}).get("integer_signature_match")
        is True,
        "serious_scale_1m": point_count >= 1_048_576,
        "repeat50": repeat == 50,
        "npz_source_recorded_on_both_routes": (
            optix.get("point_column_source") == "npz"
            and cupy.get("point_column_source") == "npz"
        ),
        "hot_speedup_material": hot_speedup >= material_floor,
        "runner_wall_speedup_material": runner_speedup >= material_floor,
        "cold_plus_query_below_material_floor": cold_plus_speedup < material_floor,
        "external_review_missing": True,
        "release_flags_false": _release_flags_false(repeat50),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "rtnn_prepared_repeat50_amortization_m7_candidate_pending_external_review_not_release"
    )

    return {
        "tool": "v3_phoenix_rtnn_prepared_repeat50_amortization_evidence",
        "status": status,
        "generic_capability": "fixed_radius_neighbors_3d_prepared_session_amortization",
        "candidate_scope": (
            "row-scoped prepared repeated-session ranked-summary aggregate; RTNN is the "
            "evidence harness, not a whole-app or paper-equivalent claim"
        ),
        "candidate_row_ids": [candidate_row_id],
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": True,
        "material_speedup_floor": material_floor,
        "checks": checks,
        "failed_checks": failed_checks,
        "evidence": {
            "root": str(EVIDENCE_ROOT.relative_to(ROOT)).replace("\\", "/"),
            "repeat50_summary": str((REPEAT50_DIR / "summary.json").relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "cache_fill_summary": str((CACHE_FILL_DIR / "summary.json").relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "source_manifest": str((EVIDENCE_ROOT / "source_manifest.sha256").relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "run_log": str((EVIDENCE_ROOT / "run.log").relative_to(ROOT)).replace("\\", "/"),
        },
        "parameters": {
            "point_count": point_count,
            "repeat": repeat,
            "radius": float(repeat50["parameters"]["radius"]),
            "k_max": int(repeat50["parameters"]["k_max"]),
            "point_column_source": repeat50["parameters"]["point_column_source"],
            "routes": repeat50["parameters"]["routes"],
        },
        "measurements": {
            "optix": _route_summary(optix),
            "cupy_grid": _route_summary(cupy),
        },
        "comparisons": {
            "hot_query_speedup": hot_speedup,
            "cold_plus_query_speedup": cold_plus_speedup,
            "runner_wall_speedup": runner_speedup,
        },
        "parity": repeat50.get("parity"),
        "review_required_before_m7": [
            "External Claude/Gemini review over the exact candidate row id and evidence packet.",
            "Codex consensus response after external review.",
            "Public wording review that keeps this scoped to repeat50 prepared-session amortization.",
        ],
        "not_release_boundaries": [
            "No V3 release authorization.",
            "No broad V3-over-V2 claim.",
            "No whole RTNN app claim.",
            "No one-shot or cold-start RTNN speedup claim; cold-plus-query is only 1.315x.",
            "No paper-equivalent RTNN claim.",
        ],
        "promotion_reading": (
            "This is the first RTNN row in the current Phoenix run that clears the 2.0x "
            "runner-wall floor, but only for the prepared repeat50/session-amortized "
            "contract. It remains pending external review and adds zero M7 rows now."
        ),
        "goal_level_decision_audit": {
            "decision": (
                "Record RTNN repeat50 prepared-session amortization as a material M7 "
                "candidate pending external review, not as immediate promotion."
            ),
            "was_i_foolish": (
                "No. The test matches the V3 prepared-execution thesis and keeps the "
                "one-shot/cold-start boundary explicit."
            ),
            "foolish_actions": (
                "It would be foolish to call this a general RTNN win, a paper-equivalent "
                "result, or a release row before external review."
            ),
            "other_path": (
                "I could keep pursuing single-run RTNN overhead or wait on AABB review, "
                "but repeat50 is the direct way to test V3 prepared-session value."
            ),
            "different_path_now": (
                "Send this exact scoped candidate for external review; if blocked, keep it "
                "as pending and continue another generic engine blocker."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    c = payload["comparisons"]
    m = payload["measurements"]
    lines = [
        "# Phoenix V3 RTNN Prepared Repeat50 Amortization Evidence",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet records a scoped prepared-session candidate. It is not V3 release "
        "authorization, not a whole RTNN app claim, and not a one-shot nearest-neighbor claim.",
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "m7_promotion_authorized: false",
        "M7 rows added now: 0",
        "```",
        "",
        "## Candidate Row",
        "",
    ]
    lines.extend(f"- `{row_id}`" for row_id in payload["candidate_row_ids"])
    lines.extend(
        [
            "",
            "## POD Result",
            "",
            f"- Point count: `{payload['parameters']['point_count']}`",
            f"- Repeat count: `{payload['parameters']['repeat']}`",
            f"- Warm OptiX/CuPy hot-query speedup: `{c['hot_query_speedup']:.3f}x`",
            f"- Warm OptiX/CuPy cold-plus-query speedup: `{c['cold_plus_query_speedup']:.3f}x`",
            f"- Warm OptiX/CuPy runner-wall speedup: `{c['runner_wall_speedup']:.3f}x`",
            "",
            "## Phase Rows",
            "",
            "| route | input load | pack/prepare | hot query median | runner wall |",
            "|---|---:|---:|---:|---:|",
            (
                f"| RTDL OptiX | {m['optix']['input_load_sec']:.6f}s | "
                f"{m['optix']['input_pack_sec'] + m['optix']['execution_prepare_sec']:.6f}s | "
                f"{m['optix']['hot_query_median_sec']:.6f}s | "
                f"{m['optix']['runner_wall_sec']:.6f}s |"
            ),
            (
                f"| CuPy grid | {m['cupy_grid']['input_load_sec']:.6f}s | "
                f"{m['cupy_grid']['grid_prepare_sec']:.6f}s | "
                f"{m['cupy_grid']['hot_query_median_sec']:.6f}s | "
                f"{m['cupy_grid']['runner_wall_sec']:.6f}s |"
            ),
            "",
            "## Boundaries",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["not_release_boundaries"])
    lines.extend(
        [
            "",
            "## Review Required Before M7",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["review_required_before_m7"])
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
        description="Emit Phoenix V3 RTNN repeat50 prepared-session evidence packet."
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
