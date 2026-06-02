from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


V2_6_PARTNER_CHOICE_GUIDANCE_VERSION = "rtdl.v2_6.partner_choice_guidance.v1"
V2_6_PARTNER_CHOICE_GUIDANCE_STATUS = "internal_guidance_not_release_authorization"
V2_6_ALLOWED_RECOMMENDED_PARTNERS = ("rtdl_primitive", "cupy", "numba", "none")
V2_6_PARTNER_CHOICE_STATUSES = (
    "recommended_reference_path",
    "measured_reference_path",
    "contract_evidence_not_default",
    "future_candidate",
    "no_promoted_partner",
)
V2_6_PROMOTED_BENCHMARK_APPS = (
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "contact_manifold",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
)
V2_6_PARTNER_CHOICE_DOCS = (
    "docs/learn/partner_choice_for_custom_logic.md",
    "docs/learn/benchmark_partner_reference_matrix.md",
)
V2_6_PARTNER_CHOICE_EVIDENCE_REPORTS = (
    "docs/reports/goal3050_partner_choice_for_custom_logic_docs_and_benchmark_matrix_2026-06-02.md",
    "docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02.md",
)
V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY = (
    "v2.6 partner-choice guidance is advisory only. It records current "
    "benchmark recommendations and evidence boundaries. It does not select a "
    "partner for the user, authorize release, authorize broad CuPy or Numba "
    "speedup wording, authorize RT-core wording, authorize true-zero-copy "
    "wording, or authorize app-specific native-engine behavior."
)


@dataclass(frozen=True)
class V26PartnerChoiceGuidanceRow:
    benchmark_app: str
    continuation_shape: str
    primitive_first_path: str
    recommended_partner: str
    recommendation_status: str
    cupy_role: str
    numba_role: str
    evidence_goal: str
    evidence_artifact: str
    user_advice: str
    automatic_partner_selection_allowed: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    broad_partner_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    release_authorized: bool = False
    app_specific_native_engine_logic_authorized: bool = False

    def __post_init__(self) -> None:
        if self.benchmark_app not in V2_6_PROMOTED_BENCHMARK_APPS:
            raise ValueError("unknown promoted benchmark app")
        if self.recommended_partner not in V2_6_ALLOWED_RECOMMENDED_PARTNERS:
            raise ValueError("unsupported recommended partner")
        if self.recommendation_status not in V2_6_PARTNER_CHOICE_STATUSES:
            raise ValueError("unsupported recommendation status")
        if self.recommended_partner == "none" and self.recommendation_status != "no_promoted_partner":
            raise ValueError("none partner rows must use no_promoted_partner status")
        for field in (
            "automatic_partner_selection_allowed",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "broad_partner_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "release_authorized",
            "app_specific_native_engine_logic_authorized",
        ):
            if getattr(self, field):
                raise ValueError(f"partner-choice row must not authorize {field}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "guidance_version": V2_6_PARTNER_CHOICE_GUIDANCE_VERSION,
            "benchmark_app": self.benchmark_app,
            "continuation_shape": self.continuation_shape,
            "primitive_first_path": self.primitive_first_path,
            "recommended_partner": self.recommended_partner,
            "recommendation_status": self.recommendation_status,
            "cupy_role": self.cupy_role,
            "numba_role": self.numba_role,
            "evidence_goal": self.evidence_goal,
            "evidence_artifact": self.evidence_artifact,
            "user_advice": self.user_advice,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "broad_partner_speedup_claim_authorized": self.broad_partner_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "release_authorized": self.release_authorized,
            "app_specific_native_engine_logic_authorized": self.app_specific_native_engine_logic_authorized,
            "claim_boundary": V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY,
        }


V2_6_PARTNER_CHOICE_ROWS: tuple[V26PartnerChoiceGuidanceRow, ...] = (
    V26PartnerChoiceGuidanceRow(
        benchmark_app="hausdorff_xhd",
        continuation_shape="active_frontier_exact_distance",
        primitive_first_path="generic OptiX active-frontier nearest-witness primitive",
        recommended_partner="rtdl_primitive",
        recommendation_status="recommended_reference_path",
        cupy_role="CuPy grouped-grid CUDA-core baseline and fairness reference",
        numba_role="contract evidence for score rows and global argmax; not the current default",
        evidence_goal="Goal3046/Goal3048/Goal3052",
        evidence_artifact=(
            "docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/"
            "hausdorff_active_frontier_small_refresh.json"
        ),
        user_advice="Use active-frontier RTDL/OptiX first for this exact app contract; keep CuPy as the same-contract CUDA-core baseline.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="spatial_rayjoin",
        continuation_shape="row_stream_compact_mask",
        primitive_first_path="scalar count/parity or first-hit primitive when it answers the query",
        recommended_partner="numba",
        recommendation_status="recommended_reference_path",
        cupy_role="established CUDA baseline and app-owned exact continuation option",
        numba_role="Numba compact-mask row-stream continuation for pip, lsi, and overlay_seed",
        evidence_goal="Goal3003/Goal3052",
        evidence_artifact=(
            "docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/"
            "rayjoin_numba_compact_mask_1m.json"
        ),
        user_advice="Use the primitive-first scalar path when possible; choose Numba only when explicit row-stream compaction is part of the app.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="rt_dbscan",
        continuation_shape="component_labeling",
        primitive_first_path="fixed-radius/core-summary primitive for neighbor/core flags",
        recommended_partner="cupy",
        recommendation_status="measured_reference_path",
        cupy_role="measured component-continuation reference for current clustering rows",
        numba_role="future candidate for custom component logic; not promoted yet",
        evidence_goal="Goal2425 lineage",
        evidence_artifact="examples/v2_0/research_benchmarks/rt_dbscan/README.md",
        user_advice="Use RTDL for fixed-radius/core summaries and CuPy for the current measured component continuation.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="robot_collision",
        continuation_shape="pose_collision_flag_reduction",
        primitive_first_path="generic any-hit/collision flag primitive where supported",
        recommended_partner="none",
        recommendation_status="no_promoted_partner",
        cupy_role="possible app-owned flag reduction path, not promoted",
        numba_role="future candidate, not promoted",
        evidence_goal="Goal2480 lineage",
        evidence_artifact="examples/v2_0/research_benchmarks/robot_collision/README.md",
        user_advice="Keep primitive parity first; do not claim a promoted custom partner path yet.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="contact_manifold",
        continuation_shape="bounded_witness_filtering",
        primitive_first_path="bounded collect and fail-closed witness primitives",
        recommended_partner="none",
        recommendation_status="no_promoted_partner",
        cupy_role="possible witness filtering reference, not promoted",
        numba_role="future candidate, not promoted",
        evidence_goal="Goal2510 lineage",
        evidence_artifact="examples/v2_0/research_benchmarks/contact_manifold/README.md",
        user_advice="Preserve the bounded witness contract first; custom partner filtering needs new same-contract evidence.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="raydb_style",
        continuation_shape="unfused_grouped_minmax_count_sum_avg",
        primitive_first_path="fused columnar grouped reduction when it exactly matches the answer",
        recommended_partner="numba",
        recommendation_status="recommended_reference_path",
        cupy_role="conformance and older partner-row reference",
        numba_role="Numba v2.6 grouped count/sum/min/max/avg continuation lane",
        evidence_goal="Goal2995/Goal3052",
        evidence_artifact=(
            "docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/"
            "raydb_numba_minmax_1m.json"
        ),
        user_advice="Use fused RTDL summaries when exact; choose Numba for the unfused grouped scalar continuation shapes currently demonstrated.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="barnes_hut",
        continuation_shape="force_vector_continuation",
        primitive_first_path="aggregate-frontier collect primitive",
        recommended_partner="cupy",
        recommendation_status="measured_reference_path",
        cupy_role="active exact force-vector partner reference",
        numba_role="future candidate, not promoted",
        evidence_goal="Goal2905 lineage",
        evidence_artifact="examples/v2_0/research_benchmarks/barnes_hut/README.md",
        user_advice="Use RTDL for frontier collection and CuPy for the current force-vector reference continuation.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="librts_spatial_index",
        continuation_shape="mutable_index_query_policy",
        primitive_first_path="generic point/range query rows where supported",
        recommended_partner="none",
        recommendation_status="no_promoted_partner",
        cupy_role="possible app-owned continuation, not promoted",
        numba_role="future candidate, not promoted",
        evidence_goal="Goal2570 lineage",
        evidence_artifact="examples/v2_0/research_benchmarks/librts_spatial_index/README.md",
        user_advice="Treat this as a no-regression/index-policy study until a custom partner continuation is measured.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="rtnn",
        continuation_shape="ranked_summary_quality_probe",
        primitive_first_path="prepared fixed-radius ranked-summary primitive",
        recommended_partner="rtdl_primitive",
        recommendation_status="recommended_reference_path",
        cupy_role="CUDA-core all-pairs baseline and quality reference",
        numba_role="future candidate for custom ranking reductions, not promoted",
        evidence_goal="Goal2821/Goal2822 lineage",
        evidence_artifact="examples/v2_0/research_benchmarks/rtnn/README.md",
        user_advice="Use prepared RTDL ranked summaries first; keep CuPy for all-pairs baseline comparisons.",
    ),
    V26PartnerChoiceGuidanceRow(
        benchmark_app="triangle_counting",
        continuation_shape="candidate_row_compact_mask",
        primitive_first_path="native scalar triangle-count primitive for scalar answer",
        recommended_partner="numba",
        recommendation_status="recommended_reference_path",
        cupy_role="optional device geometry setup and baseline summary role",
        numba_role="Numba compact-mask candidate-row continuation",
        evidence_goal="Goal3000/Goal3052",
        evidence_artifact=(
            "docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/"
            "triangle_numba_compact_mask_1m.json"
        ),
        user_advice="Keep the scalar primitive as the scalar answer; choose Numba only for explicit candidate-row compaction.",
    ),
)


def v2_6_partner_choice_guidance() -> dict[str, Any]:
    rows = tuple(row.to_metadata() for row in V2_6_PARTNER_CHOICE_ROWS)
    return {
        "guidance_version": V2_6_PARTNER_CHOICE_GUIDANCE_VERSION,
        "status": V2_6_PARTNER_CHOICE_GUIDANCE_STATUS,
        "promoted_benchmark_apps": V2_6_PROMOTED_BENCHMARK_APPS,
        "docs": V2_6_PARTNER_CHOICE_DOCS,
        "evidence_reports": V2_6_PARTNER_CHOICE_EVIDENCE_REPORTS,
        "allowed_recommended_partners": V2_6_ALLOWED_RECOMMENDED_PARTNERS,
        "recommendation_statuses": V2_6_PARTNER_CHOICE_STATUSES,
        "rows": rows,
        "row_count": len(rows),
        "app_count": len({row["benchmark_app"] for row in rows}),
        "primitive_first_rule": "use_fused_generic_rtdl_primitive_when_it_exactly_expresses_the_answer",
        "partner_choice_rule": "users_choose_supported_partners_explicitly",
        "benchmark_role": "reference_or_recommended_implementations_require_same_contract_evidence",
        "triton_status": "ignored_for_current_recommended_paths",
        "automatic_partner_selection_allowed": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "broad_partner_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "release_authorized": False,
        "app_specific_native_engine_logic_authorized": False,
        "claim_boundary": V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY,
    }


def plan_v2_6_partner_choice(
    benchmark_app: str,
    continuation_shape: str | None = None,
) -> dict[str, Any]:
    normalized_app = str(benchmark_app).strip()
    normalized_shape = None if continuation_shape is None else str(continuation_shape).strip()
    matches = tuple(
        row.to_metadata()
        for row in V2_6_PARTNER_CHOICE_ROWS
        if row.benchmark_app == normalized_app
        and (normalized_shape is None or row.continuation_shape == normalized_shape)
    )
    if not matches:
        return {
            "guidance_version": V2_6_PARTNER_CHOICE_GUIDANCE_VERSION,
            "benchmark_app": normalized_app,
            "continuation_shape": normalized_shape,
            "status": "no_measured_guidance",
            "matches": (),
            "recommended_partner": "none",
            "auto_select_partner_allowed": False,
            "recommendation": "Require explicit user partner choice and new same-contract evidence.",
            "claim_boundary": V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY,
        }
    recommended_partners = tuple(sorted({str(row["recommended_partner"]) for row in matches}))
    status = "single_recommendation" if len(matches) == 1 else "multiple_guidance_rows"
    return {
        "guidance_version": V2_6_PARTNER_CHOICE_GUIDANCE_VERSION,
        "benchmark_app": normalized_app,
        "continuation_shape": normalized_shape,
        "status": status,
        "matches": matches,
        "recommended_partners": recommended_partners,
        "recommended_partner": matches[0]["recommended_partner"] if len(recommended_partners) == 1 else "review_matches",
        "auto_select_partner_allowed": False,
        "recommendation": matches[0]["user_advice"] if len(matches) == 1 else "Review all matching rows and choose explicitly.",
        "claim_boundary": V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY,
    }


def explain_v2_6_partner_choice(
    benchmark_app: str,
    continuation_shape: str | None = None,
    *,
    user_preferred_partner: str | None = None,
) -> dict[str, Any]:
    plan = plan_v2_6_partner_choice(benchmark_app, continuation_shape)
    preferred = None if user_preferred_partner is None else str(user_preferred_partner).strip().lower()
    notes: list[str] = [str(plan["recommendation"])]
    if preferred:
        if preferred not in V2_6_ALLOWED_RECOMMENDED_PARTNERS:
            notes.append("The requested partner is outside the current supported recommendation vocabulary.")
        elif preferred not in tuple(plan.get("recommended_partners", ())):
            notes.append("The requested partner is allowed as user code only if new same-contract evidence is supplied.")
        else:
            notes.append("The requested partner matches the current recommendation for this row.")
    return {
        **plan,
        "user_preferred_partner": preferred,
        "explain_notes": tuple(notes),
        "user_choice_remains_authority": True,
        "auto_select_partner_allowed": False,
    }


def validate_v2_6_partner_choice_guidance(
    guidance: dict[str, Any] | None = None,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    guidance = v2_6_partner_choice_guidance() if guidance is None else guidance
    root = Path.cwd() if repo_root is None else Path(repo_root)
    errors: list[str] = []
    if guidance.get("guidance_version") != V2_6_PARTNER_CHOICE_GUIDANCE_VERSION:
        errors.append("unexpected v2.6 partner-choice guidance version")
    if guidance.get("status") != V2_6_PARTNER_CHOICE_GUIDANCE_STATUS:
        errors.append("unexpected v2.6 partner-choice guidance status")
    if tuple(guidance.get("promoted_benchmark_apps", ())) != V2_6_PROMOTED_BENCHMARK_APPS:
        errors.append("promoted benchmark app order changed")
    rows = tuple(guidance.get("rows", ()))
    apps = {str(row.get("benchmark_app", "")) for row in rows if isinstance(row, dict)}
    if apps != set(V2_6_PROMOTED_BENCHMARK_APPS):
        errors.append("guidance must cover every promoted benchmark app exactly at least once")
    if int(guidance.get("row_count", -1)) != len(rows):
        errors.append("row_count does not match rows")
    if int(guidance.get("app_count", -1)) != len(apps):
        errors.append("app_count does not match app coverage")
    for path in tuple(guidance.get("docs", ())) + tuple(guidance.get("evidence_reports", ())):
        if not (root / str(path)).exists():
            errors.append(f"required guidance document is missing: {path}")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("guidance rows must be dictionaries")
            continue
        if row.get("recommended_partner") not in V2_6_ALLOWED_RECOMMENDED_PARTNERS:
            errors.append(f"unsupported recommended partner: {row.get('recommended_partner')}")
        if row.get("recommendation_status") not in V2_6_PARTNER_CHOICE_STATUSES:
            errors.append(f"unsupported recommendation status: {row.get('recommendation_status')}")
        if row.get("automatic_partner_selection_allowed") is not False:
            errors.append(f"{row.get('benchmark_app')} allows automatic partner selection")
        for field in (
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "broad_partner_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "release_authorized",
            "app_specific_native_engine_logic_authorized",
        ):
            if row.get(field) is not False:
                errors.append(f"{row.get('benchmark_app')} authorizes {field}")
    for field in (
        "automatic_partner_selection_allowed",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "broad_partner_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "release_authorized",
        "app_specific_native_engine_logic_authorized",
    ):
        if guidance.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "guidance_version": guidance.get("guidance_version"),
        "errors": tuple(errors),
    }
