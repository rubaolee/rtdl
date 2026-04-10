# Codex Consensus: Goal 200 Fixed-Radius Neighbors Embree Closure

Date: 2026-04-10
Status: accepted

## Verdict

Goal 200 is complete as a correctness-first Embree closure for
`fixed_radius_neighbors`.

## Findings

- The workload contract remained unchanged:
  - inclusive `distance <= radius`
  - deterministic ordering
  - `k_max` truncation after ordering
- The native Embree path is real, not a fallback:
  - new C ABI row type
  - new Embree point-query collection path
  - new Python runtime dispatch and raw-row support
- One real implementation bug appeared during bring-up:
  - duplicate neighbor emission from repeated user-geometry callbacks
  - fixed by per-query deduplication in the native Embree query state
- The Embree rebuild watcher is now honest for modular native sources:
  - edits under `src/native/embree/` trigger rebuilds
- Verification is strong enough for this goal's scope:
  - Goal 200 slice passes
  - adjacent oracle/Embree parity slice passes

## Review Status

- Claude review: successful and approving
- Gemini review: attempted but did not yield a usable body in this run

Under the standing project bar, this is sufficient for closure:

- Codex consensus
- one real external review

## Summary

Goal 200 moves `fixed_radius_neighbors` from correctness-only CPU/oracle support
to the first accelerated backend closure. The workload is now genuinely usable
through Embree and is ready for the next milestone: external baseline harnesses
and the first benchmark/comparison story.
