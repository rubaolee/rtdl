# Goal4892: Generic Directed Point-Location Pruning Implementation Proof

Date: 2026-07-03

## Purpose

Goal4890 proved that the RayJoin Section 5.7 hot-path gap is dominated by
directed point-location/PIP candidate explosion, not by Python, output writing,
host transfer, prepared sessions, or Numba continuation:

- vertex PIP map0 in map1: RTDL tested 6,069.9x more segment-loop candidates
  than AuthorPatch;
- vertex PIP map1 in map0: 1,958.9x more;
- midpoint PIP stages: roughly 900x more.

Goal4891 designed the next move: a bounded, generic Route-B proof that prunes
impossible directed point-location candidates inside traversal while preserving
the existing public API and correctness contract.

Goal4892 implements that proof.

## Scope

Allowed code surface for the first proof:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`

Forbidden:

- no Python public API changes;
- no docs/tutorial/release-surface changes;
- no Numba API changes;
- no prepared-session or row-buffer ABI work;
- no raw OptiX callback API;
- no `rayjoin_overlay` fast path;
- no semantic/comparator change;
- no public performance claim.

## Generic Pruning Rule

The first proof uses a conservative directed point-location lower-bound rule.

For an upward directed point-location query, once a current best hit exists:

```text
If a candidate segment's minimum possible hit y is strictly greater than the
current best hit y, the segment cannot become the winning segment.
```

Therefore the kernel may skip the expensive exact segment test for that segment.

The rule is generic because it depends only on directed point-location ordering:
"find the closest valid segment above this query point under the same SoS
contract." It does not reference RayJoin overlay topology, chain semantics,
output-chain construction, or paper-specific datasets.

## Simulation-of-Simplicity Equivalence

The pruning rule must not skip equality cases.

It may reject only when the candidate segment's lower bound is strictly greater
than the current best. If the candidate could hit at the current best height, it
must remain in the normal comparator path so the existing SoS rules still decide:

- equal-height slope handling;
- map0/map1 directed ordering;
- equal-slope source-order behavior;
- canonical duplicate-edge mapping.

For scaled CDB points, the comparison is made in scaled y coordinates. For
unscaled points, the comparison uses the current best `t` and a lower bound
`segment_min_y - point_y`. Equality is preserved by using strict `>`.

## Implementation Plan

1. Add internal diagnostic counters for directed point-location candidate work:
   query count, tested segment count after pruning, pruned segment count,
   positive face count, and traversal time.
2. Add conservative in-loop pruning before the expensive line-intersection
   check in `__intersection__rayjoin_cdb_point_location`.
3. Keep the public API and Python layer unchanged.
4. Add a non-RayJoin-shaped synthetic source test that verifies the generic
   rule exists and that the diagnostic interface is internal.
5. Run focused synthetic and existing correctness tests locally.
6. Run the Australia representative POD proof:
   - byte equality must remain true;
   - candidate work must reduce by at least 10x on vertex PIP map0;
   - 100x is the strong gate.

## Verification Gates

### Required

- Existing SoS synthetic tests pass.
- New Goal4892 synthetic guard passes.
- Australia representative byte-equality remains true.
- Candidate work counters are emitted from an internal diagnostic symbol.
- Candidate work reduction:
  - hard gate: at least 10x fewer tested segment candidates on map0;
  - strong gate: at least 100x fewer tested segment candidates on map0.

### Not Sufficient

- A faster wall time without byte equality.
- A RayJoin-specific branch.
- A public API rename or documentation claim.
- Only reducing Python/output time.

## Exit Labels

Use one:

- `candidate_pruning_proof_passed_continue_engine_work`
- `candidate_pruning_correct_but_not_enough_reassess_route_a_or_c`
- `candidate_pruning_breaks_correctness_stop`
- `candidate_pruning_is_rayjoin_specific_reject`
- `measurement_not_reproducible_redo_goal4890`

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid move would be to continue tuning Python/Numba/output code after
   Goal4890 proved the hot gap is candidate explosion. This goal targets the
   measured native work count.

2. **What actions would make this decision stupid?**

   Calling a RayJoin-only shortcut generic, changing SoS semantics, or claiming
   performance from wall time before candidate counters and byte equality pass.

3. **Is there another possible path?**

   Yes: Route A grouping redesign or Route C data-flow compiler work. They are
   held back until this smaller Route-B proof shows whether in-loop pruning can
   materially reduce work without breaking correctness.

4. **Can we start a different path that truly solves the problem?**

   Yes, if this proof fails: either reassess broad-phase grouping or move to the
   larger data-flow pushdown compiler path. The current proof is the cheapest
   falsifiable next step.
