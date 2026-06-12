from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BACKEND_COMPARISON_CAMPAIGN_CLOSEOUT_VERSION = "rtdl.v2_11.backend_comparison_campaign_closeout.goal4345.v1"
BACKEND_COMPARISON_CAMPAIGN_CLOSEOUT_STATUS = (
    "internal_backend_comparison_campaign_closeout_not_release_or_public_speedup_authorization"
)
BACKEND_COMPARISON_CAMPAIGN_CLOSEOUT_CLAIM_BOUNDARY = (
    "Goal4345 closes the current internal RTDL OptiX-vs-Embree comparison "
    "campaign by summarizing the RT-core closeout, Embree scale closeout, and "
    "optimized comparison packet. It does not authorize release action, public "
    "speedup wording, whole-app acceleration wording, broad RT-core wording, "
    "Intel GPU performance wording, paper reproduction wording, true-zero-copy "
    "wording, automatic partner selection, or app-specific native-engine logic."
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RT_CORE_CLOSEOUT = ROOT / "docs" / "reports" / "goal4342_rt_core_optimization_closeout_2026-06-11.json"
DEFAULT_EMBREE_AUDIT = ROOT / "docs" / "reports" / "goal4343_embree_optimization_audit_2026-06-11.json"
DEFAULT_EMBREE_SCALE_PROBE = ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe_2026-06-11.json"
DEFAULT_COMPARISON_PACKET = (
    ROOT / "docs" / "reports" / "goal4341_optimized_embree_optix_comparison_packet_2026-06-11.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def backend_comparison_campaign_closeout(
    *,
    rt_core_closeout_path: Path | None = None,
    embree_audit_path: Path | None = None,
    embree_scale_probe_path: Path | None = None,
    comparison_packet_path: Path | None = None,
) -> dict[str, Any]:
    rt_core_path = rt_core_closeout_path or DEFAULT_RT_CORE_CLOSEOUT
    embree_path = embree_audit_path or DEFAULT_EMBREE_AUDIT
    scale_path = embree_scale_probe_path or DEFAULT_EMBREE_SCALE_PROBE
    comparison_path = comparison_packet_path or DEFAULT_COMPARISON_PACKET

    rt_core = _load_json(rt_core_path)
    embree = _load_json(embree_path)
    scale = _load_json(scale_path)
    comparison = _load_json(comparison_path)

    errors: list[str] = []
    for label, payload in {
        "rt_core_closeout": rt_core,
        "embree_audit": embree,
        "embree_scale_probe": scale,
        "comparison_packet": comparison,
    }.items():
        validation = payload.get("validation")
        if not isinstance(validation, dict) or validation.get("status") != "accept":
            errors.append(f"{label}: validation was not accept")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
        ):
            if payload.get(flag):
                errors.append(f"{label}: {flag} must remain false")

    rt_summary = dict(rt_core["summary"])
    embree_summary = dict(embree["summary"])
    scale_summary = dict(scale["summary"])
    comparison_summary = dict(comparison["summary"])

    if rt_summary.get("remaining_high_leverage_rt_core_implementation_work_count") != 0:
        errors.append("RT-core campaign still reports remaining high-leverage implementation work")
    if embree_summary.get("same_contract_scale_pair_needed_count") != 0:
        errors.append("Embree campaign still reports missing same-contract scale rows")
    if comparison_summary.get("contract_split_pair_required_count") != 4:
        errors.append("comparison packet should preserve four contract-choice blockers")

    partner_policy = {
        "default": "do_not_force_numba_universally",
        "pure_rtdl_table": (
            "Compare OptiX and Embree only on the native RTDL primitive/query phase "
            "with no app-level partner continuation in the timed metric."
        ),
        "configured_route_table": (
            "When the benchmark contract genuinely includes a continuation, hold the "
            "continuation contract fixed and label the row as RTDL+partner. Numba is "
            "acceptable for CPU/portable continuations when both sides use the same "
            "Numba work; GPU-resident CuPy/Triton continuations belong in explicitly "
            "labeled configured-route rows."
        ),
        "partner_only_rows": (
            "A partner-only row, such as the current Barnes-Hut Numba exact-force "
            "scale row, is not an OptiX-vs-Embree backend comparison."
        ),
        "automatic_partner_selection_authorized": False,
    }

    return {
        "version": BACKEND_COMPARISON_CAMPAIGN_CLOSEOUT_VERSION,
        "status": BACKEND_COMPARISON_CAMPAIGN_CLOSEOUT_STATUS,
        "claim_boundary": BACKEND_COMPARISON_CAMPAIGN_CLOSEOUT_CLAIM_BOUNDARY,
        "sources": {
            "rt_core_closeout": _relative(rt_core_path),
            "embree_audit": _relative(embree_path),
            "embree_scale_probe": _relative(scale_path),
            "comparison_packet": _relative(comparison_path),
        },
        "answers": {
            "ready_to_use_high_performance_nvidia_rt_cores": {
                "answer": "yes_internal_current_optix_paths",
                "evidence": (
                    "Goal4342 found no obvious remaining high-leverage OptiX/RT-core "
                    "implementation optimization for the current campaign."
                ),
                "boundary": (
                    "This is internal readiness for current benchmark routes, not "
                    "release authorization or public speedup wording."
                ),
            },
            "ready_to_use_high_performance_intel_embree_cpus": {
                "answer": "yes_for_native_embree_primitive_rows_with_contract_boundaries",
                "evidence": (
                    "Goal4340 fixed LibRTS AABB_INDEX_QUERY_2D; Goal4344 supplies the "
                    "five previously missing Embree scale rows; Goal4343 now reports "
                    "zero missing same-contract scale pairs."
                ),
                "boundary": (
                    "Four apps still require a contract choice before a serious "
                    "OptiX-vs-Embree ratio: Spatial RayJoin, RT-DBSCAN, Barnes-Hut, "
                    "and RTNN."
                ),
            },
            "serious_comparison_ready": {
                "answer": "yes_as_an_internal_bucketted_packet",
                "evidence": (
                    "Goal4341 separates one fully optimized LibRTS pair, three clean "
                    "same-contract query-ratio scale rows, two boundary-limited phase "
                    "rows, and four contract-choice/configured-route rows."
                ),
                "boundary": "No public speedup, release, or whole-app claim is authorized.",
            },
        },
        "comparison_buckets": {
            "fully_optimized_measured_pair_count": int(comparison_summary["measured_pair_count"]),
            "fresh_scale_comparison_row_count": int(comparison_summary["scale_comparison_row_count"]),
            "clean_internal_query_ratio_count": int(comparison_summary["internal_query_median_ratio_count"]),
            "boundary_limited_phase_ratio_count": int(comparison_summary["boundary_limited_phase_ratio_count"]),
            "contract_choice_blocker_count": int(comparison_summary["contract_split_pair_required_count"]),
            "embree_scale_artifact_count": int(scale_summary["embree_scale_artifact_count"]),
            "rt_core_remaining_high_leverage_work_count": int(
                rt_summary["remaining_high_leverage_rt_core_implementation_work_count"]
            ),
            "embree_same_contract_scale_pair_needed_count": int(
                embree_summary["same_contract_scale_pair_needed_count"]
            ),
        },
        "partner_policy": partner_policy,
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


def validate_backend_comparison_campaign_closeout() -> dict[str, Any]:
    return backend_comparison_campaign_closeout()["validation"]
