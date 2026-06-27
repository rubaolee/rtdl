from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from .v4_goal4697_specialized_tier3_api_contract import (
    V4_GOAL4697_ACCEPTED_STATUS,
    plan_v4_goal4697_specialized_tier3_callback_contract,
)


V4_GOAL4698_SPECIALIZED_TIER3_COMPILE_CACHE_STATUS = (
    "goal4698_specialized_tier3_compile_cache_scaffold_not_public_support"
)
V4_GOAL4698_NEXT_GOAL = "Goal4699 specialized Tier-3 app-route validation protocol"

V4_GOAL4698_CACHE_CONTRACT_VERSION = "goal4698.specialized_tier3_cache.v1"
V4_GOAL4698_COMPILE_READY_STAGE = "compile_cache_ready_not_executed"
V4_GOAL4698_REJECTED_STAGE = "rejected_before_compile"
V4_GOAL4698_INCOMPLETE_STAGE = "compile_input_incomplete"

V4_GOAL4698_ERROR_REJECTED = "RTDL_V4_TIER3_CALLBACK_REJECTED"
V4_GOAL4698_ERROR_INCOMPLETE_INPUT = "RTDL_V4_TIER3_COMPILE_INPUT_INCOMPLETE"
V4_GOAL4698_ERROR_COMPILE_FAILED = "RTDL_V4_TIER3_COMPILE_STAGE_FAILED"

V4_GOAL4698_COMPILE_STAGES = (
    "contract_validation",
    "numba_ptx_generation",
    "callback_symbol_extraction",
    "wrapper_specialization",
    "nvcc_wrapper_compile",
    "optix_module_create",
    "program_group_create",
    "pipeline_create",
    "launch_validation",
)

_NUMBA_ENV_VERSION_RE = re.compile(r"B2v[0-9]+")


@dataclass(frozen=True)
class V4Goal4698CompilePlan:
    callback_shape: str
    accepted: bool
    stage: str
    cache_key: str | None
    cache_components: dict[str, str]
    error_code: str | None
    error_message: str | None
    internal_compile_allowed: bool
    tier3_public_support_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "callback_shape": self.callback_shape,
            "accepted": self.accepted,
            "stage": self.stage,
            "cache_key": self.cache_key,
            "cache_components": self.cache_components,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "internal_compile_allowed": self.internal_compile_allowed,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonicalize_v4_goal4698_callback_ptx_for_cache(ptx: str) -> str:
    """Normalize known non-semantic Numba PTX cache-key drift."""

    normalized_lines: list[str] = []
    for line in str(ptx).splitlines():
        if "NumbaEnv" in line:
            line = _NUMBA_ENV_VERSION_RE.sub("B2vX", line)
        normalized_lines.append(line.rstrip())
    return "\n".join(normalized_lines).strip() + "\n"


def v4_goal4698_specialized_tier3_cache_key(
    *,
    callback_symbol: str,
    callback_ptx: str,
    toolchain_fingerprint: str,
    optix_abi: str,
    compute_target: str,
    wrapper_strategy: str = "specialize_hit_program_module_and_call_callback_as_direct_device_function",
    contract_version: str = V4_GOAL4698_CACHE_CONTRACT_VERSION,
) -> tuple[str, dict[str, str]]:
    canonical_ptx = canonicalize_v4_goal4698_callback_ptx_for_cache(callback_ptx)
    components = {
        "contract_version": contract_version,
        "callback_symbol": str(callback_symbol).strip(),
        "callback_ptx_sha256": _sha256_text(canonical_ptx),
        "callback_ptx_raw_sha256": _sha256_text(callback_ptx),
        "callback_ptx_cache_canonicalization": "numba_env_b2v_version_token_normalized",
        "toolchain_fingerprint_sha256": _sha256_text(toolchain_fingerprint),
        "optix_abi": str(optix_abi).strip(),
        "compute_target": str(compute_target).strip(),
        "wrapper_strategy": wrapper_strategy,
    }
    key_component_names = tuple(key for key in sorted(components) if key != "callback_ptx_raw_sha256")
    serialized = "\n".join(f"{key}={components[key]}" for key in key_component_names)
    return "rtdl-v4-tier3-" + _sha256_text(serialized)[:32], components


def v4_goal4698_error_code_for_rejection(status: str) -> str:
    suffix = str(status).replace("rejected_goal4697_", "").upper()
    return f"{V4_GOAL4698_ERROR_REJECTED}_{suffix}"


def classify_v4_goal4698_compile_failure(stage: str, message: str) -> dict[str, object]:
    normalized_stage = str(stage).strip().lower()
    known = normalized_stage in V4_GOAL4698_COMPILE_STAGES
    return {
        "status": "classified_compile_failure" if known else "unclassified_compile_failure",
        "stage": normalized_stage if known else "unknown",
        "error_code": (
            f"{V4_GOAL4698_ERROR_COMPILE_FAILED}_{normalized_stage.upper()}"
            if known
            else f"{V4_GOAL4698_ERROR_COMPILE_FAILED}_UNKNOWN"
        ),
        "message": str(message),
        "tier3_public_support_authorized": False,
        "release_authorized": False,
    }


def plan_v4_goal4698_specialized_tier3_compile(
    *,
    callback_shape: str,
    callback_language: str = "numba",
    numba_cabi_device_function: bool = False,
    callback_symbol: str | None = None,
    callback_ptx: str | None = None,
    toolchain_fingerprint: str | None = None,
    optix_abi: str = "8.0",
    compute_target: str = "sm_86",
    returns_scalar: bool = True,
    scalar_arguments_only: bool = True,
    mutates_shared_state: bool = False,
    writes_external_memory: bool = False,
    dynamic_allocation: bool = False,
    variable_length_output: bool = False,
    sbt_direct_callable_hot_path: bool = False,
    raw_optix_callback: bool = False,
    action_semantics: bool = False,
) -> V4Goal4698CompilePlan:
    contract_plan = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape=callback_shape,
        callback_language=callback_language,
        numba_cabi_device_function=numba_cabi_device_function,
        returns_scalar=returns_scalar,
        scalar_arguments_only=scalar_arguments_only,
        mutates_shared_state=mutates_shared_state,
        writes_external_memory=writes_external_memory,
        dynamic_allocation=dynamic_allocation,
        variable_length_output=variable_length_output,
        sbt_direct_callable_hot_path=sbt_direct_callable_hot_path,
        raw_optix_callback=raw_optix_callback,
        action_semantics=action_semantics,
    )
    if contract_plan.status != V4_GOAL4697_ACCEPTED_STATUS:
        return V4Goal4698CompilePlan(
            callback_shape=contract_plan.callback_shape,
            accepted=False,
            stage=V4_GOAL4698_REJECTED_STAGE,
            cache_key=None,
            cache_components={},
            error_code=v4_goal4698_error_code_for_rejection(contract_plan.status),
            error_message=contract_plan.reason,
            internal_compile_allowed=False,
        )

    missing_inputs = [
        name
        for name, value in (
            ("callback_symbol", callback_symbol),
            ("callback_ptx", callback_ptx),
            ("toolchain_fingerprint", toolchain_fingerprint),
        )
        if not str(value or "").strip()
    ]
    if missing_inputs:
        return V4Goal4698CompilePlan(
            callback_shape=contract_plan.callback_shape,
            accepted=True,
            stage=V4_GOAL4698_INCOMPLETE_STAGE,
            cache_key=None,
            cache_components={},
            error_code=V4_GOAL4698_ERROR_INCOMPLETE_INPUT,
            error_message="missing required compile inputs: " + ", ".join(missing_inputs),
            internal_compile_allowed=False,
        )

    cache_key, components = v4_goal4698_specialized_tier3_cache_key(
        callback_symbol=str(callback_symbol),
        callback_ptx=str(callback_ptx),
        toolchain_fingerprint=str(toolchain_fingerprint),
        optix_abi=optix_abi,
        compute_target=compute_target,
    )
    return V4Goal4698CompilePlan(
        callback_shape=contract_plan.callback_shape,
        accepted=True,
        stage=V4_GOAL4698_COMPILE_READY_STAGE,
        cache_key=cache_key,
        cache_components=components,
        error_code=None,
        error_message=None,
        internal_compile_allowed=True,
    )


def validate_v4_goal4698_specialized_tier3_compile_cache() -> dict[str, object]:
    accepted = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="_ZN8__main__21_custom_scalar_reduce_sample",
        callback_ptx=".version 8.0\n.visible .func callback(){ret;}\n",
        toolchain_fingerprint="python=3.12;numba=0.65.1;cuda=12.9;optix=8.0;driver=570.195.03",
        optix_abi="8.0",
        compute_target="sm_86",
    )
    accepted_again = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="_ZN8__main__21_custom_scalar_reduce_sample",
        callback_ptx=".version 8.0\n.visible .func callback(){ret;}\n",
        toolchain_fingerprint="python=3.12;numba=0.65.1;cuda=12.9;optix=8.0;driver=570.195.03",
        optix_abi="8.0",
        compute_target="sm_86",
    )
    changed_ptx = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="_ZN8__main__21_custom_scalar_reduce_sample",
        callback_ptx=".version 8.0\n.visible .func callback(){ret;}\n// changed\n",
        toolchain_fingerprint="python=3.12;numba=0.65.1;cuda=12.9;optix=8.0;driver=570.195.03",
        optix_abi="8.0",
        compute_target="sm_86",
    )
    changed_numba_env_version_only = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="_ZN8__main__21_custom_scalar_reduce_sample",
        callback_ptx=(
            ".version 8.0\n"
            ".common .global .align 8 .u64 _ZN08NumbaEnv21_custom_scalar_reduceB2v1B96;\n"
            ".visible .func callback(){ret;}\n"
        ),
        toolchain_fingerprint="python=3.12;numba=0.65.1;cuda=12.9;optix=8.0;driver=570.195.03",
        optix_abi="8.0",
        compute_target="sm_86",
    )
    changed_numba_env_version_again = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="_ZN8__main__21_custom_scalar_reduce_sample",
        callback_ptx=(
            ".version 8.0\n"
            ".common .global .align 8 .u64 _ZN08NumbaEnv21_custom_scalar_reduceB2v2B96;\n"
            ".visible .func callback(){ret;}\n"
        ),
        toolchain_fingerprint="python=3.12;numba=0.65.1;cuda=12.9;optix=8.0;driver=570.195.03",
        optix_abi="8.0",
        compute_target="sm_86",
    )
    rejected = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_action",
        callback_language="numba",
        numba_cabi_device_function=True,
        mutates_shared_state=True,
    )
    incomplete = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
    )
    failure = classify_v4_goal4698_compile_failure("optix_module_create", "No functions with semantic types found")

    missing: list[str] = []
    if accepted.stage != V4_GOAL4698_COMPILE_READY_STAGE or not accepted.internal_compile_allowed:
        missing.append("accepted_compile_ready")
    if accepted.cache_key != accepted_again.cache_key:
        missing.append("cache_key_determinism")
    if accepted.cache_key == changed_ptx.cache_key:
        missing.append("cache_key_ptx_sensitivity")
    if changed_numba_env_version_only.cache_key != changed_numba_env_version_again.cache_key:
        missing.append("cache_key_numba_env_version_canonicalization")
    if rejected.stage != V4_GOAL4698_REJECTED_STAGE or rejected.error_code is None:
        missing.append("rejected_before_compile")
    if incomplete.stage != V4_GOAL4698_INCOMPLETE_STAGE:
        missing.append("incomplete_inputs")
    if failure["status"] != "classified_compile_failure":
        missing.append("failure_classification")
    for plan_name, plan in (("accepted", accepted), ("rejected", rejected), ("incomplete", incomplete)):
        payload = plan.as_dict()
        for key in ("tier3_public_support_authorized", "raw_optix_callback_authorized", "release_authorized", "performance_claim_authorized"):
            if payload[key] is not False:
                missing.append(f"{plan_name}_{key}")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4698_SPECIALIZED_TIER3_COMPILE_CACHE_STATUS,
        "accepted_plan": accepted.as_dict(),
        "changed_ptx_plan": changed_ptx.as_dict(),
        "changed_numba_env_version_only_plan": changed_numba_env_version_only.as_dict(),
        "changed_numba_env_version_again_plan": changed_numba_env_version_again.as_dict(),
        "rejected_plan": rejected.as_dict(),
        "incomplete_plan": incomplete.as_dict(),
        "compile_failure_classification": failure,
        "next_goal": V4_GOAL4698_NEXT_GOAL,
    }


__all__ = [
    "V4_GOAL4698_SPECIALIZED_TIER3_COMPILE_CACHE_STATUS",
    "V4_GOAL4698_NEXT_GOAL",
    "V4_GOAL4698_CACHE_CONTRACT_VERSION",
    "V4_GOAL4698_COMPILE_READY_STAGE",
    "V4_GOAL4698_REJECTED_STAGE",
    "V4_GOAL4698_INCOMPLETE_STAGE",
    "V4Goal4698CompilePlan",
    "canonicalize_v4_goal4698_callback_ptx_for_cache",
    "v4_goal4698_specialized_tier3_cache_key",
    "v4_goal4698_error_code_for_rejection",
    "classify_v4_goal4698_compile_failure",
    "plan_v4_goal4698_specialized_tier3_compile",
    "validate_v4_goal4698_specialized_tier3_compile_cache",
]
