# Call For Review — Goal4818 RayJoin Correctness Gap Diagnosis

Date: 2026-06-30

Please review:

`history/internal_docs/goal4818_rayjoin_public_sample_correctness_gap_diagnosis_2026-06-30.md`

Supporting artifacts:

`history/internal_docs/goal4818_artifacts_2026-06-30/`

## Requested Verdict Labels

Use one:

- `approve_goal4818_gap_diagnosis_authorize_closure_packet`
- `approve_with_required_amendments`
- `fail_redo_goal4818`
- `block_due_to_runtime_edit_or_overclaim`

## Review Questions

1. Did Goal4818 remain in RTDL user/application-author mode?
2. Did it avoid all runtime/native/release-surface edits?
3. Does the structure comparison justify saying the mismatch is not formatting
   only?
4. Does the evidence support "six 2-point output chains missing, causing a
   cascade"?
5. Is the LSI count-match evidence sufficient to move suspicion downstream of
   LSI?
6. Is the PIP/SoS contract comparison between author source/reply and RTDL
   native source accurate?
7. Is it correct that `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` does not implement
   the author-reply slope-dependent `t_reported` rule and did not fix the
   mismatch?
8. Should exact author-byte reproduction with released RTDL v2.14 be classified
   as `blocked_by_released_rtdl_pip_sos_contract_gap`?
9. Should performance runs remain blocked until correctness is resolved?
10. Should the next goal be a closure/review packet rather than more execution?

## Non-Authorization Reminder

This review must not authorize:

- performance benchmarking;
- runtime/native/source edits;
- exact reproduction claims;
- generic RTDL+Numba reproduction claims;
- public release wording changes.

