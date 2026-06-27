# Goal 83 Diagnosis and Proposal: Embree Long Exact-Source `county_zipcode`

## Purpose

This document records the first serious attempt to carry the OptiX long-workload
end-to-end story over to Embree on the same exact-source `county_zipcode`
positive-hit `pip` surface, the failure that was observed, and the current repair
proposal.

This is a diagnosis/proposal document only. It is not a publishable result report.

## Target surface

- host: Linux (`lestat-lx1`)
- repo baseline for the clean run: `209db71`
- workload: long exact-source `county_zipcode`
- query shape: positive-hit `pip`
- comparison target: indexed PostGIS
- backend under test: Embree

Exact-source directories used:

- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

## Why this goal exists

OptiX now has a credible repeated raw-input end-to-end win on the accepted long
exact-source surface. The natural next question was whether the same runtime-side
advancements were already enough for Embree.

The assumption was reasonable because the relevant runtime pieces already appear
to be shared:

- prepared-execution cache
- identity-based fast path for canonical tuples
- dataset adapters returning canonical RTDL records
- prepacked point/polygon reuse for canonical dataset views

So the first step for Embree was not a speculative rewrite. It was to measure the
same surface honestly.

## Initial Linux result

The first exact-source long raw-input measurement used:

- clean Linux clone: `/home/lestat/work/rtdl_goal83`
- script:
  - `scripts/goal77_runtime_cache_measurement.py`
- backend:
  - `embree`

Observed result:

- PostGIS row count: `39073`
- Embree row count: `39215`
- PostGIS timing: about `3.10` to `3.33 s`
- Embree timing: about `44.99` to `47.74 s`
- parity vs PostGIS: `false` on every rerun
- digest mismatch was stable across reruns

Interpretation:

- this was not a noisy benchmark
- this was a stable correctness defect plus a severe performance problem

## Immediate conclusions

1. Embree is not yet in the same state as OptiX on this exact-source long
   surface.
2. The problem is not just "Embree is slower."
3. The path is correctness-broken first, then performance-bad.
4. This cannot be published as an Embree performance package.

## Technical diagnosis

The first important finding is in the native Embree positive-hit `pip` path in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`

Before the repair patch, the `positive_only` branch did this:

1. Build an Embree user-geometry scene for polygons.
2. Iterate points serially.
3. For each point, run `rtcIntersect1(...)`.
4. In the callback, run local `point_in_polygon(...)`.
5. Immediately treat that callback-local result as final truth for the emitted
   positive-hit set.

That is structurally weaker than the repaired OptiX story.

### Why that is a problem

The backend traversal and the exact truth step are being mixed together.

The callback path is appropriate for:

- candidate discovery

It is not a strong place to finalize exact truth for the published comparison
surface, especially when the accepted external truth source is PostGIS and the
cleanest exact host-side reference is GEOS-backed coverage testing.

This explains the symptom shape:

- stable parity drift
- stable wrong digest
- row count consistently too high

That pattern is much more consistent with systematic false positives than with
random traversal instability.

## Current repair proposal

The current proposal is:

### 1. Treat Embree as candidate generation only in positive-hit mode

For `positive_only != 0u`:

- the Embree callback should collect candidate polygon primitive indices
- it should not finalize truth directly in the callback

### 2. Exact-finalize only those candidates on the host

After candidate collection per point:

- sort candidate polygon indices for deterministic output
- exact-finalize each candidate:
  - use GEOS `covers(...)` when available
  - use local `point_in_polygon(...)` only as a fallback for non-GEOS builds
- emit only exact positive rows

### 3. Leave full-matrix mode unchanged

Goal 83 should remain narrow:

- only the positive-hit branch changes
- full-matrix semantics must stay as they are unless a separate defect appears

## Why this proposal is the right first fix

It matches the accepted philosophy already used elsewhere in the project:

- traversal narrows the search space
- exact finalize owns truth

That gives us:

- a clearer correctness boundary
- a better parity story against PostGIS
- a more comparable backend/runtime structure across OptiX and Embree

## Current local patch status

A local patch has already been applied in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`

The patch changes the positive-hit path so that:

- the callback records candidate polygon primitive indices
- host-side exact finalize decides whether each candidate really contains the point
- GEOS is used when available

Focused validation after this patch:

- local Mac focused slice: `OK` with one expected local Embree/GEOS limitation
- clean Linux focused slice: `19` tests, `OK`

These focused tests are necessary, but they are not sufficient.

The missing step is the decisive one:

- rerun the long exact-source Linux measurement after the patch
- confirm parity first
- then assess performance

## Why performance is still expected to be hard

Even if parity is fixed, Embree still has obvious structural costs on this
surface:

1. The point loop is effectively serial.
   - one `rtcIntersect1(...)` call per point
2. Exact finalize still happens on the host.
3. The exact-source `county_zipcode` workload is large.
4. Embree remains entirely CPU-side, unlike OptiX traversal.

So the expected order of work is:

1. restore exact parity
2. measure prepared and repeated raw-input boundaries again
3. only then decide whether Embree can realistically claim a PostGIS win on this
   surface

## Acceptance criteria for the repaired Goal 83 package

Before Goal 83 can be published, the package should show:

1. exact parity against PostGIS on the exact-source long `county_zipcode`
   positive-hit `pip` surface
2. clear timing-boundary labeling
   - repeated raw-input
   - prepared execution, if measured
3. explicit statement of whether Embree wins, loses, or remains inconclusive
4. 2+ AI review before publication

## Recommended next steps

1. rerun exact-source Linux measurement with the patched Embree backend
2. verify parity against PostGIS
3. if parity is restored:
   - measure prepared execution separately
   - determine whether the remaining issue is end-to-end overhead or backend cost
4. produce a final Goal 83 report only after parity is clean

## Current honest status

- OptiX: publishable long exact-source repeated-call win already exists
- Embree: not there yet
- Goal 83 is a real repair goal, not a mere benchmarking formality

That is normal project work. The important thing is that the failure has now been
made explicit, localized, and turned into a concrete repair plan.
