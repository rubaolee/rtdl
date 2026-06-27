# Goal 532: v0.8.0 Release Authorization And Tagging

Date: 2026-04-18
Status: accepted for release commit and tag action

## User Authorization

The user authorized release with the condition:

> if we passed pre-release test, doc, and audit, then we can release this version

This goal treats that as explicit authorization to convert the accepted v0.8
release candidate into the `v0.8.0` release if the documented pre-release
evidence remains valid.

## Preconditions Checked

- current branch: `main`
- starting commit: `37084a6b587e5ef4a22b0fbfd177d4d1c631c151`
- no existing `v0.8*` tag was present before the release action
- Goal528 macOS post-doc-refresh audit: accepted
- Goal529 Linux post-doc-refresh validation: accepted
- Goal530 v0.8 release-candidate package: accepted by Claude, Gemini, and Codex
- Goal531 public links to the release-candidate package: accepted by Claude,
  Gemini, and Codex

## Release Conversion

The release-facing docs were converted from candidate wording to release
wording:

- front page now states current released version is `v0.8.0`
- docs index now states current released version is `v0.8.0`
- v0.8 release package now states released as `v0.8.0`
- tag record now says tag `v0.8.0` is authorized for the Goal532 release commit

The bounded honesty boundary remains unchanged:

- v0.8.0 is an app-building release over the released v0.7 surface
- it is not a new DBMS, ANN system, robotics stack, clustering engine,
  simulation framework, renderer, or broad performance-speedup claim
- it does not widen the v0.7 DB/language/backend contract

## Local Validation

- focused release guards:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal530_v0_8_release_candidate_package_test tests.goal531_v0_8_release_candidate_public_links_test tests.goal532_v0_8_release_authorization_test`
  - result: `10` tests, `OK`
- full local unit discovery:
  - `PYTHONPATH=src:. python3 -m unittest discover -s tests`
  - result: `232` tests, `OK`
- stale release-candidate wording check over current public v0.8 docs:
  - no live `Release-Candidate`, `release candidate / not yet tagged`,
    `current released version remains v0.7.0`, `not authorized for tag yet`,
    or `Do not tag v0.8.0 yet` wording remains in the current public v0.8
    release package/docs/tests
- whitespace check:
  - `git diff --check`
  - result: pass

## AI Consensus

- Claude review: `docs/reports/goal532_claude_review_2026-04-18.md`
  - verdict: ACCEPT
  - tag safety: safe after the Goal532 release commit is made
- Gemini Flash review: `docs/reports/goal532_gemini_review_2026-04-18.md`
  - verdict: ACCEPT
  - tag safety: safe after the Goal532 release commit is made
- Codex consensus:
  - `history/ad_hoc_reviews/2026-04-18-codex-consensus-goal532-v0_8-release-authorization-and-tagging.md`
  - verdict: ACCEPT

## Tag Plan

Validation and consensus passed. Create annotated tag `v0.8.0` on the Goal532
release commit and push both `main` and the tag.
