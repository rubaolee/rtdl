from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4699_specialized_tier3_app_route_protocol import validate_v4_goal4699_specialized_tier3_app_route_protocol


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    protocol = payload["protocol"]
    lines = [
        "# V4 Goal4699 Specialized Tier-3 App-Route Validation Protocol",
        "",
        "Status: frozen protocol, not run",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- selected route: `{protocol['selected_route']}`",
        f"- selected surface: `{protocol['selected_surface']}`",
        f"- next goal: `{protocol['next_goal']}`",
        "",
        "## Denominators",
        "",
        f"- correctness: {protocol['correctness_denominator']}",
        f"- primary performance: {protocol['primary_performance_denominator']}",
        f"- context: {protocol['context_denominator']}",
        "",
        "## Frozen Parameters",
        "",
        f"- ray counts: `{protocol['ray_counts']}`",
        f"- warmup: `{protocol['warmup']}`",
        f"- repeat: `{protocol['repeat']}`",
        f"- callback/Tier-2 pass ratio max: `{protocol['callback_over_tier2_pass_ratio_max']}x`",
        f"- callback/Tier-2 hard kill ratio: `>{protocol['callback_over_tier2_hard_kill_ratio']}x`",
        f"- callback/context speedup min: `{protocol['callback_over_context_speedup_min']}x`",
        "",
        "## Required Telemetry",
        "",
    ]
    for item in protocol["required_telemetry"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This protocol does not authorize public Tier-3 support, app-level speed claims, or V4 release wording. It only authorizes Goal4700 to run the frozen POD app-route validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze V4 Goal4699 specialized Tier-3 app-route validation protocol.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4699_specialized_tier3_app_route_protocol()
    payload = {"schema": "rtdl.v4.goal4699_specialized_tier3_app_route_protocol.v1", "validation_status": validation["status"], **validation}
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
