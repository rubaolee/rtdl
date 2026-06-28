# Call For Review: Goal4784 Restore Original Hello-World Kernel

Reviewer: Antigravity

Requested verdict labels:
- `approve_goal4784_original_hello_world_restored_continue`
- `approve_with_required_amendments`
- `reject_goal4784_hello_world_still_wrong`

## What To Review

Please review:

```text
docs/engineering/goal4784_restore_original_hello_world_kernel_2026-06-28.md
examples/tutorial_programs/hello_world.py
tutorials/current/01_first_run.md
tutorials/current/02_hello_world.md
examples/tutorial_programs/README.md
docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md
```

Context: Goal4783 incorrectly turned hello world into a fixed-radius relation
lesson. Goal4784 restores the original RTDL hello-world teaching model:

```text
input geometry -> traverse -> refine -> emit rows -> Python program result
```

The script should print `hello, world` while still teaching a real RTDL kernel.

## Specific Questions

1. Does the current `hello_world.py` preserve the original RTDL kernel teaching
   model?
2. Is it now a real hello world rather than a fixed-radius lesson or catalog
   lookup?
3. Does the tutorial clearly teach `rt.input`, `rt.traverse`, `rt.refine`, and
   `rt.emit`?
4. Is the portable CPU reference path appropriate for first-run hello world?
5. Is the relationship to current V4 explained without claiming performance or
   GPU execution?
6. Are the user-visible index and tutorial pages consistent with the corrected
   hello-world program?
7. Did the Linux validation evidence prove the command runs and prints
   `hello, world`?
8. Should Goal4783's fixed-radius hello-world approval be superseded by this
   correction?
9. Should Goal4784 close and allow the next tutorial goal to begin?
10. What amendments are required before closure, if any?

## Required Review Output

Please write the review result to:

```text
docs/reviews/antigravity_goal4784_restore_original_hello_world_kernel_review_2026-06-28.md
```

The review must include:

- one verdict label from the allowed labels;
- P0/P1/P2 findings if any;
- answers to all 10 questions;
- explicit statement whether Goal4784 may close;
- explicit non-authorization statement:
  - no full tutorial release-quality claim;
  - no public tag authorization;
  - no acceptance of sorting/ranking tutorials;
  - no skipping remaining tutorial goals.
