# V3.0 Design Intent Reconstruction And Performance Mandate

Date: 2026-06-20

Status: V3-only control report. This document is not a release promotion and
does not authorize public performance wording by itself.

## User Mandate On 2026-06-20

The current controlling mandate is:

```text
V3 must be the highest-performance independent-language release line.
V3 must not be diluted by external embedding, SDK, or cross-language-host
scope.
```

This supersedes any accidental reading of the later V3.0.2 closeout as "V3 is
only tutorial/doc cleanup" or "V3 is only current-route bookkeeping." Historical
release documents still matter as evidence, but they are not an excuse to lower
the current V3 goal.

## Goal-Level Decision Audit

1. Was the previous reasoning dumb?

Yes, partly.

2. What made it dumb?

The mistake was treating the later conservative V3.0.2 release boundary as the
user's desired end-state, rather than as a historical shrinkage/cleanup state.
It also repeatedly mixed external-host scope into a V3-only performance
question.

3. Was another path available?

Yes. The correct path was to separate three things: original V3 performance
intent, later conservative source-tree closeout, and the user's renewed V3-only
performance mandate.

4. Can we switch paths and solve the real problem?

Yes. This report switches to a V3-only performance-release path: define the
target, classify the evidence, identify gaps, and then run/repair the V3
benchmark suite until V3 can honestly stand as the strongest independent RTDL
language/performance version.

## Document Inventory

### Early V3 Concept Documents

These documents show the first V3 ambition was larger than cleanup:

| Document | Role |
| --- | --- |
| `docs/reports/v3_0_custom_engine_extensions_concept.md` | Proposed custom engine extensions, dynamic shader injection, payload slots, cross-backend extension ideas. |
| `docs/reviews/v3_0_custom_engine_extensions_concept_claude_analysis_2026-05-11.md` | Critical review: plausible but aspirational; warns against overclaiming shader injection and Python JIT. |
| `docs/reports/v3_0_frechet_lab_lessons_after_v1_8_2026-05-12.md` | Extracts lessons: extension means typed device payload, backend shader entry contract, compact output, conformance, cost model. |
| `docs/reviews/v3_0_frechet_lab_lessons_consensus_2026-05-12.md` | Accepts Frechet lessons for planning only; does not authorize V3 delivery claims. |
| `docs/reviews/v3_0_custom_engine_extensions_critical_review_and_roadmap_after_v2_5_2026-05-29.md` | Reframes V3: shader injection is risky; partner continuation may solve most use cases; V3 must justify only logic that truly belongs inside traversal. |

### Reframed V3 Architecture Documents

These documents turn V3 into an execution-graph, residency, and continuation
architecture effort:

| Document | Role |
| --- | --- |
| `docs/reports/claude_v2_5_closeout_and_v3_0_residency_first_roadmap_2026-05-31.md` | Retires broad shader-injection first plan; moves V3 to device-residency/CUDA-graph/prepared pipeline first. |
| `docs/reports/goal4377_pre_v3_v2_13_v2_14_strategy_2026-06-14.md` | Defines V3 as primitive planner/execution-graph system, device-resident streams, fused generic continuations, backend-specific lowering, phase accounting. |
| `docs/reports/goal4384_v3_0_preflight_3ai_consensus_2026-06-14.md` | Allows only design/preflight; blocks implementation and public performance until v2.14 closeout and evidence gates. |
| `docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md` | Governing plan: app-agnostic execution graph, prepared graph plans, device-resident stream values, generic fused continuations, explicit partner policy, release-grade harness. |
| `docs/reports/goal4392_3ai_consensus_v3_0_overall_plan_2026-06-15.md` | Accepts M1 design only; implementation and public claims remain blocked. |
| `docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md` | Freezes the M1 app-agnostic execution graph IR and claim-boundary schema. |
| `docs/reports/goal4393_3ai_consensus_v3_0_m1_execution_graph_ir_2026-06-15.md` | Allows M2 skeleton only; no native execution or performance claims. |

### Midstream V3 Evidence Documents

These documents show V3 implementation and evidence work moved beyond design:

| Document | Role |
| --- | --- |
| `docs/reports/goal4414_v3_0_midterm_review_packet_2026-06-15.md` | Records M1-M17: graph IR, planner skeleton, same-contract lowering, partner rows, same-stream evidence, no-hidden-copy windows, prepared hit streams. |
| `docs/reports/goal4414_v3_0_midterm_3ai_consensus_2026-06-15.md` | Accepts midterm with boundary; continues to M18; still blocks public claims. |
| `docs/reports/goal4415_v3_0_m18_device_side_grouped_contract_2026-06-15.md` through `docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md` | Long implementation/evidence chain for grouped streams, device continuation, benchmark app route repair, prepared graph chunks, triangle, RT-DBSCAN, RTNN, Barnes-Hut, RayJoin, and related routes. |

### Performance Evidence Documents

These are the strongest documents for the "V3 as performance release" direction:

| Document | Evidence meaning |
| --- | --- |
| `docs/reports/goal2636_current_benchmark_performance_report_2026-05-27.md` | Internal standard matrix: 10 promoted apps, 11 rows, all OptiX rows faster than Embree on recorded exact subpaths; geomean 32.25x. |
| `docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md` | Strengthened matrix: 13 additional strengthened rows and 16 stress rows; all recorded OptiX ratio rows win. |
| `docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md` | Compact internal RT-vs-Embree summary for benchmark apps; explicitly not public wording. |
| `docs/history/release_reports/v2_14/public_rt_vs_embree_comparison.md` | Released v2.14 row-scoped public performance baseline. This currently remains the stronger released public performance packet. |
| `docs/reports/v2_14_vs_v3_0_2_pod_comparison_2026-06-20.md` | Fresh pod comparison: V3.0.2 passes source-tree/user-surface/ten-route health, but does not beat V2.14 as public performance evidence. |

### Conservative V3 Closeout Documents

These documents narrowed V3 into current-route/source-tree completion:

| Document | Role |
| --- | --- |
| `docs/reports/goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_2026-06-17.md` | All ten apps have V3 clean-target entries; whole-app/universal speedup remains blocked. |
| `docs/reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.md` | Queue becomes empty; no immediate runtime build targets remain. |
| `docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.md` | Completion-readiness audit: all queues empty; public claims still blocked. |
| `docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md` | Packages V3 current benchmark-app implementation state; not public performance. |
| `docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md` | Accepts narrow "current benchmark-app implementation queue complete" claim. |
| `docs/reports/goal4543_v3_0_m144_major_performance_target_refresh_2026-06-17.md` | Says no immediate pod-needed targets remain, but also blocks public performance and broad RT-core claims. |
| `docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md` | Final current-scope gate: ten current routes closed, `v3_current` canonical, no public performance. |
| `docs/release_reports/v3_0_2/*` | V3.0.2 source-tree patch release packet, support matrix, wording boundaries, final closeout. |

## What V3 Was Originally Trying To Do

V3 was not originally just documentation polish. The serious technical intent
was:

1. Turn RTDL from a primitive/app collection into a language/runtime execution
   layer.
2. Keep the native engine app-agnostic while letting users express many
   non-graphics RT-shaped applications.
3. Introduce execution graph / prepared graph structure so repeated app work
   avoids repeated Python and host-materialization overhead.
4. Make compact output, stream values, grouped reductions, ranked summaries,
   bounded witnesses, and partner continuations first-class.
5. Use OptiX/Embree/CUDA/partner routes under one explicit semantic contract.
6. Produce serious, row-scoped performance evidence across the promoted
   benchmark portfolio.

The core V3 performance idea was:

```text
RTDL owns the independent language/kernel contract and the app-agnostic
execution loop; Python authors the app; partners are explicit; performance
comes from prepared RTDL primitives, compact outputs, device/partner-side
continuations, and avoiding Python row materialization on hot paths.
```

## What V3 Was Later Shrunk Into

By Goal4536, Goal4614, and v3.0.2, the release definition had shifted:

```text
V3.0.2 = source-tree Python+partner+RTDL surface + ten current benchmark routes
closed + app-author policy + docs/gates cleaned.
```

That is a real engineering state, but it is not enough for the current user
mandate of "highest-performance independent-language release."

The shrinkage produced a product-positioning mismatch:

- Some docs and reports show strong performance evidence.
- The final v3.0.2 release packet blocks public performance claims.
- The fresh V2.14 vs V3.0.2 pod packet says V2.14 remains the stronger released
  public performance baseline.

This mismatch must be fixed by evidence and implementation, not by wording.

## What V3 Must Mean Now

Under the current mandate, V3 should mean:

```text
V3 is RTDL's independent-language performance release:
the RTDL line where RTDL owns the kernel contract, execution/planning route,
backend dispatch, compact output policy, benchmark app route, and row-scoped
performance evidence.
```

V3 can be Python-hosted and still be the independent-language release because
Python is the control plane while RTDL owns the kernel language and execution
contract.

## Current Evidence Status

### Supported

- The V3 codebase has a large benchmark-app route surface.
- Ten benchmark apps have current route closure documents.
- `v3_current` passed on the current source-tree surface in the 2026-06-20 pod
  packet.
- The 2026-06-20 pod packet ran all ten current V3 scale rows successfully.
- Historical/internal V3-family performance reports show strong OptiX-vs-Embree
  evidence across promoted apps and strengthened rows.

### Not Yet Supported

- V3 is not yet proven as the strongest released public performance baseline
  over V2.14.
- V3.0.2 lacks a current same-contract performance matrix equivalent to or
  better than the v2.14 public matrix.
- Several current V3 scale rows are route-health rows, not claim-grade
  correctness/performance rows.
- The current docs conflict: application/performance docs preserve strong
  speedup tables, while release docs block public speedup.
- "No immediate pod targets" in Goal4543 was correct only for the narrowed
  current-route completion goal, not for the reopened performance-release goal.

## P0 Gaps Blocking V3 As Highest-Performance Independent-Language Release

1. No current V3 release-grade same-contract OptiX-vs-Embree matrix.

V2.14 has the stronger released row-scoped public matrix. V3 needs an equal or
better matrix on current V3 code, current routes, current hardware, and current
validation rules.

2. Route-health and performance evidence are mixed.

The ten-app scale runner proves "the routes run." It does not by itself prove
same-contract speedups, whole-app speedups, or superiority over V2.x.

3. V3 docs describe two different products.

The performance catalog/report lineage says V3 has strong internal speedups.
The v3.0.2 release packet says V3 is proud but conservative and not a public
performance release. A user cannot tell which V3 they are learning.

4. Some benchmark rows still have validation caveats.

The 2026-06-20 V3 scale packet includes rows with skipped reference validation
or no full correctness proof. Those are unacceptable as final performance
release rows.

5. Barnes-Hut and Triangle remain warning rows.

Historical reports show both were once sensitive to measurement shape. Later
reports claim fixes. Current V3 performance release needs fresh, current,
same-contract confirmation.

## V3-Only Action Plan

### Phase A: Reopen V3 Performance Gate

- Create a V3-only performance gate.
- Define it as `v3_performance_release_candidate`.
- It must run only V3 independent-language surfaces: primitives, prepared
  execution, execution graph where present, partner-explicit continuations, and
  benchmark apps.
- It must exclude external-host, packaging, and SDK claims from the V3
  performance proof.

### Phase B: Build Current V3 Same-Contract Matrix

For every promoted app row:

- name the exact contract;
- name backend/partner;
- run OptiX and Embree or the correct CPU baseline;
- separate prepare/build/upload/query/continuation/download/validation;
- validate correctness at the performance scale;
- store raw stdout/stderr/JSON and machine-readable summary;
- mark whether it is public-ready, internal-only, or blocked.

The matrix must cover at least:

- Hausdorff / X-HD threshold and any exact-witness route that V3 wants to claim;
- Spatial RayJoin PIP/LSI/overlay-seed, without pretending full RayJoin paper
  reproduction;
- RT-DBSCAN core/count/component signature with explicit partner policy;
- Robot collision prepared flags;
- Contact manifold AABB/bounded witness;
- RayDB grouped count/sum;
- Barnes-Hut node coverage and any V3-approved force-related route;
- LibRTS AABB spatial-index query;
- RTNN ranked summary;
- Triangle counting RT-Graph-shaped summaries.

### Phase C: Promote Or Fix Rows

Each row gets exactly one of:

- `release_ready`: same-contract, correctness-validated, current-code, pod-run,
  phase-split, repeated, artifact-backed;
- `internal_only`: technically useful but not release wording;
- `fix_required`: implementation or benchmark harness work needed;
- `drop_or_demote`: not part of V3 performance release.

Rows that fail must trigger code/harness repair, not wording tricks.

### Phase D: Rewrite V3 Docs After Evidence

Only after Phase B/C:

- update `docs/application_catalog.md`;
- update `docs/performance_model.md`;
- update `docs/backend_maturity.md`;
- update `docs/release_reports/v3_0_2/` or create a new V3 performance release
  packet;
- remove ambiguity between "route closure" and "performance release";
- keep the story focused on V3 performance.

## Immediate Conclusion

V3 did have a serious performance-language ambition. The later v3.0.2 release
state is not sufficient for the user's current mandate.

The correct next move is not to delete V3 immediately and not to explain it
away. The correct next move is to reopen V3 as a V3-only performance release
candidate, run a current same-contract performance matrix on the pod, repair
failed rows, and only then publish polished V3 docs.

Until that happens, the honest status is:

```text
V3 has the architecture and route surface for a serious independent-language
performance release, but current evidence only proves route health and internal
performance history. V3 is not yet proven as the highest-performance released
line over V2.14.
```
