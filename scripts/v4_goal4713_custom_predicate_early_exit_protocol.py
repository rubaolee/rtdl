from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4713_custom_predicate_early_exit_protocol import (
    validate_v4_goal4713_custom_predicate_early_exit_protocol,
)


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    protocol = payload["protocol"]
    lines = [
        "# V4 Goal4713 Custom Predicate Early-Exit Protocol",
        "",
        f"- validation: `{payload['status']}`",
        f"- status: `{protocol['status']}`",
        f"- app: `{protocol['app']}`",
        f"- next goal: `{protocol['next_goal']}`",
        "",
        "## Primary Regimes",
        "",
        "| regime | candidates/ray | accept layer |",
        "|---|---:|---:|",
    ]
    for row in protocol["primary_regimes"]:
        lines.append(f"| `{row['name']}` | {row['candidate_hits_per_ray']} | {row.get('accept_layer')} |")
    lines.extend(["", "## Control Regimes", "", "| regime | candidates/ray | purpose |", "|---|---:|---|"])
    for row in protocol["control_regimes"]:
        lines.append(f"| `{row['name']}` | {row['candidate_hits_per_ray']} | {row['purpose']} |")
    lines.extend(["", "## Pass Conditions", ""])
    for item in protocol["pass_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Kill Conditions", ""])
    for item in protocol["kill_conditions"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "Goal4713 does not authorize POD timing, all-app benchmarking, V4 release, formal high-performance wording, public Tier-3 support, arbitrary callbacks, or raw OptiX callback support.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit V4 Goal4713 custom predicate early-exit protocol.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    payload = validate_v4_goal4713_custom_predicate_early_exit_protocol()
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
