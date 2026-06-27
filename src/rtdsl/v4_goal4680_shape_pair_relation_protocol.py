from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v4_shape_pair_relation import V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_OPERATOR
from .v4_shape_pair_relation import V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_SURFACE
from .v4_shape_pair_relation import shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4


V4_GOAL4680_SHAPE_PAIR_RELATION_PROTOCOL_STATUS = (
    "goal4680_shape_pair_relation_local_static_frontdoor_protocol_passed_not_pod_run"
)
V4_GOAL4680_SCRIPT = "scripts/v4_goal4681_shape_pair_relation_pod_benchmark.py"


@dataclass(frozen=True)
class V4Goal4680ShapePairRelationProtocol:
    status: str
    target_surface: str
    generic_primitive: str
    benchmark_script: str
    app_probe: str
    profile: str
    left_shape_count: int
    right_shape_count: int
    repeat: int
    warmup: int
    correctness_companion_left_shape_count: int
    correctness_companion_right_shape_count: int
    v2_14_denominator: str
    v3_0_2_control: str
    v4_candidate_route: str
    metric_windows: tuple[str, ...]
    pass_fail_bar: dict[str, object]
    required_outputs: tuple[str, ...]
    non_authorization: dict[str, bool]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "target_surface": self.target_surface,
            "generic_primitive": self.generic_primitive,
            "benchmark_script": self.benchmark_script,
            "app_probe": self.app_probe,
            "profile": self.profile,
            "left_shape_count": self.left_shape_count,
            "right_shape_count": self.right_shape_count,
            "repeat": self.repeat,
            "warmup": self.warmup,
            "correctness_companion_left_shape_count": self.correctness_companion_left_shape_count,
            "correctness_companion_right_shape_count": self.correctness_companion_right_shape_count,
            "v2_14_denominator": self.v2_14_denominator,
            "v3_0_2_control": self.v3_0_2_control,
            "v4_candidate_route": self.v4_candidate_route,
            "metric_windows": self.metric_windows,
            "pass_fail_bar": self.pass_fail_bar,
            "required_outputs": self.required_outputs,
            "non_authorization": self.non_authorization,
        }


def v4_goal4680_shape_pair_relation_protocol() -> V4Goal4680ShapePairRelationProtocol:
    return V4Goal4680ShapePairRelationProtocol(
        status=V4_GOAL4680_SHAPE_PAIR_RELATION_PROTOCOL_STATUS,
        target_surface=V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_SURFACE,
        generic_primitive=V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_OPERATOR,
        benchmark_script=V4_GOAL4680_SCRIPT,
        app_probe="spatial_rayjoin.overlay_active_count_probe_only",
        profile="serious_focused_same_primitive",
        left_shape_count=4096,
        right_shape_count=4096,
        repeat=7,
        warmup=2,
        correctness_companion_left_shape_count=512,
        correctness_companion_right_shape_count=512,
        v2_14_denominator=(
            "Strongest V2.14 same-primitive route for spatial_rayjoin overlay "
            "active count: prepared_optix_shape_pair_active_count_device_continuation_reuse "
            "using the V2.14 prepared-left executor/device-continuation path when "
            "present. If that route is unavailable in the checked V2.14 tree, "
            "the run must fail or be reclassified; it must not silently fall "
            "back to Numba/all-CuPy/CPU or a weaker non-prepared route."
        ),
        v3_0_2_control=(
            "V3.0.2 same route where available. A V4/V3 parity result is expected "
            "if V3.0.2 already carries the same prepared-left executor family; "
            "that does not authorize broad V4 speed wording."
        ),
        v4_candidate_route=(
            "V4 local/static wrapper "
            "prepare_shape_pair_relation_active_count_2d_prepared_left_executor_v4 "
            "over the app-agnostic prepared-left executor ABI."
        ),
        metric_windows=(
            "prepare_right_scene_seconds",
            "prepare_left_set_seconds",
            "prepare_executor_seconds",
            "active_count_hot_seconds",
            "active_count_wall_seconds",
            "correctness_parity",
            "host_row_stream_materialization_in_hot_path",
        ),
        pass_fail_bar={
            "v4_hot_over_v2_14_same_primitive_min_for_speed_credit": 1.20,
            "v4_wall_over_v2_14_same_primitive_min_for_speed_credit": 1.10,
            "v4_hot_over_v3_0_2_parity_floor": 0.98,
            "correctness_parity_required": True,
            "host_row_stream_materialization_in_hot_path_allowed": False,
            "partner_migration_counts_as_speed": False,
            "app_identity_kernel_allowed": False,
        },
        required_outputs=(
            "raw stdout JSON for v2_14, v3_0_2, and v4_current",
            "stderr for each subprocess",
            "summary.json with denominator labels, ratios, and pass/fail flags",
            "correctness companion run at 512x512 shapes",
            "phase timings for prepare_right, prepare_left, prepare_executor, and hot run",
            "native symbol list used by each route",
        ),
        non_authorization={
            "pod_run_authorized": False,
            "release_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_high_performance_wording_authorized": False,
            "broad_v4_over_v2_v3_wording_authorized": False,
            "rt_core_speedup_wording_authorized": False,
            "true_zero_copy_wording_authorized": False,
            "tier3_callback_authorized": False,
            "raw_optix_callback_authorized": False,
            "c_abi_or_embedding_authorized": False,
            "non_python_host_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_identity_kernel_authorized": False,
        },
    )


def validate_v4_goal4680_shape_pair_relation_protocol(
    protocol: V4Goal4680ShapePairRelationProtocol | dict[str, Any] | None = None,
) -> dict[str, object]:
    payload = (
        v4_goal4680_shape_pair_relation_protocol().as_dict()
        if protocol is None
        else protocol.as_dict()
        if isinstance(protocol, V4Goal4680ShapePairRelationProtocol)
        else dict(protocol)
    )
    boundary = shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4()
    missing: list[str] = []
    if payload.get("status") != V4_GOAL4680_SHAPE_PAIR_RELATION_PROTOCOL_STATUS:
        missing.append("status")
    if payload.get("target_surface") != V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_SURFACE:
        missing.append("target_surface")
    if payload.get("generic_primitive") != V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_OPERATOR:
        missing.append("generic_primitive")
    app_free_strings = (
        str(payload.get("target_surface", "")),
        str(payload.get("generic_primitive", "")),
        str(boundary.get("native_prepare_symbol", "")),
        str(boundary.get("native_run_symbol", "")),
        str(boundary.get("native_destroy_symbol", "")),
    )
    forbidden = ("rayjoin", "county", "soil", "overlay_seed")
    for text in app_free_strings:
        lowered = text.lower()
        for token in forbidden:
            if token in lowered:
                missing.append(f"app_identity_token_{token}")
    if "prepared_optix_shape_pair_active_count_device_continuation_reuse" not in str(
        payload.get("v2_14_denominator")
    ):
        missing.append("v2_14_strongest_same_primitive_denominator")
    if "must not silently fall back" not in str(payload.get("v2_14_denominator")):
        missing.append("no_silent_weak_fallback")
    bars = payload.get("pass_fail_bar")
    if not isinstance(bars, dict):
        missing.append("pass_fail_bar")
        bars = {}
    if bars.get("v4_hot_over_v2_14_same_primitive_min_for_speed_credit") != 1.20:
        missing.append("hot_bar")
    if bars.get("v4_wall_over_v2_14_same_primitive_min_for_speed_credit") != 1.10:
        missing.append("wall_bar")
    if bars.get("correctness_parity_required") is not True:
        missing.append("correctness_parity_required")
    if bars.get("host_row_stream_materialization_in_hot_path_allowed") is not False:
        missing.append("host_materialization_forbidden")
    if bars.get("partner_migration_counts_as_speed") is not False:
        missing.append("partner_migration_false")
    if bars.get("app_identity_kernel_allowed") is not False:
        missing.append("app_identity_kernel_false")
    if int(payload.get("left_shape_count", 0)) < 4096:
        missing.append("left_shape_count")
    if int(payload.get("right_shape_count", 0)) < 4096:
        missing.append("right_shape_count")
    if int(payload.get("repeat", 0)) < 7:
        missing.append("repeat")
    non_auth = payload.get("non_authorization")
    if not isinstance(non_auth, dict):
        missing.append("non_authorization")
        non_auth = {}
    if any(bool(value) for value in non_auth.values()):
        missing.append("non_authorization_flags_false")
    if boundary.get("pod_benchmark_authorized") is not False:
        missing.append("boundary_pod_false")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "local_static_frontdoor_protocol_gate_passed": not missing,
        "pod_run_authorized": False,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4680_SCRIPT",
    "V4_GOAL4680_SHAPE_PAIR_RELATION_PROTOCOL_STATUS",
    "V4Goal4680ShapePairRelationProtocol",
    "v4_goal4680_shape_pair_relation_protocol",
    "validate_v4_goal4680_shape_pair_relation_protocol",
]
