# Goal 488: v0.7 Front/Tutorial/Example/Doc Consistency Audit

Date: 2026-04-16
Status: Pending review

## Objective

Verify and refresh the public front page, tutorials, examples, and v0.7
release-facing docs so a reader sees the current bounded v0.7 DB branch state,
not the older Goal483 hold state.

## Acceptance Criteria

- Verify `README.md`, `docs/README.md`, `docs/quick_tutorial.md`,
  `docs/tutorials/README.md`, `docs/tutorials/db_workloads.md`,
  `docs/release_facing_examples.md`, `examples/README.md`, and
  `docs/release_reports/v0_7/*.md`.
- Verify current v0.7 DB examples and app/kernel demos are mentioned where
  appropriate.
- Verify documented public `python examples/...` commands refer to existing
  files.
- Verify release-facing docs mention Goal486 and Goal487 stability evidence.
- Verify stale "Goal483 is current" framing has been removed or bounded as
  historical.
- Preserve no-stage/no-commit/no-tag/no-push/no-merge/no-release status.
- Obtain Claude and Gemini external review before calling the goal closed.
