# Goal5061 - v2.14.4 Consolidated Review Quality Gate

Date: 2026-07-06

Status:

```text
completed_consolidated_review_quality_gate__padding_reviews_rejected
```

## Purpose

Goal5061 fixes the second review-gate failure exposed after Goal5060.

The consolidated review workflow is useful, but a review file can still pass a
simple whole-file length and keyword gate by adding a global padding paragraph
with all target terms.  That is not a substantive review.

## Failure Observed

The rejected consolidated review contained per-goal sections such as:

```text
The rayjoin device_order_by app migration looks correct.
verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: none
```

Then it added an explicit padding paragraph:

```text
additional padding text
satisfy the length requirement
necessary target keywords
terms we need for the goals include
successfully satisfied all constraints
```

This should never retire external review debt.

## Gate Hardening

`scripts/goal5053_v2144_release_preflight.py` now requires:

```text
whole review minimum: 800 characters
per-goal section minimum: 350 characters
required verdict fields inside each goal section
goal-specific terms inside each goal section
decision token inside each goal section
no padding/keyword-stuffing phrases anywhere in the review file
```

The gate still supports either:

- one substantive consolidated review file; or
- substantive per-goal review files.

But the substance must be in the relevant goal section, not in a global keyword
footer.

## Not Authorized

```text
review_debt_retired_by_padding
review_debt_retired_by_keyword_footer
release_ready_from_short_per_goal_approvals
```

## Expected Preflight State

Until a real review is supplied:

```text
overall_status: blocked_by_release_gates
external_review_debt: blocked
```

If a padding review file is present, it must appear in `malformed_reasons` with:

```text
goal_section_too_short_min_350_characters
forbidden_padding_or_keyword_stuffing_phrase
```

## Exit Label

```text
completed_consolidated_review_quality_gate__padding_reviews_rejected
```
