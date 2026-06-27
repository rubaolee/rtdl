from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4692_tier3_support_decision import validate_v4_goal4692_tier3_support_decision


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    decision = payload["decision"]
    lines = [
        "# V4 Goal4692 Tier-3 Support Decision",
        "",
        "Status: direct-callable overhead is yellow; public Tier-3 support is not authorized",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- measured direct-callable ratio: `{decision['measured_direct_callable_ratio']}`",
        f"- selected next track: `{decision['selected_next_track']}`",
        "",
        "## Decision",
        "",
        str(decision["decision"]),
        "",
        "## Meaning",
        "",
        "The OptiX SBT direct-callable ABI is runnable and correct, but the measured `1.67x` overhead is too high for support. The next useful Tier-3 path is module-specialized direct device callback composition: compile the user's Numba callback into the generated OptiX module and call it directly from a hit-program-shaped wrapper.",
        "",
        "## Non-Authorization",
        "",
        "- no public Tier-3 support",
        "- no arbitrary callback support",
        "- no direct-callable performance claim",
        "- no V4 release authorization",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V4 Goal4692 Tier-3 support decision.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4692_tier3_support_decision()
    payload = {"schema": "rtdl.v4.goal4692_tier3_support_decision.v1", "validation_status": validation["status"], **validation}
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
