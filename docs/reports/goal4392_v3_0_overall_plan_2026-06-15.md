# Goal4392 V3.0 Overall Plan

Date: 2026-06-15

Status: proposed overall plan for 3-AI review. This document does not authorize V3.0 implementation.

## Executive Decision

The answer to "did we finish the V3.0 overall plan?" is:

- Before this packet: no. We had a V3.0 preflight consensus and an M1 design-only unlock, but not a post-v2.14 overall plan.
- With this packet: yes, pending 3-AI acceptance. This is the V3.0 overall plan that should govern the work after v2.14.

The current project state is:

`v3_0_m1_design_allowed_implementation_blocked`

V3.0 is allowed to begin design work for M1 only. It is not allowed to begin native fused implementation, planner implementation, public API expansion, or public performance claims until the gates below are satisfied.

## Why V3.0 Exists

V2.X proved the core RTDL thesis:

- one app-agnostic ray-tracing language and primitive layer can target OptiX RT cores and Embree CPU backends;
- Python users can build serious benchmark applications without writing C++/CUDA for the whole application;
- explicit partners such as CuPy and Numba can own app continuation logic without being hidden as RTDL magic;
- fair comparisons require same contract, same data, phase accounting, and clear partner disclosure.

V2.X also exposed the real boundary:

- many remaining slow paths are not local kernel bugs;
- they are repeated materialization, missing device-resident continuations, missing fused graph execution, missing stream/lifetime accounting, and missing generic continuation primitives;
- solving those inside V2.X would push the project toward app-specific patches.

Therefore V3.0 must not be "more benchmark-specific tuning." V3.0 must be the generic execution-graph layer that lets benchmark applications express high-performance ray workloads while preserving RTDL's app-agnostic native design.

## Binding Preconditions From Goal4384

The Goal4384 3-AI preflight consensus remains binding:

1. v2.14 closeout is a hard precondition for V3.0 implementation.
2. M1 must produce a frozen execution-graph IR design document before M2 code starts.
3. V3.0 must forbid app-specific names in the public Python API surface, not only in native symbols.
4. The RTDBSCAN fused-continuation pilot must prove cross-app reuse by at least one non-DBSCAN workload.
5. Same-stream partner claims need hardware-observable evidence before public wording.
6. No V3.0 public performance claim is authorized until the release-grade benchmark harness is complete and externally reviewed.

Goal4387 changed only the first item: v2.14 closeout is now complete, so M1 design may begin. The remaining implementation and claim gates still stand.

## Architecture Thesis

V3.0 adds a generic execution layer around the existing RTDL rule:

> The native engine exposes app-agnostic primitives and execution contracts. Application semantics stay in Python or explicit partner continuation code.

V3.0 should introduce:

- **Execution graph IR**: a typed, app-agnostic graph of primitive calls, streams, continuations, reductions, residency annotations, stream annotations, and phase markers.
- **Prepared graph plans**: reusable lowered plans for OptiX, Embree, and partner continuations.
- **Device-resident stream values**: candidate ids, hit ids, face ids, flags, counts, summaries, frontier rows, and compacted rows are first-class graph values with explicit lifetime.
- **Generic fused continuations**: compact positives, grouped count/sum/min/max, first or nearest summaries, threshold summaries, component union, frontier expansion, and vector accumulation.
- **Partner continuation protocol**: CuPy, Numba, Torch, Triton, or future partners are explicit plan nodes with named streams, residency, timing, and fallback policy.
- **Profiler-grade phase accounting**: build, upload, traversal, continuation, reduction, download, and host wrapper phases are separately measured.
- **Backend-neutral contract**: OptiX RT cores and Embree CPU must execute the same logical workload contract when compared.

## Public API Boundary

Allowed public concepts:

- `GraphValue`
- `PrimitiveNode`
- `ContinuationNode`
- `PartnerNode`
- `PreparedGraph`
- `Residency`
- `StreamBinding`
- `PhaseMarker`
- `BackendPlan`
- `ExecutionReport`

Forbidden public concepts:

- app-specific public Python API names;
- app-specific native ABI names;
- No native RayJoin engine;
- No native DBSCAN engine;
- No native Barnes-Hut force-law engine;
- No native contact-manifold physics engine;
- raw arbitrary OptiX callback functions as the stable RTDL user API;
- hidden partner selection presented as RTDL-only performance;
- true-zero-copy claims without pointer, lifetime, stream, and hardware timing evidence.

OptiX programmable behavior can influence backend lowering internally, but the stable user contract must remain RTDL graph primitives plus explicit partner continuations. Users should not need to write OptiX C++ callback code to use V3.0.

## Partner Policy

For any benchmark application that needs partner continuation:

- test the best practical partner implementation, for example CuPy when it is the strongest choice;
- also test a Numba reference, because it is the no-C++/CUDA user path;
- if the Numba reference is omitted, the pilot document must explain why no Numba continuation path exists for that workload;
- disclose every partner in performance tables;
- separate RT traversal time from partner continuation time;
- do not call partner work "RTDL-only" unless the table makes the partner explicit;
- do not claim same-stream continuation unless CUDA events or Nsight-level evidence prove it;
- do not claim device-resident or zero-copy behavior unless pointer identity, residency, lifetime, and transfer evidence prove it.

The principle is: RTDL must remove unnecessary data movement and materialization that RTDL controls. It does not promise miracles over specialized hand-written C++/CUDA/OptiX for every application.

## Milestone Plan

| Milestone | Name | Purpose | Exit condition |
| --- | --- | --- | --- |
| M0 | Overall plan consensus | Freeze the V3.0 direction before any implementation | Codex, Claude, and Gemini accept this plan or accept with notes, and the consensus is recorded in a dated document; request-changes blocks start |
| M1 | Execution graph IR design | Define graph values, nodes, residency, streams, lifetimes, phase accounting, partner nodes, and non-goals | Frozen design doc, static tests, no app-specific public API names, no native implementation, and external Claude/Gemini review passed |
| M2 | Planner skeleton and validators | Implement the minimum graph validator and plan object without app-specific lowering | Tests validate IR schema, phase markers, residency rules, stream rules, and error messages |
| M3 | Residency and phase instrumentation | Make timing and movement evidence first-class before performance claims | CUDA events or Nsight evidence for GPU paths, Embree phase accounting for CPU paths, transfer/build/traversal/continuation phases separated |
| M4 | Generic fused continuation pilot | Prove one generic fused continuation path on RTDBSCAN and one non-DBSCAN workload | Same primitive reused without DBSCAN-specific names or semantics; OptiX, Embree, best partner, and Numba reference policy satisfied; same-contract measurements taken on hardware with OptiX-capable GPU and M3-grade phase accounting |
| M5 | RayJoin point-location/topology pilot | Express PIP and overlay through generic face-id, point-location, compact, and topology streams | Author code, RTDL OptiX, and RTDL Embree compared under same CDB point-location/topology contract and separated timing bases; same-contract measurements taken on hardware with OptiX-capable GPU and M3-grade phase accounting |
| M6 | Aggregate-tree/frontier pilot | Express Barnes-Hut-style and related workloads as generic frontier, node summary, and vector accumulation graphs | Traversal and continuation measured separately and together on hardware with OptiX-capable GPU and M3-grade phase accounting; no Barnes-Hut native engine or force-law ABI |
| M7 | Release-grade benchmark harness | Turn pilots into public-quality evidence | Exact datasets, scripts, repeated runs, author-code timing basis, backend/partner disclosure, phase tables, and fresh external review |

Implementation may not proceed past M1 until M1 is frozen and reviewed. Public V3.0 performance claims may not proceed until M7.

Note: Goal4384 used M5 as the release-grade public-claim gate. This plan expands the milestone sequence by adding explicit planner and instrumentation milestones, so the equivalent release-grade public-claim gate is M7.

## Benchmark-App Targets

| App/workload | V3.0 reason | Required generic capability | Public claim condition |
| --- | --- | --- | --- |
| RTDBSCAN | Current performance is dominated by continuation and convergence, not just RT traversal | fixed-radius stream, core-flag summary, component union, convergence reporting | Must prove one fused continuation primitive is reused by at least one non-DBSCAN workload |
| RayJoin LSI/PIP/overlay | Current RTDL can use RT cores but loses work to packing, materialization, and topology continuation | segment/primitive intersections, face-id point location, compact topology streams, grouped output assembly | Must compare author RT, RTDL RT, and RTDL Embree under the same paper contract and dataset timing basis |
| Barnes-Hut | Current path needs generic aggregate traversal and vector accumulation | frontier traversal, node summary, reduction, vector sum | Must not become a native Barnes-Hut force-law engine |
| Contact and robot collision | Current paths need broadphase, refinement, flags, and compact output without repeated host round trips | AABB candidates, witness/refinement streams, compact flags, grouped reductions | Must separate RT traversal from app-owned collision logic |
| RayDB and graph/ranked-summary workloads | Current paths need in-device summaries instead of host-side ranked aggregation | grouped reduction, top-k, ranked summary, compact rows | Must disclose partner and phase split |
| Triangle and distance-like apps | Current paths are useful for validating primitive contracts and backend parity | primitive contract tests, threshold flags, summary rows | Must remain evidence rows, not over-generalized claims |

## Fairness Rules

Every V3.0 performance table must say:

- hardware;
- backend;
- partner, if any;
- dataset;
- scale;
- whether data starts on host or device;
- whether build/upload/download are included;
- number of warmups and repeats;
- timing statistic;
- phase split;
- correctness contract;
- author-code timing basis when comparing to a paper system.

The comparison is only valid when the workload contract is the same. If the author code assumes device-resident data and RTDL includes host load/pack/upload, then the table must either separate those phases or run both sides under both timing bases.

## Claims That Are Not Allowed Yet

V3.0 may not claim:

- RTDL beats C++/CUDA/OptiX in general;
- RT cores always beat Embree CPU;
- RT cores always beat CUDA-core partners;
- V3.0 is zero-copy;
- V3.0 has automatic optimal partner selection;
- V3.0 reproduces a paper unless exact datasets, author code, and timing basis are matched;
- V3.0 public speedup rows before M7 external review.

## Design Questions For M1

M1 must answer these before implementation starts:

1. What is the exact execution graph schema?
2. What graph values can be device-resident, host-resident, or dual-resident?
3. How are streams represented and verified?
4. How are lifetimes represented and checked?
5. What phase markers are mandatory?
6. How do partner nodes receive and return values without hidden materialization?
7. How does OptiX lowering remain app-agnostic while still exposing face-id and hit metadata?
8. How does Embree lowering preserve the same logical contract?
9. What names are forbidden in public API and native symbols?
10. What evidence proves same-stream, device-resident, or zero-copy behavior?

## Immediate Next Actions After Consensus

If this Goal4392 plan receives 3-AI acceptance:

1. open M1 only;
2. write the execution-graph IR design document;
3. add tests that block app-specific public API names and app-specific native symbols;
4. define graph value, residency, stream, lifetime, phase, and partner-node contracts;
5. prepare a new Claude/Gemini review packet for the M1 IR design;
6. keep implementation blocked until that M1 review passes.

If any reviewer requests changes, V3.0 remains blocked until the plan is repaired and reviewed again.

## Review Questions

1. Is this specific enough to start M1 design work?
2. Does it preserve the RTDL app-agnostic native engine rule?
3. Does it keep V3.0 implementation properly blocked until M1 is frozen?
4. Does it prevent benchmark-specific rewrites from pretending to be RTDL architecture?
5. Is the partner policy strong enough for fair public comparison?
6. Are the milestones ordered correctly?
7. Is M7 the correct gate for public performance claims?

## Final Gate

V3.0 may proceed only to M1 design after this packet has a recorded 3-AI consensus.

The intended consensus state is:

`v3_0_overall_plan_accepted_m1_design_only_implementation_blocked`
