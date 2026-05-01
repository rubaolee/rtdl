#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports"
DATE = "2026-04-30"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _goal1060_database_rows() -> list[dict[str, Any]]:
    path = REPORTS / "goal1060_post_goal1058_speedup_candidate_audit_2026-04-28.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [row for row in payload.get("rows", []) if row.get("app") == "database_analytics"]


def _source_observations() -> dict[str, Any]:
    optix = _read(ROOT / "src/rtdsl/optix_runtime.py")
    embree = _read(ROOT / "src/rtdsl/embree_runtime.py")
    regional = _read(ROOT / "examples/rtdl_v0_7_db_app_demo.py")
    sales = _read(ROOT / "examples/rtdl_sales_risk_screening.py")

    return {
        "compact_summary_has_no_public_row_materialization_gate": (
            "native_continuation_backend == \"optix_db_compact_summary\"" in _read(ROOT / "examples/rtdl_database_analytics_app.py")
            and "if any(\"materialize\" in phase for phase in run_phases)" in regional
            and "if any(\"materialize\" in phase for phase in run_phases)" in sales
        ),
        "optix_grouped_summary_uses_grouped_row_api": (
            "def grouped_count_summary(self, query) -> dict[str, int]:" in optix
            and "rows = self._dataset.grouped_count" in optix
            and "def grouped_sum_summary(self, query) -> dict[str, int]:" in optix
            and "rows = self._dataset.grouped_sum" in optix
        ),
        "embree_grouped_summary_uses_grouped_row_api": (
            "def grouped_count_summary(self, query) -> dict[str, int]:" in embree
            and "rows = self._dataset.grouped_count" in embree
            and "def grouped_sum_summary(self, query) -> dict[str, int]:" in embree
            and "rows = self._dataset.grouped_sum" in embree
        ),
        "regional_dashboard_runs_three_compact_native_ops": all(
            token in regional
            for token in (
                "query_conjunctive_scan_count_sec",
                "query_grouped_count_summary_sec",
                "query_grouped_sum_summary_sec",
            )
        ),
        "sales_risk_runs_three_compact_native_ops": all(
            token in sales
            for token in (
                "query_conjunctive_scan_count_sec",
                "query_grouped_count_summary_sec",
                "query_grouped_sum_summary_sec",
            )
        ),
    }


def _profile_observations(profile_json: Path | None) -> dict[str, Any]:
    if profile_json is None or not profile_json.exists():
        return {"included": False}
    payload = json.loads(profile_json.read_text(encoding="utf-8"))
    rows: dict[str, Any] = {}
    for result in payload.get("results", []):
        backend = result.get("backend")
        if not backend:
            continue
        observation = result.get("db_review_observation", {})
        warm = result.get("prepared_session_warm_query_sec", {})
        phase_totals = result.get("reported_run_phase_totals_sec", {})
        rows[str(backend)] = {
            "status": result.get("status"),
            "observation_status": observation.get("status"),
            "warm_query_median_sec": warm.get("median_sec"),
            "row_materializing_operation_count": phase_totals.get("row_materializing_operation_count"),
            "compact_summary_operation_count": phase_totals.get("compact_summary_operation_count"),
        }
    return {
        "included": True,
        "profile_path": str(profile_json),
        "scenario": payload.get("scenario"),
        "copies": payload.get("copies"),
        "iterations": payload.get("iterations"),
        "output_mode": payload.get("output_mode"),
        "rows": rows,
    }


def build_audit(profile_json: Path | None = None) -> dict[str, Any]:
    goal1060_rows = _goal1060_database_rows()
    source = _source_observations()
    profile = _profile_observations(profile_json)

    blockers: list[str] = []
    if not goal1060_rows:
        blockers.append("missing_goal1060_database_rows")
    for key, value in source.items():
        if not value:
            blockers.append(f"source_observation_failed:{key}")
    if profile.get("included"):
        embree = profile.get("rows", {}).get("embree", {})
        if embree.get("row_materializing_operation_count") != 0:
            blockers.append("local_embree_compact_summary_materialized_rows")
        if embree.get("compact_summary_operation_count") not in {3, 6}:
            blockers.append("local_embree_compact_summary_operation_count_unexpected")

    rejected_rows = [
        {
            "path_name": row.get("path_name"),
            "rtx_sec": row.get("rtx_native_or_query_phase_sec"),
            "fastest_baseline": row.get("fastest_baseline"),
            "fastest_baseline_sec": row.get("fastest_baseline_sec"),
            "ratio_baseline_over_rtx": row.get("fastest_ratio_baseline_over_rtx"),
            "reason": row.get("reason"),
        }
        for row in goal1060_rows
    ]

    return {
        "goal": "Goal1155 DB compact-summary pre-cloud audit",
        "date": DATE,
        "valid": not blockers,
        "blockers": blockers,
        "app": "database_analytics",
        "current_public_wording_status": "public_wording_not_reviewed",
        "cloud_policy": "no_pod_until_code_or_contract_changes",
        "goal1060_database_rows": rejected_rows,
        "source_observations": source,
        "local_profile_observations": profile,
        "conclusions": [
            "The public DB app already has a compact-summary gate that rejects row-materializing public RTX claim paths.",
            "The current OptiX evidence is slower than Embree compact-summary baselines for both DB scenarios, so another pod rerun without code or contract changes is low-value.",
            "The compact-summary implementation still performs three native DB operations per scenario and grouped summaries still travel through grouped row-return APIs before Python dict decoding.",
            "The next useful optimization is a generic prepared DB compact-summary batch primitive that can execute scan-count, grouped-count summary, and grouped-sum summary in one native prepared-session dispatch with explicit phase counters.",
        ],
        "next_actions": [
            "Design a generic DB compact-summary batch request format rather than hardcoding a sales/dashboard-only API.",
            "Implement OptiX first: one prepared dataset, one batch dispatch for the scenario's scan-count and grouped summaries, and phase counters for traversal, copyback, exact filtering/grouping, and output packing.",
            "Mirror the API in Embree after OptiX so the fastest same-semantics CPU RT baseline remains fair.",
            "Only then include database_analytics in the next consolidated RTX pod batch.",
        ],
        "boundary": (
            "Goal1155 is a pre-cloud DB performance audit. It does not authorize public speedup wording, "
            "does not start cloud resources, and does not change release status."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1155 DB Compact-Summary Pre-Cloud Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        "## Summary",
        "",
        f"- App: `{payload['app']}`",
        f"- Current public wording status: `{payload['current_public_wording_status']}`",
        f"- Cloud policy: `{payload['cloud_policy']}`",
        "",
        "## Current Evidence",
        "",
        "| Path | RTX sec | Fastest baseline | Baseline sec | Baseline/RTX | Reason |",
        "| --- | ---: | --- | ---: | ---: | --- |",
    ]
    for row in payload["goal1060_database_rows"]:
        lines.append(
            f"| `{row['path_name']}` | `{row['rtx_sec']}` | `{row['fastest_baseline']}` | "
            f"`{row['fastest_baseline_sec']}` | `{row['ratio_baseline_over_rtx']}` | {row['reason']} |"
        )
    lines.extend(["", "## Source Observations", ""])
    for key, value in payload["source_observations"].items():
        lines.append(f"- `{key}`: `{value}`")
    profile = payload["local_profile_observations"]
    lines.extend(["", "## Local Profile", ""])
    if profile.get("included"):
        lines.append(
            f"- Profile: `{profile['profile_path']}`, scenario `{profile['scenario']}`, "
            f"copies `{profile['copies']}`, iterations `{profile['iterations']}`, output mode `{profile['output_mode']}`"
        )
        lines.extend(["", "| Backend | Status | Observation | Warm median sec | Row-materializing ops | Compact-summary ops |", "| --- | --- | --- | ---: | ---: | ---: |"])
        for backend, row in sorted(profile["rows"].items()):
            lines.append(
                f"| `{backend}` | `{row['status']}` | `{row['observation_status']}` | "
                f"`{row['warm_query_median_sec']}` | `{row['row_materializing_operation_count']}` | "
                f"`{row['compact_summary_operation_count']}` |"
            )
    else:
        lines.append("- No local profile JSON was provided.")
    lines.extend(["", "## Conclusions", ""])
    for conclusion in payload["conclusions"]:
        lines.append(f"- {conclusion}")
    lines.extend(["", "## Next Actions", ""])
    for action in payload["next_actions"]:
        lines.append(f"- {action}")
    lines.extend(["", "## Blockers", ""])
    if payload["blockers"]:
        for blocker in payload["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None for this audit.")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit DB compact-summary readiness before another RTX pod run.")
    parser.add_argument("--profile-json", type=Path)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=REPORTS / "goal1155_db_compact_summary_precloud_audit_2026-04-30.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=REPORTS / "goal1155_db_compact_summary_precloud_audit_2026-04-30.md",
    )
    args = parser.parse_args(argv)
    payload = build_audit(args.profile_json)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "blockers": payload["blockers"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
