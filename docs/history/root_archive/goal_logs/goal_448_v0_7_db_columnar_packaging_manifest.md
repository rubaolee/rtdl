# Goal 448: v0.7 DB Columnar Packaging Manifest

Date: 2026-04-16

## Purpose

Create a concrete packaging manifest for the v0.7 DB columnar work completed
through Goal 447.

This goal does not stage, commit, tag, merge, or push. It exists to make the
next packaging action reviewable before it happens.

## Scope

In scope:

- Runtime and native files changed for v0.7 DB prepared datasets and columnar
  transfer.
- Test files for DB truth paths, prepared datasets, columnar transfer, and
  high-level columnar defaults.
- Performance scripts and Linux PostgreSQL-backed evidence.
- Release-facing documentation refreshed for the current v0.7 DB columnar
  state.
- Handoff, review, and consensus files needed to preserve the 2-AI closure
  trail.

Out of scope:

- Staging or committing.
- Main-branch merge.
- Release tag creation.
- New backend implementation work.
- New benchmark claims beyond the existing Goal 443 and Goal 446 evidence.

## Acceptance Criteria

- The manifest separates source changes, tests, scripts, docs, evidence, and
  consensus records.
- The manifest calls out intentionally preserved invalid review attempts instead
  of treating them as valid consensus.
- The manifest records current hold conditions.
- Codex review and one external AI review both accept the manifest before this
  goal is called closed.
