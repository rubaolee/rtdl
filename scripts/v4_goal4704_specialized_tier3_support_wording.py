from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4704_specialized_tier3_support_wording import (
    validate_v4_goal4704_specialized_tier3_support_wording,
)


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    gate = payload["gate"]
    lines = [
        "# V4 Goal4704 Specialized Tier-3 Support Wording Gate",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- status: `{gate['status']}`",
        f"- candidate label: `{gate['candidate_label']}`",
        f"- public support authorized: `{gate['tier3_public_support_authorized']}`",
        "",
        "## Allowed Internal Wording",
        "",
    ]
    for item in gate["allowed_internal_wording"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Prohibited Public Wording", ""])
    for item in gate["prohibited_public_wording"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Remaining Public-Support Gates", ""])
    for item in gate["remaining_public_support_gates"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate does not authorize public Tier-3 support, release wording, arbitrary callbacks, raw OptiX callbacks, or performance claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V4 Goal4704 specialized Tier-3 support wording gate evidence.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4704_specialized_tier3_support_wording()
    payload = {
        "schema": "rtdl.v4.goal4704_specialized_tier3_support_wording.v1",
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
