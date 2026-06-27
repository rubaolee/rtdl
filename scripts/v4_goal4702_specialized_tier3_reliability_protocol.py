from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4702_specialized_tier3_reliability_protocol import validate_v4_goal4702_specialized_tier3_reliability_protocol


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    protocol = payload["protocol"]
    lines = [
        "# V4 Goal4702 Specialized Tier-3 Reliability Matrix Protocol",
        "",
        "Status: frozen protocol, not run",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- total attempts: `{protocol['total_attempts']}`",
        f"- attempts per variant: `{protocol['attempts_per_variant']}`",
        f"- success floor: `{protocol['compile_link_launch_success_floor']}`",
        f"- next goal: `{protocol['next_goal']}`",
        "",
        "## Callback Variants",
        "",
    ]
    for item in protocol["callback_variants"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Datasets", ""])
    for item in protocol["datasets"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Requirements",
            "",
            f"- correctness: {protocol['correctness_requirement']}",
            f"- cache: {protocol['cache_requirement']}",
            f"- failures: {protocol['failure_classification_requirement']}",
            "",
            "## Boundary",
            "",
            "This protocol authorizes only Goal4703 reliability execution. It does not authorize public Tier-3 support, arbitrary callback support, raw OptiX callbacks, release wording, or performance claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze V4 Goal4702 specialized Tier-3 reliability matrix protocol.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4702_specialized_tier3_reliability_protocol()
    payload = {"schema": "rtdl.v4.goal4702_specialized_tier3_reliability_protocol.v1", "validation_status": validation["status"], **validation}
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
