from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4697_specialized_tier3_api_contract import validate_v4_goal4697_specialized_tier3_api_contract


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    contract = payload["contract"]
    plans = payload["plans"]
    lines = [
        "# V4 Goal4697 Specialized Tier-3 API Contract",
        "",
        "Status: constrained API contract scaffold, not public Tier-3 support",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- candidate surface: `{contract['candidate_surface']}`",
        f"- supported callback shape: `{contract['supported_callback_shape']}`",
        f"- wrapper strategy: `{contract['wrapper_strategy']}`",
        "",
        "## Accepted Contract",
        "",
        f"- language: `{contract['callback_language']}`",
        f"- compiler contract: `{contract['compiler_contract']}`",
        f"- signature: {contract['accepted_signature']}",
        "",
        "Accepted callback shapes:",
        "",
    ]
    for item in contract["accepted_callback_shapes"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Validation Matrix", ""])
    for name, plan in plans.items():
        lines.append(f"- `{name}`: `{plan['status']}` (accepted: `{plan['accepted']}`)")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This contract allows internal productization work only. It is not public Tier-3 support, not raw OptiX callback support, not a release authorization, and not an app-level performance claim.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V4 Goal4697 specialized Tier-3 API contract.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4697_specialized_tier3_api_contract()
    payload = {"schema": "rtdl.v4.goal4697_specialized_tier3_api_contract.v1", "validation_status": validation["status"], **validation}
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
