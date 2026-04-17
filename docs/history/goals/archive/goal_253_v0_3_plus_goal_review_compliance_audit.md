# Goal 253: v0.3+ Goal Review Compliance Audit

## Objective

Audit all RTDL goals from the start of the `v0.3` line forward and check
whether each goal meets the current project review rule from `refresh.md`:

- Codex consensus
- plus at least one external-style Gemini or Claude review

## Scope Rule

This audit uses Goal 161 as the first in-scope goal because Goal 161 is the
start of the `v0.3` line in the preserved goal history.

Included:

- every `docs/goal_*.md` file with goal number `>= 161`
- matching saved review artifacts in:
  - `docs/reports/`
  - `history/ad_hoc_reviews/`

Excluded:

- handoff requests by themselves as proof of review
- pre-`v0.3` goals
- unsaved interactive review claims without a repo artifact

## Compliance Standard

A goal is compliant only if saved repo artifacts show both:

1. Codex consensus
2. at least one Gemini or Claude review report
