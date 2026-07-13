#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"


AUTHOR_PHASE = "author_treelogy_timing_ms.rt_core_force"
RTDL_PHASE = "rtdl_diagnostic_timing_ms.resident_kernel_min"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def build_template(performance_summary: dict[str, Any], performance_path: Path) -> dict[str, Any]:
    return {
        "mode": "rt_barneshut_phase_boundary_review",
        "performance_review_complete": False,
        "phase_boundary_accepted": False,
        "reviewed_summary_path": str(performance_path),
        "accepted_author_phase": AUTHOR_PHASE,
        "accepted_rtdl_phase": RTDL_PHASE,
        "reviewed_ratio_rtdl_over_author": performance_summary.get(
            "narrow_force_kernel_ratio_rtdl_over_author"
        ),
        "reviewer_notes": (
            "Human reviewer must confirm that the author rt_core_force phase and "
            "RTDL resident_kernel_min phase are comparable for the intended claim."
        ),
        "claim_boundary": (
            "Draft only. Set performance_review_complete=true and "
            "phase_boundary_accepted=true only after reviewing the matched phase "
            "boundary. This file does not prove completed paper reproduction by itself."
        ),
    }


def build_gate(app_dir: Path, review_path: Path, *, write_template: bool) -> tuple[dict[str, Any], int]:
    performance_path = app_dir / "_runs" / "same_input_performance_gate" / "summary.json"
    output_review_path = review_path
    performance = read_json(performance_path)

    if performance is None:
        return (
            {
                "mode": "rt_barneshut_phase_boundary_review_gate",
                "status": "blocked_missing_performance_summary",
                "paper_reproduction_complete": False,
                "performance_summary": str(performance_path),
            },
            2,
        )

    if performance.get("status") != "ready_for_phase_boundary_review":
        return (
            {
                "mode": "rt_barneshut_phase_boundary_review_gate",
                "status": "blocked_performance_summary_not_ready",
                "paper_reproduction_complete": False,
                "performance_summary": str(performance_path),
                "performance_status": performance.get("status"),
            },
            2,
        )

    if write_template and not output_review_path.exists():
        output_review_path.parent.mkdir(parents=True, exist_ok=True)
        output_review_path.write_text(
            json.dumps(build_template(performance, performance_path), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    review = read_json(output_review_path)
    if review is None:
        return (
            {
                "mode": "rt_barneshut_phase_boundary_review_gate",
                "status": "blocked_missing_phase_boundary_review",
                "paper_reproduction_complete": False,
                "performance_summary": str(performance_path),
                "expected_review": str(output_review_path),
                "template_hint": "rerun with --write-template to create a draft review artifact",
            },
            2,
        )

    expected_ratio = maybe_float(performance.get("narrow_force_kernel_ratio_rtdl_over_author"))
    reviewed_ratio = maybe_float(review.get("reviewed_ratio_rtdl_over_author"))
    ratio_matches = (
        expected_ratio is not None
        and reviewed_ratio is not None
        and math.isclose(expected_ratio, reviewed_ratio, rel_tol=1e-12, abs_tol=1e-12)
    )
    path_matches = review.get("reviewed_summary_path") == str(performance_path)
    author_phase_matches = review.get("accepted_author_phase") == AUTHOR_PHASE
    rtdl_phase_matches = review.get("accepted_rtdl_phase") == RTDL_PHASE
    review_complete = bool(review.get("performance_review_complete"))
    phase_accepted = bool(review.get("phase_boundary_accepted"))

    checks = {
        "performance_review_complete": review_complete,
        "phase_boundary_accepted": phase_accepted,
        "reviewed_summary_path_matches": path_matches,
        "accepted_author_phase_matches": author_phase_matches,
        "accepted_rtdl_phase_matches": rtdl_phase_matches,
        "reviewed_ratio_matches_summary": ratio_matches,
    }
    accepted = all(checks.values())
    return (
        {
            "mode": "rt_barneshut_phase_boundary_review_gate",
            "status": "accepted" if accepted else "blocked_review_incomplete_or_mismatched",
            "paper_reproduction_complete": False,
            "performance_summary": str(performance_path),
            "review": str(output_review_path),
            "checks": checks,
            "expected": {
                "reviewed_summary_path": str(performance_path),
                "accepted_author_phase": AUTHOR_PHASE,
                "accepted_rtdl_phase": RTDL_PHASE,
                "reviewed_ratio_rtdl_over_author": expected_ratio,
            },
            "observed": {
                "reviewed_summary_path": review.get("reviewed_summary_path"),
                "accepted_author_phase": review.get("accepted_author_phase"),
                "accepted_rtdl_phase": review.get("accepted_rtdl_phase"),
                "reviewed_ratio_rtdl_over_author": reviewed_ratio,
            },
            "claim_boundary": (
                "Phase-boundary review gate only. It validates that a human review "
                "artifact accepts the same timing summary, phase labels, and ratio. "
                "It does not authorize paper reproduction without the completion audit."
            ),
        },
        0 if accepted else 2,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate RT-BarnesHut performance phase-boundary review.")
    parser.add_argument("--app-dir", type=Path, default=APP_DIR)
    parser.add_argument(
        "--review",
        type=Path,
        default=None,
        help="Path to phase_boundary_review.json; defaults under same_input_performance_gate.",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--write-template", action="store_true")
    args = parser.parse_args(argv)

    app_dir = args.app_dir.resolve()
    review_path = (
        args.review.resolve()
        if args.review is not None
        else app_dir / "_runs" / "same_input_performance_gate" / "phase_boundary_review.json"
    )
    output = (
        args.output.resolve()
        if args.output is not None
        else app_dir / "_runs" / "phase_boundary_review_gate" / "summary.json"
    )
    summary, exit_code = build_gate(app_dir, review_path, write_template=args.write_template)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
