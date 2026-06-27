from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4631_STATUS = "goal4631_tier3_spike_executed_deferred_not_supported"
V4_GOAL4631_DECISION = "defer_tier3_not_v4_0_supported"
V4_GOAL4631_STAGE1_STATUS = "ptx_generated_narrow_evidence"
V4_GOAL4631_STAGE2_STATUS = "bare_numba_ptx_optix_module_create_blocked"


@dataclass(frozen=True)
class V4Tier3SpikeStage:
    stage: str
    status: str
    attempted: bool
    passed: bool
    evidence: tuple[str, ...]
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "status": self.status,
            "attempted": self.attempted,
            "passed": self.passed,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


V4_GOAL4631_STAGES = (
    V4Tier3SpikeStage(
        stage="stage0_planner_boundary",
        status="passed",
        attempted=True,
        passed=True,
        evidence=(
            "tests/v4_tier3_callback_spike_protocol_test.py",
            "tests/v4_operator_catalog_test.py",
            "tests/v4_goal4630_pushdown_recognizer_test.py",
        ),
        interpretation="Planner and push-down recognizer keep scalar callbacks spike-only and action callbacks rejected.",
    ),
    V4Tier3SpikeStage(
        stage="stage1_numba_ptx_generation",
        status=V4_GOAL4631_STAGE1_STATUS,
        attempted=True,
        passed=False,
        evidence=(
            "tools/_archive/future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json",
            "tools/_archive/future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.md",
            "tools/_archive/future/v4/tier3_numba_ptx_spike.md",
        ),
        interpretation=(
            "One scalar callback generated PTX in a pinned environment, but the protocol requires at least 20 attempts across at least 4 accepted variants for a passing Stage 1 gate."
        ),
    ),
    V4Tier3SpikeStage(
        stage="stage2_optix_wrapper_or_direct_callable_abi",
        status=V4_GOAL4631_STAGE2_STATUS,
        attempted=True,
        passed=False,
        evidence=(
            "tools/_archive/future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json",
            "tools/_archive/future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.md",
            "tools/_archive/future/v4/tier3_optix_module_link_spike.md",
        ),
        interpretation=(
            "Direct optixModuleCreate on bare Numba helper PTX failed with Invalid input / No functions with semantic types found; a real OptiX wrapper or direct-callable ABI spike is still required."
        ),
    ),
    V4Tier3SpikeStage(
        stage="stage3_correctness_parity",
        status="not_attempted",
        attempted=False,
        passed=False,
        evidence=("tools/_archive/future/v4/tier3_callback_spike_protocol_2026-06-24.md",),
        interpretation="Correctness parity inside traversal cannot start until Stage 2 links and launches.",
    ),
    V4Tier3SpikeStage(
        stage="stage4_overhead_ceiling",
        status="not_attempted",
        attempted=False,
        passed=False,
        evidence=("tools/_archive/future/v4/tier3_callback_spike_protocol_2026-06-24.md",),
        interpretation="Overhead cannot be measured because no linked callback route launches.",
    ),
)


def v4_goal4631_tier3_spike_decision() -> dict[str, Any]:
    stages = tuple(stage.as_dict() for stage in V4_GOAL4631_STAGES)
    return {
        "status": V4_GOAL4631_STATUS,
        "decision": V4_GOAL4631_DECISION,
        "tier3_public_support_authorized": False,
        "tier3_spike_can_continue_in_v4x": True,
        "v4_0_release_can_depend_on_tier3": False,
        "stage0_planner_boundary_passed": True,
        "stage1_numba_ptx_generation_attempted": True,
        "stage1_numba_ptx_generation_protocol_passed": False,
        "stage1_observed_ptx_generated": True,
        "stage1_observed_attempt_count": 1,
        "stage1_required_attempt_count": 20,
        "stage1_required_callback_variant_count": 4,
        "stage2_optix_module_link_attempted": True,
        "stage2_optix_module_link_succeeded": False,
        "stage2_blocked_stage": "optix_module_create",
        "stage2_optix_error": "Invalid input",
        "stage2_optix_log_key_phrase": "No functions with semantic types found",
        "stage3_correctness_parity_attempted": False,
        "stage4_overhead_ceiling_attempted": False,
        "stages": stages,
        "required_next_tier3_work": (
            "build_real_optix_wrapper_or_direct_callable_abi_spike",
            "run_at_least_20_compile_and_link_attempts_across_4_scalar_callback_variants",
            "prove_program_group_pipeline_and_launch_reliability_at_95_percent_or_better",
            "prove_100_percent_correctness_parity_on_dense_sparse_and_empty_datasets",
            "measure_callback_route_overhead_against_matching_handwritten_tier2_baseline",
        ),
        "release_claim_authorized": False,
        "broad_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "measured_catalog_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4631_tier3_spike_decision() -> dict[str, Any]:
    decision = v4_goal4631_tier3_spike_decision()
    if decision["decision"] != V4_GOAL4631_DECISION:
        raise ValueError("Goal4631 must defer Tier-3 unless all protocol stages pass")
    if decision["tier3_public_support_authorized"]:
        raise ValueError("Goal4631 must not authorize Tier-3 public support")
    if decision["v4_0_release_can_depend_on_tier3"]:
        raise ValueError("V4.0 release decision must not depend on Tier-3")
    if decision["stage1_numba_ptx_generation_protocol_passed"]:
        raise ValueError("Stage 1 cannot pass from one callback attempt")
    if decision["stage1_observed_attempt_count"] >= decision["stage1_required_attempt_count"]:
        raise ValueError("Stage 1 attempt count should reflect narrow evidence only")
    if decision["stage2_optix_module_link_succeeded"]:
        raise ValueError("Stage 2 evidence shows direct module creation failed")
    if decision["stage3_correctness_parity_attempted"]:
        raise ValueError("Stage 3 cannot be attempted before link/launch")
    if decision["stage4_overhead_ceiling_attempted"]:
        raise ValueError("Stage 4 cannot be attempted before link/launch")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "measured_catalog_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4631 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4631_STATUS",
    "V4_GOAL4631_DECISION",
    "V4_GOAL4631_STAGE1_STATUS",
    "V4_GOAL4631_STAGE2_STATUS",
    "V4Tier3SpikeStage",
    "V4_GOAL4631_STAGES",
    "v4_goal4631_tier3_spike_decision",
    "validate_v4_goal4631_tier3_spike_decision",
]

