# Goal614: v0.9.3 Apple RT Remaining Workload Decision

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Question

After Goals 608-612, Apple RT supports 13 native or native-assisted workload rows. Five rows remain compatibility-only:

- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

The question is whether v0.9.3 should continue implementation until these five rows are Apple MPS RT hardware-backed, or whether they should be explicitly deferred with a documented reason.

## Decision

Defer these five rows from v0.9.3 native Apple RT implementation.

Keep them callable through `run_apple_rt` compatibility dispatch, but do not mark them native or hardware-backed in v0.9.3.

## Reason

The completed v0.9.3 expansion works because the workloads are geometric or nearest-neighbor workloads that can be directly decomposed into Apple MPS-supported ray/triangle or point/box candidate discovery:

- rays and triangles;
- segment slabs;
- polygon bounding boxes;
- point-neighborhood boxes;
- polygon edge and vertex decompositions.

The remaining five rows are graph and database workloads. Apple MPS RT does not natively accept graph adjacency lists, table rows, predicates, group keys, or aggregation state. Any honest Apple RT implementation must first define a lowering contract that maps these non-geometric structures into geometric proxy primitives without changing semantics.

Implementing these rows now by routing to CPU compatibility code would violate the user's requirement that native-only work actually use Apple RT/MPS hardware. Implementing them quickly without a contract risks a misleading backend surface and brittle correctness.

## Row-by-Row Decision

| Predicate | v0.9.3 decision | Reason | Future requirement |
| --- | --- | --- | --- |
| `bfs_discover` | Defer native Apple RT | Needs graph frontier/CSR adjacency lowering to candidate rays/primitives. Current Apple MPS path has no graph adjacency primitive. | Define vertex/edge encoding, visited filtering boundary, dedupe behavior, and candidate cardinality ceilings. |
| `triangle_match` | Defer native Apple RT | Needs graph wedge/neighbor-intersection lowering. Current geometry decompositions do not represent sorted adjacency intersection. | Define edge-seed geometry encoding, neighbor candidate discovery, uniqueness/order contract, and exact triangle refinement. |
| `conjunctive_scan` | Defer native Apple RT | Needs table row/predicate encoding. Existing DB-to-RT ideas from v0.7 are not yet ported to Apple MPS primitives. | Define row boxes or interval primitives, supported predicate types, candidate ceilings, and exact predicate refinement. |
| `grouped_count` | Defer native Apple RT | Depends on DB scan candidate discovery plus group-key materialization and aggregation. | Define candidate discovery first, then exact CPU or native aggregation boundary. |
| `grouped_sum` | Defer native Apple RT | Same as grouped count, plus exact value accumulation and numeric overflow/typing boundaries. | Define candidate discovery, grouping contract, value type support, and exact accumulation rules. |

## What v0.9.3 Can Honestly Claim

v0.9.3 can claim:

- Apple Metal/MPS RT backend exists.
- Apple RT supports native or native-assisted candidate/flag discovery for the geometry and nearest-neighbor rows listed in the support matrix.
- Apple RT remains compatibility-callable for graph and DB rows, but those rows are not Apple hardware-backed yet.
- Performance evidence shows correctness-broad coverage, but not broad Apple speedups versus Embree.

v0.9.3 must not claim:

- Full Apple RT native coverage for graph workloads.
- Full Apple RT native coverage for DB workloads.
- Apple RT performance leadership over Embree.
- GPU-resident aggregation for DB or polygon workloads where CPU refinement/materialization remains documented.

## Proposed Next Goals

### Goal615: Apple RT Graph Lowering Contract

Write a design note for `bfs_discover` and `triangle_match` that specifies:

- graph input shape limits;
- ray/proxy primitive encoding;
- candidate discovery semantics;
- CPU refinement boundary;
- correctness tests required before native marking;
- performance tests required before public performance wording.

### Goal616: Apple RT DB Lowering Contract

Write a design note for `conjunctive_scan`, `grouped_count`, and `grouped_sum` that specifies:

- supported scalar types;
- predicate encoding;
- row/proxy primitive encoding;
- group-key and aggregation semantics;
- PostgreSQL/oracle parity tests;
- Apple-vs-Embree/CPU/PostgreSQL performance comparison boundaries.

### Goal617: v0.9.3 Release Gate

If Goal614 is accepted, proceed to release-gate work for the geometry/NN Apple RT expansion:

- full tests;
- docs/front-page/tutorial updates;
- support matrix audit;
- performance wording audit;
- external AI review.

## Recommendation

Accept Goal614 and stop v0.9.3 native implementation at 13 native/native-assisted rows. Treat graph and DB Apple RT native support as future design-driven work, not a last-minute release blocker.

This keeps the release honest while preserving a clear path for later graph/DB Apple RT work.

## External Review

Gemini 2.5 Flash reviewed this decision report and returned ACCEPT in the terminal session. The direct file write failed because Gemini was in Plan Mode, so Codex recorded the review transcript in:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal614_gemini_decision_review_2026-04-19.md`

Goal614 is closed under the 2-AI rule.
