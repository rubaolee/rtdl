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

from scripts.goal835_rtx_baseline_collection_plan import build_plan
from scripts.goal836_rtx_baseline_readiness_gate import expected_artifact_path
from scripts.goal836_rtx_baseline_readiness_gate import validate_artifact


GOAL = "Goal860 spatial partial-ready gate"
DATE = "2026-04-23"
SPATIAL_APPS = {"service_coverage_gaps", "event_hotspot_screening"}
OPTIONAL_BASELINES = {"scipy_baseline_when_available"}
RTX_ARTIFACTS = {
    ("service_coverage_gaps", "prepared_gap_summary"): ROOT / "docs" / "reports" / "goal811_service_coverage_rtx.json",
    ("event_hotspot_screening", "prepared_count_summary"): ROOT / "docs" / "reports" / "goal811_event_hotspot_rtx.json",
}


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _rtx_artifact_status(app: str, path_name: str) -> dict[str, Any]:
    artifact_path = RTX_ARTIFACTS[(app, path_name)]
    if not artifact_path.exists():
        return {
            "path": str(artifact_path),
            "status": "missing",
            "reason": "real RTX phase artifact has not been collected yet",
        }
    payload = _load_json(artifact_path)
    if payload is None:
        return {
            "path": str(artifact_path),
            "status": "invalid",
            "reason": "artifact is unreadable",
        }
    scenario = payload.get("scenario")
    if not isinstance(scenario, dict):
        return {
            "path": str(artifact_path),
            "status": "invalid",
            "reason": "scenario payload missing",
        }
    mode = scenario.get("mode")
    timings = scenario.get("timings_sec")
    if mode != "optix":
        return {
            "path": str(artifact_path),
            "status": "invalid",
            "reason": f"expected real optix mode artifact, got {mode!r}",
        }
    if not isinstance(timings, dict) or "optix_query" not in timings:
        return {
            "path": str(artifact_path),
            "status": "invalid",
            "reason": "optix_query timing missing",
        }
    return {
        "path": str(artifact_path),
        "status": "valid",
        "scenario": scenario.get("scenario"),
        "mode": mode,
    }


def build_spatial_gate() -> dict[str, Any]:
    plan = build_plan()
    rows_out: list[dict[str, Any]] = []
    required_valid = 0
    required_missing = 0
    required_invalid = 0

    for row in plan["rows"]:
        app = str(row["app"])
        if app not in SPATIAL_APPS:
            continue
        required_checks: list[dict[str, Any]] = []
        optional_checks: list[dict[str, Any]] = []
        for baseline in row["required_baselines"]:
            check = validate_artifact(row, baseline, expected_artifact_path(row, baseline))
            if baseline in OPTIONAL_BASELINES:
                optional_checks.append(check)
            else:
                required_checks.append(check)
                if check["status"] == "valid":
                    required_valid += 1
                elif check["status"] == "missing":
                    required_missing += 1
                elif check["status"] == "invalid":
                    required_invalid += 1
        rtx_status = _rtx_artifact_status(app, str(row["path_name"]))
        row_status = "needs_required_baselines"
        if all(item["status"] == "valid" for item in required_checks):
            row_status = "needs_real_rtx_artifact"
            if rtx_status["status"] == "valid":
                row_status = "ready_for_review"
        rows_out.append(
            {
                "app": app,
                "path_name": row["path_name"],
                "claim_limit": row["claim_limit"],
                "required_checks": required_checks,
                "optional_checks": optional_checks,
                "rtx_artifact": rtx_status,
                "row_status": row_status,
            }
        )

    status = "needs_required_baselines"
    if rows_out and all(row["row_status"] == "ready_for_review" for row in rows_out):
        status = "ready_for_review"
    elif rows_out and all(row["row_status"] in {"needs_real_rtx_artifact", "ready_for_review"} for row in rows_out):
        status = "needs_real_rtx_artifact"

    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "row_count": len(rows_out),
        "required_valid_artifact_count": required_valid,
        "required_missing_artifact_count": required_missing,
        "required_invalid_artifact_count": required_invalid,
        "status": status,
        "rows": rows_out,
        "boundary": (
            "This gate is for the two spatial prepared-summary apps only. It requires same-semantics local baselines "
            "before the apps can move toward active RTX review, and it still requires a real OptiX phase artifact "
            "before any promotion or claim review."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal860 Spatial Partial-Ready Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rows checked: `{payload['row_count']}`",
        f"- required valid artifacts: `{payload['required_valid_artifact_count']}`",
        f"- required missing artifacts: `{payload['required_missing_artifact_count']}`",
        f"- required invalid artifacts: `{payload['required_invalid_artifact_count']}`",
        "",
        "## Row Status",
        "",
        "| App | Path | Status | Required Valid | Required Missing | RTX Artifact |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['app']} | {row['path_name']} | {row['row_status']} | "
            f"{sum(1 for item in row['required_checks'] if item['status'] == 'valid')} | "
            f"{sum(1 for item in row['required_checks'] if item['status'] == 'missing')} | "
            f"{row['rtx_artifact']['status']} |"
        )
    lines.extend(["", "## Details", ""])
    for row in payload["rows"]:
        lines.append(f"### {row['app']} / {row['path_name']}")
        lines.append("")
        lines.append(f"- claim limit: {row['claim_limit']}")
        lines.append(f"- RTX artifact: `{row['rtx_artifact']['status']}` at `{row['rtx_artifact']['path']}`")
        if row["rtx_artifact"]["status"] != "valid":
            lines.append(f"- RTX artifact reason: {row['rtx_artifact'].get('reason')}")
        lines.append("")
        for item in row["required_checks"]:
            lines.append(f"- required `{item['baseline']}`: `{item['status']}`")
        for item in row["optional_checks"]:
            lines.append(f"- optional `{item['baseline']}`: `{item['status']}`")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check spatial prepared-summary baseline and RTX readiness.")
    parser.add_argument("--output-json", default="docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.json")
    parser.add_argument("--output-md", default="docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.generated.md")
    args = parser.parse_args(argv)
    payload = build_spatial_gate()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] == "ready_for_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
