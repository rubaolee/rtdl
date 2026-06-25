---

**`accept_with_required_amendments`**

---

## Findings

**What holds up:**

- Fixed-radius is correctly frozen as `pass_bounded_one_primitive`. The purpose section explicitly targets the "rerunning" failure mode, and G1's status leaves no ambiguity.
- The `goal4626_protocol_current_not_release` status label is clear and is the first substantive token in the document.
- All four evidence files and all three review files cited in the evidence chain exist on disk.
- Key numbers verified against sources: 1.655x/1.772x/1.970x match the prepared hot-path report; 1022.93x/3841.66x/9699.17x match the device-array frontdoor report; 192.64x (smallest) and 1140.11x (largest summary) are the actual row values behind "192x-1140x."
- G1-G7 ordering is logically sound: G2 selects the operator, G3 tests it, G4 resolves candidate status, G5 builds routing, G6 is explicitly conditioned on all gates passing plus a later review.
- Second Tier-2 gate rules are specific: generic operator required, serious sizes, same RT hardware, correctness parity, Python row objects excluded from hot path, win source must be attributed, fail-closed clause present.
- Non-authorization block covers all ten items required by the call for review in both the "Claim Boundary" section and the closing "Non-Authorization" section.

---

**Required amendment — one:**

The Step 4 evidence citation omits `future/v4/reviews/claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md`. That closure document is part of the completed chain: it verifies four amendments to the frontdoor report and records the binding constraint `authorized_next_step = external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive`.

The consequence is that the G3 row in the scorecard says only `missing; this is goal4628` with no sequencing prerequisite. Under the amendment closure, Goal4628 may not proceed until the fixed-radius API wrapper is productized. That pre-condition is absent from the scorecard. A reader following the scorecard forward could launch Goal4628 before the wrapper work is done, which the amendment closure explicitly prohibits.

**Required changes:**
1. Add the amendment closure as a fourth citation under Step 4 of the evidence chain.
2. Add a prerequisite clause to the G3 row: the fixed-radius device-array API wrapper must be productized (per the amendment closure constraint) before Goal4628 can be initiated.

---

**Observation (not blocking):**

The test file's `test_protocol_preserves_non_authorization_boundary` checks 8 of the 10 non-authorization items from the call for review. "whole-application speedup wording" and "true-zero-copy public wording" are both present in the protocol document but not asserted by the test. This is a test-coverage gap, not a protocol gap — the document is correct — but tightening the test would lock in those two strings.
