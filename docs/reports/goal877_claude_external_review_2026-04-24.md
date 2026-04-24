# Goal877 Claude External Review

- reviewer: `Claude`
- date: `2026-04-24`
- verdict: `ACCEPT_WITH_CAVEATS`

## Review Summary

Claude accepted Goal877 with caveats.

Accepted points:

- The profiler separates `optix_candidate_discovery_sec` from
  `cpu_exact_refinement_sec`.
- `rt_core_accelerated` remains false while
  `rt_core_candidate_discovery_active` records the narrower OptiX slice.
- The manifest keeps both polygon-overlap apps in deferred entries with claim
  scope limited to candidate discovery.
- The boundary text does not authorize full polygon-overlap/Jaccard RTX
  speedup claims.
- Local tests cover dry-run schema, mocked OptiX parity, and manifest
  constraints.

## Caveats Raised

- The original profiler duplicated Jaccard exact-refinement logic instead of
  calling the app's exact refinement path.
- OptiX parity remains mock-only locally; real Linux/RTX execution is still
  required before any performance claim or readiness promotion.

## Follow-Up Applied

The Jaccard app now exposes `_exact_jaccard_rows_for_candidates(...)`, and the
Goal877 profiler calls that helper directly. This removes the implementation
drift risk for the CPU exact-refinement phase.

The real RTX caveat remains intentionally open.
