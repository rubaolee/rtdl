# Goal 531: v0.8 Release-Candidate Public Links

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal530 created the `docs/release_reports/v0_8/` release-candidate package.
Goal531 makes that package discoverable from the user-facing documentation path.

## Files Updated

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `tests/goal531_v0_8_release_candidate_public_links_test.py`

## Changes

The front page now links:

- v0.8 Release-Candidate Package
- v0.8 Release-Candidate Statement
- v0.8 Release-Candidate Support Matrix

The docs index now puts the v0.8 release-candidate package before the v0.7
released DB package in the live reading path and release-package list.

The current architecture page now points readers to the v0.8 release-candidate
statement and support matrix before the v0.7 release reports when explaining
exact current boundaries.

## Boundary

This is navigation/documentation only. It does not tag `v0.8.0` and does not
change the v0.8 release-candidate status.

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal531_v0_8_release_candidate_public_links_test \
  tests.goal530_v0_8_release_candidate_package_test
```

Result:

```text
Ran 7 tests in 0.000s
OK
```

`git diff --check` passed.

## AI Consensus

- Claude review: `docs/reports/goal531_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal531_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The v0.8 release-candidate package is now
  discoverable from public entry points without implying tag authorization.
