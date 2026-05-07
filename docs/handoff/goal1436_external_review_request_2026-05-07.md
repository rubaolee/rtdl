# Goal 1436 External Review Request

Please review the current uncommitted Goal1436 patch in this repository.

## Scope

Goal1436 hardens the v1.5.1 `COLLECT_K_BOUNDED` release-surface proposal false flags. A prior Claude review noted that the proposal blocked whole-app speedup claims through text and forbidden wording, but did not carry a matching explicit proposal-level false flag. This patch adds `whole_app_speedup_claim_authorized_by_this_proposal: False` and validates it.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1419_v1_5_1_collect_k_release_surface_proposal_test.py`
- `tests/goal1436_v1_5_1_collect_k_release_surface_proposal_false_flags_test.py`
- `docs/reports/goal1436_v1_5_1_collect_k_release_surface_proposal_false_flag_hardening_2026-05-07.md`

## Validation

Windows focused slice:

```text
Ran 19 tests in 0.018s
OK
```

Linux GPU pod focused slice with the OptiX environment loaded:

```text
Ran 19 tests in 0.240s
OK
```

`git diff --check` passed with only expected Windows LF-to-CRLF warnings.

## Review Questions

1. Does this patch correctly make whole-app speedup claim blocking explicit at the release-surface proposal layer?
2. Does it avoid authorizing public docs changes, stable promotion, speedup wording, zero-copy wording, whole-app claims, release tags, or release action?
3. Are there any blockers that should prevent committing this hardening patch?

Please answer with `ACCEPT`, `ACCEPT WITH NOTES`, or `REJECT`, and list any precise blockers if rejected.
