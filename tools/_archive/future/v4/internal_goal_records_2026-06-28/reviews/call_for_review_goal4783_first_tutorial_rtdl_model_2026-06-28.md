# Call For Review: Goal4783 First Tutorial RTDL Model

Reviewer: Antigravity

Requested verdict labels:
- `approve_goal4783_first_tutorial_continue_to_next`
- `approve_with_required_amendments`
- `reject_goal4783_first_tutorial_not_teaching_rtdl`

## What To Review

Please review:

```text
docs/engineering/goal4783_first_tutorial_rtdl_model_2026-06-28.md
tutorials/current/01_first_run.md
tutorials/current/02_hello_world.md
examples/tutorial_programs/hello_world.py
```

Goal4783 rewrites only the first tutorial lesson. It should teach the first RTDL
programming model:

```text
user data -> candidate relation rows -> RTDL operator -> continuation -> result
```

It should not be accepted if it is merely a planner/catalog demo or a black-box
wrapper.

## Specific Questions

1. Does the rewritten first lesson teach RTDL as a language model rather than an
   app wrapper?
2. Does `hello_world.py` show input data, lowering, relation rows,
   continuation, and V4 operator request?
3. Is the tiny Python loop correctly framed as a teaching mirror, not as the
   real implementation path for larger workloads?
4. Is the fixed-radius example appropriate as the first RTDL lesson?
5. Are the docs clear for a user who does not yet know RT or OptiX?
6. Did the goal correctly validate on local Linux?
7. Are there any misleading claims about performance, GPU execution, true
   zero-copy, callbacks, or whole-app speedup?
8. Should Goal4783 close and allow the next tutorial goal to begin?
9. What amendments are required before closure, if any?

## Required Review Output

Please write the review result to:

```text
docs/reviews/antigravity_goal4783_first_tutorial_rtdl_model_review_2026-06-28.md
```

The review must include:
- one verdict label from the allowed labels;
- P0/P1/P2 findings if any;
- answers to all 9 questions;
- explicit statement whether Goal4783 may close;
- explicit non-authorization statement:
  - no full tutorial release-quality claim;
  - no public tag authorization;
  - no acceptance of `sorting_rows.py`;
  - no skipping remaining tutorial goals.
