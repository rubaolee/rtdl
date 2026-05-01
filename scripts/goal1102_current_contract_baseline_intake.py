#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1102 current-contract baseline intake"
DEFAULT_DIR = Path("docs/reports/goal1101_current_contract_non_optix_baselines")


EXPECTED = [
    {
        "name": "facility_cpu_oracle",
        "path": DEFAULT_DIR / "facility_recentered_2_5m_cpu_oracle_baseline.json",
        "app": "facility_knn_assignment",
        "path_name": "coverage_threshold_prepared_recentered",
        "backend": "cpu_oracle",
        "scenario": "facility_service_coverage_recentered",
        "query_count": 10_000_000,
        "radius": 1.0,
        "requires_matches_oracle": True,
    },
    {
        "name": "facility_embree",
        "path": DEFAULT_DIR / "facility_recentered_2_5m_embree_baseline.json",
        "app": "facility_knn_assignment",
        "path_name": "coverage_threshold_prepared_recentered",
        "backend": "embree",
        "scenario": "facility_service_coverage_recentered",
        "query_count": 10_000_000,
        "radius": 1.0,
        "requires_matches_oracle": True,
    },
    {
        "name": "barnes_hut_validation_embree",
        "path": DEFAULT_DIR / "barnes_hut_depth8_4096_embree_validation_baseline.json",
        "app": "barnes_hut_force_app",
        "path_name": "node_coverage_prepared_rich",
        "backend": "embree",
        "scenario": "barnes_hut_node_coverage",
        "query_count": 4_096,
        "radius": 0.1,
        "barnes_tree_depth": 8,
        "hit_threshold": 4,
        "requires_matches_oracle": True,
    },
    {
        "name": "barnes_hut_timing_embree",
        "path": DEFAULT_DIR / "barnes_hut_depth8_20m_embree_timing_baseline.json",
        "app": "barnes_hut_force_app",
        "path_name": "node_coverage_prepared_rich",
        "backend": "embree",
        "scenario": "barnes_hut_node_coverage",
        "query_count": 20_000_000,
        "radius": 0.1,
        "barnes_tree_depth": 8,
        "hit_threshold": 4,
        "requires_matches_oracle": False,
        "requires_timing_only": True,
    },
]


def _nested(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _median_native(payload: dict[str, Any]) -> float | None:
    value = _nested(payload, ("scenario", "timings_sec", "native_query_sec"))
    if isinstance(value, dict) and isinstance(value.get("median_sec"), (int, float)):
        return float(value["median_sec"])
    return None


def _validate(expected: dict[str, Any], payload: dict[str, Any]) -> tuple[str, list[str]]:
    issues: list[str] = []
    if payload.get("schema_version") != "goal1101_current_contract_non_optix_baseline_v1":
        issues.append("wrong schema_version")
    for key in ("app", "path_name", "backend"):
        if payload.get(key) != expected[key]:
            issues.append(f"{key} mismatch")
    if payload.get("public_speedup_claim_authorized") is not False:
        issues.append("public_speedup_claim_authorized is not false")
    if not payload.get("source_commit"):
        issues.append("missing source_commit")
    if _nested(payload, ("scenario", "scenario")) != expected["scenario"]:
        issues.append("scenario mismatch")
    if _nested(payload, ("scenario", "result", "query_count")) != expected["query_count"]:
        issues.append("query_count mismatch")
    if _nested(payload, ("scenario", "result", "radius")) != expected["radius"]:
        issues.append("radius mismatch")
    if expected.get("barnes_tree_depth") is not None and _nested(payload, ("scenario", "result", "barnes_tree_depth")) != expected["barnes_tree_depth"]:
        issues.append("barnes_tree_depth mismatch")
    if expected.get("hit_threshold") is not None and _nested(payload, ("scenario", "result", "hit_threshold")) != expected["hit_threshold"]:
        issues.append("hit_threshold mismatch")
    matches_oracle = _nested(payload, ("scenario", "result", "matches_oracle"))
    if expected.get("requires_matches_oracle") and matches_oracle is not True:
        issues.append("matches_oracle is not true")
    if expected.get("requires_timing_only") and matches_oracle is not None:
        issues.append("timing-only artifact should have matches_oracle null")
    if _median_native(payload) is None:
        issues.append("missing native_query_sec.median_sec")
    return ("ok" if not issues else "blocked", issues)


def build_intake(baseline_dir: Path = DEFAULT_DIR) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for expected in EXPECTED:
        path = baseline_dir / expected["path"].name
        if not (ROOT / path).exists():
            rows.append(
                {
                    "name": expected["name"],
                    "artifact_path": str(path),
                    "status": "missing",
                    "issues": ["artifact missing"],
                    "native_query_median_sec": None,
                    "public_speedup_claim_authorized": False,
                }
            )
            continue
        payload = json.loads((ROOT / path).read_text(encoding="utf-8"))
        status, issues = _validate(expected, payload)
        rows.append(
            {
                "name": expected["name"],
                "artifact_path": str(path),
                "status": status,
                "issues": issues,
                "native_query_median_sec": _median_native(payload),
                "public_speedup_claim_authorized": False,
            }
        )
    summary = {
        "row_count": len(rows),
        "ok_count": sum(1 for row in rows if row["status"] == "ok"),
        "missing_count": sum(1 for row in rows if row["status"] == "missing"),
        "blocked_count": sum(1 for row in rows if row["status"] == "blocked"),
        "public_speedup_claim_authorized_count": sum(1 for row in rows if row["public_speedup_claim_authorized"]),
    }
    ready = summary["ok_count"] == len(EXPECTED)
    structurally_valid = summary["row_count"] == len(EXPECTED) and summary["public_speedup_claim_authorized_count"] == 0
    return {
        "goal": GOAL,
        "date": DATE,
        "baseline_dir": str(baseline_dir),
        "rows": rows,
        "summary": summary,
        "artifact_set_complete": ready,
        "overall_status": "ready_for_2ai_baseline_review_not_public_claim" if ready else "waiting_for_baseline_artifacts",
        "valid": structurally_valid,
        "valid_meaning": (
            "The intake schema and no-claim guard are structurally valid. Use artifact_set_complete and "
            "overall_status to determine whether baseline artifacts are actually present and ready for review."
        ),
        "boundary": (
            "Goal1102 intakes current-contract non-OptiX baseline artifacts only. It does not authorize public RTX speedup claims. "
            "Even a fully OK intake still requires 2+ AI review and a separate public wording gate."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1102 Current-Contract Baseline Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Overall status: `{payload['overall_status']}`",
        "",
        f"Artifact set complete: `{str(payload['artifact_set_complete']).lower()}`",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        f"Valid meaning: {payload['valid_meaning']}",
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
    lines.extend(["", "## Rows", "", "| Name | Status | Native query median (s) | Issues |", "| --- | --- | ---: | --- |"])
    for row in payload["rows"]:
        issues = "; ".join(row["issues"])
        median = "" if row["native_query_median_sec"] is None else f"{row['native_query_median_sec']:.6f}"
        lines.append(f"| `{row['name']}` | `{row['status']}` | {median} | {issues} |")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1101 current-contract non-OptiX baseline artifacts.")
    parser.add_argument("--baseline-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--output-json", default="docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md")
    args = parser.parse_args()
    payload = build_intake(args.baseline_dir)
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "overall_status": payload["overall_status"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
