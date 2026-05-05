from __future__ import annotations

from typing import Any


def polygon_set_jaccard_optix_slower_reason(
    *,
    embree_payload: dict[str, Any],
    optix_payload: dict[str, Any],
) -> dict[str, Any]:
    """Explain bounded Jaccard OptiX-vs-Embree timing without authorizing claims."""
    embree_phases = dict(embree_payload["run_phases"])
    optix_phases = dict(optix_payload["run_phases"])
    embree_candidate_sec = float(embree_phases["rt_candidate_discovery_sec"])
    optix_candidate_sec = float(optix_phases["rt_candidate_discovery_sec"])
    embree_score_sec = float(embree_phases["native_exact_continuation_sec"])
    optix_score_sec = float(optix_phases["native_exact_continuation_sec"])
    embree_total_sec = embree_candidate_sec + embree_score_sec
    optix_total_sec = optix_candidate_sec + optix_score_sec
    embree_summary = dict(embree_payload["summary"])
    optix_summary = dict(optix_payload["summary"])
    same_summary = embree_summary == optix_summary
    return {
        "app": "polygon_set_jaccard",
        "status": "optix_slower_reason_recorded",
        "same_exact_summary": same_summary,
        "embree_candidate_row_count": int(embree_payload["candidate_row_count"]),
        "optix_candidate_row_count": int(optix_payload["candidate_row_count"]),
        "embree_candidate_discovery_sec": embree_candidate_sec,
        "optix_candidate_discovery_sec": optix_candidate_sec,
        "candidate_discovery_slowdown": (
            None if embree_candidate_sec == 0.0 else optix_candidate_sec / embree_candidate_sec
        ),
        "embree_native_exact_continuation_sec": embree_score_sec,
        "optix_native_exact_continuation_sec": optix_score_sec,
        "native_exact_continuation_slowdown": (
            None if embree_score_sec == 0.0 else optix_score_sec / embree_score_sec
        ),
        "embree_observed_pipeline_sec": embree_total_sec,
        "optix_observed_pipeline_sec": optix_total_sec,
        "observed_pipeline_slowdown": None if embree_total_sec == 0.0 else optix_total_sec / embree_total_sec,
        "reason": (
            "The bounded Jaccard path is not a monolithic GPU Jaccard kernel. It performs "
            "multi-pass RT-assisted candidate discovery, transfers/normalizes candidate-pair IDs, "
            "then runs native exact set-area scoring. In the recorded pod run, OptiX produced a "
            "smaller complete candidate set than Embree but spent more time in candidate discovery "
            "and exact native continuation, so final correctness matched while observed performance "
            "remained slower."
        ),
        "claim_boundary": (
            "Correctness-ready diagnostic only; no positive Jaccard speedup wording, no whole-app "
            "GIS claim, and no native device-level Jaccard reduction promotion."
        ),
    }


def validate_polygon_set_jaccard_optix_slower_reason(reason: dict[str, Any]) -> dict[str, Any]:
    required_fields = (
        "app",
        "status",
        "same_exact_summary",
        "embree_candidate_row_count",
        "optix_candidate_row_count",
        "embree_candidate_discovery_sec",
        "optix_candidate_discovery_sec",
        "embree_native_exact_continuation_sec",
        "optix_native_exact_continuation_sec",
        "reason",
        "claim_boundary",
    )
    for field in required_fields:
        if field not in reason:
            raise ValueError(f"missing Jaccard performance diagnostic field: {field}")
    if reason["app"] != "polygon_set_jaccard":
        raise ValueError("Jaccard performance diagnostic app must be polygon_set_jaccard")
    if reason["status"] != "optix_slower_reason_recorded":
        raise ValueError("Jaccard performance diagnostic must record optix_slower_reason_recorded")
    if reason["same_exact_summary"] is not True:
        raise ValueError("Jaccard performance diagnostic requires exact summary parity")
    if float(reason["optix_candidate_discovery_sec"]) <= float(reason["embree_candidate_discovery_sec"]):
        raise ValueError("diagnostic must record OptiX candidate discovery as slower than Embree")
    if "no positive Jaccard speedup wording" not in str(reason["claim_boundary"]):
        raise ValueError("Jaccard diagnostic must block positive public speedup wording")
    return reason
