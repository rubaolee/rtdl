# Goal 239: Final Public Surface Cleanup

Date: 2026-04-11
Status: implemented

## Objective

Fix the last release-adjacent public-surface consistency issues exposed by the
final review set before the final release decision.

This goal is intentionally narrow. It does not reopen feature work. It only
cleans the public release surface so that normal users are not pushed into
stale maintainer-facing material.

## Inputs

- aggressive external user review:
  - `[REPO_ROOT]/docs/reports/gemini_external_aggressive_user_v0_4_review_2026-04-11.md`
- total doc review:
  - `[REPO_ROOT]/docs/reports/gemini_v0_4_total_doc_review_2026-04-11.md`
- detailed process audit:
  - `[REPO_ROOT]/docs/reports/gemini_v0_4_detailed_process_audit_2026-04-11.md`

## Scope

This goal fixes only:

- front-door docs index steering
- stale milestone Q/A framing
- release-package wording that still overuses internal goal identifiers

## Success Criteria

1. `docs/README.md` no longer sends normal users into stale milestone material
   as part of the main learning path.
2. `docs/current_milestone_qa.md` is clearly marked as archived maintainer
   context.
3. `docs/release_reports/v0_4/` uses public-facing labels where possible,
   instead of unnecessary Goal-number framing.
