# Handoff: Goal3224 Claude Review of RayJoin Harness Hardening

Please perform a read-only independent Claude review of Goals 3222 and 3223.

## Expected Output

Write the review to:

`docs/reviews/goal3224_claude_review_goal3222_3223_rayjoin_harness_hardening_2026-06-03.md`

Use one of the accepted verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Scope

Goal3222 closes the remaining kernel-patch stability debt from the fused
segment-pair left-id count chain by adding a static guard around the canonical
OptiX kernel snippets and the generated dense-count replacement.

Goal3223 intakes your Goal3221 review findings for the Goal3220 current-best
Spatial RayJoin count/parity harness:

- L1: hardware metadata was weaker than Goal3218 standard,
- L2: `overlay_seed` used a zero-count fixture, making parity weak.

Goal3223 hardens both by adding v2 metadata fields, a per-workload dataset
policy, a nonzero overlay default, and a corrected overlay active-seed count
contract. It records a fresh NVIDIA A40 pod artifact with PIP 6/6, LSI 1/1, and
overlay_seed 64/64.

## Files to Inspect

- `tests/goal3222_segment_pair_count_kernel_patch_stability_test.py`
- `docs/reports/goal3222_segment_pair_count_kernel_patch_stability_guard_2026-06-03.md`
- `scripts/goal3220_spatial_rayjoin_current_best_count_harness.py`
- `tests/goal3220_spatial_rayjoin_current_best_count_harness_test.py`
- `docs/reports/goal3223_claude_review_intake_current_best_rayjoin_harness_2026-06-03.md`
- `docs/reports/goal3223_spatial_rayjoin_current_best_count_harness_2026-06-03.json`
- `docs/reports/goal3223_spatial_rayjoin_current_best_count_harness_2026-06-03.stdout`
- `tests/goal3223_current_best_rayjoin_harness_review_intake_test.py`
- Prior reviews:
  - `docs/reviews/goal3214_claude_review_fused_segment_pair_count_chain_2026-06-03.md`
  - `docs/reviews/goal3219_claude_review_goal3218_rayjoin_public_lsi_dense_probe_2026-06-03.md`
  - `docs/reviews/goal3221_claude_review_goal3220_current_best_rayjoin_count_harness_2026-06-03.md`

## Review Questions

1. Does Goal3222 materially narrow the kernel string-patch stability risk by
   catching snippet drift in ordinary unit tests before pod runtime compilation?
2. Does Goal3222 avoid overclaiming that the string-patch construction has been
   eliminated?
3. Does Goal3223 correctly close your Goal3221 L1 metadata finding by recording
   `cuda_driver_query`, `nvcc_version`, and `rtdl_optix_library`?
4. Does Goal3223 correctly close your Goal3221 L2 weak-overlay finding with a
   nonzero overlay default and an active-seed count contract?
5. Is the first failed v2 pod run interpreted correctly as a useful discovery of
   a count-contract mismatch, not as a native OptiX failure?
6. Do the reports/tests preserve the app-agnostic native boundary and keep all
   prohibited claim boundaries false?
7. What remains before stronger RayJoin benchmark, public speedup, release,
   true zero-copy, or paper-reproduction claims?

## Boundaries

This is a read-only review. Do not edit source files, reports, artifacts, or
tests other than writing the requested review file.

The expected position is that Goals 3222 and 3223 are internal hardening and
planning evidence only. They must not authorize release, public speedup claims,
broad RT-core claims, true zero-copy claims, `RTDL beats RayJoin` claims, or
RayJoin paper-reproduction claims.
