# Goal2851 Barnes-Hut Harness Progress Logging

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

During Goal2847, the Barnes-Hut canonical harness spent about 342 seconds in
the 8,192-body case before printing another line. The process was active, but
the harness looked stuck from the outside. Goal2851 fixes that operational
problem by adding backend/repeat progress messages around the expensive
Embree/OptiX sub-runs.

## Implementation

Updated:

- `scripts/goal2642_barnes_hut_embree_vs_optix_lowering_perf.py`
- `scripts/goal2803_barnes_hut_v25_consolidated_harness.py`

The underlying `run_case(...)` now accepts an optional `progress_callback`.
Goal2803 passes a callback that prints to `sys.__stdout__` with a `stderr`
fallback, which means progress remains visible even while `stdout` is
redirected around the suppressed per-case JSON.

The new messages are shaped like:

```text
[goal2803] membership case 3/3 progress: backend=embree repeat=1/3 start
[goal2803] membership case 3/3 progress: backend=embree repeat=1/3 done sec=...
```

## Boundary

This is not a performance change, not a public speedup claim, and not a release
authorization. It only improves observability for long-running pod harnesses.
The harness output and JSON payload semantics remain unchanged.

## Validation

Local static guard:

```text
py -3 -m unittest tests.goal2851_barnes_hut_harness_progress_logging_test
```

The pod smoke validation should run a tiny Barnes-Hut case and confirm the progress
lines appear before completion while the per-case JSON remains suppressed.

## Codex Verdict

`accept-with-boundary`
