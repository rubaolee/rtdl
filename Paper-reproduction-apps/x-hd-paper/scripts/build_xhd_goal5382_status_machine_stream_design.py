"""Build Goal5382 X-HD active-query status-stream design packet.

This is a design/decision packet. It does not implement a native backend.
The packet captures the next generic RTDL contract required after Goal5381
proved that current cell-MBR frontier rows plus the CPU bridge do not match the
author `-lb` offload denominator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5382_status_machine_stream_design.json"
)


AUTHOR_OFFLOAD_ROWS = 27_133_990
RTDL_BRIDGE_OFFLOAD_ROWS = 2_188_225
ACTIVE_QUERY_COUNT = 437_645
BRIDGE_CANDIDATE_ROWS = 13_129_392
AUTHOR_WIDTH_BYTES = 217_071_920
RTDL_BRIDGE_WIDTH_BYTES = 17_505_800


def build_packet() -> dict[str, Any]:
    row_ratio = RTDL_BRIDGE_OFFLOAD_ROWS / AUTHOR_OFFLOAD_ROWS
    return {
        "schema": "rtdl.xhd.goal5382.native_status_machine_stream_design.v1",
        "goal": "Goal5382",
        "status": "design_ready_review_pending",
        "exit_label": "native_status_machine_stream_design_ready__explicit_lb_still_fail_closed",
        "purpose": (
            "Define the generic native active-query status-stream contract that "
            "must exist before RTDL can claim author-compatible explicit -lb "
            "row-denominator parity."
        ),
        "prior_evidence": {
            "goal5374_author_oracle": {
                "active_in_queue_size": ACTIVE_QUERY_COUNT,
                "status_init_count": ACTIVE_QUERY_COUNT,
                "offloading_size": AUTHOR_OFFLOAD_ROWS,
                "raw_offload_rows_before_sort_reduce": AUTHOR_OFFLOAD_ROWS,
                "status_offloading_append_count": AUTHOR_OFFLOAD_ROWS,
                "raw_offload_rows_author_width_bytes": AUTHOR_WIDTH_BYTES,
                "status_cmax2_mbr_abort_count": 0,
                "status_point_loop_early_break_count": 0,
            },
            "goal5381_current_bridge_probe": {
                "active_query_count": ACTIVE_QUERY_COUNT,
                "candidate_row_count": BRIDGE_CANDIDATE_ROWS,
                "bridge_offload_row_count": RTDL_BRIDGE_OFFLOAD_ROWS,
                "rtdl_bridge_width_bytes": RTDL_BRIDGE_WIDTH_BYTES,
                "row_ratio_rtdl_div_author": row_ratio,
                "row_count_parity": False,
                "author_width_byte_parity": False,
            },
            "finding": (
                "The active-query count aligns, but the current native frontier "
                "stream plus active-query bridge emits only about 8.06 percent "
                "of the author offload rows. The current frontier stream is not "
                "the author-compatible raw status-machine stream."
            ),
        },
        "design_decision": {
            "selected_direction": "define_generic_native_active_query_status_stream",
            "rejected_directions": [
                {
                    "direction": "vectorize_cpu_active_query_bridge_first",
                    "reason": (
                        "Bridge runtime is secondary while row-count parity is "
                        "false. A faster bridge would still consume the wrong "
                        "row denominator."
                    ),
                },
                {
                    "direction": "more_scalar_radius_or_branch_order_probes",
                    "reason": (
                        "Goal5375-5377 already ruled out the known under-count, "
                        "over-count, global-bound, and heavy-before-inline-prune "
                        "surfaces."
                    ),
                },
                {
                    "direction": "xhd_specific_native_lb_kernel",
                    "reason": (
                        "RTDL core must remain generic. Paper-specific option "
                        "mapping and oracle comparison belong to the X-HD app."
                    ),
                },
            ],
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "figure7_or_figure11_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
        "required_native_stream": {
            "contract": "generic_active_query_status_stream_v1",
            "owner": "rtdl_core_generic_contract",
            "app_semantics": "none",
            "stream_kind": (
                "active-query status transitions for traversal plus continuation "
                "pipelines"
            ),
            "required_emission_point": (
                "emit raw active-query status transitions before current RTDL "
                "frontier output drops, collapses, sorts, uniques, or filters "
                "rows in a way that loses offload denominator information"
            ),
            "minimum_columns": [
                "active_queue_index",
                "query_row_id",
                "query_point_id",
                "cell_id",
                "point_begin_offset",
                "point_count",
                "min_distance",
                "max_distance",
                "current_best_distance",
                "status_code",
            ],
            "optional_columns": [
                "nearest_item_id",
                "current_best_item_id",
                "iteration_index",
                "continuation_round",
            ],
            "status_codes": [
                "inline_resolved",
                "offload",
                "miss",
                "completed",
                "aborted",
                "pruned",
            ],
            "required_telemetry": [
                "active_query_count",
                "raw_status_row_count",
                "offload_row_count",
                "miss_row_count",
                "completed_row_count",
                "aborted_row_count",
                "peak_status_row_count",
                "row_capacity",
                "overflowed",
            ],
            "fail_closed_rules": [
                "overflow must return no partial row table unless an explicit telemetry-only mode is requested",
                "unknown status codes must raise",
                "row_count_parity must be false until compared against an app-owned oracle",
                "paper option names must not appear in RTDL core symbol or column names",
            ],
        },
        "xhd_app_mapping": {
            "owner": "x-hd-paper app",
            "allowed_app_tasks": [
                "map author -lb option to a generic status-stream mode",
                "compare offload_row_count against Goal5374 OffloadingSize",
                "map generic raw status rows to author-width bytes for Figure 11 diagnostics",
                "decide whether explicit -lb remains fail-closed",
            ],
            "not_core_tasks": [
                "author-specific status enum names",
                "paper figure wording",
                "hd_exec JSON formatting",
                "dataset-specific tolerance decisions",
            ],
        },
        "implementation_plan": [
            {
                "goal": "Goal5383",
                "task": (
                    "Add a generic native status-stream prototype or new mode "
                    "that returns raw active-query status columns and telemetry."
                ),
                "pod_required": True,
                "acceptance": [
                    "focused synthetic non-X-HD status-stream test passes",
                    "X-HD Dragon -> AsianDragon row-count probe reports active_query_count parity",
                    "offload_row_count is compared to Goal5374 author oracle",
                    "no explicit -lb claim unless row_count_parity is true",
                ],
            },
            {
                "goal": "Goal5384",
                "task": (
                    "Optimize bridge/runtime only after status-stream row-count "
                    "semantics are correct."
                ),
                "pod_required": True,
                "acceptance": [
                    "optimization preserves row_count_parity",
                    "timing is reported separately from semantics",
                ],
            },
            {
                "goal": "Goal5385",
                "task": "Refresh X-HD claim matrix and memory after the status-stream outcome.",
                "pod_required": False,
                "acceptance": [
                    "explicit -lb support is either proven or closed fail-closed",
                    "Figure 7/Figure 11 claims remain unauthorized unless same-denominator gates pass",
                ],
            },
        ],
        "forbidden_claims": [
            "explicit -lb support",
            "author OffloadingSize parity",
            "Figure 7 reproduction",
            "Figure 11 memory parity",
            "same-denominator performance ratio",
            "full X-HD paper reproduction",
            "X-HD-specific native RTDL primitive",
        ],
        "allowed_summary": (
            "Goal5382 defines the generic native active-query status-stream "
            "contract required after Goal5381 showed the current frontier stream "
            "under-counts author offload rows by about 12.4x. It authorizes a "
            "generic status-stream prototype next, while keeping explicit -lb "
            "fail-closed until row-count parity is proven."
        ),
    }


def write_packet(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    packet = build_packet()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


if __name__ == "__main__":
    payload = write_packet()
    print(json.dumps({"status": payload["status"], "output": str(DEFAULT_OUTPUT)}, sort_keys=True))
