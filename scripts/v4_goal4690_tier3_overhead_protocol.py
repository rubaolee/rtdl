from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4690_tier3_overhead_protocol import validate_v4_goal4690_tier3_overhead_protocol


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    protocol = payload["protocol"]
    lines = [
        "# V4 Goal4690 Tier-3 Callback Overhead Protocol",
        "",
        "Status: protocol frozen, no timing claim and no Tier-3 support authorization",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- callback shape: `{protocol['callback_shape']}`",
        f"- primary ratio: `{protocol['primary_ratio']}`",
        f"- inner iterations: `{protocol['inner_iterations']}`",
        f"- warmup launches: `{protocol['warmup_launches']}`",
        f"- measured launches: `{protocol['measured_launches']}`",
        f"- pass ratio max: `{protocol['pass_ratio_max']}`",
        f"- hard kill ratio min: `{protocol['hard_kill_ratio_min']}`",
        "",
        "## Baselines",
        "",
        "- `direct_device_function_loop_same_numba_callback`: primary denominator.",
        "- `inline_formula_loop_context_only`: context-only lower bound, not the release denominator.",
        "",
        "## Measured Variant",
        "",
        "- `optix_direct_callable_loop_same_numba_callback`: primary measured path.",
        "",
        "## Boundary",
        "",
        "This protocol does not authorize performance claims. Goal4691 must run the POD measurement and keep release/support flags false.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze V4 Goal4690 Tier-3 callback overhead protocol.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4690_tier3_overhead_protocol()
    payload = {"schema": "rtdl.v4.goal4690_tier3_overhead_protocol.v1", "validation_status": validation["status"], **validation}
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
