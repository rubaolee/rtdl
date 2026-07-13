#!/usr/bin/env python3
"""Build Goal5364 bounded lb trace gate author-pair contract evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"

AUTHOR_LB_DIAGNOSTIC = RESULTS / "xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json"
LB_SEMANTICS_AUDIT = RESULTS / "xhd_goal5363_lb_heavy_offload_semantics_audit.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _author_run_summary(run: dict[str, Any]) -> dict[str, Any]:
    iteration = run["iteration_3"]
    return {
        "lb": int(run["lb"]),
        "hd_result": float(run["hd_result"]),
        "running_avg_time_ms": float(run["running_avg_time_ms"]),
        "process_wall_sec": float(run["process_wall_sec"]),
        "large_cells": int(run["large_cells"]),
        "memory": {
            "WL": int(run["memory"]["WL"]),
            "WL Heavy Peak": int(run["memory"]["WL Heavy Peak"]),
        },
        "iteration_3": {
            "RTTime_ms": float(iteration["rt_time_ms"]),
            "CUDATime_ms": float(iteration["cuda_time_ms"]),
            "OffloadingSize": int(iteration["offloading_size"]),
            "ComparedPoints": int(iteration["compared_points"]),
            "Hits": int(iteration["hits"]),
            "NumInputPoints": int(iteration["num_input_points"]),
            "NumOutputPoints": int(iteration["num_output_points"]),
            "Radius": float(iteration["radius"]),
        },
    }


def build_artifact() -> dict[str, Any]:
    author = _load_json(AUTHOR_LB_DIAGNOSTIC)
    audit = _load_json(LB_SEMANTICS_AUDIT)
    lb0 = _author_run_summary(author["author_runs"]["lb_0"])
    lb256 = _author_run_summary(author["author_runs"]["lb_256"])

    author_pair_valid = (
        lb0["lb"] == 0
        and lb256["lb"] == 256
        and lb0["hd_result"] == lb256["hd_result"]
        and lb0["large_cells"] == 0
        and lb0["memory"]["WL Heavy Peak"] == 0
        and lb0["iteration_3"]["OffloadingSize"] == 0
        and lb256["large_cells"] > 0
        and lb256["memory"]["WL Heavy Peak"] > 0
        and lb256["iteration_3"]["OffloadingSize"] > 0
    )
    semantics_ready = bool(audit["comparison"]["matched"]) and not bool(
        audit["semantic_mapping_decision"]["lb_option_supported_now"]
    )

    rtdl_counterpart_contract = {
        "status": "required_not_yet_run",
        "input_scope_must_match_author_pair": {
            "input1": author["input_scope"]["input1"],
            "input2": author["input_scope"]["input2"],
            "input1_num_points": author["input_scope"]["input1_num_points"],
            "input2_num_points": author["input_scope"]["input2_num_points"],
            "exact_paper_dataset_identity_proven": False,
            "level": author["level"],
        },
        "required_runs": [
            {
                "label": "rtdl_lb0_disabled_offload_counterpart",
                "candidate_rtdl_control": {
                    "author_lb": 0,
                    "max_inline_points_mapping": "disable_offload_for_all_cells",
                    "acceptable_implementation": (
                        "Use a threshold larger than every cell point count or an "
                        "explicit disabled-offload mode; record the exact mechanism."
                    ),
                },
                "must_match_author_fields": {
                    "HDResult": lb0["hd_result"],
                    "OffloadingSize": 0,
                    "WL Heavy Peak": 0,
                },
            },
            {
                "label": "rtdl_lb256_heavy_offload_counterpart",
                "candidate_rtdl_control": {
                    "author_lb": 256,
                    "max_inline_points_mapping": 256,
                    "offload_rule": "cell_point_count > max_inline_points",
                },
                "must_match_author_fields": {
                    "HDResult": lb256["hd_result"],
                    "OffloadingSize_positive": True,
                    "WL Heavy Peak_positive": True,
                },
            },
        ],
        "comparison_rules": {
            "hd_result": "exact_or_tolerance_equal_per_run",
            "lb0_offload": "must_be_zero",
            "lbN_offload": "must_be_positive_when_author_positive",
            "denominators": (
                "RTDL may separately report generic bytes and author-width "
                "uint32-equivalent bytes; any ratio requires same denominator."
            ),
            "performance": "not_compared_by_this_gate",
        },
        "current_reason_missing": (
            "Goal5296 produced an author-side lb=0/lb=256 pair only. No RTDL "
            "same-input lb0/lb256 counterpart artifact exists yet."
        ),
    }

    matched = bool(author_pair_valid and semantics_ready)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5364.lb_trace_gate_author_pair_contract.v1",
        "goal": "Goal5364",
        "date": "2026-07-09",
        "status": (
            "bounded_lb_trace_gate_author_pair_ready__rtdl_counterpart_missing"
            if matched
            else "bounded_lb_trace_gate_author_pair_incomplete"
        ),
        "purpose": (
            "Promote the existing Level-B author-only lb=0/lb=256 diagnostic "
            "into an explicit bounded trace-gate contract for the next RTDL "
            "counterpart run, without claiming -lb support yet."
        ),
        "input_artifacts": {
            "author_lb_diagnostic": str(AUTHOR_LB_DIAGNOSTIC),
            "lb_semantics_audit": str(LB_SEMANTICS_AUDIT),
        },
        "author_pair": {
            "status": "ready" if author_pair_valid else "invalid",
            "level": author["level"],
            "input_scope": author["input_scope"],
            "lb_0": lb0,
            "lb_256": lb256,
            "comparison": author["comparison"],
            "claim_boundary_from_source": author["claim_boundary"],
        },
        "rtdl_counterpart_contract": rtdl_counterpart_contract,
        "decision": {
            "author_pair_ready": bool(author_pair_valid),
            "rtdl_counterpart_run_available": False,
            "explicit_lb_support_authorized": False,
            "figure7_reproduced": False,
            "figure11_reproduced": False,
            "next_gate": "run_rtdl_lb0_lb256_counterpart_on_same_level_b_input",
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "comparison": {
            "matched": matched,
            "author_pair_valid": bool(author_pair_valid),
            "semantics_audit_ready": bool(semantics_ready),
            "rtdl_counterpart_missing": True,
        },
        "exit_label": "bounded_lb_trace_gate_author_pair_ready__next_run_rtdl_counterpart",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5364_lb_trace_gate_author_pair_contract.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
