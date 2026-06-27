from __future__ import annotations

from dataclasses import dataclass
import re

from .v4_goal4686_tier3_wrapper_abi_scaffold import SEMANTIC_OPTIX_WRAPPER_SOURCE
from .v4_goal4686_tier3_wrapper_abi_scaffold import V4_GOAL4686_CALLBACK_SYMBOL


V4_GOAL4687_TIER3_WRAPPER_COMPILE_PROBE_STATUS = (
    "goal4687_tier3_wrapper_symbol_compile_probe_not_support"
)
V4_GOAL4687_NEXT_GOAL = "Goal4688 tier3 semantic wrapper OptiX module-link probe"

_FUNC_RE = re.compile(r"\.func\b(?P<body>[^\\{;]*?)(?P<name>[A-Za-z_.$][A-Za-z0-9_.$]*)\s*\(")
_C_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class V4Goal4687SymbolProbe:
    status: str
    symbol: str | None
    c_identifier_compatible: bool
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "symbol": self.symbol,
            "c_identifier_compatible": self.c_identifier_compatible,
            "reason": self.reason,
        }


def extract_numba_callback_symbol_from_ptx(
    ptx: str,
    *,
    callback_name_hint: str = "custom_scalar_reduce",
) -> V4Goal4687SymbolProbe:
    """Extract the PTX function symbol for the constrained Numba callback."""

    matches: list[str] = []
    for match in _FUNC_RE.finditer(ptx):
        name = match.group("name")
        if callback_name_hint in name:
            matches.append(name)
    if len(matches) == 1:
        symbol = matches[0]
        return V4Goal4687SymbolProbe(
            status="symbol_extracted",
            symbol=symbol,
            c_identifier_compatible=bool(_C_IDENTIFIER_RE.match(symbol)),
            reason="one PTX .func symbol matched the callback name hint",
        )
    if not matches:
        return V4Goal4687SymbolProbe(
            status="symbol_not_found",
            symbol=None,
            c_identifier_compatible=False,
            reason="no PTX .func symbol matched the callback name hint",
        )
    return V4Goal4687SymbolProbe(
        status="symbol_ambiguous",
        symbol=None,
        c_identifier_compatible=False,
        reason=f"{len(matches)} PTX .func symbols matched the callback name hint",
    )


def specialize_semantic_wrapper_source(callback_symbol: str) -> str:
    """Return the semantic wrapper source bound to the extracted callback symbol."""

    if not _C_IDENTIFIER_RE.match(callback_symbol):
        raise ValueError(f"callback symbol is not a C-compatible identifier: {callback_symbol!r}")
    return SEMANTIC_OPTIX_WRAPPER_SOURCE.replace(V4_GOAL4686_CALLBACK_SYMBOL, callback_symbol)


def validate_v4_goal4687_tier3_wrapper_compile_probe_contract() -> dict[str, object]:
    sample_ptx = """
.visible .func  (.param .b64 func_retval0) _ZN8__main__21_custom_scalar_reduce_sample(
    .param .b64 _ZN8__main__21_custom_scalar_reduce_sample_param_0
)
{
    ret;
}
"""
    probe = extract_numba_callback_symbol_from_ptx(sample_ptx)
    missing: list[str] = []
    if probe.status != "symbol_extracted":
        missing.append("sample_symbol_extraction")
    if probe.symbol is None:
        missing.append("sample_symbol")
    if not probe.c_identifier_compatible:
        missing.append("sample_symbol_c_identifier")
    specialized = specialize_semantic_wrapper_source(probe.symbol or "_missing_symbol")
    if probe.symbol and probe.symbol not in specialized:
        missing.append("specialized_symbol")
    if V4_GOAL4686_CALLBACK_SYMBOL in specialized:
        missing.append("placeholder_removed")
    for entry in (
        "__direct_callable__rtdl_tier3_scalar_reduce",
        "__raygen__rtdl_tier3_probe",
        "__miss__rtdl_tier3_probe",
        "__closesthit__rtdl_tier3_probe",
    ):
        if entry not in specialized:
            missing.append(entry)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "probe_status": probe.as_dict(),
        "goal_status": V4_GOAL4687_TIER3_WRAPPER_COMPILE_PROBE_STATUS,
        "next_goal": V4_GOAL4687_NEXT_GOAL,
        "pod_authorized": False,
        "tier3_public_support_authorized": False,
        "raw_optix_callback_authorized": False,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4687_TIER3_WRAPPER_COMPILE_PROBE_STATUS",
    "V4_GOAL4687_NEXT_GOAL",
    "V4Goal4687SymbolProbe",
    "extract_numba_callback_symbol_from_ptx",
    "specialize_semantic_wrapper_source",
    "validate_v4_goal4687_tier3_wrapper_compile_probe_contract",
]
