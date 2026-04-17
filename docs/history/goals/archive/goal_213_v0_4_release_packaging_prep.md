# Goal 213: v0.4 Release Packaging Preparation

Date: 2026-04-10
Status: executed

## Goal

Prepare the canonical `v0.4` release-report package before the final post-`4am`
Claude whole-line audit.

This goal is intentionally a packaging-preparation slice, not the final release
tag itself.

## Scope

- create the canonical `docs/release_reports/v0_4/` package
- translate the current implemented nearest-neighbor line from "preview"
  language into release-package language
- keep the honesty boundary explicit:
  - package prepared
  - final whole-line Claude audit still pending
  - tag not created yet
- update the docs index to point readers at the new release package

## Acceptance

- `docs/release_reports/v0_4/README.md` exists
- `docs/release_reports/v0_4/release_statement.md` exists
- `docs/release_reports/v0_4/support_matrix.md` exists
- `docs/release_reports/v0_4/audit_report.md` exists
- `docs/release_reports/v0_4/tag_preparation.md` exists
- live docs point to the prepared package without falsely claiming a release tag

## Non-Goals

- changing `VERSION`
- creating the final `v0.4` git tag
- claiming Claude whole-line audit completion before it exists
