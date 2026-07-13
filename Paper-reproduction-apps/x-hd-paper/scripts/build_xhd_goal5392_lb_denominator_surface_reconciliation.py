from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5392_lb_denominator_surface_reconciliation.json"

GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5391 = RESULTS / "xhd_goal5391_lb_fanout_semantics.json"
GOAL5375 = RESULTS / "xhd_goal5375_rtdl_status_machine_counterpart_assessment.json"
GOAL5377_DEFAULT = RESULTS / "xhd_goal5377_default_status_probe_pod.json"
GOAL5377_HEAVY = RESULTS / "xhd_goal5377_heavy_before_inline_prune_probe_pod.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _division(row_count: int, active_count: int) -> dict[str, Any]:
    quotient, remainder = divmod(row_count, active_count)
    return {
        "row_count": row_count,
        "active_query_count": active_count,
        "rows_per_active_average": row_count / active_count,
        "integer_multiple": remainder == 0,
        "rows_per_active_integer_if_exact": quotient if remainder == 0 else None,
        "remainder": remainder,
    }


def _surface(
    *,
    name: str,
    row_count: int,
    active_count: int,
    author_rows: int,
    category: str,
    status: str,
    source_artifacts: list[str],
    interpretation: str,
    raw_author_denominator_candidate: bool,
) -> dict[str, Any]:
    delta = author_rows - row_count
    return {
        "name": name,
        "category": category,
        "status": status,
        "row_count": row_count,
        "active_query_count": active_count,
        "division": _division(row_count, active_count),
        "row_delta_author_minus_surface": delta,
        "absolute_row_delta": abs(delta),
        "row_ratio_surface_div_author": row_count / author_rows,
        "raw_author_denominator_candidate": raw_author_denominator_candidate,
        "source_artifacts": source_artifacts,
        "interpretation": interpretation,
    }


def _candidate_by_name(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for candidate in payload["candidate_counterparts"]:
        if candidate["name"] == name:
            return candidate
    raise KeyError(name)


def build(output: Path = OUT) -> dict[str, Any]:
    author_payload = _read_json(GOAL5387)
    goal5391 = _read_json(GOAL5391)
    goal5375 = _read_json(GOAL5375)
    goal5377_default = _read_json(GOAL5377_DEFAULT)
    goal5377_heavy = _read_json(GOAL5377_HEAVY)

    author_trace = author_payload["author_lb_trace_v2"]
    active_count = int(author_trace["active_in_queue_size"])
    author_rows = int(author_trace["raw_offload_rows_before_sort_reduce"])
    author_hash = int(author_trace["batch_0"]["raw_offload_row_hash"])

    bridge_rows = int(goal5391["rtdl_denominator"]["raw_offload_rows"])
    default_candidate = _candidate_by_name(goal5375, "author_radius_inline_kind2_current_surface")
    inline_global_candidate = _candidate_by_name(
        goal5375, "author_radius_inline_global_bound_kind2_current_surface"
    )
    full_cover_candidate = _candidate_by_name(
        goal5375, "goal5365_full_cover_lb256_behavior_gate_surface"
    )
    noinline_candidate = _candidate_by_name(goal5375, "author_radius_noinline_raw_kind2_current_surface")

    default_rows = int(default_candidate["raw_offload_rows_before_sort_reduce"])
    inline_global_rows = int(inline_global_candidate["raw_offload_rows_before_sort_reduce"])
    full_cover_rows = int(full_cover_candidate["raw_offload_rows_before_sort_reduce"])
    noinline_rows = int(noinline_candidate["raw_offload_rows_before_sort_reduce"])
    heavy_rows = int(goal5377_heavy["comparison_to_author"]["rtdl_raw_frontier_kind2_rows"])

    surfaces = [
        _surface(
            name="current_bridge_materialized_offload_rows",
            row_count=bridge_rows,
            active_count=active_count,
            author_rows=author_rows,
            category="post_bridge_materialized_offload",
            status="fails_author_raw_denominator",
            raw_author_denominator_candidate=False,
            source_artifacts=[str(GOAL5391)],
            interpretation=(
                "Goal5390/5391 bridge output proves full-source active-query "
                "plumbing is not source-limited, but this surface is much smaller "
                "than the author raw offload stream and is not the sole native "
                "implementation target."
            ),
        ),
        _surface(
            name="default_inline_raw_kind2_count",
            row_count=default_rows,
            active_count=active_count,
            author_rows=author_rows,
            category="native_raw_kind2_count_only",
            status="undercounts_author_raw_denominator",
            raw_author_denominator_candidate=True,
            source_artifacts=[str(GOAL5375), str(GOAL5377_DEFAULT)],
            interpretation=(
                "Raw kind2 telemetry is closer to the author raw row count than "
                "the bridge surface, but it still misses by millions of rows and "
                "lacks author status-machine transition identity."
            ),
        ),
        _surface(
            name="inline_global_bound_raw_kind2_count",
            row_count=inline_global_rows,
            active_count=active_count,
            author_rows=author_rows,
            category="native_raw_kind2_count_only",
            status="same_as_default_global_bound_does_not_explain_gap",
            raw_author_denominator_candidate=True,
            source_artifacts=[str(GOAL5375)],
            interpretation=(
                "Existing RTDL global-bound early break does not change this "
                "raw kind2 denominator, so it is not a proxy for the author's "
                "cmax2/status-machine behavior."
            ),
        ),
        _surface(
            name="full_cover_lb256_behavior_gate_surface",
            row_count=full_cover_rows,
            active_count=active_count,
            author_rows=author_rows,
            category="closest_prior_behavior_surface",
            status="closest_prior_surface_but_not_author_semantics",
            raw_author_denominator_candidate=True,
            source_artifacts=[str(GOAL5375)],
            interpretation=(
                "This is the closest prior surface by absolute row-count delta. "
                "It should inform the next design, but it is still not row-count "
                "parity and has not proven author raw status-transition identity."
            ),
        ),
        _surface(
            name="noinline_or_heavy_before_raw_kind2_overcount",
            row_count=max(noinline_rows, heavy_rows),
            active_count=active_count,
            author_rows=author_rows,
            category="native_raw_kind2_overcount",
            status="overcounts_author_raw_denominator",
            raw_author_denominator_candidate=True,
            source_artifacts=[str(GOAL5375), str(GOAL5377_HEAVY)],
            interpretation=(
                "Classifying heavy/offload before inline pruning, or removing "
                "inline pruning, overshoots the author denominator by a large "
                "margin. This rejects the simple branch-order explanation."
            ),
        ),
    ]

    closest = min(surfaces, key=lambda item: item["absolute_row_delta"])
    bridge_surface = surfaces[0]
    raw_candidates = [surface for surface in surfaces if surface["raw_author_denominator_candidate"]]
    closest_raw_candidate = min(raw_candidates, key=lambda item: item["absolute_row_delta"])

    return {
        "goal": "Goal5392",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5392.lb_denominator_surface_reconciliation.v1",
        "status": "denominator_surfaces_reconciled__bridge_surface_not_sole_target",
        "exit_label": "lb_denominator_surfaces_reconciled__select_raw_status_target_before_native_work",
        "purpose": (
            "Reconcile all known RTDL -lb row-denominator surfaces against the "
            "Goal5387 author trace v2 oracle before selecting the next native "
            "status-stream implementation target."
        ),
        "input_artifacts": {
            "goal5387_author_trace_v2": str(GOAL5387),
            "goal5391_bridge_fanout": str(GOAL5391),
            "goal5375_counterpart_assessment": str(GOAL5375),
            "goal5377_default_status_probe": str(GOAL5377_DEFAULT),
            "goal5377_heavy_before_inline_probe": str(GOAL5377_HEAVY),
        },
        "author_oracle": {
            "active_in_queue_size": active_count,
            "raw_offload_rows_before_sort_reduce": author_rows,
            "raw_offload_row_hash": author_hash,
            "division": _division(author_rows, active_count),
        },
        "surfaces": surfaces,
        "summary": {
            "surface_count": len(surfaces),
            "bridge_surface_is_sole_target": False,
            "closest_surface_by_absolute_row_delta": closest["name"],
            "closest_raw_denominator_candidate": closest_raw_candidate["name"],
            "bridge_absolute_row_delta": bridge_surface["absolute_row_delta"],
            "closest_raw_candidate_absolute_row_delta": closest_raw_candidate["absolute_row_delta"],
            "bridge_is_farther_from_author_than_closest_raw_candidate": (
                bridge_surface["absolute_row_delta"] > closest_raw_candidate["absolute_row_delta"]
            ),
            "any_surface_has_row_count_parity": any(surface["row_count"] == author_rows for surface in surfaces),
            "any_surface_has_hash_parity": False,
        },
        "decision": {
            "native_implementation_should_start_from": (
                "author_compatible_raw_status_semantics_not_post_bridge_row_count"
            ),
            "next_goal": "generic_status_stream_target_selection_or_fail_closed_closeout",
            "why": (
                "The current bridge surface is the most visibly mismatched "
                "full-source materialized output, but raw-kind2 and full-cover "
                "surfaces are much closer to the author raw denominator. The "
                "next native work must explain and target the raw status stream, "
                "not optimize or hard-code the bridge row count."
            ),
            "bridge_runtime_optimization_rejected_as_next_main_path": True,
            "hardcode_author_rows_per_active_rejected": True,
            "full_cover_promoted_to_correctness_claim": False,
        },
        "claim_boundary": {
            "denominator_surface_reconciliation_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "full_cover_surface_promoted_to_author_semantics": False,
            "bridge_surface_promoted_to_sole_target": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
