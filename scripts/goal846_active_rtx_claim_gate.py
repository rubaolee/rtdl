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
from scripts.goal838_local_baseline_collection_manifest import build_collection_manifest


GOAL = "Goal846 active RTX claim gate"
DATE = "2026-04-23"
BLOCKING_STATUSES = {
    "local_command_ready",
    "linux_postgresql_required",
    "linux_preferred_for_large_exact_oracle",
}


def build_active_claim_gate() -> dict[str, Any]:
    readiness = analyze_plan()
    manifest = build_collection_manifest()

    action_by_key = {
        (str(action["app"]), str(action["path_name"]), str(action["baseline"])): action
        for action in manifest["actions"]
    }

    rows_out: list[dict[str, Any]] = []
    valid_count = 0
    missing_count = 0
    invalid_count = 0
    skipped_count = 0

    for row in readiness["rows"]:
        if row["section"] != "active":
            continue
        blocking_checks: list[dict[str, Any]] = []
        skipped_checks: list[dict[str, Any]] = []
        for check in row["artifact_checks"]:
            key = (str(row["app"]), str(row["path_name"]), str(check["baseline"]))
            action = action_by_key.get(key)
            action_status = None if action is None else str(action["status"])
            item = {
                **check,
                "collection_status": action_status,
            }
            if action_status in BLOCKING_STATUSES:
                blocking_checks.append(item)
                if check["status"] == "valid":
                    valid_count += 1
                elif check["status"] == "missing":
                    missing_count += 1
                elif check["status"] == "invalid":
                    invalid_count += 1
            else:
                skipped_checks.append(item)
                skipped_count += 1
        rows_out.append(
            {
                "app": row["app"],
                "path_name": row["path_name"],
                "blocking_checks": blocking_checks,
                "skipped_checks": skipped_checks,
                "row_status": "ok"
                if all(item["status"] == "valid" for item in blocking_checks)
                else "needs_blocking_baselines",
            }
        )

    required_count = valid_count + missing_count + invalid_count
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_gate_goal": readiness["goal"],
        "source_manifest_goal": manifest["goal"],
        "blocking_statuses": sorted(BLOCKING_STATUSES),
        "row_count": len(rows_out),
        "required_artifact_count": required_count,
        "valid_artifact_count": valid_count,
        "missing_artifact_count": missing_count,
        "invalid_artifact_count": invalid_count,
        "skipped_optional_or_deferred_count": skipped_count,
        "status": "ok" if required_count and not missing_count and not invalid_count else "needs_blocking_baselines",
        "rows": rows_out,
        "boundary": (
            "This gate is for active OptiX claim-review readiness only. It counts mandatory active same-semantics "
            "baselines and explicitly excludes optional reference baselines and deferred app rows. It does not "
            "authorize a public RTX speedup claim by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal846 Active RTX Claim Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- active rows checked: `{payload['row_count']}`",
        f"- mandatory active baseline artifacts: `{payload['required_artifact_count']}`",
        f"- valid mandatory artifacts: `{payload['valid_artifact_count']}`",
        f"- missing mandatory artifacts: `{payload['missing_artifact_count']}`",
        f"- invalid mandatory artifacts: `{payload['invalid_artifact_count']}`",
        f"- skipped optional/deferred artifacts: `{payload['skipped_optional_or_deferred_count']}`",
        "",
        "## Row Readiness",
        "",
        "| App | Path | Status | Mandatory Valid | Mandatory Missing | Mandatory Invalid | Skipped Optional/Deferred |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        blocking = row["blocking_checks"]
        skipped = row["skipped_checks"]
        lines.append(
            f"| {row['app']} | {row['path_name']} | {row['row_status']} | "
            f"{sum(1 for item in blocking if item['status'] == 'valid')} | "
            f"{sum(1 for item in blocking if item['status'] == 'missing')} | "
            f"{sum(1 for item in blocking if item['status'] == 'invalid')} | "
            f"{len(skipped)} |"
        )
    lines.extend(["", "## Blocking Gaps", ""])
    for row in payload["rows"]:
        bad = [item for item in row["blocking_checks"] if item["status"] != "valid"]
        if not bad:
            continue
        lines.append(f"### {row['app']} / {row['path_name']}")
        lines.append("")
        for item in bad:
            lines.append(
                f"- `{item['baseline']}`: `{item['status']}` at `{item['path']}` "
                f"(collection status: `{item.get('collection_status')}`)"
            )
            for error in item.get("errors", ()):
                lines.append(f"- error: {error}")
        lines.append("")
    lines.extend(["## Non-Blocking Exclusions", ""])
    for row in payload["rows"]:
        if not row["skipped_checks"]:
            continue
        lines.append(f"### {row['app']} / {row['path_name']}")
        lines.append("")
        for item in row["skipped_checks"]:
            lines.append(
                f"- `{item['baseline']}` excluded from this gate "
                f"(collection status: `{item.get('collection_status')}`, artifact status: `{item['status']}`)"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check active mandatory RTX claim baselines only.")
    parser.add_argument("--output-json", default="docs/reports/goal846_active_rtx_claim_gate_2026-04-23.json")
    parser.add_argument("--output-md", default="docs/reports/goal846_active_rtx_claim_gate_2026-04-23.generated.md")
    args = parser.parse_args(argv)
    payload = build_active_claim_gate()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
