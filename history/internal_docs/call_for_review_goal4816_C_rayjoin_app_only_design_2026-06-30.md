# Call For Review: Goal4816-C RayJoin App-Only Reproduction Design

Date: 2026-06-30

Review target:

`history/internal_docs/goal4816_C_rayjoin_app_only_reproduction_design_2026-06-30.md`

Prior gates:

- `history/internal_docs/antigravity_goal4816_A_contract_extraction_review_2026-06-30.md`
- `history/internal_docs/antigravity_goal4816_B_capability_map_review_2026-06-30.md`

## Requested Verdict Labels

Use one of:

- `approve_goal4816_C_app_only_design_authorize_4816_D`;
- `approve_with_required_amendments_before_4816_D`;
- `block_goal4816_C_redo_design`;
- `block_goal4816_line_due_to_user_mode_capability_gap`.

## Review Questions

1. Does the design correctly enforce the role constraint that the agent is an
   RTDL user/application author, not an RTDL developer?
2. Does it prohibit modifications to `src/rtdsl/**`, `src/native/**`, and the
   v2.14 release surface?
3. Does it correctly split `bundled_helper_bounded_available_input_reproduction_not_generic`
   from `generic_primitive_numba_attempt`?
4. Does Route 1 honestly label `rayjoin_overlay` and private helper use as
   bundled-helper evidence, not generic user-language reproduction?
5. Does Route 2 use released RTDL assets and Numba continuation in a plausible
   user-mode way without private helper laundering?
6. Does Route 2 correctly identify the clean generic row/coordinate output
   problem as a possible `missing_v2_14_capability` rather than patching RTDL?
7. Does the design correctly preserve the unresolved author-reply PIP
   `t_reported` determinism contract?
8. Are the correctness gates sufficient before any POD performance run?
9. Does the design avoid treating scalar LSI/PIP counts or Numba compact-mask
   continuations as full Section 5.7 polygon overlay?
10. Should Goal4816-D be authorized as a correctness smoke/preflight plan, or
    must Goal4816-C be amended first?

## Non-Authorization Boundaries

This review must not authorize:

- modifying RTDL runtime/native/release code;
- running POD performance experiments;
- using private helpers as generic user APIs;
- claiming full 8/8 Section 5.7 reproduction;
- claiming bundled-helper evidence as generic RTDL language evidence.

## Expected Reviewer Output

Please provide:

- one verdict label;
- P0/P1/P2 findings;
- answers to the ten questions;
- explicit statement whether Goal4816-D is authorized;
- explicit non-authorization block.
