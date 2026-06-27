from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4676_PROTOCOL_STATUS = "goal4676_aggregate_frontier_focused_pod_protocol_frozen_not_run"
V4_GOAL4676_SCRIPT = "scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py"
V4_GOAL4676_TARGET_SURFACE = "v4_aggregate_frontier_device_columns_2d_prepared_runner"
V4_GOAL4676_GENERIC_PRIMITIVE = "AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D"


@dataclass(frozen=True)
class V4Goal4676AggregateFrontierProtocol:
    status: str
    target_surface: str
    generic_primitive: str
    benchmark_script: str
    app_probe: str
    profile: str
    body_count: int
    repeat: int
    warmup: int
    correctness_companion_body_count: int
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
            "body_count": self.body_count,
            "repeat": self.repeat,
            "warmup": self.warmup,
            "correctness_companion_body_count": self.correctness_companion_body_count,
            "v2_14_denominator": self.v2_14_denominator,
            "v3_0_2_control": self.v3_0_2_control,
            "v4_candidate_route": self.v4_candidate_route,
            "metric_windows": self.metric_windows,
            "pass_fail_bar": self.pass_fail_bar,
            "required_outputs": self.required_outputs,
            "non_authorization": self.non_authorization,
        }


def v4_goal4676_aggregate_frontier_protocol() -> V4Goal4676AggregateFrontierProtocol:
    """Return the frozen focused POD protocol for Goal4676."""

    return V4Goal4676AggregateFrontierProtocol(
        status=V4_GOAL4676_PROTOCOL_STATUS,
        target_surface=V4_GOAL4676_TARGET_SURFACE,
        generic_primitive=V4_GOAL4676_GENERIC_PRIMITIVE,
        benchmark_script=V4_GOAL4676_SCRIPT,
        app_probe="barnes_hut_force_app_as_probe_only",
        profile="serious",
        body_count=32768,
        repeat=7,
        warmup=2,
        correctness_companion_body_count=2048,
        v2_14_denominator=(
            "V2.14 public/user-runnable aggregate-frontier route: "
            "collect_aggregate_frontier_2d_optix when exported by V2.14 plus "
            "host-materialized row_offsets/frontier_i64_rows and explicit Numba "
            "CPU weighted-vector continuation. If the OptiX wrapper is unavailable "
            "in the checked V2.14 tree, the run must fail or be reclassified; it "
            "must not silently fall back to a weak CPU-only denominator."
        ),
        v3_0_2_control=(
            "V3.0.2 device-column primitive control using the same logical "
            "frontier/vector contract where available. V4/V3 parity is not a "
            "clean V4 failure or win because the device-column primitive already "
            "exists in V3.0.2."
        ),
        v4_candidate_route=(
            "V4 candidate prepared runner through "
            "prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4, "
            "then explicit CuPy or Numba downstream weighted-vector continuation."
        ),
        metric_windows=(
            "aggregate_frontier_frontier_only_hot_seconds",
            "full_frontier_plus_partner_hot_seconds",
            "full_frontier_plus_partner_wall_seconds",
            "correctness_parity",
            "checksum_parity_for_large_run",
            "host_frontier_materialization_in_hot_path",
        ),
        pass_fail_bar={
            "v4_frontier_only_hot_over_v2_14_min": 1.20,
            "v4_full_hot_over_v2_14_min": 1.20,
            "v4_full_wall_over_v2_14_min": 1.10,
            "correctness_parity_required": True,
            "large_run_checksum_parity_required": True,
            "host_frontier_materialization_in_hot_path_allowed": False,
            "partner_migration_counts_as_speed": False,
            "v4_over_v3_0_2_same_route_required_for_clean_new_lever": False,
        },
        required_outputs=(
            "raw stdout JSON for v2_14, v3_0_2, and v4_current",
            "stderr for each subprocess",
            "summary.json with ratios, pass/fail flags, and denominator labels",
            "correctness companion run at body_count=2048",
            "phase timings for frontier traversal/collection and downstream continuation",
        ),
        non_authorization={
            "release_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_high_performance_wording_authorized": False,
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


def validate_v4_goal4676_aggregate_frontier_protocol(
    protocol: V4Goal4676AggregateFrontierProtocol | dict[str, Any] | None = None,
) -> dict[str, object]:
    payload = (
        v4_goal4676_aggregate_frontier_protocol().as_dict()
        if protocol is None
        else protocol.as_dict()
        if isinstance(protocol, V4Goal4676AggregateFrontierProtocol)
        else dict(protocol)
    )
    missing: list[str] = []
    if payload.get("status") != V4_GOAL4676_PROTOCOL_STATUS:
        missing.append("status")
    if payload.get("target_surface") != V4_GOAL4676_TARGET_SURFACE:
        missing.append("target_surface")
    if "collect_aggregate_frontier_2d_optix" not in str(payload.get("v2_14_denominator")):
        missing.append("v2_14_optix_denominator")
    if "must not silently fall back to a weak CPU-only denominator" not in str(
        payload.get("v2_14_denominator")
    ):
        missing.append("no_weak_cpu_fallback")
    bars = payload.get("pass_fail_bar")
    if not isinstance(bars, dict):
        missing.append("pass_fail_bar")
        bars = {}
    if bars.get("v4_frontier_only_hot_over_v2_14_min") != 1.20:
        missing.append("frontier_only_bar")
    if bars.get("v4_full_hot_over_v2_14_min") != 1.20:
        missing.append("full_hot_bar")
    if bars.get("v4_full_wall_over_v2_14_min") != 1.10:
        missing.append("full_wall_bar")
    if bars.get("partner_migration_counts_as_speed") is not False:
        missing.append("partner_migration_boundary")
    if bars.get("host_frontier_materialization_in_hot_path_allowed") is not False:
        missing.append("host_materialization_boundary")
    if int(payload.get("body_count", 0)) < 32768:
        missing.append("serious_scale")
    if int(payload.get("repeat", 0)) < 7:
        missing.append("repeat")
    non_auth = payload.get("non_authorization")
    if not isinstance(non_auth, dict):
        missing.append("non_authorization")
        non_auth = {}
    if any(bool(value) for value in non_auth.values()):
        missing.append("non_authorization_flags_false")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "pod_benchmark_protocol_frozen": not missing,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4676_GENERIC_PRIMITIVE",
    "V4_GOAL4676_PROTOCOL_STATUS",
    "V4_GOAL4676_SCRIPT",
    "V4_GOAL4676_TARGET_SURFACE",
    "V4Goal4676AggregateFrontierProtocol",
    "v4_goal4676_aggregate_frontier_protocol",
    "validate_v4_goal4676_aggregate_frontier_protocol",
]
