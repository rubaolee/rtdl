# Call For Review: V4 Goal4684 High-Performance Target Reset

Please review:

- `future/v4/v4_goal4684_high_performance_target_reset_2026-06-25.md`
- `src/rtdsl/v4_goal4684_high_performance_target_reset.py`
- `tests/v4_goal4684_high_performance_target_reset_test.py`

Requested verdict labels:

- `accept_goal4684_reset_continue_tier3_wrapper_spike_protocol`
- `reject_goal4684_tier2_target_still_available`
- `accept_with_required_amendments`
- `blocked_insufficient_evidence`

## Questions

1. Is the reset honest: no clean existing Tier-2/app target remains for near-term formal high-performance V4?
2. Are the dispositions for RTDBSCAN, RTNN, shape-pair, contact/witness, aggregate-frontier, and existing app selection accurate?
3. Is Tier-3 wrapper/direct-callable ABI the correct next architecture lever if work continues toward final high-performance V4?
4. Does the document keep Tier-3 as spike-only and avoid public support/release wording?
5. Does Goal4685 correctly avoid repeating the old bare-PTX `optixModuleCreate` probe?
6. Are the non-authorization boundaries complete?

## Non-Authorization

This review must not authorize:

- V4 release;
- public speedup wording;
- whole-app high-performance claims;
- POD spending;
- Tier-3 public support;
- raw OptiX callback support;
- app-specific native kernels;
- C ABI, embedding, true-zero-copy, or non-Python host claims.
