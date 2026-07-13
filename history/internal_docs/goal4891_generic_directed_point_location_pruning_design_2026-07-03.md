# Goal4891: Generic Directed Point-Location Candidate-Pruning Design

Date: 2026-07-03

## Purpose

Goal4890 measured the missing work-count denominator for the Australia
representative Section 5.7 workload. The result was decisive:

| Stage | RTDL segment-loop iterations | AuthorPatch segment tests | RTDL / AuthorPatch |
| --- | ---: | ---: | ---: |
| vertex PIP map0 in map1 | 511,943,147,571 | 84,341,083 | 6,069.9x |
| vertex PIP map1 in map0 | 36,359,368,176 | 18,561,490 | 1,958.9x |
| midpoint PIP map0 | 68,493,462 | 74,815 | 915.5x |
| midpoint PIP map1 | 105,145,275 | 108,540 | 968.7x |

Goal4891 designs the next RTDL mechanism to reduce this candidate explosion.
It is not an implementation goal.

## Non-Negotiable Constraints

The solution must be generic RTDL engine work, not a RayJoin shortcut.

Forbidden:

- no `rayjoin_overlay` fast path;
- no hidden RayJoin-only kernel;
- no raw public OptiX any-hit / closest-hit callback API;
- no public performance claim;
- no broad release claim;
- no prepared-session / row-buffer / Numba API work unless separately justified;
- no semantic/comparator change.

Allowed:

- generic directed point-location primitive redesign;
- generic in-traversal pruning;
- generic data-flow pushdown for point-location predicates;
- internal kernel specialization if the public abstraction remains generic;
- a small proof experiment after review approval.

## What The Measurement Means

The issue is not that RTDL launches more point queries. Query counts match.

The issue is that RTDL's current public directed point-location route tests far
more candidate segments per query. Therefore, the next work must reduce work
volume before tuning per-test kernel speed.

This is the concrete form of the previously discussed fusion gap:

```text
current RTDL: traverse broad candidate ranges -> materialize/continue outside
needed path: prune/decide more inside traversal using a generic contract
```

## Candidate Design Routes

### Route A: Generic Candidate-Range Tightening

Change the prepared directed point-location acceleration structure so each
vertical-ray query visits fewer segment ranges.

Examples:

- tighter group ranges;
- query-direction-aware AABB grouping;
- split large y-ranges / x-ranges so leaf ranges are smaller;
- maintain generic planar-map point-location semantics.

Pros:

- keeps current public primitive shape;
- no callback-like feature;
- easiest to prove generic.

Risk:

- may not reach AuthorPatch if AuthorPatch's advantage comes from shader-level
  pruning rather than grouping.

### Route B: Generic In-Traversal Pruning Predicate

Move the generic point-location rejection rules into traversal so the kernel can
discard candidates before the full segment loop.

Examples:

- x-bound rejection;
- vertical-edge rejection;
- above/below query rejection;
- same Simulation-of-Simplicity ordering, but as part of generic directed
  point-location.

Pros:

- directly attacks the 915x-6069x PIP work explosion;
- still generic if the contract is "directed planar-map point-location," not
  "RayJoin overlay."

Risk:

- must prove this is not a RayJoin-only kernel under a generic name.

### Route C: Data-Flow Pushdown For Point-Location

Expose a declarative point-location query plan where RTDL can push recognized
filters/reductions into traversal.

User-facing shape stays data-flow:

```python
with rtdl.prepare_directed_point_location_2d(base_map, direction="up") as locator:
    faces = locator.locate_points(points, contract="planar_map_sos")
```

The engine decides whether to use Route A/B internally.

Pros:

- preserves RTDL's language identity: users write what they want, not raw
  callbacks;
- future-proof for other workloads.

Risk:

- too large for the first proof if treated as a full compiler project.

## Recommended First Proof

Do not start with a full compiler.

Start with **Route B over the existing public directed point-location primitive**
as a narrow generic proof:

1. Keep the public API identical.
2. Keep output byte-equal on the Australia representative workload.
3. Add generic instrumentation:
   - query count;
   - candidate segment-loop count;
   - positive face count;
   - traversal time.
4. Require the candidate count to move materially toward AuthorPatch:
   - hard gate: at least 10x fewer RTDL candidate segment iterations on map0;
   - strong gate: at least 100x fewer on map0;
   - ideal direction: same order of magnitude as AuthorPatch.
5. Validate on a second non-RayJoin-shaped directed point-location synthetic
   workload before claiming genericity.

This proof may use internal kernel specialization, but the public claim is only:

```text
generic directed point-location candidate pruning
```

not:

```text
RayJoin overlay acceleration
```

## Verification Gates

Before implementation:

- external review approves this design direction;
- exact allowed code surface is named;
- expected counters are frozen.
- the non-RayJoin synthetic workload is defined before coding;
- the SoS equivalence argument is written before coding.

After implementation proof:

- byte equality preserved on Australia representative;
- synthetic directed point-location correctness tests pass;
- candidate count reduced by the frozen threshold;
- no public docs/release/performance claim is made;
- no RayJoin-only symbol appears in the new public API.

## Required Amendments Accepted From Antigravity Review

Antigravity reviewed the first Goal4891 design and returned
`approve_with_amendments`. These amendments are now part of Goal4891.

### AM1: Non-RayJoin Synthetic Workload

The proof must include at least one synthetic directed point-location workload
that is not shaped like RayJoin overlay.

Acceptable options:

- randomized non-grid-aligned planar-map topology;
- concentric nested rings with slanted edges;
- Delaunay-like irregular triangulation if cheap to construct.

The point of this test is not to reproduce an application. It is to prove that
the pruning rule is a generic directed point-location rule, not a RayJoin-only
patch.

### AM2: Simulation-of-Simplicity Equivalence

Before coding, the proof must state why the pruning rule cannot change the
existing Simulation-of-Simplicity ordering.

The pruning rule may reject a segment only when it is impossible for that
segment to beat the current best hit under the same directed point-location
contract. It must not skip any candidate that could participate in:

- equal-height tie handling;
- slope tie handling;
- map0/map1 directed overlay ordering;
- canonical duplicate-edge ordering.

If that proof cannot be stated, the implementation must not start.

### AM3: First-Proof Code Surface

The first proof is limited to:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`

No Python API, compiler representation, docs, tutorials, public surface,
prepared-session API, row-buffer ABI, or Numba partner API changes are allowed
in the first proof.

### AM4: Diagnostic Work-Count Interface

The candidate/query counters from Goal4890 must become a clean internal
diagnostic surface for the proof so every run can report:

- query count;
- candidate segment-loop count;
- positive face count;
- traversal time.

This diagnostic surface must not become public API clutter and must not be used
for public performance claims.

## Failure Labels

Use one:

- `candidate_pruning_proof_passed_continue_engine_work`
- `candidate_pruning_correct_but_not_enough_reassess_route_a_or_c`
- `candidate_pruning_breaks_correctness_stop`
- `candidate_pruning_is_rayjoin_specific_reject`
- `measurement_not_reproducible_redo_goal4890`

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid move would be to implement Numba/row-buffer/prepared-session work
   after Goal4890 proved the dominant problem is candidate explosion. This goal
   instead targets the measured cause.

2. **What would make this decision stupid?**

   Implementing a RayJoin-only kernel and calling it generic.

3. **Is there another path?**

   Native micro-tuning exists, but it is not first because the work count is
   915x-6069x larger. Reduce work first.

4. **Can we start a different path that truly solves the problem?**

   Yes: a reviewed, generic directed point-location pruning proof with frozen
   candidate-count gates.
