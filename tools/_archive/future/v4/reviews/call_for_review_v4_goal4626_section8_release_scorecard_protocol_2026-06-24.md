# Call For Review: V4 Goal4626 Section 8 Release Scorecard Protocol

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4626_scorecard_protocol`
- `accept_with_required_amendments`
- `reject_goal4626_scorecard_misleading_or_incomplete`

## Review Request

Please critically review:

- `future/v4/v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md`

Focused test:

- `py -m unittest tests.v4_goal4626_section8_scorecard_protocol_test`
- Result: `OK`, 3 tests

## Context

Goal4625 was amended after review caught a stale mistake: fixed-radius Section 8
work was already completed for one bounded primitive. Goal4626 now freezes that
truth instead of rerunning fixed-radius.

The protocol records four fixed-radius evidence steps:

1. original whole-call Section 8 route: strict gate failed
2. prepared hot-path revision: passed with 1.655x, 1.772x, 1.970x
3. Route D hand-written OptiX ceiling: acquired; old product path was
   192x-1140x slower
4. Torch device-array front door: accepted; gap reduction 1022.93x, 3841.66x,
   and 9699.17x

The protocol then freezes gates G1-G7:

- G1 fixed-radius anchor
- G2 operator coverage audit (`goal4627`)
- G3 second Tier-2 same-contract gate (`goal4628`)
- G4 weighted-sum candidate decision (`goal4629`)
- G5 push-down recognizer (`goal4630`)
- G6 Tier-3 boundary/execution (`goal4631`)
- G7 final release decision (`goal4632`)

## Questions

1. Does Goal4626 correctly treat fixed-radius as completed for one bounded
   primitive, not as still unrun?
2. Does it avoid turning fixed-radius into a broad V4 performance-release claim?
3. Are gates G1-G7 sufficient and ordered correctly for the remaining V4 work?
4. Are the second Tier-2 gate rules strong enough to prevent toy or
   non-comparable measurements?
5. Does the non-authorization block preserve release, broad speedup, CuPy,
   Tier-3, raw callback, true-zero-copy, C ABI, and app-specific-kernel
   boundaries?
6. What amendments are required before Goal4626 can be marked complete?

## Non-Authorization

This review request does not authorize:

- V4 release
- V4 release-candidate status
- public broad speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
