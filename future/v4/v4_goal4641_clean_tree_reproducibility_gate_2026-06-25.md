# V4 Goal4641 Clean-Tree Reproducibility Gate

Status: complete pending external review.

Decision label:

`complete_clean_tree_reproducibility_gate_pending_external_review`

## Purpose

Goal4641 proves that the V4 release-hardening state can run from a committed,
clean checkout. This is the guard against a fake release that only works because
the main working tree contains untracked local files.

This goal does not authorize final V4 release. It closes the clean-tree blocker
so Goal4642 can request final 3-AI release authorization.

## Clean Worktree

Clean worktree path:

`C:/Users/Lestat/Desktop/work/rtdl_v4_goal4641_clean_tree_check`

Validated commit:

`35d04dbf0b1734e7c1fc323c366a046de51edee8`

The clean worktree was checked out detached at that commit. `git status --short`
was empty before validation and empty again after validation.

## Important Catch

The first clean-tree attempt failed one V4 AABB test because
`scripts/v3_0_m30_librts_prepared_all_ops_refresh.py` had been left out of the
committed V4 package. Even though the filename is historical, the script is a
current V4 AABB gate dependency.

That missing dependency was fixed by adding the script to the committed V4
release-hardening state and amending the Goal4640 commit. The clean-tree gate
then passed. This is exactly the kind of defect Goal4641 is meant to catch.

## Verification Commands

Full V4 test group from clean worktree:

```text
$env:PYTHONPATH='src;.'
$env:PYTHONDONTWRITEBYTECODE='1'
$mods = Get-ChildItem tests\v4*_test.py | ForEach-Object { 'tests.' + $_.BaseName }
py -3 -m unittest $mods
```

Result:

```text
Ran 165 tests in 28.164s
OK
```

Catalog dry-run from clean worktree:

```text
$env:PYTHONPATH='src;.'
$env:PYTHONDONTWRITEBYTECODE='1'
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16
```

Result:

```text
status: passed
git_commit: 35d04dbf0b1734e7c1fc323c366a046de51edee8
example_count: 11
failed_examples: []
release_authorized: false
broad_v4_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
```

Quickstart from clean worktree:

```text
$env:PYTHONPATH='src;.'
$env:PYTHONDONTWRITEBYTECODE='1'
py -3 examples\v4\v4_frontdoor_quickstart.py
```

Result:

```text
status: ok
front_door_status: v4_scorecard_passed_front_door_pending_final_authorization
measured_surface_count: 8
candidate_surface_count: 0
release_claim_authorized: false
whole_app_speedup_claim_authorized: false
true_zero_copy_authorized: false
tier3_callback_claim_authorized: false
```

Post-validation status:

```text
git status --short
```

Result:

```text
<empty>
```

## Machine-Readable Updates

- `src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py` records the
  Goal4641 decision and non-authorization flags.
- `tests/v4_goal4641_clean_tree_reproducibility_test.py` fixes the clean-tree
  evidence as a regression gate.
- `src/rtdsl/v4_release_decision.py` now records Goal4641 as a passed gate and
  removes `goal4641_clean_tree_reproducibility_gate_not_done` from release
  blockers.

## Remaining Release Blockers

- Goal4642 final 3-AI release authorization is not done.
- Goal4641 external review is pending or debt.
- Existing review debts that were deliberately carried through Goal4640 remain
  visible until final authorization or explicit closure.

## Goal-Level Decision Audit

Was I stupid?

No for this goal. I did the correct uncomfortable check: run the release package
from a clean worktree instead of trusting the dirty main working tree.

If yes, what actions made the decision stupid?

Not applicable. The first failure was useful, not stupid: it exposed a real
missing dependency in the committed V4 package.

Was there another possibility that avoids getting stuck on a bad path?

Yes. The bad path would have been to ignore the clean-tree failure because the
file had a `v3_` prefix. I did the opposite: treated it as a current V4
dependency because the V4 AABB gate imports it.

Can I start a different path that actually solves the problem?

Yes. The next path is Goal4642 final authorization. Goal4641 should not expand
into more cleanup work unless external review finds a concrete reproducibility
defect.

## Non-Authorization

This Goal4641 decision does not authorize final V4 release, release-candidate
wording, broad V4 speedup wording, whole-application speedup wording, public
true-zero-copy wording, Tier-3 callback support, raw OptiX callback support,
CuPy performance wording, C ABI, embedding, non-Python host bindings, or
app-specific native kernels.
