# Goal 456: v0.7 Pre-Stage Filelist Ledger

Date: 2026-04-16

## Purpose

Create a machine-readable ledger for every currently changed or untracked path
before any future staging decision.

## Scope

This goal classifies the current worktree into:

- source/runtime files to include
- tests to include
- validation scripts to include
- release-facing documentation to include
- goal, report, handoff, and consensus evidence to include
- archive/generated artifacts to exclude by default
- files that require manual review before staging

## Non-Goals

- Do not stage files.
- Do not commit files.
- Do not tag, push, merge, or release.
- Do not treat invalid external-review attempts as consensus.

## Acceptance Criteria

- A script enumerates `git status --porcelain --untracked-files=all`.
- A JSON ledger records each path, status, decision, category, and rationale.
- A CSV ledger records the same path-level data for manual inspection.
- The report summarizes include, exclude, and manual-review counts.
- The archive `rtdsl_current.tar.gz` is excluded by default.
- Goal 456 receives 2-AI consensus before closure.
