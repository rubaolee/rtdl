#!/usr/bin/env python3
"""Compare author and RTDL outputs for a mapped X-HD same-input gate.

This app-owned helper follows
``build_xhd_mapped_candidate_same_input_gate_packet.py``. It reads the packet's
expected author and RTDL JSON outputs, compares ``HDResult`` with an explicit
tolerance, and keeps timing fields as separated evidence. It does not compute a
performance ratio and does not claim full paper reproduction.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
import sys
from typing import Any, Dict, List


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        out = float(value)
    except Exception:
        return None
    return out if math.isfinite(out) else None


def _extract_author_timing(payload: Dict[str, Any]) -> Dict[str, Any]:
    running = payload.get("Running") if isinstance(payload.get("Running"), dict) else {}
    repeats = running.get("Repeats") if isinstance(running.get("Repeats"), list) else []
    reported_times = [
        float(value)
        for repeat in repeats
        if isinstance(repeat, dict)
        for value in [_float_or_none(repeat.get("ReportedTime"))]
        if value is not None
    ]
    return {
        "running_avg_time_ms": _float_or_none(running.get("AvgTime")),
        "reported_time_ms_values": reported_times,
        "reported_time_ms_median": statistics.median(reported_times) if reported_times else None,
        "timing_semantics": "author hd_exec internal Running fields; not ratio-aligned with RTDL route timing",
    }


def _extract_rtdl_timing(payload: Dict[str, Any]) -> Dict[str, Any]:
    running = payload.get("Running") if isinstance(payload.get("Running"), dict) else {}
    rtdl = payload.get("RTDL") if isinstance(payload.get("RTDL"), dict) else {}
    return {
        "running_avg_time_ms": _float_or_none(running.get("AvgTime")),
        "route_label": rtdl.get("route_label"),
        "run_phases": rtdl.get("run_phases") if isinstance(rtdl.get("run_phases"), dict) else {},
        "timing_semantics": rtdl.get(
            "running_avg_time_semantics",
            "RTDL timing semantics unavailable; do not compare as author internal timing",
        ),
    }


def _compare_workload(packet_workload: Dict[str, Any], *, tolerance: float) -> Dict[str, Any]:
    expected = packet_workload.get("expected_outputs")
    if not isinstance(expected, dict):
        return {
            "workload_id": packet_workload.get("workload_id"),
            "matched": False,
            "status": "expected_outputs_missing_from_packet",
            "errors": ["expected_outputs missing from workload packet"],
        }
    author_path = pathlib.Path(str(expected.get("author_json", "")))
    rtdl_path = pathlib.Path(str(expected.get("rtdl_json", "")))
    errors: List[str] = []
    if not author_path.exists():
        errors.append(f"author JSON missing: {author_path}")
    if not rtdl_path.exists():
        errors.append(f"RTDL JSON missing: {rtdl_path}")
    if errors:
        return {
            "workload_id": packet_workload.get("workload_id"),
            "author_json": str(author_path),
            "rtdl_json": str(rtdl_path),
            "matched": False,
            "status": "outputs_missing",
            "errors": errors,
        }

    author_payload = _load_json(author_path)
    rtdl_payload = _load_json(rtdl_path)
    author_hd = _float_or_none(author_payload.get("HDResult"))
    rtdl_hd = _float_or_none(rtdl_payload.get("HDResult"))
    if author_hd is None or rtdl_hd is None:
        errors.append("HDResult missing or non-finite in author or RTDL JSON")
        abs_diff = None
        matched = False
    else:
        abs_diff = abs(author_hd - rtdl_hd)
        matched = bool(abs_diff <= tolerance)

    return {
        "workload_id": packet_workload.get("workload_id"),
        "figure": packet_workload.get("figure"),
        "input_type": packet_workload.get("input_type"),
        "n_dims": packet_workload.get("n_dims"),
        "author_json": str(author_path),
        "rtdl_json": str(rtdl_path),
        "author_hd_result": author_hd,
        "rtdl_hd_result": rtdl_hd,
        "abs_diff": abs_diff,
        "tolerance": tolerance,
        "matched": matched,
        "status": "matched" if matched else "mismatch_or_invalid",
        "errors": errors,
        "author_timing": _extract_author_timing(author_payload),
        "rtdl_timing": _extract_rtdl_timing(rtdl_payload),
        "performance_ratio_reported": False,
    }


def build_comparison(packet_path: pathlib.Path, *, tolerance: float) -> Dict[str, Any]:
    packet = _load_json(packet_path)
    errors: List[str] = []
    if packet.get("schema") != "rtdl.paper_reproduction.xhd.mapped_candidate_same_input_gate_packet.v1":
        errors.append("packet schema mismatch")
    if packet.get("classification") != "mapped_candidate_same_input_gate_commands_ready":
        errors.append(f"packet is not command-ready: {packet.get('classification')}")
    workloads = packet.get("workload_packets")
    if not isinstance(workloads, list) or not workloads:
        errors.append("packet has no workload_packets")
        workloads = []

    comparisons = [
        _compare_workload(workload, tolerance=tolerance)
        for workload in workloads
        if isinstance(workload, dict)
    ]
    any_missing = any(comp.get("status") == "outputs_missing" for comp in comparisons)
    all_matched = bool(comparisons and all(comp.get("matched") is True for comp in comparisons))
    if errors:
        classification = "packet_not_ready_for_output_comparison"
        same_input_gate_passed = False
    elif any_missing:
        classification = "mapped_candidate_outputs_missing"
        same_input_gate_passed = False
    elif all_matched:
        classification = "mapped_candidate_same_input_gate_passed"
        same_input_gate_passed = True
    else:
        classification = "mapped_candidate_same_input_gate_failed"
        same_input_gate_passed = False

    return {
        "schema": "rtdl.paper_reproduction.xhd.mapped_candidate_same_input_output_comparison.v1",
        "packet_path": str(packet_path),
        "classification": classification,
        "same_input_gate_passed": same_input_gate_passed,
        "workload_comparison_count": len(comparisons),
        "matched_count": sum(1 for comp in comparisons if comp.get("matched") is True),
        "comparisons": comparisons,
        "errors": errors,
        "performance_ratio_reported": False,
        "sufficient_to_claim_exact_input": False,
        "claim_boundary": {
            "same_input_gate_passed": same_input_gate_passed,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "claiming exact paper dataset reproduction from same-input HDResult match alone",
            "claiming Figure 5 reproduction from this comparison alone",
            "claiming full X-HD paper reproduction from this comparison alone",
            "claiming author-vs-RTDL performance ratio from this comparison",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_json", type=pathlib.Path)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        comparison = build_comparison(args.packet_json, tolerance=args.tolerance)
    except Exception as exc:
        print(f"mapped candidate output comparison failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(comparison, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if comparison["classification"] == "mapped_candidate_same_input_gate_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
