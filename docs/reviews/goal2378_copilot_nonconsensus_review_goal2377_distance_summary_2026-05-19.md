# Goal2378 Copilot Non-Consensus Review: Goal2377 Distance Summary

Date: 2026-05-19

Reviewer: GitHub Copilot CLI.

Consensus status: non-consensus sanity review only. This review does not replace
Claude or Gemini for strict RTDL consensus because Copilot is treated as a
useful auxiliary reviewer, not as one of the required distinct external AI
families.

## Availability Note

Gemini Flash was attempted first and returned `MODEL_CAPACITY_EXHAUSTED` / 429.
It later left a partial/stale review file with incorrect ABI-layout details and
pre-rerun timing ratios, so that file was rejected and is not counted as
consensus. Claude was attempted next and returned an out-of-extra-usage message
before producing a review file.

## Verdict

`accept-with-boundary`

## Summary

Copilot's read-only sanity review accepted the Goal2377 direction with the same
boundary used in the handoff:

- The exported surface must remain generic and avoid RTNN-branded identifiers.
- The Python runtime and benchmark runner should verify the full
  `--result-mode summary` path.
- The evidence boundary should stay narrow: this is a measured continuation,
  not a witness-row replacement or RTNN paper-equivalence claim.
- The pod artifacts should show no row download and no host exact-refine.
- The C++/CUDA host-device summary layout should be explicitly guarded.

## Follow-Up Applied

The layout concern was addressed after the Copilot review by adding native
`static_assert` checks for `RtdlFixedRadiusNeighborSummary`:

- `sizeof(size_t) == 8`
- `sizeof(RtdlFixedRadiusNeighborSummary) == 32`
- expected `offsetof` values for `count`, `min_distance`, `max_distance`, and
  `sum_distance`

The focused Goal2377/2375/2371/2348 test slice was rerun after this change and
passed.

## Boundary

This review supports continuing local development, but it does not satisfy the
project's strict Claude/Gemini consensus rule for important claims or release
decisions. A fresh Claude or Gemini review remains pending when those tools are
available.
