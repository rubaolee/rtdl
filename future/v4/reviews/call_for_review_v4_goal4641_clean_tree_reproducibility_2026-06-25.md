# Call For Review: V4 Goal4641 Clean-Tree Reproducibility Gate

Requested reviewer: Claude or Antigravity.

Requested verdict labels:

- `approve_goal4641_clean_tree_reproducibility_continue_goal4642`
- `approve_with_required_amendments_before_goal4642`
- `reject_goal4641_clean_tree_reproducibility_incomplete_or_overclaimed`

## Review Scope

Goal4641 is the clean-tree reproducibility gate for formal V4 release
hardening. It does not authorize final release. It asks whether the current V4
package can run from a committed clean checkout, without relying on untracked
files in the main working tree.

## Files To Review

- `future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md`
- `src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py`
- `tests/v4_goal4641_clean_tree_reproducibility_test.py`
- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4632_release_decision_test.py`
- `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`
- `scripts/v4_catalog_regression_gate.py`
- `examples/v4/v4_frontdoor_quickstart.py`

## Evidence To Check

Clean worktree:

- `C:/Users/Lestat/Desktop/work/rtdl_v4_goal4641_clean_tree_check`

Validated commit recorded in the evidence:

- `35d04dbf0b1734e7c1fc323c366a046de51edee8`

Recorded local verification:

- clean worktree `git status --short`: empty before validation;
- clean worktree full V4 test group: `165 tests OK`;
- clean worktree catalog dry-run: passed, `example_count: 11`,
  `failed_examples: []`;
- clean worktree quickstart: passed with `status: ok`;
- clean worktree `git status --short`: empty after validation;
- local post-edit V4 test group: `168 tests OK`.

Important integrity note:

- The first clean-tree attempt failed because a current V4 AABB gate dependency,
  `scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`, had been left out of
  the committed package. The dependency was then added to the committed state,
  and the clean-tree validation passed. Please verify that this is recorded as a
  useful defect catch, not hidden.

## Questions

1. Does Goal4641 actually prove committed clean-tree reproducibility for the V4
   release-hardening package?
2. Is it acceptable that the evidence records the clean validation commit
   `35d04dbf...`, while the Goal4641 evidence file itself is added after that
   validation, assuming the local and later clean gates pass?
3. Did the release decision correctly remove
   `goal4641_clean_tree_reproducibility_gate_not_done` while preserving final
   3-AI authorization as a blocker?
4. Did Goal4641 avoid broad release, broad speedup, whole-app speedup,
   true-zero-copy, Tier-3 callback, CuPy, C ABI, embedding, and non-Python host
   overclaims?
5. Are any amendments required before Goal4642 final 3-AI authorization?

## Non-Authorization Boundary

Do not authorize final V4 release, release-candidate wording, broad V4 speedup
wording, whole-application speedup wording, public true-zero-copy wording,
Tier-3 callback support, raw OptiX callback support, CuPy performance wording,
C ABI, embedding, non-Python host bindings, or app-specific native kernels.
