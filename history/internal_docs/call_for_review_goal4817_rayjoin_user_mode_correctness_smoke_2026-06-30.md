# Call For Review — Goal4817 RayJoin User-Mode Correctness Smoke

Date: 2026-06-30

Please review:

`history/internal_docs/goal4817_rayjoin_user_mode_correctness_smoke_execution_2026-06-30.md`

Supporting artifacts:

`history/internal_docs/goal4817_artifacts_2026-06-30/`

## Current Review State

An Antigravity CLI review was attempted from the local workspace on
2026-06-30, but the process produced no output for several minutes and was
stopped. No review verdict was obtained from that attempt. Goal4817 therefore
remains `pending_external_review`; this file is the active review request.

## Requested Verdict Labels

Use one:

- `approve_goal4817_smoke_complete_authorize_4818_gap_diagnosis`
- `approve_with_required_amendments`
- `fail_redo_goal4817`
- `block_due_to_runtime_edit_or_misclassification`

## Review Questions

1. Did Goal4817 remain in RTDL user/application-author mode?
2. Did it avoid all edits to `src/rtdsl/**`, `src/native/**`, and the release
   surface?
3. Is the clean checkout evidence sufficient?
4. Is building `build/librtdl_optix.so` from the clean checkout an acceptable
   user install/build step rather than a runtime modification?
5. Is the tiny fixture route smoke correctly labeled as not Section 5.7 and not
   performance evidence?
6. Is the generic+Numba probe correctly framed as blocked/unproven rather than
   a generic reproduction?
7. Is the author public-sample bundled-helper mismatch correctly treated as a
   correctness failure/gap rather than a success?
8. Does the author binary health check prove the author sample answer is valid
   in the current POD environment?
9. Is the equal-ties environment-knob result correctly interpreted as
   insufficient for the author-reply slope-dependent `t_reported` rule?
10. Should Goal4818 be authorized as a user-mode correctness-gap diagnosis, with
    no performance runs and no RTDL edits?

## Non-Authorization Reminder

This review must not authorize:

- performance benchmarking;
- Section 5.7 full reproduction claims;
- generic RTDL+Numba reproduction claims;
- runtime/native/source modifications;
- public release wording changes.
