# Goal5058 - v2.14.4 Review Debt Content Gate

Date: 2026-07-06

Status:

```text
completed_review_debt_content_gate__external_review_still_pending
```

## Purpose

Goal5058 hardens the v2.14.4 release preflight so that review debt cannot be
retired by an empty or placeholder file whose name merely matches
`*review*goalNNNN*.md`.

This matters because the release preflight is now the authoritative gate after
POD runtime debt was retired.  The remaining blocker is review debt, so the
review check must not be satisfied by a filename alone.

## Change

`scripts/goal5053_v2144_release_preflight.py` now validates review file content
shape:

```text
must not be call_for_review_*
must contain verdict or verdict_label
must contain at least one decision word:
  approve / pass / revise / fail / block
```

Files that match the glob but fail this content check are reported under:

```text
external_review_debt.malformed
```

and do not retire the corresponding review debt.

## Verification

Command:

```powershell
$env:PYTHONPATH='src'; py -3 -m unittest tests.goal5053_v2144_release_preflight_test
```

Result:

```text
pending
```

## Claim Boundary

Authorized:

```text
review_debt_content_gate_added
placeholder_review_files_do_not_retire_debt
```

Not authorized:

```text
review_debt_retired
public_release_ready
v2_14_4_speedup_claim
true_zero_copy_claim
author_parity_claim
device_group_by_public_ready
```

## Exit Label

```text
completed_review_debt_content_gate__external_review_still_pending
```
