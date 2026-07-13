# Goal4988 Project Cleanup After v2.14.3 Release Staging

Date: 2026-07-04

## Purpose

Clean the local workspace after the v2.14.3 release-staging work without deleting
project evidence, tests, reports, or source changes that are part of the current
engineering state.

## Cleanup Actions

Removed verified transient or local-only artifacts:

- `build/`
  - Local ignored build output.
  - Removed because it is reproducible and not part of the release-staging source state.
- `history/internal_docs/docs_reports/goal387_claude_print_capture.tmp`
  - Tracked historical temporary capture file.
  - Removed because it is explicitly a `.tmp` file and not required by the current v2.14.3 evidence chain.
- `exp-project-1/current-head-source.tar`
  - Local-only ignored tracked-source snapshot, approximately 1.18 GB.
  - Removed because the durable source of truth is the archived git branch/commit:
    `codex/v4-tier2-section8` at `35e295a83d2186f717276babc649b94a17659a22`.
  - `exp-project-1/MIGRATION_RECORD_2026-06-30.md` was updated to document this removal.

## Verification

Post-cleanup checks:

```text
pycache_dirs=0
temp_like_files=0
build_exists=False
exp_tar_exists=False
```

Public surface leak scan:

```text
rg "Goal[0-9]+|Claude|Gemini|Antigravity|Codex|verdict|call_for_review|internal_docs|2\.04x" \
  README.md docs examples/current tutorials/current Paper-reproduction-apps/rayjoin-paper/README.md -n
```

Result: no matches.

## Preserved State

The remaining dirty tree is intentional project state, not disposable cache:

- v2.14.3 source changes under `src/native/optix/**` and `src/rtdsl/**`.
- RayJoin paper-reproduction app changes under `Paper-reproduction-apps/rayjoin-paper/**`.
- Regression and genericity tests under `tests/`.
- Goal reports, review files, and measurement artifacts under `history/internal_docs/**`.
- Large `goal4971` packed-cache files under `history/internal_docs/**`, preserved as internal evidence for the top4 representative runs.

These are not public-surface files and must remain excluded from public release artifacts unless intentionally archived as internal history.

## Current Git State Summary

After cleanup:

```text
modified=9
deleted=1
untracked=122
total=132
```

The `deleted=1` entry is the intentional removal of:

```text
history/internal_docs/docs_reports/goal387_claude_print_capture.tmp
```

## Release-Staging Boundary

This cleanup does not claim the repository is ready to commit or push. It only
removes local transient artifacts and records the remaining project state. A
separate staging/squash decision is still required for the v2.14.3 source,
tests, paper-reproduction app, and internal evidence files.

## Exit Label

`completed_project_cleanup_after_v2_14_3_release_staging__transients_removed_public_surface_clean`
