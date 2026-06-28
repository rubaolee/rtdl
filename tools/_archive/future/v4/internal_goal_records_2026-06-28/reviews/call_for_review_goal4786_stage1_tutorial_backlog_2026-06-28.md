# Call For Review: Goal4786 Stage 1 Tutorial Backlog

Date: 2026-06-28

Requested output file:

`docs/reviews/antigravity_goal4786_stage1_tutorial_backlog_review_2026-06-28.md`

## Review Target

Primary file:

`docs/engineering/goal4786_stage1_tutorial_backlog_for_benchmark_apps_2026-06-28.md`

Useful context:

- `examples/benchmark_apps/README.md`
- `examples/tutorial_programs/README.md`
- `docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md`
- `tutorials/current/README.md`

## Background

The user rejected tutorial work that hid RTDL concepts behind one-call helper
APIs. The corrected direction is:

1. Stage 1 teaches RTDL language concepts through small tutorial programs.
2. Stage 2 benchmark apps are exams that combine those concepts.
3. Before writing each topic, the maintainer must inspect old working examples
   and modernize them for V4 instead of blindly inventing replacements.

Goal4784 restored the original RTDL hello-world kernel. Goal4785 restored the
Goal97 ray-hit sorting tutorial. Goal4786 is only a planning backlog for what
Stage 1 still needs before Stage 2 can fairly ask a learner to read or write
the 10 benchmark apps.

## Required Review Questions

Please answer each question explicitly.

1. Does the backlog correctly treat benchmark apps as Stage 2 exams rather than
   basic tutorials?
2. Does it include all 10 benchmark apps in the prerequisite matrix?
3. Does it preserve hello world and sorting as the first two accepted topics?
4. Does each remaining topic identify current candidate files and old materials
   that should be inspected before writing?
5. Are any major RTDL language concepts missing before a learner tries the 10
   benchmark apps?
6. Is the backlog too app-specific anywhere, or does it stay at the RTDL
   concept/language-feature level?
7. Does it explicitly require showing the lowering from user problem to RTDL
   relation/operator/continuation/output?
8. Does it avoid claiming that tutorials are complete or release-ready?
9. Are the Linux validation and external-review gates appropriate?
10. May Goal4786 close as a planning goal?

## Verdict Labels

Use one of:

- `approve_goal4786_stage1_backlog_continue`
- `approve_goal4786_with_required_amendments`
- `reject_goal4786_backlog_incomplete`

## Non-Authorization

Approval of this file does not authorize claiming the tutorial surface is
complete. It only authorizes using the backlog as the ordered work list for
future tutorial-writing goals.
