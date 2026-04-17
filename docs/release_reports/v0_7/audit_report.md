# RTDL v0.7.0 Release Audit Report

Date: 2026-04-16
Status: released bounded DB package

## Audit Scope

This audit checks the bounded `v0.7` DB branch package for:

- code/test/performance wording closure through Goal 470
- public doc/example/tutorial consistency
- honest branch-versus-release framing
- native prepared DB dataset and repeated-query performance claim consistency
- external tester report response and Windows stale-binary blocker handling
- external DB attack-report response
- current pre-release full-test, doc-refresh, and audit evidence
- external Windows v0.6.1 Expert Attack Suite intake and boundary handling
- newer local broad unittest discovery repair evidence
- release-candidate audit after Goal478 with Claude and Gemini review
- post-Goal481 dry-run staging plan with Claude and Gemini review
- Goal483 historical release-report refresh after Goal482 with Claude and
  Gemini review
- Goal486 post-disk-cleanup artifact-integrity audit with Claude and Gemini review
- Goal487 release-hold stability audit with Claude and Gemini review
- Goal488 front/tutorial/example/doc consistency audit with Claude and Gemini review
- Goal489 current-safe history synchronization with Claude and Gemini review
- Goal490 post-Goal489 pre-stage ledger refresh and dry-run staging plan
- Goal491 post-Goal490 release-hold audit with Claude and Gemini review
- Goal492 ready-for-explicit-staging-authorization hold with Claude and Gemini
  review

## Findings

The first branch pass exposed one real public-surface gap:

- DB example scripts still exposed only:
  - `cpu_python_reference`
  - `cpu`

That gap is now corrected. The public DB examples now expose:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`

The DB tutorial and release-facing example index were updated to reflect the
actual backend closure achieved in Goals 426-437.

The second branch pass added native prepared DB dataset closure:

- Embree prepared scene reuse
- OptiX prepared GAS/traversable reuse
- Vulkan prepared BLAS/TLAS reuse
- Linux repeated-query performance gate against PostgreSQL, rebased in Goal 452
  against the best PostgreSQL modes tested so far

The third branch pass removed the row-struct ingestion caveat for the RT
prepared DB dataset path:

- Embree columnar prepared DB dataset transfer
- OptiX columnar prepared DB dataset transfer
- Vulkan columnar prepared DB dataset transfer
- refreshed Linux repeated-query performance gate using `transfer="columnar"`
  with PostgreSQL included
- Goal 452 performance wording refresh:
  - query-only results against best-tested PostgreSQL are mixed
  - setup-plus-10-query total time favors RTDL in the measured Linux evidence
  - this is not an exhaustive PostgreSQL tuning claim

The fourth branch pass added app-facing and fresh-checkout validation evidence:

- app-level v0.7 DB demo
- kernel-form v0.7 DB demo
- Linux fresh-checkout validation after the demo additions
- fresh Linux PostgreSQL availability check
- fresh Linux backend build/probe sequence for Embree, OptiX, and Vulkan
- fresh focused DB correctness tests and prepared-dataset tests
- fresh Linux repeated-query performance artifacts with PostgreSQL included

The fifth branch pass handled newer external tester reports:

- macOS user-perspective correctness report:
  - 179/179 checks passed on the documented public workload surface across
    available backends
- Windows v0.6 audit:
  - identified a real stale/missing Embree DLL and public API mismatch in an
    older snapshot
  - current branch now checks required Embree exports before assigning ctypes
    signatures
  - stale or incomplete Embree libraries fail with an actionable rebuild
    message instead of raw `AttributeError`
  - `make build-embree` is documented as a public build/probe target
  - fresh Windows current-branch sync verified `rt.csr_graph`,
    `rt.embree_version()`, `build\librtdl_embree.dll`, 22/22 required Embree
    exports, and the public graph Embree examples

The sixth branch pass handled the v0.7 DB attack report and current pre-release
gate:

- the external DB attack report and 105-test attack suite were preserved in
  the repo
- local non-platform gaps were closed and regression-tested:
  - empty denormalized DB inputs
  - float-bound `between`
  - alternate integer `grouped_sum` value fields
  - large boundary row counts
  - repeated and failed kernel compilation cleanup
- the Goal 429 cross-engine PostgreSQL gate now treats missing local OptiX or
  Vulkan as a clean skip on non-Linux hosts, not a full-suite error
- local full unittest discovery now passes:
  - `941` tests
  - `105` expected skips
  - no failures or errors
- Linux focused pre-release testing on the synced current worktree passes:
  - PostgreSQL ready
  - Embree, OptiX, and Vulkan probes pass
  - `155` focused v0.7 DB/PostgreSQL/native tests pass

The seventh branch pass handled the newer external Windows v0.6.1 Expert
Attack Suite report:

- the report is preserved in `docs/reports/`
- the reported Windows Embree graph/geometry stress workloads are accepted as
  positive supporting evidence:
  - BFS Galaxy Attack
  - Triangle Clique Attack
  - PIP Cloud Attack
  - LSI Cross Attack
  - resource-pressure cycling
  - randomized graph parity
- the report's "Certified for deployment" wording is recorded as external
  tester language only
- the report is not used as a v0.7 DB/PostgreSQL gate or release authorization

The eighth branch pass added a newer local broad unittest discovery check:

- the default unittest pattern was confirmed to cover only `217` tests in this
  checkout
- the broader project pattern `python3 -m unittest discover -s tests -p
  '*test*.py'` was run to include `goal*_test.py`
- the first broad run found five test-harness/environment errors:
  - three local macOS sandbox `ProcessPoolExecutor` semaphore errors in
    multi-process visual-demo tests
  - two baseline-runner CLI subprocess tests missing `PYTHONPATH=src`
- those issues were repaired narrowly:
  - CLI subprocess tests now pass the required `PYTHONPATH`
  - multi-process visual-demo tests skip cleanly when the local environment
    denies process semaphore access
- the final broad local sweep passed:
  - `1151` tests
  - `108` skips
  - no failures or errors
- Goal 477 has Claude and Gemini external-review acceptance; it is local
  supporting evidence only and not release authorization

The ninth branch pass added a release-candidate audit after Goal478:

- Goal 479 verifies that Goal477 and Goal478 have Codex, Claude, and Gemini
  ACCEPT evidence
- invalid Gemini Flash placeholder attempts are explicitly marked invalid and
  excluded from consensus
- release-facing reports retain hold/no-release/no-tag/no-merge boundaries
- active v0.7 release-path docs have no retired non-release metrics task
  references
- prior Goal470, Goal473, and Goal475 audit JSON artifacts remain `valid: true`
- Goal 479 has Claude and Gemini external-review acceptance, but it is not
  release authorization

The tenth branch pass added a post-Goal481 dry-run staging plan:

- Goal 482 enumerates the current dirty worktree after Goal481
- the plan includes `427` release-package paths and excludes only
  `rtdsl_current.tar.gz`
- the plan has `0` manual-review paths and `11` grouped advisory
  `git add -- ...` command groups
- the plan explicitly records `staging_performed: false` and
  `release_authorization: false`
- Goal 482 has Claude and Gemini external-review acceptance, but it is not
  staging or release authorization

Goal 483 refreshed the release-facing reports after Goal482:

- the audit report, branch statement, support matrix, and tag-preparation
  report now reference Goal482
- the refresh preserves hold/no-release/no-tag/no-merge boundaries
- Goal 483 has Claude and Gemini external-review acceptance, but it is not
  staging or release authorization

Goal 486 handled the disk-full/home-Git incident:

- the accidental home-directory Git repository was disabled by moving
  `/Users/rl2025/.git` to `/Users/rl2025/.git.home-backup-2026-04-16`
- all JSON report artifacts parse and all report text artifacts are non-empty
- Goal484 remains valid after cleanup
- disk free-space threshold is satisfied
- `git diff --check` is clean
- Claude and Gemini accepted the audit
- no staging, commit, tag, push, merge, or release was performed

Goal 487 verified release-hold stability after Goal486:

- Goal486 Codex/Claude/Gemini acceptance records are present
- the home-directory Git repository remains disabled with backup present
- no runaway home-level `git add` or `git ls-files` process is active
- disk, diff, and Goal486 audit checks remain valid
- Claude and Gemini accepted the stability audit
- no staging, commit, tag, push, merge, or release was performed

Goal 488 refreshed the public front-door docs after Goal487:

- front page, docs index, quick tutorial, tutorial ladder, DB tutorial,
  release-facing examples, examples index, and v0.7 release reports were
  checked
- public example commands point to existing files
- v0.7 app-level and kernel-form DB demos are documented
- stale "Goal483 is current" framing was removed
- Claude and Gemini accepted the consistency audit

Goal 489 adopted the external history synchronization report safely:

- the Antigravity report was preserved in `docs/reports/`
- historical root goal docs through Goal431 were archived
- current v0.7 root goal docs from Goal432 onward were preserved
- version sequence trackers for v0.1 through v0.7 are present
- root `history/` now has catch-up rounds through the current v0.7 hold state
- `history/history.db`, `revision_dashboard.md`, and
  `revision_dashboard.html` validate
- Claude and Gemini accepted the history synchronization audit

Goal 490 refreshed the pre-stage ledger after Goal489:

- the current dirty tree is classified after public-doc and history work
- archived historical goal docs and root `history/` chronicle artifacts are
  part of the advisory package
- `rtdsl_current.tar.gz` is the only default exclusion
- generated `git add -- ...` command strings remain advisory only
- no staging, commit, tag, push, merge, or release was performed

## Remaining Honest Boundary

The branch package is coherent, but still bounded:

- this is not a DBMS release
- PostgreSQL remains an external baseline, not an RTDL backend
- the total-time performance win is bounded to the Linux 200k-row synthetic
  setup-plus-10-query gate; query-only results are mixed against the
  best-tested PostgreSQL modes
- the Goal 464 fresh-checkout run is on a GTX 1070, which has no NVIDIA RT
  cores; it is not RT-core hardware-speedup evidence
- columnar prepared dataset ingestion is closed for the bounded Embree, OptiX,
  and Vulkan RT DB paths, but RTDL still does not provide DBMS storage,
  indexing, transactions, or arbitrary SQL
- Windows is now retested for the bounded graph/API/Embree deployment issue
  found by the external v0.6 audit, but Linux remains the primary v0.7
  PostgreSQL/GPU correctness and performance validation platform
- Goal 470 is a pre-release checkpoint and does not authorize tagging or
  merging by itself
- Goal 471 is supporting Windows v0.6.1 Embree graph/geometry evidence, not a
  v0.7 DB/PostgreSQL release gate
- Goal 477 is newer local broad unittest evidence with Claude and Gemini
  external-review acceptance, but it is not release authorization
- Goal 479 is the current release-candidate audit after Goal478 with Claude and
  Gemini external-review acceptance, but it is not release authorization
- Goal 482 is the current dry-run staging command plan with Claude and Gemini
  external-review acceptance, but no staging command has been run and it is not
  release authorization
- Goal 483 is the earlier release-report refresh after Goal482 with Claude and
  Gemini external-review acceptance, but it is not staging or release
  authorization
- Goal 486 is the post-disk-cleanup artifact-integrity audit with Claude and
  Gemini external-review acceptance
- Goal 487 is the current release-hold stability audit with Claude and Gemini
  external-review acceptance; it is not staging or release authorization
- Goal 488 is the current front/tutorial/example/doc consistency audit with
  Claude and Gemini external-review acceptance
- Goal 489 is the current history synchronization audit with Claude and Gemini
  external-review acceptance
- Goal 490 is the current post-Goal489 pre-stage ledger refresh, but it is only
  advisory until external review is complete and the user explicitly approves a
  staging action
- the line is released as the bounded `v0.7.0` DB package

## Audit Result

The `v0.7` DB branch package is internally coherent and honestly documented
after the public-surface cleanup above.
