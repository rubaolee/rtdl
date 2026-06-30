# Goal2582 LibRTS Internal Publish Consensus

Date: 2026-05-24

## Verdict

**ACCEPT for internal online publication.**

This consensus covers the LibRTS-style spatial-index benchmark slice after
Goal2581. It authorizes committing and pushing the internal benchmark app,
reports, tests, and generic RTDL `AABB_INDEX_QUERY_2D` runtime/native support.

It does not authorize broad public speedup wording.

## Review Inputs

- Codex implementation and validation in this working tree.
- Claude review:
  `docs/reports/goal2582_librts_internal_publish_claude_review_2026-05-24.md`
- Gemini review:
  `docs/reports/goal2582_librts_internal_publish_gemini_review_2026-05-24.md`

Both external reviews returned **ACCEPT** with no blocking issues.

## Agreed Scope

The publishable slice includes:

- LibRTS-style benchmark app under
  `examples/v2_0/research_benchmarks/librts_spatial_index/`.
- Authors-code evidence and RTDL OptiX evidence reports from Goal2574 through
  Goal2581.
- Generic `AABB_INDEX_QUERY_2D` CPU/reference and OptiX runtime support.
- Native OptiX count-only support for:
  `point_contains`, `range_contains`, and `range_intersects`.
- Tests covering generic primitive contracts, app-agnostic native symbols, pod
  evidence metadata, and report claim boundaries.

## Consensus Findings

- The native engine remains app-agnostic for this slice. Native symbols and
  kernels are expressed as generic AABB-index operations, not `LibRTS` symbols.
- The `range_intersects` path uses a generic two-pass diagonal/anti-diagonal
  traversal with exact segment-box refinement and duplicate suppression.
- Prepared query buffers are part of the runtime contract and are necessary for
  fair steady-state query timing.
- The recorded pod evidence is sufficient for internal benchmark publication:
  CPU/OptiX correctness was checked on small fixtures, and prepared-query
  paper-like fixture counts match authors-code evidence for 10k/100k/1M rows.
- The reports keep the required boundary: generated paper-like fixtures,
  count-only paths, prepared-query latency, and no broad public speedup claim.

## Nonblocking Follow-Ups

- `OptixAabbIndex2D` should be exported for users who want to type-annotate the
  high-level prepared wrapper returned by `prepare_aabb_index_2d(backend="optix")`.
  This was addressed before publication.
- Float32 truncation in the OptiX path remains a general RTDL native-backend
  boundary; future reports should mention it when large-coordinate datasets are
  introduced.
- Mutable update performance remains outside the RTDL native path for this
  slice.

## Required Wording Boundary

Use this wording for any public-facing mention:

> Generic OptiX `AABB_INDEX_QUERY_2D` count-only subpath; not LibRTS-specific,
> not exact paper artifact datasets, and not authorized for broad public
> speedup claims without further consensus review. Timing rows reflect
> prepared-query latency; scene preparation and query-buffer upload are separate
> phases.
