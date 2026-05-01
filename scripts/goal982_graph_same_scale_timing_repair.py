#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_graph_analytics_app as graph_app
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact


GOAL = "Goal982 graph same-scale timing repair"
DATE = "2026-04-26"
APP = "graph_analytics"
PATH_NAME = "graph_visibility_edges_gate"
BASELINE_NAME = "embree_graph_ray_bfs_and_triangle_when_available"


def _time(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    return fn(), time.perf_counter() - start


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _expected_summary(copies: int) -> dict[str, Any]:
    return {
        "bfs": {
            "discovered_edge_count": 2 * copies,
            "discovered_vertex_count": 2 * copies,
            "max_level": 1,
        },
        "triangle_count": {
            "touched_vertex_count": 3 * copies,
            "triangle_count": copies,
        },
        "visibility_edges": {
            "blocked_edge_count": 3 * copies,
            "visible_edge_count": copies,
        },
    }


def collect(copies: int = 20000, repeats: int = 3, *, write: bool = False) -> dict[str, Any]:
    samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(repeats):
        payload, sec = _time(
            lambda: graph_app.run_app(
                "embree",
                "all",
                copies=copies,
                output_mode="summary",
            )
        )
        samples.append(sec)
        last_summary = {
            key: section["summary"]
            for key, section in payload["sections"].items()
        }

    expected = _expected_summary(copies)
    parity = last_summary == expected
    row = load_goal835_row(app=APP, path_name=PATH_NAME, baseline_name=BASELINE_NAME)
    artifact = build_baseline_artifact(
        row=row,
        baseline_name=BASELINE_NAME,
        source_backend="embree",
        benchmark_scale={"copies": copies, "iterations": repeats, "scenario": "all"},
        repeated_runs=repeats,
        correctness_parity=parity,
        phase_seconds={
            "native_query": _median(samples),
            "records": float(len(last_summary)),
            "row_digest": 1.0,
            "strict_pass": 1.0 if parity else 0.0,
            "strict_failures": 0.0 if parity else 1.0,
            "status": 1.0 if parity else 0.0,
        },
        summary=last_summary,
        notes=[
            "Same-scale local Embree graph timing baseline for the A5000 graph visibility-edge gate.",
            "This is a conservative non-OptiX baseline: it times the unified Embree graph RT summary path at copies=20000.",
            "It does not authorize public RTX speedup claims.",
        ],
        validation={
            "matches_analytic_expected": parity,
            "expected_summary": expected,
            "samples": samples,
        },
    )
    artifact_path = ROOT / "docs" / "reports" / f"goal835_baseline_{APP}_{PATH_NAME}_{BASELINE_NAME}_2026-04-23.json"
    if write:
        write_baseline_artifact(artifact_path, artifact)

    report = {
        "goal": GOAL,
        "date": DATE,
        "status": "ok" if parity else "blocked",
        "artifact_path": str(artifact_path),
        "wrote_artifact": write,
        "copies": copies,
        "repeats": repeats,
        "phase_seconds": artifact["phase_seconds"],
        "summary": last_summary,
        "expected_summary": expected,
        "public_speedup_claim_authorized": False,
        "claim_effect": (
            "Graph now has a positive same-scale non-OptiX timing baseline; Goal978 can classify it by timing."
            if parity
            else "Graph timing remains blocked because Embree summary does not match analytic expected counts."
        ),
    }
    return {"report": report, "artifact": artifact}


def to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Goal982 Graph Same-Scale Timing Repair",
            "",
            f"Date: {DATE}",
            "",
            "Goal982 repairs the graph timing baseline after Goal981 repaired local Embree graph correctness. It does not authorize public RTX speedup claims.",
            "",
            f"- status: `{report['status']}`",
            f"- copies: `{report['copies']}`",
            f"- repeats: `{report['repeats']}`",
            f"- native query median sec: `{report['phase_seconds']['native_query']}`",
            f"- wrote artifact: `{report['wrote_artifact']}`",
            f"- public speedup authorized: `{report['public_speedup_claim_authorized']}`",
            f"- claim effect: {report['claim_effect']}",
            "",
            "## Summary",
            "",
            "```json",
            json.dumps(report["summary"], indent=2, sort_keys=True),
            "```",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repair graph same-scale Embree timing baseline.")
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output-json", default="docs/reports/goal982_graph_same_scale_timing_repair_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal982_graph_same_scale_timing_repair_2026-04-26.md")
    args = parser.parse_args(argv)

    payload = collect(args.copies, args.repeats, write=args.write)
    report = payload["report"]
    (ROOT / args.output_json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(report) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
