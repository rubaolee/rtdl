# Goal4635 Component-Union Promotion Review Debt

Status: `goal4635_local_gate_and_catalog_update_complete_external_review_debt_open_not_release`

## What Completed Locally

Goal4635 POD gate passed on the RTX A5000 POD after installing the missing
Embree control dependencies.

Evidence:

- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/README.md`

Key result:

- failed checks: `0`
- runner vs Embree hot speedup: `1.3930791165731065x`
- runner vs Embree wall speedup: `1.6001250028719352x`
- runner vs legacy OptiX wall speedup: `1.2080037787208602x`
- canonical component signatures matched across all variants

Code/docs/tests updated:

- `src/rtdsl/v4_goal4635_component_union_promotion_decision.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_coverage_audit.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4.py`
- `future/v4/v4_goal4635_component_union_promotion_decision_2026-06-25.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `tests/v4_goal4635_component_union_target_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_goal4627_coverage_audit_test.py`
- `tests/v4_goal4632_release_decision_test.py`
- `tests/v4_frontdoor_test.py`

Verification:

- focused related tests: `30` tests passed
- broad V4 gate: `86` tests passed
- catalog regression dry-run gate passed and wrote:
  - `future/v4/evidence/v4_goal4635_catalog_regression_gate_after_component_union_2026-06-25.json`
  - `future/v4/evidence/v4_goal4635_catalog_regression_gate_after_component_union_2026-06-25.md`

## External Review Attempts

Claude attempt:

- command timed out after approximately four minutes
- stdout file: `future/v4/reviews/claude_v4_goal4635_component_union_promotion_review_2026-06-25.raw.md`
- stderr file: `future/v4/reviews/claude_v4_goal4635_component_union_promotion_review_2026-06-25.stderr.txt`
- both files were empty when inspected

Antigravity attempt:

- command exited `0`
- stdout file: `future/v4/reviews/antigravity_v4_goal4635_component_union_promotion_review_2026-06-25.raw.md`
- stderr file: `future/v4/reviews/antigravity_v4_goal4635_component_union_promotion_review_2026-06-25.stderr.txt`
- both files were empty when inspected

## Debt

Goal4635 cannot be marked 3-AI complete yet.

Required external review target:

- `future/v4/reviews/call_for_review_v4_goal4635_component_union_promotion_decision_2026-06-25.md`

Acceptable closure labels:

- `accept_goal4635_component_union_promotion_not_release`
- `accept_with_required_amendments`

Blocking/rejecting labels:

- `reject_promotion_keep_partial`
- `blocked_need_more_evidence`

## Non-Authorization

This debt record does not authorize:

- V4 release
- V4 release candidate
- broad V4 speedup wording
- whole-application speedup wording
- all-benchmark speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy component-union performance
- Torch component-union performance
- C ABI / embedding / non-Python host claims
- application-specific native kernels
