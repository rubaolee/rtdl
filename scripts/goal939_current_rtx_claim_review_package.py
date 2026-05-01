#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


GOAL = "Goal939 current RTX claim-review package"
DATE = "2026-04-25"
READY_FOR_RTX_CLAIM_REVIEW = "ready_for_rtx_claim_review"
RT_CORE_READY = "rt_core_ready"

NATIVE_CONTINUATION_SUMMARY = (
    "Every ready app must expose native_continuation_active and "
    "native_continuation_backend in the relevant app payloads. These fields "
    "describe the native traversal/summary continuation and do not by "
    "themselves authorize a speedup claim."
)


def _is_ready(app: str) -> bool:
    readiness = rt.optix_app_benchmark_readiness(app)
    maturity = rt.rt_core_app_maturity(app)
    return (
        readiness.status == READY_FOR_RTX_CLAIM_REVIEW
        and maturity.current_status == RT_CORE_READY
    )


def _row(app: str) -> dict[str, Any]:
    readiness = rt.optix_app_benchmark_readiness(app)
    maturity = rt.rt_core_app_maturity(app)
    performance = rt.optix_app_performance_matrix()[app]
    public_wording = rt.rtx_public_wording_status(app)
    return {
        "app": app,
        "readiness_status": readiness.status,
        "rt_core_status": maturity.current_status,
        "performance_class": performance.performance_class,
        "public_wording_status": public_wording.status,
        "public_wording": public_wording.reviewed_wording,
        "public_wording_evidence": public_wording.evidence,
        "public_wording_boundary": public_wording.boundary,
        "native_continuation_required": True,
        "next_goal_or_evidence": readiness.next_goal,
        "allowed_claim": readiness.allowed_claim,
        "benchmark_contract": readiness.benchmark_contract,
        "non_claim_or_blocker": readiness.blocker,
        "required_action": maturity.required_action,
        "cloud_policy": maturity.cloud_policy,
    }


def build_package() -> dict[str, Any]:
    rows = [_row(app) for app in rt.public_apps() if _is_ready(app)]
    public_wording_rows = rt.rtx_public_wording_matrix()
    reviewed_public_wording = [
        app for app, row in public_wording_rows.items() if row.status == "public_wording_reviewed"
    ]
    blocked_public_wording = [
        app for app, row in public_wording_rows.items() if row.status == "public_wording_blocked"
    ]
    held_rows = [
        {
            "app": app,
            "readiness_status": rt.optix_app_benchmark_readiness(app).status,
            "rt_core_status": rt.rt_core_app_maturity(app).current_status,
            "allowed_claim": rt.optix_app_benchmark_readiness(app).allowed_claim,
            "blocker": rt.optix_app_benchmark_readiness(app).blocker,
        }
        for app in rt.public_apps()
        if not _is_ready(app)
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_of_truth": {
            "readiness": "rtdsl.optix_app_benchmark_readiness_matrix()",
            "maturity": "rtdsl.rt_core_app_maturity_matrix()",
            "public_wording": "rtdsl.rtx_public_wording_matrix()",
            "packet": "docs/reports/goal937_ready_rtx_claim_review_packet_2026-04-25.md",
        },
        "ready_count": len(rows),
        "reviewed_public_wording_count": len(reviewed_public_wording),
        "blocked_public_wording_count": len(blocked_public_wording),
        "held_count": len(held_rows),
        "ready_apps": [row["app"] for row in rows],
        "reviewed_public_wording_apps": reviewed_public_wording,
        "blocked_public_wording_apps": blocked_public_wording,
        "native_continuation_summary": NATIVE_CONTINUATION_SUMMARY,
        "rows": rows,
        "held_rows": held_rows,
        "public_wording_pattern": (
            "RTDL includes a bounded NVIDIA OptiX/RTX-backed sub-path for <app>: <allowed_claim>. "
            "The claim covers that native traversal/summary phase only; excluded work remains outside the claim."
        ),
        "forbidden_wording": [
            "RTDL accelerates the whole app",
            "RTDL beats CPU/PostGIS/Embree",
            "All graph/database/spatial work is RT-core accelerated",
            "Polygon area/Jaccard is fully native OptiX",
        ],
        "boundary": (
            "This package is a current claim-review index. It does not run benchmarks, "
            "does not start cloud resources, does not promote held apps, and does not "
            "authorize public speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal939 Current RTX Claim-Review Package",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- ready claim-review rows: `{payload['ready_count']}`",
        f"- reviewed public wording rows: `{payload['reviewed_public_wording_count']}`",
        f"- blocked public wording rows: `{payload['blocked_public_wording_count']}`",
        f"- held or out-of-target rows: `{payload['held_count']}`",
        "- source of truth: `rtdsl.optix_app_benchmark_readiness_matrix()` plus `rtdsl.rt_core_app_maturity_matrix()` plus `rtdsl.rtx_public_wording_matrix()`",
        "",
            "## Ready Rows",
            "",
        "| App | Performance class | Public wording status | Native-continuation required | Evidence/goals | Allowed claim | Non-claim boundary |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['performance_class']}` | `{row['public_wording_status']}` | `{row['native_continuation_required']}` | {row['next_goal_or_evidence']} | "
            f"{row['allowed_claim']} | {row['non_claim_or_blocker']} |"
        )
    lines.extend(
        [
            "",
            "## Held Rows",
            "",
            "| App | Readiness | RT-core status | Boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in payload["held_rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['readiness_status']}` | `{row['rt_core_status']}` | {row['blocker']} |"
        )
    lines.extend(
        [
            "",
            "## Public Wording Pattern",
            "",
            payload["native_continuation_summary"],
            "",
            "Only rows with `public_wording_reviewed` may use a reviewed public speedup wording. Rows with `public_wording_blocked` or `public_wording_not_reviewed` remain technical claim-review rows only.",
            "",
            payload["public_wording_pattern"],
            "",
            "Forbidden wording:",
            "",
        ]
    )
    for phrase in payload["forbidden_wording"]:
        lines.append(f"- {phrase}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This package is an index for review. It is not release authorization and not a benchmark result.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the current RTX claim-review package from live matrices.")
    parser.add_argument("--output-json", default="docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.json")
    parser.add_argument("--output-md", default="docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.md")
    args = parser.parse_args(argv)

    payload = build_package()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(to_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
