from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4709_formal_hp_app_target_selection import validate_v4_goal4709_formal_hp_app_target_selection


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    selection = payload["selection"]
    contract = selection["selected_target_contract"]
    lines = [
        "# V4 Goal4709 Formal High-Performance App Target Selection",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- selected app: `{selection['selected_app']}`",
        f"- POD authorized: `{selection['pod_authorized']}`",
        f"- next goal: `{selection['next_goal']}`",
        "",
        "## Selected Target Contract",
        "",
        f"- app family: {contract['app_family']}",
        f"- generic feature: {contract['generic_feature_under_test']}",
        f"- not app-specific kernel: `{contract['not_app_specific_kernel']}`",
        f"- minimum scale: {contract['minimum_scale']}",
        "",
        "## Rejected Existing Targets",
        "",
        "| target | reason |",
        "|---|---|",
    ]
    for row in selection["rejected_existing_targets"]:
        lines.append(f"| `{row['target']}` | {row['reason']} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Goal4709 selects a target and authorizes only Goal4710 protocol freeze. It does not authorize POD spend, app-level speed claims, release wording, or public Tier-3 support.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V4 Goal4709 formal app-level target selection evidence.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    validation = validate_v4_goal4709_formal_hp_app_target_selection()
    payload = {
        "schema": "rtdl.v4.goal4709_formal_hp_app_target_selection.v1",
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
