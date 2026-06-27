from __future__ import annotations

from dataclasses import dataclass

from .v4_operator_catalog import V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS
from .v4_operator_catalog import V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS
from .v4_operator_catalog import plan_v4_operator_request


V4_GOAL4685_TIER3_WRAPPER_ABI_PROTOCOL_STATUS = (
    "goal4685_tier3_wrapper_direct_callable_abi_protocol_gate_no_pod"
)
V4_GOAL4685_NEXT_GOAL = "Goal4686 tier3 wrapper ABI local implementation spike"


@dataclass(frozen=True)
class V4Goal4685Tier3Stage:
    stage: str
    required_evidence: tuple[str, ...]
    pass_condition: str
    kill_condition: str

    def as_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "required_evidence": self.required_evidence,
            "pass_condition": self.pass_condition,
            "kill_condition": self.kill_condition,
        }


@dataclass(frozen=True)
class V4Goal4685Tier3WrapperAbiProtocol:
    status: str
    protocol_scope: str
    required_stages: tuple[V4Goal4685Tier3Stage, ...]
    forbidden_paths: tuple[str, ...]
    next_goal: str
    local_protocol_gate_authorized: bool = True
    pod_authorized: bool = False
    implementation_authorized: bool = False
    tier3_public_support_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_identity_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "protocol_scope": self.protocol_scope,
            "required_stages": tuple(stage.as_dict() for stage in self.required_stages),
            "forbidden_paths": self.forbidden_paths,
            "next_goal": self.next_goal,
            "local_protocol_gate_authorized": self.local_protocol_gate_authorized,
            "pod_authorized": self.pod_authorized,
            "implementation_authorized": self.implementation_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_identity_kernel_authorized": self.app_identity_kernel_authorized,
        }


def v4_goal4685_tier3_wrapper_abi_protocol() -> V4Goal4685Tier3WrapperAbiProtocol:
    stages = (
        V4Goal4685Tier3Stage(
            stage="stage0_planner_boundary",
            required_evidence=(
                "scalar Numba device callback request returns tier3_spike_only_not_v4_0_release_surface",
                "action-shaped callback request returns rejected_action_shaped_callback_deferred",
                "no API surface is exposed for Tier-3",
                "release/support/raw-callback flags remain false",
            ),
            pass_condition="planner fails closed except for spike-only scalar reduce candidates",
            kill_condition="planner exposes a Tier-3 public API surface or accepts action-shaped callbacks",
        ),
        V4Goal4685Tier3Stage(
            stage="stage1_ptx_generation_reliability",
            required_evidence=(
                "20 compile attempts across at least 4 scalar callback variants",
                ">=95% compile reliability",
                "PTX ISA/header and callback symbol recorded for every success",
                "failures classified by stage and error type",
            ),
            pass_condition=(
                "Numba can reliably emit scalar device-function PTX under pinned "
                "toolchain with >=95% compile reliability"
            ),
            kill_condition="compile reliability <95% or callback symbol cannot be identified",
        ),
        V4Goal4685Tier3Stage(
            stage="stage2_semantic_optix_wrapper_or_direct_callable",
            required_evidence=(
                "Numba PTX is composed with a hand-written semantic OptiX wrapper or direct-callable ABI",
                "OptiX module creation succeeds for the semantic module, not bare helper PTX",
                "program group creation succeeds",
                "pipeline creation succeeds",
                "launch succeeds",
                "attempt count and reliability are recorded",
            ),
            pass_condition="semantic OptiX wrapper/direct-callable route succeeds with >=95% reliability",
            kill_condition="only bare helper PTX is tested, or wrapper/direct-callable reliability <95%",
        ),
        V4Goal4685Tier3Stage(
            stage="stage3_correctness_parity",
            required_evidence=(
                "dense-hit dataset",
                "sparse-hit dataset",
                "no-hit dataset",
                "CPU or hand-written Tier-2 fused reference named",
                "integer exactness or float tolerance fixed before run",
            ),
            pass_condition="100% correctness parity across all deterministic datasets",
            kill_condition="any correctness parity case fails",
        ),
        V4Goal4685Tier3Stage(
            stage="stage4_overhead_ceiling",
            required_evidence=(
                "matching hand-written fused baseline",
                "sizes 32768 and 131072",
                "repeat >=10 and warmup >=2",
                "median callback route <=1.50x matching fused route at every tested size",
                "no tested size >2.00x",
            ),
            pass_condition="callback overhead stays inside the frozen ceiling",
            kill_condition="median overhead >1.50x at any required size or any size >2.00x",
        ),
    )
    return V4Goal4685Tier3WrapperAbiProtocol(
        status=V4_GOAL4685_TIER3_WRAPPER_ABI_PROTOCOL_STATUS,
        protocol_scope=(
            "protocol/local gate only for a future Tier-3 wrapper/direct-callable ABI spike. "
            "It upgrades the old blocked bare-PTX probe into a required semantic OptiX "
            "module path, but it does not authorize implementation, POD, public support, or release."
        ),
        required_stages=stages,
        forbidden_paths=(
            "repeating the old bare Numba helper PTX optixModuleCreate probe as a success path",
            "raw OptiX callbacks as the user-facing public API",
            "action-shaped callbacks with shared mutation, dynamic allocation, or variable-length output",
            "app-identity native kernels",
            "C ABI / embedding / non-Python-host work",
            "public Tier-3 callback support wording before all stages pass and external review authorizes it",
        ),
        next_goal=(
            "Goal4686 may implement only a local spike scaffold for the semantic "
            "wrapper/direct-callable ABI. POD remains a later gate after local "
            "structure and protocol validation."
        ),
    )


def validate_v4_goal4685_tier3_wrapper_abi_protocol() -> dict[str, object]:
    protocol = v4_goal4685_tier3_wrapper_abi_protocol()
    payload = protocol.as_dict()
    scalar_plan = plan_v4_operator_request(
        "custom",
        callback_shape="custom_scalar_reduce",
        numba_device_function=True,
    )
    action_plan = plan_v4_operator_request(
        "custom",
        callback_shape="custom_action",
        mutates_shared_state=True,
        variable_length_output=True,
    )
    stage_names = tuple(str(stage["stage"]) for stage in payload["required_stages"])
    stage_text = " ".join(str(stage) for stage in payload["required_stages"])
    forbidden_text = " ".join(str(item) for item in payload["forbidden_paths"])
    missing: list[str] = []
    if payload["status"] != V4_GOAL4685_TIER3_WRAPPER_ABI_PROTOCOL_STATUS:
        missing.append("status")
    for required_stage in (
        "stage0_planner_boundary",
        "stage1_ptx_generation_reliability",
        "stage2_semantic_optix_wrapper_or_direct_callable",
        "stage3_correctness_parity",
        "stage4_overhead_ceiling",
    ):
        if required_stage not in stage_names:
            missing.append(required_stage)
    if "semantic OptiX" not in stage_text:
        missing.append("semantic_optix_wrapper")
    if "bare Numba helper PTX" not in forbidden_text:
        missing.append("bare_ptx_forbidden")
    if scalar_plan.status != "tier3_spike_only_not_v4_0_release_surface":
        missing.append("scalar_planner_status")
    if scalar_plan.tier3_protocol_status != V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS:
        missing.append("scalar_protocol_status")
    if scalar_plan.api_surface is not None:
        missing.append("scalar_api_surface")
    if action_plan.status != "rejected_action_shaped_callback_deferred":
        missing.append("action_planner_status")
    if action_plan.tier3_protocol_status != V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS:
        missing.append("action_protocol_status")
    if action_plan.tier3_spike_authorized is not False:
        missing.append("action_spike_authorized")
    if payload.get("local_protocol_gate_authorized") is not True:
        missing.append("local_protocol_gate_authorized")
    for key in (
        "pod_authorized",
        "implementation_authorized",
        "tier3_public_support_authorized",
        "raw_optix_callback_authorized",
        "release_authorized",
        "public_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_identity_kernel_authorized",
    ):
        if payload.get(key) is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "protocol": payload,
        "scalar_plan_status": scalar_plan.status,
        "action_plan_status": action_plan.status,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4685_TIER3_WRAPPER_ABI_PROTOCOL_STATUS",
    "V4_GOAL4685_NEXT_GOAL",
    "V4Goal4685Tier3Stage",
    "V4Goal4685Tier3WrapperAbiProtocol",
    "v4_goal4685_tier3_wrapper_abi_protocol",
    "validate_v4_goal4685_tier3_wrapper_abi_protocol",
]
