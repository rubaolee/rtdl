# v2.14.1 Final Gate Report

Date: 2026-07-03

Status: `pass_public_surface_and_source_tree_gate__pending_commit_packaging`

## Purpose

Close the v2.14.1 source-tree surface after packaging the RayJoin
paper-reproduction app as a first-class paper-reproduction project, while
keeping the public user path clean and current.

This gate does not authorize any new performance optimization work. It only
checks that the v2.14.1 surface is coherent enough to be staged for release.

## Version State

- `VERSION`: `v2.14.1`
- `pyproject.toml`: `2.14.1`
- Front page: `README.md` describes the current source-tree surface as
  `v2.14.1`.
- Release package: `docs/release_reports/v2_14/README.md` marks the active
  version as `v2.14.1`.
- Closeout note added:
  `docs/release_reports/v2_14/v2_14_1_closeout.md`.

## Public Surface Changes

The public surface now includes:

- the current README and v2.14-line release package;
- the existing tutorials/examples/docs path;
- `Paper-reproduction-apps/rayjoin-paper/` as a separate paper-reproduction
  app line, parallel to benchmark apps rather than mixed into them.

The public surface does not expose V3/V4/Phoenix/review-process wording.

## Gate Checks Run

### Source-Tree Doctor

Command:

```bash
py -3 scripts/rtdl_source_tree_doctor.py
```

Result:

- required checks: pass;
- version marker: `v2.14.1`;
- optional warnings only: `cupy`, `numba`, OptiX library, Embree library not
  configured on this Windows host.

### Source-Tree Doctor Unit Test

Command:

```bash
py -3 -m unittest tests.goal4278_source_tree_doctor_test
```

Result:

```text
Ran 4 tests
OK
```

### RayJoin Paper App Syntax

Commands:

```bash
py -3 -m compileall -q Paper-reproduction-apps/rayjoin-paper
bash -n Paper-reproduction-apps/rayjoin-paper/scripts/setup_author_official.sh
bash -n Paper-reproduction-apps/rayjoin-paper/scripts/run_author_public_sample.sh
bash -n Paper-reproduction-apps/rayjoin-paper/scripts/run_rtdl_public_sample.sh
bash -n Paper-reproduction-apps/rayjoin-paper/scripts/run_full_public_sample.sh
```

Result: pass.

### Public Leak Scan

Command class:

```bash
rg -n "V3|V4|Goal[0-9]+|Claude|Gemini|Antigravity|Codex|verdict|call_for_review|Phoenix|future/v4|docs/reviews|docs/reports" README.md docs tutorials examples Paper-reproduction-apps
```

Result: no matches.

### Stale Version Scan

Command class:

```bash
rg -n "v2\\.13|v2_13|v2\\.6|examples/v2_0" README.md docs tutorials examples Paper-reproduction-apps
```

Result: no matches.

Remediation applied during this gate:

- updated `docs/versioning.md` from stale v2.13 wording to v2.14.1;
- removed stale public references to legacy v2.12/v2.13 evidence links from the
  current RT-core evidence matrix;
- removed user-visible `v2.6` wording from current benchmark example strings,
  replacing it with neutral legacy-Numba wording while keeping compatibility
  helper names intact.

### Markdown Link Check

Scope:

- `README.md`;
- `docs/**/*.md`;
- `tutorials/**/*.md`;
- `examples/**/*.md`;
- `Paper-reproduction-apps/**/*.md`.

Result:

```text
checked_markdown_files=94
checked_local_links=446
local_markdown_links=pass
```

## Linux RayJoin Evidence Already Captured

The RayJoin project full public-sample Linux run was completed before this
gate and recorded in:

`history/internal_docs/goal4929_rayjoin_complete_paper_reproduction_project_linux_run_2026-07-03.md`

Key result:

- AuthorOfficial Section 5.7 output equals public answer: pass;
- RTDL Section 5.7 output equals public answer: pass;
- RTDL+Numba Section 5.7 output equals public answer: pass;
- shared Section 5.7 SHA-256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`.

## Dirty Tree Note

The current development worktree still contains substantial tracked and
untracked project state from the RayJoin reproduction, public-surface cleanup,
tests, and internal review records. This report does not claim a clean git
tree.

The correct next release-packaging action is to stage/commit intentionally,
not to delete or revert the project-state files as if they were cache.

## Exit Label

`v2_14_1_final_gate_passed__public_surface_clean__source_tree_checks_pass__pending_commit_packaging`
