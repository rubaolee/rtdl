#!/usr/bin/env python3
"""Build the Goal5421 bounded-geo same-POD packet plan.

This script is intentionally planning-only.  It reads existing Goal5420,
Goal5305, and Goal5307 evidence and writes the command packet that a later
execution goal may run through scripts/current_pod_ssh.py.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5421_bounded_geo_same_pod_packet_plan.json"

GOAL5420 = RESULTS / "xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json"
GOAL5305 = RESULTS / "xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json"
GOAL5307 = RESULTS / "xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json"

AUTHOR_BIN = "/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec"
RTDL_REPO = "/tmp/rtdl_goal5419"
RTDL_SCRIPT = (
    "/tmp/rtdl_goal5419/Paper-reproduction-apps/x-hd-paper/scripts/"
    "run_xhd_goal5305_county_zcta_rtdl_numba_gate.py"
)
RTDL_LIBRARY = "/tmp/rtdl_goal5419/build/librtdl_optix.so"
POD_HOST = "213.173.108.24"
POD_PORT = 13502


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _author_command(input1: str, input2: str, output_json: str) -> list[str]:
    return [
        AUTHOR_BIN,
        "-input1",
        input1,
        "-input2",
        input2,
        "-input_type",
        "wkt",
        "-n_dims",
        "2",
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "-normalize=false",
        "-json",
        output_json,
        "-overwrite=true",
        "-check=false",
    ]


def _rtdl_command(input1: str, input2: str, author_json: str, summary: str) -> list[str]:
    return [
        "cd",
        RTDL_REPO,
        "&&",
        "PYTHONPATH=src:.",
        f"RTDL_OPTIX_LIBRARY={RTDL_LIBRARY}",
        "python3",
        RTDL_SCRIPT,
        "--input1",
        input1,
        "--input2",
        input2,
        "--author-json",
        author_json,
        "--summary",
        summary,
        "--input-type",
        "wkt",
        "--n-dims",
        "2",
        "--partner",
        "triton",
        "--triton-strategy",
        "dense_point_nearest_tiled",
        "--tolerance",
        "1e-5",
    ]


def _county_row(goal5305: dict[str, Any]) -> dict[str, Any]:
    input_info = goal5305["input"]
    author = goal5305["author"]
    rtdl = goal5305["rtdl"]
    phases = goal5305["run_phases"]
    return {
        "case_id": "county_zcta_bounded",
        "paper_pair": "dtl_cnty.wkt -> uszipcode.wkt",
        "category": "geo_bounded",
        "input_identity_level": "level_b_bounded_geo_fixture",
        "input_type": "wkt",
        "n_dims": 2,
        "remote_inputs": {
            "input1": input_info["input1"],
            "input2": input_info["input2"],
        },
        "expected_point_counts": [input_info["point_count_a"], input_info["point_count_b"]],
        "author": {
            "expected_hd_result": author["HDResult"],
            "prior_author_json": author["author_json"],
            "prior_running_avg_time_ms": None,
            "command": _author_command(
                input_info["input1"],
                input_info["input2"],
                "/tmp/xhd_goal5422/out/author_county_zcta_bounded.json",
            ),
        },
        "rtdl": {
            "expected_hd_result": rtdl["HDResult"],
            "prior_route_sec": phases["rtdl_route_sec"],
            "prior_total_sec": phases["total_sec"],
            "route": rtdl["route"],
            "partner": rtdl["partner"],
            "triton_strategy": rtdl["triton_strategy"],
            "partner_reference_contract": rtdl["partner_reference_contract"],
            "native_engine_row_contract": rtdl["native_engine_row_contract"],
            "per_source_witness_exact": rtdl["per_source_witness_exact"],
            "command": _rtdl_command(
                input_info["input1"],
                input_info["input2"],
                "/tmp/xhd_goal5422/out/author_county_zcta_bounded.json",
                "/tmp/xhd_goal5422/out/rtdl_county_zcta_bounded_triton_summary.json",
            ),
        },
        "comparison": {
            "prior_abs_diff": author["abs_diff"],
            "tolerance": author["tolerance"],
            "prior_matched": author["matched"],
        },
        "packet_status": "planned_not_executed",
    }


def _water_bg_row(goal5307: dict[str, Any]) -> dict[str, Any]:
    input_info = goal5307["input"]
    author = goal5307["author"]
    rtdl = goal5307["rtdl"]
    comparison = goal5307["comparison"]
    phases = goal5307["run_phases"]
    remote_input1 = "/tmp/xhd_goal5306/data/USADetailedWaterBodies_arcgis_bounded.wkt"
    remote_input2 = "/tmp/xhd_goal5306/data/USACensusBlockGroupBoundaries_arcgis_bounded.wkt"
    return {
        "case_id": "water_bg_bounded",
        "paper_pair": input_info["paper_pair"],
        "category": "geo_bounded",
        "input_identity_level": "level_b_bounded_geo_fixture",
        "input_type": "wkt",
        "n_dims": 2,
        "remote_inputs": {
            "input1": remote_input1,
            "input2": remote_input2,
        },
        "expected_point_counts": [input_info["point_count_a"], input_info["point_count_b"]],
        "author": {
            "expected_hd_result": author["HDResult"],
            "prior_author_json": author["json"],
            "prior_running_avg_time_ms": author["Running_AvgTime_ms"],
            "command": _author_command(
                remote_input1,
                remote_input2,
                "/tmp/xhd_goal5422/out/author_water_bg_bounded.json",
            ),
        },
        "rtdl": {
            "expected_hd_result": rtdl["HDResult"],
            "prior_route_sec": phases["rtdl_route_sec"],
            "prior_total_sec": phases["rtdl_total_sec"],
            "route": rtdl["route"],
            "partner": rtdl["partner"],
            "triton_strategy": rtdl["triton_strategy"],
            "partner_reference_contract": rtdl["partner_reference_contract"],
            "native_engine_row_contract": rtdl["native_engine_row_contract"],
            "per_source_witness_exact": rtdl["per_source_witness_exact"],
            "command": _rtdl_command(
                remote_input1,
                remote_input2,
                "/tmp/xhd_goal5422/out/author_water_bg_bounded.json",
                "/tmp/xhd_goal5422/out/rtdl_water_bg_bounded_triton_summary.json",
            ),
        },
        "comparison": {
            "prior_abs_diff": comparison["abs_diff"],
            "tolerance": comparison["tolerance"],
            "prior_matched": comparison["matched"],
        },
        "packet_status": "planned_not_executed",
    }


def build_payload() -> dict[str, Any]:
    goal5420 = _load_json(GOAL5420)
    goal5305 = _load_json(GOAL5305)
    goal5307 = _load_json(GOAL5307)

    rows = [_county_row(goal5305), _water_bg_row(goal5307)]
    all_prior_match = all(bool(row["comparison"]["prior_matched"]) for row in rows)
    all_expected_case_ids = [row["case_id"] for row in rows]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5421.bounded_geo_same_pod_packet_plan.v1",
        "goal": "Goal5421",
        "status": "bounded_geo_same_pod_packet_planned__no_execution",
        "matched": bool(goal5420["matched"] and all_prior_match),
        "purpose": (
            "Define the bounded-geo same-POD command packet before any new "
            "execution. This keeps the partner/Triton geo route family separate "
            "from the graphics hd_exec-compatible packet."
        ),
        "pod": {
            "host": POD_HOST,
            "port": POD_PORT,
            "wrapper_required": True,
            "wrapper_command_prefix": (
                f"py scripts/current_pod_ssh.py --host {POD_HOST} --port {POD_PORT} exec"
            ),
            "naked_ssh_allowed": False,
        },
        "execution": {
            "goal5421_executes_pod": False,
            "bounded_geo_matrix_execution_claimed": False,
            "next_execution_goal": "Goal5422_bounded_geo_same_pod_packet_execution",
            "remote_work_dir": "/tmp/xhd_goal5422",
            "remote_output_dir": "/tmp/xhd_goal5422/out",
            "setup_commands": [
                "mkdir -p /tmp/xhd_goal5422/out",
            ],
        },
        "rows": rows,
        "row_count": len(rows),
        "case_ids": all_expected_case_ids,
        "claim_boundary": {
            "bounded_geo_packet_plan_claimed": True,
            "bounded_geo_execution_claimed": False,
            "level_b_bounded_geo_correctness_claimed_from_prior_evidence": all_prior_match,
            "figure5_reproduction_claimed": False,
            "geo_figure5_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "denominator_policy": {
            "author_running_avg_time_ms": "record_if_author_json_reports_it",
            "author_process_wall_sec": "record_in_goal5422_execution_only",
            "rtdl_route_sec": "record_in_goal5422_execution_only",
            "rtdl_total_sec": "record_in_goal5422_execution_only",
            "ratio_authorized": False,
            "reason": (
                "Author internal timing, author process wall, RTDL route wall, "
                "and RTDL total are separate denominators."
            ),
        },
        "source_artifacts": {
            "goal5420": str(GOAL5420),
            "goal5305": str(GOAL5305),
            "goal5307": str(GOAL5307),
        },
        "forbidden_summaries": [
            "Geo Figure 5 reproduced",
            "bounded geo execution completed by Goal5421",
            "County-ZCTA or WaterBodies-BG are exact paper inputs",
            "author-vs-RTDL performance ratio is available",
            "RTDL reproduces the author X-HD RT-core algorithm on geo",
            "explicit -lb has been reopened",
        ],
        "recommended_next_goal": "Goal5422_bounded_geo_same_pod_packet_execution",
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
