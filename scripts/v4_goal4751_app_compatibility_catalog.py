#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rtdsl.v4_app_compatibility import validate_v4_app_compatibility_catalog
from rtdsl.v4_app_compatibility import v4_app_compatibility_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = (
    ROOT / "future" / "v4" / "evidence" / "v4_goal4751_app_compatibility_catalog_2026-06-26.json"
)
DEFAULT_REPORT = ROOT / "future" / "v4" / "v4_goal4751_app_compatibility_catalog_2026-06-26.md"


def _render_report(payload: dict[str, object]) -> str:
    lines = [
        "# V4 Goal4751 App Compatibility Superset Catalog",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This catalog makes the V4.0 superset obligation explicit at the app level.",
        "It does not complete the compatibility repairs by itself; it identifies the",
        "remaining V4.0 repair rows before the final POD matrix.",
        "",
        "## Rows",
        "",
        "| App | Status | V4 route status | CuPy | Numba |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:  # type: ignore[index]
        lines.append(
            f"| `{row['app']}` | `{row['status']}` | `{row['v4_route_status']}` | "
            f"{row['cupy_status']} | {row['numba_status']} |"
        )
    lines.extend(["", "## Repair Required", ""])
    repair = [row for row in payload["rows"] if row["status"] == "compatibility_repair_required"]  # type: ignore[index]
    for row in repair:
        lines.append(f"- `{row['app']}`: {row['blocker']}")
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "This catalog does not authorize release, public speed claims, or treating inherited compatibility as V4-new speedup.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write V4 Goal4751 app compatibility catalog artifacts.")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload = {
        "schema": "rtdl.v4.goal4751.app_compatibility_catalog.v1",
        "status": "goal4751_app_compatibility_catalog_written_repairs_in_progress",
        "validation": validate_v4_app_compatibility_catalog(),
        "rows": list(v4_app_compatibility_rows()),
        "claim_boundary": {
            "release_authorized": False,
            "public_speed_claim_authorized": False,
            "inherited_compatibility_counts_as_speed": False,
        },
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(_render_report(payload), encoding="utf-8")
    print(args.evidence)
    print(args.report)
    print(payload["validation"]["status"])
    return 0 if payload["validation"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
