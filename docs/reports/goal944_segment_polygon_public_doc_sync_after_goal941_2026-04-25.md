# Goal944 Segment/Polygon Public Doc Sync After Goal941

Date: 2026-04-25

## Scope

Goal944 fixes stale segment/polygon public documentation after Goal941 and Goal942 promoted bounded prepared segment/polygon paths to RTX claim-review readiness.

## Problem Found

The segment/polygon tutorial and feature docs still contained pre-Goal941 wording:

- direct road/hitcount paths still reject `--require-rt-core`
- pair-row speedup promotion still requires the old Goal873 strict RTX gate
- released OptiX RT-core claims are still blocked until a strict gate has a real RTX artifact

That was stale after Goal941 supplied the RTX artifacts and Goal942 promoted the bounded prepared paths to claim-review readiness.

## Fix

Updated:

- `docs/tutorials/segment_polygon_workloads.md`
- `docs/features/segment_polygon_hitcount/README.md`
- `docs/features/segment_polygon_anyhit_rows/README.md`
- `tests/goal858_segment_polygon_docs_optix_boundary_test.py`

Current wording now says:

- road hazard has a bounded claim-review path for prepared compact summary traversal
- segment/polygon hit-count has a bounded claim-review path through the Goal933 prepared profiler
- segment/polygon pair rows have a bounded claim-review path through the Goal934 prepared profiler and Goal941 artifact
- public claims remain narrow: no full GIS/routing, no broad segment/polygon speedup, and no unbounded row-volume speedup

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal858_segment_polygon_docs_optix_boundary_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test -v
```

Result: 8 tests OK.

Stale phrase sweep:

```bash
rg -n 'Goal873|strict RTX validation passes|still behind the Goal873|released OptiX RT-core claims are still blocked|still reject|reject `--require-rt-core` today|nine bounded|exactly nine|ready set is exactly nine|after Goal937|remain held for claim review' README.md docs/*.md docs/tutorials docs/features tests src/rtdsl/app_support_matrix.py
```

Only expected historical/current-valid references remain:

- graph component scripts still reject `--require-rt-core`; the unified graph app is the claim-sensitive graph entry point
- the historical `Goal873NativePairRowOptixGateTest` class name remains

## Boundary

This is a documentation synchronization goal. It does not authorize public speedup claims.
