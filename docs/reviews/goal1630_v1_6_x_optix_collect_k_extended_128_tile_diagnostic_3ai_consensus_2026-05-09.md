# Goal1630 v1.6.x OptiX Collect-K Extended 128-Tile Diagnostic 3-AI Consensus

## Verdict

`accepted_as_internal_diagnostic_candidate`

Codex, Claude, and Gemini agree that the opt-in
`RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC` patch is a reasonable
internal diagnostic candidate for extending the experimental OptiX
`COLLECT_K_BOUNDED` row-width-2 tiled path from 64 tile segments to 128 tile
segments.

## Consensus Points

- The default tiled boundary remains `131072` candidates unless the diagnostic
  environment variable is explicitly enabled.
- The extended diagnostic capacity math is consistent: `262144` candidates with
  the 2048-row CUB tile path requires 128 tile segments, and the final compact
  level requires at most 1024 prefix blocks.
- The A4500 evidence shows `262144` candidates using
  `row_width2_bounded_multi_tile_sort_merge` with `tile_count=128` and accepted
  Goal1506 parity.
- The repeats=5 A/B evidence keeps parity and shows the deferred merge-sync
  diagnostic still reducing median native stage total at the extended scale.
- The larger workspace can remain allocated in a long-lived process after the
  diagnostic is disabled. Reviewers agree this is safe as a high-watermark
  pattern but should remain documented as an internal diagnostic constraint.

## Claim Boundary

This consensus accepts Goal1630 as internal v1.6.x diagnostic evidence only. It
does not authorize public speedup wording, true zero-copy wording, stable
`COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup
claims, release tags, or release action.
