# Call For Review: V4 Goal4683 Contact/Witness Design Audit

Please review `future/v4/v4_goal4683_contact_witness_design_audit_2026-06-25.md` and the machine gate in `src/rtdsl/v4_goal4683_contact_witness_design_audit.py`.

Requested verdict labels:

- `accept_goal4683_no_go_continue_goal4684`
- `reject_goal4683_no_go_target_is_clean_v4_lever`
- `accept_with_required_amendments`
- `blocked_insufficient_evidence`

## Questions

1. Does the evidence support killing `AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D` as a V4.0 high-performance target?
2. Is the key reasoning correct: V2.14 already has bounded collect-k primitives, while current already has exact-witness partner device-column surfaces?
3. Would implementing this target risk rebranding existing V2.14/current work rather than proving a new V4 runtime lever?
4. Does the artifact correctly preserve the app-identity-kernel lock?
5. Is the next step right: Goal4684 should reset target selection around a genuinely absent generic fused primitive or stop the formal high-performance path?
6. Are the non-authorization boundaries complete?

## Non-Authorization

This review must not authorize:

- V4 release;
- public speedup wording;
- whole-app high-performance claims;
- POD spending for this killed target;
- app-specific native kernels;
- partner-migration speed credit;
- C ABI, embedding, true-zero-copy, or non-Python host claims.
