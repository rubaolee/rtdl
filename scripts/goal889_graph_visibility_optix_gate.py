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

from examples import rtdl_graph_analytics_app as graph_app


GOAL = "Goal889 graph visibility OptiX gate"
DATE = "2026-04-24"


def _canonical(payload: dict[str, object]) -> dict[str, object]:
    section = payload["sections"]["visibility_edges"]  # type: ignore[index]
    return {
        "row_count": section["row_count"],
        "summary": section["summary"],
        "rows": section.get("rows", ()),
    }


def run_gate(*, copies: int, output_mode: str, strict: bool) -> dict[str, object]:
    if copies < 1:
        raise ValueError("copies must be at least 1")
    if output_mode not in {"rows", "summary"}:
        raise ValueError("output_mode must be rows or summary")

    records: list[dict[str, object]] = []
    start = time.perf_counter()
    cpu_payload = graph_app.run_app("cpu_python_reference", "visibility_edges", copies=copies, output_mode=output_mode)
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
        optix_payload = graph_app.run_app(
            "optix",
            "visibility_edges",
            copies=copies,
            output_mode=output_mode,
            require_rt_core=True,
        )
        records.append(
            {
                "label": "optix_visibility_anyhit",
                "status": "ok",
                "sec": time.perf_counter() - start,
                "digest": _canonical(optix_payload),
            }
        )
    except Exception as exc:  # noqa: BLE001 - optional backend gate records absence.
        records.append(
            {
                "label": "optix_visibility_anyhit",
                "status": "unavailable_or_failed",
                "sec": time.perf_counter() - start,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )

    strict_failures: list[str] = []
    optix = records[1]
    if optix["status"] != "ok":
        strict_failures.append("optix_visibility_anyhit did not run")
    else:
        optix["parity_vs_cpu_python_reference"] = optix["digest"] == records[0]["digest"]
        if not optix["parity_vs_cpu_python_reference"]:
            strict_failures.append("optix_visibility_anyhit failed digest parity")

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
            "claim_scope": "OptiX ray/triangle any-hit traversal for graph visibility-edge filtering",
            "non_claim": "not BFS, triangle-count, shortest-path, graph database, or general graph analytics acceleration",
            "required_phase_groups": ("cpu_python_reference", "optix_visibility_anyhit", "strict_pass", "strict_failures"),
        },
        "boundary": (
            "This gate validates only the graph visibility_edges RT sub-path. "
            "BFS and triangle_count remain host-indexed fallback and are not "
            "promoted by this gate."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the graph visibility OptiX gate.")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-mode", choices=("rows", "summary"), default="summary")
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
