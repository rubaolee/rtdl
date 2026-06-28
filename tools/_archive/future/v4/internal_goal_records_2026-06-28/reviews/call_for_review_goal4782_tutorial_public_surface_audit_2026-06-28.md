# Call For Review: Goal4782 Tutorial Public Surface Audit

Reviewer: Antigravity

Requested verdict labels:
- `approve_goal4782_audit_recorded_continue_to_goal4783`
- `approve_with_required_audit_amendments`
- `reject_goal4782_audit_incomplete`

## What To Review

Please review:

```text
docs/engineering/goal4782_tutorial_public_surface_audit_2026-06-28.md
docs/engineering/goal4782_public_surface_file_inventory_2026-06-28.md
docs/engineering/tutorial_programs_auditable_goals_2026-06-28.md
docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md
```

Context: The user ordered a full tutorial repair sequence. Goal4782 is only the
first goal: audit the current public tutorial/docs/examples surface before
editing. The audit intentionally does not claim the tutorial surface is
release-quality.

## Specific Questions

1. Is the Goal4782 audit scope correct for a public tutorial/docs/examples
   surface?
2. Does the audit correctly avoid pretending that runnable examples equal good
   teaching?
3. Does it correctly flag `sorting_rows.py` as blocked/unreviewed instead of
   accepting the current working-tree edit?
4. Does it correctly identify that visible legacy/full benchmark harness files
   under `examples/benchmark_apps` can confuse users?
5. Are any public tutorial/docs/examples files missing from the audit that
   should be included before Goal4782 can close?
6. Are any verdicts too generous, especially for tutorial programs that only
   call planners or print JSON payloads?
7. Does the audit preserve the required split between tutorial programs,
   benchmark apps, and paper reproduction apps?
8. Does the audit correctly keep RayJoin Section 5.7 as paper-reproduction
   workload/exam rather than tutorial curriculum?
9. Should Goal4782 be allowed to close after this audit, with remediation moved
   to Goal4783-4808?
10. What exact amendments are required before Goal4782 can be closed?

## Required Review Output

Please write a review file with:

- one verdict label from the allowed labels;
- P0/P1/P2 findings if any;
- answers to all 10 questions;
- explicit statement whether Goal4782 may close;
- explicit non-authorization statement:
  - no tutorial release-quality claim;
  - no public tag authorization;
  - no acceptance of current `sorting_rows.py` implementation;
  - no skipping Goal4783-4808.

Suggested output path:

```text
docs/reviews/antigravity_goal4782_tutorial_public_surface_audit_review_2026-06-28.md
```
