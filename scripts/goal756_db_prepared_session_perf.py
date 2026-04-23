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

from examples import rtdl_database_analytics_app as db_app


BACKENDS = ("cpu", "cpu_reference", "cpu_python_reference", "embree", "optix", "vulkan")


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _compact(payload: dict[str, Any]) -> dict[str, Any]:
    def compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
        compacted = dict(summary)
        risky_ids = compacted.pop("risky_order_ids", None)
        if isinstance(risky_ids, list):
            compacted["risky_order_count"] = len(risky_ids)
            compacted["risky_order_id_sample"] = risky_ids[:10]
        return compacted

    compact = {
        key: value
        for key, value in payload.items()
        if key not in {"sections"}
    }
    if isinstance(compact.get("summary"), dict):
        compact["summary"] = compact_summary(compact["summary"])
    sections = {}
    for name, section in payload.get("sections", {}).items():
        sections[name] = {
            key: value
            for key, value in section.items()
            if key not in {"results", "rows"}
        }
        if isinstance(sections[name].get("summary"), dict):
            sections[name]["summary"] = compact_summary(sections[name]["summary"])
    compact["sections"] = sections
    return compact


def _reported_session_phases(payload: dict[str, Any]) -> dict[str, Any]:
    phases: dict[str, Any] = {}
    session = payload.get("prepared_session")
    if isinstance(session, dict):
        phases["unified_session"] = dict(session)
    for name, section in payload.get("sections", {}).items():
        if isinstance(section, dict) and isinstance(section.get("session"), dict):
            phases[name] = dict(section["session"])
    return phases


def _profile_backend(
    backend: str,
    *,
    scenario: str,
    copies: int,
    iterations: int,
) -> dict[str, Any]:
    one_shot_payload, one_shot_sec = _time_call(
        lambda: db_app.run_app(backend, scenario=scenario, copies=copies, output_mode="summary")
    )

    session, prepare_total_sec = _time_call(lambda: db_app.prepare_session(backend, scenario=scenario, copies=copies))
    run_samples: list[float] = []
    last_payload: dict[str, Any] | None = None
    close_sec = 0.0
    try:
        for _ in range(iterations):
            last_payload, elapsed = _time_call(lambda: session.run(output_mode="summary"))
            run_samples.append(elapsed)
    finally:
        _, close_sec = _time_call(session.close)

    return {
        "backend": backend,
        "status": "ok",
        "one_shot_total_sec": one_shot_sec,
        "prepared_session_prepare_total_sec": prepare_total_sec,
        "prepared_session_warm_query_sec": _stats(run_samples),
        "prepared_session_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": (
            one_shot_sec / statistics.median(run_samples) if run_samples and statistics.median(run_samples) > 0.0 else 0.0
        ),
        "reported_prepare_phases_sec": _reported_session_phases(last_payload or {}),
        "phase_contract": {
            "one_shot_total": "complete public app call including fixture construction, backend selection, native prepare, query, materialization, and summary postprocess",
            "prepared_session_prepare_total": "public app prepare_session call including fixture construction and native prepared dataset creation where available",
            "prepared_session_warm_query": "session.run only: prepared queries plus result materialization and app summary construction",
            "reported_prepare_phases": "scenario-provided construction/selection/prepare timers embedded in app JSON",
            "not_yet_split": "native DB launch/traversal, candidate copy-back, exact filtering/grouping, and Python materialization are still grouped inside session.run unless a backend exposes lower-level timers",
        },
        "one_shot_output": _compact(one_shot_payload),
        "prepared_session_output": _compact(last_payload or {}),
    }


def run_suite(
    *,
    backends: tuple[str, ...],
    scenario: str,
    copies: int,
    iterations: int,
    strict: bool,
) -> dict[str, Any]:
    if copies <= 0:
        raise ValueError("--copies must be positive")
    if iterations <= 0:
        raise ValueError("--iterations must be positive")

    results: list[dict[str, Any]] = []
    for backend in backends:
        try:
            results.append(_profile_backend(backend, scenario=scenario, copies=copies, iterations=iterations))
        except Exception as exc:
            if strict:
                raise
            results.append({"backend": backend, "status": "skipped_or_failed", "error": str(exc)})

    return {
        "suite": "goal756_db_prepared_session_perf",
        "scenario": scenario,
        "copies": copies,
        "iterations": iterations,
        "results": results,
        "boundary": "Prepared DB session profiler compares one-shot app calls with reused prepared sessions. GTX 1070 evidence is backend behavior evidence only, not RTX RT-core speedup evidence.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal756 DB prepared-session performance profiler.")
    parser.add_argument("--backend", action="append", choices=BACKENDS)
    parser.add_argument("--scenario", choices=("regional_dashboard", "sales_risk", "all"), default="all")
    parser.add_argument("--copies", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)

    payload = run_suite(
        backends=tuple(args.backend) if args.backend else ("cpu", "embree", "optix", "vulkan"),
        scenario=args.scenario,
        copies=args.copies,
        iterations=args.iterations,
        strict=args.strict,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
