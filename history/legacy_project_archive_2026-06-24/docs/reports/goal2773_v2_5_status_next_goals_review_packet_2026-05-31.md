# Goal2773 - v2.5 Status And Next-Goals Review Packet

Date: 2026-05-31

Status: review packet / planning document. This is not a release gate and does
not authorize public performance wording.

## Purpose

This document consolidates where RTDL v2.5 stands after Goal2772 and proposes
the next planned goals needed to finish a defensible v2.5 internal milestone.
It is written for external reviewers so they can critique the scope, risks,
missing primitives, and release-readiness path before the next implementation
push.

## v2.5 Goal Restatement

The current v2.5 goal should not be phrased as "all 10 apps must run on
Triton." The better goal is:

RTDL v2.5 should prove that the app-agnostic RTDL engine can hand generic
device-resident RT outputs to explicit partner continuations, with per-phase
partner choice, neutral buffer/lifetime discipline, and tiered same-contract
benchmark evidence.

This means:

- Triton is an important optimized partner, not a mandatory partner.
- CuPy remains a valid partner where it is the right tool, especially for
  irregular or fallback-backed phases.
- CPU/reference continuation must remain available for correctness and
  portability.
- Partner selection must be explicit, documented, and fail-closed.
- Performance claims must be per-phase/per-partner unless whole-app evidence
  is separately measured and reviewed.

## Design Rules That Must Hold

1. **Engine remains app-agnostic.** Native RTDL primitives may expose generic
   hit streams, primitive ids, ray ids, typed payload columns, status buffers,
   and reductions. They must not expose RayDB, DBSCAN, RayJoin, Hausdorff,
   RTNN, Barnes-Hut, or other app-specific semantics.
2. **Partner choice belongs to the user/app layer.** The runtime may provide
   helpers, plan/explain metadata, and supported partner cells, but it must not
   silently force one partner for all apps.
3. **Every handoff must have explicit ownership and copy semantics.** If a
   boundary is same-pointer / CUDA-array / DLPack-compatible, say so. If it
   copies, label the copy. Do not call reduced-copy or stream-ordered staging
   "true zero-copy."
4. **Benchmarks are tiered.** Tier A aims for same-contract parity. Tier B is
   per-app bets with fallback paths. Tier C is no-regression RT-path evidence,
   not partner parity.
5. **Claims stay bounded.** No public speedup wording, broad RT-core wording,
   true-zero-copy wording, or release wording is authorized by this packet.

## Current Location After Goal2772

The v2.5 work has made substantial progress on the RT-output-to-partner seam.
The most recent chain is:

| Goal | Main contribution | Status |
| --- | --- | --- |
| Goal2756 | Reusable OptiX hit-stream device output buffers | Implemented/reviewed |
| Goal2758 | Reusable hit-stream buffer performance probe | Implemented/reviewed |
| Goal2760 | Async hit-stream promotion requirements gate | Implemented/reviewed |
| Goal2762 | Device status buffers for row count / hit count / overflow | Implemented/reviewed |
| Goal2764 | Same-stream status consumer | Implemented, Claude+Gemini reviewed |
| Goal2767 | Stream-ordered async input upload hardening | Implemented/reviewed |
| Goal2768 | Same-stream bounded row-window consumer | Implemented/reviewed |
| Goal2769 | Same-stream row-reduction consumer | Implemented/reviewed |
| Goal2770 | CUDA-event ordered cross-stream row-reduction consumer | Implemented/reviewed |
| Goal2771 | Event-ordered grouped reduction by generic `ray_id` | Implemented/reviewed |
| Goal2772 | Richer grouped reductions: count/sum/xor/min/max/first/last | Implemented/reviewed |

Latest pod evidence:

- Goal2772 full test: 7 tests OK.
- Corrected v2.5 hit-stream regression including Goal2772: 60 tests OK.
- Pod built OptiX with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- A real initializer bug in `group_last_hit_row_index` was caught on pod and
  fixed before consensus.

The current result is best described as:

> A strong bounded OptiX hit-stream to partner-continuation substrate exists for
> generic row/status/grouped reductions, including CUDA-event cross-stream
> ordering and caller-owned device output columns.

It is not yet:

- a global neutral-buffer solution for every partner boundary;
- a full 10-app v2.5 benchmark closure;
- a release gate;
- proof of true zero-copy;
- proof of public speedup.

## Benchmark Tier Map

The accepted tiered manifest remains the clean framing for v2.5:

| App | Tier | Current v2.5 meaning | Remaining work |
| --- | --- | --- | --- |
| `raydb_style` | A | Strongest current prepared/hit-stream evidence | Fold into final harness/matrix |
| `triangle_counting` | A | Reduction-shaped and realistic | Triton/partner wiring plus streaming/OOM closure |
| `spatial_rayjoin` | A | Count/parity path is realistic | Decide count/parity v2.5 route and measure |
| `librts_spatial_index` | A | RT-core count baseline | Warm/median harness and no-regression evidence |
| `hausdorff_xhd` | B | Needs grouped max+argmax/witness | Add witness-preserving generic reduction |
| `rtnn` | B | Needs bounded top-k/ranked summary | Add ranked/top-k primitive and live harness |
| `barnes_hut` | B | Needs grouped vector sum | Add vector-valued grouped reduction or accepted fallback |
| `rt_dbscan` | B | Irregular components/union-find | Decide Triton-native attempt vs CuPy fallback-backed path |
| `contact_manifold` | C | RT collection baseline | No-regression harness, not partner parity |
| `robot_collision` | C | RT any-hit baseline | No-regression harness, not partner parity |

## Planned Next Goals

The current estimate is 8 major goals, likely 12-18 normal-sized Goal27xx
commits because each major item usually needs implementation, pod evidence,
review, and consensus.

| Planned goal | Purpose | Why it matters | Rough dependency |
| --- | --- | --- | --- |
| Goal2774 | Declare grouped-reduction support matrix and public internal API shape | Turns Goal2772 columns into a documented supported primitive family | Goal2772 |
| Goal2775 | Grouped max+argmax / witness-preserving reduction | Needed for `hausdorff_xhd` and other witness apps | Goal2774 |
| Goal2776 | Bounded top-k / ranked summary | Needed for RTNN-style nearest-neighbor benchmarks | Goal2774 |
| Goal2777 | Grouped vector sum | Needed for Barnes-Hut force/vector phases | Goal2774 |
| Goal2778 | DBSCAN components decision and fallback-backed contract | Prevents v2.5 from being blocked on pure Triton union-find research | Goal2774 |
| Goal2779 | Tier A benchmark harness execution | RayDB, triangle counting, RayJoin count/parity, librts count with same-contract timing | Goals2774-2778 as needed |
| Goal2780 | Cross-partner neutral-buffer/lifetime audit and fail-closed matrix | Checks whether v2.5 partner choice is real across boundaries, not just metadata | Ongoing |
| Goal2781 | v2.5 readiness packet and final review request | Consolidates evidence, docs, claim boundary, and remaining misses | All above |

## High-Risk Areas

1. **Global neutral-buffer seam is not fully closed.** Goal2770-2772 prove
   strong OptiX-to-CuPy/Torch-style paths for this hit-stream lane, but the
   older design risk remains: every partner boundary must be checked for hidden
   torch coercion or silent copies.
2. **DBSCAN may not be a Triton-native win.** The right v2.5 answer may be a
   fallback-backed CuPy components phase with explicit partner selection and
   honest same-contract timing.
3. **Top-k and witness reductions need careful semantics.** A fast primitive
   that loses witness identity, tie behavior, or row-order meaning is not
   acceptable.
4. **Tiered benchmark claims can drift into whole-app claims.** The final
   matrix must separate RT traversal, handoff, partner continuation, host
   materialization, and total time.
5. **Plan/explain must stay advisory.** A planner can suggest partners, but the
   user/app must be able to choose supported partners explicitly.

## Proposed Acceptance Bar For v2.5

v2.5 can be considered internally complete when:

- The supported partner-operation matrix is documented and tested.
- The runtime exposes grouped scalar, richer grouped, max+argmax, top-k/ranked,
  and vector-sum continuation shapes, or documents accepted fallback paths.
- Tier A apps have same-contract pod evidence with phase-separated timing.
- Tier B apps have either parity evidence or reviewed accepted misses/fallbacks.
- Tier C apps have no-regression evidence on their RT path.
- Cross-partner ownership/lifetime and copy/zero-copy metadata are
  machine-readable and fail-closed.
- No app-specific semantics enter native engine ABI or generic primitive names.
- Final release-readiness wording receives required external review before any
  public claim is made.

## Questions For External Reviewers

1. Is the v2.5 goal phrased correctly as partner-composable, per-phase parity
   rather than "all apps on Triton"?
2. Are the planned goals in the right order, or should top-k/witness/vector
   reductions be reprioritized?
3. Does Goal2772 provide enough substrate to start app-facing primitive work,
   or should Goal2780 neutral-buffer/lifetime audit happen first?
4. Is the DBSCAN fallback-backed path acceptable for v2.5, or should pure
   Triton union-find remain a release requirement?
5. Are any benchmark apps missing from the tier map or misclassified?
6. What additional conformance tests are necessary before v2.5 can be called
   internally complete?

## Bottom Line

RTDL v2.5 is no longer just a Triton preview. It now has a concrete, tested
device-resident hit-stream continuation substrate. The next work should convert
that substrate into declared, benchmark-relevant generic primitives and then
close the tiered benchmark matrix. The likely remaining distance is about 8
major goals, or 12-18 normal Goal27xx commits with pod evidence and review.
