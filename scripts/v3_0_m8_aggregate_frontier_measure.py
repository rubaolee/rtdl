from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M8 aggregate-frontier measured lowering pilot.")
    parser.add_argument("--point-count", type=int, default=512)
    parser.add_argument("--bucket-size", type=int, default=16)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--hardware", default=None)
    parser.add_argument("--output", type=Path, default=Path("build/goal4402_v3_0_m8_aggregate_frontier_lowering.json"))
    args = parser.parse_args()

    hardware = args.hardware or _hardware_label()
    payload = rt.run_v3_m8_aggregate_frontier_lowering_case(
        point_count=args.point_count,
        bucket_size=args.bucket_size,
        theta=args.theta,
        warmups=args.warmups,
        repeats=args.repeats,
        hardware=hardware,
    )
    validation = rt.validate_v3_m8_aggregate_frontier_lowering_payload(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"validation": validation, "comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _hardware_label() -> str:
    return f"{platform.platform()} / {platform.processor() or platform.machine()}"


if __name__ == "__main__":
    raise SystemExit(main())
