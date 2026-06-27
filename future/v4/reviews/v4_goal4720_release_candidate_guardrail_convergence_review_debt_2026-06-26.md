# V4 Goal4720 Review Debt

Date: 2026-06-26

Status: `external_review_debt_open`

Debt type: `3_ai_goal_completion_review_debt`

## Reason

Goal4720 is a goal-completion decision for the V4 release-candidate machine
gate. The user allows review debt when external reviewers are not immediately
available, but final public tag authorization still requires external 3-AI
closure.

## Debt Scope

Review the Goal4720 report and the call-for-review packet:

- `future/v4/v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`
- `future/v4/reviews/call_for_review_v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`

## Current Internal Validation

- Catalog regression dry-run: `passed`
- Targeted release-state tests: `34 OK`
- Full V4 local suite: `435 OK`
- Compile check: passed

## Boundaries While Debt Is Open

Allowed:

- continue release packaging and clean-tree validation;
- prepare external review material;
- fix wording or gate drift discovered by reviewers.

Not allowed:

- final public tag;
- broad legacy all-app speedup claim;
- arbitrary callback support claim;
- raw OptiX callback claim;
- C ABI / embedding / non-Python host claim;
- app-specific native kernel claim.

## Required Closure

Close this debt by recording external reviewer verdicts. A passing closure
should explicitly say whether Goal4720 is accepted as a release-candidate
machine-gate convergence step and whether any wording, docs, examples, or
machine gates must change before final tag.
