from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5372_author_shader_status_machine_gap.json"
AUTHOR_ROOT = Path.home() / "AppData" / "Local" / "Temp" / "xhd-author-src"
AUTHOR_SHADER = AUTHOR_ROOT / "src" / "rt" / "shaders" / "shaders_nn_uniform_grid.cu"
AUTHOR_RT = AUTHOR_ROOT / "src" / "hd_impl" / "hausdorff_distance_rt.h"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_all(text: str, needles: list[str]) -> bool:
    return all(needle in text for needle in needles)


def build_artifact() -> dict[str, Any]:
    goal5369 = _read_json(RESULTS / "xhd_goal5369_lb_queue_state_requirements.json")
    goal5370 = _read_json(RESULTS / "xhd_goal5370_author_like_queue_state_reference.json")
    goal5371 = _read_json(RESULTS / "xhd_goal5371_inline_global_bound_lb_probe.json")

    shader = _read_text(AUTHOR_SHADER)
    rt_impl = _read_text(AUTHOR_RT)

    source_checks = {
        "shader_status_enum": _has_all(
            shader,
            [
                "enum class ShaderStatus",
                "kInit = 1 << 0",
                "kOffloading = 1 << 1",
                "kAborted = 1 << 2",
            ],
        ),
        "payload_layout": _has_all(
            shader,
            [
                "auto in_q_idx = optixGetPayload_0()",
                "auto n_hits = optixGetPayload_1()",
                "auto status = optixGetPayload_3()",
                "optixGetPayload_4()",
            ],
        ),
        "radius_and_cmin2_prune": "min_dist2 > radius * radius || min_dist2 >= get_cmin2()" in shader,
        "cmax2_abort_branch": _has_all(
            shader,
            [
                "max_dist2 <= *params.cmax2",
                "update_status(ShaderStatus::kAborted)",
            ],
        ),
        "heavy_offload_append_branch": _has_all(
            shader,
            [
                "np_in_cell > params.processing_threshold",
                "offloading_point_ids.Append(in_q_idx)",
                "params.offloading_cell_ids[tail] = mbr_id",
                "update_status(ShaderStatus::kOffloading)",
            ],
        ),
        "point_loop_early_break_branch": _has_all(
            shader,
            [
                "dist2 <= *params.cmax2",
                "optixSetPayload_2(optixGetPayload_2() + (offset - begin + 1))",
                "update_status(ShaderStatus::kAborted)",
            ],
        ),
        "raygen_post_status_mapping": _has_all(
            shader,
            [
                "params.cmin2[i] = INVALID_DISTANCE",
                "params.cmin2[i] = cmin2",
                "atomicMax(params.cmax2, cmin2)",
                "params.miss_queue.Append(point_id_a)",
            ],
        ),
        "lb_option_threshold_semantics": _has_all(
            rt_impl,
            [
                "processing_threshold = config_.lb",
                "processing_threshold = std::numeric_limits<uint32_t>::max()",
                "Load-balancing is disabled",
            ],
        ),
        "offloading_size_is_pre_lb_processing_queue_size": _has_all(
            rt_impl,
            [
                "auto offloading_size = offloading_point_ids_.size(stream)",
                "total_offloading_size += offloading_size",
                'json_iter["OffloadingSize"] = total_offloading_size',
                "loadBalanceProcessing",
            ],
        ),
        "load_balance_restores_shader_cmin2": _has_all(
            rt_impl,
            [
                "curr_cmin2 = cmin2[idx_in_queue]",
                "early_break = curr_cmin2 == INVALID_DISTANCE",
                "min_dist2 >= curr_cmin2",
                "early_break = max_dist2 <= *p_cmax2",
                "atomicMax(p_cmax2, curr_cmin2)",
            ],
        ),
    }

    if not all(source_checks.values()):
        missing = [name for name, ok in source_checks.items() if not ok]
        raise RuntimeError(f"Author source checks failed: {missing}")

    author_rows = int(goal5371["comparison"]["author_offloading_size_rows"])
    inline_rows = int(goal5371["comparison"]["rtdl_author_radius_inline_count_only_kind2_rows"])
    raw_rows = int(goal5371["comparison"]["rtdl_author_radius_noinline_raw_kind2_rows_from_goal5368"])
    return {
        "goal": "Goal5372",
        "date": "2026-07-09",
        "schema": "rtdl.paper_reproduction.xhd.goal5372.author_shader_status_machine_gap.v1",
        "status": "author_shader_status_machine_gap_matrix_ready__implementation_or_author_instrumentation_next",
        "exit_label": "status_machine_requirements_ready__lb_support_still_unauthorized",
        "purpose": (
            "Pin the author X-HD RT shader payload/status-machine semantics that "
            "control lb OffloadingSize, and map them against the current RTDL "
            "telemetry gaps before any explicit -lb support is attempted."
        ),
        "source_evidence": {
            "author_shader": str(AUTHOR_SHADER),
            "author_rt_impl": str(AUTHOR_RT),
            "checks": source_checks,
        },
        "author_status_machine": {
            "payload_fields": [
                {"payload": 0, "name": "in_q_idx", "meaning": "index into the active author in_queue"},
                {"payload": 1, "name": "n_hits", "meaning": "visited cell hit count"},
                {"payload": 2, "name": "n_compared_pairs", "meaning": "point comparisons performed in shader"},
                {"payload": 3, "name": "status", "meaning": "bitmask: kInit / kOffloading / kAborted"},
                {"payload": "4/5", "name": "cmin2", "meaning": "per-active-source current best squared distance"},
            ],
            "status_bits": {
                "kInit": 1,
                "kOffloading": 2,
                "kAborted": 4,
            },
            "critical_branches": [
                {
                    "name": "radius_or_cmin2_prune",
                    "predicate": "min_dist2 > radius^2 OR min_dist2 >= cmin2",
                    "effect": "return without offload append and without row emission",
                },
                {
                    "name": "cmax2_mbr_abort",
                    "predicate": "max_dist2 <= global cmax2",
                    "effect": "update cmin2 with max_dist2, set kAborted, terminate ray",
                },
                {
                    "name": "heavy_cell_offload",
                    "predicate": "cell_point_count > processing_threshold",
                    "effect": "append (in_q_idx, cell_id), set kOffloading, return",
                },
                {
                    "name": "point_loop_early_break",
                    "predicate": "point distance <= global cmax2",
                    "effect": "increment compared-pair payload, set kAborted, terminate ray",
                },
                {
                    "name": "valid_complete_source",
                    "predicate": "not aborted, not offloaded, cmin2 finite",
                    "effect": "atomicMax global cmax2 with cmin2",
                },
                {
                    "name": "miss_source",
                    "predicate": "not aborted, not offloaded, cmin2 remains infinity",
                    "effect": "append point_id_a to miss_queue",
                },
            ],
            "load_balance_followup": [
                "offload rows are sorted by in_q_idx",
                "offload rows are reduced/grouped by in_q_idx before CUDA processing",
                "loadBalanceProcessing restores shader-computed cmin2 by idx_in_queue",
                "loadBalanceProcessing can early-break against global cmax2",
                "valid load-balance current best can update global cmax2",
            ],
        },
        "rtdl_current_evidence": {
            "author_offloading_size_rows": author_rows,
            "rtdl_author_radius_inline_count_only_kind2_rows": inline_rows,
            "rtdl_author_radius_inline_global_bound_kind2_rows": int(
                goal5371["comparison"]["rtdl_author_radius_inline_global_bound_kind2_rows"]
            ),
            "rtdl_author_radius_noinline_raw_kind2_rows": raw_rows,
            "inline_div_author": inline_rows / author_rows,
            "noinline_div_author": raw_rows / author_rows,
            "global_bound_early_break_count": int(
                goal5371["probe_results"]["inline_global_bound_count_only"][
                    "global_bound_early_break_count"
                ]
            ),
            "queue_state_reference_available": bool(goal5370["comparison"]["matched"]),
            "queue_requirements_gate_available": goal5369["next_gate_contract"]["name"],
        },
        "gap_matrix": [
            {
                "author_semantic": "active in_queue index namespace",
                "author_source": "payload_0 is in_q_idx; offload rows append in_q_idx",
                "rtdl_current_status": "missing for Dragon -> AsianDragon lb trace",
                "needed_next": "emit/count raw offload rows in the same active queue index space",
            },
            {
                "author_semantic": "dynamic per-source cmin2",
                "author_source": "payload_4/5 carries cmin2; shader and loadBalanceProcessing update it",
                "rtdl_current_status": "bounded state shape exists; large lb trace cmin2 is missing",
                "needed_next": "carry current_best_sq/cmin2 into raw offload counting and record its source",
            },
            {
                "author_semantic": "cmax2 abort status",
                "author_source": "max_dist2 <= cmax2 sets kAborted and later stores INVALID_DISTANCE",
                "rtdl_current_status": "existing global-bound flag does not fire in Goal5371",
                "needed_next": "separate cmax2_mbr_abort_count from generic global-bound early-break",
            },
            {
                "author_semantic": "heavy-cell offload append",
                "author_source": "np_in_cell > processing_threshold appends (in_q_idx, cell_id)",
                "rtdl_current_status": "generic kind2 counts exist but denominator does not match",
                "needed_next": "count raw append events after author prune/abort/status checks",
            },
            {
                "author_semantic": "loadBalanceProcessing grouping",
                "author_source": "sort/reduce offload rows by in_q_idx, restore cmin2, process offloaded cells",
                "rtdl_current_status": "not represented in current count-only probe",
                "needed_next": "report raw rows before sort/reduce and grouped active-point count separately",
            },
            {
                "author_semantic": "miss queue",
                "author_source": "complete source with infinite cmin2 appends point_id_a to miss_queue",
                "rtdl_current_status": "not present in lb count probes",
                "needed_next": "report miss_count and next in_queue size if reconstructing full iteration",
            },
        ],
        "next_gate_contract": {
            "name": "author_shader_status_machine_lb_trace",
            "minimum_fields": [
                "active_in_queue_size",
                "raw_offload_rows_before_sort_reduce",
                "raw_offload_rows_author_width_bytes",
                "status_count_init",
                "status_count_offloading",
                "status_count_aborted",
                "miss_queue_count",
                "cmax2_mbr_abort_count",
                "point_loop_early_break_count",
                "current_best_state_source",
                "row_count_parity_against_author_offloading_size",
            ],
            "implementation_options": [
                "generic RTDL experimental status-machine probe over cell-MBR traversal",
                "author instrumentation that dumps raw offload rows and per-source status/cmin2 oracle",
            ],
            "success_exit_label": "author_status_machine_lb_denominator_compared",
            "failure_exit_label": "author_status_machine_requires_deeper_instrumentation",
        },
        "claim_boundary": {
            "status_machine_gap_matrix_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "input_artifacts": {
            "goal5369": str(RESULTS / "xhd_goal5369_lb_queue_state_requirements.json"),
            "goal5370": str(RESULTS / "xhd_goal5370_author_like_queue_state_reference.json"),
            "goal5371": str(RESULTS / "xhd_goal5371_inline_global_bound_lb_probe.json"),
        },
    }


def main() -> None:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, sort_keys=True))


if __name__ == "__main__":
    main()
