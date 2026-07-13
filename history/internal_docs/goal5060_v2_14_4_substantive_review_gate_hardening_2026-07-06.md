# Goal5060 - v2.14.4 Substantive Review Gate Hardening

Date: 2026-07-06

Status:

```text
completed_substantive_review_gate_hardening__template_approvals_rejected
```

## Purpose

Goal5060 fixes a failure exposed by the first all-review-debt retirement attempt.

The preflight gate accepted files that contained only a minimal approval shape:

```text
verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: None
non_blocking_notes: None
```

Those files satisfied the old keyword check but did not review any evidence.
That is not a real external review and must not retire release debt.

## Fix

`scripts/goal5053_v2144_release_preflight.py` now rejects shallow template
approvals.

For each review-required goal, the gate now requires:

```text
minimum length: 800 characters
required fields:
  verdict_label:
  pass/fail/required_amendments:
  blocking_findings:
  non_blocking_notes:
goal-specific section:
  GoalXXXX
goal-specific terms:
  terms tied to that goal's evidence and risk area
decision token:
  approve/pass/revise/fail/block
```

The gate also records `malformed_reasons`, so a failing review file is not just
marked malformed; the reason is visible.

## Consolidated Reviews

The user asked for a single comprehensive review packet.  Goal5060 preserves
that workflow.

The preflight now accepts either:

- per-goal review files such as `review_goal5050_...md`; or
- a consolidated review file matching:

```text
*review*v2_14_4*review*debt*.md
*review*all_open_review_debt*.md
```

A consolidated review must still contain a substantive section for each required
goal and must pass the same goal-specific terms.

## Boundary

This does not judge whether the reviewer agrees with the project.  It only
blocks obviously empty/template review files from retiring debt.

Not authorized:

```text
review_debt_retired_by_template_approval
public_release_ready_from_keyword_only_review
release_preflight_ready_without_substantive_review
```

## Verification

The shallow `review_goal5048_2026-07-06.md` style files are now classified as
malformed because they are too short and lack goal-specific terms.

Expected preflight result after this goal, until real review is supplied:

```text
overall_status: blocked_by_release_gates
external_review_debt: blocked
malformed: non-empty for the template review files
```

## Exit Label

```text
completed_substantive_review_gate_hardening__template_approvals_rejected
```
