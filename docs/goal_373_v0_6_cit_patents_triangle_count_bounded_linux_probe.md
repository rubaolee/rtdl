# Goal 373: v0.6 bounded cit-Patents triangle-count Linux probe

## Why this goal exists

Goal 372 added the runnable probe path for the first `cit-Patents`
triangle-count slice.

The next bounded step is to execute that probe on Linux and record the first
real result.

## Scope

In scope:

- run the first bounded `cit-Patents` triangle-count probe on Linux
- preserve the current Python/oracle/PostgreSQL contract
- record the resulting timing/parity evidence honestly

Out of scope:

- full `cit-Patents` triangle-count closure
- committing to a larger bound than the probe result justifies
- benchmark or paper-scale claims

## Exit condition

This goal is complete when the repo has:

- a saved bounded Linux probe report
- a saved external review
- a saved Codex consensus note
