#!/usr/bin/env python3
"""Frozen scientific shape for the Goal5776 real-scale V2/V4 matrix.

This module contains no application implementation and launches no worker.  It
defines the exact execution units, statistical rows, lifecycle boundaries and
round-major schedule that the later controller, evaluator and independent
recount must all agree on.

The central fairness rule is deliberately simple: the ``cold`` timer starts at
the same user-visible input path for either method, so immutable file loading
is included on both sides rather than being silently charged to only one side.
The ``prepared`` timer starts after that method's loading and preparation, with
both observations reported separately rather than called free.  Either timer
ends only after the same canonical application output and mandatory behavioral
traversal receipt have been materialized.  The correctness comparator runs
outside the timer.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
METHODS = (V2, V4)

COLD = "installed_cold_compile_prepare_execute"
PREPARED = "prepared_first_execute"
LIFECYCLES = (COLD, PREPARED)

PAIR_COUNT = 8
FORMAL_WORKER_TIMEOUT_SECONDS = 1_800
RAYJOIN_BATCHES = tuple(f"batch{index}" for index in range(6))

RTDBSCAN_CASES = (
    "locked12",
    "endpoint_exact",
    "endpoint_below",
    "endpoint_above",
    "duplicate_pair",
    "grid3_sparse",
    "grid3_dense",
    "grid4_sparse",
    "grid4_dense",
    "grid6_sparse",
    "grid6_dense",
    "grid8_sparse",
    "grid8_dense",
    "grid10_sparse",
    "grid10_dense",
    "float32_sqrt_rounding_counterexample",
    "nx2_zero_z_lift",
    "goal5776_clustered3d_4096",
)


@dataclass(frozen=True)
class ExecutionUnit:
    unit_id: str
    app: str
    paper_algorithm: str
    workload: str
    statistical_suffixes: tuple[str, ...] = ("complete",)
    cold_statistical_suffixes: tuple[str, ...] | None = None
    prepared_statistical_suffixes: tuple[str, ...] | None = None
    input_scale: str = ""
    input_identity_level: str = ""
    supported_lifecycles: tuple[str, ...] = LIFECYCLES
    v4_numba_leaf_cache_required: bool = True

    @property
    def statistical_row_ids(self) -> tuple[str, ...]:
        return tuple(
            f"{self.unit_id}::{suffix}" for suffix in self.statistical_suffixes
        )

    def statistical_row_ids_for(self, lifecycle: str) -> tuple[str, ...]:
        if lifecycle not in self.supported_lifecycles:
            return ()
        if lifecycle == COLD and self.cold_statistical_suffixes is not None:
            suffixes = self.cold_statistical_suffixes
        elif lifecycle == PREPARED and self.prepared_statistical_suffixes is not None:
            suffixes = self.prepared_statistical_suffixes
        elif lifecycle in LIFECYCLES:
            suffixes = self.statistical_suffixes
        else:
            raise ValueError(f"unknown lifecycle: {lifecycle}")
        return tuple(f"{self.unit_id}::{suffix}" for suffix in suffixes)


def _units() -> tuple[ExecutionUnit, ...]:
    triangle = tuple(
        ExecutionUnit(
            unit_id=f"triangle__{dataset.lower().replace('-', '_')}__{algorithm.lower().replace('-', '_')}",
            app="triangle_counting",
            paper_algorithm=algorithm,
            workload=dataset,
            input_scale="official SNAP graph; exact author count",
            input_identity_level="official_snap_graph_bytes__exact_author_count",
        )
        for dataset in ("com-dblp", "cit-Patents", "soc-LiveJournal1")
        for algorithm in ("RT-1A2", "RT-2A1")
    )
    rtdbscan = tuple(
        ExecutionUnit(
            unit_id=f"rtdbscan__{case_id}",
            app="rt_dbscan",
            paper_algorithm="bounded_radius_graph_component_partition",
            workload=case_id,
            input_scale=(
                "frozen real-scale clustered3d capacity case; point_count = 4096"
                if case_id == "goal5776_clustered3d_4096"
                else "frozen correctness case; point_count <= 4096"
            ),
            input_identity_level=(
                "deterministic_public_benchmark_family_capacity_case__not_paper_dataset"
                if case_id == "goal5776_clustered3d_4096"
                else "frozen_exact_correctness_case__not_real_scale_performance_authority"
            ),
        )
        for case_id in RTDBSCAN_CASES
    )
    return (
        ExecutionUnit(
            "particle__microfluidics_5000", "particle_tracking",
            "tetrahedral_closest_face_cell_transition",
            "author microfluidics mesh / 5,000 query step",
            input_scale="314,587 mesh points / 1,659,240 cells / 5,000 queries",
            input_identity_level=(
                "public_author_mesh__deterministic_query_recipe__"
                "not_author_random_particle_bytes"
            ),
        ),
        *triangle,
        *rtdbscan,
        ExecutionUnit(
            "rtnn__kitti12m_q4096_k4", "rtnn",
            "exact_ranked_distance_window_topk",
            "KITTI-derived Level-B",
            input_scale="12,000,000 search points / 4,096 queries / K=4",
            input_identity_level=(
                "level_b_same_source_deterministic_recipe__not_exact_paper_input"
            ),
        ),
        ExecutionUnit(
            "xhd__dragon_to_happy", "x_hd",
            "directed_exact_max_of_nearest_witness",
            "Stanford Dragon to Happy Buddha",
            input_scale="437,645 source / 543,652 target points",
            input_identity_level=(
                "public_stanford_meshes_level_b_preprocessed__not_exact_paper_bytes"
            ),
        ),
        ExecutionUnit(
            "rtbh__author_32768", "rt_barneshut",
            "aggregate_hierarchy_inverse_square_scalar_force",
            "author prepared hierarchy/force state",
            input_scale="32,768 bodies / 1,486 hierarchy nodes",
            input_identity_level="author_prepared_state_export",
            v4_numba_leaf_cache_required=False,
        ),
        ExecutionUnit(
            "raydb__ssb_sf10_q11", "raydb",
            "partitioned_triangle_grouped_i64_sum",
            "SSB-SF10 Q1.1 packet",
            input_scale="59,986,052 relational rows / 12 partitions",
            input_identity_level=(
                "deterministic_generated_ssb_sf10_same_bytes__not_exact_paper_input"
            ),
            # The authentic real-scale packet route owns loading, lowering,
            # partition creation and execution in one complete call.  The
            # small fixture owner is not the paper-scale route and may not be
            # substituted to manufacture a prepared comparison.
            supported_lifecycles=(COLD,),
        ),
        ExecutionUnit(
            "librts__parks_point_contains", "librts",
            "aabb_index.point_contains_count",
            "parks.bz2 point contains",
            input_scale="11,544,398 indexed boxes / 100,000 queries",
            input_identity_level="public_parks_dataset_frozen_query_slice",
            v4_numba_leaf_cache_required=False,
        ),
        ExecutionUnit(
            "librts__parks_range_contains", "librts",
            "aabb_index.range_contains_count",
            "parks.bz2 range contains",
            input_scale="11,544,398 indexed boxes / 100,000 queries",
            input_identity_level="public_parks_dataset_frozen_query_slice",
            v4_numba_leaf_cache_required=False,
        ),
        ExecutionUnit(
            "rayjoin__top4_six_batch", "rayjoin",
            "paper_six_batch_planar_overlay",
            "Section-5.7 county x zipcode top4",
            # Cold is one complete six-batch application invocation.  Its
            # shared loading/compile/session setup cannot honestly be copied
            # into six independent row timers.  Prepared execution has six
            # genuinely distinct query batches and therefore six rows.
            statistical_suffixes=RAYJOIN_BATCHES,
            cold_statistical_suffixes=("six_batch_complete",),
            prepared_statistical_suffixes=RAYJOIN_BATCHES,
            input_scale="1,705,027 county edges / 9,982,960 zipcode edges",
            input_identity_level="public_arcgis_same_source_packed_top4_pair",
        ),
    )


UNITS = _units()
UNIT_BY_ID = {unit.unit_id: unit for unit in UNITS}
FORMAL_UNITS = tuple(
    unit for unit in UNITS
    if unit.app != "rt_dbscan"
    or unit.unit_id.endswith("goal5776_clustered3d_4096")
)


def statistical_rows(*, lifecycle: str | None = None) -> tuple[dict[str, str], ...]:
    if lifecycle is not None and lifecycle not in LIFECYCLES:
        raise ValueError(f"unknown lifecycle: {lifecycle}")
    rows = []
    lifecycles: Iterable[str] = LIFECYCLES if lifecycle is None else (lifecycle,)
    for resolved_lifecycle in lifecycles:
        for unit in FORMAL_UNITS:
            if resolved_lifecycle not in unit.supported_lifecycles:
                continue
            for row_id in unit.statistical_row_ids_for(resolved_lifecycle):
                rows.append({
                    "lifecycle": resolved_lifecycle,
                    "unit_id": unit.unit_id,
                    "row_id": row_id,
                    "app": unit.app,
                    "paper_algorithm": unit.paper_algorithm,
                })
    return tuple(rows)


def schedule() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for lifecycle in LIFECYCLES:
        for unit in FORMAL_UNITS:
            if lifecycle not in unit.supported_lifecycles:
                continue
            for pair_index in range(PAIR_COUNT):
                order = METHODS if pair_index % 2 == 0 else tuple(reversed(METHODS))
                for order_ordinal, method in enumerate(order):
                    rows.append({
                        "worker_index": len(rows),
                        "lifecycle": lifecycle,
                        "unit_id": unit.unit_id,
                        "pair_index": pair_index,
                        "order_ordinal": order_ordinal,
                        "method": method,
                    })
    return tuple(rows)


def contract_document() -> dict[str, object]:
    units = [
        {
            "unit_id": unit.unit_id,
            "app": unit.app,
            "paper_algorithm": unit.paper_algorithm,
            "workload": unit.workload,
            "input_scale": unit.input_scale,
            "input_identity_level": unit.input_identity_level,
            "supported_lifecycles": list(unit.supported_lifecycles),
            "v4_numba_leaf_cache_required": unit.v4_numba_leaf_cache_required,
            "statistical_row_ids_by_lifecycle": {
                lifecycle: list(unit.statistical_row_ids_for(lifecycle))
                for lifecycle in LIFECYCLES
            },
        }
        for unit in FORMAL_UNITS
    ]
    schedule_rows = schedule()
    functional_only_units = tuple(
        unit for unit in UNITS if unit not in FORMAL_UNITS)
    unit_lifecycle_count = {
        lifecycle: sum(
            lifecycle in unit.supported_lifecycles for unit in FORMAL_UNITS)
        for lifecycle in LIFECYCLES
    }
    return {
        "schema": "rtdl.goal5776.real_scale_formal_contract.v1",
        "goal": 5776,
        "methods": list(METHODS),
        "lifecycles": list(LIFECYCLES),
        "pair_count_per_unit_lifecycle": PAIR_COUNT,
        "execution_unit_count": len(FORMAL_UNITS),
        "functional_execution_unit_count": len(UNITS),
        "formal_execution_unit_count": len(FORMAL_UNITS),
        "functional_only_rtdbscan_proof_case_count": len(UNITS) - len(FORMAL_UNITS),
        "formal_unit_ids": [unit.unit_id for unit in FORMAL_UNITS],
        "functional_only_unit_ids": [
            unit.unit_id for unit in functional_only_units],
        "formal_unit_lifecycle_count_by_lifecycle": unit_lifecycle_count,
        "formal_unit_lifecycle_count_total": sum(unit_lifecycle_count.values()),
        "worker_count_derivation": (
            "(15 cold unit-lifecycles + 14 prepared unit-lifecycles) "
            "* 8 ABBA pairs * 2 methods = 464"
        ),
        "row_count_derivation": (
            "15 cold rows + 13 ordinary prepared rows + 6 directly timed "
            "RayJoin prepared batch rows = 34"
        ),
        "row_shape_exceptions": {
            "raydb__ssb_sf10_q11": (
                "cold only; no authentic prepared cross-call owner"
            ),
            "rayjoin__top4_six_batch": (
                "one complete cold row; six directly timed prepared batch rows"
            ),
        },
        "independent_row_count_by_lifecycle": {
            lifecycle: len(statistical_rows(lifecycle=lifecycle))
            for lifecycle in LIFECYCLES
        },
        "independent_row_count_total": len(statistical_rows()),
        "formal_worker_count": len(schedule_rows),
        "units": units,
        "timing_contract": {
            "registered_seconds_are_same_worker_mutually_exclusive_phase_sum": True,
            "phase_sum": (
                "cold = load + prepare + execute + teardown; prepared = execute; "
                "RayJoin cold execute is one directly observed complete six-batch wall"
            ),
            "medians_or_nested_phase_observations_may_be_summed": False,
            "cold_immutable_input_loading_inside_timer_for_both_methods": True,
            "prepared_immutable_input_loading_inside_execute_timer": False,
            "timer_start": (
                "at the same user-visible immutable input path for cold; before the "
                "first logical execute after separately reported loading and preparation "
                "for prepared"
            ),
            "timer_end": (
                "after canonical application output and mandatory behavioral traversal "
                "receipt are materialized for both methods, and after method-owned "
                "teardown for the cold lifecycle"
            ),
            "correctness_comparator_inside_timer": False,
            "v2_and_v4_same_endpoint_boundary": True,
            "prepared_work_is_free": False,
            "prepared_work_reported_separately": True,
            "first_build_callback_compilation_reported_separately": True,
            "installed_leaf_cache_may_hide_first_build_cost": False,
            "unsupported_prepared_route_may_be_substituted_from_fixture": False,
        },
        "statistics_contract": {
            "ratio": "v2_direct_seconds / v4_seconds",
            "greater_than_one_favors": V4,
            "summary": "median of eight paired ABBA ratios",
            "bootstrap_draws": 10_000,
            "bootstrap_ci_indices": [249, 9749],
            "row_local_no_slower_gate": "paired_ratio_median >= 1.0",
            "cross_app_compensation_allowed": False,
            "cross_lifecycle_compensation_allowed": False,
            "rayjoin_derived_sum_is_independent": False,
            "fixed_speedup_target_used": False,
        },
        "worker_contract": {
            "fresh_parent_pid_required": True,
            "one_exact_source_native_plan_target_identity": True,
            "predeclared_application_correctness_relation_required": True,
            "behavioral_true_optix_required": True,
            "failed_incomplete_unbound_pending_session_counts_must_be_zero": True,
            "default_may_select_between_application_algorithms": False,
            "retry_resume_replacement_row_drop_relabel_allowed": False,
            "per_worker_timeout_seconds": FORMAL_WORKER_TIMEOUT_SECONDS,
            "worker_timeout_is_terminal_and_not_retried": True,
        },
        "correctness_contract": {
            "claim_language": (
                "126/126 satisfy their predeclared application correctness "
                "relation; not every floating quantity is bitwise equal"
            ),
            "fully_discrete_or_digest_exact_functional_paths": 114,
            "mixed_identity_exact_numeric_tolerance_functional_paths": 12,
            "mixed_relations": {
                "rtnn": "neighbor IDs exact; squared distance abs tolerance 1e-6",
                "x_hd": "source/item witness IDs exact; value abs tolerance 1e-6",
                "rt_barneshut": (
                    "source IDs exact; scalar-force relation uses the frozen "
                    "absolute/relative tolerance comparator"
                ),
            },
        },
        "claim_boundary": {
            "performance_result_exists": False,
            "pod_authorized": False,
            "home_smoke_timings_may_be_used_as_formal_rows": False,
            "cold_may_be_replaced_by_prepared": False,
            "prepared_may_be_called_free": False,
            "paper_dataset_replacement_claimed": False,
        },
    }


def contract_sha256() -> str:
    return hashlib.sha256(json.dumps(
        contract_document(), sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print(json.dumps(contract_document(), indent=2, sort_keys=True))
