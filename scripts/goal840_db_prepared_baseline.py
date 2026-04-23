#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts import goal756_db_prepared_session_perf as goal756
from scripts.goal839_baseline_artifact_schema import (
    build_baseline_artifact,
    load_goal835_row,
    write_baseline_artifact,
)


GOAL = "Goal840 local prepared DB baseline collector"
DATE = "2026-04-23"
SCENARIOS = ("sales_risk", "regional_dashboard")
BACKENDS = ("cpu", "embree")


def _baseline_name(backend: str) -> str:
    if backend == "cpu":
        return "cpu_oracle_compact_summary"
    if backend == "embree":
        return "embree_compact_summary"
    raise ValueError(f"unsupported backend: {backend}")


def _extract_result(payload: dict[str, Any], backend: str) -> dict[str, Any]:
    for result in payload.get("results", ()):
        if result.get("backend") == backend:
            return result
    raise KeyError(f"backend result not found: {backend}")


def _section(result: dict[str, Any], scenario: str) -> dict[str, Any]:
    return dict(result["prepared_session_output"]["sections"][scenario])


def _summary_fingerprint(section: dict[str, Any]) -> dict[str, Any]:
    summary = dict(section.get("summary") or {})
    summary.pop("risky_order_id_sample", None)
    return {
        "summary": summary,
        "row_counts": section.get("row_counts"),
        "output_mode": section.get("output_mode"),
    }


def _collect_phase_seconds(result: dict[str, Any], scenario: str) -> dict[str, float]:
    prepare = result.get("reported_prepare_phases_sec", {}).get(scenario, {})
    run = result.get("reported_run_phases_sec", {}).get(scenario, {})
    query_and_materialize = sum(
        float(value)
        for key, value in run.items()
        if key.startswith("query_") and key.endswith("_sec")
    )
    if query_and_materialize == 0.0 and "cpu_reference_execute_and_postprocess_sec" in run:
        query_and_materialize = float(run["cpu_reference_execute_and_postprocess_sec"])
    input_build = prepare.get("input_construction_sec")
    if input_build is None:
        input_build = prepare.get("table_construction_sec", 0.0)
    return {
        "input_pack_or_table_build": float(input_build),
        "backend_prepare": float(prepare.get("prepare_sec", 0.0)),
        "native_query": query_and_materialize,
        "copyback_or_materialization": query_and_materialize,
        "python_summary_postprocess": float(run.get("python_summary_postprocess_sec", 0.0)),
    }


def build_db_baseline_artifact(
    *,
    backend: str,
    scenario: str,
    copies: int,
    iterations: int,
) -> dict[str, Any]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")
    if copies <= 0:
        raise ValueError("--copies must be positive")
    if iterations <= 0:
        raise ValueError("--iterations must be positive")

    baseline_name = _baseline_name(backend)
    row = load_goal835_row(
        app="database_analytics",
        path_name=f"prepared_db_session_{scenario}",
        baseline_name=baseline_name,
    )
    target_payload = goal756.run_suite(
        backends=(backend,),
        scenario=scenario,
        copies=copies,
        iterations=iterations,
        output_mode="compact_summary",
        strict=True,
    )
    target_result = _extract_result(target_payload, backend)
    target_section = _section(target_result, scenario)

    if backend == "cpu":
        reference_section = dict(target_result["one_shot_output"]["sections"][scenario])
        parity_note = "CPU oracle artifact validates prepared-session compact summary against the same backend one-shot compact summary."
    else:
        reference_payload = goal756.run_suite(
            backends=("cpu",),
            scenario=scenario,
            copies=copies,
            iterations=iterations,
            output_mode="compact_summary",
            strict=True,
        )
        reference_section = _section(_extract_result(reference_payload, "cpu"), scenario)
        parity_note = "Embree artifact validates against the same-scale CPU prepared-session compact summary."

    correctness_parity = _summary_fingerprint(target_section) == _summary_fingerprint(reference_section)
    validation = {
        "goal": GOAL,
        "date": DATE,
        "scenario": scenario,
        "target_backend": backend,
        "reference_backend": "cpu" if backend == "embree" else "cpu_self_one_shot",
        "target_summary": _summary_fingerprint(target_section),
        "reference_summary": _summary_fingerprint(reference_section),
    }
    notes = [
        parity_note,
        "Goal756 exposes section-level input construction, prepare, query/materialization, and Python summary postprocess timers.",
        "The current public DB profiler does not split native query from copy-back/materialization, so both required phases are represented by the same aggregate query total.",
        "This artifact is same-semantics baseline evidence only and does not authorize any public speedup claim.",
    ]

    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend=backend,
        benchmark_scale={"copies": copies, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=correctness_parity,
        phase_seconds=_collect_phase_seconds(target_result, scenario),
        summary={"scenario": scenario, "prepared_session_section": target_section},
        notes=notes,
        validation=validation,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a Goal836-valid prepared DB baseline artifact.")
    parser.add_argument("--backend", choices=BACKENDS, required=True)
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)

    artifact = build_db_baseline_artifact(
        backend=args.backend,
        scenario=args.scenario,
        copies=args.copies,
        iterations=args.iterations,
    )
    write_baseline_artifact(args.output_json, artifact)
    print(Path(args.output_json).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
