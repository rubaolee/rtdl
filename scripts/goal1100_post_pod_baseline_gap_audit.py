#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1100 post-pod baseline gap audit"

FACILITY_RTX = "docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json"
FACILITY_CPU = "docs/reports/goal1083_facility_recentered_2_5m_cpu_oracle.json"
FACILITY_OLD_BEST = "docs/reports/goal835_baseline_facility_knn_assignment_coverage_threshold_prepared_best_available_non_optix_backend_same_semantics_2026-04-23.json"
BARNES_VALIDATION_RTX = "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json"
BARNES_TIMING_RTX = "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json"
BARNES_OLD_BEST = "docs/reports/goal835_baseline_barnes_hut_force_app_node_coverage_prepared_best_available_non_optix_backend_same_semantics_2026-04-23.json"


def _load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _exists(path: str) -> bool:
    return (ROOT / path).exists()


def _median_optix(path: str) -> float | None:
    timings = _load(path).get("scenario", {}).get("timings_sec", {})
    query = timings.get("optix_query_sec")
    if isinstance(query, dict) and isinstance(query.get("median_sec"), (int, float)):
        return float(query["median_sec"])
    return None


def build_audit() -> dict[str, Any]:
    facility_cpu = _load(FACILITY_CPU) if _exists(FACILITY_CPU) else {}
    facility_rtx = _load(FACILITY_RTX) if _exists(FACILITY_RTX) else {}
    barnes_validation = _load(BARNES_VALIDATION_RTX) if _exists(BARNES_VALIDATION_RTX) else {}
    barnes_timing = _load(BARNES_TIMING_RTX) if _exists(BARNES_TIMING_RTX) else {}

    facility_rtx_result = facility_rtx.get("scenario", {}).get("result", {})
    facility_cpu_scenario = facility_cpu.get("scenario", {})
    barnes_validation_result = barnes_validation.get("scenario", {}).get("result", {})
    barnes_timing_result = barnes_timing.get("scenario", {}).get("result", {})

    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "rtx_artifact": FACILITY_RTX,
            "rtx_query_median_sec": _median_optix(FACILITY_RTX) if _exists(FACILITY_RTX) else None,
            "rtx_correctness": facility_rtx_result.get("matches_oracle") is True,
            "baseline_status": "partial_cpu_oracle_present_needs_fastest_non_optix_phase_baseline",
            "baseline_artifacts": [
                {
                    "path": FACILITY_CPU,
                    "status": "usable_for_correctness_and_cpu_oracle_context",
                    "limitation": "CPU oracle total time is present, but this is not a reviewed fastest non-OptiX phase-separated baseline for public wording.",
                    "scale": {
                        "customer_count": facility_cpu_scenario.get("result", {}).get("customer_count"),
                        "coordinate_mapping": facility_cpu_scenario.get("coordinate_mapping"),
                    },
                    "timings_sec": facility_cpu_scenario.get("timings_sec"),
                },
                {
                    "path": FACILITY_OLD_BEST,
                    "status": "not_same_current_contract",
                    "limitation": "Older Goal835 best-available baseline covers coverage_threshold_prepared at 80k rows, not the current recentered 10M-query contract.",
                },
            ],
            "next_action": (
                "Produce a same current-contract fastest non-OptiX phase-separated baseline, preferably Embree or CPU oracle with "
                "input/prepare/query/postprocess phases separated and reviewed against the recentered RTX artifact."
            ),
            "public_speedup_claim_ready": False,
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "rtx_artifacts": [BARNES_VALIDATION_RTX, BARNES_TIMING_RTX],
            "rtx_validation_query_median_sec": _median_optix(BARNES_VALIDATION_RTX) if _exists(BARNES_VALIDATION_RTX) else None,
            "rtx_timing_query_median_sec": _median_optix(BARNES_TIMING_RTX) if _exists(BARNES_TIMING_RTX) else None,
            "rtx_correctness": barnes_validation_result.get("matches_oracle") is True,
            "rtx_timing_has_validation": barnes_timing_result.get("matches_oracle") is True,
            "baseline_status": "current_contract_baseline_missing",
            "baseline_artifacts": [
                {
                    "path": BARNES_OLD_BEST,
                    "status": "not_same_current_contract",
                    "limitation": "Older Goal835 baseline is 4,096 bodies at radius 10.0; current rich contract uses depth 8, radius 0.1, threshold 4, and a 20M timing repeat.",
                }
            ],
            "next_action": (
                "Produce a same current-contract non-OptiX baseline pair: one validated depth-8 small-scale row matching the RTX validation contract "
                "and one large timing row matching the 20M timing contract, then run 2+ AI review before public wording."
            ),
            "public_speedup_claim_ready": False,
        },
    ]
    summary = {
        "row_count": len(rows),
        "rtx_correct_count": sum(1 for row in rows if row["rtx_correctness"]),
        "public_speedup_claim_ready_count": sum(1 for row in rows if row["public_speedup_claim_ready"]),
        "baseline_missing_or_partial_count": sum(
            row["baseline_status"] != "same_current_contract_baseline_complete" for row in rows
        ),
    }
    valid = (
        summary["row_count"] == 2
        and summary["rtx_correct_count"] == 2
        and summary["public_speedup_claim_ready_count"] == 0
        and summary["baseline_missing_or_partial_count"] == 2
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "rows": rows,
        "summary": summary,
        "valid": valid,
        "boundary": (
            "Goal1100 audits baseline readiness after Goal1098/Goal1099. It does not authorize public RTX speedup claims. "
            "Both audited apps still need same-current-contract baseline review before public wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1100 Post-Pod Baseline Gap Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| App | Path | RTX correct | Baseline status | Public claim ready | Next action |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['rtx_correctness']}` | "
            f"`{row['baseline_status']}` | `{row['public_speedup_claim_ready']}` | {row['next_action']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit post-pod baseline gaps before public RTX wording.")
    parser.add_argument("--output-json", default="docs/reports/goal1100_post_pod_baseline_gap_audit_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1100_post_pod_baseline_gap_audit_2026-04-29.md")
    args = parser.parse_args()
    payload = build_audit()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
