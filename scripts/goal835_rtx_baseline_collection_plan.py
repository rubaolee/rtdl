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

from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest


GOAL = "Goal835 RTX baseline collection plan"
DATE = "2026-04-23"


def _rows(section: str, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        contract = entry.get("baseline_review_contract")
        if not isinstance(contract, dict):
            contract = {}
        rows.append(
            {
                "section": section,
                "app": entry.get("app"),
                "path_name": entry.get("path_name"),
                "command": entry.get("command"),
                "scale": entry.get("scale"),
                "claim_scope": entry.get("claim_scope"),
                "non_claim": entry.get("non_claim"),
                "baseline_status": contract.get("status"),
                "comparable_metric_scope": contract.get("comparable_metric_scope"),
                "required_baselines": list(contract.get("required_baselines", ())),
                "required_phases": list(contract.get("required_phases", ())),
                "claim_limit": contract.get("claim_limit"),
                "minimum_repeated_runs": contract.get("minimum_repeated_runs"),
                "requires_correctness_parity": contract.get("requires_correctness_parity"),
                "requires_phase_separation": contract.get("requires_phase_separation"),
                "forbidden_comparison": contract.get("forbidden_comparison"),
                "baseline_artifact_stub": (
                    f"docs/reports/goal835_baseline_{entry.get('app')}_{entry.get('path_name')}_<backend>_2026-04-23.json"
                ),
            }
        )
    return rows


def build_plan() -> dict[str, Any]:
    manifest = build_manifest()
    rows = [
        *_rows("active", list(manifest.get("entries", ()))),
        *_rows("deferred", list(manifest.get("deferred_entries", ()))),
    ]
    invalid = [
        row for row in rows
        if row.get("baseline_status") != "required_before_public_speedup_claim"
        or not row.get("required_baselines")
        or not row.get("required_phases")
        or row.get("requires_correctness_parity") is not True
        or row.get("requires_phase_separation") is not True
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_manifest_goal": manifest.get("goal"),
        "active_count": sum(1 for row in rows if row["section"] == "active"),
        "deferred_count": sum(1 for row in rows if row["section"] == "deferred"),
        "row_count": len(rows),
        "invalid_count": len(invalid),
        "rows": rows,
        "status": "ok" if not invalid else "needs_attention",
        "boundary": (
            "This plan is a local baseline checklist. It does not run benchmarks, "
            "start cloud, promote deferred apps, or authorize RTX speedup claims."
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
        "# Goal835 RTX Baseline Collection Plan",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- active entries: `{payload['active_count']}`",
        f"- deferred entries: `{payload['deferred_count']}`",
        f"- invalid entries: `{payload['invalid_count']}`",
        "",
        "## Baseline Checklist",
        "",
        "| Section | App | Path | Required baselines | Required phases | Claim limit |",
        "|---|---|---|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row["section"]),
                    _fmt(row["app"]),
                    _fmt(row["path_name"]),
                    _fmt(row["required_baselines"]),
                    _fmt(row["required_phases"]),
                    _fmt(row["claim_limit"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Review Rule",
            "",
            "A public RTX speedup claim may not be made from a cloud artifact unless the matching row above has same-semantics baseline artifacts, correctness parity, and phase-separated timing.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the Goal835 RTX baseline collection plan.")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args(argv)
    payload = build_plan()
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    if args.output_md:
        Path(args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
