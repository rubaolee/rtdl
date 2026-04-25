#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _command_plan(*, copies: int, graph_chunk_copies: int, jaccard_chunk_copies: tuple[int, ...]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = [
        {
            "label": "graph_visibility_edges_gate",
            "required": True,
            "command": [
                sys.executable,
                "scripts/goal889_graph_visibility_optix_gate.py",
                "--copies",
                str(copies),
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                str(graph_chunk_copies),
                "--strict",
                "--output-json",
                "docs/reports/goal914_graph_visibility_optix_gate_rtx.json",
            ],
        },
    ]
    for chunk_copies in jaccard_chunk_copies:
        commands.append(
            {
                "label": f"jaccard_chunk_{chunk_copies}",
                "required": chunk_copies == jaccard_chunk_copies[0],
                "command": [
                    sys.executable,
                    "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                    "--app",
                    "jaccard",
                    "--mode",
                    "optix",
                    "--copies",
                    str(copies),
                    "--output-mode",
                    "summary",
                    "--validation-mode",
                    "analytic_summary",
                    "--chunk-copies",
                    str(chunk_copies),
                    "--output-json",
                    f"docs/reports/goal914_jaccard_chunk_{chunk_copies}_rtx.json",
                ],
            }
        )
    return commands


def run_driver(
    *,
    mode: str,
    copies: int,
    graph_chunk_copies: int,
    jaccard_chunk_copies: tuple[int, ...],
    output_json: Path,
) -> dict[str, Any]:
    if mode not in {"dry-run", "run"}:
        raise ValueError("mode must be dry-run or run")
    if copies < 1:
        raise ValueError("copies must be positive")
    if graph_chunk_copies < 1:
        raise ValueError("graph_chunk_copies must be positive")
    if not jaccard_chunk_copies or any(chunk < 1 for chunk in jaccard_chunk_copies):
        raise ValueError("jaccard_chunk_copies must contain positive values")

    plan = _command_plan(
        copies=copies,
        graph_chunk_copies=graph_chunk_copies,
        jaccard_chunk_copies=jaccard_chunk_copies,
    )
    results: list[dict[str, Any]] = []
    for item in plan:
        if mode == "dry-run":
            results.append(
                {
                    "label": item["label"],
                    "required": item["required"],
                    "status": "planned",
                    "returncode": None,
                    "command": item["command"],
                }
            )
            continue
        completed = subprocess.run(
            item["command"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        results.append(
            {
                "label": item["label"],
                "required": item["required"],
                "status": "pass" if completed.returncode == 0 else "fail",
                "returncode": completed.returncode,
                "command": item["command"],
                "stdout_tail": completed.stdout[-2000:],
                "stderr_tail": completed.stderr[-2000:],
            }
        )
        if completed.returncode != 0 and item["required"] and item["label"] != "jaccard_chunk_100":
            break

    required_failures = [
        result["label"]
        for result in results
        if result["required"] and result["status"] == "fail"
    ]
    payload = {
        "goal": "Goal914 targeted RTX graph/Jaccard rerun driver",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "copies": copies,
        "graph_chunk_copies": graph_chunk_copies,
        "jaccard_chunk_copies": list(jaccard_chunk_copies),
        "results": results,
        "required_failures": required_failures,
        "status": "pass" if not required_failures else "fail",
        "boundary": (
            "Targeted post-Goal913 cloud rerun helper only. This driver does not "
            "authorize RTX speedup claims and intentionally avoids the full cloud suite."
        ),
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run only the post-Goal913 RTX graph/Jaccard gates.")
    parser.add_argument("--mode", choices=("dry-run", "run"), default="dry-run")
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--graph-chunk-copies", type=int, default=100)
    parser.add_argument(
        "--jaccard-chunk-copies",
        default="100,50,20",
        help="comma-separated Jaccard chunk sizes; first value is the required production rerun",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("docs/reports/goal914_rtx_targeted_graph_jaccard_rerun.json"),
    )
    args = parser.parse_args(argv)
    chunks = tuple(int(part.strip()) for part in args.jaccard_chunk_copies.split(",") if part.strip())
    payload = run_driver(
        mode=args.mode,
        copies=args.copies,
        graph_chunk_copies=args.graph_chunk_copies,
        jaccard_chunk_copies=chunks,
        output_json=args.output_json,
    )
    print(json.dumps({"output_json": str(args.output_json), "status": payload["status"]}, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
