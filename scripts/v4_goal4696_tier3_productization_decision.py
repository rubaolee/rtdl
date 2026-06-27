from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4696_tier3_productization_decision import validate_v4_goal4696_tier3_productization_decision


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    decision = payload["decision"]
    lines = [
        "# V4 Goal4696 Tier-3 Productization Decision",
        "",
        "Status: constrained productization candidate, not public Tier-3 support",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- productization candidate: `{decision['productization_candidate']}`",
        f"- supported callback shape: `{decision['supported_callback_shape']}`",
        f"- SBT direct callable status: `{decision['sbt_direct_callable_status']}`",
        "",
        "## Decision",
        "",
        str(decision["decision"]),
        "",
        "## Rejected Shapes",
        "",
    ]
    for item in decision["rejected_callback_shapes"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Before Public Support", ""])
    for item in decision["required_before_public_support"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", "This is not public Tier-3 support, not a release authorization, and not an app-level performance claim.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V4 Goal4696 Tier-3 productization decision.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4696_tier3_productization_decision()
    payload = {"schema": "rtdl.v4.goal4696_tier3_productization_decision.v1", "validation_status": validation["status"], **validation}
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
