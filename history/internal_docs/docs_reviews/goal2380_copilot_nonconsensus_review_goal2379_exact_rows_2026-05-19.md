# Goal2380 Copilot Non-Consensus Review: Goal2379 Exact Rows

Date: 2026-05-19

Reviewer: GitHub Copilot CLI.

Consensus status: non-consensus sanity review only. This review does not replace
Claude or Gemini for strict RTDL consensus because Copilot is treated as a
useful auxiliary reviewer, not as one of the required distinct external AI
families.

## Verdict

`accept-with-boundary`

## Summary

Copilot accepted the Goal2379 direction with boundary:

- The intended ABI is app-agnostic.
- The Python API keeps `run_raw(...)` and adds explicit `run_exact_raw(...)` /
  `--result-mode exact-raw`.
- The claim boundary is appropriately constrained: no ranked-K, no RTNN
  paper-equivalence, and no RT-core claim.
- The report should include numeric pod metrics and explicit ABI layout details.
- Struct layout should be guarded with offset/size assertions.

## Follow-Up Applied

After the Copilot sanity review, the Goal2379 report was updated with an ABI
layout table for `RtdlFixedRadiusNeighborRow`. The native header already
contains `static_assert` checks for field offsets and total size, and the report
already includes the pod timing table showing `exact_refine == 0.0` and the
measured speedups over Goal2371 old prepared rows.

## Boundary

This review supports continuing local development, but it does not satisfy the
project's strict Claude/Gemini consensus rule for important claims or release
decisions. A fresh Claude or Gemini review remains pending when those tools are
available.
