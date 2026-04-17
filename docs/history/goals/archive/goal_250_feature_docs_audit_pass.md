# Goal 250: Feature Docs Audit Pass

## Objective

Expand tier-3 audit coverage through the public feature reference pages and the
example entrypoints they directly rely on.

## Scope

This pass covers:

- `docs/features/*/README.md`
- the shared example entrypoints referenced by those feature pages where fresh
  repo-root execution was part of the documented contract

## Required Checks

- feature names and acronyms are expanded where that improves first-read clarity
- feature docs use the current repo-root command style consistently
- documented example commands actually run from the released repository root
- any doc/example mismatch found during this pass is fixed rather than merely
  reported
