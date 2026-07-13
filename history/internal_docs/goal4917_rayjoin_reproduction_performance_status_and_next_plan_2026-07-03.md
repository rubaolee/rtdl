# Goal4917 — RayJoin Reproduction / Performance Status And Next Work Plan

Date: 2026-07-03

## Purpose

This document consolidates the current state after the RayJoin reproduction and
post-v2.14 performance work through Goal4916. It records:

- what has been achieved;
- what is proven by evidence;
- what is not proven;
- why the current micro-optimization line should stop;
- what the next work should be if the project continues.

This is a planning/reporting document. It does not authorize new performance
claims, public wording changes, V3/V4 resurrection, raw OptiX callbacks, or new
native output subsystems.

## One-Paragraph Status

RTDL now has a correct, bounded RayJoin paper-reproduction engineering route for
Section 5.2 / 5.3 / 5.7, with the key Section 5.7 representative path running
through public RTDL planar-map primitives, a new public planar-map workspace API,
and Numba app-layer continuation. The route is byte-equal to AuthorOfficial on
the Australia representative Section 5.7 workload and preserves correctness
while reaching a best prepared-hot body around `3.8–4.0s`. The remaining
performance gap is no longer a simple LSI/PIP primitive issue or a setup knob
issue; small Python writer optimizations are exhausted. Any larger performance
gain now requires a new architecture decision: dataflow-to-kernel pushdown,
in-traversal continuation, or a separately reviewed compiled/native output
subsystem.

## Current Best Evidence

### Correctness Comparator

The current comparator is:

```text
AuthorOfficial = author source + documented RTDL contract patch
```

This comparator has been disclosed and reviewed. Its important distinction:

- author-derived behavior, such as directed point-location / SoS slope ordering,
  is treated as the author intended contract;
- RTDL-defined deterministic duplicate-half-edge canonicalization is explicitly
  disclosed and must not be described as raw-author byte reproduction unless a
  given dataset proves the patch has zero effect.

### Section 5.2 / 5.3 / 5.7 Status

| Section | Status | Evidence Type | Boundary |
|---|---|---|---|
| 5.2 LSI | reproduced on approved representative data | public planar-map LSI primitive, count-level / row-level where available | not a full eight-pair exact-input claim |
| 5.3 PIP / point-location | reproduced on approved representative data | public planar-map point-location primitive and raw-author query hash where applicable | point-location correctness is bounded to tested datasets/contracts |
| 5.7 Polygon overlay | bounded representative reproduction complete | public LSI + public PIP + app-layer overlay writer; byte-equal to AuthorOfficial | representative / bounded, not full eight-pair paper dataset claim; Australia/SA results are AuthorOfficial-contract results, not raw-author-byte-equality claims unless a per-dataset patch-impact audit proves zero effect |

The strongest correctness anchor remains the byte-equal Section 5.7
representative output:

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
bytes:  6189260
lines:  276320
```

## RTDL Language/Product Work Completed

### Public Primitives

RTDL now exposes the core public primitives needed by the RayJoin-style
planar-map route:

```text
prepare_planar_map_lsi_2d_optix
prepare_planar_map_point_location_2d_optix
```

These are public planar-map primitives, not user-facing calls to the bundled
`rtdsl.rayjoin_overlay` helper.

### Public Workspace API

Goal4913 implemented:

```text
PlanarMapWorkspace2DOptix
prepare_planar_map_workspace_2d_optix
```

The intended user shape is:

```python
with prepare_planar_map_workspace_2d_optix(left, right, cache_dir=cache) as ws:
    pair_rows = ws.run_lsi_pair_id_rows()
    left_faces = ws.run_left_points_in_right()
    right_faces = ws.run_right_points_in_left()
```

This is a product-level improvement because it turns the hand-built
prepared-session pattern into a coherent RTDL lifecycle API:

```text
load/pack once
prepare LSI once
prepare point-location once
run hot query bodies repeatedly
close handles explicitly
```

### Numba Partner Role

Numba is validated as a useful app-layer partner:

- midpoint generation;
- point-pair dedupe;
- chain keep/skip decisions;
- writer skip-plan construction.

Numba does not run inside the RTDL LSI/PIP traversal kernels and does not replace
OptiX traversal.

## Performance Progression

Australia representative Section 5.7:

Definition:

```text
Hot Body = prepared-hot query+output body, including LSI/PIP replay,
reprojection/sorting, app continuation, exact output-chain writer, and file
summary checks. It excludes cold one-time workspace setup and import/setup
phases.
```

| Goal | Route | Hot Body | Writer | Correct |
|---|---|---:|---:|---|
| Goal4902 | point-location session reuse | `6.915s` | `3.031s` | yes |
| Goal4904 | prepared LSI + PIP replay | `4.638s` | `2.562s` | yes |
| Goal4910 | direct no-xsect descriptor | `3.918s` | `1.840s` | yes |
| Goal4914 | public workspace smoke | `3.955s` | `1.875s` | yes |
| Goal4915 | direct intersection flush probe | `3.832s` | `1.763s` | yes |

Earlier Goal4887/4888 discussions used a coarser `query+output` baseline around:

```text
20.920s query+output
```

That number mixed the wrong cold/hot interpretation into the branch decision.
The later hot/prepared measurements showed the important correction:

```text
Goal4888 "native traversal dominated" was a cold/unprepared-state conclusion.
Prepared-hot state is Branch A: materialization/output/session-lifecycle work.
```

The original `3–8s` hot query+output target that looked unrealistic under the
cold `18.880s` interpretation has in fact been reached in prepared-hot mode:

```text
best prepared-hot query+output body: 3.832s
```

This does not mean the earlier block was wrong. It means the block forced the
measurement distinction that made the route possible: do not attack cold setup
and hot replay with the same explanation.

Interpretation:

- Prepared LSI/PIP/session reuse produced the major improvement.
- The workspace API productized the route without meaningful hot-path
  regression.
- Goal4915 produced a small improvement but missed the hard productization bar.
- Python writer micro-optimizations are now a low-yield path.

## What Is Not Solved

### Not A Broad Speedup Claim

The project cannot honestly claim:

- broad RayJoin speedup;
- broad RTDL speedup;
- full eight-pair Section 5.7 performance;
- single-run cold-start win over AuthorOfficial;
- raw OptiX callback parity.

### Cold Setup Is Still Real

The workspace API is an in-process repeated-query / hot-session tool. It does
not erase one-time setup:

- CDB load/pack exists, though packed cache reduces it;
- point-location prepared locator build remains nontrivial;
- cross-process GAS/build-artifact persistence was explicitly deferred because
  it is backend/driver-sensitive and high-risk.

### Remaining Hot Path Is Mostly App-Layer Output

After prepared LSI/PIP replay:

- LSI replay is tiny (`~0.006s`);
- native PIP traversal itself is tiny, though Python row conversion remains;
- exact output-chain writer remains about `1.7–1.9s`;
- reprojection/sorting remains around `0.8–0.9s`.

The current exact AuthorOfficial text/topology output format is expensive in
Python. Small writer tweaks have been tested and no longer justify more work.

This matters for architecture: the remaining RayJoin hot-path gap is
writer/output-format bound, not traversal-reduce bound. A dataflow-to-kernel
pushdown compiler is still an important long-term RTDL language investment, but
it is not the direct remedy for this RayJoin representative workload's remaining
seconds. The RayJoin-specific remaining leverage is a compiled/native output
writer, and that is precisely the risky/app-specific direction that must not be
smuggled into RTDL core.

## Why We Should Stop Micro-Optimization Now

The following paths have been tested:

- point-location group-mode tuning: no meaningful win;
- no-xsect writer skip tweaks: exhausted;
- direct no-xsect descriptor: small win only;
- direct intersection-chain flush: small win only;
- prepared LSI/PIP/session reuse: real win, now productized.

Continuing to produce more Python writer variants would likely be
looks-busy-but-low-value work. The next meaningful performance gain requires a
different class of work.

## Next Work Plan

### Goal4918 — Clean Integration And Public/Private Boundary Audit

Purpose:

Ensure the new v2.14-era public primitives and workspace API are integrated
cleanly without leaking internal RayJoin reproduction process material into
user-facing docs.

Work:

- audit `README`, `docs/`, `tutorials/`, `examples/`;
- decide whether `prepare_planar_map_workspace_2d_optix` is public-facing now or
  remains internal until a tutorial/example is ready;
- ensure no V3/V4 or internal review language leaks back into the public surface;
- add a concise primitive/API reference if the workspace is exposed publicly.

Exit gate:

```text
user-visible surface clean; workspace API either documented or explicitly kept internal
```

### Goal4919 — RayJoin Paper-Reproduction Package Consolidation

Purpose:

Package the RayJoin reproduction engineering app as a stable internal/paper
artifact with clear claims.

Work:

- collect Section 5.2 / 5.3 / 5.7 final reports into one index;
- link comparator disclosure;
- link AuthorOfficial patch disclosure;
- link representative data provenance;
- link performance table;
- explicitly mark full eight-pair exact-input reproduction as not claimed.

Exit gate:

```text
single reader-facing reproduction packet exists; all claims have artifact links
```

### Goal4920 — Workspace API User Example

Purpose:

Show a spatial/database expert how to use RTDL without knowing OptiX internals.

Work:

- create a small runnable planar-map example:
  - load/pack CDB-like fixture;
  - prepare workspace;
  - run LSI pair rows;
  - run point-location;
  - use a small Python/Numba continuation;
- keep it smaller than RayJoin full overlay;
- avoid one-call “do everything” style.

Exit gate:

```text
example teaches the RTDL model: prepare workspace, run primitives, compose app logic
```

### Goal4921 — Architecture Decision: Next High-Performance Track

Purpose:

Make the project-owner decision on the next large performance architecture.

Options:

1. **Dataflow-to-kernel pushdown compiler**
   - long-term RTDL language direction;
   - users write dataflow / reduce logic;
   - compiler decides what enters traversal.
   - this is **not** expected to move the remaining RayJoin representative
     number, because that number is now mostly exact output-chain writer and
     reprojection/sort work rather than traversal reduction.

2. **Native/compiled output writer subsystem**
   - narrower and RayJoin-adjacent;
   - can improve exact output assembly;
   - risks becoming app-output-specific infrastructure.
   - this is the only plausible direct lever for the remaining RayJoin
     representative hot-body gap, but it is also the most likely to violate the
     generic-engine rule unless scoped as paper-app infrastructure.

3. **Stop at v2.14 + workspace + partner app continuation**
   - honest current product state;
   - no new architecture risk.
   - this is the default honest product state unless the owner explicitly
     accepts one of the larger architecture risks above.

Exit gate:

```text
owner chooses one track; no implementation begins before decision and review
```

### Goal4922 — If Track 1 Is Chosen: Minimal Pushdown Spike

Purpose:

Build the smallest falsifiable experiment for RTDL dataflow-to-kernel pushdown.
This is a generic language/R&D track, not a RayJoin performance rescue.

Work:

- choose one generic reduce pattern, not RayJoin overlay;
- choose a workload whose remaining cost is actually traversal/continuation
  bound, not exact text output bound;
- define user-facing dataflow form;
- measure against separate traverse + continuation;
- kill if no material win or if it becomes raw OptiX callback exposure.

Exit gate:

```text
pushdown produces a real win on a generic pattern, or the spike is killed
```

### Goal4923 — If Track 2 Is Chosen: Native/Compiled Output Writer Design

Purpose:

Design, but not yet implement, a compiled output writer subsystem. This is the
only track aimed directly at RayJoin's remaining hot-body seconds, and therefore
must be treated as high-risk for app-specific leakage.

Work:

- define what is generic output infrastructure vs RayJoin output format;
- identify whether this belongs in RTDL core, app package, or paper-reproduction
  app only;
- assume the default answer is "paper-reproduction app only" unless a reviewer
  can show a genuinely generic output-descriptor abstraction;
- require byte equality;
- require a strong performance bar before productization.

Exit gate:

```text
external review decides whether this is legitimate infrastructure or app-specific code
```

## Immediate Recommendation

Do Goal4918 and Goal4919 before any new architecture work.

Reason:

- the code has moved;
- the claims are subtle;
- the user-facing surface must stay clean;
- the reproduction package should become stable before the project opens a new
  high-risk performance branch.

After that, the project owner should decide Goal4921.

## Summary For Management

What we can say:

```text
We reproduced a bounded RayJoin Section 5.7 representative workload with
RTDL public planar-map primitives plus Numba app-layer continuation, byte-equal
to the documented AuthorOfficial comparator. We also converted the hand-built
prepared-session route into a reusable public workspace API with no meaningful
hot-path regression.
```

What we cannot say:

```text
We do not yet beat the author’s fused C++/CUDA/OptiX implementation broadly.
We do not claim full eight-pair Section 5.7 performance.
We do not expose raw OptiX callback equivalence.
```

What the work taught us:

```text
RTDL's clean dataflow + public primitive model works for correctness and
composition. For large performance gains, the next problem is architectural:
move selected dataflow continuation into traversal through compiler pushdown,
or explicitly build a compiled output subsystem. Small Python-side tweaks are
now exhausted.
```
