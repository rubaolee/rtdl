# Call For Review: Goal4785 Restore Goal97 Sorting Tutorial

Reviewer: Antigravity

Requested verdict labels:
- `approve_goal4785_goal97_sorting_restored_continue`
- `approve_with_required_amendments`
- `reject_goal4785_sorting_still_wrong`

## What To Review

Please review:

```text
docs/engineering/goal4785_restore_goal97_sorting_tutorial_2026-06-28.md
examples/tutorial_programs/sorting_rows.py
tutorials/current/03_sorting_rows.md
examples/tutorial_programs/README.md
docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md
```

Context: Goal4785 restores the original Goal97 ray-hit sorting design as the
second V4 tutorial lesson. It should teach:

```text
values -> segment geometry -> segment-intersection hit rows -> hit counts -> stable sorted output
```

It should not be accepted if it is merely a planner/catalog demo, a generic
predecessor-row story, or a claim that RTDL is a general sorting library.

## Specific Questions

1. Does `sorting_rows.py` preserve the original Goal97 ray-hit sorting concept?
2. Does it use a real RTDL kernel with `rt.input`, `rt.traverse`, `rt.refine`,
   and `rt.emit`?
3. Does the tutorial clearly explain how values become segments and how hit
   counts become rank?
4. Does it avoid claiming RTDL is a general-purpose sorting replacement?
5. Does it clearly state the tutorial restriction to nonnegative integers?
6. Is it appropriate as the second lesson after hello world?
7. Are the docs and user-visible index consistent with the restored program?
8. Did the Linux validation prove the expected Goal97 output?
9. Should Goal4785 close and allow the next tutorial goal to begin?
10. What amendments are required before closure, if any?

## Required Review Output

Please write the review result to:

```text
docs/reviews/antigravity_goal4785_restore_goal97_sorting_tutorial_review_2026-06-28.md
```

The review must include:

- one verdict label from the allowed labels;
- P0/P1/P2 findings if any;
- answers to all 10 questions;
- explicit statement whether Goal4785 may close;
- explicit non-authorization statement:
  - no full tutorial release-quality claim;
  - no public tag authorization;
  - no sorting performance claim;
  - no general sorting-library claim;
  - no skipping remaining tutorial goals.
