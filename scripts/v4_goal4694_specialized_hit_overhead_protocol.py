from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4694_specialized_hit_overhead_protocol import validate_v4_goal4694_specialized_hit_overhead_protocol


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    protocol = payload["protocol"]
    lines = [
        "# V4 Goal4694 Specialized Hit Callback Overhead Protocol",
        "",
        "Status: protocol frozen, no timing claim and no Tier-3 support authorization",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- primary ratio: `{protocol['primary_ratio']}`",
        f"- trace iterations: `{protocol['trace_iterations']}`",
        f"- warmup launches: `{protocol['warmup_launches']}`",
        f"- measured launches: `{protocol['measured_launches']}`",
        f"- pass ratio max: `{protocol['pass_ratio_max']}`",
        f"- hard kill ratio min: `{protocol['hard_kill_ratio_min']}`",
        f"- baseline: `{protocol['baseline_variant']}`",
        f"- measured: `{protocol['measured_variant']}`",
        "",
        "## Boundary",
        "",
        "This protocol measures the specialized hit-program callback shape selected after Goal4693. It does not authorize performance claims or public Tier-3 support.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze V4 Goal4694 specialized hit-callback overhead protocol.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4694_specialized_hit_overhead_protocol()
    payload = {"schema": "rtdl.v4.goal4694_specialized_hit_overhead_protocol.v1", "validation_status": validation["status"], **validation}
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
