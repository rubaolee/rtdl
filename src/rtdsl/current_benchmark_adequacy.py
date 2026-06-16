from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from .v2_9_benchmark_adequacy import ADEQUACY_LEVELS
from .v2_9_benchmark_adequacy import v2_9_benchmark_adequacy_rows


CURRENT_BENCHMARK_ADEQUACY_VERSION = "rtdl.v3_0.current_benchmark_adequacy.goal4451.v1"
CURRENT_BENCHMARK_ADEQUACY_STATUS = "internal_perf_triage_not_release_authorization"
CURRENT_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY = (
    "Goal4450 refreshes the current benchmark adequacy advisory after V3 M41-M54 "
    "evidence: Barnes-Hut is now mixed explicit because Goal4442's fused CPU/Numba "
    "route and Goal4448's fused Numba CUDA subtree prototype expose the frontier "
    "materialization bottleneck and beat the current prepared RTDL/OptiX route at "
    "tested scales, while Goal4449 turns the fused CUDA shape into a reusable "
    "app-reference partner API and Goal4450 wires that API into the Barnes-Hut "
    "app front door, with Goal4458 later reranking the current Barnes-Hut front "
    "doors and keeping prepared RTDL/OptiX as RT-core device-column evidence "
    "rather than a Barnes-Hut RT-core speedup row; RTNN separates "
    "Goal4381 exact float64 aggregate rows from Goal4443 resident graph-bridge "
    "rows; triangle counting keeps scalar primitive wording while Goal4444 fixes "
    "the no-C++ Numba construction debt; RT-DBSCAN adds Goal4445 compact "
    "component-signature output; and robot collision adds Goal4446 NumPy "
    "vectorized grouped-segment query lowering. Goal4451 updates Spatial "
    "RayJoin repeated-PIP guidance by preserving the prepared batch executor "
    "and fail-closing unsafe prepared-points CUDA graph replay. This advisory does not authorize "
    "release action, public speedup wording, whole-app acceleration wording, "
    "broad RT-core wording, paper-reproduction wording, true-zero-copy wording, "
    "automatic partner selection, AMD performance wording, or app-specific "
    "native-engine logic."
)


@dataclass(frozen=True)
class CurrentBenchmarkAdequacyRow:
    app: str
    promoted_reader_view: str
    current_performance_reading: str
    adequacy: str
    current_recommended_path: str
    current_partner_role: str
    needs_numba_reference: bool
    numba_reference_reason: str
    amd_hiprt_readiness: str
    next_generic_runtime_action: str
    evidence_refs: tuple[str, ...]
    pod_needed_next: bool
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if self.adequacy not in ADEQUACY_LEVELS:
            raise ValueError(f"unknown adequacy level: {self.adequacy}")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence refs must not be empty")
        for field in (
            "promoted_reader_view",
            "current_performance_reading",
            "current_recommended_path",
            "current_partner_role",
            "numba_reference_reason",
            "amd_hiprt_readiness",
            "next_generic_runtime_action",
        ):
            value = getattr(self, field)
            if not value or value.strip().lower() == "n/a":
                raise ValueError(f"{self.app}: {field} must be explicit")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "app": self.app,
            "promoted_reader_view": self.promoted_reader_view,
            "current_performance_reading": self.current_performance_reading,
            "adequacy": self.adequacy,
            "current_recommended_path": self.current_recommended_path,
            "current_partner_role": self.current_partner_role,
            "needs_numba_reference": self.needs_numba_reference,
            "numba_reference_reason": self.numba_reference_reason,
            "amd_hiprt_readiness": self.amd_hiprt_readiness,
            "next_generic_runtime_action": self.next_generic_runtime_action,
            "evidence_refs": self.evidence_refs,
            "pod_needed_next": self.pod_needed_next,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CURRENT_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY,
        }


_CURRENT_OVERRIDES: dict[str, dict[str, object]] = {
    "spatial_rayjoin": {
        "current_performance_reading": (
            "strong but contract-specific: current evidence supports RTDL/OptiX "
            "prepared scalar-count and active-count subcontracts for repeated PIP, "
            "LSI, and overlay-style active counts, not a universal PIP dominance or "
            "RayJoin paper-reproduction claim. Goal4039 is the latest representative "
            "mixed-route confirmation on RTX 4000 Ada after the Numba CUDA toolchain "
            "repair: one-shot bounded PIP still favors Numba, while repeated PIP uses "
            "the RTDL/OptiX prepared batch executor and LSI/overlay remain "
            "RTDL/OptiX-favorable versus Numba. Goal4050 found the prepared-points "
            "CUDA graph replay path unsafe. Goal4451 turns that finding into runtime "
            "policy: unvalidated graph replay now fails closed by default, validated "
            "graph prepare/replay errors are reported as quarantined, and the batch "
            "executor remains the recommended repeated-PIP path."
        ),
        "current_recommended_path": (
            "mixed explicit route: use Numba for bounded PIP one-shot when that is "
            "the measured contract; use RTDL/OptiX prepared point/closed-shape batch "
            "executor for repeated PIP requests; use exact RTDL/OptiX prepared "
            "segment-pair count for LSI; use RTDL/OptiX prepared-left shape-pair "
            "active-count executor for overlay active count. Do not use prepared-points "
            "CUDA graph replay as a correctness or performance path after Goal4451."
        ),
        "current_partner_role": (
            "Numba remains an explicit no-C++ comparison/reference lane for bounded "
            "PIP and scalar-count continuations; CuPy remains a dense CUDA-core "
            "baseline/opponent. Partner choice is explicit user policy, not automatic "
            "dispatch hidden behind the RayJoin front door."
        ),
        "next_generic_runtime_action": (
            "treat Numba-reference and scalar-count OptiX contracts as covered for "
            "current V3 guidance; Goal4451 fail-closes unsafe graph replay, so use "
            "the batch executor for repeated PIP and revisit graph replay only after "
            "OptiX/CUDA capture passes hardware validation without zero-count replay"
        ),
        "evidence_refs": (
            "Goal3688",
            "Goal3713",
            "Goal3733",
            "Goal3734",
            "Goal3737",
            "Goal3749",
            "Goal3761",
            "Goal3766",
            "Goal3767",
            "Goal3784",
            "Goal3785",
            "Goal3834",
            "Goal3838",
            "Goal3842",
            "Goal3866",
            "Goal3867",
            "Goal3933",
            "Goal3934",
            "Goal3935",
            "Goal3936",
            "Goal4039",
            "Goal4050",
            "Goal4451",
        ),
    },
    "rt_dbscan": {
        "current_performance_reading": (
            "strong at scale with boundary: Goal3758 A5000 prepared-repeat evidence shows "
            "the no-RawKernel Numba prepared grid continuation at 1.106x-1.153x versus "
            "the prepared CuPy grid, and the OptiX RT-core threshold-flags plus Numba "
            "prepared continuation reaches 1.367x at 65k points and 1.748x at 131k "
            "points versus prepared CuPy. Goal4040/4041 keep the "
            "partition_convergence_hybrid timing is mixed and not promoted over grouped "
            "stream. Goal4046/4047 show a useful narrower component-size-signature "
            "contract, not for full DBSCAN core/border/noise promotion. Goal4445 adds "
            "the current compact component-signature output mode: when the requested "
            "answer is cluster-size/noise/core summary, RTDL avoids per-point Python "
            "cluster rows and keeps CuPy and Numba partner aggregation explicit."
        ),
        "current_recommended_path": (
            "RTDL/OptiX fixed-radius grouped stream plus explicit output mode: "
            "`output_mode=\"component_signature\"` for compact cluster summaries, "
            "`output_mode=\"full\"` only when per-point Python cluster rows are required"
        ),
        "current_partner_role": (
            "CuPy and Numba component continuations both exist; Goal4445 uses CuPy as "
            "the direct device-array aggregation route and Numba as the no-C++ "
            "Python-source reference through the CUDA array interface"
        ),
        "next_generic_runtime_action": (
            "treat compact component signatures as the recommended summary output; "
            "keep full row materialization explicit; revisit partition_convergence_hybrid "
            "only with a fused resident component-label continuation or prepared/native "
            "partition handle; use the component-size signature mode only for the "
            "narrower graph-component contract"
        ),
        "evidence_refs": (
            "Goal2802",
            "Goal3567",
            "Goal3742",
            "Goal3744",
            "Goal3758",
            "Goal3768",
            "Goal3769",
            "Goal3784",
            "Goal3785",
            "Goal4040",
            "Goal4041",
            "Goal4046",
            "Goal4047",
            "Goal4389",
            "Goal4445",
        ),
    },
    "robot_collision": {
        "current_performance_reading": (
            "strong with contract boundary: Goal3757 A5000 prepared-batch evidence "
            "shows OptiX device-buffer compact flags at 4.825x versus Embree for "
            "1024 poses and 3.960x for 4096 poses; scalar device-count is 31.345x "
            "and 66.591x respectively. Goal4428 refreshes the same-contract xlarge "
            "prepared grouped-segment any-hit row with OptiX 6.76x faster than Embree "
            "on traversal. Goal4446 removes the largest Python query-lowering debt "
            "by using NumPy vectorized endpoint arrays for large prepared probes "
            "without changing the primitive contract."
        ),
        "current_recommended_path": (
            "prepared grouped-segment any-hit flag/count primitive with "
            "`lowering_mode=\"numpy_arrays\"` for large timing or summary probes"
        ),
        "current_partner_role": (
            "no partner needed for the promoted grouped-segment any-hit path; app "
            "policy remains outside the primitive"
        ),
        "next_generic_runtime_action": (
            "preserve the prepared-buffer and device-buffer/count split; keep the "
            "sampled grouped-segment contract separate from planner or exact-solid "
            "collision wording; run actual AMD functional validation before AMD "
            "performance work"
        ),
        "evidence_refs": (
            "Goal2654",
            "Goal3567",
            "Goal3755",
            "Goal3757",
            "Goal3765",
            "Goal3784",
            "Goal3785",
            "Goal4428",
            "Goal4446",
        ),
    },
    "barnes_hut": {
        "current_performance_reading": (
            "mixed explicit / fused partner evidence: Goal4052 adds a generic no-atomic "
            "Numba offset kernel for presegmented grouped-vector streams, and "
            "Goal4053 wraps it in a prepared session that is 3.77x-3.89x faster than "
            "the old atomic Numba path on tested generic shapes. Goal4438/4439 show "
            "RTDL/OptiX can emit aggregate-frontier device columns and feed Numba/CuPy "
            "partners. Goal4440/4441 show CPU/Embree host-materialized baselines are "
            "dominated by frontier collection and host materialization. Goal4442 adds "
            "a fused CPU/Numba route that avoids frontier and contribution row "
            "materialization and is faster than the current RTDL/OptiX+Numba route "
            "at tested 8192/16384/32768-body scales. Goal4448 adds a no-C++ "
            "Python-source Numba CUDA fused-subtree prototype that also avoids "
            "frontier and contribution row materialization, beats the prepared "
            "RTDL/OptiX+Numba route by 3.38x-7.82x on the same scale ladder, and "
            "beats the fused CPU/Numba route at 32768 bodies while remaining slower "
            "at 8192/16384. Goal4449 promotes the same fused CUDA shape to the "
            "reusable `prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda` "
            "app-reference partner API, and Goal4450 exposes it as the "
            "`fused_frontier_force_sum_bucketized_numba_cuda` app front-door mode. "
            "Goal4458 reranks the current force-summary front doors and keeps fused "
            "CPU/Numba as the fastest measured route on the RTX 4000 Ada pod at "
            "8192/16384/32768 bodies, fused Numba CUDA as the no-C++ GPU fused "
            "partner lane, and prepared RTDL/OptiX+Numba as RT-core device-column "
            "evidence rather than Barnes-Hut RT-core speedup evidence."
        ),
        "adequacy": "adequate",
        "current_recommended_path": (
            "choose `fused_frontier_force_sum_bucketized_cpu_numba` for the current "
            "strongest CPU fused baseline; choose "
            "`fused_frontier_force_sum_bucketized_numba_cuda` for the current "
            "app-front-door no-C++ fused GPU partner route, or "
            "`prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda` when "
            "embedding the reusable API directly; choose "
            "`prepared_aggregate_frontier_weighted_vector_optix --partner numba` "
            "when the purpose is RTDL/OptiX device-column evidence"
        ),
        "current_partner_role": (
            "Numba powers the current no-C++ fused CPU and CUDA prototype routes "
            "and is also the fastest measured partner for the current prepared "
            "aggregate-frontier RTDL/OptiX device-column contract; CuPy remains "
            "the measured comparison partner, not the default winner for this "
            "contract"
        ),
        "next_generic_runtime_action": (
            "treat as covered for Numba-reference, fused CPU/GPU partner, "
            "presegmented grouped-vector continuation, and route-choice evidence; "
            "Barnes-Hut RT-core speedup requires promoting the fused subtree "
            "traversal plus vector accumulation shape into an app-agnostic "
            "RT-native/device primitive, not more host-row optimization"
        ),
        "evidence_refs": (
            "Goal2803",
            "Goal3599",
            "Goal3567",
            "Goal3746",
            "Goal3762",
            "Goal3777",
            "Goal3780",
            "Goal3784",
            "Goal3785",
            "Goal3869",
            "Goal4052",
            "Goal4053",
            "Goal4438",
            "Goal4439",
            "Goal4440",
            "Goal4441",
            "Goal4442",
            "Goal4448",
            "Goal4449",
            "Goal4450",
            "Goal4458",
        ),
    },
    "rtnn": {
        "current_performance_reading": (
            "strong same-contract RTDL evidence / not paper reproduction: the older "
            "front door still includes `prepared_optix_ranked_summary` and Goal3820 "
            "pure JSON A5000 evidence at 4096 and 65536 points, not an RTNN "
            "paper-reproduction claim. Goal4381 then shows exact float64 RTDL/OptiX "
            "native ranked-summary aggregate is 10.14x faster than exact Embree on "
            "the 1M uniform row and 11.80x faster on the 262K shell row. Goal4443 "
            "shows the resident graph bridge can run a 1M resident search scene with "
            "65K query batches, CUDA graph replay, and same-stream CuPy/Numba "
            "reductions at about 5ms per batch with 1000-repeat second-level hot evidence."
        ),
        "adequacy": "strong",
        "current_recommended_path": (
            "mixed explicit: use prepared RTDL/OptiX exact float64 ranked-summary aggregate "
            "for same-contract float64 OptiX-vs-Embree comparisons; use "
            "the historical `prepared_optix_ranked_summary` app mode for that front "
            "door; use `prepared_ranked_summary_graph_partner_bridge` for resident "
            "graph replay plus same-stream CuPy/Numba app-bridge evidence"
        ),
        "current_partner_role": (
            "no partner needed for exact float64 native aggregate; CuPy and Numba are "
            "both explicit partners for the resident graph bridge and must not be "
            "collapsed into automatic exact-vs-float32 route selection"
        ),
        "next_generic_runtime_action": (
            "keep exact aggregate and resident graph-bridge contracts separate; "
            "prove output-contract equivalence before comparing with official RTNN "
            "authors-code rows; run actual AMD functional validation before AMD "
            "performance work"
        ),
        "evidence_refs": (
            "Goal2800",
            "Goal2822",
            "Goal3567",
            "Goal3771",
            "Goal3772",
            "Goal3784",
            "Goal3785",
            "Goal3820",
            "Goal3937",
            "Goal4381",
            "Goal4422",
            "Goal4443",
        ),
    },
    "triangle_counting": {
        "current_performance_reading": (
            "mixed primitive + partner-construction evidence: Goal3819 shows the "
            "explicit `--optix-graph-mode native` route on the current app fixture "
            "is faster than the auto fallback (0.9871935369446874s versus "
            "6.018893013708293s) while still reporting no RT-core triangle-count "
            "claim. Goal4444 refreshes the explicit RT-Graph summary-contract "
            "partner row by replacing the old Numba CPU-contract builder with direct "
            "binary vectorized summary construction before Numba device upload, "
            "cutting Numba construction debt by 19.96x-23.07x while CuPy remains the "
            "large-scale performance route."
        ),
        "current_recommended_path": (
            "generic RT graph relationship-count primitive for the scalar answer; "
            "use explicit `--optix-graph-mode native` for current native timing and "
            "use Goal4444 partner rows only for RT-Graph summary-contract experiments"
        ),
        "current_partner_role": (
            "no partner needed for the scalar primitive answer; CuPy is current "
            "large-scale performance for explicit summary-contract construction and "
            "Numba is now a much fairer no-C++ Python-source reference"
        ),
        "next_generic_runtime_action": (
            "keep scalar triangle-count wording primitive-first; do not claim RT-Graph "
            "paper reproduction or broad triangle-count acceleration; remaining "
            "construction debt is fully device-side or segmented summary construction"
        ),
        "evidence_refs": (
            "Goal2797",
            "Goal3567",
            "Goal3782",
            "Goal3784",
            "Goal3785",
            "Goal3819",
            "Goal3856",
            "Goal4424",
            "Goal4444",
        ),
    },
}


def _row_from_legacy(row: object) -> CurrentBenchmarkAdequacyRow:
    values: dict[str, object] = {
        "app": row.app,
        "promoted_reader_view": row.promoted_reader_view,
        "current_performance_reading": row.current_performance_reading,
        "adequacy": row.adequacy,
        "current_recommended_path": row.current_recommended_path,
        "current_partner_role": row.current_partner_role,
        "needs_numba_reference": row.needs_numba_reference,
        "numba_reference_reason": row.numba_reference_reason,
        "amd_hiprt_readiness": row.amd_hiprt_readiness,
        "next_generic_runtime_action": row.next_generic_runtime_action,
        "evidence_refs": row.evidence_refs,
        "pod_needed_next": row.pod_needed_next,
    }
    values.update(_CURRENT_OVERRIDES.get(str(row.app), {}))
    return CurrentBenchmarkAdequacyRow(**values)  # type: ignore[arg-type]


CURRENT_BENCHMARK_ADEQUACY_ROWS: tuple[CurrentBenchmarkAdequacyRow, ...] = tuple(
    _row_from_legacy(row) for row in v2_9_benchmark_adequacy_rows()
)


def current_benchmark_adequacy_rows() -> tuple[CurrentBenchmarkAdequacyRow, ...]:
    return CURRENT_BENCHMARK_ADEQUACY_ROWS


def current_benchmark_adequacy() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_BENCHMARK_ADEQUACY_ROWS)


def summarize_current_benchmark_adequacy(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_adequacy()
    adequacy_counts = {level: 0 for level in ADEQUACY_LEVELS}
    for row in matrix:
        adequacy_counts[str(row["adequacy"])] += 1
    numba_apps = tuple(row["app"] for row in matrix if row["needs_numba_reference"])
    pod_apps = tuple(row["app"] for row in matrix if row["pod_needed_next"])
    return {
        "version": CURRENT_BENCHMARK_ADEQUACY_VERSION,
        "status": CURRENT_BENCHMARK_ADEQUACY_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "adequacy_counts": adequacy_counts,
        "numba_reference_needed_apps": numba_apps,
        "pod_needed_next_apps": pod_apps,
        "claim_boundary": CURRENT_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    }


def validate_current_benchmark_adequacy(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_adequacy()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    expected_apps = set(V2_8_PROMOTED_BENCHMARK_APPS)
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: got={sorted(apps)} expected={sorted(expected_apps)}")
    for row in matrix:
        app = str(row.get("app", "<missing>"))
        if row.get("version") != CURRENT_BENCHMARK_ADEQUACY_VERSION:
            errors.append(f"{app}: stale version")
        if row.get("claim_boundary") != CURRENT_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY:
            errors.append(f"{app}: stale claim boundary")
        if row.get("adequacy") not in ADEQUACY_LEVELS:
            errors.append(f"{app}: invalid adequacy level")
        if not row.get("evidence_refs"):
            errors.append(f"{app}: missing evidence refs")
        for key in (
            "promoted_reader_view",
            "current_performance_reading",
            "current_recommended_path",
            "current_partner_role",
            "numba_reference_reason",
            "amd_hiprt_readiness",
            "next_generic_runtime_action",
        ):
            value = row.get(key)
            if not isinstance(value, str) or not value.strip() or value.strip().lower() == "n/a":
                errors.append(f"{app}: {key} must be explicit")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": CURRENT_BENCHMARK_ADEQUACY_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": CURRENT_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY,
    }
