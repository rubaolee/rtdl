#!/usr/bin/env python3
"""Build the Goal5354 radius-growth semantics artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"


AUTHOR_SOURCE_EXCERPT = {
    "repository": "https://github.com/pwrliang/X-HD.git",
    "commit": "7bf41c8442d059c94f4178355c6d5a10571d9658",
    "file": "src/hd_impl/hausdorff_distance_rt.h",
    "lines": "398-419 in pinned checkout",
    "semantics": [
        "last_in_size = in_size; in_size = in_queue.size(stream)",
        "if in_size > 0 and radius < hd_ub, update radius",
        "adaptive: reduced_factor = (last_in_size - in_size) / last_in_size",
        "adaptive: for expand_factor in [8,4,2,1], if reduced_factor < 1/expand_factor, radius += expand_factor * cell_diagonal and break",
        "double: radius *= 2",
        "add: radius += cell_diagonal",
        "radius = min(radius, hd_ub)",
    ],
}


def _step_dict(**kwargs: Any) -> dict[str, object]:
    return rt.radius_growth_step(**kwargs).to_dict()


def _trace_dict(**kwargs: Any) -> list[dict[str, object]]:
    return [step.to_dict() for step in rt.radius_growth_trace(**kwargs)]


def build_artifact() -> dict[str, Any]:
    adaptive_examples = {
        "low_reduction_adds_8_diagonals": _step_dict(
            radius=2.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=100,
            next_input_count=90,
            mode="adaptive",
        ),
        "strict_boundary_one_eighth_adds_4_diagonals": _step_dict(
            radius=2.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=1000,
            next_input_count=875,
            mode="adaptive",
        ),
        "half_reduction_adds_1_diagonal": _step_dict(
            radius=2.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=100,
            next_input_count=50,
            mode="adaptive",
        ),
    }
    mode_examples = {
        "double": _step_dict(
            radius=3.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=10,
            next_input_count=8,
            mode="double",
        ),
        "add": _step_dict(
            radius=3.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=10,
            next_input_count=8,
            mode="add",
        ),
        "clamp": _step_dict(
            radius=9.0,
            hd_upper_bound=10.0,
            cell_diagonal=2.0,
            last_input_count=100,
            next_input_count=99,
            mode="adaptive",
        ),
    }
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5354.radius_growth_semantics.v1",
        "goal": "Goal5354",
        "date": "2026-07-09",
        "status": "radius_growth_schedule_helper_ready__route_mapping_not_yet_enabled",
        "purpose": (
            "Extract the author-compatible add/double/adaptive radius update rule "
            "into a generic RTDL helper and prove the strict threshold behavior."
        ),
        "author_source_excerpt": AUTHOR_SOURCE_EXCERPT,
        "rtdl_api": {
            "module": "src/rtdsl/radius_schedule.py",
            "exports": [
                "RadiusGrowthStep",
                "radius_growth_step",
                "radius_growth_trace",
                "RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION",
            ],
            "contract": rt.RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION,
            "app_semantics": "none",
        },
        "examples": {
            "adaptive": adaptive_examples,
            "modes": mode_examples,
            "non_xhd_retry_radius_consumer_trace": _trace_dict(
                initial_radius=0.25,
                hd_upper_bound=5.0,
                cell_diagonal=0.25,
                input_counts=[20, 18, 9, 3],
                mode="adaptive",
            ),
        },
        "current_xhd_mapping_status": {
            "tune_radius_author_values": ["adaptive", "double", "add"],
            "helper_semantics_available": True,
            "run_xhd_rtdl_hd_exec_explicit_tune_radius_still_fail_closed": True,
            "route_uses_helper": False,
            "reason": (
                "This goal proves the schedule rule in isolation. A later behavior "
                "gate must decide how to wire it into the cell-MBR route and compare "
                "iteration traces against author outputs."
            ),
        },
        "claim_boundary": {
            "author_rt_core_algorithm_equivalence_claimed": False,
            "author_tune_radius_route_mapping_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next_targets": [
            "wire_tune_radius_to_cell_mbr_route_under_explicit_flag",
            "compare_author_and_rtdl_radius_iteration_trace_on_bounded_or_level_b_input",
            "keep_explicit_tune_radius_fail_closed_until_trace_mapping_is_verified",
        ],
        "exit_label": "radius_growth_schedule_helper_ready__next_target_route_trace_mapping",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5354_radius_growth_semantics.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
