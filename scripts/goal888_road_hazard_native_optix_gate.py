#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_road_hazard_screening as road_app


GOAL = "Goal888 road hazard native OptiX gate"
DATE = "2026-04-24"


def _canonical(payload: dict[str, object]) -> dict[str, object]:
    keep = {
        "row_count",
        "priority_segments",
        "priority_segment_count",
        "rows",
    }
    return {key: payload[key] for key in sorted(keep) if key in payload}


def _run_cpu(copies: int, output_mode: str) -> dict[str, object]:
    return road_app.run_case("cpu_python_reference", copies=copies, output_mode=output_mode)


def _run_optix_native(copies: int, output_mode: str) -> dict[str, object]:
    return road_app.run_case("optix", copies=copies, output_mode=output_mode, optix_mode="native")


def run_gate(*, copies: int, output_mode: str, strict: bool) -> dict[str, object]:
    if copies < 1:
        raise ValueError("copies must be at least 1")
    if output_mode not in {"rows", "priority_segments", "summary"}:
        raise ValueError("output_mode must be rows, priority_segments, or summary")

    records: list[dict[str, object]] = []
    start = time.perf_counter()
    cpu_payload = _run_cpu(copies, output_mode)
    records.append(
        {
            "label": "cpu_python_reference",
            "status": "ok",
            "sec": time.perf_counter() - start,
            "digest": _canonical(cpu_payload),
        }
    )

    start = time.perf_counter()
    try:
        optix_payload = _run_optix_native(copies, output_mode)
        records.append(
            {
                "label": "optix_native",
                "status": "ok",
                "sec": time.perf_counter() - start,
                "digest": _canonical(optix_payload),
            }
        )
    except Exception as exc:  # noqa: BLE001 - optional backend gate records absence.
        records.append(
            {
                "label": "optix_native",
                "status": "unavailable_or_failed",
                "sec": time.perf_counter() - start,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )

    strict_failures: list[str] = []
    native = records[1]
    if native["status"] != "ok":
        strict_failures.append("optix_native did not run")
    else:
        native["parity_vs_cpu_python_reference"] = native["digest"] == records[0]["digest"]
        if not native["parity_vs_cpu_python_reference"]:
            strict_failures.append("optix_native failed digest parity")

    return {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "copies": copies,
        "output_mode": output_mode,
        "records": records,
        "strict": strict,
        "strict_failures": strict_failures,
        "strict_pass": not strict_failures,
        "status": "pass" if not strict_failures else ("fail" if strict else "non_strict_recorded_gaps"),
        "cloud_claim_contract": {
            "claim_scope": "native OptiX segment/polygon hit-count traversal for compact road-hazard summaries",
            "non_claim": "not default road-hazard public speedup and not a full GIS routing or risk model claim",
            "required_phase_groups": ("cpu_python_reference", "optix_native", "strict_pass", "strict_failures"),
        },
        "boundary": (
            "This gate validates the road-hazard app through the explicit native "
            "segment/polygon OptiX mode. It does not promote the default app path "
            "or authorize a public RTX speedup claim by itself."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the road-hazard native OptiX gate.")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-mode", choices=("rows", "priority_segments", "summary"), default="summary")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_gate(copies=args.copies, output_mode=args.output_mode, strict=args.strict)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "status": payload["status"], "strict_pass": payload["strict_pass"]}, sort_keys=True))
    return 1 if args.strict and not payload["strict_pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
