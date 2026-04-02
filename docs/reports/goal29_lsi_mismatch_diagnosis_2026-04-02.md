# Goal 29 LSI Mismatch Diagnosis (2026-04-02)

## Scope

Goal 29 investigated the larger-slice `lsi` mismatch discovered in Goal 28D on Linux exact-source `County ⊲⊳ Zipcode` runs.

The round was intentionally allowed to close in one of two ways:
- a demonstrated parity fix plus regression coverage, or
- a concrete root-cause diagnosis with bounded unresolved status

This round closes in the second form.

## Frozen Reproducer

The mismatch was reproduced on a frozen `k=5` slice copied from the Linux host.

Observed pair-level difference:
- CPU (`rt.run_cpu(...)`): `7` pairs
- Embree (`rt.run_embree(...)`): `3` pairs
- CPU-only pairs:
  - `(24, 368)`
  - `(25, 367)`
  - `(26, 365)`
  - `(111, 345)`
- Embree-only pairs: none

All four missing pairs shared:
- `left_chain_id = 27489`
- `right_chain_id = 4706`

This made a general conversion failure unlikely and pointed to a workload-specific `lsi` issue.

## Minimal Exact-Source Reproducer

A much smaller reproducer was then extracted from the exact-source slice:
- 4 left segments
- 4 right segments
- expected intersections exactly matching the four CPU-only pairs above

On that reproducer:
- CPU returned all 4 expected pairs
- Embree returned 0 pairs

This proved the bug was not dependent on the larger slice as a whole.

## Confirmed Findings

### 1. Float precision loss is a real contributing factor

The Python reference path uses Python `float` arithmetic, i.e. double precision.

The active native ABI between Python and the Embree shared library uses `float` coordinates in:
- `_RtdlSegment`
- `_RtdlPoint`
- `_RtdlTriangle`
- `_RtdlRay2D`
- polygon vertex arrays

When the minimal 4-pair reproducer was rounded to float32 on the Python side and then run through the CPU reference path, one of the four intersections disappeared immediately. That confirms the current float-based native ABI is already too lossy for exact-source geographic segment data at this coordinate scale.

So one confirmed problem is:
- exact-source `lsi` on geographic coordinates is not safe under the current float-based native geometry ABI

### 2. Float precision loss is not the whole story

Even after local experimental attempts to:
- use double-precision math inside native `segment_intersection(...)`
- normalize the query ray
- widen candidate bounds
- enable Embree robust scene mode
- try an Embree collision-style broad phase
- promote the local native ABI prototype toward doubles

the minimal exact-source reproducer still did not become parity-clean in the active backend.

That means the mismatch is not explained by a single epsilon constant or one simple local math bug.

### 3. The current Embree LSI broad-phase design remains suspect

The current `lsi` Embree path models the workload through a segment-as-ray style traversal over user geometry. That model already looked fragile for exact-source geographic data, and Goal 29 did not produce evidence that it is trustworthy at larger exact-source scales.

So the second confirmed problem is:
- the current Embree `lsi` broad phase remains structurally suspect for exact-source GIS segments, even beyond the now-confirmed float-ABI issue

## What Was Attempted

During diagnosis, several uncommitted local experiments were tried and then discarded because they were not sufficient:
- tighter native analytic intersection logic
- XY padding of segment bounds
- robust Embree scene mode
- normalized finite-ray parameterization
- an Embree scene-collision broad-phase attempt
- a prototype double-precision ABI change

These experiments narrowed the diagnosis, but none produced a publishable fix in this round.

No runtime code changes from those attempts were kept.

## Current Honest Status

Goal 29 does **not** close with a parity fix.

Goal 29 **does** close with a materially tighter diagnosis:
- the mismatch is real and frozen
- it can be reproduced on a minimal exact-source segment set
- float32 truncation in the active native ABI is one confirmed contributing cause
- the current Embree `lsi` broad phase still has unresolved candidate-omission or traversal-stability problems on exact-source geographic geometry

## Next Required Goal

The next correct goal is:

**redesign or instrument the Embree `lsi` broad phase before any larger exact-source `County ⊲⊳ Zipcode` claims are extended**

That next round should do at least one of:
- add direct instrumentation proving whether missed pairs fail before or inside the native refine callback
- replace the current segment-as-ray `lsi` broad phase with a better Embree-side candidate-generation design
- formally migrate the active native geometry ABI from float to double where exact-source Linux runs require it

Until that is done, larger exact-source `lsi` Linux results should be treated as bounded and unresolved.
