# Goal 94: v0.1 Release Validation

## Objective

Run the final release-head validation package for RTDL v0.1.

This goal is the release-quality rerun and artifact sanity pass, not a new
feature or performance goal.

## Scope

Validate the accepted v0.1 release head across:

- focused local milestone tests
- focused Linux backend tests
- accepted backend/performance artifacts
- release-doc consistency against the repo state

## Required outputs

- release-validation report
- release-validation artifact checklist
- explicit pass/fail summary for:
  - local tests
  - Linux tests
  - backend artifact integrity
  - doc/result consistency

## Constraints

- prefer focused high-signal validation over huge unstable reruns
- use Linux where the backend/hardware surface actually matters
- do not claim broader coverage than the release validation actually runs

## Acceptance

Goal 94 is done when:

- the chosen release-head validation commands pass
- the accepted backend artifacts are internally consistent
- the release docs do not contradict the measured artifacts
- the package has 2+ AI review before publish
