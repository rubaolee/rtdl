# Codex Review: Goal 97 Ray-Hit Sorting

Date: 2026-04-05
Reviewer: Codex
Verdict: APPROVE-WITH-NOTES

## Findings

The implemented Goal 97 slice is technically sound as a first RTDL
non-join/capability test.

Strong points:

- it reuses an existing mature RTDL workload family (`lsi`) instead of
  introducing a special-case primitive
- the implemented offset construction correctly fixes the `x = 0` degeneracy in
  the original literal geometric idea
- duplicate handling is explicit and deterministic through `original_index`
- the verification stack is good:
  - direct formula
  - stable Python sort
  - quicksort-style reference

Notes:

- this is not yet a published cross-backend result; the local package is still
  limited by current Mac native/backend availability
- the current strongest accepted status is “implemented locally,” not “backend
  closure”

## Agreement and Disagreement

Agreements:

- the accepted scope should stay at nonnegative integers for the first round
- correctness and portability should be the primary claim, not performance
- the sorted output should be derived from `(value, hit_count, original_index)`
  rather than pretending duplicates vanish

No substantive disagreement with the current implementation direction.

## Recommended next step

Run Goal 97 on the available Linux backends, then package a small accepted
backend-parity closure with 2+ AI consensus before publish.
