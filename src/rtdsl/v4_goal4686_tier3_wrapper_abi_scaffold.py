from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4686_TIER3_WRAPPER_ABI_SCAFFOLD_STATUS = (
    "goal4686_tier3_wrapper_abi_local_scaffold_complete_no_pod"
)
V4_GOAL4686_NEXT_GOAL = "Goal4687 tier3 wrapper ABI symbol extraction and compile probe"
V4_GOAL4686_CALLBACK_SYMBOL = "rtdl_user_scalar_reduce"


SEMANTIC_OPTIX_WRAPPER_SOURCE = r"""
#include <optix.h>
#include <optix_device.h>

extern "C" __device__ double rtdl_user_scalar_reduce(
    double hit_t,
    unsigned int primitive_id,
    double payload0,
    double state0);

struct RtdlTier3ProbeParams {
    double* output_state;
};

extern "C" {
__constant__ RtdlTier3ProbeParams params;
}

extern "C" __device__ __noinline__ void __direct_callable__rtdl_tier3_scalar_reduce() {
    double value = rtdl_user_scalar_reduce(1.0, 0u, 2.0, 3.0);
    if (params.output_state != nullptr) {
        params.output_state[0] = value;
    }
}

extern "C" __global__ void __raygen__rtdl_tier3_probe() {
    // Minimal semantic entry for module/pipeline creation. Goal4689 owns the
    // first optixDirectCall launch probe.
}

extern "C" __global__ void __miss__rtdl_tier3_probe() {
}

extern "C" __global__ void __closesthit__rtdl_tier3_probe() {
}
""".strip()


@dataclass(frozen=True)
class V4Goal4686Tier3WrapperAbiScaffold:
    status: str
    callback_symbol: str
    semantic_entries: tuple[str, ...]
    wrapper_source: str
    composition_strategy: tuple[str, ...]
    next_goal: str
    old_bare_ptx_success_path_allowed: bool = False
    local_scaffold_complete: bool = True
    pod_authorized: bool = False
    tier3_public_support_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_identity_kernel_authorized: bool = False

    def as_dict(self, *, include_source: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": self.status,
            "callback_symbol": self.callback_symbol,
            "semantic_entries": self.semantic_entries,
            "composition_strategy": self.composition_strategy,
            "next_goal": self.next_goal,
            "old_bare_ptx_success_path_allowed": self.old_bare_ptx_success_path_allowed,
            "local_scaffold_complete": self.local_scaffold_complete,
            "pod_authorized": self.pod_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_identity_kernel_authorized": self.app_identity_kernel_authorized,
        }
        if include_source:
            payload["wrapper_source"] = self.wrapper_source
        return payload


def v4_goal4686_tier3_wrapper_abi_scaffold() -> V4Goal4686Tier3WrapperAbiScaffold:
    return V4Goal4686Tier3WrapperAbiScaffold(
        status=V4_GOAL4686_TIER3_WRAPPER_ABI_SCAFFOLD_STATUS,
        callback_symbol=V4_GOAL4686_CALLBACK_SYMBOL,
        semantic_entries=(
            "__direct_callable__rtdl_tier3_scalar_reduce",
            "__raygen__rtdl_tier3_probe",
            "__miss__rtdl_tier3_probe",
            "__closesthit__rtdl_tier3_probe",
        ),
        wrapper_source=SEMANTIC_OPTIX_WRAPPER_SOURCE,
        composition_strategy=(
            "compile a constrained Numba scalar device callback to PTX",
            "extract or alias the callback symbol to rtdl_user_scalar_reduce",
            "compile the semantic OptiX wrapper source with direct-callable and launch entries",
            "link callback PTX and wrapper PTX/OptiX-IR into one OptiX pipeline",
            "create direct-callable, raygen, miss, and hitgroup program groups",
            "launch the semantic probe before any performance or support claim",
        ),
        next_goal=(
            "Goal4687 must prove symbol extraction/aliasing and compile the semantic "
            "wrapper shape. It still must not claim Tier-3 support or run a full POD "
            "overhead benchmark until the compile/link gate passes."
        ),
    )


def validate_v4_goal4686_tier3_wrapper_abi_scaffold() -> dict[str, object]:
    scaffold = v4_goal4686_tier3_wrapper_abi_scaffold()
    payload = scaffold.as_dict()
    source = str(payload["wrapper_source"])
    entries = tuple(str(item) for item in payload["semantic_entries"])
    strategy = " ".join(str(item) for item in payload["composition_strategy"])
    missing: list[str] = []
    if payload["status"] != V4_GOAL4686_TIER3_WRAPPER_ABI_SCAFFOLD_STATUS:
        missing.append("status")
    for entry in (
        "__direct_callable__rtdl_tier3_scalar_reduce",
        "__raygen__rtdl_tier3_probe",
        "__miss__rtdl_tier3_probe",
        "__closesthit__rtdl_tier3_probe",
    ):
        if entry not in entries or entry not in source:
            missing.append(entry)
    if V4_GOAL4686_CALLBACK_SYMBOL not in source:
        missing.append("callback_symbol")
    if "optix_device.h" not in source:
        missing.append("optix_device_include")
    if "semantic OptiX wrapper" not in strategy:
        missing.append("semantic_wrapper_strategy")
    if "link callback PTX and wrapper" not in strategy:
        missing.append("link_strategy")
    if payload.get("old_bare_ptx_success_path_allowed") is not False:
        missing.append("old_bare_ptx_success_path_allowed")
    if payload.get("local_scaffold_complete") is not True:
        missing.append("local_scaffold_complete")
    for key in (
        "pod_authorized",
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
        "scaffold": scaffold.as_dict(include_source=False),
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4686_TIER3_WRAPPER_ABI_SCAFFOLD_STATUS",
    "V4_GOAL4686_NEXT_GOAL",
    "V4_GOAL4686_CALLBACK_SYMBOL",
    "SEMANTIC_OPTIX_WRAPPER_SOURCE",
    "V4Goal4686Tier3WrapperAbiScaffold",
    "v4_goal4686_tier3_wrapper_abi_scaffold",
    "validate_v4_goal4686_tier3_wrapper_abi_scaffold",
]
