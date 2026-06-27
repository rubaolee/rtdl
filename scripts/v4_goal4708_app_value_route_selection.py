from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4708_app_value_route_selection import validate_v4_goal4708_app_value_route_selection


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    selection = payload["selection"]
    lines = [
        "# V4 Goal4708 App-Level Value Route Selection",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- status: `{selection['status']}`",
        f"- selected app-level route: `{selection['selected_app_level_route']}`",
        f"- operator candidate route: `{selection['operator_candidate_route']}`",
        f"- decision: {selection['decision']}",
        "",
        "| target | classification | app-level claim | reason |",
        "|---|---|---|---|",
    ]
    for row in selection["route_rows"]:
        lines.append(
            f"| `{row['target']}` | `{row['classification']}` | `{row['app_level_claim_authorized']}` | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate forbids counting the specialized Tier-3 operator candidate as app-level high-performance V4 evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V4 Goal4708 app-level route-selection evidence.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    validation = validate_v4_goal4708_app_value_route_selection()
    payload = {
        "schema": "rtdl.v4.goal4708_app_value_route_selection.v1",
        "validation_status": validation["status"],
        **validation,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if validation["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
