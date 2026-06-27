from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4710_custom_scored_app_protocol import validate_v4_goal4710_custom_scored_app_protocol


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    protocol = payload["protocol"]
    lines = [
        "# V4 Goal4710 Custom Scored App Protocol",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- status: `{protocol['status']}`",
        f"- app: `{protocol['app']}`",
        f"- next goal: `{protocol['next_goal']}`",
        f"- POD authorized for next goal: `{protocol['pod_authorized_for_next_goal']}`",
        "",
        "## Callbacks",
        "",
        f"- primary: {', '.join(protocol['primary_callbacks'])}",
        f"- control: {', '.join(protocol['control_callbacks'])}",
        "",
        "## Baselines",
        "",
    ]
    for row in protocol["baselines"]:
        lines.append(f"- `{row['name']}` at `{row['root']}`: {row['required_discovery']}")
    lines.extend(["", "## Pass Conditions", ""])
    for item in protocol["pass_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Kill Conditions", ""])
    for item in protocol["kill_conditions"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Goal4710 authorizes only the next focused POD benchmark under this protocol. It does not authorize app-level speed claims, release wording, public Tier-3 support, or all-app benchmarking.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V4 Goal4710 custom scored app protocol evidence.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    validation = validate_v4_goal4710_custom_scored_app_protocol()
    payload = {
        "schema": "rtdl.v4.goal4710_custom_scored_app_protocol.v1",
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
