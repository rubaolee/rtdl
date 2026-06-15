from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M9 OptiX grouped-stream partner evidence.")
    parser.add_argument("--point-count", type=int, default=2048)
    parser.add_argument("--radius", type=float, default=1.01)
    parser.add_argument("--component-threshold", type=int, default=1)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--query-block-size", type=int, default=None)
    parser.add_argument("--direct-side-effect", action="store_true")
    parser.add_argument("--hardware", default=None)
    parser.add_argument("--output", type=Path, default=Path("build/goal4403_v3_0_m9_grouped_stream_partner.json"))
    args = parser.parse_args()

    payload = rt.run_v3_m9_grouped_stream_partner_case(
        point_count=args.point_count,
        radius=args.radius,
        component_threshold=args.component_threshold,
        warmups=args.warmups,
        repeats=args.repeats,
        hardware=args.hardware or _hardware_label(),
        grouped_union_query_block_size=args.query_block_size,
        grouped_union_direct_side_effect=args.direct_side_effect,
    )
    validation = rt.validate_v3_m9_grouped_stream_payload(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"validation": validation, "comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _hardware_label() -> str:
    gpu = _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,pci.bus_id",
            "--format=csv,noheader",
        ]
    ).strip()
    if gpu:
        return gpu.splitlines()[0]
    return f"{platform.platform()} / {platform.processor() or platform.machine()}"


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


if __name__ == "__main__":
    raise SystemExit(main())
