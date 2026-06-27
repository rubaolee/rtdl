from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4701_specialized_tier3_support_candidate import validate_v4_goal4701_specialized_tier3_support_candidate


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    candidate = payload["candidate"]
    lines = [
        "# V4 Goal4701 Specialized Tier-3 Support Candidate",
        "",
        "Status: support-candidate packet, not public support",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- candidate label: `{candidate['candidate_label']}`",
        f"- next goal: `{candidate['next_goal']}`",
        "",
        "## Candidate Scope",
        "",
        str(candidate["candidate_scope"]),
        "",
        "## Evidence Chain",
        "",
    ]
    for item in candidate["evidence_chain"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Satisfied Gates", ""])
    for item in candidate["satisfied_gates"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Missing Before Public Support", ""])
    for item in candidate["missing_before_public_support"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This packet does not authorize public Tier-3 support, arbitrary callback support, raw OptiX callbacks, broad speedup claims, whole-app speedup claims, or V4 release wording.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V4 Goal4701 specialized Tier-3 support candidate packet.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4701_specialized_tier3_support_candidate()
    payload = {"schema": "rtdl.v4.goal4701_specialized_tier3_support_candidate.v1", "validation_status": validation["status"], **validation}
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
