from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4712_next_lever_after_custom_scored_failure import (
    validate_v4_goal4712_next_lever_after_custom_scored_failure,
)


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    selection = payload["selection"]
    contract = selection["selected_target_contract"]
    lines = [
        "# V4 Goal4712 Next Lever After Custom-Scored Failure",
        "",
        f"- validation: `{payload['status']}`",
        f"- status: `{selection['status']}`",
        f"- selected target: `{selection['selected_target']}`",
        f"- next goal: `{selection['next_goal']}`",
        "",
        "## Failure Fact",
        "",
        f"- source goal: `{selection['failure_fact']['source_goal']}`",
        f"- failed target: `{selection['failure_fact']['failed_target']}`",
        f"- classification: `{selection['failure_fact']['classification']}`",
        f"- primary geomean V3 speedup: `{selection['failure_fact']['primary_geomean_v3_speedup']}`",
        f"- min primary V3 speedup: `{selection['failure_fact']['min_primary_v3_speedup']}`",
        "",
        "## Selected Contract",
        "",
        f"- generic feature: `{contract['generic_feature_under_test']}`",
        f"- app family: `{contract['app_family']}`",
        f"- allowed callback shape: `{contract['allowed_callback_shape']}`",
        f"- engine-owned action: `{contract['engine_owned_action']}`",
        "",
        contract["why_this_can_win"],
        "",
        "## Rejected Patterns",
        "",
        "| pattern | reason |",
        "|---|---|",
    ]
    for row in selection["rejected_patterns"]:
        lines.append(f"| `{row['pattern']}` | {row['reason']} |")
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "- POD is not authorized by Goal4712.",
            "- V4 release is not authorized.",
            "- Formal high-performance V4 wording is not authorized.",
            "- Public Tier-3 support is not authorized.",
            "- Arbitrary callback or raw OptiX callback support is not authorized.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit V4 Goal4712 next lever selection after Goal4711 failure.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    payload = validate_v4_goal4712_next_lever_after_custom_scored_failure()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
