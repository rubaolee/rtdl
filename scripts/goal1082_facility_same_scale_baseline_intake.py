#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1082 facility same-scale baseline intake"
RTX_ARTIFACT = ROOT / "docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json"
BASELINE_ARTIFACT = ROOT / "docs/reports/goal1081_same_scale_baselines/facility_coverage_threshold_2_5m_cpu_oracle.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_intake() -> dict[str, Any]:
    rtx = _load(RTX_ARTIFACT)
    baseline = _load(BASELINE_ARTIFACT)
    rtx_params = rtx["parameters"]
    baseline_params = baseline["parameters"]
    rtx_result = rtx["scenario"]["result"]
    baseline_result = baseline["scenario"]["result"]
    same_scale = (
        int(rtx_params["copies"]) == int(baseline_params["copies"]) == 2_500_000
        and int(rtx_result["query_count"]) == int(baseline_result["customer_count"]) == 10_000_000
        and float(rtx_params["radius"]) == float(baseline_params["radius"]) == 1.0
    )
    decision_matches = bool(rtx_result["all_queries_reached_threshold"]) == bool(
        baseline_result["all_customers_covered"]
    )
    covered_count_matches = int(rtx_result["threshold_reached_count"]) == int(
        baseline_result["covered_customer_count"]
    )
    public_claim_authorized = same_scale and decision_matches and covered_count_matches
    return {
        "goal": GOAL,
        "date": DATE,
        "source_artifacts": [
            str(RTX_ARTIFACT.relative_to(ROOT)),
            str(BASELINE_ARTIFACT.relative_to(ROOT)),
        ],
        "scale": {
            "copies": int(rtx_params["copies"]),
            "query_count": int(rtx_result["query_count"]),
            "radius": float(rtx_params["radius"]),
        },
        "rtx_result": {
            "threshold_reached_count": int(rtx_result["threshold_reached_count"]),
            "all_queries_reached_threshold": bool(rtx_result["all_queries_reached_threshold"]),
            "matches_oracle_in_artifact": rtx_result["matches_oracle"],
            "skip_validation": bool(rtx_params["skip_validation"]),
            "optix_query_median_sec": float(rtx["scenario"]["timings_sec"]["optix_query_sec"]["median_sec"]),
        },
        "baseline_result": {
            "covered_customer_count": int(baseline_result["covered_customer_count"]),
            "all_customers_covered": bool(baseline_result["all_customers_covered"]),
            "cpu_reference_total_sec": float(baseline["scenario"]["timings_sec"]["cpu_reference_total_sec"]),
            "input_build_sec": float(baseline["scenario"]["timings_sec"]["input_build_sec"]),
        },
        "checks": {
            "same_scale": same_scale,
            "decision_matches": decision_matches,
            "covered_count_matches": covered_count_matches,
            "public_claim_authorized": public_claim_authorized,
        },
        "verdict": "BLOCK",
        "reason": (
            "The same-scale CPU oracle says all 10,000,000 customers are covered, but the RTX timing row "
            "with validation skipped reports only 8,898,102 threshold-reaching queries. The facility RTX "
            "public wording remains blocked until a corrected same-scale RTX validation run passes. The "
            "likely engineering cause is coordinate precision at 2.5M copies: x coordinates reach about "
            "15 million while the radius is 1.0, which is unsafe for float-oriented RT traversal without "
            "tiling, recentering, or another precision-aware mapping."
        ),
        "next_actions": [
            "Do not publish a facility RTX speedup ratio from the current 2.5M timing row.",
            "Add or use a precision-aware tiled/recentered facility benchmark mapping before the next cloud run.",
            "Rerun same-scale OptiX with validation enabled or with a reviewed validation-equivalent artifact.",
        ],
        "boundary": (
            "Goal1082 is an intake/audit of one same-scale facility baseline. It does not change public wording, "
            "does not authorize release, and does not authorize public RTX speedup claims."
        ),
        "valid": same_scale and not public_claim_authorized,
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1082 Facility Same-Scale Baseline Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Verdict: **{payload['verdict']}**",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        "## Result",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in payload["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Evidence",
            "",
            f"- RTX threshold-reaching count: `{payload['rtx_result']['threshold_reached_count']}` / `{payload['scale']['query_count']}`.",
            f"- CPU oracle covered count: `{payload['baseline_result']['covered_customer_count']}` / `{payload['scale']['query_count']}`.",
            f"- RTX timing row skipped validation: `{payload['rtx_result']['skip_validation']}`.",
            f"- RTX query median: `{payload['rtx_result']['optix_query_median_sec']}` seconds.",
            f"- CPU reference total: `{payload['baseline_result']['cpu_reference_total_sec']}` seconds.",
            "",
            "## Reason",
            "",
            payload["reason"],
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["next_actions"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the facility same-scale baseline against the RTX timing row.")
    parser.add_argument("--output-json", default="docs/reports/goal1082_facility_same_scale_baseline_intake_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1082_facility_same_scale_baseline_intake_2026-04-29.md")
    args = parser.parse_args()
    payload = build_intake()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "verdict": payload["verdict"], **payload["checks"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
