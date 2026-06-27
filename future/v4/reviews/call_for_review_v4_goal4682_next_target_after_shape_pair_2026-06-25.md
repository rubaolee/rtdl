# Call For Review: V4 Goal4682 Next Target After Shape-Pair No-Speed Result

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4682_continue_goal4683_contact_witness_design_audit`
- `reject_goal4682_wrong_next_target`
- `accept_with_required_amendments_before_goal4683`

## Review Target

- Report:
  `future/v4/v4_goal4682_next_target_after_shape_pair_2026-06-25.md`
- Evidence:
  `future/v4/evidence/v4_goal4682_next_target_after_shape_pair_2026-06-25.json`
- Code:
  `src/rtdsl/v4_goal4682_next_target_after_shape_pair.py`
- Tests:
  `tests/v4_goal4682_next_target_after_shape_pair_test.py`

## Questions

1. Is it correct to close shape-pair relation active count as no-promotion after
   Goal4681?
2. Is `AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D` a reasonable next design/audit
   gate, or is it too likely to be V2.14 bounded collect-k rebranded?
3. Is the no-implementation/no-POD boundary strong enough?
4. Should Goal4683 proceed as an audit gate, or should V4 stop and reframe
   before any further high-performance work?

## Non-Authorization To Preserve

This review must not authorize:

- V4 release.
- public speedup wording.
- broad V4-over-V2/V3 claims.
- whole-app high-performance wording.
- measured-catalog promotion for shape-pair relation active count.
- implementation/POD for the contact-witness target.
- app-identity native kernels.
- Tier-3 callbacks or embedding/C ABI work.
