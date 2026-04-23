#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal835_rtx_baseline_collection_plan import build_plan


GOAL = "Goal836 RTX baseline readiness gate"
DATE = "2026-04-23"


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()


def expected_artifact_path(row: dict[str, Any], baseline_name: str, artifact_root: Path = ROOT) -> Path:
    stub = str(row["baseline_artifact_stub"])
    return artifact_root / stub.replace("<backend>", _slug(baseline_name))


def _load_artifact(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact JSON errors vary by Python.
        return None, f"unreadable_json: {exc}"
    if not isinstance(payload, dict):
        return None, "artifact root is not a JSON object"
    return payload, None


def _phase_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def validate_artifact(row: dict[str, Any], baseline_name: str, path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "baseline": baseline_name,
            "path": str(path),
            "status": "missing",
            "errors": ["artifact file is missing"],
        }

    payload, load_error = _load_artifact(path)
    if payload is None:
        return {
            "baseline": baseline_name,
            "path": str(path),
            "status": "invalid",
            "errors": [str(load_error)],
        }

    errors: list[str] = []
    if payload.get("app") != row.get("app"):
        errors.append(f"app mismatch: expected {row.get('app')!r}, got {payload.get('app')!r}")
    if payload.get("path_name") != row.get("path_name"):
        errors.append(f"path_name mismatch: expected {row.get('path_name')!r}, got {payload.get('path_name')!r}")
    if payload.get("baseline_name") != baseline_name:
        errors.append(f"baseline_name mismatch: expected {baseline_name!r}, got {payload.get('baseline_name')!r}")
    if payload.get("status") != "ok":
        errors.append(f"status must be 'ok', got {payload.get('status')!r}")
    if payload.get("correctness_parity") is not True:
        errors.append("correctness_parity must be true")
    if payload.get("phase_separated") is not True:
        errors.append("phase_separated must be true")
    if payload.get("authorizes_public_speedup_claim") is not False:
        errors.append("authorizes_public_speedup_claim must be false")

    repeated_runs = payload.get("repeated_runs")
    if not isinstance(repeated_runs, int) or repeated_runs < int(row.get("minimum_repeated_runs") or 0):
        errors.append(
            f"repeated_runs must be >= {row.get('minimum_repeated_runs')}, got {repeated_runs!r}"
        )

    covered = set(_phase_list(payload.get("required_phase_coverage")))
    required = set(_phase_list(row.get("required_phases")))
    missing_phases = sorted(required - covered)
    if missing_phases:
        errors.append(f"missing required phase coverage: {', '.join(missing_phases)}")

    metric_scope = payload.get("comparable_metric_scope")
    if metric_scope != row.get("comparable_metric_scope"):
        errors.append("comparable_metric_scope does not match Goal835 plan")

    return {
        "baseline": baseline_name,
        "path": str(path),
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "repeated_runs": repeated_runs,
        "covered_phase_count": len(covered),
    }


def analyze_plan(plan: dict[str, Any] | None = None, artifact_root: Path = ROOT) -> dict[str, Any]:
    if plan is None:
        plan = build_plan()
    rows_out: list[dict[str, Any]] = []
    missing_count = 0
    invalid_count = 0
    valid_count = 0

    for row in plan.get("rows", ()):
        required_baselines = [str(item) for item in row.get("required_baselines", ())]
        artifact_checks = [
            validate_artifact(row, baseline, expected_artifact_path(row, baseline, artifact_root))
            for baseline in required_baselines
        ]
        missing = [item for item in artifact_checks if item["status"] == "missing"]
        invalid = [item for item in artifact_checks if item["status"] == "invalid"]
        valid = [item for item in artifact_checks if item["status"] == "valid"]
        missing_count += len(missing)
        invalid_count += len(invalid)
        valid_count += len(valid)
        rows_out.append(
            {
                "section": row.get("section"),
                "app": row.get("app"),
                "path_name": row.get("path_name"),
                "required_baselines": required_baselines,
                "required_phases": row.get("required_phases"),
                "claim_limit": row.get("claim_limit"),
                "artifact_checks": artifact_checks,
                "row_status": "ok" if not missing and not invalid else "needs_baselines",
            }
        )

    required_count = missing_count + invalid_count + valid_count
    status = "ok" if required_count and not missing_count and not invalid_count else "needs_baselines"
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_plan_goal": plan.get("goal"),
        "row_count": len(rows_out),
        "active_count": sum(1 for row in rows_out if row["section"] == "active"),
        "deferred_count": sum(1 for row in rows_out if row["section"] == "deferred"),
        "required_artifact_count": required_count,
        "valid_artifact_count": valid_count,
        "missing_artifact_count": missing_count,
        "invalid_artifact_count": invalid_count,
        "status": status,
        "rows": rows_out,
        "boundary": (
            "This readiness gate only inspects local baseline evidence. It does not run benchmarks, "
            "start cloud resources, promote deferred apps, or authorize RTX speedup claims."
        ),
    }


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal836 RTX Baseline Readiness Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rows checked: `{payload['row_count']}`",
        f"- required baseline artifacts: `{payload['required_artifact_count']}`",
        f"- valid artifacts: `{payload['valid_artifact_count']}`",
        f"- missing artifacts: `{payload['missing_artifact_count']}`",
        f"- invalid artifacts: `{payload['invalid_artifact_count']}`",
        "",
        "## Row Readiness",
        "",
        "| Section | App | Path | Status | Missing | Invalid | Valid |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        checks = row["artifact_checks"]
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row["section"]),
                    _fmt(row["app"]),
                    _fmt(row["path_name"]),
                    _fmt(row["row_status"]),
                    str(sum(1 for item in checks if item["status"] == "missing")),
                    str(sum(1 for item in checks if item["status"] == "invalid")),
                    str(sum(1 for item in checks if item["status"] == "valid")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Missing Or Invalid Baselines", ""])
    for row in payload["rows"]:
        bad = [item for item in row["artifact_checks"] if item["status"] != "valid"]
        if not bad:
            continue
        lines.append(f"### {row['app']} / {row['path_name']}")
        lines.append("")
        for item in bad:
            lines.append(f"- `{item['baseline']}`: `{item['status']}` at `{item['path']}`")
            for error in item.get("errors", ()):
                lines.append(f"- error: {error}")
        lines.append("")
    lines.extend(
        [
            "## Release Rule",
            "",
            "An RTX speedup claim package is incomplete while this gate reports `needs_baselines`.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Goal835 baseline artifacts before RTX claim review.")
    parser.add_argument("--output-json", default="docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json")
    parser.add_argument("--output-md", default="docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.generated.md")
    args = parser.parse_args(argv)
    payload = analyze_plan()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
