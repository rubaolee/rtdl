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
SCHEMA_VERSION = "goal921_db_phase_review_contract_v2"


def _cloud_claim_contract() -> dict[str, Any]:
    return {
        "claim_scope": "prepared DB compact-summary sessions only",
        "non_claim": "not SQL, not DBMS behavior, not full row materialization speedup, and not broad RTX app speedup",
        "required_phase_groups": (
            "one_shot_total_sec",
            "prepared_session_prepare_total_sec",
            "prepared_session_warm_query_sec",
            "reported_prepare_phases_sec",
            "reported_run_phases_sec",
            "reported_native_db_phases_sec",
            "reported_run_phase_totals_sec",
            "reported_native_db_phase_totals_sec",
            "db_review_observation",
        ),
        "cloud_policy": "include in the single active RTX batch only after local pre-cloud readiness passes",
    }


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
        phases["unified_session"] = {
            key: value
            for key, value in session.items()
            if key != "per_section_run_sec"
        }
    for name, section in payload.get("sections", {}).items():
        if isinstance(section, dict) and isinstance(section.get("session"), dict):
            phases[name] = dict(section["session"])
    return phases


def _reported_run_phases(payload: dict[str, Any]) -> dict[str, Any]:
    phases: dict[str, Any] = {}
    session = payload.get("prepared_session")
    if isinstance(session, dict) and isinstance(session.get("per_section_run_sec"), dict):
        phases["unified_session"] = {"per_section_run_sec": dict(session["per_section_run_sec"])}
    for name, section in payload.get("sections", {}).items():
        if isinstance(section, dict) and isinstance(section.get("run_phases"), dict):
            phases[name] = dict(section["run_phases"])
    return phases


def _reported_run_phase_modes(payload: dict[str, Any]) -> dict[str, Any]:
    phase_modes: dict[str, Any] = {}
    for name, section in payload.get("sections", {}).items():
        if not isinstance(section, dict):
            continue
        run_phases = section.get("run_phases")
        if not isinstance(run_phases, dict):
            continue
        phase_modes[name] = {
            "scan": (
                "count_summary"
                if "query_conjunctive_scan_count_sec" in run_phases
                else "row_materializing"
                if "query_conjunctive_scan_and_materialize_sec" in run_phases
                else "unknown"
            ),
            "grouped_count": (
                "group_summary"
                if "query_grouped_count_summary_sec" in run_phases
                else "row_materializing"
                if "query_grouped_count_and_materialize_sec" in run_phases
                else "unknown"
            ),
            "grouped_sum": (
                "group_summary"
                if "query_grouped_sum_summary_sec" in run_phases
                else "row_materializing"
                if "query_grouped_sum_and_materialize_sec" in run_phases
                else "unknown"
            ),
        }
    return phase_modes


def _reported_run_phase_totals(payload: dict[str, Any]) -> dict[str, Any]:
    totals: dict[str, Any] = {
        "all_sections_query_sec": 0.0,
        "all_sections_python_summary_postprocess_sec": 0.0,
        "row_materializing_operation_count": 0,
        "compact_summary_operation_count": 0,
        "sections": {},
    }
    modes = _reported_run_phase_modes(payload)
    for name, section in payload.get("sections", {}).items():
        if not isinstance(section, dict):
            continue
        run_phases = section.get("run_phases")
        if not isinstance(run_phases, dict):
            continue
        query_sec = sum(
            float(value)
            for key, value in run_phases.items()
            if key.startswith("query_") and isinstance(value, (int, float))
        )
        postprocess_sec = float(run_phases.get("python_summary_postprocess_sec", 0.0) or 0.0)
        section_modes = modes.get(name, {})
        row_materializing = sum(1 for mode in section_modes.values() if mode == "row_materializing")
        compact_summary = sum(1 for mode in section_modes.values() if mode in {"count_summary", "group_summary"})
        totals["all_sections_query_sec"] += query_sec
        totals["all_sections_python_summary_postprocess_sec"] += postprocess_sec
        totals["row_materializing_operation_count"] += row_materializing
        totals["compact_summary_operation_count"] += compact_summary
        totals["sections"][name] = {
            "query_sec": query_sec,
            "python_summary_postprocess_sec": postprocess_sec,
            "row_materializing_operation_count": row_materializing,
            "compact_summary_operation_count": compact_summary,
        }
    return totals


def _reported_native_db_phases(payload: dict[str, Any]) -> dict[str, Any]:
    phases: dict[str, Any] = {}
    for name, section in payload.get("sections", {}).items():
        if isinstance(section, dict) and isinstance(section.get("native_db_phases"), dict):
            phases[name] = dict(section["native_db_phases"])
    return phases


def _reported_native_db_phase_totals(native_phases: dict[str, Any]) -> dict[str, Any]:
    totals: dict[str, Any] = {
        "counter_status": "absent",
        "operation_count": 0,
        "traversal_sec": 0.0,
        "bitset_copyback_sec": 0.0,
        "exact_filter_sec": 0.0,
        "output_pack_sec": 0.0,
        "raw_candidate_count": 0,
        "emitted_count": 0,
        "sections": {},
    }
    for section_name, section_phases in native_phases.items():
        if not isinstance(section_phases, dict):
            continue
        section_total = {
            "operation_count": 0,
            "traversal_sec": 0.0,
            "bitset_copyback_sec": 0.0,
            "exact_filter_sec": 0.0,
            "output_pack_sec": 0.0,
            "raw_candidate_count": 0,
            "emitted_count": 0,
        }
        for phase in section_phases.values():
            if not isinstance(phase, dict):
                continue
            section_total["operation_count"] += 1
            section_total["traversal_sec"] += float(phase.get("traversal", 0.0) or 0.0)
            section_total["bitset_copyback_sec"] += float(phase.get("bitset_copyback", 0.0) or 0.0)
            section_total["exact_filter_sec"] += float(phase.get("exact_filter", 0.0) or 0.0)
            section_total["output_pack_sec"] += float(phase.get("output_pack", 0.0) or 0.0)
            section_total["raw_candidate_count"] += int(phase.get("raw_candidate_count", 0) or 0)
            section_total["emitted_count"] += int(phase.get("emitted_count", 0) or 0)
        if section_total["operation_count"]:
            totals["sections"][section_name] = section_total
            totals["operation_count"] += section_total["operation_count"]
            totals["traversal_sec"] += section_total["traversal_sec"]
            totals["bitset_copyback_sec"] += section_total["bitset_copyback_sec"]
            totals["exact_filter_sec"] += section_total["exact_filter_sec"]
            totals["output_pack_sec"] += section_total["output_pack_sec"]
            totals["raw_candidate_count"] += section_total["raw_candidate_count"]
            totals["emitted_count"] += section_total["emitted_count"]
    if totals["operation_count"]:
        totals["counter_status"] = "exported"
    elif native_phases:
        totals["counter_status"] = "empty"
    return totals


def _db_review_observation(
    *,
    output_mode: str,
    run_phase_totals: dict[str, Any],
    native_phase_totals: dict[str, Any],
) -> dict[str, Any]:
    row_materializing = int(run_phase_totals.get("row_materializing_operation_count", 0) or 0)
    compact_summary = int(run_phase_totals.get("compact_summary_operation_count", 0) or 0)
    native_status = str(native_phase_totals.get("counter_status", "absent"))
    if output_mode != "compact_summary":
        status = "not_claim_path"
        blocker = "DB RT-core review requires compact_summary output mode."
    elif row_materializing:
        status = "needs_interface_tuning"
        blocker = "One or more DB operations still materialize rows in the warm-query path."
    elif native_status != "exported":
        status = "needs_native_counter_artifact"
        blocker = "Compact-summary shape is clean, but this artifact lacks exported OptiX native DB counters."
    elif compact_summary:
        status = "phase_clean_candidate_for_rtx_review"
        blocker = "None for local shape; compare RTX artifact against baselines before promotion."
    else:
        status = "unrecognized"
        blocker = "No DB run-phase operations were detected."
    return {
        "status": status,
        "blocker": blocker,
        "row_materializing_operation_count": row_materializing,
        "compact_summary_operation_count": compact_summary,
        "native_counter_status": native_status,
    }


def _profile_backend(
    backend: str,
    *,
    scenario: str,
    copies: int,
    iterations: int,
    output_mode: str,
) -> dict[str, Any]:
    one_shot_payload, one_shot_sec = _time_call(
        lambda: db_app.run_app(backend, scenario=scenario, copies=copies, output_mode=output_mode)
    )

    session, prepare_total_sec = _time_call(lambda: db_app.prepare_session(backend, scenario=scenario, copies=copies))
    run_samples: list[float] = []
    last_payload: dict[str, Any] | None = None
    close_sec = 0.0
    try:
        for _ in range(iterations):
            last_payload, elapsed = _time_call(lambda: session.run(output_mode=output_mode))
            run_samples.append(elapsed)
    finally:
        _, close_sec = _time_call(session.close)

    reported_native_db_phases = _reported_native_db_phases(last_payload or {})
    run_phase_totals = _reported_run_phase_totals(last_payload or {})
    native_phase_totals = _reported_native_db_phase_totals(reported_native_db_phases)

    return {
        "backend": backend,
        "status": "ok",
        "schema_version": SCHEMA_VERSION,
        "cloud_claim_contract": _cloud_claim_contract(),
        "output_mode": output_mode,
        "one_shot_total_sec": one_shot_sec,
        "prepared_session_prepare_total_sec": prepare_total_sec,
        "prepared_session_warm_query_sec": _stats(run_samples),
        "prepared_session_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": (
            one_shot_sec / statistics.median(run_samples) if run_samples and statistics.median(run_samples) > 0.0 else 0.0
        ),
        "reported_prepare_phases_sec": _reported_session_phases(last_payload or {}),
        "reported_run_phases_sec": _reported_run_phases(last_payload or {}),
        "reported_run_phase_modes": _reported_run_phase_modes(last_payload or {}),
        "reported_run_phase_totals_sec": run_phase_totals,
        "reported_native_db_phases_sec": reported_native_db_phases,
        "reported_native_db_phase_totals_sec": native_phase_totals,
        "db_review_observation": _db_review_observation(
            output_mode=output_mode,
            run_phase_totals=run_phase_totals,
            native_phase_totals=native_phase_totals,
        ),
        "phase_contract": {
            "one_shot_total": "complete public app call including fixture construction, backend selection, native prepare, query, materialization, and summary postprocess",
            "prepared_session_prepare_total": "public app prepare_session call including fixture construction and native prepared dataset creation where available",
            "prepared_session_warm_query": "session.run only: prepared queries plus any required grouped/row output shaping and app summary construction",
            "reported_prepare_phases": "scenario-provided construction/selection/prepare timers embedded in app JSON",
            "reported_run_phases": "scenario-provided per-operation query timers embedded in app JSON; grouped compact-summary fast paths use query_*_summary_sec while row paths use query_*_and_materialize_sec",
            "reported_run_phase_modes": "per-section classification of scan/grouped_count/grouped_sum as count_summary, group_summary, or row_materializing",
            "reported_run_phase_totals": "summed query/postprocess phase time plus explicit row-materializing versus compact-summary operation counts",
            "reported_native_db_phases": "OptiX prepared DB native counters when exported: traversal, candidate bitset copy-back, exact native filtering/grouping, output packing, raw candidate count, and emitted result count",
            "reported_native_db_phase_totals": "summed native DB counters across sections and operations; counter_status is exported, empty, or absent",
            "db_review_observation": "machine-readable local readiness observation for DB compact-summary RTX review; not a public speedup claim",
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
    output_mode: str,
    strict: bool,
) -> dict[str, Any]:
    if copies <= 0:
        raise ValueError("--copies must be positive")
    if iterations <= 0:
        raise ValueError("--iterations must be positive")

    results: list[dict[str, Any]] = []
    for backend in backends:
        try:
            results.append(_profile_backend(
                backend,
                scenario=scenario,
                copies=copies,
                iterations=iterations,
                output_mode=output_mode,
            ))
        except Exception as exc:
            if strict:
                raise
            results.append({"backend": backend, "status": "skipped_or_failed", "error": str(exc)})

    return {
        "suite": "goal756_db_prepared_session_perf",
        "schema_version": SCHEMA_VERSION,
        "cloud_claim_contract": _cloud_claim_contract(),
        "scenario": scenario,
        "copies": copies,
        "iterations": iterations,
        "output_mode": output_mode,
        "results": results,
        "boundary": "Prepared DB session profiler compares one-shot app calls with reused prepared sessions. GTX 1070 evidence is backend behavior evidence only, not RTX RT-core speedup evidence.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal756 DB prepared-session performance profiler.")
    parser.add_argument("--backend", action="append", choices=BACKENDS)
    parser.add_argument("--scenario", choices=("regional_dashboard", "sales_risk", "all"), default="all")
    parser.add_argument("--copies", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output-mode", choices=("summary", "compact_summary"), default="summary")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)

    payload = run_suite(
        backends=tuple(args.backend) if args.backend else ("cpu", "embree", "optix", "vulkan"),
        scenario=args.scenario,
        copies=args.copies,
        iterations=args.iterations,
        output_mode=args.output_mode,
        strict=args.strict,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
