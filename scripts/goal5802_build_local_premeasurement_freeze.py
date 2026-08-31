#!/usr/bin/env python3
"""Create the Goal5802 local-only premeasurement freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5802_premeasurement.contract import build_freeze


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--product-binding", type=Path, required=True)
    parser.add_argument("--engineering-effort-ledger", type=Path, required=True)
    parser.add_argument("--successor-forecast", type=Path, required=True)
    parser.add_argument("--postresult-instrument-repair", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    binding = json.loads(args.product_binding.read_text(encoding="utf-8"))
    if not isinstance(binding, dict):
        raise RuntimeError("Goal5802 product binding root is not an object")
    engineering = json.loads(
        args.engineering_effort_ledger.read_text(encoding="utf-8"))
    if not isinstance(engineering, dict):
        raise RuntimeError("Goal5802 engineering ledger root is not an object")
    forecast = json.loads(args.successor_forecast.read_text(encoding="utf-8"))
    if not isinstance(forecast, dict):
        raise RuntimeError("Goal5802 successor forecast root is not an object")
    repair = None
    if args.postresult_instrument_repair is not None:
        repair = json.loads(args.postresult_instrument_repair.read_text(
            encoding="utf-8"))
        if not isinstance(repair, dict):
            raise RuntimeError("Goal5802 postresult repair root is not an object")
    freeze = build_freeze(
        args.root, binding, engineering, forecast,
        postresult_instrument_repair=repair)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(freeze, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": freeze["status"],
        "freeze_sha256": freeze["freeze_sha256"],
        "worker_row_count": freeze["worker_row_count"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
