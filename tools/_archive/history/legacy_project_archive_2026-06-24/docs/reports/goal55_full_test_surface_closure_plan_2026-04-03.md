# Goal 55 Plan: Full Test Surface Closure

Date: 2026-04-03

## Current Baseline

Current full test discovery on the repo:

- command:
  - `python3 -m unittest discover -s tests -p '*test.py'`
- result:
  - `179` tests
  - `1` skip
  - `OK`

This is a strong baseline, but it is not yet the same as a clearly organized
verification surface.

## Main Observed Gaps

### 1. Test taxonomy is implicit

The repo mixes:

- unit tests
- backend integration tests
- goal-specific regression tests
- system-style workflow tests

but that split is not made explicit in one canonical place.

### 2. System acceptance is distributed

Accepted bounded packages now exist for:

- `County ⊲⊳ Zipcode`
- `BlockGroup ⊲⊳ WaterBodies`
- bounded `LKAU ⊲⊳ PKAU`

but there is not yet a single release-style system test layer that clearly
states which accepted package checks belong to the ongoing acceptance gate.

### 3. Verification commands are not consolidated enough

The repo has enough tests, but not yet one clearly documented matrix such as:

- fast unit gate
- backend integration gate
- full system gate

## Planned Work

1. Write a test inventory report with current classification.
2. Add or refine tests where the acceptance-critical path is too indirect.
3. Add a canonical system-test matrix for the accepted bounded packages.
4. Update the reliability/process docs with the final verification commands.
5. Run the resulting suite.
6. Send the goal to Gemini and Claude for review before publication.

## Expected Outcome

If this goal succeeds, the repo should be able to answer these questions
cleanly:

- what are the unit tests?
- what are the backend integration tests?
- what are the system tests?
- what commands define a release-style verification pass?
