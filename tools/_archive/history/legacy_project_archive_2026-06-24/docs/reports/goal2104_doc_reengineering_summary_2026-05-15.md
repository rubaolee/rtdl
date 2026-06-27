# Goal2104 Documentation And Repository-Surface Re-Engineering Summary

Status: complete.

Purpose: summarize the full cleanup pass that made the RTDL repository easier
to browse from the front page. The guiding rule was simple: learners should
quickly find current v2.0-facing material; internal researchers should find
advanced design context; historical reviewers should find logs and evidence
without those files flooding the normal path.

## Why This Was Needed

Before this pass, the repository front page and `docs/`/`examples/` directory
views mixed several audiences:

- current learner docs;
- old release notes and goal logs;
- handoff files;
- generated artifacts;
- archived proof apps;
- proposal/research notes;
- release evidence and review records;
- large scripts and tests directories with no entry point.

That made the project look more complicated than the current RTDL user model.
The cleanup did not delete the history. It moved material into the right lane.

## Work Sequence

| Goal | Commit(s) | Focus | Result |
| --- | --- | --- | --- |
| Goal2099 | `4682cdff` | API/internal docs cleanup | Active API/internal docs were made current and old API/wiki material moved under history. |
| Goal2100 | `04064771` | `docs/` information architecture | Added Learn/Research/Audit doors and moved old root logs/version notes out of the learner path. |
| Goal2101 | `26b1b36d`, `3b549c73` | Front-page navigation audit | Verified active public links, removed stale learner wording, and moved old-looking docs directories into Research/Audit/History. |
| Goal2102 | `da2acdb7`, `8d00701a` | `examples/` organization | Rewrote examples index, moved archived helper apps under `examples/internal/archived_apps/`, and kept unified public wrappers at root. |
| Goal2103 | `461a816e` | Root/scripts/tests cleanup | Removed tracked top-level `apps/`, `generated/`, `schemas`, and `build` surfaces; added `scripts/README.md` and `tests/README.md`. |

## Final Reader Lanes

| Reader | Start Here | What They See |
| --- | --- | --- |
| Learner/user | `README.md`, `docs/learn/README.md`, `examples/README.md` | Current v2.0-facing tutorials, app examples, support boundaries, and runnable source-tree commands. |
| Internal researcher | `docs/research/README.md` | Architecture notes, RayJoin/Embree context, app implementation notes, design proposals, and future research notes. |
| Release/audit reviewer | `docs/audit/README.md`, `docs/history/README.md`, `docs/reports/`, `docs/reviews/` | Process docs, runbooks, release evidence, reviews, old goals, archived docs, and preserved artifacts. |
| Maintainer | `scripts/README.md`, `tests/README.md` | Entry points for maintenance scripts and the large regression/evidence suite. |

## Major Moves

| Old Surface | New Home | Reason |
| --- | --- | --- |
| root-level `docs/goal_*.md` | `docs/history/root_archive/goal_logs/` | Goal logs are history, not learner docs. |
| root-level `docs/v0_*.md`, `docs/v1_*.md` | `docs/history/root_archive/version_notes/` | Old version notes should not sit beside current docs. |
| `docs/archive/` | `docs/history/release_archive/` | Historical release entry points belong under History. |
| `docs/directives/` | `docs/audit/process/directives/` | Directive snapshots are audit/process evidence. |
| `docs/proposals/` | `docs/research/proposals/` | Proposals are research/design context. |
| `docs/technical_app_notes/` | `docs/research/app_notes/` | App implementation notes are advanced research/developer material. |
| `examples/rtdl_v0_7_*` helper apps | `examples/internal/archived_apps/` | Compatibility helpers remain runnable but no longer clutter the public example root. |
| retired Apple RT scenario helpers | `examples/internal/archived_apps/` | Public users should start from the unified Apple RT wrapper. |
| top-level `apps/` | `examples/internal/` and `docs/history/source_archive/apps/` | Old proof/demo sources were not a current front-door app surface. |
| top-level `generated/` | `examples/generated/plan_bundles/` | Generated bundles belong with generated examples. |
| top-level `schemas/` | `src/rtdsl/schemas/`, `scripts/schemas/` | Runtime schema and audit schema have different owners. |
| tracked `build/` artifacts | `docs/history/build_artifacts_archive/` | Historical build outputs should not look like a live build directory. |

## Current Front-Door Shape

The tracked root no longer exposes `apps/`, `generated/`, `schemas/`, or tracked
`build/` as product-looking folders. Current users should see the project as:

- `README.md`
- `docs/`
- `examples/`
- `src/`
- `scripts/`
- `tests/`
- ordinary project metadata

`scripts/` and `tests/` remain top-level because they are standard maintainer
surfaces, but each now has a README that tells readers where to start.

## Validation

| Gate | What It Checks |
| --- | --- |
| `tests.goal2100_docs_information_architecture_reorg_test` | Learn/Research/Audit doors and archived root docs. |
| `tests.goal2101_frontpage_navigation_link_audit_test` | Active public local links resolve and active learner docs do not carry old-version clutter. |
| `tests.goal2102_examples_directory_organization_audit_test` | Example root has no old-version/goal-named public files and archived helpers live under internal. |
| `tests.goal2103_root_scripts_tests_organization_audit_test` | Tracked top-level `apps/`, `generated/`, `schemas`, and `build` are gone; relocated schemas resolve. |
| Existing docs/examples gates | Public front page, tutorial/example consistency, app catalog, support matrix, and retired-app surface checks. |

Observed validation during the cleanup:

- Goal2101 active public scan: 55 public Markdown files, 384 local links, 0 broken active links, 0 active old-version markers.
- Goal2102 examples scan: root `examples/*.py` old-version/goal-name scan clean, examples README local links clean.
- Goal2103 root scan: no tracked `apps/`, `generated/`, `schemas`, or `build` front-door paths remain.
- Focused docs/examples/root organization suites passed after each stage.

## Boundaries

This was a documentation and repository-surface re-engineering pass. It did not:

- authorize v2.0 release;
- change the 3-AI consensus redline;
- make new performance claims;
- delete historical evidence;
- remove existing reports or reviews;
- change RTDL's public programming model.

Some local untracked work remains in the working tree from prior development
sessions, including review/report artifacts and local handoff/archive files.
Those were intentionally not swept into these commits.

## Result

The repository now presents one current learner path, one advanced research
path, and one audit/history path. The old material is still available, but it no
longer blocks a normal reader from understanding RTDL as a current Python-hosted
DSL/runtime with v2.0-facing Python+partner+RTDL docs.

