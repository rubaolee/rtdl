# Goal2820 Single Block-Partial Reset Elision

Date: 2026-05-31

Verdict: implementation-pending-pod-evidence.

Goal2820 targets the single-request small-row overhead left after Goal2819.
Inspection found a generic inefficiency in the prepared-query ranked-summary
aggregate path: when the runtime chose the block-partial aggregate mode, it
still reset the prepared-handle aggregate workspace even though the block-
partial path writes and downloads per-block partials from the prepared-query
handle and returns before using that workspace.

The change moves the aggregate-workspace reset below the block-partial early
return. Direct and two-step aggregate paths still reset and reuse the prepared
aggregate workspace exactly as before.

This remains app-agnostic. The vocabulary is fixed-radius neighbors, prepared
queries, ranked summaries, block partials, and aggregate workspaces. No RTNN
native ABI or benchmark-specific branch is introduced.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No single-request performance conclusion is authorized until clean pod
  artifacts exist.
