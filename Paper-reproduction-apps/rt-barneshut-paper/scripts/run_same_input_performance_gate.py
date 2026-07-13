#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"
RUN_DIR = APP_DIR / "_runs" / "same_input_performance_gate"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return numerator / denominator


def build_summary(app_dir: Path) -> tuple[dict[str, Any], int]:
    output = app_dir / "_runs" / "same_input_performance_gate" / "summary.json"
    missing: list[str] = []
    paths = {
        "author_treelogy": app_dir / "_runs" / "author_same_input" / "summary.json",
        "rtdl_diagnostic": app_dir / "_runs" / "rtdl_diagnostic" / "summary.json",
        "author_comparator": app_dir / "_runs" / "author_comparator_gate" / "summary.json",
        "same_input_compare": app_dir / "_runs" / "same_input_rtdl_comparison_gate" / "summary.json",
    }
    payloads: dict[str, dict[str, Any]] = {}
    for key, path in paths.items():
        try:
            payloads[key] = read_json(path)
        except FileNotFoundError:
            missing.append(str(path))

    if missing:
        summary = {
            "mode": "same_input_performance_gate",
            "status": "blocked_missing_required_summaries",
            "missing": missing,
            "paper_reproduction_complete": False,
            "performance_review_complete": False,
            "claim_boundary": (
                "Performance summary requires completed same-input author and "
                "RTDL correctness gates. Missing summaries mean no performance "
                "claim is authorized."
            ),
        }
        return summary, 2

    author_comparator = payloads["author_comparator"]
    same_input_compare = payloads["same_input_compare"]
    author_treelogy = payloads["author_treelogy"]
    rtdl_summary = payloads["rtdl_diagnostic"]
    rtdl_payload = rtdl_summary.get("rtdl_payload") or {}
    rtdl_timing = rtdl_payload.get("timing_ms") or {}

    correctness_ready = bool(
        author_comparator.get("same_input_author_comparator_closed")
        and same_input_compare.get("same_input_author_rtdl_comparator_closed")
        and same_input_compare.get("matched")
    )
    author_force_ms = maybe_number(author_treelogy.get("rt_core_force_ms"))
    author_preprocess_ms = maybe_number(author_treelogy.get("preprocessing_ms"))
    author_execution_ms = maybe_number(author_treelogy.get("execution_ms"))
    rtdl_resident_min_ms = maybe_number(rtdl_timing.get("resident_kernel_min"))
    rtdl_resident_mean_ms = maybe_number(rtdl_timing.get("resident_kernel_mean"))
    rtdl_tree_prepare_ms = maybe_number(rtdl_timing.get("tree_prepare_cpu"))
    rtdl_compile_ms = maybe_number(rtdl_timing.get("extension_compile"))
    rtdl_tensor_prepare_ms = maybe_number(rtdl_timing.get("tensor_prepare_host_to_device"))

    comparable_timing_available = author_force_ms is not None and rtdl_resident_min_ms is not None
    summary = {
        "mode": "same_input_performance_gate",
        "status": (
            "ready_for_phase_boundary_review"
            if correctness_ready and comparable_timing_available
            else "blocked_until_correctness_and_timing_are_available"
        ),
        "paper_reproduction_complete": False,
        "performance_review_complete": False,
        "correctness_ready": correctness_ready,
        "same_input_compare": {
            "matched": bool(same_input_compare.get("matched")),
            "force_count": same_input_compare.get("force_count"),
            "max_abs_error": same_input_compare.get("max_abs_error"),
            "max_rel_error": same_input_compare.get("max_rel_error"),
            "mismatch_count": same_input_compare.get("mismatch_count"),
        },
        "author_treelogy_timing_ms": {
            "preprocessing": author_preprocess_ms,
            "rt_core_force": author_force_ms,
            "execution": author_execution_ms,
        },
        "rtdl_diagnostic_timing_ms": {
            "tree_prepare_cpu": rtdl_tree_prepare_ms,
            "extension_compile": rtdl_compile_ms,
            "tensor_prepare_host_to_device": rtdl_tensor_prepare_ms,
            "resident_kernel_min": rtdl_resident_min_ms,
            "resident_kernel_mean": rtdl_resident_mean_ms,
        },
        "narrow_force_kernel_ratio_rtdl_over_author": ratio(rtdl_resident_min_ms, author_force_ms),
        "phase_boundary": {
            "author_force_phase": (
                "Patched author treelogy summary field rt_core_force_ms parsed from "
                "RT Cores Force Calculations time. RTBH_FORCE_OUT is emitted after "
                "the measured force phase."
            ),
            "rtdl_force_phase": (
                "RTDL resident_kernel_min from CUDA event timing inside the diagnostic "
                "force kernel. Tree preparation, extension compilation, host-to-device "
                "tensor preparation, and force-file dump are reported separately."
            ),
            "review_required": (
                "The ratio is a narrow force-kernel comparison, not a whole paper "
                "performance claim. A completed paper-reproduction claim still needs "
                "human review of matched phase boundaries."
            ),
        },
        "source_summaries": {key: str(path) for key, path in paths.items()},
        "claim_boundary": (
            "Same-input performance summary only. It is valid only after same-input "
            "correctness gates close, and it does not authorize a completed "
            "RT-BarnesHut paper-reproduction claim by itself."
        ),
    }
    return summary, 0 if summary["status"] == "ready_for_phase_boundary_review" else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize same-input RT-BarnesHut timing fields.")
    parser.add_argument("--app-dir", type=Path, default=APP_DIR)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    app_dir = args.app_dir.resolve()
    output = args.output.resolve() if args.output else app_dir / "_runs" / "same_input_performance_gate" / "summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    summary, exit_code = build_summary(app_dir)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
