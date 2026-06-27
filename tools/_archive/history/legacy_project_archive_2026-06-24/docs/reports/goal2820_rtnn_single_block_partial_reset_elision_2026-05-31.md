# Goal2820 Single Block-Partial Reset Elision

Date: 2026-05-31

Verdict: accept-with-boundary as a correctness-preserving cleanup; neutral single-request performance evidence.

Goal2820 targets the single-request small-row overhead left after Goal2819.
Inspection found a generic inefficiency in the prepared-query ranked-summary
aggregate path: when the runtime chose the block-partial aggregate mode, it
still reset the prepared-handle aggregate workspace even though the block-
partial path writes and downloads per-block partials from the prepared-query
handle and returns before using that workspace.

The change moves the aggregate-workspace reset below the block-partial early
return. Direct and two-step aggregate paths still reset and reuse the prepared
aggregate workspace exactly as before. Clean RTX A5000 pod evidence shows this
cleanup is not the next meaningful single-request performance lever: the 32K
row is slightly slower within run noise and the 65K row is essentially
unchanged versus Goal2819.

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
- This is internal RTNN-v2.5 optimization evidence only. It authorizes the
  narrower engineering conclusion that unused aggregate-workspace reset elision
  is correct but not a material single-request speedup.

## Pod Evidence

Artifacts are saved under
`docs/reports/goal2820_rtnn_single_block_partial_reset_elision_pod/`.

| Row | Goal2819 single median sec | Goal2820 median sec | Change |
| --- | ---: | ---: | ---: |
| uniform 32K | 0.000070732 | 0.000073352 | 0.964x |
| uniform 65K | 0.000127490 | 0.000127328 | 1.001x |

Environment:

- GPU: NVIDIA RTX A5000, driver 570.211.01.
- Source commit: `827b076644146d29c4aac8b8f36c0945f59b74ba`.
- Source dirty state: `[]`.
- Focused tests: 17 passed.

## Interpretation

The negative/neutral result is useful. It says the single-request small-row
overhead is now dominated by the remaining kernel launch, row download, and
device/host orchestration path rather than this unused workspace reset. The
next useful v2.5 work should stay at the generic runtime level: larger grouped
device-resident reductions, event-ordered cross-stream handoff, or a stronger
consumer path that avoids host scalar synchronization.
