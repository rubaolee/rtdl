from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_BENCHMARK_ROUTE_DECISION_VERSION = "rtdl.v3_0.current_benchmark_route_decisions.goal4495.v1"
CURRENT_BENCHMARK_ROUTE_DECISION_STATUS = "internal_route_guidance_not_auto_dispatch"
CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY = (
    "Goal4180 refreshes current benchmark route decisions after the Goal4074-4177 "
    "RT-DBSCAN grouped-union bottleneck, partition-summary feasibility, host-work "
    "skip, non-skip active pair stream, device partition-key decode, and unordered "
    "non-skip stream chain, plus direct device status union and route-level direct-status "
    "comparison, prepared direct-status replay, explicit app-mode smoke, shape-dependent "
    "repeated app-route timing, explicit partition-cell-factor route sweeps, a route-choice "
    "advisor, 131k plus 262k scale probes, a warmed one-shot route probe, and a "
    "524k and 1M factor-0.25 extension probes, all-predicate-only mode, mixed "
    "predicate policy probe, policy-aware semantic signature, advisor refresh, and a "
    "road3d 2M all-predicate scale probe, Goal4172-4174 declared "
    "external-proof route evidence, the Goal4176 all-items direct-status "
    "refactor, and the Goal4177 post-refactor large-scale timing evidence. It is "
    "advisory guidance only: users choose partners "
    "explicitly. It does not authorize release action, public speedup wording, "
    "whole-app acceleration wording, broad RT-core wording, paper-reproduction "
    "wording, true-zero-copy wording, automatic partner selection, AMD performance "
    "wording, or app-specific native-engine logic. Goal4438 updates the Barnes-Hut "
    "partner guidance for the prepared aggregate-frontier device-column contract: "
    "Numba is currently fastest there, while CuPy remains the measured comparison "
    "partner, not the default winner for that contract. Goal4439 exposes that "
    "route as the explicit Barnes-Hut app mode "
    "`prepared_aggregate_frontier_weighted_vector_optix`. Goal4440 adds "
    "CPU and Embree host-materialized logical baselines for that route and "
    "keeps them diagnostic, not public GPU-vs-CPU or OptiX-vs-Embree wording. "
    "Goal4441 replaces the Python host vector continuation with a Numba CPU "
    "continuation for those baselines and shows the remaining bottleneck is "
    "frontier collection and host materialization. Goal4442 adds a fused "
    "CPU/Numba route that avoids frontier and contribution row materialization "
    "and is faster than the current RTDL/OptiX+Numba route for the tested "
    "Barnes-Hut scales; Barnes-Hut route guidance is therefore mixed explicit "
    "choice, not RT-core speedup wording. Goal4443 refreshes RTNN after the "
    "Goal4381 large aggregate evidence and Goal4422 app-level graph bridge: "
    "exact float64 OptiX aggregate rows beat exact Embree aggregate rows on "
    "large RTNN-shaped data, while the prepared graph plus same-stream CuPy "
    "and Numba partner bridge is the explicit resident app route. RTNN route "
    "guidance is mixed explicit because exact float64 aggregate and float32 "
    "resident graph rows must not be collapsed into one automatic backend claim. "
    "Goal4459 extends that RTNN app bridge from the uniform M47 row to a "
    "clustered 1,048,576-point / 65,536-query / repeat=1000 row, preserving "
    "signature, CUDA graph replay, same-stream CuPy and Numba reductions, and "
    "no-hidden-column-copy gates while keeping public and paper-reproduction "
    "claims blocked. Goal4460 then adds shell distribution support to the "
    "generic M19 ranked-summary graph bridge and records a shell 1,048,576-point "
    "/ 65,536-query / repeat=1000 row with the same signature, same-stream "
    "partner, and no-hidden-copy gates. "
    "Goal4444 refreshes triangle-counting partner guidance after replacing the "
    "transitional Numba CPU-contract builder with a direct binary vectorized "
    "summary path before Numba device upload. It materially reduces the no-C++ "
    "Numba staging debt while preserving CuPy as the current large-scale "
    "performance route and keeping scalar triangle-count wording primitive-first. "
    "Goal4445 adds a compact RT-DBSCAN component-signature output path that "
    "avoids per-point Python cluster rows when the user only needs the cluster "
    "size/noise/core summary. Goal4446 refreshes robot-collision setup guidance "
    "by replacing the Python-heavy grouped-segment query lowering with NumPy "
    "vectorized endpoint arrays for large prepared probes. Goal4451 hardens "
    "Spatial RayJoin repeated-PIP guidance by fail-closing the unsafe "
    "prepared-points CUDA graph replay path and preserving the prepared batch "
    "executor as the correctness-preserving repeated-request path. Goal4452 "
    "refreshes RT-DBSCAN route guidance so Goal4445's compact "
    "`output_mode=\"component_signature\"` summary contract is the current "
    "front-door reading, while full Python rows, direct-status candidates, "
    "partition factors, and border policies remain explicit user choices. "
    "Goal4484 instruments the mixed predicate direct-status path to include "
    "OptiX count-threshold prepare cost and records a 524k compact-signature "
    "matrix where predicate direct-status is the measured explicit route for "
    "clustered3d, road3d, and ngsim_dense while grouped-stream Numba remains "
    "the conservative fallback/reference path. Goal4485 extends the same "
    "compact-signature route matrix to 1,048,576 points and keeps predicate "
    "direct-status fastest on all three profiles for both one-shot and warmed "
    "replay timing. Goal4486 adds a generic prepared self-query 3-D fixed-radius "
    "count-threshold device-column primitive and wires RT-DBSCAN predicate "
    "direct-status to it, eliminating host query repack/upload for self-query "
    "workloads while keeping route selection explicit. Goal4487 instruments "
    "direct-status prepare phase accounting, and Goal4488 replaces generic "
    "tuple-of-xyz materialization with direct Point3D/mapping/sequence "
    "row-to-column lowering, cutting the diagnostic direct-status prepare "
    "phase by roughly 2.0x-2.4x on the 1M rows without changing signatures. "
    "Goal4489 adds caller-owned CuPy point-column direct-status prepare, "
    "cutting prepare by 12x-124x when x/y/z device columns already exist, "
    "with point-column construction reported separately. Goal4490 wires that "
    "entry point into an explicit RT-DBSCAN app mode and proves the boundary: "
    "when the app must construct coordinate columns from Python rows and charge "
    "that build, the route is not a stable total-time win, so it remains a "
    "non-default integration path. Goal4491 removes a redundant coordinate-helper "
    "pre-scan and improves app-constructed coordinate build by 1.04x-1.11x, "
    "which is useful hygiene but still not a default-route promotion. "
    "Goal4453 refreshes triangle-counting Numba partner guidance after moving "
    "RT-1A2/RT-2A1 geometry fill from host materialization and re-upload to "
    "partner-resident Numba device columns. It removes unnecessary data movement "
    "inside the explicit summary-contract route, but does not authorize a "
    "triangle-counting RT-core speedup claim; the remaining debt is graph-summary "
    "construction and segmented paper-dataset lowering. Goal4454 adds generic "
    "dense-label and sorted-key fast paths to the NumPy direct-binary summary "
    "builder, reducing the explicit no-C++ Numba summary-contract route on dense "
    "sorted graph inputs while preserving the same claim boundary. Goal4455 "
    "re-ranks triangle CuPy versus optimized Numba after Goal4454 and confirms "
    "CuPy remains the measured performance partner while Numba remains the "
    "no-C++ Python-source reference. Goal4456 extends the Numba direct-binary "
    "summary builder with a bounded-id remap fast path for gapped but bounded "
    "nonnegative graph ids, reducing avoidable `np.unique(return_inverse)` "
    "compaction work without changing the claim boundary. Goal4457 removes "
    "host-column materialization from the app's CuPy device-column summary route "
    "while keeping the reusable builder's compatibility default. Goal4458 reranks "
    "the current Barnes-Hut app front doors under one force-summary contract and "
    "confirms that fused CPU/Numba is fastest on the RTX 4000 Ada pod at "
    "8192/16384/32768 bodies, fused Numba CUDA is the no-C++ GPU partner lane, "
    "and prepared RTDL/OptiX remains RT-core device-column evidence rather than "
    "a Barnes-Hut RT-core speedup claim. Goal4483 extends that rerank to "
    "65536/131072 bodies and makes Barnes-Hut guidance scale-dependent: fused "
    "Numba CUDA is fastest there, while prepared RTDL/OptiX+Numba remains slower "
    "because aggregate-frontier row emission is still the hot-path contract. "
    "Goal4461 adds the Triangle Counting "
    "segmented RT-2A1 route: CuPy builds a directed CSR and two-hop count estimate, "
    "then bounded duplicate two-hop ray batches reuse one generic OptiX triangle "
    "scene. This removes the previous global two-hop summary materialization from "
    "that explicit route while keeping triangle-count RT-core speedup claims blocked. "
    "Goal4462 validates that route on the real `com-lj` paper dataset that failed "
    "Goal2593 RTDL 2A1/1A2 with a 7,429,851,776-byte CUDA allocation failure; "
    "segmented RTDL matches 177,820,130 expected triangles without global two-hop "
    "summary materialization. Goal4463 adds source-range triangle-scene segmentation "
    "for `soc-LiveJournal1`, where one global directed-edge OptiX scene OOMed; "
    "segmented scenes match 285,730,264 expected triangles without global two-hop "
    "or global triangle-scene materialization. Goal4464 extends that route to "
    "`com-orkut`, where 8M and 4M directed-edge scene caps still OOMed during "
    "OptiX scene preparation but a 2M cap matched 627,584,181 expected triangles "
    "with 59 scenes, 1,744 ray segments, and no global two-hop or triangle-scene "
    "materialization. Goal4465 replaces per-directed-edge Python segment planning "
    "with NumPy prefix/searchsorted planning, reducing `com-orkut` planner median "
    "from 28.885s to 3.665s without changing the generic engine contract. "
    "Goal4466 tunes `com-orkut` ray-batch caps on the RTX 4000 Ada pod: 15M is "
    "the best measured explicit cap, while 18M/20M OOM during query and must not "
    "become hidden automatic defaults. Goal4467 refreshes the current large-row "
    "comparison packet: RTDL now completes `com-lj`, `soc-LiveJournal1`, and "
    "`com-orkut` exactly, but cuGraph remains 8.26x-15.91x faster end to end "
    "and authors pure count kernels remain much faster than RTDL query traversal. "
    "Goal4468 adds explicit unique-weighted segment rays for RT-2A1: the CuPy "
    "partner compresses duplicate two-hop keys into unique rays plus uint64 "
    "weights before calling the same generic weighted any-hit primitive. This "
    "reduces physical rays by 1.76x-1.84x and traversal median by 2.36x-2.47x "
    "on the large rows, but shifts the bottleneck to partner unique compression. "
    "Goal4469 adds explicit prepared segment replay so each compressed segment "
    "is built once and replayed for warmup/repeat queries before release, "
    "improving large-row totals by 1.43x-1.84x versus Goal4467 while preserving "
    "the no-public-speedup boundary. Goal4470 refreshes the current comparison "
    "packet after M73: the cuGraph gap narrows to 5.58x-8.64x, but cuGraph and "
    "authors pure kernels still remain faster on their relevant contracts. "
    "Goal4471 adds explicit `phase_split_ms` telemetry for the prepared "
    "segmented Triangle Counting rows, separating paid-once scene/ray build "
    "from warmup and measured replay query throughput so the next optimization "
    "target is unique-key compression or reusable prepared ray batches, not "
    "more timing interpretation. Goal4472 adds an explicit no-C++ "
    "`--segment-unique-key-builder numba_direct` path that reduces segment-ray "
    "build and backend time on the three large rows, but keeps hidden default "
    "promotion blocked because end-to-end total is mixed. Goal4473 adds backend "
    "query-phase telemetry for the same route and shows the M77 native query_pack "
    "plus traversal medians are essentially equal between `cupy_repeat` and "
    "`numba_direct`; the remaining query-wall movement is therefore replay/envelope "
    "work, not native RT traversal evidence. Goal4474 adds a generic prepared "
    "ray-batch weighted any-hit sum and uses it in Triangle Counting prepared "
    "segment replay, moving repeated ray-column packing out of the measured query "
    "path and improving M78 query medians by about 4.8x-5.2x versus M77. "
    "Goal4475 refreshes the post-M78 comparison: RTDL M78 narrows the cuGraph "
    "end-to-end gap to 3.15x-4.89x but still does not authorize RTDL-beats-cuGraph "
    "or public RT-core triangle-count speedup wording. Goal4476 audits and "
    "reverts a no-weight-sum-sync M80 candidate because query medians are "
    "unchanged and total/backend timing does not improve. Goal4477 adds a "
    "generic compact constant-ray prepared batch ABI and tests it as M81; the "
    "ABI is correct, but large-row totals are 0.83x/0.86x/0.94x versus M78, "
    "so M78 remains the current best route. Goal4478 adds opt-in synchronized "
    "segment-ray build subphase telemetry and shows `cupy_unique_counts` is "
    "the scaling hotspot at 41.6%/46.8%/53.3% of segment-ray construction on "
    "the three large rows. Goal4479 adds an explicit `numba_direct_sort_rle` "
    "candidate that replaces `cp.unique(return_counts)` with in-place CuPy "
    "sort plus run-length counting; same-commit w1/r3 rows improve total time "
    "by 1.126x/1.090x/1.071x and segment-ray build by 1.145x/1.149x/1.187x, "
    "so it becomes the current internal Triangle Counting route while public "
    "speedup wording remains blocked. Goal4480 retests the compact constant-ray "
    "layout on top of Goal4479; it remains correct but total time is worse on "
    "all three large rows, so full ray columns remain the current internal route. "
    "Goal4481 tests a no-C++ Numba fused decode/project output builder; it is "
    "correct but segment-ray build is 0.661x/0.701x/0.664x versus the current "
    "CuPy-vectorized output route, so it remains rejected. Goal4482 scouts an "
    "already-sorted source-group skip-sort fast path for the remaining "
    "unique/count boundary. It is rejected because sorted source groups cover "
    "only 0.131%/0.617%/0.001% of two-hop rows on the three large paper rows; "
    "the next useful grouped/local unique-count work must be a true bounded-kernel "
    "strategy, not a sortedness shortcut."
)

ROUTE_DECISION_KINDS = (
    "primitive_first",
    "numba_continuation",
    "mixed_explicit",
    "no_partner_needed",
    "fastest_partner_with_numba_reference",
    "numba_fastest_with_cupy_comparison",
)
PARTNER_POLICIES = (
    "none",
    "numba",
    "cupy_fastest_numba_reference",
    "numba_fastest_cupy_comparison",
    "mixed_explicit_user_choice",
    "explicit_route_choice_cpu_numba_or_optix_numba_cupy_comparison",
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
            "prepared-points CUDA graph replay retired after Goal4451 fail-closed guard",
        ),
        next_runtime_action=(
            "next major work is larger generic route evidence, not more one-off RayJoin tuning; "
            "use the reusable prepared-points batch executor for repeated PIP; prepared-points "
            "CUDA graph replay is fail-closed and quarantined after Goal4050/Goal4451 until "
            "OptiX/CUDA capture can pass hardware validation without zero-count replay"
        ),
        evidence_refs=("Goal3866", "Goal3867", "Goal3933", "Goal3934", "Goal3935", "Goal3936", "Goal3937", "Goal4039", "Goal4050", "Goal4451"),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="rt_dbscan",
        decision_kind="mixed_explicit",
        current_reader_decision=(
            "Use the unblocked RTDL/OptiX grouped stream plus Numba column-signature continuation "
            "for the conservative one-shot/default route. "
            "Keep existing partition_convergence_hybrid previews explicit and unpromoted. Goal4088 "
            "cuts device partition-summary build time by 1.6x-2.3x. Goal4093 adds an explicit "
            "non-skip active pair stream that emits 1.5x-2.6x fewer rows and improves build time "
            "by 1.06x-1.14x. Goal4096 then removes unnecessary host partition-key reconstruction "
            "for device pair enumeration, improving non-skip build medians by 1.18x-1.47x over "
            "Goal4093. Goal4100 adds an explicit unordered non-skip stream for order-insensitive "
            "continuations, improving build medians by 1.13x-1.17x over the Goal4096 sorted "
            "non-skip path and pair emit medians by 1.38x-2.32x. Five-run prepared reuse "
            "still does not beat the recommended route on clustered or road profiles. "
            "Goal4104 shows that direct device status consumption beats materialized unordered "
            "partition-pair rows inside the resident runtime shape by 1.239x, 1.508x, and "
            "1.311x. Goal4105 then shows the naive app-level direct-status route is not "
            "route-promotable because repeated point generation and column packing make it "
            "slower than the current route at 0.475x, 0.380x, and 0.206x. Goal4079-4105 "
            "therefore identify the next serious target as a prepared/resident direct-status "
            "fixed-radius grouped-union primitive that reduces candidate enumeration, root-read "
            "traffic, repeated scan work, setup/packing work, and full partition-pair "
            "materialization together. Goal4108 adds that prepared direct-status handle and "
            "records prepared replay wins of 1.802x, 2.465x, and 1.488x over one-shot direct "
            "status, plus 3.752x, 4.648x, and 1.207x over the current route under a resident "
            "reuse boundary. Goal4109 exposes the path as the explicit app mode "
            "partner_cupy_prepared_direct_status_union_component_signature_3d, while keeping "
            "one-shot default-route promotion blocked because the app CLI smoke is still "
            "prepare-dominated. Goal4114 then measures the actual repeated app route and "
            "shows the direct-status path is shape-dependent: it wins clustered3d and road3d "
            "repeated component-signature replay by 1.796x and 1.439x, but loses on "
            "ngsim_dense at 0.178x replay speedup, so it must remain an explicit profile-aware "
            "choice rather than a universal default. Goal4116 exposes the partition cell factor "
            "as an explicit user-selected app parameter. Goal4117 then shows tuned explicit "
            "partition-cell-factor choices make the prepared direct-status route faster than the "
            "current repeated route on all three tested profiles: clustered3d uses 0.25 for "
            "2.961x replay speedup, road3d uses 0.25 for 1.866x, and ngsim_dense uses 0.5 "
            "for 1.312x. Goal4121 adds an advisory-only route explainer. Goal4122 then "
            "checks 131k scale and shows clustered3d remains best at 0.25 for 3.211x, "
            "road3d remains best at 0.25 for 1.545x, and ngsim_dense becomes best at "
            "0.25 for 1.399x. Goal4126 extends the scale evidence to 262k and keeps "
            "0.25 best on clustered3d, road3d, and ngsim_dense with 3.118x, 1.428x, "
            "and 1.642x replay speedups. Goal4130 then checks the warmed one-shot "
            "prepare-plus-one-measured-run boundary and shows the tuned direct-status "
            "route also wins all tested profiles/scales, with one-shot total speedups "
            "from 1.819x to 3.410x. Goal4134 then extends the currently winning "
            "0.25 factor to 524k and keeps all three tested profiles above parity: "
            "clustered3d 3.291x replay / 3.250x one-shot total, road3d 1.367x / "
            "1.910x, and ngsim_dense 1.769x / 2.489x. The advisor now ranks "
            "same-scale options by replay speedup for repeated workloads and by "
            "one-shot total speedup for one-shot workloads, which keeps the 65k "
            "ngsim_dense factor asymmetry visible instead of hiding it. Goal4138 "
            "extends factor 0.25 to 1M and keeps all three profiles above parity: "
            "clustered3d 3.430x replay / 3.383x one-shot total, road3d 1.396x / "
            "1.705x, and ngsim_dense 1.790x / 2.432x. This is still "
            "an explicit route choice, not "
            "automatic tuning. Goals4158-4160 then split predicate direct-status into "
            "a proven all-predicate fast path and a blocked mixed-predicate path. "
            "Goal4164 exposes the all-predicate path as an explicit fail-closed mode. "
            "Goal4165 shows no single grouped-stream variant universally explains mixed "
            "predicate component-size drift; Goal4166 adds a policy-aware semantic "
            "signature; Goal4167 updates the advisor so counts-only semantics can be "
            "compared without promoting mixed predicate direct-status. Goal4169 extends "
            "the road-like all-predicate wrapper evidence to 2,097,152 points, where it "
            "preserves the RT-DBSCAN app signature and remains above parity. Goal4173 "
            "then measures the caller-declared external-proof all-predicate route at "
            "2,097,152 points: it preserves the same signature, skips RT count-threshold "
            "execution, records no RT-core claim for the declared subpath, and improves "
            "elapsed time by 1.662x over the current grouped-stream route and 1.211x over "
            "the measured all-true wrapper under warmed-runtime timing. Goal4176 then "
            "removes the synthetic predicate-column layer from that declared route: it now "
            "uses the generic all-items direct-status component-signature primitive and "
            "wraps the result at the RT-DBSCAN app boundary. Goal4177 adds the timing "
            "post-refactor pod timing: the declared all-items route preserves the same "
            "signature, materializes no predicate columns, executes no RT count-threshold, "
            "and improves elapsed time by 1.704x over the current grouped-stream route "
            "and 1.269x over the measured all-true predicate direct-status route."
        ),
        primary_route=(
            "mixed explicit RT-DBSCAN route: grouped-stream Numba for conservative mixed "
            "predicate rows; explicit all-predicate-only predicate direct-status CuPy mode "
            "when all predicate flags are measured true; explicit caller-declared all-items "
            "direct-status CuPy mode when all predicate flags are externally proven true; "
            "prepared direct-status CuPy remains an explicit profile-aware candidate under "
            "policy-aware contracts"
        ),
        partner_policy="mixed_explicit_user_choice",
        primitive_contract="fixed-radius count-threshold device columns plus grouped stream component labels",
        user_choice_guidance=(
            "Use the advisory route explainer before choosing. For tested one-shot and repeated "
            "component-signature workloads, choose the explicit CuPy prepared direct-status app "
            "mode when the user accepts that partner and factor choice; use grouped-stream Numba "
            "as the conservative fallback/reference path. Set `partition_cell_factor` explicitly "
            "from tested evidence. Use 0.25 for clustered/road-like profiles in the tested "
            "65k/131k/262k/524k/1M packets. For dense NGSIM-like profiles, use the route advisor "
            "because the 65k best factor depends on intent: one-shot total timing ranks 0.25 "
            "first, while repeated replay ranks 0.5 first; 131k/262k/524k/1M rank 0.25 first "
            "for the tested evidence. For all-predicate rows, the explicit measured "
            "all-true mode fails closed if the runtime does not observe the fast path; "
            "Goal4169 records road3d 2M evidence for that wrapper. If the caller already "
            "has an external proof that all predicate flags are true, Goal4173 records "
            "a declared route that skips predicate measurement and improves the 2M "
            "elapsed time. Goal4176 refactors that route to use a generic all-items "
            "direct-status component signature instead of synthetic predicate columns, "
            "and Goal4177 provides post-refactor pod timing: 1.704x elapsed speedup over "
            "the current grouped-stream route and 1.269x over the measured all-true "
            "predicate direct-status route on the 2M road3d row. The declared route "
            "still requires explicit user selection and external proof and does not "
            "promote hidden selection. "
            "For mixed predicate "
            "rows, choose a policy-aware semantic contract explicitly; counts-only semantics "
            "can pass, but Goal4165 does not justify broad mixed direct-status promotion. "
            "Do not auto-select the partner, route, factor, or border policy."
        ),
        rejected_or_unpromoted_candidates=(
            "blocked grouped stream candidate from Goal3936",
            "partition_convergence_hybrid default promotion after Goal4041 mixed timing",
            "partition_convergence_hybrid full-DBSCAN promotion after Goal4047 graph-component-only app mode",
            "partition_convergence_hybrid default promotion after Goal4071 same-profile route comparison",
            "partition_convergence_hybrid default promotion after Goal4088 host-AABB skip improvement",
            "partition_convergence_hybrid non-skip default promotion after Goal4093 active-pair stream evidence",
            "partition_convergence_hybrid default promotion after Goal4096 device key decode improvement",
            "partition_convergence_hybrid unordered non-skip default promotion after Goal4100 order-insensitive stream evidence",
            "partition_convergence_hybrid direct-status app-level promotion after Goal4105 setup-boundary comparison",
            "partition_convergence_hybrid universal default promotion after Goal4108 prepared replay and Goal4109 app smoke",
            "partition_convergence_hybrid universal default promotion after Goal4114 shape-dependent repeated app-route timing",
            "automatic partition-cell-factor tuning after Goal4117 explicit factor sweep",
            "automatic one-shot route promotion after Goal4130 warmed one-shot evidence",
            "universal factor sweep claim after Goal4134 factor-0.25-only 524k extension",
            "universal factor sweep claim after Goal4138 factor-0.25-only 1M extension",
            "mixed predicate direct-status broad promotion after Goal4165 policy-variant probe",
            "component-size signature as the only mixed-predicate semantic contract after Goal4166",
        ),
        next_runtime_action=(
            "keep the user-visible profile/reuse advisor scale-aware and policy-aware; next serious runtime work is "
            "either direct-status prepare/shared-column reduction, broader profile coverage beyond the current 65k/131k/262k/524k/1M/2M packet, "
            "or a generic border-assignment policy primitive if mixed-predicate component-size distributions must be contractual. "
            "Goal4088, Goal4093, Goal4096, Goal4100, Goal4104, Goal4105, Goal4108, Goal4109, "
            "Goal4114, Goal4116, Goal4117, Goal4121, Goal4122, Goal4126, Goal4130, Goal4134, Goal4138, "
            "Goal4158, Goal4159, Goal4164, Goal4165, Goal4166, Goal4167, Goal4173, Goal4176, and Goal4177 prove "
            "producer-side cleanup, active-pair materialization reduction, device-resident "
            "key decoding, explicit unordered set-stream contracts, and direct status "
            "consumption matter, but hidden factor selection, hidden border-policy selection, "
            "and universal default promotion remain blocked"
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
            "Goal4093",
            "Goal4096",
            "Goal4100",
            "Goal4104",
            "Goal4105",
            "Goal4108",
            "Goal4109",
            "Goal4114",
            "Goal4116",
            "Goal4117",
            "Goal4121",
            "Goal4122",
            "Goal4126",
            "Goal4130",
            "Goal4134",
            "Goal4138",
            "Goal4158",
            "Goal4159",
            "Goal4160",
            "Goal4164",
            "Goal4165",
            "Goal4166",
            "Goal4167",
            "Goal4169",
            "Goal4172",
            "Goal4173",
            "Goal4174",
            "Goal4176",
            "Goal4177",
        ),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="robot_collision",
        decision_kind="no_partner_needed",
        current_reader_decision=(
            "Use the prepared grouped-segment any-hit primitive. For large prepared "
            "timing or summary probes, use Goal4446's NumPy vectorized query lowering; "
            "no partner continuation is needed on the promoted path."
        ),
        primary_route="prepared grouped-segment any-hit primitive with NumPy vectorized query lowering",
        partner_policy="none",
        primitive_contract="PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1",
        user_choice_guidance=(
            "Use `lowering_mode=\"numpy_arrays\"` for large prepared probes to avoid "
            "Python endpoint/ctypes materialization debt. Use a custom partner only "
            "for app-owned postprocessing outside the promoted flag/count contract."
        ),
        rejected_or_unpromoted_candidates=("custom partner flag-reduction route",),
        next_runtime_action=(
            "preserve the prepared-buffer and device-buffer/count split; do not turn "
            "the sampled grouped-segment contract into robot-planner wording; validate "
            "AMD functional parity later"
        ),
        evidence_refs=("Goal2654", "Goal3567", "Goal3755", "Goal3757", "Goal4428", "Goal4446"),
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
        decision_kind="mixed_explicit",
        current_reader_decision=(
            "Use scale-dependent explicit Barnes-Hut force-summary route guidance. "
            "Goal4458 reranks the current front doors at 8192/16384/32768 bodies and "
            "keeps fused CPU/Numba ahead of fused Numba CUDA and prepared RTDL/OptiX+Numba. "
            "Goal4483 extends the same rerank to 65536/131072 bodies; there, "
            "fused Numba CUDA is fastest by 2.31x-2.95x versus fused CPU/Numba "
            "and 5.27x-13.77x versus prepared RTDL/OptiX+Numba. Use "
            "fused_frontier_force_sum_bucketized_cpu_numba for small tested CPU-fastest rows. "
            "Use fused_frontier_force_sum_bucketized_numba_cuda for the no-C++ Python-source "
            "GPU fused partner lane and for the current larger tested rows. Use "
            "prepared_aggregate_frontier_weighted_vector_optix with --partner numba when the "
            "purpose is RTDL/OptiX RT-core aggregate-frontier device-column execution evidence. "
            "Goal4440 host-materialized logical baselines remain diagnostic. For that prepared "
            "OptiX contract, Numba remains the fastest measured GPU partner. For the prepared "
            "OptiX contract, Numba remains faster than CuPy on Goal4458 and Goal4483. Do "
            "not state Barnes-Hut RT-core speedup wording."
        ),
        primary_route=(
            "mixed explicit: scale-dependent fused CPU/Numba or fused Numba CUDA app route; "
            "RTDL/OptiX+Numba for RT-core device-column evidence"
        ),
        partner_policy="explicit_route_choice_cpu_numba_or_optix_numba_cupy_comparison",
        primitive_contract="aggregate-frontier fused vector sum plus prepared device-column frontier continuation",
        user_choice_guidance=(
            "Choose fused_frontier_force_sum_bucketized_cpu_numba for the small tested "
            "Goal4458 rows where CPU/Numba is fastest. Choose "
            "fused_frontier_force_sum_bucketized_numba_cuda for the larger tested "
            "Goal4483 65,536 / 131,072 rows and when the user wants a GPU fused route "
            "without writing C++ or CUDA source. Choose "
            "prepared_aggregate_frontier_weighted_vector_optix with --partner numba when testing "
            "the RTDL/OptiX RT-core device-column route. Keep CuPy available as the same-contract "
            "comparison partner, but do not promote it over Numba for the prepared OptiX "
            "aggregate-frontier route after Goal4458/Goal4483. Do not auto-select across CPU-fused, "
            "Numba CUDA fused, OptiX device-column, and older exact-force contracts."
        ),
        rejected_or_unpromoted_candidates=(
            "universal Numba fastest claim",
            "universal CuPy fastest claim",
            "whole Barnes-Hut speedup claim",
            "RT-core N-body speedup claim",
            "public backend speedup claim from host-materialized CPU/Embree baselines",
            "Barnes-Hut RT-core speedup claim after Goal4442 fused CPU/Numba evidence",
            "Barnes-Hut RT-core speedup claim after Goal4458 current front-door rerank",
            "Barnes-Hut RT-core speedup claim after Goal4483 larger-row rerank",
            "universal CPU/Numba fastest claim after Goal4483",
            "promoting prepared OptiX+CuPy over prepared OptiX+Numba after Goal4458",
        ),
        next_runtime_action=(
            "if Barnes-Hut RT-core acceleration remains a goal, design a fused RT-native/device "
            "route that avoids aggregate-frontier row emission and compare it against Goal4483 "
            "large-row fused Numba CUDA plus Goal4458 small-row fused CPU/Numba under the same "
            "force-summary contract; otherwise keep Barnes-Hut as mixed explicit scale-dependent "
            "fused CPU/GPU partner plus RT device-column evidence"
        ),
        evidence_refs=(
            "Goal2803",
            "Goal3599",
            "Goal3746",
            "Goal3762",
            "Goal3869",
            "Goal4052",
            "Goal4053",
            "Goal4436",
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
        decision_kind="mixed_explicit",
        current_reader_decision=(
            "Use the exact float64 RTDL/OptiX native ranked-summary aggregate when the user needs "
            "same-contract backend comparison against Embree. Goal4381 shows OptiX is 10.14x "
            "faster than Embree on the 1,048,576-point uniform aggregate row and 11.80x faster "
            "on the 262,144-point shell row. Use prepared_ranked_summary_graph_partner_bridge "
            "when the user wants the current resident app bridge: Goal4443 records a 1,048,576 "
            "resident search scene with a 65,536-query batch, repeat=1000, signature-matched "
            "CuPy and Numba same-stream partner reductions, and about 5ms hot median per batch "
            "for both partners. Goal4459 extends the same resident app-bridge contract to a "
            "clustered 1,048,576-point scene with 65,536-query batches and repeat=1000: "
            "CuPy measures 130.079ms hot median per batch, Numba measures 131.442ms, both "
            "partners preserve the same signature, use CUDA graph replay and same-stream "
            "device reductions, and pass the no-hidden-column-copy hot-window gate. Goal4460 adds "
            "the shell distribution row to the same contract: CuPy measures 38.588ms hot median "
            "per batch and Numba measures 39.267ms, with the same parity and hot-window gates. Keep exact "
            "float64 aggregate and float32 graph-bridge rows separate."
        ),
        primary_route=(
            "mixed explicit RTNN route: exact RTDL/OptiX native aggregate for same-contract "
            "OptiX-vs-Embree comparison; prepared graph plus explicit CuPy/Numba same-stream "
            "partner reductions for resident app-bridge evidence"
        ),
        partner_policy="mixed_explicit_user_choice",
        primitive_contract="fixed-radius ranked nearest summary aggregate plus resident graph partial-summary bridge",
        user_choice_guidance=(
            "Choose prepared_ranked_summary_raw or the native aggregate runner row when exact float64 "
            "backend comparison is required. Choose prepared_ranked_summary_graph_partner_bridge for "
            "the resident float32 app bridge and keep both CuPy and Numba visible; CuPy is the slightly "
            "faster measured partner in the M47 uniform row, M63 clustered row, and M64 shell row, "
            "while Numba is near parity and remains the no-C++ Python-source reference. Do not "
            "auto-select across exact aggregate, float32 graph bridge, distribution, or official "
            "RTNN diagnostic rows."
        ),
        rejected_or_unpromoted_candidates=(
            "RTNN paper reproduction",
            "official RTNN comparison without output-contract equivalence",
            "automatic exact-vs-float32 route selection",
            "arbitrary ANN index speedup claim",
            "treating the clustered resident app bridge as a full RTNN paper row",
            "treating the shell resident app bridge as a full RTNN paper row",
        ),
        next_runtime_action=(
            "preserve exact aggregate and resident graph bridge as separate front-door rows; future "
            "work is paper-dataset acquisition and official RTNN same-output-contract comparison, "
            "not more synthetic distribution timing"
        ),
        evidence_refs=(
            "Goal2821",
            "Goal2822",
            "Goal3820",
            "Goal3937",
            "Goal4381",
            "Goal4422",
            "Goal4443",
            "Goal4459",
            "Goal4460",
        ),
        pod_needed_next=False,
    ),
    CurrentBenchmarkRouteDecision(
        app="triangle_counting",
        decision_kind="primitive_first",
        current_reader_decision=(
            "Use the generic RT graph relationship-count composition for the scalar answer. "
            "When the user explicitly wants the RT-Graph summary-contract partner route, "
            "Goal4444 makes Numba a much fairer no-C++ reference by replacing the old "
            "cpu_contract_then_numba_device_upload staging path with "
            "direct_binary_numpy_summary_then_numba_device_upload, and Goal4453 removes "
            "the follow-on host geometry materialization/re-upload by filling RT-1A2/RT-2A1 "
            "geometry from partner-resident Numba device columns. The Goal4444 staging fix "
            "measured a 19.96x-23.07x Numba total-time improvement over M27 on the same two "
            "mappings, and Goal4454 adds dense-label plus sorted-key summary fast paths that "
            "improve the same explicit Numba route by about 1.60x-1.65x total time on the "
            "200,000 K4-clique dense/sorted fixture. Goal4455 re-ranks after that improvement: "
            "CuPy remains the measured performance partner, about 2.85x faster than optimized "
            "Numba total time on the same 200,000 K4-clique fixture. "
            "Goal4456 extends the Numba summary fast path from dense labels to bounded-id "
            "gapped nonnegative labels, with a 4.71x compaction subphase win on a stride-2 "
            "200,000 K4-clique fixture. "
            "Goal4457 removes host-column materialization from the app's CuPy device-column "
            "summary route, improving CuPy total time by about 1.37x-1.40x versus Goal4455 "
            "on the dense 200,000 K4-clique fixture. "
            "Goal4461 adds an explicit segmented duplicate two-hop RT-2A1 CuPy route that "
            "builds only a directed CSR and two-hop count estimate, then reuses one generic "
            "OptiX triangle scene across bounded ray batches. On the 200,000 K4-clique row "
            "it matched the generated 800,000-triangle oracle with 1,200,000 directed edge "
            "triangles, 800,000 duplicate two-hop rays, four segments, and no global two-hop "
            "summary materialization. Goal4462 then runs the same segmented route on the real "
            "`com-lj` paper dataset, replacing the Goal2593 7,429,851,776-byte CUDA allocation "
            "failure with an exact 177,820,130 / 177,820,130 triangle-count match over "
            "33,895,259 directed edge triangles, 928,731,472 duplicate two-hop rays, and "
            "186 segments. Goal4463 then adds source-range triangle-scene segmentation "
            "and runs `soc-LiveJournal1`, matching 285,730,264 / 285,730,264 expected "
            "triangles over 42,260,523 directed edge triangles, 1,383,299,326 duplicate "
            "two-hop rays, 6 scenes, and 280 ray segments, with neither global two-hop "
            "summary nor global triangle scene materialized. Goal4464 then extends the "
            "same source-range segmented route to `com-orkut`: 8M and 4M directed-edge "
            "scene caps still OOMed at OptiX scene preparation, while the measured 2M "
            "cap matched 627,584,181 / 627,584,181 expected triangles over 117,117,316 "
            "directed edge triangles, 8,579,930,671 duplicate two-hop rays, 59 scenes, "
            "and 1,744 ray segments. CuPy remains the current large-scale performance "
            "partner for this explicit route; this is still not a triangle-count RT-core "
            "speedup claim. Goal4465 removes the avoidable Python per-edge planner loop "
            "from that route with NumPy prefix/searchsorted segmentation, reducing the "
            "`com-orkut` planner median from 28.885s to 3.665s while preserving the same "
            "scene/ray counts and exact triangle result. Goal4466 then tunes ray batch "
            "size for `com-orkut`: 15M reduces the warmup-0 repeat-1 probe to 34.231s "
            "and ray build to 5.629s, while 18M and 20M fail with CUDA OOM during query. "
            "Goal4467 refreshes the current comparison packet with exact current RTDL "
            "large-row totals: 14.153s on `com-lj`, 25.747s on `soc-LiveJournal1`, "
            "and 115.032s on `com-orkut`. cuGraph remains 8.26x-15.91x faster "
            "end to end, and authors pure count kernels remain much faster than RTDL "
            "query traversal. Goal4468 adds explicit unique-weighted segment rays: "
            "per-segment duplicate two-hop `(src, dst)` probes are compressed into "
            "unique rays plus uint64 weights before the same generic weighted any-hit "
            "primitive runs. On the three large rows this reduces physical rays by "
            "1.76x-1.84x and improves traversal median by 2.36x-2.47x, but the "
            "CuPy unique compression cost makes whole totals only slightly better on "
            "`com-lj`/`soc-LiveJournal1` and slightly worse on `com-orkut`. "
            "Goal4469 adds explicit prepared segment replay: build one compressed "
            "segment, replay warmup/repeat queries, then release it. This improves "
            "formal totals to 9.552s on `com-lj`, 17.986s on `soc-LiveJournal1`, "
            "and 62.428s on `com-orkut`, or 1.43x-1.84x faster than Goal4467. "
            "Goal4470 refreshes the comparison packet after M73: the cuGraph gap "
            "narrows from 8.26x-15.91x to 5.58x-8.64x, but cuGraph still wins "
            "end to end and authors pure count kernels remain much faster. "
            "Goal4471 then reruns the three large rows with explicit `phase_split_ms`: "
            "`com-lj` pays 2.341s build-once and 0.925s median replay query, "
            "`soc-LiveJournal1` pays 3.035s build-once and 1.282s median replay "
            "query, and `com-orkut` pays 15.243s build-once and 8.216s median "
            "replay query. Counts match the known expected paper-dataset counts. "
            "Goal4472 then adds explicit `numba_direct` unique-key fill: segment-ray "
            "build improves by 1.17x/1.36x/1.64x and backend phase by "
            "1.05x/1.03x/1.09x on `com-lj`/`soc-LiveJournal1`/`com-orkut`, "
            "but total wall time is mixed, so this remains an explicit option. "
            "Goal4473 adds backend query-phase telemetry on the same three large "
            "rows: `numba_direct` total is 1.09x/1.08x/1.12x faster in the M77 "
            "packet, segment-ray build is 1.18x/1.34x/1.64x faster, and native "
            "query pack plus traversal is about 1.00x between key builders. The "
            "remaining query-wall movement is therefore non-native replay envelope "
            "cost, not evidence of slower RT traversal. Goal4474 adds a generic "
            "prepared ray-batch weighted any-hit sum and wires prepared segment "
            "replay through it. This moves ray-column packing to an explicit "
            "build-once `prepared_ray_batch_build` phase and improves query median "
            "by about 4.8x-5.2x versus M77; current `numba_direct` totals are "
            "5.404s, 11.669s, and 35.379s on the three large rows. Goal4475 "
            "refreshes the post-M78 comparison: cuGraph remains 3.15x-4.89x "
            "faster end to end, RTDL M78 is 5.92x-7.99x faster than the authors "
            "`rt_tc` full pipeline on the two completed rows because authors "
            "preprocessing dominates, and authors pure count kernels remain "
            "faster than RTDL M78 query. Goal4476 tests and rejects removing "
            "per-segment weight-sum reduction/sync telemetry: M80 no-sync and "
            "explicit-sync variants do not improve total/backend timing, so "
            "M78 remains the current best internal route. Goal4477 adds the "
            "app-agnostic compact `xz_constant_y_direction` prepared ray-batch "
            "ABI and tests it on all three large rows. It preserves counts and "
            "RT traversal medians are essentially unchanged, but best M81 totals "
            "are slower than M78 by 20.9%/16.2%/6.3%, so the current route does "
            "not switch. Goal4478 adds explicit `sync_subphases` telemetry for "
            "segment-ray construction. The three large rows show "
            "`cupy_unique_counts` as the top subphase: 0.694s/1.035s/6.306s, "
            "or 41.6%/46.8%/53.3% of segment-ray construction. Goal4479 tests "
            "an explicit `numba_direct_sort_rle` replacement for that phase. "
            "Counts, lowered ray counts, and weight sums match `numba_direct`, "
            "while same-commit w1/r3 totals improve to 6.489s/13.273s/35.990s "
            "from 7.308s/14.467s/38.564s. Goal4480 retests compact constant-ray "
            "columns with `numba_direct_sort_rle`; prepared batch build improves "
            "only 1.02x-1.03x and total time is 0.924x/0.945x/0.986x, so the "
            "compact layout remains rejected for this route. Goal4481 tests "
            "`numba_fused_decode_project`; counts/rays/weights match, but "
            "total time is 0.899x/0.945x/0.953x and segment-ray build is "
            "0.661x/0.701x/0.664x, so CuPy vectorized output remains current. "
            "Goal4482 scouts whether the remaining unique/count boundary can "
            "use an already-sorted source-group skip-sort fast path. It cannot: "
            "sorted source groups cover only 0.131%/0.617%/0.001% of two-hop "
            "rows on `com-lj`/`soc-LiveJournal1`/`com-orkut`, so that shortcut "
            "is rejected and the current internal route remains unchanged. "
            "Goal4492 then measures bounded source-group local unique-count "
            "coverage: 16K rows covers 93.73%/89.85%/69.43% of two-hop rows "
            "and 65K covers 99.85%/99.38%/98.44%, so a single small bounded "
            "local kernel is not the right default; the credible next shape is "
            "hybrid/two-pass small-source local unique plus large-tail sort/RLE "
            "fallback. Goal4493 validates a bounded `<=2048` local-hash "
            "prototype over 20M selected two-hop rows per paper dataset: it "
            "matches fill plus sort/RLE and is 1.13x/1.01x/1.43x faster on "
            "`com-lj`/`soc-LiveJournal1`/`com-orkut`. Goal4494 implements the "
            "integrated per-segment local-hash plus large-tail sort/RLE candidate "
            "and rejects it: counts match, but backend and segment-ray construction "
            "are slower than the current `numba_direct_sort_rle` route on all "
            "three paper rows."
        ),
        primary_route="generic RT graph relationship-count composition",
        partner_policy="primitive_only",
        primitive_contract="canonical graph-cycle scalar count",
        user_choice_guidance=(
            "For the scalar answer, stay on the primitive-first relationship-count route. "
            "For explicit RT-Graph summary-contract experiments, choose CuPy for the current "
            "fastest large-scale graph-contract builder. Numba remains the no-C++ reference "
            "when Python-source partner code matters; cite Goal4444 for direct binary summary "
            "construction, Goal4453 for partner-resident Numba geometry fill, Goal4454 "
            "for dense-label/sorted-key summary fast paths, and Goal4455 for the post-M58 "
            "CuPy-vs-Numba rerank. Cite Goal4456 when gapped but bounded nonnegative graph ids "
            "are the reason the Numba path avoids `np.unique(return_inverse)` remapping. "
            "Cite Goal4457 for the current CuPy app route that skips host-column materialization."
            " Cite Goal4461 when the user needs the segmented RT-2A1 route that avoids global "
            "two-hop summary materialization by lowering duplicate two-hop rays in bounded "
            "generic RT batches. Cite Goal4462 when the user asks whether this segmented "
            "route actually runs a formerly OOM paper dataset: `com-lj` now matches the "
            "expected triangle count exactly. Cite Goal4463 when the requested dataset "
            "also needs source-range triangle-scene segmentation: `soc-LiveJournal1` "
            "now matches the expected triangle count exactly. Cite Goal4464 when the "
            "largest paper row is requested: `com-orkut` now matches exactly with a "
            "2M directed-edge scene cap, after larger scene caps OOMed during OptiX "
            "scene preparation. Cite Goal4465 when discussing the current optimized "
            "segmented planner: it is a partner-side prefix/searchsorted optimization, "
            "not a native-engine specialization. Cite Goal4466 when discussing explicit "
            "ray-batch cap tuning: use 5M as conservative and 15M as the measured "
            "`com-orkut`/RTX 4000 Ada tuned cap; do not auto-hide larger caps. "
            "Cite Goal4467 for the current comparison packet and its no-speedup boundary. "
            "Cite Goal4468 when choosing the explicit `unique_weighted` segmented "
            "ray representation: it reduces traversal pressure but makes partner "
            "compression the bottleneck, so it is not an automatic default. Cite "
            "Goal4469 when the user wants the explicit prepared/repeated schedule: "
            "`prepared_segment_replay` builds each compressed segment once, replays "
            "queries, and releases it. Cite Goal4470 for the current post-M73 "
            "comparison packet and its still-blocked public-speedup boundary. Cite "
            "Goal4471 when wording needs cold/build versus hot/replay phase split: "
            "the app now emits `phase_split_ms`, and legacy build totals must not "
            "be read as paid every measured replay. Cite Goal4472 when the user "
            "asks for the no-C++ direct unique-key builder: "
            "`--segment-unique-key-builder numba_direct_sort_rle` is now the "
            "current measured internal route; use `numba_direct` as the "
            "Goal4472/Goal4478 baseline. It is still not a hidden default. Cite Goal4473 "
            "when the user asks whether M76's query-side movement is native RT "
            "traversal: M77 shows native query pack/traversal are essentially "
            "unchanged, while total time favors `numba_direct` on all three rows. "
            "Cite Goal4474 when discussing the current prepared replay route: it "
            "uses generic prepared ray batches so repeated ray-column packing is "
            "paid once as `prepared_ray_batch_build`, not on every replay query. "
            "Cite Goal4475 for the current post-M78 comparison packet: cuGraph "
            "is still 3.15x-4.89x faster end to end, while RTDL's full-pipeline "
            "authors-code reading remains distinct from pure counting-kernel timing. "
            "Cite Goal4476 when ruling out scalar weight-sum telemetry/copy-back "
            "as the main remaining debt. Cite Goal4477 when discussing the "
            "compact constant-ray prepared batch ABI: it is a valid generic ABI, "
            "but it is not the Triangle Counting current-best route because it "
            "does not improve the large-row totals. Cite Goal4478 when discussing "
            "the segment-ray construction bottleneck: `cupy_unique_counts` was "
            "the measured first target. Cite Goal4479 for the current "
            "`numba_direct_sort_rle` route and its still-unsolved unique/count "
            "materialization boundary. Cite Goal4480 when rejecting compact "
            "constant-ray columns on top of the sort/RLE route. Cite Goal4481 "
            "when rejecting the no-C++ Numba fused decode/project output builder. "
            "Cite Goal4482 when rejecting an already-sorted source-group "
            "skip-sort fast path: sorted two-hop row coverage is below 1% on "
            "all three large rows. Cite Goal4492 when rejecting a single small "
            "bounded local unique-count kernel and when choosing a hybrid/two-pass "
            "source-group plan instead. Cite Goal4493 when the user asks whether "
            "the local-hash branch itself is viable: it validates at 20M selected "
            "small-group rows. Cite Goal4494 when rejecting the integrated "
            "per-segment local-hash plus large-tail sort/RLE candidate: it is "
            "correct, but backend and segment-ray construction are slower than "
            "the current `numba_direct_sort_rle` route on all three paper rows."
        ),
        rejected_or_unpromoted_candidates=(
            "auto fallback timing route",
            "RT-core triangle-count paper claim",
            "old M27 cpu_contract_then_numba_device_upload timing as current Numba guidance",
            "host-materialized Numba geometry upload as current Numba guidance",
            "treating dense-label/sorted-key summary fast paths as universal graph input behavior",
            "promoting Numba over CuPy after Goal4454 without the Goal4455 rerank evidence",
            "treating bounded-id remap as safe for huge sparse id spaces",
            "requiring CuPy host-column materialization in app summary mode after Goal4457",
            "treating the Goal4461 segmented RT-2A1 route as a public triangle-count RT-core speedup claim",
            "treating the Goal4462 com-lj success as a refreshed full paper-dataset speedup matrix",
            "treating the Goal4463 soc-LiveJournal1 success as a refreshed full paper-dataset speedup matrix",
            "treating the Goal4464 com-orkut success as a public RTDL-vs-cuGraph or RTDL-vs-authors speedup claim",
            "treating the Goal4465 planner speedup as an RT-core traversal speedup",
            "making the Goal4466 15M ray-batch cap a universal or hidden automatic default",
            "claiming Goal4467 shows RTDL beats cuGraph or authors pure kernels",
            "making Goal4468 unique-weighted rays a hidden automatic default",
            "claiming Goal4468 solves whole-route triangle-count performance",
            "making Goal4469 prepared segment replay a hidden automatic default",
            "claiming Goal4469 authorizes public RT-core triangle-count speedups",
            "claiming Goal4470 shows RTDL beats cuGraph or authors pure kernels",
            "reading legacy segment_ray_build_total_ms as actual paid wall time after Goal4471",
            "making Goal4472 numba_direct unique-key fill a hidden default",
            "making Goal4473 query-phase telemetry a hidden automatic key-builder selector",
            "treating Goal4473 query-wall movement as native RT traversal regression",
            "treating Goal4474 prepared ray batches as graph-specific native engine callbacks",
            "claiming Goal4474 alone refreshes RTDL-vs-cuGraph or authors-code comparisons",
            "claiming Goal4475 shows RTDL beats cuGraph or authors pure kernels",
            "promoting the Goal4476 no-weight-sum-sync candidate as an optimization",
            "promoting the Goal4477 compact constant-ray batch layout as the current Triangle Counting route",
            "claiming Goal4479 solves Triangle Counting partner materialization rather than improving the unique/count boundary",
            "promoting the Goal4480 compact constant-ray layout retest on top of sort/RLE",
            "promoting the Goal4481 numba_fused_decode_project output builder",
            "promoting an already-sorted source-group skip-sort fast path after Goal4482",
            "promoting a single small bounded source-group local unique-count kernel after Goal4492",
            "treating the Goal4493 local-hash prototype as route evidence without integrated rerank",
            "promoting the Goal4494 per-segment local-hash plus large-tail sort/RLE candidate",
            "spending the next Triangle Counting optimization cycle on counts/filter, duplicate count sum, or RT traversal before further reducing Goal4479 sort/RLE unique-count cost",
            "automatic CuPy-vs-Numba partner selection",
        ),
        next_runtime_action=(
            "preserve the generic graph relationship-count route and avoid claiming RT-core "
            "triangle-count acceleration; current comparison packet is complete for the "
            "large former-OOM rows (`com-lj`, `soc-LiveJournal1`, and `com-orkut`), "
            "Goal4468 proves unique-weighted segment rays reduce traversal pressure, "
            "and Goal4469 proves explicit prepared segment replay improves large-row "
            "totals; Goal4471 separates one-shot build cost from replay throughput; "
            "Goal4472 adds explicit no-C++ numba_direct unique-key fill with "
            "build/backend wins, and Goal4473 shows M77 totals favor numba_direct "
            "while native query pack/traversal are effectively unchanged; Goal4474 "
            "adds the reusable prepared ray-batch weighted-sum API and makes it "
            "the prepared replay path; Goal4475 refreshes the post-M78 comparison "
            "packet and keeps public speedup wording blocked; Goal4476 rules out "
            "weight-sum telemetry/sync cleanup as a useful next optimization; "
            "Goal4477 adds and tests a compact constant-ray prepared batch ABI "
            "but keeps M78 as current best because totals regress; next work is "
            "targeting partner materialization and segment-ray construction; "
            "Goal4478 identifies `cupy_unique_counts` as the scaling hotspot, "
            "and Goal4479 replaces it with explicit in-place sort/RLE counting, "
            "making `numba_direct_sort_rle` the current internal route; next "
            "work is further reducing sort/RLE unique-count cost, Numba key "
            "fill, or fused decode/projection; Goal4480 shows compact "
            "constant-ray columns should not be the next route-promotion target, "
            "and Goal4481 shows a simple no-C++ Numba fused decode/project "
            "output builder should not be promoted; Goal4482 shows an "
            "already-sorted source-group skip-sort fast path should not be "
            "promoted because sorted two-hop row coverage is below 1% on all "
            "large rows; Goal4492 shows a single small bounded local unique-count "
            "kernel is also insufficient because 16K covers only 69.43% of "
            "`com-orkut` two-hop rows, so next useful work must avoid "
            "overfitting to only small source groups; Goal4493 validates "
            "the small-source `<=2048` local-hash branch, and Goal4494 "
            "implements the integrated local-hash plus large-tail sort/RLE "
            "candidate, but rejects it because backend and segment-ray build "
            "time are worse on all three paper rows. Keep `numba_direct_sort_rle` "
            "as the current complete route. If Triangle Counting is revisited, "
            "the target is a coarser-batched segmented unique/count strategy "
            "with fewer per-segment kernel launches or a different reusable "
            "segmented reduction primitive, not this exact per-segment local "
            "hash branch."
        ),
        evidence_refs=(
            "Goal2797",
            "Goal3567",
            "Goal3782",
            "Goal3819",
            "Goal3856",
            "Goal4424",
            "Goal4444",
            "Goal4453",
            "Goal4454",
            "Goal4455",
            "Goal4456",
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
            "Goal4492",
            "Goal4493",
            "Goal4494",
        ),
        pod_needed_next=False,
    ),
)


def _refresh_goal4484_route_decisions(
    rows: tuple[CurrentBenchmarkRouteDecision, ...],
) -> tuple[CurrentBenchmarkRouteDecision, ...]:
    refreshed: list[CurrentBenchmarkRouteDecision] = []
    for row in rows:
        if row.app != "rt_dbscan":
            refreshed.append(row)
            continue
        refreshed.append(
            CurrentBenchmarkRouteDecision(
                app="rt_dbscan",
                decision_kind="mixed_explicit",
                current_reader_decision=(
                    "Use the explicit RTDL/OptiX predicate direct-status CuPy "
                    "column-signature route with the prepared self-query "
                    "count-threshold producer for the measured 524k and 1M compact "
                    "cluster-size/noise/core summary profiles. Keep grouped-stream "
                    "Numba as the conservative same-contract fallback/reference path. "
                    "Set `output_mode=\"component_signature\"` when compact summaries "
                    "are sufficient. "
                    "Set `output_mode=\"full\"` only when per-point Python cluster "
                    "rows are actually required, and keep graph-only component "
                    "signatures out of full DBSCAN wording."
                ),
                primary_route=(
                    "explicit RTDL/OptiX self-query count-threshold device columns plus CuPy "
                    "predicate direct-status compact signature; grouped-stream Numba fallback"
                ),
                partner_policy="mixed_explicit_user_choice",
                primitive_contract=(
                    "fixed-radius core flags and grouped-stream component labels with "
                    "explicit compact component-signature or full-row output"
                ),
                user_choice_guidance=(
                    "Choose the output contract first. For compact summaries at the "
                    "measured 524k and 1M clustered3d/road3d/ngsim_dense profiles, choose "
                    "the explicit self-query predicate direct-status CuPy route with "
                    "`partition_cell_factor` set explicitly; use grouped-stream Numba "
                    "when a conservative same-contract fallback/reference is needed. "
                    "Keep CuPy and Numba explicitly selected and measured. "
                    "Use `output_mode=\"full\"` only for row consumers that truly need "
                    "per-point labels in Python. Do not auto-select the partner, route, "
                    "factor, output contract, or border policy."
                ),
                rejected_or_unpromoted_candidates=(
                    "blocked grouped stream candidate from Goal3936",
                    "partition_convergence_hybrid default promotion after Goal4041 mixed timing",
                    "partition_convergence_hybrid full-DBSCAN promotion after Goal4047 graph-component-only app mode",
                    "partition_convergence_hybrid universal default promotion after Goal4108 prepared replay and Goal4109 app smoke",
                    "automatic partition-cell-factor tuning after Goal4117 explicit factor sweep",
                    "mixed predicate direct-status broad promotion after Goal4165 policy-variant probe",
                    "component-size signature as the only mixed-predicate semantic contract after Goal4166",
                    "graph-only direct-status component signature as full DBSCAN after Goal4484",
                    "full-row materialization as the default summary-output contract after Goal4445",
                    "automatic output_mode/partner selection after Goal4452 route refresh",
                    "promoting temporary app-constructed point columns as the default after Goal4495",
                ),
                next_runtime_action=(
                    "keep predicate direct-status as the measured explicit compact-signature "
                    "route for the Goal4484/Goal4485/Goal4486/Goal4488/Goal4489/Goal4490 524k and 1M profiles, "
                    "with Goal4495 extending the caller-owned point-column reuse boundary to the 2M `road3d` profile; "
                    "keep grouped-stream Numba as fallback/reference; keep full Python row materialization explicit; "
                    "keep the profile/reuse advisor visible for explicit route choices; "
                    "Goal4488 reduces direct-status row-columnization prepare debt and Goal4489 "
                    "adds the shared device-coordinate-column entry point; Goal4490 adds an explicit charged "
                    "app mode and shows app-constructed coordinate columns are not a default promotion; "
                    "Goal4491 removes redundant coordinate-helper pre-scan but keeps the same promotion boundary; "
                    "Goal4495 shows that existing device columns remain valuable at 2M road3d, but temporary "
                    "app-constructed columns are still essentially flat when charged; next serious runtime work "
                    "is broader non-road3d 2M profile coverage or a policy primitive only if new evidence requires it. "
                    "hidden factor selection, hidden output-contract selection, hidden border-policy "
                    "selection, and automatic partner selection remain blocked."
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
                    "Goal4093",
                    "Goal4096",
                    "Goal4100",
                    "Goal4104",
                    "Goal4105",
                    "Goal4108",
                    "Goal4109",
                    "Goal4114",
                    "Goal4116",
                    "Goal4117",
                    "Goal4121",
                    "Goal4122",
                    "Goal4126",
                    "Goal4130",
                    "Goal4134",
                    "Goal4138",
                    "Goal4158",
                    "Goal4159",
                    "Goal4160",
                    "Goal4164",
                    "Goal4165",
                    "Goal4166",
                    "Goal4167",
                    "Goal4169",
                    "Goal4172",
                    "Goal4173",
                    "Goal4174",
                    "Goal4176",
                    "Goal4177",
                    "Goal4445",
                    "Goal4452",
                    "Goal4484",
                    "Goal4485",
                    "Goal4486",
                    "Goal4487",
                    "Goal4488",
                    "Goal4489",
                    "Goal4490",
                    "Goal4491",
                    "Goal4495",
                ),
                pod_needed_next=False,
            )
        )
    return tuple(refreshed)


CURRENT_BENCHMARK_ROUTE_DECISIONS = _refresh_goal4484_route_decisions(
    CURRENT_BENCHMARK_ROUTE_DECISIONS
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
