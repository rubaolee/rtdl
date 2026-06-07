# Goal3709 Next Project Goals After Segment-Pair Exact Count

Date: 2026-06-07

## Position

The project direction remains:

- RTDL is a language/runtime for making hardware ray tracing units easier to use from Python.
- The native engine must stay generic and app-agnostic.
- Users choose partners. RTDL should provide high-performance reference support for partners it claims to support.
- Benchmark apps are not demos; they are the stress tests that force better generic primitives.
- The next work should attack major performance and design gaps, not close a version while weak benchmark rows remain.

Goal3700 through Goal3708 changed the immediate RayJoin line-segment intersection diagnosis:

| Step | RTDL LSI Count | RTDL Query Seconds | Relative To RayJoin | Meaning |
| --- | ---: | ---: | ---: | --- |
| Goal3698 guarded scalar count | `20860` | about `0.0072` | far slower | Correct, but host/candidate-heavy. |
| Goal3702 one-pass exact OptiX count | `20860` | `0.004467187` | `0.198743x` | Removed candidate download and separate exact-refine pass. |
| Goal3705 prepared-left one-pass exact count | `20860` | `0.0010864129` | `0.833929x` | Removed timed left upload and reached near-RayJoin latency. |
| Goal3708 no-telemetry negative probe | `20860` | `0.0011297837` | `0.777436x` | Disabling candidate telemetry did not help, so selected route keeps telemetry. |

This is a real improvement, but it is not enough. The remaining gap is not a documentation problem: RTDL is now close to RayJoin on this LSI count slice, but it is still behind on the same-source A5000 measurement. The project needs the next generic performance leap.

## Goal 1: RayJoin Same-Contract Composite Rebaseline

Build a current, reviewer-readable RayJoin app-level table after Goals 3700-3708.

Acceptance:

- Report RayJoin as one benchmark app and also expose its subcontracts.
- Include LSI count, PIP/closed-shape count, overlay/area, and any prepared-route rows currently used.
- For each row, state backend, partner, dataset, exact oracle, one-shot timing, prepared/resident timing, and claim boundary.
- Show the app-level composite score transparently rather than hiding weak rows behind averages.
- No "RTDL beats RayJoin" claim unless the evidence actually supports it.

Reason:

The user/reviewer view is app-level. Subcontract tables are useful for engineering, but the release story needs one honest RayJoin answer.

## Goal 2: Generic Dense-Boundary Exact Scalar Count

Build a generic exact scalar-count primitive or continuation for dense boundary-status workloads.

Acceptance:

- Native/runtime vocabulary stays generic: closed shape, relation status, boundary element, scalar count, correction, workspace.
- No RayJoin, county, CDB, GIS ownership, map, or app-specific terms in the native engine.
- Full-county exact count remains correct on the A5000 public CDB slice.
- Same-contract comparison includes the current resident/corrected route as baseline.
- Report separates one-shot, prepared, and resident timings.
- Claim-boundary flags remain false until a reviewed release packet authorizes wording.

Reason:

RayJoin PIP-style counts expose dense boundary sets. Materializing dense boundary rows is the wrong shape for scalar count-only workloads. The generic primitive should count/correct on device rather than shipping a large ambiguous row stream.

## Goal 3: Segment-Pair Exact Count Final Push

Decide whether the remaining LSI gap can be closed within the current generic architecture.

Candidate directions:

- Resident repeated-query executor to amortize Python/ctypes and launch setup.
- Hybrid exactness path that uses fast traversal plus targeted double-precision correction only where necessary.
- Better prepared-pair handle that keeps both left and right exact payloads resident across a batch.
- If none win, write a precise negative report explaining why RayJoin's app-specialized path still has the edge.

Acceptance:

- Exact count remains `20860` on the current same-source validation slice.
- Any improvement must compare against Goal3705, not against an obsolete slower RTDL route.
- If a route is slower, preserve it only as a negative probe and do not select it by default.
- The final report states whether the gap is launch/API overhead, traversal overhead, exact-predicate overhead, or app-specialized RayJoin logic.

Reason:

Goal3705 is close enough that a small amount of real generic runtime work might cross parity. But the project should not spend days on tiny telemetry toggles unless they change the app-level outcome.

## Goal 4: Numba Reference Paths For Partner-Needed Apps

For every benchmark app that needs custom continuation logic, provide a Numba-based high-performance reference path where technically possible.

Acceptance:

- Produce the 10-app table:
  - primitives only,
  - Numba continuation,
  - CuPy continuation,
  - no partner needed,
  - missing runtime feature.
- For RT-DBSCAN and triangle counting, either provide Numba paths or document the exact generic primitive that makes the Numba path unnecessary.
- Same-contract perf artifacts compare Numba and CuPy where both exist.
- Docs say users may still choose CuPy, C/CUDA extensions, or other partners, but RTDL's recommended reference should not require writing raw CUDA strings when Numba is viable.

Reason:

The user's hard requirement is that supported custom logic must not force users into CuPy RawKernel or hand-written C++/CUDA. Numba is the best current path for "Python user writes GPU logic" without raw kernel strings.

## Goal 5: Seconds-Scale Benchmark Matrix

Refresh the 10 benchmark apps with meaningful repeated or seconds-scale measurements.

Acceptance:

- Each benchmark row runs long enough to reduce launch-noise dominance, either by larger data or repeated steady-state loops.
- Tables include v2 current, prior accepted baseline, backend, partner, dataset, oracle, and claim boundary.
- For RayJoin, include both subcontracts and a single app-level summary.
- For apps using only RTDL primitives, make clear that the app developer does not write OptiX programs; they call RTDL primitives.
- Weak rows are labeled as design gaps.

Reason:

Tiny one-off timings created confusing ratios and user frustration. The matrix must represent serious app behavior, not noise.

## Goal 6: Partner Choice Product Surface

Make the user-facing model precise:

1. Try a built-in RTDL primitive first.
2. If custom continuation logic is needed, choose a partner.
3. RTDL provides high-performance reference paths for supported partners.
4. Users remain free to use Python, Numba, CuPy, C/CUDA extensions, or future partners.
5. Partner logic stays outside the native engine.

Acceptance:

- Public docs and benchmark docs use this model consistently.
- Partner capability matrix names Numba and CuPy roles honestly.
- No PyTorch dependency is implied unless a current path actually uses it.
- Docs explain that "OptiX route" means RTDL uses the OptiX backend internally, not that the app author writes OptiX shader code inside RTDL.

Reason:

The project is a language/runtime, not a fixed app library and not a magic auto-partner selector.

## Goal 7: AMD HIP RT Preparation

Prepare for AMD hardware-ray validation.

Acceptance:

- HIP RT support matrix lists implemented, proof-only, missing, and frozen surfaces.
- Map current OptiX generic primitives to expected HIP RT equivalents.
- Write an AMD cloud setup checklist before renting hardware.
- First AMD target is functional parity; performance comes after parity.

Reason:

Cross-vendor hardware RT is a core project goal, but AMD work should begin from a clean primitive map, not from app-shaped legacy surfaces.

## Goal 8: Future-Version Design Capture

Keep larger design ideas out of the current release/perf lane while preserving them for later.

Acceptance:

- Device-resident row streams, user-defined shader injection, Triton/Numba broader orchestration, and multi-partner residency are tracked in `docs/research/future_version_to_do_list.md`.
- Current goals distinguish "needed now for benchmark performance" from "future v3.x extensibility".
- No current docs imply that v2.x already delivers user-defined shader injection or true zero-copy unless a later report proves it.

Reason:

The project needs ambition without claim drift. Future ideas should not vanish, but they also should not blur current evidence.

## Consensus Rule

- Important implementation goals need Codex plus at least one external AI review.
- Public claims, roadmap changes, release gates, and major performance conclusions need Codex plus Claude plus Gemini.
- Codex plus Codex is never independent consensus.
- Failed external AI invocations must be recorded as failures, not counted as reviews.

## Immediate Next Goal

Start with Goal 1 and Goal 2 in parallel:

- Goal 1 gives the user/reviewer a clean RayJoin app-level answer.
- Goal 2 attacks the biggest generic performance gap still exposed by RayJoin-style workloads.

Do not close the current performance campaign merely because the latest LSI route improved. The project should close it only when the remaining weak rows are either improved by generic primitives or honestly documented as requiring a larger future runtime extension.
