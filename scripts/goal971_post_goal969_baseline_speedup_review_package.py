#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal836_rtx_baseline_readiness_gate import analyze_plan
from scripts.goal846_active_rtx_claim_gate import build_active_claim_gate
import rtdsl as rt


GOAL = "Goal971 post-Goal969 baseline/speedup review package"
DATE = "2026-04-26"

GROUP_REPORTS = [
    "goal969_artifact_report_group_a_robot_2026-04-26.json",
    "goal969_artifact_report_group_b_fixed_radius_2026-04-26.json",
    "goal969_artifact_report_group_c_database_2026-04-26.json",
    "goal969_artifact_report_group_d_spatial_2026-04-26.json",
    "goal969_artifact_report_group_e_segment_polygon_2026-04-26.json",
    "goal969_artifact_report_group_f_graph_2026-04-26.json",
    "goal969_artifact_report_group_g_prepared_decision_2026-04-26.json",
    "goal969_artifact_report_group_h_polygon_2026-04-26.json",
]

COMPLETE_BASELINE_STATUS = "same_semantics_baselines_complete"
ACTIVE_GATE_LIMITED_STATUS = "active_gate_complete_but_full_baseline_review_limited"
BASELINE_PENDING_STATUS = "rtx_artifact_ready_baseline_pending"

FIXED_RADIUS_SCOPES = {
    "outlier_detection": {
        "claim_scope": "prepared fixed-radius scalar threshold-count traversal only",
        "non_claim": (
            "not per-point outlier labels, row-returning outputs, broad anomaly detection, "
            "or whole-app speedup"
        ),
    },
    "dbscan_clustering": {
        "claim_scope": "prepared fixed-radius scalar core-count traversal only",
        "non_claim": "not per-point core flags, cluster expansion, full DBSCAN clustering, or whole-app speedup",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rtx_phase_seconds(row: dict[str, Any]) -> float | None:
    value = row.get("warm_query_median_sec")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _claim_scope(row: dict[str, Any]) -> str | None:
    app = str(row.get("app", ""))
    override = FIXED_RADIUS_SCOPES.get(app)
    if override is not None:
        return override["claim_scope"]
    value = row.get("claim_scope") or row.get("cloud_contract_claim_scope")
    return str(value) if value is not None else None


def _non_claim(row: dict[str, Any]) -> str | None:
    app = str(row.get("app", ""))
    override = FIXED_RADIUS_SCOPES.get(app)
    if override is not None:
        return override["non_claim"]
    value = row.get("non_claim") or row.get("cloud_contract_non_claim")
    return str(value) if value is not None else None


def _baseline_maps() -> tuple[dict[tuple[str, str], dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    readiness = analyze_plan()
    active_gate = build_active_claim_gate()
    readiness_by_key = {
        (str(row["app"]), str(row["path_name"])): row
        for row in readiness["rows"]
    }
    active_by_key = {
        (str(row["app"]), str(row["path_name"])): row
        for row in active_gate["rows"]
    }
    return readiness_by_key, active_by_key


def _baseline_summary(
    row: dict[str, Any],
    readiness_by_key: dict[tuple[str, str], dict[str, Any]],
    active_by_key: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    key = (str(row["app"]), str(row["path_name"]))
    readiness = readiness_by_key.get(key)
    active = active_by_key.get(key)
    checks = [] if readiness is None else list(readiness.get("artifact_checks", ()))
    valid = [item for item in checks if item.get("status") == "valid"]
    missing = [item for item in checks if item.get("status") == "missing"]
    invalid = [item for item in checks if item.get("status") == "invalid"]

    active_status = None if active is None else active.get("row_status")
    blocking_checks = [] if active is None else list(active.get("blocking_checks", ()))
    skipped_checks = [] if active is None else list(active.get("skipped_checks", ()))

    if checks and not missing and not invalid:
        status = COMPLETE_BASELINE_STATUS
        baseline_complete_for_review = True
        reason = "all Goal835 required same-semantics baselines are valid"
    elif active_status == "ok":
        status = ACTIVE_GATE_LIMITED_STATUS
        baseline_complete_for_review = False
        reason = (
            "Goal846 active gate is green for its blocking subset, but optional, local-unsupported, "
            "or full Goal835 baselines remain incomplete"
        )
    else:
        status = BASELINE_PENDING_STATUS
        baseline_complete_for_review = False
        reason = "RTX artifact exists, but matching same-semantics baseline artifacts are incomplete"

    return {
        "baseline_status": status,
        "baseline_complete_for_speedup_review": baseline_complete_for_review,
        "public_speedup_claim_authorized": False,
        "baseline_reason": reason,
        "required_baseline_count": len(checks),
        "valid_baseline_count": len(valid),
        "missing_baseline_count": len(missing),
        "invalid_baseline_count": len(invalid),
        "active_gate_status": active_status,
        "active_blocking_baseline_count": len(blocking_checks),
        "active_skipped_baseline_count": len(skipped_checks),
        "baseline_checks": [
            {
                "baseline": item.get("baseline"),
                "status": item.get("status"),
                "path": item.get("path"),
                "errors": item.get("errors", []),
            }
            for item in checks
        ],
    }


def build_package() -> dict[str, Any]:
    readiness_by_key, active_by_key = _baseline_maps()
    rows: list[dict[str, Any]] = []
    group_statuses: list[dict[str, Any]] = []

    for name in GROUP_REPORTS:
        report_path = ROOT / "docs" / "reports" / name
        report = _load_json(report_path)
        group_statuses.append(
            {
                "path": str(report_path),
                "status": report.get("status"),
                "entry_count": report.get("entry_count"),
                "failure_count": report.get("failure_count"),
            }
        )
        for row in report.get("rows", ()):
            baseline = _baseline_summary(row, readiness_by_key, active_by_key)
            public_wording = rt.rtx_public_wording_status(str(row.get("app")))
            rows.append(
                {
                    "app": row.get("app"),
                    "path_name": row.get("path_name"),
                    "rtx_artifact_status": row.get("artifact_status"),
                    "runner_status": row.get("runner_status"),
                    "cloud_contract_status": row.get("cloud_contract_status"),
                    "claim_scope": _claim_scope(row),
                    "non_claim": _non_claim(row),
                    "rtx_native_or_query_phase_sec": _rtx_phase_seconds(row),
                    "current_public_wording_status": public_wording.status,
                    "current_public_wording_boundary": public_wording.boundary,
                    **baseline,
                }
            )

    complete = [row for row in rows if row["baseline_status"] == COMPLETE_BASELINE_STATUS]
    active_limited = [row for row in rows if row["baseline_status"] == ACTIVE_GATE_LIMITED_STATUS]
    pending = [row for row in rows if row["baseline_status"] == BASELINE_PENDING_STATUS]
    bad_rtx = [
        row for row in rows
        if row["rtx_artifact_status"] != "ok"
        or row["runner_status"] != "ok"
        or row["cloud_contract_status"] != "ok"
    ]

    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_artifact_reports": GROUP_REPORTS,
        "source_baseline_gate": "scripts.goal836_rtx_baseline_readiness_gate.analyze_plan()",
        "source_active_gate": "scripts.goal846_active_rtx_claim_gate.build_active_claim_gate()",
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "group_count": len(group_statuses),
        "row_count": len(rows),
        "rtx_artifact_ready_count": len(rows) - len(bad_rtx),
        "bad_rtx_artifact_count": len(bad_rtx),
        "same_semantics_baselines_complete_count": len(complete),
        "active_gate_limited_count": len(active_limited),
        "baseline_pending_count": len(pending),
        "baseline_complete_for_speedup_review_count": sum(
            1 for row in rows if row["baseline_complete_for_speedup_review"]
        ),
        "public_speedup_claim_authorized_count": sum(
            1 for row in rows if row["public_speedup_claim_authorized"]
        ),
        "group_statuses": group_statuses,
        "rows": rows,
        "boundary": (
            "Goal971 packages post-Goal969 RTX A5000 evidence against local same-semantics baseline readiness. "
            "It does not authorize public speedup wording. Public speedup language still requires separate "
            "2-AI review of comparable baselines, phase separation, and claim scope."
        ),
    }


def _fmt_sec(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.6f}"
    return ""


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal971 Post-Goal969 Baseline/Speedup Review Package",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- RTX artifact rows: `{payload['row_count']}`",
        f"- RTX artifact-ready rows: `{payload['rtx_artifact_ready_count']}`",
        f"- strict same-semantics baseline-complete rows: `{payload['same_semantics_baselines_complete_count']}`",
        f"- active-gate limited rows: `{payload['active_gate_limited_count']}`",
        f"- baseline-pending rows: `{payload['baseline_pending_count']}`",
        f"- baseline-complete rows ready for separate speedup review: `{payload['baseline_complete_for_speedup_review_count']}`",
        f"- public speedup claims authorized by this package: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## App/Path Status",
        "",
        "| App | Path | RTX phase (s) | RTX artifact | Baseline status | Current public wording | Valid / Required | Public speedup authorized? |",
        "| --- | --- | ---: | --- | --- | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | {_fmt_sec(row['rtx_native_or_query_phase_sec'])} | "
            f"`{row['rtx_artifact_status']}` | `{row['baseline_status']}` | "
            f"`{row['current_public_wording_status']}` | "
            f"{row['valid_baseline_count']} / {row['required_baseline_count']} | "
            f"`{row['public_speedup_claim_authorized']}` |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- `same_semantics_baselines_complete` means the strict Goal836 required baseline set is present and valid; this still needs review before public speedup wording.",
            "- `active_gate_complete_but_full_baseline_review_limited` means an older active gate has enough blocking evidence for internal review, but optional or unsupported baselines are not fully complete.",
            "- `rtx_artifact_ready_baseline_pending` means the RT sub-path ran on A5000, but same-semantics baseline evidence must be collected before speedup comparison.",
            "- No row in this package authorizes a whole-app speedup claim.",
            "- Release-facing wording must follow `rtdsl.rtx_public_wording_matrix()` rather than this baseline package alone.",
            "",
            "## Missing Or Invalid Baseline Detail",
            "",
        ]
    )
    for row in payload["rows"]:
        bad = [item for item in row["baseline_checks"] if item["status"] != "valid"]
        if not bad:
            continue
        lines.append(f"### {row['app']} / {row['path_name']}")
        lines.append("")
        for item in bad:
            lines.append(f"- `{item['baseline']}`: `{item['status']}`")
            for error in item.get("errors", ()):
                lines.append(f"- error: {error}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build post-Goal969 RTX baseline/speedup review package.")
    parser.add_argument("--output-json", default="docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.md")
    args = parser.parse_args(argv)

    payload = build_package()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["bad_rtx_artifact_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
