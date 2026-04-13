# Goal 323 Report: v0.5 Call For Test Publish

Date:
- `2026-04-12`

Goal:
- make the `v0.5 preview` call-for-test document visible enough that outside
  reviewers can actually find and use it

Files involved:
- `docs/release_reports/v0_5_preview/call_for_test.md`
- `docs/release_reports/v0_5_preview/support_matrix.md`

What changed:
- the call-for-test doc stays in the preview release-report package
- the `v0.5 preview` support matrix now links to it directly
- the file path itself is stable and reviewable after checkout:
  - `docs/release_reports/v0_5_preview/call_for_test.md`

Why this matters:
- a call-for-test document that is only present on disk is not enough
- external reviewers need to be able to find the invitation from the preview
  package without repo archaeology
- the README front page should stay cleaner than the internal/external review
  path

Honesty boundary:
- this does not change the preview support surface
- this does not upgrade `v0.5` from preview-ready to final-release-ready
- this only improves discoverability of the existing preview testing request
