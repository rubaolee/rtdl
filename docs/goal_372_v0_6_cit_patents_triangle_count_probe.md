# Goal 372: v0.6 bounded cit-Patents triangle-count probe

## Why this goal exists

Goal 371 closed the plan for the first `cit-Patents` triangle-count slice.

The next bounded move is to create the runnable probe path that will choose the
first honest edge cap from real measurements instead of guesswork.

## Scope

In scope:

- add the first bounded `cit-Patents` triangle-count probe script
- keep the script aligned with the current truth/oracle/PostgreSQL contract
- add focused script-level test coverage

Out of scope:

- full `cit-Patents` triangle-count closure
- committing to a larger final bound before probing
- any new baseline or backend work

## Exit condition

This goal is complete when the repo has:

- a runnable bounded `cit-Patents` triangle-count probe script
- focused tests proving it works on a small fixture
- a saved external review
- a saved Codex consensus note
