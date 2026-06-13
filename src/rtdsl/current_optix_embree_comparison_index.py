from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .current_benchmark_scale_profiles import (
    CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
    current_benchmark_scale_profiles,
)
from .current_embree_cpu_partner_reference import (
    CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
    current_embree_cpu_partner_reference_rows,
)
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_VERSION = (
    "rtdl.v2_12.current_optix_embree_comparison_index.goal4359.v1"
)
CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_STATUS = (
    "internal_cross_backend_comparison_index_not_speedup_authorization"
)
CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_CLAIM_BOUNDARY = (
    "Goal4338 indexes the current NVIDIA OptiX scale-profile evidence beside the "
    "current Embree CPU reference registry. It is a comparability and planning "
    "packet, not a public speedup table. It does not authorize release action, "
    "package-install wording, public speedup wording, whole-app acceleration "
    "wording, broad RT-core wording, Intel GPU performance wording, paper "
    "reproduction wording, true-zero-copy wording, automatic partner selection, "
    "or app-specific native-engine logic."
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPTIX_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal4329_current_pod_validation" / "scale_summary_allpass.json"
)
DEFAULT_EMBREE_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal4298_v2_11_embree_cpu_partner_reference_local_linux.json"
)
DEFAULT_RAYJOIN_SAME_STREAM_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13"
    / "summary.json"
)


COMPARISON_GAPS: dict[str, dict[str, str]] = {
    "hausdorff_xhd": {
        "comparison_class": "contract_split_pair_required",
        "reason": (
            "OptiX evidence is a prepared threshold-decision route at 1024 copies; "
            "Embree evidence is an exact directed-summary route at 8 copies."
        ),
        "required_next_action": (
            "run the same directed-summary or same threshold-decision contract on "
            "both backends at the same point counts, copies, repeat, and warmup"
        ),
    },
    "spatial_rayjoin": {
        "comparison_class": "same_stream_scalar_count_pairs_available",
        "reason": (
            "Goal4358 adds RayJoin-exported same-stream LSI and PIP scalar-count "
            "pairs for RTDL OptiX and RTDL Embree. The older broad registry row "
            "is still mixed, so these ratios are scoped to the split scalar-count "
            "contracts rather than the whole RayJoin app."
        ),
        "required_next_action": (
            "use the Goal4358 LSI/PIP scalar-count pairs for internal backend "
            "comparison; keep overlay active-count and whole-app wording separate"
        ),
    },
    "rt_dbscan": {
        "comparison_class": "contract_split_pair_required",
        "reason": (
            "OptiX evidence is a 65K grouped-stream plus Numba signature route "
            "without CPU validation; Embree evidence is a tiny prepared-row route "
            "with Python continuation."
        ),
        "required_next_action": (
            "run a common fixed-radius neighbor-row or grouped-signature contract "
            "with matching validation and continuation policy on both backends"
        ),
    },
    "robot_collision": {
        "comparison_class": "same_contract_different_scale_pair_required",
        "reason": (
            "Both rows are prepared collision-count routes, but OptiX uses the "
            "scaled 1024-pose resident profile and Embree uses the tiny fixture."
        ),
        "required_next_action": (
            "run the scaled prepared-buffer/device-count contract on both backends "
            "with matching repeat, warmup, validation, and summary-only policy"
        ),
    },
    "contact_manifold": {
        "comparison_class": "same_contract_different_scale_pair_required",
        "reason": (
            "Both rows use bounded collect-k style discovery, but OptiX uses grid64 "
            "with witness capacity 128 and Embree uses the tiny fixture with capacity 8."
        ),
        "required_next_action": (
            "run the same grid size, witness capacity, repeat count, and backend "
            "contract on both backends"
        ),
    },
    "raydb_style": {
        "comparison_class": "same_contract_different_scale_pair_required",
        "reason": (
            "Both rows are primitive-first grouped count routes, but OptiX uses "
            "262144 generated rows / 1024 groups while Embree uses 4096 rows / 128 groups."
        ),
        "required_next_action": (
            "run identical generated row and group counts on both backends, with "
            "summary-only iteration policy held constant"
        ),
    },
    "barnes_hut": {
        "comparison_class": "contract_split_pair_required",
        "reason": (
            "OptiX scale evidence is currently the Numba exact-force partner route; "
            "Embree evidence is a node-coverage prepared decision route."
        ),
        "required_next_action": (
            "choose either exact-force partner continuation or prepared node coverage "
            "as the comparison contract, then run that one contract on both sides"
        ),
    },
    "librts_spatial_index": {
        "comparison_class": "same_contract_different_scale_pair_required",
        "reason": (
            "Both rows are prepared AABB-index routes, but OptiX uses 32768 boxes "
            "and queries with skip-counts while Embree uses 1024 boxes and queries "
            "with operation=all."
        ),
        "required_next_action": (
            "run identical box/query counts and operation policy; record whether "
            "count validation is enabled on both sides"
        ),
    },
    "rtnn": {
        "comparison_class": "contract_split_pair_required",
        "reason": (
            "OptiX evidence is a 3-D prepared ranked-summary route; the current "
            "Embree registry is a 2-D ANN candidate-quality front door, and the "
            "local artifact may still contain the older Numba CPU reference row."
        ),
        "required_next_action": (
            "refresh the current Embree artifact, then decide between 2-D ANN "
            "candidate quality and 3-D ranked-summary as the paired contract"
        ),
    },
    "triangle_counting": {
        "comparison_class": "same_contract_different_scale_pair_required",
        "reason": (
            "Both rows are native graph-summary style routes, but OptiX uses the "
            "RT-Graph 2A1 fixture at 2048 copies while Embree uses the default "
            "summary route at 128 copies."
        ),
        "required_next_action": (
            "run the same fixture, copy count, repeat, warmup, and output-mode "
            "on both backends"
        ),
    },
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_rows_by_id(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not payload:
        return {}
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("row_id")): row
        for row in rows
        if isinstance(row, dict) and row.get("row_id")
    }


def _artifact_row_summary(
    artifact_rows: dict[str, dict[str, Any]],
    row_id: str,
) -> dict[str, Any]:
    row = artifact_rows.get(row_id)
    if row is None:
        return {
            "row_id": row_id,
            "artifact_present": False,
            "status": "missing_current_row_artifact",
            "elapsed_sec": None,
            "claim_flag_violations": None,
        }
    semantic = row.get("semantic_stdout_check")
    violations = None
    if isinstance(semantic, dict):
        violations = semantic.get("claim_flag_violations")
    return {
        "row_id": row_id,
        "artifact_present": True,
        "status": row.get("status"),
        "elapsed_sec": row.get("elapsed_sec"),
        "claim_flag_violations": violations,
    }


def _rayjoin_same_stream_pairs(payload: dict[str, Any] | None) -> tuple[dict[str, Any], ...]:
    if not payload:
        return ()
    rtdl = payload.get("rtdl")
    if not isinstance(rtdl, dict):
        return ()
    pairs: list[dict[str, Any]] = []
    for workload in ("lsi", "pip"):
        workload_payload = rtdl.get(workload)
        if not isinstance(workload_payload, dict):
            continue
        backends = workload_payload.get("backends")
        if not isinstance(backends, dict):
            continue
        optix = backends.get("optix")
        embree = backends.get("embree")
        if not isinstance(optix, dict) or not isinstance(embree, dict):
            continue
        optix_ms = float(optix["hot_median_sec"]) * 1000.0
        embree_ms = float(embree["hot_median_sec"]) * 1000.0
        pairs.append(
            {
                "workload": workload,
                "contract": str(optix.get("output_contract")),
                "row_count": int(optix["row_count"]),
                "cross_backend_count_match": int(optix["row_count"]) == int(embree["row_count"]),
                "optix_hot_query_ms": optix_ms,
                "embree_hot_query_ms": embree_ms,
                "optix_faster_than_embree": embree_ms / optix_ms if optix_ms else float("inf"),
                "optix_execution_route": optix.get("execution_route"),
                "embree_execution_route": embree.get("execution_route"),
                "ratio_authorization": "internal_same_stream_scalar_count_only_not_public_claim",
            }
        )
    return tuple(pairs)


def current_optix_embree_comparison_index(
    *,
    optix_artifact_path: Path | None = None,
    embree_artifact_path: Path | None = None,
    rayjoin_same_stream_artifact_path: Path | None = None,
) -> dict[str, Any]:
    optix_path = optix_artifact_path or DEFAULT_OPTIX_ARTIFACT
    embree_path = embree_artifact_path or DEFAULT_EMBREE_ARTIFACT
    rayjoin_path = rayjoin_same_stream_artifact_path or DEFAULT_RAYJOIN_SAME_STREAM_ARTIFACT
    optix_artifact = _load_json(optix_path)
    embree_artifact = _load_json(embree_path)
    rayjoin_artifact = _load_json(rayjoin_path)
    optix_artifact_rows = _artifact_rows_by_id(optix_artifact)
    embree_artifact_rows = _artifact_rows_by_id(embree_artifact)
    rayjoin_same_stream_pairs = _rayjoin_same_stream_pairs(rayjoin_artifact)

    optix_registry = {row["app"]: row for row in current_benchmark_scale_profiles()}
    embree_registry = {row["app"]: row for row in current_embree_cpu_partner_reference_rows()}

    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for app in V2_8_PROMOTED_BENCHMARK_APPS:
        optix = optix_registry.get(app)
        embree = embree_registry.get(app)
        gap = COMPARISON_GAPS[app]
        if optix is None:
            errors.append(f"{app}: missing OptiX scale-profile registry row")
            continue
        if embree is None:
            errors.append(f"{app}: missing Embree CPU reference registry row")
            continue

        optix_artifact_summary = _artifact_row_summary(optix_artifact_rows, optix["row_id"])
        embree_artifact_summary = _artifact_row_summary(embree_artifact_rows, embree["row_id"])
        if optix_artifact_summary["claim_flag_violations"] not in (None, []):
            errors.append(f"{app}: OptiX artifact reports claim-boundary violations")
        if embree_artifact_summary["claim_flag_violations"] not in (None, []):
            errors.append(f"{app}: Embree artifact reports claim-boundary violations")

        ratio_authorized = False
        same_stream_pairs: tuple[dict[str, Any], ...] = ()
        if app == "spatial_rayjoin":
            same_stream_pairs = rayjoin_same_stream_pairs
            ratio_authorized = len(same_stream_pairs) == 2 and all(
                bool(pair["cross_backend_count_match"]) for pair in same_stream_pairs
            )
            if not ratio_authorized:
                errors.append("spatial_rayjoin: missing accepted Goal4358 same-stream LSI/PIP pair evidence")

        rows.append(
            {
                "app": app,
                "optix": {
                    "registry_version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
                    "row_id": optix["row_id"],
                    "requires_numba": optix["requires_numba"],
                    "purpose": optix["purpose"],
                    "artifact": optix_artifact_summary,
                },
                "embree_cpu": {
                    "registry_version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
                    "row_id": embree["row_id"],
                    "uses_numba": embree["uses_numba"],
                    "route_class": embree["route_class"],
                    "purpose": embree["purpose"],
                    "artifact": embree_artifact_summary,
                },
                "comparison_class": gap["comparison_class"],
                "reason_existing_artifacts_are_not_speedup_grade": gap["reason"],
                "required_next_action": gap["required_next_action"],
                "same_stream_scalar_count_pairs": same_stream_pairs,
                "ratio_authorized_from_existing_artifacts": ratio_authorized,
                "ratio_authorization_scope": (
                    "internal_same_stream_scalar_count_only_not_public_claim"
                    if ratio_authorized
                    else "not_authorized"
                ),
                "public_speedup_claim_authorized": False,
                "release_authorized": False,
            }
        )

    missing_artifacts = [
        row
        for row in rows
        if not row["optix"]["artifact"]["artifact_present"]
        or not row["embree_cpu"]["artifact"]["artifact_present"]
    ]
    comparable_without_new_run = [
        row for row in rows if row["ratio_authorized_from_existing_artifacts"]
    ]
    if {row["app"] for row in comparable_without_new_run} - {"spatial_rayjoin"}:
        errors.append("only Goal4358 Spatial RayJoin same-stream ratios may be authorized here")
    if comparable_without_new_run and len(rayjoin_same_stream_pairs) != 2:
        errors.append("Spatial RayJoin ratio authorization requires two same-stream scalar-count pairs")

    validation = {
        "version": CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len({row["app"] for row in rows}),
        "row_count": len(rows),
        "missing_current_artifact_count": len(missing_artifacts),
        "authorized_existing_artifact_ratio_count": len(comparable_without_new_run),
    }
    return {
        "version": CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_VERSION,
        "status": CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_STATUS,
        "claim_boundary": CURRENT_OPTIX_EMBREE_COMPARISON_INDEX_CLAIM_BOUNDARY,
        "optix_artifact_path": str(optix_path.relative_to(ROOT)) if optix_path.is_absolute() else str(optix_path),
        "embree_artifact_path": str(embree_path.relative_to(ROOT)) if embree_path.is_absolute() else str(embree_path),
        "rayjoin_same_stream_artifact_path": (
            str(rayjoin_path.relative_to(ROOT)) if rayjoin_path.is_absolute() else str(rayjoin_path)
        ),
        "rows": tuple(rows),
        "summary": {
            "app_count": len({row["app"] for row in rows}),
            "row_count": len(rows),
            "ratio_authorized_from_existing_artifacts_count": len(comparable_without_new_run),
            "same_stream_scalar_count_pair_count": len(rayjoin_same_stream_pairs),
            "missing_current_artifact_count": len(missing_artifacts),
            "same_stream_scalar_count_pairs_available_count": sum(
                1 for row in rows if row["comparison_class"] == "same_stream_scalar_count_pairs_available"
            ),
            "same_contract_different_scale_pair_required_count": sum(
                1 for row in rows if row["comparison_class"] == "same_contract_different_scale_pair_required"
            ),
            "contract_split_pair_required_count": sum(
                1 for row in rows if row["comparison_class"] == "contract_split_pair_required"
            ),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "validation": validation,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


def validate_current_optix_embree_comparison_index() -> dict[str, Any]:
    return current_optix_embree_comparison_index()["validation"]
