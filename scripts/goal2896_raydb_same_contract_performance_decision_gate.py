#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PRIMITIVE_FIRST_BACKEND = "paper_rt_optix_v2_5_primitive_first"
HIT_STREAM_TRITON_BACKEND = "paper_rt_optix_device_hit_stream_triton_prepared"
OLD_PAPER_BACKEND = "paper_rt_optix"

REQUIRED_ROW_COUNTS = (250000, 1000000)
REQUIRED_MODES = ("count", "sum")
REQUIRED_BACKENDS = (
    OLD_PAPER_BACKEND,
    PRIMITIVE_FIRST_BACKEND,
    HIT_STREAM_TRITON_BACKEND,
)
HIT_STREAM_MIN_SLOWDOWN_BY_MODE = {
    "count": 10.0,
    "sum": 50.0,
}
OLD_PAPER_MIN_SPEEDUP_BY_MODE = {
    "count": 20.0,
    "sum": 5.0,
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _case_key(case: dict[str, Any]) -> tuple[int, str, str]:
    return (int(case["row_count"]), str(case["mode"]), str(case["backend"]))


def _median_sec(case: dict[str, Any]) -> float:
    value = float(case["median_wall_sec"])
    if value <= 0.0:
        raise ValueError(f"non-positive median_wall_sec for {_case_key(case)}: {value}")
    return value


def _claim_boundary(case: dict[str, Any]) -> dict[str, Any]:
    raw = case.get("claim_boundary")
    return raw if isinstance(raw, dict) else {}


def _case_does_not_authorize_claims(case: dict[str, Any]) -> bool:
    boundary = _claim_boundary(case)
    if boundary:
        blocked_keys = (
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "release_authorized",
        )
        return all(boundary.get(key) is not True for key in blocked_keys)
    return case.get("true_zero_copy_authorized") is not True


def analyze_payload(payload: dict[str, Any], *, source_artifact: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    cases = payload.get("cases")
    if not isinstance(cases, list):
        cases = []
        errors.append("input payload has no cases list")

    by_key: dict[tuple[int, str, str], dict[str, Any]] = {}
    for case in cases:
        if isinstance(case, dict):
            try:
                by_key[_case_key(case)] = case
            except Exception as exc:
                errors.append(f"malformed case skipped: {exc}")

    if payload.get("all_correct") is not True:
        errors.append("input payload all_correct is not true")

    comparisons: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for row_count in REQUIRED_ROW_COUNTS:
        for mode in REQUIRED_MODES:
            key = (row_count, mode)
            primitive = by_key.get((*key, PRIMITIVE_FIRST_BACKEND))
            hit_stream = by_key.get((*key, HIT_STREAM_TRITON_BACKEND))
            old_paper = by_key.get((*key, OLD_PAPER_BACKEND))
            if primitive is None:
                errors.append(f"missing primitive-first case for rows={row_count} mode={mode}")
                continue
            if hit_stream is None:
                errors.append(f"missing prepared hit-stream Triton case for rows={row_count} mode={mode}")
                continue
            if old_paper is None:
                errors.append(f"missing old paper_rt_optix diagnostic case for rows={row_count} mode={mode}")
                continue

            for label, case in (
                ("primitive_first", primitive),
                ("hit_stream_triton", hit_stream),
                ("old_paper_rt_optix", old_paper),
            ):
                if case.get("matches_cpu_reference") is not True:
                    errors.append(f"{label} case failed CPU reference for rows={row_count} mode={mode}")
                if not _case_does_not_authorize_claims(case):
                    errors.append(f"{label} case authorizes a blocked claim for rows={row_count} mode={mode}")

            if primitive.get("v2_5_selected_path") != "prepared_fused_generic_grouped_reduction":
                errors.append(f"primitive-first did not record fused selected path for rows={row_count} mode={mode}")
            if primitive.get("partner_continuation_required") is not False:
                errors.append(f"primitive-first still requires partner continuation for rows={row_count} mode={mode}")
            if primitive.get("typed_hit_stream_forced") is not False:
                errors.append(f"primitive-first forced typed hit stream for rows={row_count} mode={mode}")

            primitive_sec = _median_sec(primitive)
            hit_stream_sec = _median_sec(hit_stream)
            old_paper_sec = _median_sec(old_paper)
            hit_stream_slowdown = hit_stream_sec / primitive_sec
            old_paper_speedup = old_paper_sec / primitive_sec
            hit_threshold = HIT_STREAM_MIN_SLOWDOWN_BY_MODE[mode]
            old_threshold = OLD_PAPER_MIN_SPEEDUP_BY_MODE[mode]
            hit_pass = hit_stream_slowdown >= hit_threshold
            old_pass = old_paper_speedup >= old_threshold
            if not hit_pass:
                errors.append(
                    f"hit-stream Triton slowdown {hit_stream_slowdown:.3f}x below "
                    f"{hit_threshold:.1f}x for rows={row_count} mode={mode}"
                )
            if not old_pass:
                errors.append(
                    f"old paper_rt_optix speedup {old_paper_speedup:.3f}x below "
                    f"{old_threshold:.1f}x for rows={row_count} mode={mode}"
                )

            comparisons.append(
                {
                    "row_count": row_count,
                    "mode": mode,
                    "primitive_first_backend": PRIMITIVE_FIRST_BACKEND,
                    "prepared_hit_stream_triton_backend": HIT_STREAM_TRITON_BACKEND,
                    "primitive_first_median_wall_sec": primitive_sec,
                    "prepared_hit_stream_triton_median_wall_sec": hit_stream_sec,
                    "prepared_hit_stream_triton_slowdown_vs_primitive_first": hit_stream_slowdown,
                    "required_min_slowdown": hit_threshold,
                    "pass": hit_pass,
                }
            )
            diagnostics.append(
                {
                    "row_count": row_count,
                    "mode": mode,
                    "old_paper_rt_optix_backend": OLD_PAPER_BACKEND,
                    "old_paper_rt_optix_median_wall_sec": old_paper_sec,
                    "primitive_first_median_wall_sec": primitive_sec,
                    "primitive_first_speedup_vs_old_paper_rt_optix": old_paper_speedup,
                    "required_min_speedup": old_threshold,
                    "pass": old_pass,
                    "comparison_scope": "diagnostic_full_call_baseline_not_prepared_same_contract",
                }
            )

    status = "pass" if not errors else "fail"
    return {
        "goal": "Goal2896 RayDB same-contract performance decision gate",
        "status": status,
        "source_artifact": source_artifact,
        "git_head": payload.get("git_head"),
        "nvidia_smi": payload.get("nvidia_smi"),
        "row_counts": list(REQUIRED_ROW_COUNTS),
        "modes": list(REQUIRED_MODES),
        "required_backends": list(REQUIRED_BACKENDS),
        "thresholds": {
            "prepared_hit_stream_triton_min_slowdown_vs_primitive_first": HIT_STREAM_MIN_SLOWDOWN_BY_MODE,
            "old_paper_rt_optix_min_speedup_for_primitive_first": OLD_PAPER_MIN_SPEEDUP_BY_MODE,
        },
        "all_correct": payload.get("all_correct") is True
        and all(bool(case.get("matches_cpu_reference")) for case in cases if isinstance(case, dict)),
        "comparisons": comparisons,
        "diagnostics": diagnostics,
        "decision": {
            "raydb_scalar_grouped_fast_path": PRIMITIVE_FIRST_BACKEND,
            "selected_design_rule": "primitive_first_for_exact_fused_generic_grouped_reductions",
            "hit_stream_triton_reserved_for": "continuations_not_expressible_as_fused_generic_rtdl_reductions",
            "triton_front_door_promoted_for_scalar_grouped_reductions": False,
            "auto_triton_promotion_authorized": False,
        },
        "claim_boundary": {
            "internal_decision_gate_only": True,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = _load_json(args.input)
    summary = analyze_payload(payload, source_artifact=str(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"[goal2896] status={summary['status']} comparisons={len(summary['comparisons'])} "
        f"errors={len(summary['errors'])} output={args.output}",
        flush=True,
    )
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
