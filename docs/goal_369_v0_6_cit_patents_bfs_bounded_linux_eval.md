# Goal 369: v0.6 first bounded cit-Patents BFS Linux evaluation

## Why this goal exists

Goal 368 added the first bounded `cit-Patents` BFS script. The next bounded
step is to run it on Linux with the current oracle and PostgreSQL baselines.

## Scope

In scope:

- run the bounded `cit-Patents` BFS slice on Linux
- preserve the corrected PostgreSQL timing split from Goal 361
- record any dataset-specific boundary discovered during the first live run

Out of scope:

- full `cit-Patents` closure
- triangle-count on `cit-Patents`
- backend expansion beyond the current Python/oracle/PostgreSQL trio

## Exit condition

This goal is complete when the repo has:

- a saved bounded Linux `cit-Patents` BFS report
- a saved external review
- a saved Codex consensus note
