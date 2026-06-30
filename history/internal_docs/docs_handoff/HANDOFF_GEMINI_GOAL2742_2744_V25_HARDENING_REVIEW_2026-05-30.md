# Handoff: Gemini Review For Goals2742-2744 v2.5 Hardening

Please perform a read-only independent review of Goals2742, 2743, and 2744.

## Context

RTDL v2.5 is hardening the generic device-resident hit-stream handoff and typed
primitive payload column design. Goal2740 added a cross-partner transfer plan
and received a Claude review:

- `docs/reports/goal2740_hit_stream_cross_partner_transfer_plan_2026-05-30.md`
- `docs/reviews/goal2741_claude_review_goal2740_cross_partner_transfer_2026-05-30.md`

After that, Codex implemented three narrow follow-up hardening goals:

- Goal2742: preserve `producer_consumer_stream_ordering` when the OptiX runtime
  rebuilds a hit-stream handoff with extra phase timings.
- Goal2743: make the Triton group-id validation boundary explicit as
  `torch_cuda_precheck_host_scalar_sync`, not a device-resident error-flag path.
- Goal2744: audit the native OptiX hit-stream release entrypoint and Python
  fail-closed release-symbol requirement.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/triton_partner_continuation.py`
- `tests/goal2738_native_hit_stream_stream_ordering_boundary_test.py`
- `tests/goal2743_triton_group_id_validation_boundary_test.py`
- `tests/goal2744_native_hit_stream_release_enforcement_audit_test.py`
- `tests/goal2706_native_optix_hit_stream_device_columns_test.py`
- `docs/reports/goal2742_optix_hit_stream_metadata_preservation_2026-05-30.md`
- `docs/reports/goal2743_triton_group_id_validation_boundary_2026-05-30.md`
- `docs/reports/goal2744_native_hit_stream_release_enforcement_audit_2026-05-30.md`

## Review Questions

1. Does Goal2742 correctly preserve stream-ordering metadata without claiming
   stream synchronization is proven?
2. Does Goal2743 honestly expose Triton's current group-id validation as a
   host-scalar-sync precheck, not a future device-resident error flag?
3. Does Goal2744 correctly classify native release-entrypoint status as
   "present/audited" while keeping broader native lifetime, multi-driver, and
   true-zero-copy claims blocked?
4. Do the tests catch the intended regressions without overfitting to stale
   historical wording?
5. Are public speedup, true-zero-copy, and partner-replacement claim boundaries
   preserved?

## Expected Output

Write your review to:

`docs/reviews/goal2745_gemini_review_goal2742_2744_v25_hardening_2026-05-30.md`

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not modify source code.
