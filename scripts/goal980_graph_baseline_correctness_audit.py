#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_graph_analytics_app as graph_app


GOAL = "Goal980 graph baseline correctness audit"
DATE = "2026-04-26"


def _section_digest(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "row_count": section["row_count"],
            "summary": section["summary"],
        }
        for key, section in payload["sections"].items()
    }


def _run(backend: str, scenario: str, copies: int) -> tuple[dict[str, Any], float]:
    start = time.perf_counter()
    payload = graph_app.run_app(backend, scenario, copies=copies, output_mode="summary")
    return payload, time.perf_counter() - start


def audit(copies_list: tuple[int, ...] = (1, 2, 8, 16, 256)) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for copies in copies_list:
        cpu_payload, cpu_sec = _run("cpu_python_reference", "all", copies)
        embree_payload, embree_sec = _run("embree", "all", copies)
        cpu_digest = _section_digest(cpu_payload)
        embree_digest = _section_digest(embree_payload)
        mismatches: dict[str, dict[str, Any]] = {}
        for section in ("bfs", "triangle_count", "visibility_edges"):
            if cpu_digest[section] != embree_digest[section]:
                mismatches[section] = {
                    "cpu": cpu_digest[section],
                    "embree": embree_digest[section],
                }
        rows.append(
            {
                "copies": copies,
                "cpu_sec": cpu_sec,
                "embree_sec": embree_sec,
                "status": "ok" if not mismatches else "mismatch",
                "mismatches": mismatches,
            }
        )

    mismatch_rows = [row for row in rows if row["status"] != "ok"]
    return {
        "goal": GOAL,
        "date": DATE,
        "status": "blocked" if mismatch_rows else "ok",
        "rows": rows,
        "mismatch_count": len(mismatch_rows),
        "public_speedup_claim_authorized": False,
        "claim_effect": (
            "graph_analytics must remain excluded from public RTX/Embree speedup claims "
            "until graph native correctness is repaired and same-scale baseline timings are recollected"
            if mismatch_rows
            else "graph local correctness check passed; timing review is still separate"
        ),
        "boundary": (
            "Goal980 audits local graph baseline correctness only. It does not repair native graph kernels, "
            "collect cloud data, or authorize public speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal980 Graph Baseline Correctness Audit",
        "",
        f"Date: {DATE}",
        "",
        payload["boundary"],
        "",
        f"- status: `{payload['status']}`",
        f"- mismatch rows: `{payload['mismatch_count']}`",
        f"- public speedup authorized: `{payload['public_speedup_claim_authorized']}`",
        f"- claim effect: {payload['claim_effect']}",
        "",
        "| Copies | CPU sec | Embree sec | Status | Mismatched sections |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        sections = ", ".join(row["mismatches"].keys())
        lines.append(
            f"| {row['copies']} | {row['cpu_sec']:.6f} | {row['embree_sec']:.6f} | "
            f"`{row['status']}` | {sections} |"
        )
    lines.extend(["", "## Mismatch Detail", ""])
    for row in payload["rows"]:
        if not row["mismatches"]:
            continue
        lines.append(f"### copies={row['copies']}")
        lines.append("")
        for section, detail in row["mismatches"].items():
            lines.append(f"- `{section}` CPU: `{detail['cpu']}`")
            lines.append(f"- `{section}` Embree: `{detail['embree']}`")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit graph CPU/Embree baseline correctness.")
    parser.add_argument("--copies", type=int, action="append", help="copy scale to test; repeatable")
    parser.add_argument("--output-json", default="docs/reports/goal980_graph_baseline_correctness_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal980_graph_baseline_correctness_audit_2026-04-26.md")
    args = parser.parse_args(argv)

    copies = tuple(args.copies) if args.copies else (1, 2, 8, 16, 256)
    payload = audit(copies)
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
