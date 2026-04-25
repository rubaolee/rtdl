#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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


GOAL = "Goal889/905 graph OptiX native traversal gate"
DATE = "2026-04-24"


def _json_default(value: object) -> object:
    if hasattr(value, "_asdict"):
        return value._asdict()  # type: ignore[attr-defined]
    raise TypeError(f"object of type {type(value).__name__} is not JSON serializable")


def _row_digest(rows: object) -> str:
    encoded = json.dumps(rows, sort_keys=True, default=_json_default, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _canonical(payload: dict[str, object], section_name: str, *, include_rows: bool) -> dict[str, object]:
    section = payload["sections"][section_name]  # type: ignore[index]
    rows = section.get("rows", ())  # type: ignore[attr-defined]
    canonical = {
        "row_count": section.get("row_count", len(rows)),  # type: ignore[attr-defined]
        "summary": section["summary"],  # type: ignore[index]
        "row_digest": _row_digest(rows),
    }
    if include_rows:
        canonical["rows"] = rows
    return canonical


def _expected_summary_record(scenario: str, copies: int) -> dict[str, object]:
    if scenario == "visibility_edges":
        digest = {
            "row_count": 4 * copies,
            "summary": {
                "visible_edge_count": copies,
                "blocked_edge_count": 3 * copies,
            },
            "row_digest": _row_digest(()),
        }
    elif scenario == "bfs":
        digest = {
            "row_count": 2 * copies,
            "summary": {
                "discovered_edge_count": 2 * copies,
                "discovered_vertex_count": 2 * copies,
                "max_level": 1,
            },
            "row_digest": _row_digest(()),
        }
    elif scenario == "triangle_count":
        digest = {
            "row_count": copies,
            "summary": {
                "triangle_count": copies,
                "touched_vertex_count": 3 * copies,
            },
            "row_digest": _row_digest(()),
        }
    else:
        raise ValueError(f"unsupported scenario: {scenario}")
    return {
        "label": f"analytic_expected_{scenario}",
        "scenario": scenario,
        "status": "ok",
        "sec": 0.0,
        "digest": digest,
        "validation_mode": "analytic_summary",
    }


def _run_cpu_record(scenario: str, copies: int, include_rows: bool) -> dict[str, object]:
    start = time.perf_counter()
    output_mode = "rows" if include_rows else "summary"
    payload = graph_app.run_app("cpu_python_reference", scenario, copies=copies, output_mode=output_mode)
    return {
        "label": f"cpu_python_reference_{scenario}",
        "scenario": scenario,
        "status": "ok",
        "sec": time.perf_counter() - start,
        "digest": _canonical(payload, scenario, include_rows=include_rows),
    }


def _run_optix_visibility_chunked_record(copies: int, chunk_copies: int, include_rows: bool) -> dict[str, object]:
    if include_rows:
        return _run_optix_record("visibility_edges", copies, include_rows)
    start = time.perf_counter()
    total_visible = 0
    total_blocked = 0
    total_rows = 0
    chunks = 0
    remaining = copies
    try:
        while remaining:
            current = min(chunk_copies, remaining)
            payload = graph_app.run_app(
                "optix",
                "visibility_edges",
                copies=current,
                output_mode="summary",
                require_rt_core=True,
            )
            section = payload["sections"]["visibility_edges"]  # type: ignore[index]
            summary = section["summary"]  # type: ignore[index]
            total_visible += int(summary["visible_edge_count"])  # type: ignore[index]
            total_blocked += int(summary["blocked_edge_count"])  # type: ignore[index]
            total_rows += int(section.get("row_count", 0))  # type: ignore[attr-defined]
            chunks += 1
            remaining -= current
        return {
            "label": "optix_visibility_anyhit",
            "scenario": "visibility_edges",
            "status": "ok",
            "sec": time.perf_counter() - start,
            "digest": {
                "row_count": total_rows,
                "summary": {
                    "visible_edge_count": total_visible,
                    "blocked_edge_count": total_blocked,
                },
                "row_digest": _row_digest(()),
            },
            "optix_graph_mode": "not_applicable",
            "chunk_copies": chunk_copies,
            "chunk_count": chunks,
        }
    except Exception as exc:  # noqa: BLE001 - optional backend gate records absence.
        return {
            "label": "optix_visibility_anyhit",
            "scenario": "visibility_edges",
            "status": "unavailable_or_failed",
            "sec": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "optix_graph_mode": "not_applicable",
            "chunk_copies": chunk_copies,
            "chunk_count": chunks,
        }


def _run_optix_record(scenario: str, copies: int, include_rows: bool) -> dict[str, object]:
    start = time.perf_counter()
    kwargs: dict[str, object] = {}
    label = "optix_visibility_anyhit"
    if scenario in {"bfs", "triangle_count"}:
        kwargs["optix_graph_mode"] = "native"
        label = f"optix_native_graph_ray_{scenario}"
    else:
        kwargs["require_rt_core"] = True
    try:
        output_mode = "rows" if include_rows else "summary"
        payload = graph_app.run_app("optix", scenario, copies=copies, output_mode=output_mode, **kwargs)
        return {
            "label": label,
            "scenario": scenario,
            "status": "ok",
            "sec": time.perf_counter() - start,
            "digest": _canonical(payload, scenario, include_rows=include_rows),
            "optix_graph_mode": kwargs.get("optix_graph_mode", "not_applicable"),
        }
    except Exception as exc:  # noqa: BLE001 - optional backend gate records absence.
        return {
            "label": label,
            "scenario": scenario,
            "status": "unavailable_or_failed",
            "sec": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "optix_graph_mode": kwargs.get("optix_graph_mode", "not_applicable"),
        }


def run_gate(
    *,
    copies: int,
    output_mode: str,
    strict: bool,
    validation_mode: str = "analytic_summary",
    chunk_copies: int = 100,
) -> dict[str, object]:
    if copies < 1:
        raise ValueError("copies must be at least 1")
    if output_mode not in {"rows", "summary"}:
        raise ValueError("output_mode must be rows or summary")
    if validation_mode not in {"analytic_summary", "full_reference", "none"}:
        raise ValueError("validation_mode must be analytic_summary, full_reference, or none")
    if output_mode == "rows" and validation_mode == "analytic_summary":
        raise ValueError("analytic_summary validation is only valid with summary output")
    if chunk_copies < 1:
        raise ValueError("chunk_copies must be at least 1")

    records: list[dict[str, object]] = []
    include_rows = output_mode == "rows"
    scenarios = ("visibility_edges", "bfs", "triangle_count")
    reference_by_scenario: dict[str, dict[str, object]] = {}

    records.append(_run_optix_visibility_chunked_record(copies, chunk_copies, include_rows))
    for scenario in ("bfs", "triangle_count"):
        records.append(_run_optix_record(scenario, copies, include_rows))

    if validation_mode == "full_reference":
        for scenario in scenarios:
            record = _run_cpu_record(scenario, copies, include_rows)
            records.append(record)
            reference_by_scenario[scenario] = record
    elif validation_mode == "analytic_summary":
        for scenario in scenarios:
            record = _expected_summary_record(scenario, copies)
            records.append(record)
            reference_by_scenario[scenario] = record

    strict_failures: list[str] = []
    if strict and validation_mode == "none":
        strict_failures.append("strict mode requires analytic_summary or full_reference validation")
    for record in records:
        if not str(record["label"]).startswith("optix_"):
            continue
        scenario = str(record["scenario"])
        if record["status"] != "ok":
            strict_failures.append(f"{record['label']} did not run")
            continue
        if scenario in reference_by_scenario:
            parity_key = (
                "parity_vs_cpu_python_reference"
                if validation_mode == "full_reference"
                else "parity_vs_analytic_expected"
            )
            record[parity_key] = record["digest"] == reference_by_scenario[scenario]["digest"]
            if not record[parity_key]:
                strict_failures.append(f"{record['label']} failed {validation_mode} parity")

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
        "chunk_copies": chunk_copies,
        "validation_mode": validation_mode,
        "output_mode": output_mode,
        "records": records,
        "strict": strict,
        "strict_failures": strict_failures,
        "strict_pass": not strict_failures,
        "status": "pass" if not strict_failures else ("fail" if strict else "non_strict_recorded_gaps"),
        "cloud_claim_contract": {
            "claim_scope": (
                "OptiX ray/triangle any-hit traversal for graph visibility-edge filtering, "
                "plus explicit native OptiX graph-ray traversal candidate generation for BFS and triangle-count"
            ),
            "non_claim": (
                "not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration; "
                "BFS visited/frontier bookkeeping and triangle set-intersection remain outside RT traversal"
            ),
            "required_phase_groups": (
                "cpu_python_reference_visibility_edges",
                "cpu_python_reference_bfs",
                "cpu_python_reference_triangle_count",
                "analytic_expected_visibility_edges",
                "analytic_expected_bfs",
                "analytic_expected_triangle_count",
                "optix_visibility_anyhit",
                "optix_native_graph_ray_bfs",
                "optix_native_graph_ray_triangle_count",
                "strict_pass",
                "strict_failures",
            ),
        },
        "boundary": (
            "This gate validates bounded graph RT sub-paths only. Visibility uses "
            "ray/triangle any-hit and is chunked in summary mode to avoid the "
            "global observer-target cross-product. BFS and triangle-count use "
            "explicit native OptiX graph-ray mode for candidate generation, while "
            "higher-level graph state management remains app/Python-owned."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the graph visibility OptiX gate.")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-mode", choices=("rows", "summary"), default="summary")
    parser.add_argument(
        "--validation-mode",
        choices=("analytic_summary", "full_reference", "none"),
        default="analytic_summary",
        help="Use analytic fixture summaries by default so cloud timing reaches OptiX before CPU reference work.",
    )
    parser.add_argument("--chunk-copies", type=int, default=100)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_gate(
        copies=args.copies,
        output_mode=args.output_mode,
        strict=args.strict,
        validation_mode=args.validation_mode,
        chunk_copies=args.chunk_copies,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "status": payload["status"], "strict_pass": payload["strict_pass"]}, sort_keys=True))
    return 1 if args.strict and not payload["strict_pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
