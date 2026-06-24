# Phoenix V3 Goal4392 Alignment Audit

Status: active alignment audit, 2026-06-20.

This audit compares the Phoenix V3 rebuild line with the formal V3 plan:

```text
docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md
docs/reports/goal4392_3ai_consensus_v3_0_overall_plan_2026-06-15.md
docs/reviews/goal4392_claude_review_v3_0_overall_plan_2026-06-15.md
docs/reviews/goal4392_gemini_review_v3_0_overall_plan_2026-06-15.md
```

## Goal4392 Control Point

Goal4392 says V3 exists because V2.x exposed repeated materialization, missing
device-resident continuations, missing fused graph execution, missing
stream/lifetime accounting, and missing generic continuation primitives.

It also says V3 must not be just more benchmark-specific tuning. The V3 answer
must be a generic execution-graph layer with:

- execution graph IR;
- prepared graph plans;
- device-resident stream values;
- generic fused continuations;
- explicit partner continuation protocol;
- profiler-grade phase accounting;
- backend-neutral OptiX/Embree contract.

The accepted Goal4392 consensus authorized M1 design only at that time. Later
M1-M149 work exists, but Phoenix must still judge that work against the same
binding conditions before promoting it as V3.

## Alignment Verdict

Current Phoenix direction is partly aligned, but needs a correction.

Aligned:

- Phoenix keeps M150-M214 out of V3.
- Phoenix treats broad V3-over-V2 speedup as unauthorized.
- Phoenix uses exact artifacts and keeps release authorization false.
- Phoenix identifies the right technical source material in M0-M149.

Needs correction:

- The Phoenix candidate matrix was too route-first. It risked turning V3 into a
  queue of benchmark repairs instead of a generic execution-graph language
  release.
- The next queue must start with Goal4392 compliance mapping, not with isolated
  row tuning.
- Each P0 route must map to at least one generic V3 capability and must carry
  partner policy, phase accounting, and same-contract evidence requirements.

## Required Phoenix Reframe

Phoenix V3 should now be framed as:

```text
Rebuild V3 as the Goal4392 execution-graph / prepared-continuation language
release, then use serious benchmark apps as M4-M7 evidence that the generic
layer solves real V2.x performance and usability problems.
```

The benchmark rows remain essential, but they are evidence for generic
capabilities. They are not the architecture by themselves.

## Goal4392-To-Phoenix Mapping

| Goal4392 item | Phoenix interpretation | Current status | Required action |
| --- | --- | --- | --- |
| M1 execution graph IR | The user-facing V3 language contract must be graph values, nodes, residency, streams, lifetimes, phase markers, partner nodes, and backend plans. | Historical M1 work exists, but Phoenix docs need a current compliance index. | Build a current M1-M7 compliance table before promoting any row. |
| M2 planner skeleton and validators | Existing route machinery must be classified as generic planner/validator behavior or left internal. | Some skeleton and prepared graph work exists in M1-M149. | Identify what is production-grade, what is route-specific, and what is internal-only. |
| M3 residency and phase instrumentation | Performance claims require phase accounting before route rows can become public evidence. | Current reports have timing ratios, but not all rows have complete phase/lifetime evidence. | Add phase/accounting requirements to every P0 route rerun. |
| M4 generic fused continuation pilot | RTDBSCAN cannot be DBSCAN-only; one fused primitive must be reused by a non-DBSCAN workload. | Phoenix names RTDBSCAN and grouped reductions, but reuse proof is not yet the first-class gate. | Promote grouped count/sum, compact positives, component union, or ranked summaries only with cross-app reuse evidence. |
| M5 RayJoin point-location/topology pilot | RayJoin must express PIP/overlay through generic face-id, point-location, compact, and topology streams. | Strong hot-route rows exist, but paper-contract and topology-materialization boundaries remain. | Keep RayJoin P0 only as a generic topology-stream pilot, not as a native RayJoin engine. |
| M6 aggregate-tree/frontier pilot | Barnes-Hut must stay generic frontier/node-summary/vector-accumulation work. | Barnes-Hut has useful rows and a V3-vs-V2 regression. | Treat Barnes-Hut as the aggregate-frontier pilot; tune only in generic frontier/vector terms. |
| M7 release-grade benchmark harness | Public claims require exact datasets, scripts, repeated runs, author timing basis, backend/partner disclosure, phase tables, and fresh external review. | Current all-app and paired evidence are serious, but release authorization remains false. | Keep M7 incomplete until the harness and external review are finished. |

## Route Priority Adjustments

P0 routes remain useful, but their reason changes:

- RTDBSCAN is P0 only as the fused-continuation and cross-app reuse pilot.
- RayDB-style reductions are P0 because grouped count/sum can be a reusable
  generic continuation primitive.
- Triangle is P0 as prepared graph / summary-row evidence, not as graph database
  performance wording.
- RTNN is P0 as ranked-summary and prepared-chunk evidence.
- RayJoin is P0 as point-location/topology-stream evidence.
- Barnes-Hut is P0 as aggregate-frontier/vector-accumulation evidence, and its
  regression blocks public performance wording until tuned or explained.

## Partner And Evidence Rules

Every Phoenix P0 row must say:

- named generic V3 capability instantiated by the row;
- best practical partner, if used;
- Numba reference, or written reason for omission;
- OptiX and Embree same-contract basis;
- whether data starts on host or device;
- build/upload/traversal/continuation/reduction/download phase split;
- repeat count and statistic;
- correctness contract;
- claim boundary.

No same-stream, device-resident, no-hidden-copy, or zero-copy-adjacent wording
can appear without hardware-observable evidence.

Rows that do not instantiate a named generic V3 capability must be removed from
Phoenix release evidence rather than retained as supplementary performance
evidence.

The current paired benchmark geomean, 1.012x V3 speedup versus V2.14, is a
release-blocking fact for broad V3-over-V2 performance wording. Until a later
same-hardware paired artifact materially changes that result, Phoenix may
describe stronger runability and route health, but it must not describe broad
V3 timing superiority.

M150-M214 exclusions are enforced by the V3 release wording gate. Active V3
docs may mention C ABI, embedding, SDK, external runtime, DLPack-like bridge, or
zero-copy-adjacent terms only as explicit exclusions, non-claims, history, or
blocked/out-of-scope material.

## Goal-Level Decision Audit

Decision: amend Phoenix so Goal4392's generic execution-graph architecture
governs the performance rebuild.

1. Was I foolish?

   Partly. The first Phoenix matrix had correct boundaries but still leaned too
   hard toward route-by-route benchmark repair as the next action.

2. What actions made the decision foolish?

   I let current benchmark evidence drive the work queue before explicitly
   rechecking it against the formal Goal4392 architecture gate.

3. Was there another path?

   Yes. Read Goal4392 first, map Phoenix routes to generic graph capabilities,
   and only then choose benchmark reruns.

4. Can I now try a different path that actually solves the problem?

   Yes. Phoenix now uses Goal4392 as the control plane: generic V3 capability
   first, benchmark-app evidence second, public claims last.

## Conclusion

Phoenix can still produce the high-performance V3 the user wants, but only if
it stops acting like a benchmark patch queue. The correct path is to revive the
M0-M149 work as a Goal4392-compliant execution-graph language release and make
the benchmark apps prove that release.
