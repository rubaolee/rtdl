#!/usr/bin/env python3
"""Build Goal5291 Figure 5 Dragon -> HappyBuddha candidate matrix.

This script consolidates existing author-log, author rerun, and RTDL route
evidence for the strongest currently available Figure 5 graphics candidate.
It intentionally reports separated denominators and never computes an
author-vs-RTDL performance ratio.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


TARGET_PAIR = ("dragon.ply", "happy_buddha.ply")
TOLERANCE = 1e-6


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"could not parse JSON: {path}") from exc


def _paper_log_rows(log_index: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for record in log_index.get("run_all_records", []):
        files = tuple(item.get("basename") for item in record.get("input", {}).get("files", []))
        if files == TARGET_PAIR and record.get("category") == "graphics":
            rows.append(record)
    return rows


def _unique_float(rows: Iterable[Mapping[str, Any]], key: str) -> float:
    values = sorted({
        float(row[key])
        for row in rows
        if row.get(key) is not None
    })
    if len(values) != 1:
        raise ValueError(f"expected exactly one {key}, got {values}")
    return values[0]


def _timing_record(row: Mapping[str, Any]) -> dict[str, Any]:
    running = row.get("running", {})
    return {
        "section": row.get("section"),
        "config": row.get("config"),
        "relative_log_path": row.get("relative_log_path"),
        "gpu": row.get("gpu", {}).get("name"),
        "running_avg_time_ms": running.get("avg_time"),
        "reported_time_median_ms": running.get("reported_time_median"),
        "repeat_count": running.get("repeat_count"),
        "num_points_per_cell": running.get("num_points_per_cell"),
    }


def _first_case(route_artifact: Mapping[str, Any]) -> Mapping[str, Any]:
    cases = route_artifact.get("cases", [])
    if not cases:
        raise ValueError("route artifact has no cases")
    return cases[0]


def _route_entry(label: str, artifact_path: Path, artifact: Mapping[str, Any]) -> dict[str, Any]:
    case = _first_case(artifact)
    rtdl_route = case.get("rtdl_route", {})
    phase = artifact.get("phase_timings_sec", {})
    case_phase = case.get("phase_timings_sec", {})
    return {
        "label": label,
        "artifact": str(artifact_path),
        "goal": artifact.get("goal"),
        "status": artifact.get("status"),
        "matched": case.get("matched"),
        "route_distance": rtdl_route.get("distance"),
        "author_abs_diff": case.get("author_abs_diff"),
        "route_wall_sec": case_phase.get("rtdl_route_wall"),
        "case_total_sec": case_phase.get("case_total"),
        "load_full_inputs_sec": phase.get("load_full_inputs"),
        "artifact_total_sec": phase.get("total"),
        "route_warmup_used": artifact.get("summary_statistics", {}).get("route_warmup_used"),
        "route_warmup_sec": phase.get("route_warmup"),
        "per_source_witness_exact": rtdl_route.get("per_source_witness_exact"),
        "global_bound_early_break": rtdl_route.get("global_bound_early_break"),
        "global_bound_early_break_count": rtdl_route.get("global_bound_early_break_count"),
        "frontier_row_count": rtdl_route.get("frontier_row_count"),
        "native_symbol": rtdl_route.get("frontier_native_symbol"),
    }


def build_matrix(
    *,
    log_index_path: Path,
    author_gate_path: Path,
    phase_matrix_path: Path,
    rtdl_fresh_path: Path,
    rtdl_warm_path: Path,
    date: str,
) -> dict[str, Any]:
    log_index = _load_json(log_index_path)
    author_gate = _load_json(author_gate_path)
    phase_matrix = _load_json(phase_matrix_path)
    rtdl_fresh = _load_json(rtdl_fresh_path)
    rtdl_warm = _load_json(rtdl_warm_path)

    paper_rows = _paper_log_rows(log_index)
    if len(paper_rows) != 5:
        raise ValueError(f"expected five Dragon -> HappyBuddha Figure 5 rows, got {len(paper_rows)}")
    paper_hd = _unique_float(paper_rows, "hd_result")
    author_hd = float(author_gate["author_hd_result"])
    rtdl_fresh_entry = _route_entry("rtdl_goal5212_fresh", rtdl_fresh_path, rtdl_fresh)
    rtdl_warm_entry = _route_entry("rtdl_goal5212_explicit_warm", rtdl_warm_path, rtdl_warm)
    rtdl_fresh_hd = float(rtdl_fresh_entry["route_distance"])
    rtdl_warm_hd = float(rtdl_warm_entry["route_distance"])

    author_vs_paper = abs(author_hd - paper_hd)
    rtdl_fresh_vs_author = abs(rtdl_fresh_hd - author_hd)
    rtdl_warm_vs_author = abs(rtdl_warm_hd - author_hd)
    rtdl_fresh_vs_paper = abs(rtdl_fresh_hd - paper_hd)

    author_phase = phase_matrix.get("author_phase_evidence", {})
    rtdl_phase = phase_matrix.get("rtdl_phase_evidence", {})
    paper_timing_records = [_timing_record(row) for row in sorted(paper_rows, key=lambda row: (str(row.get("section")), str(row.get("config"))))]

    value_matched = (
        author_vs_paper <= TOLERANCE
        and rtdl_fresh_vs_author <= TOLERANCE
        and rtdl_warm_vs_author <= TOLERANCE
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5291.figure5_dragon_happy_candidate_matrix.v1",
        "goal": "Goal5291",
        "date": date,
        "status": (
            "figure5_graphics_dragon_happy_value_matched_candidate_ready__ratio_not_authorized"
            if value_matched
            else "figure5_graphics_dragon_happy_value_mismatch__do_not_time"
        ),
        "inputs": {
            "log_index": str(log_index_path),
            "author_gate": str(author_gate_path),
            "phase_matrix": str(phase_matrix_path),
            "rtdl_fresh_route": str(rtdl_fresh_path),
            "rtdl_explicit_warm_route": str(rtdl_warm_path),
        },
        "candidate": {
            "category": "graphics",
            "pair": list(TARGET_PAIR),
            "level": "level_b_same_source_candidate_only",
            "exact_paper_dataset_identity_proven": False,
            "point_counts": [
                item.get("num_points")
                for item in paper_rows[0].get("input", {}).get("files", [])
            ],
            "paper_log_paths": [
                item.get("path")
                for item in paper_rows[0].get("input", {}).get("files", [])
            ],
        },
        "value_evidence": {
            "tolerance": TOLERANCE,
            "paper_log_hd_result": paper_hd,
            "author_rerun_hd_result": author_hd,
            "rtdl_fresh_hd_result": rtdl_fresh_hd,
            "rtdl_explicit_warm_hd_result": rtdl_warm_hd,
            "author_rerun_vs_paper_log_abs_diff": author_vs_paper,
            "rtdl_fresh_vs_author_rerun_abs_diff": rtdl_fresh_vs_author,
            "rtdl_explicit_warm_vs_author_rerun_abs_diff": rtdl_warm_vs_author,
            "rtdl_fresh_vs_paper_log_abs_diff": rtdl_fresh_vs_paper,
            "value_matched_candidate": value_matched,
            "paper_log_match_note": (
                "Author rerun and RTDL match the paper-branch log within tolerance; "
                "this does not prove byte-identical paper input files."
            ),
        },
        "paper_log_timing_records": paper_timing_records,
        "separated_denominators": {
            "paper_log": {
                "gpu": sorted({str(row.get("gpu", {}).get("name")) for row in paper_rows}),
                "record_count": len(paper_rows),
                "timing_fields": ["Running.AvgTime", "ReportedTime median"],
                "records": paper_timing_records,
            },
            "author_rerun": {
                "gpu": "NVIDIA RTX 4000 Ada Generation",
                "running_avg_time_ms_goal5186": author_gate.get("author_running_avg_time_ms"),
                "phase_matrix_running_avg_time_ms_goal5188": author_phase.get("running_avg_time_ms"),
                "phase_matrix_process_wall_sec_goal5188": author_phase.get("process_wall_sec"),
                "reported_time_ms_goal5188": author_phase.get("reported_time_ms"),
                "bvh_build_time_ms_goal5188": author_phase.get("bvh_build_time_ms"),
                "source": author_phase.get("source"),
            },
            "rtdl_goal5188_baseline_route": {
                "route_wall_sec": rtdl_phase.get("route_wall_sec"),
                "case_total_sec": rtdl_phase.get("case_total_sec"),
                "load_full_inputs_sec": rtdl_phase.get("load_full_inputs_sec"),
                "total_sec": rtdl_phase.get("total_sec"),
                "source": rtdl_phase.get("source"),
            },
            "rtdl_goal5212_fresh_route": rtdl_fresh_entry,
            "rtdl_goal5212_explicit_warm_route": rtdl_warm_entry,
        },
        "comparison_policy": {
            "same_denominator_ratio_allowed": False,
            "ratio_reported": False,
            "forbidden_ratio_reasons": [
                "paper log uses author internal timing on RTX 3090",
                "author rerun uses author internal AvgTime and process wall on RTX 4000 Ada",
                "RTDL reports route/case/load totals with different phase boundaries",
                "exact paper input byte identity is not proven",
                "this covers one graphics pair, not the full Figure 5 matrix",
                "Goal5211/Goal5212 global-bound route preserves HDResult but per-source witnesses may be approximate",
            ],
        },
        "decision": {
            "candidate_ready_for_review": value_matched,
            "continue_to_ratio": False,
            "continue_to_full_figure5_claim": False,
            "next_options": [
                "send Goals5288-5291 as the current Figure 5 review packet",
                "if Figure 5 remains priority, acquire or verify BraTS/geo inputs and exact graphics input provenance",
                "otherwise move to Figure 6 phase/counter mapping or another paper blocker",
            ],
        },
        "claim_boundary": {
            "figure5_reproduced": False,
            "figure5_full_matrix_reproduced": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "level_b_same_source_value_matched_candidate_claimed": value_matched,
        },
        "matched": bool(value_matched),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 5 Dragon -> HappyBuddha candidate matrix.")
    parser.add_argument("--log-index", required=True)
    parser.add_argument("--author-gate", required=True)
    parser.add_argument("--phase-matrix", required=True)
    parser.add_argument("--rtdl-fresh-route", required=True)
    parser.add_argument("--rtdl-warm-route", required=True)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    artifact = build_matrix(
        log_index_path=Path(args.log_index),
        author_gate_path=Path(args.author_gate),
        phase_matrix_path=Path(args.phase_matrix),
        rtdl_fresh_path=Path(args.rtdl_fresh_route),
        rtdl_warm_path=Path(args.rtdl_warm_route),
        date=args.date,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "status": artifact["status"], "matched": artifact["matched"]}, indent=2))
    return 0 if artifact["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
