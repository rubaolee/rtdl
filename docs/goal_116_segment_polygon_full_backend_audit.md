# Goal 116: Segment/Polygon Full Backend Audit

Date: 2026-04-06
Status: accepted

## Purpose

Finish a full backend audit for the `segment_polygon_hitcount` feature family.

This goal is not another family-definition step. The family is already closed.
This goal checks whether the current implementation is actually strong enough to
stand as a product feature across the current backend surface.

## Required outcomes

1. correctness is checked against the Python oracle on accepted datasets for:
   - `cpu`
   - `embree`
   - `optix`
   - `vulkan`
2. a large deterministic external correctness check exists against PostGIS
3. the current performance/parallelization state is written explicitly, backend
   by backend
4. the final package distinguishes:
   - correctness closure
   - prepared-path usefulness
   - remaining optimization gaps

## Accepted honesty boundary

This goal must not overclaim RT-core maturity for `segment_polygon_hitcount`.

If a backend is correct only through a fallback or local-oracle path, the final
package must say that directly.

## Accepted package shape

- one goal report
- one machine-readable artifact bundle
- one explicit backend-status conclusion covering:
  - Python oracle
  - native CPU oracle
  - Embree
  - OptiX
  - Vulkan
