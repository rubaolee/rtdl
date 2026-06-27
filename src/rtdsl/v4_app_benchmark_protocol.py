from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v4_app_route_binding import V4_GOAL4652_APP_ORDER
from .v4_app_route_binding import V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON
from .v4_app_route_binding import V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE
from .v4_app_route_binding import V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER
from .v4_app_route_binding import V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR
from .v4_app_route_binding import v4_goal4652_app_route_bindings


V4_GOAL4653_PROTOCOL_STATUS = "goal4653_full_app_level_protocol_frozen_not_run"

V4_PROTOCOL_FULL_APP_CANDIDATE = "full_app_v4_speed_row_candidate"
V4_PROTOCOL_PARTIAL_CONTROL_ONLY = "partial_operator_control_not_app_claim"
V4_PROTOCOL_NO_ROUTE_BLOCKER = "no_v4_route_blocker"
V4_PROTOCOL_DEFERRED_EXCLUDED = "deferred_excluded_with_reason"

V4_PROTOCOL_ROW_TYPES = (
    V4_PROTOCOL_FULL_APP_CANDIDATE,
    V4_PROTOCOL_PARTIAL_CONTROL_ONLY,
    V4_PROTOCOL_NO_ROUTE_BLOCKER,
    V4_PROTOCOL_DEFERRED_EXCLUDED,
)

V4_GOAL4653_PROTOCOL_SOURCE_INPUTS = (
    "future/v4/evidence/v4_goal4652_app_route_binding_matrix_2026-06-25.json",
    "future/v4/evidence/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.json",
    "future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.json",
    "scripts/phoenix_v3_serious_paired_v2x_runner.sh",
)


@dataclass(frozen=True)
class V4Goal4653ProtocolRow:
    app: str
    route_class: str
    protocol_row_type: str
    benchmark_app_frontdoor: str
    v2_14_route: str
    v3_route: str
    v4_route: str
    mapped_v4_operators: tuple[str, ...]
    dataset_scale: str
    warmup: int
    repeat: int
    correctness_contract: str
    denominator: str
    metric_windows: tuple[str, ...]
    pass_fail_bar: dict[str, object]
    claim_class_if_pass: str
    contributes_to_formal_high_performance: bool
    v4_run_required_in_goal4654: bool
    blocker_or_gap: str
    release_claim_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False
    silent_v2_v3_fallback_authorized: bool = False

    def __post_init__(self) -> None:
        if self.app not in V4_GOAL4652_APP_ORDER:
            raise ValueError(f"{self.app}: unexpected app for Goal4653")
        if self.protocol_row_type not in V4_PROTOCOL_ROW_TYPES:
            raise ValueError(f"{self.app}: invalid protocol row type")
        if not self.benchmark_app_frontdoor:
            raise ValueError(f"{self.app}: benchmark app front door must be explicit")
        if not self.v2_14_route or not self.v3_route:
            raise ValueError(f"{self.app}: V2.14 and V3 routes must be explicit")
        if not self.correctness_contract:
            raise ValueError(f"{self.app}: correctness contract must be explicit")
        if not self.denominator:
            raise ValueError(f"{self.app}: denominator must be explicit")
        if not self.metric_windows:
            raise ValueError(f"{self.app}: metric windows must be explicit")
        if not self.pass_fail_bar:
            raise ValueError(f"{self.app}: pass/fail bar must be explicit")
        if not self.blocker_or_gap:
            raise ValueError(f"{self.app}: blocker/gap must be explicit")
        if self.protocol_row_type == V4_PROTOCOL_FULL_APP_CANDIDATE:
            if self.route_class != V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE:
                raise ValueError(f"{self.app}: full app candidate must be fused-operator-addressable")
            if not self.v4_run_required_in_goal4654:
                raise ValueError(f"{self.app}: full app candidate must require V4 run")
            if not self.mapped_v4_operators:
                raise ValueError(f"{self.app}: full app candidate needs mapped V4 operators")
            if not self.contributes_to_formal_high_performance:
                raise ValueError(f"{self.app}: full app candidate must contribute to formal subset if it passes")
        if self.protocol_row_type != V4_PROTOCOL_FULL_APP_CANDIDATE:
            if self.contributes_to_formal_high_performance:
                raise ValueError(f"{self.app}: non-full row cannot contribute to formal high-performance")
            if self.v4_run_required_in_goal4654 and self.protocol_row_type in {
                V4_PROTOCOL_NO_ROUTE_BLOCKER,
                V4_PROTOCOL_DEFERRED_EXCLUDED,
            }:
                raise ValueError(f"{self.app}: blocked/deferred row cannot require V4 run")
        for flag in (
            "release_claim_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "app_specific_native_kernel_authorized",
            "silent_v2_v3_fallback_authorized",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false before Goal4655/4657")

    def as_dict(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "route_class": self.route_class,
            "protocol_row_type": self.protocol_row_type,
            "benchmark_app_frontdoor": self.benchmark_app_frontdoor,
            "v2_14_route": self.v2_14_route,
            "v3_route": self.v3_route,
            "v4_route": self.v4_route,
            "mapped_v4_operators": self.mapped_v4_operators,
            "dataset_scale": self.dataset_scale,
            "warmup": self.warmup,
            "repeat": self.repeat,
            "correctness_contract": self.correctness_contract,
            "denominator": self.denominator,
            "metric_windows": self.metric_windows,
            "pass_fail_bar": self.pass_fail_bar,
            "claim_class_if_pass": self.claim_class_if_pass,
            "contributes_to_formal_high_performance": self.contributes_to_formal_high_performance,
            "v4_run_required_in_goal4654": self.v4_run_required_in_goal4654,
            "blocker_or_gap": self.blocker_or_gap,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
            "silent_v2_v3_fallback_authorized": self.silent_v2_v3_fallback_authorized,
        }


_COMMON_V2_ROUTE = "same-app V2.14 incumbent route from scripts/phoenix_v3_serious_paired_v2x_runner.sh"
_COMMON_V3_ROUTE = "same-app Phoenix V3/current route from scripts/phoenix_v3_serious_paired_v2x_runner.sh"
_COMMON_METRICS = ("wall_seconds", "hot_phase_seconds", "correctness_parity")
_FULL_SPEED_BAR = {
    "correctness_parity_required": True,
    "v4_vs_v2_14_wall_speedup_min": 1.20,
    "v4_vs_v3_wall_speedup_min": 1.05,
    "no_regression_floor": 0.98,
    "partner_migration_counts_as_win": False,
    "algorithmic_complexity_outlier_must_be_labeled": True,
}
_PARTIAL_CONTROL_BAR = {
    "correctness_parity_required": True,
    "operator_control_only": True,
    "whole_app_speedup_claim_authorized": False,
    "if_measured_no_regression_floor": 0.98,
    "excluded_from_formal_high_performance_score": True,
}
_HAUSDORFF_FOCUSED_SPEED_BAR = {
    "correctness_parity_required": True,
    "v4_vs_v2_14_wall_speedup_min": 1.20,
    "v4_vs_v2_14_primary_metric_speedup_min": 1.20,
    "v4_vs_v3_hot_speedup_min": 1.20,
    "prepare_no_regression_floor_where_comparable": 0.80,
    "coordinate_normalized_1m_correctness_probe_required": True,
    "partner_migration_counts_as_win": False,
    "app_specific_native_kernel_authorized": False,
}
_BLOCKER_BAR = {
    "v4_route_required": False,
    "count_as_visible_blocker": True,
    "excluded_from_geomean": True,
    "posthoc_exclusion_forbidden": True,
}


_PROTOCOL_ROWS = (
    V4Goal4653ProtocolRow(
        app="rt_dbscan",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        protocol_row_type=V4_PROTOCOL_FULL_APP_CANDIDATE,
        benchmark_app_frontdoor="examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="V4 fixed-radius count-threshold plus fixed Numba component-union route",
        mapped_v4_operators=(
            "v4_fixed_radius_count_threshold_2d_device_arrays",
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
        ),
        dataset_scale="clustered3d point_count=262144 radius=3.0 min_neighbors=4 plus fixed-radius operator scale from Goal4639",
        warmup=1,
        repeat=5,
        correctness_contract="component labels canonical signature and noise/core classification parity",
        denominator="same-app V2.14/V3 incumbent route; partner migration cannot count as V4 speed win",
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_FULL_SPEED_BAR,
        claim_class_if_pass="true_v4_operator_win_candidate",
        contributes_to_formal_high_performance=True,
        v4_run_required_in_goal4654=True,
        blocker_or_gap="Whole-app RTDBSCAN timing is not yet measured under the V4 route.",
    ),
    V4Goal4653ProtocolRow(
        app="raydb_style",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        protocol_row_type=V4_PROTOCOL_FULL_APP_CANDIDATE,
        benchmark_app_frontdoor="examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="V4 grouped-i64, grouped-argmin, and any-hit operator route",
        mapped_v4_operators=(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            "v4_closest_hit_grouped_argmin_3d_device_arrays",
            "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        ),
        dataset_scale="generated deterministic RayDB rows >=131072, grouped-i64 widths 1/16/256, repeat=7 warmup=2 controls",
        warmup=2,
        repeat=7,
        correctness_contract="grouped aggregate columns exactly match CPU/Torch reference for count/sum/min/argmin rows",
        denominator="same-app V2.14/V3 incumbent route, not CuPy migration",
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_FULL_SPEED_BAR,
        claim_class_if_pass="true_v4_operator_win_candidate",
        contributes_to_formal_high_performance=True,
        v4_run_required_in_goal4654=True,
        blocker_or_gap="Whole-app RayDB-style V4 route must still be measured against V2.14/V3.",
    ),
    V4Goal4653ProtocolRow(
        app="triangle_counting",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        protocol_row_type=V4_PROTOCOL_FULL_APP_CANDIDATE,
        benchmark_app_frontdoor="examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="V4 ray-triangle any-hit weighted-sum plus grouped-i64 route",
        mapped_v4_operators=(
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        ),
        dataset_scale="Goal4633 shapes 32768/131072/262144/524288 plus grouped-i64 ray_counts 32768/131072",
        warmup=2,
        repeat=7,
        correctness_contract="triangle count and weighted compact summary parity against graph oracle/reference route",
        denominator="same-app V2.14/V3 incumbent route, not partner-only replay",
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_FULL_SPEED_BAR,
        claim_class_if_pass="true_v4_operator_win_candidate",
        contributes_to_formal_high_performance=True,
        v4_run_required_in_goal4654=True,
        blocker_or_gap="Whole-app triangle-counting V4 timing is not yet measured against V2.14/V3.",
    ),
    V4Goal4653ProtocolRow(
        app="librts_spatial_index",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        protocol_row_type=V4_PROTOCOL_FULL_APP_CANDIDATE,
        benchmark_app_frontdoor="examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="V4 generic prepared AABB all-ops count route",
        mapped_v4_operators=("v4_aabb_index_query_2d_all_ops_count_prepared_runner",),
        dataset_scale="box_count=1000000 query_count=1000 operation=all repeats=240",
        warmup=1,
        repeat=240,
        correctness_contract="all operation counts match cross-backend for same AABB dataset",
        denominator="same-app V2.14/V3 prepared AABB controls plus same-contract Embree baseline with explicit denominator",
        metric_windows=_COMMON_METRICS,
        pass_fail_bar={
            **_FULL_SPEED_BAR,
            "algorithmic_complexity_outlier_must_be_labeled": True,
            "public_geomean_headline_forbidden": True,
        },
        claim_class_if_pass="true_v4_operator_win_candidate_or_algorithmic_complexity_win_labeled",
        contributes_to_formal_high_performance=True,
        v4_run_required_in_goal4654=True,
        blocker_or_gap="LibRTS paper reproduction remains out of scope; this row is generic AABB all-ops only.",
    ),
    V4Goal4653ProtocolRow(
        app="hausdorff_xhd",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        protocol_row_type=V4_PROTOCOL_FULL_APP_CANDIDATE,
        benchmark_app_frontdoor="examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route=(
            "official V4 point-group nearest-witness plus adaptive CuPy "
            "global-argmax route with coordinate-normalized correctness boundary"
        ),
        mapped_v4_operators=(
            "v4_point_group_nearest_witness_2d_device_arrays",
            "v4_fixed_radius_count_threshold_2d_device_arrays",
        ),
        dataset_scale=(
            "Goal4667 focused rows at 65536 and 262144 points/side plus "
            "1048576 coordinate-normalized correctness-boundary probe"
        ),
        warmup=5,
        repeat=9,
        correctness_contract=(
            "directed Hausdorff distance parity; 1M exactness requires measured "
            "coordinate-normalization span boundary"
        ),
        denominator=(
            "V2.14 Embree directed-summary primary denominator plus V3.0.2 CuPy "
            "hot/prepare denominator from Goal4665; partner migration alone does "
            "not count as a V4 win"
        ),
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_HAUSDORFF_FOCUSED_SPEED_BAR,
        claim_class_if_pass="focused_true_v4_runtime_candidate_row_not_release_by_itself",
        contributes_to_formal_high_performance=True,
        v4_run_required_in_goal4654=True,
        blocker_or_gap=(
            "Goal4667 clears the focused Hausdorff gate through a generic adaptive "
            "CuPy argmax continuation, but this is one app row and does not "
            "authorize V4 release without the full app-level decision protocol."
        ),
    ),
    V4Goal4653ProtocolRow(
        app="robot_collision",
        route_class=V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
        protocol_row_type=V4_PROTOCOL_PARTIAL_CONTROL_ONLY,
        benchmark_app_frontdoor="examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="partial V4 any-hit flags control only",
        mapped_v4_operators=("v4_ray_triangle_any_hit_flags_2d_device_arrays",),
        dataset_scale="any-hit flags max_torch_reference_count=8192 control; no frozen full collision planning route",
        warmup=1,
        repeat=5,
        correctness_contract="collision hit/no-hit flag parity if measured as control",
        denominator="operator-control denominator only; no app-level V4 speed denominator",
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_PARTIAL_CONTROL_BAR,
        claim_class_if_pass="partial_operator_control_not_v4_app_win",
        contributes_to_formal_high_performance=False,
        v4_run_required_in_goal4654=False,
        blocker_or_gap="Needs generic grouped segment/pose lowering before whole-app V4 row.",
    ),
    V4Goal4653ProtocolRow(
        app="contact_manifold",
        route_class=V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
        protocol_row_type=V4_PROTOCOL_PARTIAL_CONTROL_ONLY,
        benchmark_app_frontdoor="examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="partial V4 nearest-witness control only",
        mapped_v4_operators=("v4_point_group_nearest_witness_2d_device_arrays",),
        dataset_scale="point-group nearest-witness query_counts 32768/131072 mixed4/mixed6 controls",
        warmup=2,
        repeat=7,
        correctness_contract="nearest witness/contact candidate parity if measured as control",
        denominator="operator-control denominator only; no app-level V4 speed denominator",
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_PARTIAL_CONTROL_BAR,
        claim_class_if_pass="partial_operator_control_not_v4_app_win",
        contributes_to_formal_high_performance=False,
        v4_run_required_in_goal4654=False,
        blocker_or_gap="Needs bounded witness collection/contact manifold generic operator before whole-app V4 row.",
    ),
    V4Goal4653ProtocolRow(
        app="rtnn",
        route_class=V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
        protocol_row_type=V4_PROTOCOL_PARTIAL_CONTROL_ONLY,
        benchmark_app_frontdoor="examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="V4 ranked-summary candidate route present, measured, and performance-failed",
        mapped_v4_operators=(
            "v4_point_group_nearest_witness_2d_device_arrays",
            "v4_fixed_radius_ranked_summary_3d_prepared_runner",
        ),
        dataset_scale=(
            "ranked-summary candidate rows at 65536, 262144, and 1048576 "
            "points; serious scales are hot-path parity"
        ),
        warmup=2,
        repeat=7,
        correctness_contract="ranked-summary signature/query-count validation passes for V4 candidate rows",
        denominator=(
            "closest old-version ranked-summary front door versus V4 candidate; "
            "not exact same-runner V2/V3/V4"
        ),
        metric_windows=_COMMON_METRICS,
        pass_fail_bar=_PARTIAL_CONTROL_BAR,
        claim_class_if_pass="candidate_route_present_but_does_not_move_app_level_bar",
        contributes_to_formal_high_performance=False,
        v4_run_required_in_goal4654=False,
        blocker_or_gap=(
            "Goal4660/4661 prove the V4 candidate executes, but 262144 and "
            "1048576 point rows are parity, so RTNN cannot count as a V4 speed win."
        ),
    ),
    V4Goal4653ProtocolRow(
        app="spatial_rayjoin",
        route_class=V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER,
        protocol_row_type=V4_PROTOCOL_NO_ROUTE_BLOCKER,
        benchmark_app_frontdoor="examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="no current V4 route",
        mapped_v4_operators=(),
        dataset_scale="public CDB / same-source spatial join controls remain V2/V3 only",
        warmup=0,
        repeat=0,
        correctness_contract="no V4 correctness contract because no V4 route exists",
        denominator="visible blocker row; no hidden fallback denominator",
        metric_windows=("blocker_status",),
        pass_fail_bar=_BLOCKER_BAR,
        claim_class_if_pass="no_v4_route_blocker",
        contributes_to_formal_high_performance=False,
        v4_run_required_in_goal4654=False,
        blocker_or_gap="Relation topology/PIP stream is not a current V4 generic Tier-2 surface.",
    ),
    V4Goal4653ProtocolRow(
        app="barnes_hut",
        route_class=V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON,
        protocol_row_type=V4_PROTOCOL_DEFERRED_EXCLUDED,
        benchmark_app_frontdoor="examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
        v2_14_route=_COMMON_V2_ROUTE,
        v3_route=_COMMON_V3_ROUTE,
        v4_route="deferred; no Barnes-Hut app-identity V4 kernel",
        mapped_v4_operators=(),
        dataset_scale="Barnes-Hut/N-body force-law rows remain historical controls only",
        warmup=0,
        repeat=0,
        correctness_contract="no V4 correctness contract because V4.0 excludes app-identity aggregate-tree force law",
        denominator="visible deferred row; no hidden fallback denominator",
        metric_windows=("deferred_status",),
        pass_fail_bar=_BLOCKER_BAR,
        claim_class_if_pass="deferred_excluded_with_reason",
        contributes_to_formal_high_performance=False,
        v4_run_required_in_goal4654=False,
        blocker_or_gap="Aggregate-tree weighted vector sum is Barnes-Hut/N-body app-identity specific and excluded from V4.0 generic Tier-2.",
    ),
)


def v4_goal4653_protocol_rows() -> tuple[dict[str, Any], ...]:
    return tuple(row.as_dict() for row in _PROTOCOL_ROWS)


def v4_goal4653_protocol_summary() -> dict[str, Any]:
    rows = v4_goal4653_protocol_rows()
    by_type = {row_type: 0 for row_type in V4_PROTOCOL_ROW_TYPES}
    for row in rows:
        by_type[str(row["protocol_row_type"])] += 1
    return {
        "status": V4_GOAL4653_PROTOCOL_STATUS,
        "app_count": len(rows),
        "app_order": V4_GOAL4652_APP_ORDER,
        "by_protocol_row_type": by_type,
        "full_app_v4_speed_row_count": by_type[V4_PROTOCOL_FULL_APP_CANDIDATE],
        "partial_control_count": by_type[V4_PROTOCOL_PARTIAL_CONTROL_ONLY],
        "visible_blocker_or_deferred_count": by_type[V4_PROTOCOL_NO_ROUTE_BLOCKER]
        + by_type[V4_PROTOCOL_DEFERRED_EXCLUDED],
        "source_inputs": V4_GOAL4653_PROTOCOL_SOURCE_INPUTS,
        "all_rows_have_pre_frozen_bars": all(bool(row["pass_fail_bar"]) for row in rows),
        "no_naive_whole_suite_geomean_trigger": True,
        "posthoc_app_exclusion_forbidden": True,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
        "silent_v2_v3_fallback_authorized": False,
        "pod_spend_authorized_by_this_goal": False,
    }


def validate_v4_goal4653_protocol() -> dict[str, Any]:
    route_rows = {row["app"]: row for row in v4_goal4652_app_route_bindings()}
    rows = v4_goal4653_protocol_rows()
    apps = tuple(str(row["app"]) for row in rows)
    if apps != V4_GOAL4652_APP_ORDER:
        raise ValueError(f"Goal4653 app order drift: {apps!r}")
    if len(set(apps)) != len(apps):
        raise ValueError("Goal4653 apps must be unique")
    for row in rows:
        route = route_rows[row["app"]]
        if row["route_class"] != route["route_class"]:
            raise ValueError(f"{row['app']}: route class drift from Goal4652")
        if tuple(row["mapped_v4_operators"]) != tuple(route["mapped_v4_operators"]):
            raise ValueError(f"{row['app']}: mapped V4 operator drift from Goal4652")
        if row["protocol_row_type"] == V4_PROTOCOL_FULL_APP_CANDIDATE:
            if row["pass_fail_bar"].get("v4_vs_v2_14_wall_speedup_min") != 1.20:
                raise ValueError(f"{row['app']}: full speed row must freeze 1.20x V4/V2.14 bar")
            if row["pass_fail_bar"].get("partner_migration_counts_as_win") is not False:
                raise ValueError(f"{row['app']}: partner migration cannot count as a win")
        if row["protocol_row_type"] != V4_PROTOCOL_FULL_APP_CANDIDATE:
            if row["contributes_to_formal_high_performance"]:
                raise ValueError(f"{row['app']}: non-full row contributes to formal high performance")
        for flag in (
            "release_claim_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "app_specific_native_kernel_authorized",
            "silent_v2_v3_fallback_authorized",
        ):
            if row[flag]:
                raise ValueError(f"{row['app']}: row authorized {flag}")
    summary = v4_goal4653_protocol_summary()
    if summary["full_app_v4_speed_row_count"] != 5:
        raise ValueError("Goal4668 must freeze exactly five full V4 app speed-row candidates")
    if summary["partial_control_count"] != 3:
        raise ValueError("Goal4668 must keep three partial controls visible")
    if summary["visible_blocker_or_deferred_count"] != 2:
        raise ValueError("Goal4653 must keep two blocker/deferred rows visible")
    return summary


__all__ = [
    "V4_GOAL4653_PROTOCOL_STATUS",
    "V4_PROTOCOL_FULL_APP_CANDIDATE",
    "V4_PROTOCOL_PARTIAL_CONTROL_ONLY",
    "V4_PROTOCOL_NO_ROUTE_BLOCKER",
    "V4_PROTOCOL_DEFERRED_EXCLUDED",
    "V4_PROTOCOL_ROW_TYPES",
    "V4Goal4653ProtocolRow",
    "v4_goal4653_protocol_rows",
    "v4_goal4653_protocol_summary",
    "validate_v4_goal4653_protocol",
]
