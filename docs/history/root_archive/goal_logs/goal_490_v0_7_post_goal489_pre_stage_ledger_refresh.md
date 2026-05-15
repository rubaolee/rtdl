# Goal 490: v0.7 Post-Goal489 Pre-Stage Ledger Refresh

Date: 2026-04-16
Status: Pending review

## Objective

Refresh the non-mutating pre-stage ledger and dry-run staging command plan after
Goal488 and Goal489 changed the public docs and history/archive surface.

## Acceptance Criteria

- Enumerate the current dirty worktree after Goal489 using
  `git status --porcelain=v1 --untracked-files=all`.
- Classify source, tests, examples, docs, reports, handoffs, consensus records,
  archived historical goal docs, and root `history/` artifacts.
- Exclude only `rtdsl_current.tar.gz` by default.
- Produce JSON, CSV, and generated Markdown evidence.
- Produce grouped advisory `git add -- ...` command strings without running
  them.
- Verify no manual-review paths remain in the current dirty tree.
- Verify `git diff --check` remains clean.
- Preserve no-stage/no-commit/no-tag/no-push/no-merge/no-release status.
- Obtain Claude and Gemini external review before calling the goal closed.
