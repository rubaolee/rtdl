from __future__ import annotations

import re


V4_GOAL4688_TIER3_MODULE_LINK_PROBE_STATUS = (
    "goal4688_tier3_semantic_wrapper_module_link_probe_not_support"
)
V4_GOAL4688_NEXT_GOAL = "Goal4689 tier3 semantic wrapper minimal launch probe"
_FUNC_NAME_RE = re.compile(r"\.func\b(?P<body>[^\\{;]*?)(?P<name>[A-Za-z_.$][A-Za-z0-9_.$]*)\s*\(")


def _split_ptx_header_and_body(ptx: str) -> tuple[str, str]:
    lines = ptx.splitlines()
    body_start = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith((".visible", ".extern", ".func", ".entry")):
            body_start = index
            break
    else:
        return ptx, ""
    return "\n".join(lines[:body_start]).strip(), "\n".join(lines[body_start:]).strip()


def compose_goal4688_combined_ptx(callback_ptx: str, wrapper_ptx: str) -> str:
    """Compose callback and semantic wrapper PTX into one module candidate.

    This is intentionally conservative: keep the wrapper header/toolchain target,
    append the callback function body, then append the wrapper semantic entries.
    The resulting PTX is only a probe input for OptiX module creation, not a
    supported production linker.
    """

    wrapper_header, wrapper_body = _split_ptx_header_and_body(wrapper_ptx)
    _callback_header, callback_body = _split_ptx_header_and_body(callback_ptx)
    if not wrapper_header or not wrapper_body or not callback_body:
        raise ValueError("both callback and wrapper PTX must contain a header and body")
    for match in _FUNC_NAME_RE.finditer(callback_body):
        symbol = match.group("name")
        extern_pattern = re.compile(
            r"\.extern\s+\.func\b(?:(?!\n\s*(?:\.visible|\.entry|\.func|\.extern)).)*?"
            + re.escape(symbol)
            + r"\s*\([^;]*?\)\s*;",
            re.DOTALL,
        )
        wrapper_body = extern_pattern.sub(
            f"// rtdl goal4688 removed duplicate extern declaration for {symbol}",
            wrapper_body,
        )
    return "\n\n".join(
        (
            wrapper_header,
            "// rtdl goal4688 composed callback PTX body",
            callback_body,
            "// rtdl goal4688 semantic wrapper PTX body",
            wrapper_body,
            "",
        )
    )


def validate_v4_goal4688_tier3_module_link_probe_contract() -> dict[str, object]:
    callback_ptx = """
.version 8.0
.target sm_75
.address_size 64

.visible .func  (.param .b64 func_retval0) _ZN8__main__21_custom_scalar_reduce_sample(
    .param .b64 _ZN8__main__21_custom_scalar_reduce_sample_param_0
)
{
    ret;
}
"""
    wrapper_ptx = """
.version 8.0
.target sm_75
.address_size 64

.visible .func __direct_callable__rtdl_tier3_scalar_reduce()
{
    ret;
}
.visible .entry __raygen__rtdl_tier3_probe()
{
    ret;
}
"""
    combined = compose_goal4688_combined_ptx(callback_ptx, wrapper_ptx)
    missing: list[str] = []
    if "custom_scalar_reduce_sample" not in combined:
        missing.append("callback_body")
    if "__direct_callable__rtdl_tier3_scalar_reduce" not in combined:
        missing.append("direct_callable_entry")
    if "__raygen__rtdl_tier3_probe" not in combined:
        missing.append("raygen_entry")
    if combined.count(".version") != 1:
        missing.append("single_header")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4688_TIER3_MODULE_LINK_PROBE_STATUS,
        "next_goal": V4_GOAL4688_NEXT_GOAL,
        "pod_authorized": False,
        "tier3_public_support_authorized": False,
        "raw_optix_callback_authorized": False,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4688_TIER3_MODULE_LINK_PROBE_STATUS",
    "V4_GOAL4688_NEXT_GOAL",
    "compose_goal4688_combined_ptx",
    "validate_v4_goal4688_tier3_module_link_probe_contract",
]
