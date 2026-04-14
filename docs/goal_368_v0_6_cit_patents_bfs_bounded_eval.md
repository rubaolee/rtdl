# Goal 368: v0.6 first bounded cit-Patents BFS evaluation

## Why this goal exists

Goal 367 prepares the raw `cit-Patents` dataset path. The next bounded step is
to run the first real BFS slice on that second dataset family.

## Scope

In scope:

- add the first bounded `cit-Patents` BFS evaluation script
- keep the script aligned with the current evaluation harness
- add focused script-level test coverage

Out of scope:

- full `cit-Patents` evaluation closure
- triangle-count on `cit-Patents`
- any new backend work

## Exit condition

This goal is complete when the repo has:

- a runnable bounded `cit-Patents` BFS script
- focused tests proving the script works on a small fixture
- a saved external review
- a saved Codex consensus note
