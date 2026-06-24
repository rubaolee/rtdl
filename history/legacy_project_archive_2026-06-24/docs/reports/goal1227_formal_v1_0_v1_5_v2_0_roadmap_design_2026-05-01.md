# Goal1227 Formal RTDL Roadmap Design: v1.0, v1.5, v2.0

Date: 2026-05-01

Author: Codex

Status: draft for Gemini review

## Executive Summary

RTDL's roadmap should be app-first, then primitive-first, then
ecosystem-first.

v1.0 should stabilize the application foundation and preserve the bounded
evidence produced by the v0.9.8 NVIDIA RT and Embree work. v1.5 should reduce
engine technical debt by migrating selected app-specific native paths to
generic traversal-plus-reduction primitives. v2.0 should make RTDL a clean
participant in external GPU compute ecosystems through explicit zero-copy
handoff, not by becoming a general-purpose Python compiler.

The roadmap must keep one rule constant across all versions: public performance
claims are phase-specific and evidence-specific. Backend availability, native
RT traversal, RT-core use, and same-contract speedup evidence are separate
facts.

## Design Principles

1. Applications justify RTDL. Generic architecture is valuable only if it
   preserves useful app behavior.
2. RTDL should accelerate traversal-heavy kernels, not pretend to accelerate
   whole applications when Python, ranking, refinement, DBMS work, graph
   analytics, or postprocessing dominate.
3. v1.0 may keep technical debt when it is necessary to prove correctness and
   performance.
4. v1.5 should remove technical debt only behind reviewed contracts and parity
   gates.
5. v2.0 should integrate with compute partners explicitly rather than hiding
   unsupported work behind a magic compiler.
6. Public docs must be more conservative than engineering docs.

## Current Starting Point

After the v0.9.8 work, RTDL has a stable current baseline:

- Embree is the CPU RT backend, fallback path, and same-contract comparison
  baseline for many app sub-paths.
- NVIDIA OptiX/RTX evidence exists for multiple bounded sub-paths.
- Some sub-paths have reviewed public speedup wording.
- Some sub-paths are deliberately blocked because valid evidence shows OptiX
  slower than Embree or below the public threshold.
- The project has a public wording matrix that separates reviewed, blocked, and
  non-NVIDIA rows.

This baseline is strong enough to continue toward v1.0, but it is not a claim
that every app, graph operation, polygon operation, DB operation, or whole
workflow is RT-core accelerated.

## v1.0: App Credibility Release

### Purpose

v1.0 should make RTDL credible to users by presenting stable, useful,
well-documented applications with honest acceleration boundaries.

v1.0 is not the architectural-cleanup release. It is the release where RTDL
proves that selected app-critical kernels can be expressed through RTDL and
executed through RT-capable backends with reproducible correctness and timing
evidence.

### Required Product Properties

v1.0 should provide:

- a stable public app catalog;
- clear install and run instructions;
- a support matrix for Embree, OptiX/RTX, Apple RT, HIPRT, and future Vulkan;
- app-level docs explaining what each app does;
- per-app boundaries explaining which phase is RT-accelerated;
- examples that still work when optional GPU backends are unavailable;
- tests that protect public wording and release-facing docs;
- release reports that preserve evidence and review trails.

### Accepted Technical Debt

v1.0 may keep app-specific native endpoints where needed:

- robot pose collision screening;
- database compact summaries;
- segment/polygon hit-count and bounded row paths;
- road-hazard compact summaries;
- Hausdorff threshold decisions;
- graph visibility/candidate generation;
- ANN/KNN candidate gates;
- Barnes-Hut node-coverage decision paths.

This debt is acceptable because v1.0's job is to prove useful app targets and
performance ceilings. Removing these endpoints too early would risk breaking
the apps that justify RTDL.

### Public Claim Boundary

v1.0 public claims must stay bounded:

- `robot_collision_screening` wording is normalized/prepared pose-flag wording,
  not whole robot planning.
- `barnes_hut_force_app` wording is node-coverage query wording, not full force
  reduction.
- DB compact summaries are not full DBMS acceleration.
- Graph visibility or candidate generation is not BFS, triangle counting,
  shortest-path, or whole graph analytics acceleration.
- Polygon candidate discovery is not exact polygon-area/Jaccard refinement.
- Hausdorff threshold decision is not exact Hausdorff distance unless separately
  proven.

### v1.0 Exit Criteria

v1.0 should be considered ready when:

- all public docs align with the current support matrix;
- all public speedup wording has reviewed evidence;
- blocked rows are explicitly documented as blocked;
- release tests pass;
- external review consensus exists for release authorization;
- compatibility wrappers and examples are stable enough for users.

## v1.5: Generic Primitive Refactor

### Purpose

v1.5 should reduce the native-engine technical debt exposed by v1.0.

The goal is to move domain knowledge out of C++/CUDA/OptiX/Embree-specific
entry points and into Python lowering code. The native engine should know about
geometry, payloads, traversal, and reductions, not application names.

### Non-Goal

v1.5 should not be a broad backend rewrite. It should not retire working v1.0
paths until replacement paths are proven. It should not use abstraction as an
excuse to regress performance or weaken public claim boundaries.

### Primitive Set

The initial v1.5 primitive set should match the refined Goal1042 consensus:

| Primitive | Purpose | Initial status |
| --- | --- | --- |
| `ANY_HIT` | Per-probe boolean hit/overlap/collision decision | stable target |
| `COUNT_HITS` | Per-probe or grouped hit counts under defined filtering rules | stable target |
| `REDUCE_FLOAT(MIN|MAX|SUM)` | Floating reductions for distances, payload sums, and threshold summaries | stable target |
| `REDUCE_INT(COUNT|SUM)` | Integer counts, flags, and grouped integer summaries | stable target |
| `COLLECT_K_BOUNDED` | Bounded candidate/hit collection for KNN/ANN or row-like paths | experimental after scalar primitives |

The split between float and integer reductions is intentional. It forces the ABI
to define dtype, precision, overflow, determinism, and comparison tolerance.

### Geometry And Payload Model

The primitive ABI should define a small set of lowered geometry types:

- points;
- segments;
- triangles;
- rays;
- AABBs;
- optional scalar payload arrays;
- optional object ids or group ids;
- bounded output buffers for experimental collection.

Python app code should lower domain data into these schemas. Native code should
not know about "robot", "database", "road hazard", "Hausdorff app", or "Barnes
Hut app" as business concepts.

### Required Contracts Before Coding

Before implementing v1.5 native code, the project should write and review:

- primitive ABI contract;
- result schema contract;
- per-app lowering matrix;
- backend parity matrix;
- fallback behavior contract;
- overflow and truncation rules;
- determinism and tolerance rules;
- public wording contract for generic primitive support;
- migration and retirement gates.

### Migration And Retirement Gate

A v1.0 app-specific endpoint may be retired only when its v1.5 path proves:

- correctness parity under the app's defined schema and tolerance;
- row/result-shape parity where rows are part of the contract;
- performance parity or explicitly accepted overhead;
- stable fallback behavior;
- preserved public claim boundaries;
- tests covering both old and new paths during the migration window.

"Exact bit parity" should not be a universal requirement. It may be appropriate
for integer counts and booleans, but floating reductions across Embree, OptiX,
Vulkan, HIPRT, and Apple RT need explicit tolerances.

### First Implementation Slice

The first v1.5 slice should be narrow:

1. Define the primitive ABI and lowering matrix.
2. Implement `ANY_HIT` and `COUNT_HITS` for one already-proven geometry pair in
   Embree and OptiX.
3. Migrate one or two fixed-radius prepared-summary apps behind compatibility
   wrappers.
4. Run old-vs-new correctness and performance comparisons.
5. Keep old app-specific endpoints until the replacement path is reviewed.

Only after this slice is accepted should the project implement
`REDUCE_FLOAT`, `REDUCE_INT`, or experimental `COLLECT_K_BOUNDED`.

## v2.0: Explicit Compute Partnership

### Purpose

v2.0 should make RTDL a clean traversal/reduction component inside larger GPU
and data-compute workflows.

RTDL should not become a general-purpose compiler for arbitrary Python,
database queries, graph algorithms, or simulation code. That would create a
large compiler project with unpredictable performance cliffs.

### Accepted v2.0 Direction

v2.0 should pursue explicit compute partnership:

- RTDL handles RT traversal and simple native reductions.
- External compute tools handle dense custom compute.
- DLPack or equivalent zero-copy protocols connect the phases.
- Users can see which phase used RTDL and which phase used another compute
  framework.

Likely partner classes include CuPy, PyTorch, Triton, Numba, and similar GPU
array/kernel systems. Other integrations, such as RAPIDS, TensorFlow,
PostgreSQL, or PostGIS, should be treated as possible future integrations, not
v2.0 commitments unless separately designed and reviewed.

### Extension Mechanisms

DLPack/zero-copy handoff should be the preferred stable extension path.

PTX, SPIR-V, dynamic native plugins, or user-injected hit programs may be useful
for power users, but they should remain experimental until the project has:

- ABI versioning;
- sandbox/security expectations;
- backend compatibility rules;
- reproducibility rules;
- review and claim-boundary rules;
- failure-mode documentation.

Native plugin execution should not be part of stable public speedup wording in
v1.5 or early v2.0.

### v2.0 Claim Boundary

v2.0 should preserve phase-specific claims:

- RTDL accelerated the traversal/reduction phase.
- A partner framework accelerated the downstream compute phase.
- The combination may be fast, but whole-workflow speedup claims require
  same-contract end-to-end evidence.

## Roadmap Table

| Version | Primary goal | Native engine state | Python/user state | Claim posture |
| --- | --- | --- | --- | --- |
| v1.0 | App credibility | App-specific endpoints allowed | Stable examples and docs | Bounded reviewed sub-path claims |
| v1.5 | Technical-debt reduction | Generic primitives introduced gradually | Python lowering becomes explicit | Primitive support is not automatic speedup wording |
| v2.0 | Ecosystem partnership | RTDL as traversal/reduction component | Users compose with external compute tools | Phase-specific claims unless end-to-end evidence exists |

## Immediate Next Work: Continue v1.0 First

The project should continue v1.0 work before starting v1.5 implementation:

1. Keep docs, tutorials, and examples aligned with the current public support
   matrix.
2. Harden release-facing tests around app behavior and claim boundaries.
3. Keep blocked RTX rows clearly blocked until new evidence changes them.
4. Improve user-facing app quality without changing public performance wording.
5. Prepare the v1.5 primitive ABI and per-app lowering matrix as design docs,
   not implementation yet.

This sequencing matters. If v1.5 begins before v1.0 is stable, RTDL risks
refactoring away the very app behavior that proves the project is useful.

## Gemini Review Questions

Please review this design for:

1. Whether v1.0 correctly prioritizes app credibility and bounded public claims.
2. Whether the v1.5 primitive set matches the prior Goal1042 consensus.
3. Whether the migration/retirement gates are strict enough without requiring
   impossible bit parity for all floating backends.
4. Whether v2.0 correctly chooses explicit compute partnership over a magic
   Python compiler.
5. Whether any statement still overclaims RT-core acceleration, graph support,
   DB support, or whole-app speedup.
