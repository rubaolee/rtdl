from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_BENCHMARK_ROUTE_DECISION_VERSION = "rtdl.v2_10.current_benchmark_route_decisions.goal4091.v1"
CURRENT_BENCHMARK_ROUTE_DECISION_STATUS = "internal_route_guidance_not_auto_dispatch"
CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY = (
    "Goal4091 refreshes current benchmark route decisions after the Goal4074-4088 "
    "RT-DBSCAN grouped-union bottleneck, partition-summary feasibility, and host-work "
    "skip chain. It is advisory "
    "guidance only: users choose partners explicitly. It does not authorize release "
    "action, public speedup wording, whole-app acceleration wording, broad RT-core "
    "wording, paper-reproduction wording, true-zero-copy wording, automatic partner "
    "selection, AMD performance wording, or app-specific native-engine logic."
)

ROUTE_DECISION_KINDS = (
    "primitive_first",
    "numba_continuation",
    "mixed_explicit",
    "no_partner_needed",
    "fastest_partner_with_numba_reference",
)
PARTNER_POLICIES = (
    "none",
    "numba",
    "cupy_fastest_numba_reference",
    "mixed_explicit_user_choice",
    "primitive_only",
)


@dataclass(frozen=True)
class CurrentBenchmarkRouteDecision:
    app: str
    decision_kind: str
    current_reader_decision: str
    primary_route: str
    partner_policy: str
    primitive_contract: str
    user_choice_guidance: str
    rejected_or_unpromoted_candidates: tuple[str, ...]
    next_runtime_action: str
    evidence_refs: tuple[str, ...]
    pod_needed_next: bool
    user_explicit_choice_required: bool = True
    automatic_partner_selection_authorized: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    amd_performance_claim_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if self.decision_kind not in ROUTE_DECISION_KINDS:
            raise ValueError(f"{self.app}: unsupported decision kind")
        if self.partner_policy not in PARTNER_POLICIES:
            raise ValueError(f"{self.app}: unsupported partner policy")
        for field in (
            "current_reader_decision",
            "primary_route",
            "primitive_contract",
            "user_choice_guidance",
            "next_runtime_action",
        ):
            value = getattr(self, field)
            if not value or value.strip().lower() == "n/a":
                raise ValueError(f"{self.app}: {field} must be explicit")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence refs must not be empty")
        if self.user_explicit_choice_required is not True:
            raise ValueError(f"{self.app}: user explicit choice must remain required")
        for flag in (
            "automatic_partner_selection_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "amd_performance_claim_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
            "status": CURRENT_BENCHMARK_ROUTE_DECISION_STATUS,
            "app": self.app,
            "decision_kind": self.decision_kind,
            "current_reader_decision": self.current_reader_decision,
            "primary_route": self.primary_route,
            "partner_policy": self.partner_policy,
            "primitive_contract": self.primitive_contract,
            "user_choice_guidance": self.user_choice_guidance,
            "rejected_or_unpromoted_candidates": self.rejected_or_unpromoted_candidates,
            "next_runtime_action": self.next_runtime_action,
            "evidence_refs": self.evidence_refs,
            "pod_needed_next": self.pod_needed_next,
            "user_explicit_choice_required": self.user_explicit_choice_required,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "amd_performance_claim_authorized": self.amd_performance_claim_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY,
        }


CURRENT_BENCHMARK_ROUTE_DECISIONS: tuple[CurrentBenchmarkRouteDecision, ...] = (
    CurrentBenchmarkRouteDecision(
        app="hausdorff_xhd",
        decision_kind="primitive_first",
        current_reader_decision="Use RTDL/OptiX nearest-witness primitives for the promoted exact route.",
        primary_route="RTDL/OptiX active-frontier nearest-witness plus generic grouped max continuation",
        partner_policy="primitive_only",
        primitive_contract="directed max-of-nearest-distance witness computation",
        user_choice_guidance="Choose Numba/CuPy only as an explicit same-contract baseline or custom continuation.",
        rejected_or_unpromoted_candidates=("paper-reproduction claim", "broad X-HD superiority claim"),
        next_runtime_action="preserve primitive-first route; future work is broader residency and AMD validation",
        evidence_refs=("Goal2801", "Goal3143", "Goal3567", "Goal3773", "Goal3774"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="spatial_rayjoin",
        decision_kind="mixed_explicit",
        current_reader_decision=(
            "Use Numba for bounded PIP one-shot; use RTDL/OptiX prepared primitives for "
            "repeated PIP, LSI scalar count, and overlay active count."
        ),
        primary_route="mixed explicit RayJoin route from Goal4039 RTX 4000 Ada fixed-Numba-toolchain evidence",
        partner_policy="mixed_explicit_user_choice",
        primitive_contract="prepared point/closed-shape batch count, segment-pair exact count, shape-pair active count",
        user_choice_guidance=(
            "Do not auto-dispatch. Ask the user which contract they are running: bounded PIP one-shot "
            "currently favors Numba, while LSI/overlay and repeated PIP favor RTDL/OptiX."
        ),
        rejected_or_unpromoted_candidates=(
            "universal PIP dominance",
            "RayJoin paper reproduction",
            "RTDL-beats-RayJoin whole-app claim",
            "prepared-points CUDA graph replay after Goal4050 OptiX/CUDA prepare failure",
        ),
        next_runtime_action=(
            "next major work is larger generic route evidence, not more one-off RayJoin tuning; "
            "treat prepared-points CUDA graph replay as quarantined until a real OptiX-capture fix exists"
        ),
        evidence_refs=("Goal3866", "Goal3867", "Goal3933", "Goal3934", "Goal3935", "Goal3936", "Goal3937", "Goal4039", "Goal4050"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="rt_dbscan",
        decision_kind="numba_continuation",
        current_reader_decision=(
            "Use the unblocked RTDL/OptiX grouped stream plus Numba column-signature continuation. "
            "Keep existing partition_convergence_hybrid previews explicit and unpromoted. Goal4088 "
            "cuts device partition-summary build time by 1.6x-2.3x, but five-run prepared reuse "
            "still does not beat the recommended route on clustered or road profiles. Goal4079-4088 "
            "therefore identify the next serious target as a generic fused/native fixed-radius "
            "grouped-union work-reduction primitive that reduces candidate enumeration, root-read "
            "traffic, and full partition-pair materialization together."
        ),
        primary_route="RTDL/OptiX fixed-radius grouped stream with Numba component/signature continuation",
        partner_policy="numba",
        primitive_contract="fixed-radius count-threshold device columns plus grouped stream component labels",
        user_choice_guidance="Use Numba for no-RawKernel custom labeling; keep blocked mode off until it wins.",
        rejected_or_unpromoted_candidates=(
            "blocked grouped stream candidate from Goal3936",
            "partition_convergence_hybrid default promotion after Goal4041 mixed timing",
            "partition_convergence_hybrid full-DBSCAN promotion after Goal4047 graph-component-only app mode",
            "partition_convergence_hybrid default promotion after Goal4071 same-profile route comparison",
            "partition_convergence_hybrid default promotion after Goal4088 host-AABB skip improvement",
        ),
        next_runtime_action=(
            "pursue the Goal4080/4086 generic fixed-radius grouped-union work-reduction candidate; "
            "Goal4088 proves producer-side cleanup matters, but success still requires same-contract "
            "correctness, lower candidate/root work than Goal4079, no ngsim_dense regression, and "
            "production timing that beats the current grouped-stream Numba route before any "
            "default-route reconsideration"
        ),
        evidence_refs=(
            "Goal3758",
            "Goal3859",
            "Goal3918",
            "Goal3920",
            "Goal3936",
            "Goal3937",
            "Goal4040",
            "Goal4041",
            "Goal4046",
            "Goal4047",
            "Goal4071",
            "Goal4074",
            "Goal4075",
            "Goal4078",
            "Goal4079",
            "Goal4080",
            "Goal4084",
            "Goal4085",
            "Goal4086",
            "Goal4087",
            "Goal4088",
        ),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="robot_collision",
        decision_kind="no_partner_needed",
        current_reader_decision="Use prepared RTDL/OptiX any-hit collision flags; no partner continuation is needed.",
        primary_route="prepared RTDL/OptiX any-hit flag primitive",
        partner_policy="none",
        primitive_contract="prepared any-hit collision flag and scalar count",
        user_choice_guidance="Use a custom partner only for app-owned postprocessing outside the promoted flag contract.",
        rejected_or_unpromoted_candidates=("custom partner flag-reduction route",),
        next_runtime_action="preserve prepared device-buffer/scalar-count split and validate AMD functional parity later",
        evidence_refs=("Goal2654", "Goal3567", "Goal3755", "Goal3757"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="contact_manifold",
        decision_kind="no_partner_needed",
        current_reader_decision="Use bounded RTDL/OptiX witness collection; no promoted partner continuation is needed.",
        primary_route="prepared bounded contact-witness collect primitive",
        partner_policy="none",
        primitive_contract="fail-closed bounded witness collection",
        user_choice_guidance="Custom exact refinement can be user code, but it is outside the current promoted route.",
        rejected_or_unpromoted_candidates=("unbounded witness materialization", "partner exact-refinement promotion"),
        next_runtime_action="keep as primitive-only unless richer exact refinement becomes a benchmark pressure point",
        evidence_refs=("Goal2654", "Goal3567", "Goal3775", "Goal3776"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="raydb_style",
        decision_kind="primitive_first",
        current_reader_decision="Use primitive-first RTDL/OptiX fused grouped reductions when the fused primitive fits.",
        primary_route="primitive-first RTDL/OptiX grouped count/sum reductions",
        partner_policy="primitive_only",
        primitive_contract="columnar grouped count/sum/min/max/avg reduction",
        user_choice_guidance="Choose a partner only for unfused continuations that the native primitive does not express.",
        rejected_or_unpromoted_candidates=("forced Triton continuation for fused reductions",),
        next_runtime_action="preserve primitive-first route and avoid partner work for exact fused scalar reductions",
        evidence_refs=("Goal2979", "Goal3565", "Goal3567", "Goal3779", "Goal3781"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="barnes_hut",
        decision_kind="fastest_partner_with_numba_reference",
        current_reader_decision=(
            "Use RTDL/OptiX for membership/frontier work; CuPy remains fastest measured force continuation, "
            "with Numba available as the no-RawKernel reference. Goal4053 adds a prepared Numba "
            "grouped-vector continuation session for presegmented typed streams, but it is not a "
            "full force-law route promotion."
        ),
        primary_route="RTDL/OptiX membership primitive plus explicit force-vector partner continuation",
        partner_policy="cupy_fastest_numba_reference",
        primitive_contract="aggregate-frontier membership plus grouped vector continuation",
        user_choice_guidance=(
            "Choose CuPy for fastest measured force continuation or Numba for no-RawKernel Python JIT "
            "custom logic; use the Goal4053 prepared grouped-vector session when the user already has "
            "presegmented vector streams and wants repeated resident reductions."
        ),
        rejected_or_unpromoted_candidates=("Numba-as-fastest-force-route", "whole Barnes-Hut speedup claim"),
        next_runtime_action=(
            "prepared Numba grouped-vector session is available for presegmented streams; future major "
            "work is deeper hierarchical vector primitive design, not app-only tuning"
        ),
        evidence_refs=("Goal2803", "Goal3599", "Goal3746", "Goal3762", "Goal3869", "Goal4052", "Goal4053"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="librts_spatial_index",
        decision_kind="no_partner_needed",
        current_reader_decision="Use prepared generic AABB index query; no promoted partner continuation is needed.",
        primary_route="prepared RTDL/OptiX AABB spatial-index query primitive",
        partner_policy="none",
        primitive_contract="prepared AABB index query",
        user_choice_guidance="Treat custom partner work as optional app code until a measured same-contract continuation exists.",
        rejected_or_unpromoted_candidates=("mutable-index custom continuation",),
        next_runtime_action="keep as no-regression prepared-index row and validate AMD functional parity later",
        evidence_refs=("Goal2798", "Goal3601", "Goal3770"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="rtnn",
        decision_kind="primitive_first",
        current_reader_decision="Use prepared RTDL/OptiX ranked-summary aggregate; no promoted partner continuation is needed.",
        primary_route="prepared RTDL/OptiX fixed-radius ranked-summary aggregate",
        partner_policy="primitive_only",
        primitive_contract="fixed-radius ranked nearest summary aggregate",
        user_choice_guidance="Use CuPy/Numba only for explicit custom ranking baselines beyond the promoted summary contract.",
        rejected_or_unpromoted_candidates=("RTNN paper reproduction", "partner ranking route without same-contract evidence"),
        next_runtime_action="keep prepared columns first-class; future work is larger batched/replay evidence",
        evidence_refs=("Goal2821", "Goal2822", "Goal3820", "Goal3937"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="triangle_counting",
        decision_kind="primitive_first",
        current_reader_decision="Use explicit native RT graph summary mode for the scalar triangle-count route.",
        primary_route="generic RT graph scalar summary primitive",
        partner_policy="primitive_only",
        primitive_contract="canonical graph-cycle scalar count",
        user_choice_guidance="Choose Numba only if the user explicitly needs candidate-row compaction, not for the scalar answer.",
        rejected_or_unpromoted_candidates=("auto fallback timing route", "RT-core triangle-count paper claim"),
        next_runtime_action="preserve explicit native mode and avoid claiming RT-core triangle-count acceleration",
        evidence_refs=("Goal2797", "Goal3567", "Goal3782", "Goal3819", "Goal3856"),
        pod_needed_next=False,
    ),
)


def current_benchmark_route_decisions() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_BENCHMARK_ROUTE_DECISIONS)


def summarize_current_benchmark_route_decisions(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_route_decisions()
    kind_counts = {kind: 0 for kind in ROUTE_DECISION_KINDS}
    partner_counts = {policy: 0 for policy in PARTNER_POLICIES}
    for row in matrix:
        kind_counts[str(row["decision_kind"])] += 1
        partner_counts[str(row["partner_policy"])] += 1
    return {
        "version": CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        "status": CURRENT_BENCHMARK_ROUTE_DECISION_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "decision_kind_counts": kind_counts,
        "partner_policy_counts": partner_counts,
        "pod_needed_next_apps": tuple(row["app"] for row in matrix if row["pod_needed_next"]),
        "claim_boundary": CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY,
        "automatic_partner_selection_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "amd_performance_claim_authorized": False,
    }


def explain_current_benchmark_route(app: str) -> dict[str, Any]:
    normalized = str(app).strip()
    matches = tuple(row for row in current_benchmark_route_decisions() if row["app"] == normalized)
    if not matches:
        return {
            "version": CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
            "app": normalized,
            "status": "no_current_route_decision",
            "recommendation": "Require explicit user route choice and new same-contract evidence.",
            "automatic_partner_selection_authorized": False,
            "claim_boundary": CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY,
        }
    row = matches[0]
    return {
        **row,
        "status": "current_route_decision_found",
        "recommendation": row["user_choice_guidance"],
        "user_choice_remains_authority": True,
        "automatic_partner_selection_authorized": False,
    }


def validate_current_benchmark_route_decisions(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_route_decisions()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    expected_apps = set(V2_8_PROMOTED_BENCHMARK_APPS)
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: got={sorted(apps)} expected={sorted(expected_apps)}")
    if len(matrix) != len(apps):
        errors.append("route decisions must have exactly one row per app")
    for row in matrix:
        app = str(row.get("app", "<missing>"))
        if row.get("decision_kind") not in ROUTE_DECISION_KINDS:
            errors.append(f"{app}: invalid decision kind")
        if row.get("partner_policy") not in PARTNER_POLICIES:
            errors.append(f"{app}: invalid partner policy")
        if row.get("user_explicit_choice_required") is not True:
            errors.append(f"{app}: user explicit choice must remain required")
        if not row.get("evidence_refs"):
            errors.append(f"{app}: evidence refs must not be empty")
        for key in (
            "current_reader_decision",
            "primary_route",
            "primitive_contract",
            "user_choice_guidance",
            "next_runtime_action",
        ):
            value = row.get(key)
            if not isinstance(value, str) or not value.strip() or value.strip().lower() == "n/a":
                errors.append(f"{app}: {key} must be explicit")
        for flag in (
            "automatic_partner_selection_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "amd_performance_claim_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY,
    }
