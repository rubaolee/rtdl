from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from .v2_9_benchmark_adequacy import ADEQUACY_LEVELS
from .v2_9_benchmark_adequacy import v2_9_benchmark_adequacy_rows


CURRENT_BENCHMARK_ADEQUACY_VERSION = "rtdl.v3_0.current_benchmark_adequacy.goal4491.v1"
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
    "rather than a Barnes-Hut RT-core speedup row, and Goal4483 extending the "
    "rerank to 65536/131072 bodies where fused Numba CUDA becomes fastest while "
    "prepared RTDL/OptiX+Numba remains slower due to aggregate-frontier row emission; "
    "RTNN separates "
    "Goal4381 exact float64 aggregate rows from Goal4443 uniform resident "
    "graph-bridge rows, Goal4459 clustered resident graph-bridge rows, and "
    "Goal4460 shell resident graph-bridge rows; "
    "triangle counting keeps scalar primitive wording while Goal4444 fixes "
    "the no-C++ Numba construction debt; RT-DBSCAN adds Goal4445 compact "
    "component-signature output; Goal4484 refreshes RT-DBSCAN route guidance "
    "with a 524k compact-signature matrix where predicate direct-status is the "
    "measured explicit route and grouped-stream Numba remains the conservative "
    "fallback/reference path; Goal4485 extends the same RT-DBSCAN compact "
    "signature matrix to 1M points with the same route outcome; Goal4486 removes "
    "the RT-DBSCAN self-query count-threshold host-query repack/upload debt via "
    "a generic prepared self-query fixed-radius primitive; Goal4487 instruments "
    "RT-DBSCAN direct-status prepare phase accounting; Goal4488 removes the "
    "generic tuple-of-xyz row-columnization intermediate for common Point3D, "
    "mapping, and sequence inputs; Goal4489 adds caller-owned CuPy point-column "
    "direct-status prepare for honest shared-column handoff; Goal4490 wires that "
    "path into an explicit RT-DBSCAN app mode and shows app-constructed coordinate "
    "columns are not a stable total-time promotion when build time is charged; "
    "Goal4491 removes a redundant coordinate-helper pre-scan for a modest 1.04x-1.11x "
    "app-constructed build improvement without changing that boundary; and robot "
    "collision adds Goal4446 NumPy "
    "vectorized grouped-segment query lowering. Goal4451 updates Spatial "
    "RayJoin repeated-PIP guidance by preserving the prepared batch executor "
    "and fail-closing unsafe prepared-points CUDA graph replay. Goal4459 also "
    "makes the RTNN app bridge non-toy on a clustered 1M/65K/repeat=1000 row "
    "while preserving signature, same-stream partner, and no-hidden-copy gates. "
    "Goal4460 closes the app-bridge shell distribution gap with the same gates. "
    "Goal4464 closes Triangle Counting's largest paper-dataset OOM validation row "
    "by running source-range segmented RT-2A1 on `com-orkut` with a measured 2M "
    "directed-edge scene cap, while keeping public speedup claims blocked. "
    "Goal4465 removes the Triangle Counting segmented planner's per-edge Python "
    "loop with NumPy prefix/searchsorted planning, making the remaining large-row "
    "debts duplicate-ray construction, traversal, and comparison rather than "
    "avoidable planning overhead. Goal4466 records explicit ray-batch cap tuning "
    "for `com-orkut`: 15M is the measured RTX 4000 Ada cap, while 18M/20M are "
    "unsafe during query and cannot be hidden defaults. Goal4467 refreshes the "
    "Triangle Counting current comparison packet and records that RTDL completes "
    "the large rows exactly while cuGraph remains much faster and authors pure "
    "count kernels remain much faster than RTDL query traversal. Goal4468 adds "
    "explicit unique-weighted segment rays for Triangle Counting: physical ray "
    "count and traversal drop materially, but partner unique compression becomes "
    "the bottleneck and whole-route speedup remains blocked. Goal4469 adds "
    "explicit prepared segment replay, improving Triangle Counting large-row "
    "totals by 1.43x-1.84x versus Goal4467 while preserving claim boundaries. "
    "Goal4470 refreshes the post-M73 comparison: cuGraph remains faster by "
    "5.58x-8.64x and authors pure kernels remain much faster. Goal4471 adds "
    "explicit Triangle Counting phase-split telemetry so build-once cost, "
    "warmup query time, and measured replay query throughput are no longer "
    "collapsed into legacy aggregate fields. Goal4472 adds explicit no-C++ "
    "Numba direct unique-key fill for Triangle Counting; it improves build and "
    "backend phases but has mixed end-to-end total timing, so default promotion "
    "remains blocked. Goal4473 adds backend query-phase telemetry and shows the "
    "M77 same-commit packet has `numba_direct` faster end to end on all three "
    "large rows while native query pack/traversal stay essentially equal; the "
    "remaining query-wall movement is replay envelope work, not native RT "
    "traversal evidence. Goal4474 adds a generic prepared ray-batch weighted "
    "any-hit sum and uses it in Triangle Counting prepared replay, improving "
    "large-row query medians by about 4.8x-5.2x versus M77 while keeping the "
    "engine contract app-agnostic. Goal4475 refreshes the post-M78 comparison: "
    "cuGraph remains 3.15x-4.89x faster end to end, while RTDL M78 full-pipeline "
    "wins over authors-code full pipeline remain separate from pure kernel timing. "
    "Goal4476 audits and reverts a no-weight-sum-sync M80 candidate because "
    "query medians are unchanged and total/backend timing does not improve. "
    "Goal4477 adds a generic compact constant-ray prepared batch ABI and tests "
    "it as M81; it is correct and app-agnostic, but best large-row totals are "
    "0.83x/0.86x/0.94x versus M78, so current best remains M78. Goal4478 adds "
    "opt-in synchronized segment-ray build subphase telemetry and shows "
    "`cupy_unique_counts` is the scaling hotspot at 41.6%/46.8%/53.3% of "
    "segment-ray construction on `com-lj`/`soc-LiveJournal1`/`com-orkut`; "
    "this identifies the next optimization target but is not a speedup claim. "
    "Goal4479 adds explicit `numba_direct_sort_rle`, replacing "
    "`cp.unique(return_counts)` with in-place CuPy sort plus run-length "
    "counting; same-commit w1/r3 rows improve total time by "
    "1.126x/1.090x/1.071x and segment-ray build by 1.145x/1.149x/1.187x, "
    "so it becomes the current internal Triangle Counting route while public "
    "speedup wording remains blocked. Goal4480 retests the compact constant-ray "
    "layout on top of Goal4479; it remains correct but total time is worse on "
    "all three large rows, so full ray columns remain the current internal route. "
    "Goal4481 tests a no-C++ Numba fused decode/project output builder; it is "
    "correct but segment-ray build is 0.661x/0.701x/0.664x versus the current "
    "CuPy-vectorized output route, so it remains rejected. Goal4482 rejects an "
    "already-sorted source-group skip-sort fast path for Triangle Counting "
    "because sorted groups cover only 0.131%/0.617%/0.001% of two-hop rows on "
    "the three large paper rows; future grouped/local unique-count work must be "
    "a true bounded-kernel strategy, not a sortedness shortcut. "
    "This advisory does not authorize "
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
            "the compact component-signature output mode: when the requested "
            "answer is cluster-size/noise/core summary, RTDL avoids per-point Python "
            "cluster rows and keeps CuPy and Numba partner aggregation explicit. "
            "Goal4484 records a 524k compact-signature route matrix where explicit "
            "predicate direct-status CuPy is fastest on clustered3d, road3d, and "
            "ngsim_dense. Goal4485 extends the same matrix to 1,048,576 points "
            "and keeps predicate direct-status fastest on all three profiles for "
            "one-shot and warmed replay timing, while grouped-stream Numba remains "
            "the conservative same-contract fallback/reference path. Goal4486 "
            "adds a generic prepared self-query 3-D fixed-radius count-threshold "
            "device-column primitive and wires this route to it, reducing the "
            "count-threshold run from about 2.2s to 0.16-0.34s on the 1M rows "
            "without changing signatures. Goal4487 then proves direct-status "
            "prepare is dominated by host row extraction and coordinate-column "
            "upload, and Goal4488 cuts the diagnostic direct-status prepare "
            "phase by about 2.0x-2.4x with a generic Point3D/mapping/sequence "
            "row-columnization fast path. Goal4489 adds a caller-owned CuPy "
            "point-column entry point; when x/y/z device columns already exist, "
            "direct-status prepare improves by 12x-124x on the same 1M rows, "
            "with point-column construction timed separately and not hidden."
            " Goal4490 adds the explicit app-level charged coordinate-column mode: "
            "signatures match, one-shot clustered3d improves modestly, but road3d, "
            "ngsim_dense, and warmed replay do not produce a stable total-time win "
            "once app-side column construction is charged."
            " Goal4491 then removes the coordinate-helper pre-scan, improving "
            "that build phase by 1.04x-1.11x while preserving the same no-promotion boundary."
        ),
        "current_recommended_path": (
            "Explicit RTDL/OptiX self-query predicate direct-status CuPy for measured 524k/1M "
            "`output_mode=\"component_signature\"` compact cluster summaries; "
            "grouped-stream Numba fallback/reference; "
            "`output_mode=\"full\"` only when per-point Python cluster rows are required"
        ),
        "current_partner_role": (
            "CuPy is the measured predicate direct-status compact-signature route in "
            "Goal4484/Goal4485/Goal4486/Goal4488/Goal4489/Goal4490/Goal4491; Numba remains the no-C++ Python-source same-contract fallback "
            "and grouped-stream reference route"
        ),
        "next_generic_runtime_action": (
            "keep predicate direct-status explicit for measured compact summary "
            "profiles; keep full row materialization explicit; use the shared "
            "device-coordinate-column entry point only where callers already own "
            "partner columns, because Goal4490 shows app-constructed columns are "
            "not a stable default promotion after charging build time; broaden profile coverage next; use "
            "graph-only component-size signature only for the narrower "
            "graph-component contract"
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
            "Goal4484",
            "Goal4485",
            "Goal4486",
            "Goal4487",
            "Goal4488",
            "Goal4489",
            "Goal4490",
            "Goal4491",
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
            "evidence rather than Barnes-Hut RT-core speedup evidence. Goal4483 "
            "extends the same rerank to 65536/131072 bodies and changes current "
            "guidance to scale-dependent: fused Numba CUDA is fastest at those "
            "larger rows, 2.31x-2.95x faster than fused CPU/Numba and "
            "5.27x-13.77x faster than prepared RTDL/OptiX+Numba."
        ),
        "adequacy": "adequate",
        "current_recommended_path": (
            "choose `fused_frontier_force_sum_bucketized_cpu_numba` for the current "
            "small-scale CPU-fastest rows from Goal4458; choose "
            "`fused_frontier_force_sum_bucketized_numba_cuda` for the current "
            "larger-row fastest fused Numba CUDA route from Goal4483, or "
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
            "contract; after Goal4483 the fused Numba CUDA path is the fastest "
            "measured larger-row Barnes-Hut app route, while prepared OptiX+Numba "
            "remains the RT-core evidence route"
        ),
        "next_generic_runtime_action": (
            "treat as covered for Numba-reference, fused CPU/GPU partner, "
            "presegmented grouped-vector continuation, and route-choice evidence; "
            "Barnes-Hut RT-core speedup requires promoting the fused subtree "
            "traversal plus vector accumulation shape into an app-agnostic "
            "RT-native/device primitive and comparing against the Goal4483 "
            "large-row fused Numba CUDA result, not more host-row optimization"
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
            "Goal4483",
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
            "reductions at about 5ms per batch with 1000-repeat second-level hot evidence. "
            "Goal4459 extends the same app-bridge contract to a clustered 1M resident "
            "scene: CuPy measures 130.079ms hot median per 65K-query batch and Numba "
            "measures 131.442ms, with signature, CUDA graph replay, same-stream partner "
            "reduction, and no-hidden-copy gates still passing. Goal4460 adds the shell "
            "distribution row under the same app-bridge contract: CuPy measures 38.588ms "
            "hot median per 65K-query batch and Numba measures 39.267ms, with the same "
            "parity and hot-window gates."
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
            "authors-code rows; do not add more synthetic distribution timing unless "
            "it changes a route decision; run actual AMD functional validation before "
            "AMD performance work"
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
            "Goal4459",
            "Goal4460",
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
            "large-scale performance route. Goal4461 adds a segmented RT-2A1 CuPy "
            "route that avoids global two-hop summary materialization and matches the "
            "generated 800,000-triangle oracle on the 200,000-K4-clique pod row. "
            "Goal4462 validates that route on the real `com-lj` paper dataset that "
            "previously OOMed, matching 177,820,130 expected triangles. Goal4463 adds "
            "source-range triangle-scene segmentation and validates `soc-LiveJournal1`, "
            "matching 285,730,264 expected triangles without global scene materialization. "
            "Goal4464 validates the largest paper row, `com-orkut`, after lowering the "
            "default scene cap to the measured 2M directed-edge configuration: it matches "
            "627,584,181 expected triangles with no global two-hop summary or global "
            "triangle scene, while exposing planning and duplicate-ray build as the "
            "remaining performance debt. Goal4465 reduces the `com-orkut` planner "
            "median from 28.885s to 3.665s by replacing Python per-edge segmentation "
            "with NumPy prefix/searchsorted planning; duplicate-ray build and traversal "
            "are now the main route-level debts. Goal4466 tunes the explicit ray-batch "
            "cap on the RTX 4000 Ada pod: 15M lowers the warmup-0 repeat-1 probe to "
            "34.231s, but 18M/20M OOM during query, so this is tuning guidance rather "
            "than a universal default. Goal4467 refreshes current RTDL large-row totals "
            "to 14.153s on `com-lj`, 25.747s on `soc-LiveJournal1`, and 115.032s on "
            "`com-orkut`, while documenting that cuGraph is still 8.26x-15.91x faster "
            "end to end and authors pure kernels remain much faster than RTDL query. "
            "Goal4468 adds explicit unique-weighted segment rays: physical rays fall "
            "by 1.76x-1.84x and traversal median improves by 2.36x-2.47x, but "
            "partner unique compression makes construction 2.44x-2.50x slower, so "
            "whole-route speedup remains blocked. Goal4469 adds explicit prepared "
            "segment replay, improving formal totals to 9.552s on `com-lj`, "
            "17.986s on `soc-LiveJournal1`, and 62.428s on `com-orkut`. "
            "Goal4470 refreshes the current comparison packet after M73: cuGraph "
            "is still 5.58x-8.64x faster end to end, and authors pure count "
            "kernels are still much faster than RTDL query. Goal4471 adds "
            "phase-split telemetry for the same prepared replay route: build-once "
            "cost is 2.341s/3.035s/15.243s on `com-lj`/`soc-LiveJournal1`/"
            "`com-orkut`, while median measured replay query is "
            "0.925s/1.282s/8.216s. Goal4472 adds explicit no-C++ "
            "`numba_direct` unique-key fill. It improves segment-ray build by "
            "1.17x/1.36x/1.64x and backend phase by 1.05x/1.03x/1.09x on the "
            "large rows, while end-to-end total remains mixed. Goal4473 adds "
            "backend query-phase telemetry: the M77 packet shows `numba_direct` "
            "faster end to end by 1.09x/1.08x/1.12x, while native query pack "
            "plus traversal remains about 1.00x versus `cupy_repeat`. The "
            "observed query-wall movement is therefore replay/envelope cost, "
            "not native RT traversal regression. Goal4474 adds the generic "
            "prepared ray-batch weighted any-hit primitive and wires it into "
            "prepared segmented replay. Query medians improve by about "
            "4.8x-5.2x versus M77, and current `numba_direct` totals are "
            "5.404s/11.669s/35.379s on the three large rows. Goal4475 refreshes "
            "the post-M78 comparison: the cuGraph gap is now 3.15x-4.89x, RTDL "
            "M78 is 5.92x-7.99x faster than the authors `rt_tc` full pipeline "
            "on the two completed rows because authors preprocessing dominates, "
            "and authors pure count kernels remain faster than RTDL M78 query. "
            "Goal4476 tests and rejects removing per-segment weight-sum "
            "reduction/sync telemetry: M80 no-sync and explicit-sync variants "
            "do not improve total/backend timing, so M78 remains the current "
            "best internal route. Goal4477 adds the compact "
            "`xz_constant_y_direction` prepared ray-batch ABI and tests it as "
            "M81. Counts match and RT traversal medians stay essentially equal, "
            "but best M81 totals are 6.532s/13.562s/37.623s versus M78 "
            "5.404s/11.669s/35.379s, so the current route does not switch. "
            "Goal4478 profiles the M78 current-best route with explicit "
            "`sync_subphases` telemetry and identifies `cupy_unique_counts` "
            "as the top segment-ray build subphase on all three large rows: "
            "0.694s/1.035s/6.306s, or 41.6%/46.8%/53.3% of segment-ray "
            "construction. Goal4479 tests explicit `numba_direct_sort_rle`: "
            "counts, lowered ray counts, and weight sums match `numba_direct`, "
            "while same-commit w1/r3 totals improve to 6.489s/13.273s/35.990s "
            "from 7.308s/14.467s/38.564s. Goal4480 retests compact constant-ray "
            "columns with `numba_direct_sort_rle`; prepared batch build improves "
            "only 1.02x-1.03x and total time is 0.924x/0.945x/0.986x, so full "
            "ray columns remain the current route. Goal4481 tests "
            "`numba_fused_decode_project`; counts/rays/weights match, but "
            "total time is 0.899x/0.945x/0.953x and segment-ray build is "
            "0.661x/0.701x/0.664x, so CuPy vectorized output remains current. "
            "Goal4482 scouts the possible already-sorted source-group skip-sort "
            "fast path for the remaining unique/count boundary. Sorted source "
            "groups cover only 0.131%/0.617%/0.001% of two-hop rows on "
            "`com-lj`/`soc-LiveJournal1`/`com-orkut`, so that shortcut is "
            "rejected and the current route remains unchanged."
        ),
        "current_recommended_path": (
            "generic RT graph relationship-count primitive for the scalar answer; "
            "use explicit `--optix-graph-mode native` for current native timing and "
            "use Goal4444/Goal4457 partner rows for RT-Graph global-summary experiments; "
            "use Goal4461 segmented RT-2A1 only when the explicit goal is avoiding "
            "global two-hop summary materialization; cite Goal4462 for the currently "
            "passing `com-lj` paper-dataset segmented row, Goal4463 for the "
            "source-range segmented-scene `soc-LiveJournal1` row, and Goal4464 for "
            "the `com-orkut` row that needs the measured 2M scene cap. Cite Goal4465 "
            "for the current vectorized segmented planner. Cite Goal4466 for explicit "
            "ray-batch cap tuning: 5M conservative, 15M measured for `com-orkut` on "
            "RTX 4000 Ada, larger tested caps unsafe. Cite Goal4467 for the current "
            "large-row comparison packet and its no-speedup boundary. Cite Goal4468 "
            "for the explicit `unique_weighted` segmented ray representation; it is "
            "a traversal-pressure reduction route, not an automatic default. Cite "
            "Goal4469 for explicit `prepared_segment_replay` when the workload is "
            "prepared/repeated and the user accepts the schedule choice. Cite "
            "Goal4470 for the current post-M73 comparison packet and no-speedup "
            "boundary. Cite Goal4471 when explaining cold/build versus hot/replay "
            "phase split or why legacy build-total fields are not wall-time build "
            "costs for prepared replay. Cite Goal4472 when the explicit no-C++ "
            "`numba_direct` key builder is relevant; do not auto-select it. Cite "
            "Goal4473 when explaining that M77's native pack/traversal telemetry "
            "does not support a native RT regression reading for query-wall movement. "
            "Cite Goal4474 for the current prepared replay path: generic prepared "
            "ray batches move repeated ray-column packing into a paid-once "
            "`prepared_ray_batch_build` phase. Cite Goal4475 for the current "
            "post-M78 comparison packet and its still-blocked public-speedup "
            "boundary. Cite Goal4476 when ruling out scalar weight-sum "
            "telemetry/copy-back as the main remaining debt. Cite Goal4477 "
            "when discussing the compact constant-ray prepared batch ABI: it is "
            "valid generic runtime surface, but not a Triangle Counting "
            "performance route promotion. Cite Goal4478 when discussing the "
            "segment-ray construction bottleneck: `cupy_unique_counts` was "
            "the measured first target. Cite Goal4479 when choosing the "
            "current measured internal route: `numba_direct_sort_rle` improves "
            "that boundary but does not solve partner materialization. Cite "
            "Goal4480 when rejecting compact constant-ray columns on top of "
            "the sort/RLE route. Cite Goal4481 when rejecting the no-C++ Numba "
            "fused decode/project output builder. Cite Goal4482 when rejecting "
            "an already-sorted source-group skip-sort fast path: sorted two-hop "
            "row coverage is below 1% on all three large rows."
        ),
        "current_partner_role": (
            "no partner needed for the scalar primitive answer; CuPy is current "
            "large-scale performance for explicit global summary-contract construction; "
            "for the segmented RT-2A1 route, keep CuPy and Numba builders as explicit "
            "choices and treat current `numba_direct_sort_rle` plus prepared ray "
            "batches as the fastest measured internal route; partner-owned device "
            "weights are consumed by generic prepared ray batches, and Numba remains "
            "the no-C++ Python-source reference/direct key-fill option; Goal4479 "
            "improves the Goal4478 `cp.unique(return_counts)` hotspot with explicit "
            "sort/RLE counting, but the unique/count boundary remains partner-side "
            "construction debt"
        ),
        "next_generic_runtime_action": (
            "keep scalar triangle-count wording primitive-first; do not claim RT-Graph "
            "paper reproduction or broad triangle-count acceleration; after Goal4471, "
            "the one-shot build versus replay-throughput split is explicit, and "
            "Goal4472 partially reduces unique-key construction with an explicit "
            "Numba direct-fill route; Goal4473 shows native pack/traversal are not "
            "the query-wall regression source; Goal4474 adds the reusable prepared "
            "ray-batch weighted-sum API and makes it the prepared replay path; "
            "Goal4475 refreshes the post-M78 comparison packet and keeps public "
            "speedup wording blocked; Goal4476 rules out weight-sum telemetry/sync "
            "cleanup as a useful next optimization; Goal4477 adds and tests a "
            "compact constant-ray prepared batch ABI but keeps M78 as current best "
            "because totals regress; Goal4478 narrows partner materialization "
            "and segment-ray construction work to the duplicate-key unique/count "
            "boundary; Goal4479 replaces generic `cp.unique(return_counts)` with "
            "explicit sort/RLE counting and promotes `numba_direct_sort_rle` as "
            "the current internal route; next work is further reducing sort/RLE "
            "unique-count cost, Numba key fill, or fused decode/projection; "
            "Goal4480 shows compact constant-ray columns should not be the next "
            "route-promotion target, and Goal4481 shows a simple no-C++ Numba "
            "fused decode/project output builder should not be promoted; "
            "Goal4482 shows an already-sorted source-group skip-sort fast path "
            "should not be promoted because sorted two-hop row coverage is below "
            "1% on all large rows; next useful work is a true lower-overhead "
            "grouped/local unique-count strategy, "
            "without breaking the app-agnostic primitive contract"
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
            "Goal4457",
            "Goal4461",
            "Goal4462",
            "Goal4463",
            "Goal4464",
            "Goal4465",
            "Goal4466",
            "Goal4467",
            "Goal4468",
            "Goal4469",
            "Goal4470",
            "Goal4471",
            "Goal4472",
            "Goal4473",
            "Goal4474",
            "Goal4475",
            "Goal4476",
            "Goal4477",
            "Goal4478",
            "Goal4479",
            "Goal4480",
            "Goal4481",
            "Goal4482",
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
