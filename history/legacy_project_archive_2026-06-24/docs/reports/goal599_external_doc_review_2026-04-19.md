# Goal599 External Doc Review

Date: 2026-04-19

## Verdict

ACCEPT.

## Review Notes

The v0.9.2 Apple RT public documentation has been thoroughly reviewed and found to be current, consistent, and honestly bounded.

Specific verifications:
1. **Current Versioning:** The docs correctly identify `v0.9.1` as the released closest-hit slice and `v0.9.2` as the current candidate line carrying the Apple RT full-surface dispatch and native-slice performance work.
2. **Apple RT Reality:** The documentation accurately reflects that Apple RT utilizes real Apple Metal/MPS RT for the native slices (3D closest-hit, 3D hit-count, and 2D segment-intersection), while explicitly noting that other workloads fallback to `cpu_reference_compat`.
3. **Honesty Boundaries:** The performance boundaries are correctly and consistently maintained. The docs explicitly state that Apple RT is not a broad speedup claim, acknowledging that Embree remains faster on current hit-count and segment-intersection fixtures. Embree continues to be correctly identified as the only broadly mature/optimized backend.
4. **Stale Phrases:** All identified stale phrases from post-v0.9.1 have been successfully scrubbed and replaced with accurate v0.9.2 descriptions.

The refresh successfully presents a coherent and transparent Apple RT story for new and existing users.
