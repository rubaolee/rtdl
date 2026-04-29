#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1108 current RTX vs same-contract baseline comparison"


ROWS = [
    {
        "name": "facility_recentered_coverage_threshold_2_5m",
        "app": "facility_knn_assignment",
        "path_name": "coverage_threshold_prepared_recentered",
        "rtx_artifact": "docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
        "baseline_artifacts": {
            "cpu_oracle": "docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_cpu_oracle_baseline.json",
            "embree": "docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_embree_baseline.json",
        },
        "required": {
            "scenario": "facility_service_coverage_recentered",
            "query_count": 10_000_000,
            "radius": 1.0,
            "hit_threshold": 1,
        },
        "rtx_requires_matches_oracle": True,
    },
    {
        "name": "barnes_hut_depth8_20m_node_coverage",
        "app": "barnes_hut_force_app",
        "path_name": "node_coverage_prepared_rich",
        "rtx_artifact": "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json",
        "rtx_validation_artifact": "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json",
        "baseline_artifacts": {
            "embree": "docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json",
        },
        "required": {
            "scenario": "barnes_hut_node_coverage",
            "query_count": 20_000_000,
            "radius": 0.1,
            "hit_threshold": 4,
            "barnes_tree_depth": 8,
            "node_count": 65_536,
        },
        "rtx_requires_matches_oracle": False,
        "validation_required": True,
    },
]


def _load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _nested(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _rtx_median(payload: dict[str, Any]) -> float | None:
    value = _nested(payload, ("scenario", "timings_sec", "optix_query_sec", "median_sec"))
    return float(value) if isinstance(value, (int, float)) else None


def _baseline_median(payload: dict[str, Any]) -> float | None:
    value = _nested(payload, ("scenario", "timings_sec", "native_query_sec", "median_sec"))
    return float(value) if isinstance(value, (int, float)) else None


def _contract_issues(payload: dict[str, Any], required: dict[str, Any]) -> list[str]:
    result = _nested(payload, ("scenario", "result"))
    issues: list[str] = []
    if _nested(payload, ("scenario", "scenario")) != required["scenario"]:
        issues.append("scenario mismatch")
    for key in ("query_count", "radius", "hit_threshold", "barnes_tree_depth", "node_count"):
        if key in required and isinstance(result, dict) and result.get(key) != required[key]:
            issues.append(f"{key} mismatch")
    return issues


def _source_commit(payload: dict[str, Any]) -> str | None:
    value = payload.get("source_commit")
    return str(value) if value else None


def build_comparison() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for spec in ROWS:
        rtx = _load(spec["rtx_artifact"])
        rtx_issues = _contract_issues(rtx, spec["required"])
        rtx_median = _rtx_median(rtx)
        if rtx_median is None:
            rtx_issues.append("missing RTX median")
        if spec.get("rtx_requires_matches_oracle") and _nested(rtx, ("scenario", "result", "matches_oracle")) is not True:
            rtx_issues.append("RTX artifact lacks matches_oracle true")

        validation_status = None
        validation_path = spec.get("rtx_validation_artifact")
        if validation_path:
            validation = _load(str(validation_path))
            validation_issues = _contract_issues(
                validation,
                {**spec["required"], "query_count": 4_096},
            )
            if _nested(validation, ("scenario", "result", "matches_oracle")) is not True:
                validation_issues.append("validation artifact lacks matches_oracle true")
            validation_status = "ok" if not validation_issues else "blocked"
        baseline_rows: list[dict[str, Any]] = []
        for baseline_name, baseline_path in spec["baseline_artifacts"].items():
            baseline = _load(baseline_path)
            baseline_issues = _contract_issues(baseline, spec["required"])
            median = _baseline_median(baseline)
            if median is None:
                baseline_issues.append("missing baseline median")
            if baseline.get("public_speedup_claim_authorized") is not False:
                baseline_issues.append("baseline claim flag is not false")
            ratio = None if rtx_median is None or median is None or rtx_median <= 0 else median / rtx_median
            baseline_rows.append(
                {
                    "baseline": baseline_name,
                    "artifact": baseline_path,
                    "status": "ok" if not baseline_issues else "blocked",
                    "issues": baseline_issues,
                    "native_query_median_sec": median,
                    "engineering_ratio_baseline_over_rtx": ratio,
                    "source_commit": _source_commit(baseline),
                }
            )
        source_commits = {row["source_commit"] for row in baseline_rows}
        source_commits.add(_source_commit(rtx))
        source_commits.discard(None)
        blockers = [
            "cross_host_comparison_not_public_claim",
            "public_wording_review_required",
        ]
        if len(source_commits) > 1:
            blockers.append("source_commit_mismatch_requires_rerun_for_public_claim")
        if validation_status == "blocked":
            blockers.append("rtx_validation_artifact_blocked")
        if rtx_issues:
            blockers.append("rtx_artifact_contract_blocked")
        if any(row["status"] != "ok" for row in baseline_rows):
            blockers.append("baseline_contract_blocked")
        rows.append(
            {
                "name": spec["name"],
                "app": spec["app"],
                "path_name": spec["path_name"],
                "rtx_artifact": spec["rtx_artifact"],
                "rtx_status": "ok" if not rtx_issues else "blocked",
                "rtx_issues": rtx_issues,
                "rtx_query_median_sec": rtx_median,
                "rtx_source_commit": _source_commit(rtx),
                "rtx_validation_status": validation_status,
                "baselines": baseline_rows,
                "public_speedup_claim_authorized": False,
                "public_claim_blockers": blockers,
            }
        )
    return {
        "goal": GOAL,
        "date": DATE,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "rtx_ok_count": sum(1 for row in rows if row["rtx_status"] == "ok"),
            "baseline_ok_count": sum(
                1 for row in rows for baseline in row["baselines"] if baseline["status"] == "ok"
            ),
            "public_speedup_claim_authorized_count": sum(
                1 for row in rows if row["public_speedup_claim_authorized"]
            ),
        },
        "valid": all(row["rtx_status"] == "ok" for row in rows)
        and all(baseline["status"] == "ok" for row in rows for baseline in row["baselines"])
        and all(not row["public_speedup_claim_authorized"] for row in rows),
        "boundary": (
            "Goal1108 computes engineering comparison ratios between existing RTX artifacts and same-contract baselines. "
            "It does not authorize public RTX speedup claims because the current artifacts are cross-host, source commits differ, "
            "and public wording review remains required."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1108 Current RTX vs Same-Contract Baseline Comparison",
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
            "| App | Path | RTX median (s) | Baseline | Baseline median (s) | Engineering ratio | Public claim? | Blockers |",
            "| --- | --- | ---: | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        blockers = "; ".join(row["public_claim_blockers"])
        for baseline in row["baselines"]:
            ratio = baseline["engineering_ratio_baseline_over_rtx"]
            lines.append(
                f"| `{row['app']}` | `{row['path_name']}` | {row['rtx_query_median_sec']:.6f} | "
                f"`{baseline['baseline']}` | {baseline['native_query_median_sec']:.6f} | "
                f"{ratio:.2f}x | `false` | {blockers} |"
            )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare current RTX artifacts against same-contract baselines.")
    parser.add_argument("--output-json", default="docs/reports/goal1108_current_rtx_vs_baseline_comparison_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1108_current_rtx_vs_baseline_comparison_2026-04-29.md")
    args = parser.parse_args()
    payload = build_comparison()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
